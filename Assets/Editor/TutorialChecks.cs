using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Drives production actions; tutorial state is assigned only in the separate skip test.
    public static class TutorialChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static int assertions;
        static readonly List<string> failures = new();
        static void Check(bool ok, string message)
        {
            assertions++;
            if (!ok) throw new Exception("[Catchline] Tutorial check failed: " + message);
        }
        static object Call(VoyageGame g, string method, params object[] args) =>
            typeof(VoyageGame).GetMethod(method, Hidden).Invoke(g, args);
        static void Field(VoyageGame g, string field, object value) =>
            typeof(VoyageGame).GetField(field, Hidden).SetValue(g, value);
        static void Frame(VoyageGame g, int w = 1440, int h = 900)
        {
            g.Cam.aspect = w / (float)h;
            g.PrepareInterface(w, h, 1);
            Canvas.ForceUpdateCanvases();
            g.PrepareInterface(w, h, 1);
        }
        static void Press(VoyageGame g, string id)
        {
            Frame(g);
            Check(g.InvokeInterface(id), "action exists and enabled: " + id);
        }
        static void Until(VoyageGame g, Func<bool> done, string label, float seconds = 120)
        {
            for (float t = 0; t < seconds && !done(); t += .05f) g.Tick(.05f);
            Check(done(), label);
        }
        static void Step(VoyageGame g, VoyageGame.TutStep step, string target = null, bool line = true)
        {
            foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            {
                Frame(g, size.x, size.y);
                Check(g.Tutorial == step, $"expected {step}, got {g.Tutorial} at {size}");
                var result = ((string pose, string text, string target, bool dismiss)?)Call(g, "TutorialLine");
                Check(result.HasValue == line, step + " line presence");
                if (!line) continue;
                Check(!string.IsNullOrEmpty(result.Value.text), step + " has explanation");
                Check(result.Value.target == target, step + " expected target " + target);
                if (target != null)
                {
                    var canvas = g.GetComponentInChildren<CoastalCanvas>();
                    assertions++;
                    if (canvas == null || !canvas.TryFind(target, out var rect) || rect.width <= 0 || rect.height <= 0)
                        failures.Add(step + " target does not resolve after PrepareInterface: " + target + " at " + size);
                }
            }
            Debug.Log("[Catchline] Tutorial reached " + step);
        }
        static void SaveChecks(VoyageGame g, string path)
        {
            g.State.Save(path);
            Check(File.Exists(path), "isolated save was written");
            var saved = GameState.Load(path);
            Check(saved != null && saved.Tutorial == g.State.Tutorial, "save round trip preserves " + g.Tutorial);
        }

        public static void Run()
        {
            assertions = 0;
            failures.Clear();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("Tutorial isolated action checks");
            root.SetActive(false);
            var g = root.AddComponent<VoyageGame>();
            g.SessionOnly = true;
            g.Build();
            root.SetActive(true);
            string path = Path.Combine(Application.temporaryCachePath, "tutorial-check-" + Guid.NewGuid().ToString("N") + ".json");
            try
            {
                Check(g.State.Hull == 0 && g.State.Roster.Count == 0, "fresh rowboat without recruited crew");
                // SessionOnly substitutes a tier chooser for title/start. Invoke the same fresh-start hook
                // directly, while retaining save isolation throughout the fixture.
                Field(g, "showTitle", false);
                Call(g, "BeginFirstVoyage");
                Check(g.IntroActive && g.Tutorial == VoyageGame.TutStep.Hello, "BeginFirstVoyage starts Hello and intro");
                g.SkipIntro();
                Until(g, () => !g.IntroActive, "intro completes");
                Frame(g);
                var hello = ((string pose, string text, string target, bool dismiss)?)Call(g, "TutorialLine");
                Check(hello.HasValue && (hello.Value.target == "port/sail" || hello.Value.target == "shop/close"),
                    "fresh Hello points to sail or the overlying shop close button");
                Step(g, VoyageGame.TutStep.Hello, hello.Value.target);
                // Close an overlying shop through its real action; then the coach must point to Set sail.
                // If an old build points behind the shop, retain the recorded target failure while checking later steps.
                if (hello.Value.target == "shop/close" || !g.GetComponentInChildren<CoastalCanvas>().TryFind("port/sail", out _))
                {
                    Press(g, "shop/close");
                    Step(g, VoyageGame.TutStep.Hello, "port/sail");
                }
                SaveChecks(g, path);
                g.SetSail();
                Until(g, () => g.CurrentMode == VoyageGame.Mode.Fishing, "SetSail reaches fishing");
                Step(g, VoyageGame.TutStep.FirstCast, "rod/0");
                SaveChecks(g, path);
                var rod = g.Rods[0];
                Until(g, () => g.AtFishingGround, "boat reaches fishing ground");
                Check(g.CanCommandRod(rod), "first rod command available");
                g.CommandRod(rod);
                Check(g.Manning == rod, "captain accepted rod command");
                Until(g, () => rod.State == RodState.Bite, "real cast reaches bite");
                Until(g, () => rod.Reading == null || rod.Reading.Phase == FishPhase.Take && rod.Reading.PhaseTime >= .15f,
                    "patient strike waits for sustained take");
                g.StrikeTap();
                Debug.Log($"[Catchline] Tutorial strike state={rod.State} model={rod.Reading?.Phase} result={rod.ReadingResult} attended={g.MinigameRod == rod}");
                Check(rod.Reading == null || rod.ReadingResult == StrikeResult.Hooked, "real strike hooks");
                Until(g, () => g.Stats.Landed > 0, "strike lands a fish");
                if (g.UsesDeckGraph)
                {
                    // Migrated rowboats land into station baskets, then Carry -> Keep -> Stow.
                    // Auto-carry may already have accepted the first action; use the same commands either way.
                    for (float t = 0; t < 60 && g.Cooler.Count == 0; t += .05f)
                    {
                        if (!g.RodViewActive && g.Captain.Idle)
                        {
                            var basket = g.DeckGraph.OfKind(StationKind.Rod).Select(s => s.Out)
                                .FirstOrDefault(b => b != null && b.UnclaimedCount > 0);
                            if (basket != null) g.CaptainHaulFrom(basket);
                            if (g.DeckGraph.OfKind(StationKind.SortTable).Any(s => s.In != null && s.In.UnclaimedCount > 0))
                                g.CommandKeep(true);
                        }
                        g.Tick(.05f);
                    }
                }
                else if (g.OnDeck.Count > 0)
                {
                    Until(g, () => g.Cooler.Count > 0 || g.OnDeck.Any(g.CanCarry), "landed catch becomes carryable");
                    if (g.Cooler.Count == 0) g.CommandCarry(g.OnDeck.First(g.CanCarry));
                }
                Until(g, () => g.Cooler.Count > 0, "real catch is stowed");
                Check(g.Stats.Landed > 0, "landing recorded through game API");
                g.HeadHome();
                Until(g, () => g.CurrentMode == VoyageGame.Mode.Harbour, "HeadHome reaches harbour");
                Step(g, VoyageGame.TutStep.Sell, "market/sell");
                SaveChecks(g, path);
                Press(g, "shop/close");
                Step(g, VoyageGame.TutStep.Sell, "shop/tab/Market");
                Press(g, "shop/tab/Market");
                Step(g, VoyageGame.TutStep.Sell, "market/sell");
                Press(g, "market/sell");
                Check(g.State.UnsoldCatch.Count == 0 && g.State.LastSale?.Coins > 0, "market action sells real haul");
                Step(g, VoyageGame.TutStep.Skiff);
                SaveChecks(g, path);

                // Match LeadShots' refit prerequisites; this suite tests tutorial actions, not savings pacing.
                g.State.Coins = GameData.SkiffCost;
                g.State.BestVoyageFish = GameData.SkiffFishGoal;
                Step(g, VoyageGame.TutStep.Refit, "shop/tab/Chandlery");
                SaveChecks(g, path);
                Press(g, "shop/tab/Chandlery");
                Press(g, "refit/select");
                Step(g, VoyageGame.TutStep.Refit, "shop/buy");
                Press(g, "shop/buy");
                Check(g.State.Hull == 1, "real Product action refits skiff");
                Until(g, () => g.SimTime > (float)typeof(VoyageGame).GetField("refitUntil", Hidden).GetValue(g), "refit celebration finishes");
                Step(g, VoyageGame.TutStep.Welcome, "shop/tab/CrewOffice");
                SaveChecks(g, path);
                Press(g, "shop/tab/CrewOffice");
                Step(g, VoyageGame.TutStep.Welcome, "crew/tab/chests");
                Press(g, "crew/tab/chests");
                Step(g, VoyageGame.TutStep.Welcome, "chests/welcome/open");
                Field(g, "cardUiClock", 10f);
                Press(g, "chests/welcome/open");
                Check(g.State.Roster.Any(c => c.Def?.Role == CardRole.Navigator), "welcome chest recruits navigator");
                Check(Call(g, "TutorialLine") == null, "coach waits while chest reveal is open");
                Field(g, "cardUiClock", 20f);
                Press(g, "reveal/all");
                Field(g, "cardUiClock", 30f);
                Press(g, "reveal/collect");
                Step(g, VoyageGame.TutStep.MeetMira);
                SaveChecks(g, path);
                Press(g, "cardpanel/close");
                Press(g, "tut/bubble/ok");
                Step(g, VoyageGame.TutStep.Recruit, "crew/tab/recruit");
                SaveChecks(g, path);
                Press(g, "crew/tab/recruit");
                Step(g, VoyageGame.TutStep.Recruit);
                Press(g, "tut/bubble/ok");
                Step(g, VoyageGame.TutStep.Done, line: false);
                SaveChecks(g, path);

                // Seeding is confined to testing the explicit skip operation from every enum step.
                foreach (VoyageGame.TutStep step in Enum.GetValues(typeof(VoyageGame.TutStep)))
                {
                    g.SetTutorial(step);
                    g.SkipTutorial();
                    Check(g.Tutorial == VoyageGame.TutStep.Done && Call(g, "TutorialLine") == null, "skip from " + step);
                }
                // Remove the field from a valid save, preserving its version and all other data.
                SaveChecks(g, path);
                string json = File.ReadAllText(path);
                string old = Regex.Replace(json, "\"Tutorial\"\\s*:\\s*-?\\d+\\s*,", "");
                Check(old != json && !old.Contains("\"Tutorial\""), "old-save fixture really omits tutorial field");
                File.WriteAllText(path, old);
                var legacy = GameState.Load(path);
                Check(legacy != null, "old save without tutorial loads");
                typeof(VoyageGame).GetProperty("State").SetValue(g, legacy);
                Check(g.Tutorial == VoyageGame.TutStep.Done && Call(g, "TutorialLine") == null, "old save skips tutorial");
                Debug.Log($"[Catchline] Tutorial action/save/skip checks reached {assertions} assertions; unresolved targets: {failures.Count}");
                Check(failures.Count == 0, string.Join("; ", failures));
                Debug.Log("[Catchline] TUTORIAL CHECKS PASSED: " + assertions);
            }
            finally
            {
                if (File.Exists(path)) File.Delete(path);
                UnityEngine.Object.DestroyImmediate(root);
            }
        }
    }
}

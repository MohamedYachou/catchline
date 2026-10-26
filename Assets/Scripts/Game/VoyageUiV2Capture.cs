using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // UI v2 screen captures, save-isolated (TEST / SessionOnly) only.
    // Native: Catchline.exe -capture-uiv2 <dir> [-uiv2-screens voyage,operations]  -> <screen>-1440.png / -844.png
    // Editor: Catchline > UI v2 Preview writes Temp/uiv2-request.txt; frames are a scene + Canvas composite for iteration only.
    public partial class VoyageGame
    {
        public static readonly string[] UiV2Screens = { "voyage", "operations", "crew" };
        static readonly Vector2Int[] UiV2Sizes = { new(1440, 900), new(844, 390) };

        void StartUiV2Capture(string[] args)
        {
            if (!SessionOnly) return;
            int polishCapture = Array.IndexOf(args, "-capture-fish-polish");
            if (polishCapture >= 0 && polishCapture + 1 < args.Length)
            { StartCoroutine(CaptureFishPolish(Path.GetFullPath(args[polishCapture + 1]))); return; }
            int rodCapture = Array.IndexOf(args, "-capture-fish-view");
            if (rodCapture >= 0 && rodCapture + 1 < args.Length)
            { StartCoroutine(CaptureFishView(Path.GetFullPath(args[rodCapture + 1]))); return; }
            string dir = null, screens = null;
            int flag = Array.IndexOf(args, "-capture-uiv2");
            if (flag >= 0 && flag + 1 < args.Length) dir = Path.GetFullPath(args[flag + 1]);
            int only = Array.IndexOf(args, "-uiv2-screens");
            if (only >= 0 && only + 1 < args.Length) screens = args[only + 1];
#if UNITY_EDITOR
            const string request = "Temp/uiv2-request.txt";
            if (dir == null && File.Exists(request))
            {
                var lines = File.ReadAllLines(request); File.Delete(request);
                dir = Path.GetFullPath(lines[0]); if (lines.Length > 1) screens = lines[1];
            }
#endif
            if (dir != null) StartCoroutine(CaptureUiV2(dir, screens != null ? screens.Split(',') : UiV2Screens));
        }

        bool StageUiV2(string screen)
        {
            if (screen.StartsWith("harbour-h") || screen is "depart-lane" or "chart-leg" or "sea-entry" or
                "return-sea" or "return-chart" or "return-lane" or "arrival-crates" ||
                screen.StartsWith("intro-") || screen.StartsWith("cage-") || screen.StartsWith("net-"))
                return StageHarbourEvidence(screen);
            if (screen.StartsWith("day-") || screen.StartsWith("new-")) { toastUntil = 0; return StageRestaurantDay(screen); }
            if (screen.StartsWith("restaurant-"))
            {
                // Restaurant mockup screens with sample numbers (VoyageRestaurantUi.cs).
                RestaurantPreview = screen switch { "restaurant-plan" => RestaurantScreen.Plan, "restaurant-prep" => RestaurantScreen.Prep, "restaurant-arrange" => RestaurantScreen.Arrange, _ when screen.StartsWith("restaurant-service") => RestaurantScreen.Service, _ => RestaurantScreen.Closing };
                RestaurantService.Rail = screen switch { "restaurant-service-jobs" => RestaurantRailMode.Jobs, "restaurant-service-scroll" => RestaurantRailMode.Scroll, "restaurant-service-chips" => RestaurantRailMode.Chips, "restaurant-service-mockup" => RestaurantRailMode.Mockup, _ => RestaurantRailMode.Scroll };
                toastUntil = 0;
                return true;
            }
            switch (screen)
            {
                case "voyage":
                    StartTier5Trial(); captureFreeze = true;
                    for (int n = 0; n < 3600; n++) Tick(.05f);
                    CloseManagement(); toastUntil = 0;
                    return CurrentMode == Mode.Fishing;
                case "operations":
                case "crew":
                    if (CurrentMode != Mode.Fishing) { StartTier5Trial(); captureFreeze = true; for (int n = 0; n < 3600; n++) Tick(.05f); }
                    OpenManagement(); managementTab = screen == "operations" ? 1 : 2; dashboardDetail = -1; toastUntil = 0;
                    selectedManagementCrew = State.Crew.ToList().FindIndex(c => c.Role == CrewRole.Fisherman);
                    return ManagementOpen;
                case "crew-deckhand":
                    if (CurrentMode != Mode.Fishing) { StartTier5Trial(); captureFreeze = true; for (int n = 0; n < 3600; n++) Tick(.05f); }
                    OpenManagement(); managementTab = 2; dashboardDetail = -1;
                    selectedManagementCrew = State.Crew.ToList().FindIndex(c => c.Role == CrewRole.Deckhand);
                    return ManagementOpen;
                case "title":
                    NewGame(); hadSave = false; showTitle = true; toastUntil = 0;
                    return true;
                case "settings":
                    NewGame(); showTitle = showSettings = true; toastUntil = 0;
                    return true;
                case "sort-home":
                    if (!StageUiV2("sort")) return false;
                    // Reuse the live Canvas so this catches controls surviving a mode change.
                    PrepareInterface(1440, 900);
                    if (!InvokeInterface("deck/keep")) return false;
                    for (int n = 0; n < 1200 && (Scheduler.OnDeck > 0 || !Captain.Idle); n++) Tick(.05f);
                    if (Scheduler.OnDeck > 0 || !Captain.Idle) return false;
                    // A second waiting fish reproduces the return-trip scheduler case as well.
                    var waiting = DeckGraph.OfKind(Catchline.Game.Deck.StationKind.SortTable).First().In;
                    waiting.Put(new CaughtFish { Species = Species.Mackerel, Kg = .62f, StowedAt = SimTime }, false);
                    PrepareInterface(1440, 900);
                    if (Navigation != null) Sailor.Push(Navigation.Grounds.Last().Centre);
                    HeadHome();
                    PrepareInterface(1440, 900);
                    return CurrentMode == Mode.SailingHome && !GetComponentsInChildren<Transform>(false)
                        .Any(t => t.name is "deck/keep" or "deck/throw");
                case "sort":
                    // Rowboat with a fish on the sort table under a fresh catch card and a two-line toast.
                    StartTestTier(0); captureFreeze = true; Showcase(0, 0); SetupDeckGraph();
                    for (int n = 0; n < 200; n++) Tick(.05f);
                    var sort = DeckGraph?.OfKind(Catchline.Game.Deck.StationKind.SortTable).FirstOrDefault();
                    if (sort?.In == null) return false;
                    sort.In.Put(new CaughtFish { Species = Species.Mackerel, Kg = .62f, StowedAt = SimTime }, false);
                    lastCatchSpecies = Species.Mackerel; lastCatchKg = .62f; catchUntil = SimTime + CatchDisplaySeconds;
                    Toast("Mackerel on the sort table. Keep it for the market, or throw it back to the sea.");
                    return CurrentMode == Mode.Fishing;
                default: return false;
            }
        }

        // HARBOUR-IMPORT-1: fixture-only staging. Production harbour/trip/minigame rules are untouched.
        // The snag image deliberately selects the existing snag branch, independent of crew RNG consumption.
        sealed class EvidenceSnagRandom : System.Random
        {
            public EvidenceSnagRandom() : base(15701) { }
            public override double NextDouble() => .1;
        }

        bool StageHarbourEvidence(string screen)
        {
            if (!SessionOnly) return false;
            LeaveCage(); CancelNetHaulGame();
            netView?.Dispose(); netView = null;
            EndIntro(); NewGame();
            captureFreeze = true; showTitle = paused = panelOpen = false;
            State = new GameState(15701); // repeatable crew, fish and cage cues; no save or PlayerPrefs writes
            State.Hull = screen.StartsWith("harbour-h") ? int.Parse(screen.Substring(9)) :
                screen.StartsWith("intro-") || screen == "arrival-crates" ? 0 : 4;
            State.Coins = 10000; State.Fuel = State.FuelCapacity;
            RebuildBoat(false); Tick(.05f);
            for (int n = 0; n < 80; n++) Tick(.025f);
            toastUntil = catchUntil = 0;
            if (screen.StartsWith("harbour-h")) return CurrentMode == Mode.Harbour;

            if (screen.StartsWith("intro-"))
            {
                BeginIntro();
                float seconds = screen == "intro-open" ? .5f : screen == "intro-basin" ? 5.5f : 10f;
                Advance(seconds); return IntroActive;
            }
            if (screen.StartsWith("cage-"))
            {
                if (!StartTier5Trial()) return false;
                captureFreeze = true;
                buoyTimers[0] = buoyTimers[1] = BuoySoakSeconds;
                var rng = State.Rng;
                if (screen == "cage-snag") State.Rng = new EvidenceSnagRandom();
                bool opened = TryBuoyWork(Captain) && Until(() => CageViewActive);
                State.Rng = rng;
                if (!opened) return false;
                Advance(.8f);
                if (screen == "cage-pull") return Cage?.Phase == CagePhase.Pull;
                for (int n = 0; n < 1600 && Cage != null && Cage.Phase is CagePhase.Pull or CagePhase.Snag; n++)
                {
                    if (Cage.Phase == CagePhase.Snag)
                    {
                        if (screen == "cage-snag") { toastUntil = 0; return true; }
                        DragCage(Cage.SnagDirection);
                    }
                    else if (n % 4 == 0) TapCage();
                    Tick(.05f);
                }
                // The production view moves its first crab onto the board after .5s.
                // Capture after that transfer settles, rather than an empty sorting board.
                Advance(1.1f); toastUntil = 0;
                return screen == "cage-board" && Cage?.Phase == CagePhase.Sort;
            }
            if (screen.StartsWith("net-"))
            {
                if (!StartNetBoatTrial()) return false;
                captureFreeze = true;
                Advance(1);
                if (!SetNet() || !Until(() => NetViewActive)) return false;
                Advance(.7f);
                if (screen == "net-setting") return NetGameSetting && NetViewActive;
                for (int n = 0; n < 1600 && NetGameActive; n++)
                {
                    if (NetGamePhase >= .43f && NetGamePhase <= .55f) TapNetGame();
                    Tick(.025f);
                }
                if (Net != NetState.Soaking) return false;
                Advance(2);
                TickNet(GameData.ShallowNetSoakSeconds + 1f);
                if (!HaulNet() || !Until(() => NetViewActive)) return false;
                Advance(.7f);
                if (screen == "net-haul") return NetViewActive && !NetGameSetting;
                for (int n = 0; n < 1600 && NetGameActive && NetGameProgress < .8f; n++)
                { if (NetGameTension < .64f) TapNetGame(); Tick(.025f); }
                return NetViewActive && NetGameProgress >= .8f;
            }

            SelectedSpot = 0;
            SetSail();
            if (screen == "depart-lane")
            { Advance(3f); return Leg == TripLeg.HarbourOut; }
            if (screen == "chart-leg")
                return Until(() => Leg == TripLeg.ChartOut && ChartRoute >= .45f && ChartAlpha > .95f);
            if (!Until(() => Leg == TripLeg.SeaOut && !chartActive)) return false;
            if (screen == "sea-entry") { Advance(.25f); return Leg == TripLeg.SeaOut; }
            if (!Until(() => CurrentMode == Mode.Fishing && Leg == TripLeg.None)) return false;
            if (screen == "arrival-crates")
                for (int n = 0; n < 12; n++) Cooler.Add(new CaughtFish { Species = Species.Mackerel, Kg = 1.1f, StowedAt = SimTime });
            HeadHome();
            if (screen == "return-sea") { Advance(1); return Leg == TripLeg.SeaHome; }
            if (screen == "return-chart")
                return Until(() => Leg == TripLeg.ChartHome && ChartRoute >= .45f && ChartAlpha > .95f);
            if (screen == "return-lane")
            {
                if (!Until(() => Leg == TripLeg.HarbourIn && !chartActive)) return false;
                Advance(3); return Leg == TripLeg.HarbourIn;
            }
            if (!Until(() => CurrentMode == Mode.Harbour)) return false;
            panelOpen = false; toastUntil = 0; Advance(1.1f);
            return crates.Count > 0 && screen == "arrival-crates";

            void Advance(float seconds) { for (float t = 0; t < seconds; t += .025f) Tick(.025f); }
            bool Until(Func<bool> done)
            { for (int n = 0; n < 12000 && !done(); n++) Tick(.025f); return done(); }
        }

        IEnumerator CaptureUiV2(string directory, IEnumerable<string> screens)
        {
            Application.runInBackground = true; Directory.CreateDirectory(directory);
            captureFreeze = true; showTitle = paused = false;
            Time.timeScale = 0;
            foreach (var screen in screens)
            {
                if (!StageUiV2(screen)) { Debug.LogError("[Catchline] UIV2 stage failed: " + screen); QuitCapture(5); yield break; }
                captureFreeze = true;
                foreach (var size in UiV2Sizes)
                {
                    if (!Application.isEditor) { Screen.SetResolution(size.x, size.y, false); for (int n = 0; n < 20; n++) yield return null; }
                    PrepareInterface(size.x, size.y); Visual(0);
                    for (int n = 0; n < 8; n++) yield return null;
                    string name = $"{screen}-{size.x}";
                    if (Application.isEditor) yield return CompositeFrame(directory, name, size);
                    else yield return CaptureFrame(directory, name);
                    Debug.Log($"[Catchline] UIV2 frame {name}");
                }
            }
            Debug.Log("[Catchline] UIV2 CAPTURES COMPLETE");
            QuitCapture(0);
        }

        // Editor preview only: scene and Canvas rendered separately at the exact size, then composited.
        IEnumerator CompositeFrame(string directory, string name, Vector2Int size)
        {
            yield return new WaitForEndOfFrame();
            var scene = RenderTexture.GetTemporary(size.x, size.y, 24, RenderTextureFormat.ARGB32);
            var ui = RenderTexture.GetTemporary(size.x, size.y, 24, RenderTextureFormat.ARGB32);
            var previous = Cam.targetTexture;
            Cam.targetTexture = scene;
            UnityEngine.Rendering.RenderPipeline.SubmitRenderRequest(Cam, new UnityEngine.Rendering.RenderPipeline.StandardRequest { destination = scene });
            Cam.targetTexture = previous;
            coastalUi.RenderCapture(ui);
            Texture2D Read(RenderTexture rt)
            {
                var t = new Texture2D(size.x, size.y, TextureFormat.RGBA32, false);
                var active = RenderTexture.active; RenderTexture.active = rt;
                t.ReadPixels(new Rect(0, 0, size.x, size.y), 0, 0); t.Apply(); RenderTexture.active = active; return t;
            }
            var a = Read(scene); var b = Read(ui);
            var pa = a.GetPixels32(); var pb = b.GetPixels32();
            for (int i = 0; i < pa.Length; i++)
            {
                float k = pb[i].a / 255f;
                pa[i] = new Color32((byte)(pa[i].r * (1 - k) + pb[i].r * k), (byte)(pa[i].g * (1 - k) + pb[i].g * k), (byte)(pa[i].b * (1 - k) + pb[i].b * k), 255);
            }
            a.SetPixels32(pa); a.Apply();
            File.WriteAllBytes(Path.Combine(directory, name + ".png"), a.EncodeToPNG());
            Destroy(a); Destroy(b); RenderTexture.ReleaseTemporary(scene); RenderTexture.ReleaseTemporary(ui);
        }

        static void QuitCapture(int code)
        {
#if UNITY_EDITOR
            if (Application.isEditor) { UnityEditor.EditorApplication.ExitPlaymode(); return; }
#endif
            Application.Quit(code);
        }
    }
}

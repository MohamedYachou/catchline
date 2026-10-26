using System;
using System.IO;
using Catchline.Game;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Only the disposable scratch project receives the runtime half of this capture fixture.
    public static class PolishSweepCapture
    {
        static void ScratchOnly()
        {
            if (!Path.GetFullPath(Application.dataPath).Replace('\\', '/').EndsWith("/Catchline-sim/Assets"))
                throw new Exception("POLISH SWEEP: scratch project required");
        }
        public static void Prepare()
        {
            ScratchOnly();
            string source = File.ReadAllText("Assets/Editor/PolishSweepCapture.cs");
            const string begin = "POLISH_RUNTIME_BEGIN";
            int a = source.LastIndexOf(begin, StringComparison.Ordinal) + begin.Length;
            int b = source.LastIndexOf("POLISH_RUNTIME_END", StringComparison.Ordinal);
            File.WriteAllText("Assets/Scripts/Game/PolishSweepRuntime.cs", source.Substring(a, b - a));
            Debug.Log("[Catchline] POLISH FIXTURE PREPARED. Snapshot written to Assets/Scripts/Game/PolishSweepRuntime.cs");
        }
        public static void BuildNative()
        { Build("PolishSweep"); }
        public static void BuildSupplement()
        { Build("PolishSupplement"); }
        public static void BuildCurrent()
        { Build("PolishCurrent"); }
        static void Build(string folder)
        {
            ScratchOnly();
            if (!File.Exists("Assets/Scripts/Game/PolishSweepRuntime.cs")) throw new Exception("Prepare fixture first");
            ArtImport.BuildLibrary();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var game = new GameObject("Polish Sweep SessionOnly TEST").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            EditorSceneManager.SaveScene(scene, "Assets/PolishSweepAcceptance.unity");
            var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes = new[] { "Assets/PolishSweepAcceptance.unity" },
                locationPathName = "Builds/" + folder + "/Catchline.exe", target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None });
            if (result.summary.result != BuildResult.Succeeded) throw new Exception("POLISH SWEEP build " + result.summary.result);
            Debug.Log("[Catchline] POLISH SWEEP BUILD PASSED. Snapshot written to Builds/" + folder + "/Catchline.exe");
        }
    }
}

/*POLISH_RUNTIME_BEGIN
using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Catchline.Game.Deck;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void StartPolishSweep()
        {
            string[] args = Environment.GetCommandLineArgs();
            int at = Array.IndexOf(args, "-capture-polish-sweep");
            if (at < 0 || at + 1 >= args.Length) return;
            var game = UnityEngine.Object.FindFirstObjectByType<VoyageGame>();
            if (game == null || !game.SessionOnly) { Debug.LogError("POLISH requires SessionOnly"); Application.Quit(21); return; }
            int only = Array.IndexOf(args, "-polish-sections");
            string sections = only >= 0 ? args[only + 1] : "1,2,3,4,5";
            game.StartCoroutine(game.CapturePolish(Path.GetFullPath(args[at + 1]), sections));
        }

        IEnumerator CapturePolish(string directory, string sections)
        {
            yield return null;
            Application.runInBackground = true; Directory.CreateDirectory(directory);
            Time.timeScale = 0; captureFreeze = true;
            var records = new List<string>(); int failed = 0;
            File.WriteAllText(Path.Combine(directory, "touch-rects.csv"), "frame,control,x,y,width,height,enabled\n");
            File.WriteAllText(Path.Combine(directory, "effective-hit-samples.csv"), "frame,control,dpi,scale,nominalPixels,x,y,width,height,artWidth,artHeight,centerRoutesTo,nominalGridHits,nominalGridTotal\n");
            var stages = new List<string>();
            bool Want(int n) => sections.Split(',').Contains(n.ToString());
            if (Want(1)) stages.AddRange(new[] { "1-title", "1-intro-start", "1-intro-mid", "1-intro-end", "1-first-harbour" });
            if (Want(2)) for (int hull = 0; hull <= 4; hull++)
            {
                stages.Add("2-h" + hull + "-harbour");
                foreach (string tab in new[] { "Supplies", "Chandlery", "CrewOffice", "HarbourMaster", "Market" })
                    stages.Add("2-h" + hull + "-" + tab);
            }
            if (Want(2)) stages.Add("2-traffic-basin");
            if (Want(3))
            {
                stages.AddRange(new[] { "3-depart-lane", "3-chart-leg", "3-sea-entry" });
                for (int map = 0; map < 7; map++) stages.Add("3-map" + map + "-arrival");
            }
            if (Want(4)) stages.AddRange(new[] { "4-rod-cast", "4-rod-bite", "4-rod-fight", "4-rod-catch",
                "4-net-setting", "4-net-haul", "4-cage-pull", "4-cage-board",
                "4-gut-board", "4-gut-clean", "4-gut-ragged", "4-gut-leave",
                "4-sort", "4-sort-home", "4-deck-crew", "4-hold-full" });
            if (Want(5)) stages.AddRange(new[] { "5-return-sea", "5-return-chart", "5-return-lane", "5-arrival-crates",
                "5-market-before", "5-market-after", "5-reloaded" });
            if (Want(6)) for (int hull = 0; hull <= 4; hull++) stages.Add("6-h" + hull + "-boatyard");
            if (Want(7)) stages.AddRange(new[] { "7-crew-walking", "7-crew-carrying" });
            if (Want(8)) stages.AddRange(new[] { "8-current-rod-holder", "8-current-market" });
            if (Want(9)) stages.AddRange(new[] { "rod-cast", "rod-bite", "rod-fight", "rod-catch", "net-setting", "net-haul", "cage-pull", "cage-board", "gut-board", "gut-clean", "gut-ragged", "gut-leave", "sort", "sort-home", "deck-crew", "hold-full" }.Select(s => "9-" + s));
            if (Want(10)) stages.AddRange(new[] { "10-title", "10-harbour", "10-crew-office", "10-chart", "10-return", "10-map1", "10-market", "10-rod-holder" });
            if (Want(11)) stages.AddRange(new[] { "11-crew-walking", "11-crew-carrying" });
            foreach (string stage in stages)
            {
                bool ok = false;
                try { ok = StagePolish(stage, directory); }
                catch (Exception ex) { Debug.LogWarning("POLISH stage exception " + stage + " " + ex); }
                if (!ok)
                {
                    failed++; records.Add(stage + " STAGING FAILED; no native evidence");
                    File.WriteAllLines(Path.Combine(directory, "progress.txt"), records);
                    Debug.LogWarning("[Catchline] POLISH STAGING FAILED " + stage); continue;
                }
                captureFreeze = true;
                foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
                {
                    Screen.SetResolution(size.x, size.y, false);
                    for (int n = 0; n < 12; n++) yield return null;
                    PrepareInterface(size.x, size.y); snapCamera = true; Visual(0);
                    if (stage.StartsWith("6-h"))
                        foreach (var scroll in GetComponentsInChildren<ScrollRect>(false))
                            if (scroll.name == "shop/grid/Chandlery") scroll.verticalNormalizedPosition = 0;
                    for (int n = 0; n < 8; n++) yield return null;
                    yield return new WaitForEndOfFrame();
                    string name = stage + "-" + size.x + ".png";
                    var frame = ScreenCapture.CaptureScreenshotAsTexture();
                    File.WriteAllBytes(Path.Combine(directory, name), frame.EncodeToPNG()); Destroy(frame);
                    if (Want(9) || Want(10) || Want(11)) PolishHitAudit(directory, name, size);
                    var corners = new Vector3[4];
                    foreach (var button in GetComponentsInChildren<Button>(false))
                    {
                        var rect = button.transform as RectTransform;
                        if (rect == null || rect.rect.width <= 0 || rect.rect.height <= 0) continue;
                        rect.GetWorldCorners(corners);
                        float x = corners[0].x, y = size.y - corners[1].y;
                        float w = corners[2].x - corners[0].x, h = corners[1].y - corners[0].y;
                        if (x >= size.x || y >= size.y || x + w <= 0 || y + h <= 0) continue;
                        File.AppendAllText(Path.Combine(directory, "touch-rects.csv"),
                            string.Format(System.Globalization.CultureInfo.InvariantCulture, "{0},{1},{2:F1},{3:F1},{4:F1},{5:F1},{6}\n",
                            name, button.name.Replace(',', '_'), x, y, w, h, button.interactable));
                    }
                    string record = name + " mode=" + CurrentMode + " leg=" + Leg + " map=" + ActiveSpot + " ground=" + ActiveGroundId;
                    records.Add(record); File.WriteAllLines(Path.Combine(directory, "progress.txt"), records);
                    Debug.Log("[Catchline] POLISH FRAME " + record);
                }
            }
            File.WriteAllLines(Path.Combine(directory, "capture-complete.txt"), records);
            Debug.Log("[Catchline] POLISH CAPTURES COMPLETE sections=" + sections + " failures=" + failed);
            Application.Quit(failed == 0 ? 0 : 22);
        }

        // Query production raycasters without dispatching pointer actions. Includes invisible child /hit Images.
        void PolishHitAudit(string directory, string frame, Vector2Int size)
        {
            if (size.x != 844 || EventSystem.current == null) return;
            var corners = new Vector3[4];
            Rect Bounds(RectTransform t)
            {
                t.GetWorldCorners(corners);
                return Rect.MinMaxRect(corners[0].x, corners[0].y, corners[2].x, corners[2].y);
            }
            Rect Clip(Rect a, Rect b) => Rect.MinMaxRect(Mathf.Max(a.xMin,b.xMin), Mathf.Max(a.yMin,b.yMin), Mathf.Min(a.xMax,b.xMax), Mathf.Min(a.yMax,b.yMax));
            Button Route(Vector2 point)
            {
                var data = new PointerEventData(EventSystem.current) { position = point };
                var found = new List<RaycastResult>(); EventSystem.current.RaycastAll(data, found);
                return found.Count == 0 ? null : found[0].gameObject.GetComponentInParent<Button>();
            }
            foreach (var button in GetComponentsInChildren<Button>(false))
            {
                if (!button.IsInteractable()) continue;
                var art = Bounds((RectTransform)button.transform);
                var all = new List<Rect>();
                foreach (var g in button.GetComponentsInChildren<Graphic>(false))
                {
                    if (!g.raycastTarget || g.canvasRenderer.cull || g.GetComponentInParent<Button>() != button) continue;
                    var r = Clip(Bounds(g.rectTransform), new Rect(0,0,size.x,size.y));
                    foreach (var mask in g.GetComponentsInParent<RectMask2D>(false)) r = Clip(r, Bounds(mask.rectTransform));
                    if (r.width > 0 && r.height > 0) all.Add(r);
                }
                if (all.Count == 0) continue;
                var hit = Rect.MinMaxRect(all.Min(r=>r.xMin), all.Min(r=>r.yMin), all.Max(r=>r.xMax), all.Max(r=>r.yMax));
                // Fixed 44-pixel sample square, independent of the DPI-expanded production rectangle.
                Vector2 center = hit.center; int count = 0;
                for (int y=0;y<9;y++) for (int x=0;x<9;x++)
                    if (Route(center + new Vector2(-21.5f+x*43f/8,-21.5f+y*43f/8)) == button) count++;
                var centerButton = Route(center);
                var canvas = button.GetComponentInParent<Canvas>();
                File.AppendAllText(Path.Combine(directory, "effective-hit-samples.csv"), string.Format(System.Globalization.CultureInfo.InvariantCulture,
                    "{0},{1},{2:F1},{3:F3},{4:F2},{5:F2},{6:F2},{7:F2},{8:F2},{9:F2},{10:F2},{11},{12},81\n",
                    frame, button.name.Replace(',', '_'), Screen.dpi, canvas != null ? canvas.scaleFactor : 0, CoastalCanvas.TouchPixels,
                    hit.x, size.y-hit.yMax, hit.width, hit.height, art.width, art.height, centerButton != null ? centerButton.name.Replace(',', '_') : "none", count));
            }
        }

        bool PolishUntil(Func<bool> done)
        { for (int n = 0; n < 18000 && !done(); n++) Tick(.025f); return done(); }
        void PolishAdvance(float seconds)
        { for (float t = 0; t < seconds; t += .025f) Tick(.025f); }
        void PolishReset(int hull = 4)
        {
            LeaveGut(); LeaveCage(); CancelNetHaulGame(); netView?.Dispose(); netView = null;
            EndIntro(); NewGame(); State = new GameState(17501);
            State.Hull = hull; State.Coins = 10000; State.Fuel = State.FuelCapacity;
            showTitle = paused = panelOpen = confirmHeadHome = false; captureFreeze = true;
            RebuildBoat(false); Tick(.05f); PolishAdvance(1); toastUntil = catchUntil = 0;
        }

        bool StagePolish(string stage, string directory)
        {
            if (!SessionOnly) return false;
            if (stage.StartsWith("9-")) return StagePolish("4-" + stage.Substring(2), directory);
            if (stage.StartsWith("11-")) return StagePolish("7-" + stage.Substring(3), directory);
            if (stage.StartsWith("10-"))
            {
                string key = stage.Substring(3);
                return StagePolish(key == "title" ? "1-title" : key == "harbour" ? "2-h0-harbour" : key == "crew-office" ? "2-h1-CrewOffice" : key == "chart" ? "2-h0-HarbourMaster" : key == "return" ? "5-return-sea" : key == "map1" ? "3-map1-arrival" : "8-current-" + key, directory);
            }
            if (stage == "1-title") return StageUiV2("title");
            if (stage.StartsWith("1-intro-"))
                return StageUiV2(stage.EndsWith("start") ? "intro-open" : stage.EndsWith("mid") ? "intro-basin" : "intro-close");
            if (stage == "1-first-harbour") { PolishReset(0); return true; }
            if (stage.StartsWith("8-current-"))
            {
                PolishReset(0); panelOpen = true;
                hudTab = stage.EndsWith("market") ? HudTab.Market : HudTab.Chandlery;
                if (hudTab == HudTab.Chandlery) shopSelection[hudTab] = "upgrade/RodHolder";
                else { State.LogCount[(int)Species.Mackerel] = 12; State.LogBest[(int)Species.Mackerel] = 1.1f; }
                return true;
            }
            if (stage.StartsWith("6-h"))
            {
                int hull = int.Parse(stage.Substring(3, 1)); PolishReset(hull);
                hudTab = HudTab.Chandlery; panelOpen = true;
                shopSelection[hudTab] = hull == 1 ? "refit/compact" : hull == 2 ? "refit/prep" : hull == 3 ? "refit/tier5" : "refit";
                return true;
            }
            if (stage.StartsWith("7-crew-"))
            {
                PolishReset(); if (!StartTier5Trial()) return false;
                PolishAdvance(.1f); SetupDeckGraph();
                if (Scheduler == null) return false;
                CloseManagement(); Scheduler.CancelAll();
                var chosen = workers.FirstOrDefault(kv => !kv.Value.Captain && kv.Value.Role == CrewRole.Deckhand);
                if (chosen.Key == null) { Debug.LogWarning("POLISH crew missing: " + string.Join(";", workers.Select(kv => kv.Key.Name + ":" + kv.Value.Role))); return false; }
                chosen.Value.SetDuties(Duty.Haul, Duty.Sort);
                foreach (var p in People) p.Stop();
                Scheduler.Workers.RemoveAll(w => w != chosen.Value);
                var gear = DeckGraph.OfKind(StationKind.Rod).FirstOrDefault();
                if (gear == null) return false;
                for (int n = 0; n < 3; n++) LandOnDeck(gear, Species.Mackerel, 1.1f);
                bool carrying = stage.EndsWith("carrying");
                bool arrived = PolishUntil(() => chosen.Key.Walking && (carrying ? chosen.Value.Hands.Count > 0 : chosen.Value.Hands.Count == 0));
                toastUntil = catchUntil = 0; PlaceBasketFish(); Visual(0);
                File.AppendAllText(Path.Combine(directory, "crew-state.txt"), stage + " worker=" + chosen.Key.Name + " walking=" + chosen.Key.Walking + " hands=" + chosen.Value.Hands.Count + " job=" + chosen.Value.Current + "\n");
                return arrived;
            }
            if (stage.StartsWith("2-h"))
            {
                int hull = int.Parse(stage.Substring(3, 1)); PolishReset(hull);
                string tab = stage.Substring(5);
                if (tab == "harbour") return true;
                hudTab = (HudTab)Enum.Parse(typeof(HudTab), tab); panelOpen = true;
                chartFocus = 6; chartDetailsOpen = chartContractsOpen = false; return true;
            }
            if (stage == "2-traffic-basin") { PolishReset(2); ShowHarbourTraffic(.42f); return true; }
            if (stage.StartsWith("3-map"))
            {
                PolishReset(4); int map = int.Parse(stage.Substring(5, 1));
                if (!State.Known(map) && !State.BuyChart(map)) return false;
                SelectedSpot = map; SetSail(); return PolishUntil(() => CurrentMode == Mode.Fishing && Leg == TripLeg.None);
            }
            if (stage.StartsWith("3-")) return StageUiV2(stage.Substring(2));
            if (stage.StartsWith("4-rod-"))
            {
                PolishReset(0); if (!StageFishViewCapture()) return false;
                if (stage == "4-rod-cast") { PolishAdvance(.6f); return RodViewActive; }
                var rod = Manning;
                if (!PolishUntil(() => rod.Reading.Phase == FishPhase.Take)) return false;
                if (stage == "4-rod-bite") { Tick(.2f); return RodViewActive; }
                StrikeTap();
                if (stage == "4-rod-fight") { PolishAdvance(.35f); return RodViewActive; }
                if (!PolishUntil(() => !RodViewActive)) return false;
                lastCatchSpecies = rod.HookedSpecies; lastCatchKg = rod.HookedKg; catchUntil = SimTime + CatchDisplaySeconds;
                return Stats.Landed > 0;
            }
            if (stage.StartsWith("4-net-") || stage.StartsWith("4-cage-") || stage == "4-sort" || stage == "4-sort-home")
                return StageUiV2(stage.Substring(2));
            if (stage.StartsWith("4-gut-"))
            {
                PolishReset(3); if (!StartPrepBoatTrial()) return false;
                SetupDeckGraph(); PolishAdvance(1);
                Scheduler.Workers.RemoveAll(w => !w.Captain);
                var table = DeckGraph.OfKind(StationKind.ProcessTable).FirstOrDefault();
                if (table?.In == null) return false;
                for (int n = 0; n < 2; n++) table.In.Put(new CaughtFish { Species = Species.Mackerel, Kg = 1.2f }, false);
                if (!CaptainGutAt(table) || !PolishUntil(() => GutWaiting)) return false;
                PolishAdvance(.6f);
                if (stage == "4-gut-clean") { CutGut(new[] { new Vector2(.05f, 0), new Vector2(.5f, .03f), new Vector2(.95f, 0) }); Tick(.2f); }
                if (stage == "4-gut-ragged") { CutGut(new[] { new Vector2(.1f, 0), new Vector2(.5f, .3f), new Vector2(.9f, .02f) }); Tick(.2f); }
                if (stage == "4-gut-leave") { LeaveGut(); PolishAdvance(1); return !GutViewActive; }
                return GutViewActive;
            }
            if (stage == "4-deck-crew" || stage == "4-hold-full")
            {
                PolishReset(); StartTier5Trial(); captureFreeze = true;
                for (int n = 0; n < 1200; n++) Tick(.05f);
                CloseManagement(); toastUntil = catchUntil = 0;
                if (stage == "4-hold-full")
                {
                    Cooler.Clear(); for (int n = 0; n < 80; n++) Cooler.Add(new CaughtFish { Species = Species.Cod, Kg = 3, StowedAt = SimTime });
                    Visual(0);
                }
                return CurrentMode == Mode.Fishing;
            }
            if (stage.StartsWith("5-return-") || stage == "5-arrival-crates") return StageUiV2(stage.Substring(2));
            if (stage == "5-market-before" || stage == "5-market-after" || stage == "5-reloaded")
            {
                PolishReset(2);
                for (int n = 0; n < 12; n++) State.UnsoldCatch.Add(new CaughtFish { Species = Species.Mackerel, Kg = 1.1f, StowedAt = SimTime });
                hudTab = HudTab.Market; panelOpen = true;
                if (stage == "5-market-before") return true;
                PrepareInterface(1440, 900);
                if (!InvokeInterface("market/sell")) return false;
                if (stage == "5-reloaded")
                {
                    string path = Path.Combine(directory, "preview-save.json");
                    int coins = State.Coins; State.Save(path); var loaded = GameState.Load(path);
                    if (loaded == null || loaded.Coins != coins) return false;
                    State = loaded; RebuildBoat(false); Tick(.05f); hudTab = HudTab.Market; panelOpen = true;
                    File.WriteAllText(Path.Combine(directory, "preview-reload-check.txt"), "PASS explicit evidence-folder save/load; coins=" + coins + "; SessionOnly remains true; player save not accessed.");
                }
                return State.LastSale != null || stage == "5-reloaded";
            }
            return false;
        }
    }
}
POLISH_RUNTIME_END*/

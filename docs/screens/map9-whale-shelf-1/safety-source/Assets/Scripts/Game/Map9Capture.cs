using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace Catchline.Game
{
    // Explicit native evidence mode, guarded by the serialized SessionOnly scene.
    public partial class VoyageGame
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void StartMap9Capture()
        {
            var args = Environment.GetCommandLineArgs(); int flag = Array.IndexOf(args, "-capture-map9");
            if (flag < 0 || flag + 1 >= args.Length) return;
            var game = UnityEngine.Object.FindFirstObjectByType<VoyageGame>();
            if (game == null || !game.SessionOnly) { Debug.LogError("[Catchline] MAP9 requires SessionOnly TEST scene"); Application.Quit(7); return; }
            game.StartCoroutine(game.CaptureMap9(Path.GetFullPath(args[flag + 1])));
        }
        IEnumerator CaptureMap9(string directory)
        {
            yield return null;
            Directory.CreateDirectory(directory); Application.runInBackground = true;
            NewGame(); EndIntro(); State = new GameState(6501);
            State.Hull = 4; State.Coins = 10000; State.Fuel = State.FuelCapacity;
            captureFreeze = true; showTitle = paused = panelOpen = false; Time.timeScale = 0;
            RebuildBoat(false); Tick(.05f);
            chartFocus = 8; chartDetailsOpen = false; chartContractsOpen = false;
            hudTab = HudTab.HarbourMaster; panelOpen = true;
            var frames = new List<string>();
            yield return Frames("chart"); // actual overview with the unowned 1920-coin chart
            chartDetailsOpen = true; PrepareInterface(1440, 900);
            if (!InvokeInterface("chart/select") || !State.Known(8) || SelectedSpot != 8) { Fail("chart purchase through UI"); yield break; }
            panelOpen = false; SetSail();
            if (!Until(() => Leg == TripLeg.SeaOut && !chartActive)) { Fail("normal harbour/chart/sea departure"); yield break; }
            for (int n = 0; n < 160 && Leg == TripLeg.SeaOut && !Sailor.Arrived; n++) Tick(.025f);
            if (Leg != TripLeg.SeaOut) { Fail("sail-out frame state"); yield break; }
            yield return Frames("sail-out");
            if (!Until(() => CurrentMode == Mode.Fishing && Leg == TripLeg.None)) { Fail("Herring shoals arrival"); yield break; }
            yield return Frames("herring-shoals");
            foreach (string ground in new[] { "shelf-edge", "whale-road" })
            {
                if (!Relocate(ground) || !Until(() => CurrentMode == Mode.Fishing && Sailor.Arrived) || ActiveGroundId != ground)
                { Fail(ground + " relocation"); yield break; }
                yield return Frames(ground);
            }
            HeadHome();
            if (!Until(() => CurrentMode == Mode.Harbour)) { Fail("return home"); yield break; }
            File.WriteAllLines(Path.Combine(directory, "capture-complete.txt"), frames);
            Debug.Log("[Catchline] MAP9 NATIVE CAPTURES COMPLETE: chart purchase, normal departure, three anchors and home; " + frames.Count + " frames");
            Application.Quit(0);

            bool Until(Func<bool> done)
            { for (int n = 0; n < 16000 && !done(); n++) Tick(.025f); return done(); }
            void Fail(string stage) { Debug.LogError("[Catchline] MAP9 native failed: " + stage); Application.Quit(8); }
            IEnumerator Frames(string stage)
            {
                toastUntil = catchUntil = 0;
                foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
                {
                    Screen.SetResolution(size.x, size.y, false);
                    for (int n = 0; n < 20; n++) yield return null;
                    PrepareInterface(size.x, size.y); snapCamera = true;
                    for (int n = 0; n < 80; n++) Visual(.025f);
                    for (int n = 0; n < 8; n++) yield return null;
                    yield return new WaitForEndOfFrame();
                    var frame = ScreenCapture.CaptureScreenshotAsTexture();
                    string name = stage + "-" + size.x + ".png";
                    File.WriteAllBytes(Path.Combine(directory, name), frame.EncodeToPNG()); Destroy(frame);
                    string record = name + " mode=" + CurrentMode + " leg=" + Leg + " ground=" + ActiveGroundId + " position=" + (Sailor != null ? Sailor.Position.ToString("F2") : "harbour");
                    frames.Add(record); Debug.Log("[Catchline] MAP9 FRAME " + record);
                }
            }
        }
    }
}

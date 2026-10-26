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
        static void StartMap11Capture()
        {
            var args = Environment.GetCommandLineArgs(); int flag = Array.IndexOf(args, "-capture-map11");
            if (flag < 0 || flag + 1 >= args.Length) return;
            var game = UnityEngine.Object.FindFirstObjectByType<VoyageGame>();
            if (game == null || !game.SessionOnly) { Debug.LogError("[Catchline] MAP11 requires SessionOnly TEST scene"); Application.Quit(7); return; }
            game.StartCoroutine(game.CaptureMap11(Path.GetFullPath(args[flag + 1])));
        }
        IEnumerator CaptureMap11(string directory)
        {
            yield return null;
            Directory.CreateDirectory(directory); Application.runInBackground = true;
            NewGame(); EndIntro(); State = new GameState(6501);
            State.Hull = 4; State.Coins = 40000; State.Fuel = State.FuelCapacity;
            captureFreeze = true; showTitle = paused = panelOpen = false; Time.timeScale = 0;
            RebuildBoat(false); Tick(.05f);
            chartPage = ChartPage(10); chartPageFocus = chartFocus = 10; chartDetailsOpen = false; chartContractsOpen = false;
            hudTab = HudTab.HarbourMaster; panelOpen = true;
            var frames = new List<string>();
            yield return Frames("chart"); // actual overview with the unowned 36000-coin chart
            chartDetailsOpen = true; PrepareInterface(1440, 900);
            if (!InvokeInterface("chart/select") || !State.Known(10) || SelectedSpot != 10) { Fail("chart purchase through UI"); yield break; }
            panelOpen = false; SetSail();
            if (!Until(() => Leg == TripLeg.SeaOut && !chartActive)) { Fail("normal harbour/chart/sea departure"); yield break; }
            for (int n = 0; n < 160 && Leg == TripLeg.SeaOut && !Sailor.Arrived; n++) Tick(.025f);
            if (Leg != TripLeg.SeaOut) { Fail("sail-out frame state"); yield break; }
            yield return Frames("sail-out");
            if (!Until(() => CurrentMode == Mode.Fishing && Leg == TripLeg.None)) { Fail("Kelp edge arrival"); yield break; }
            yield return Frames("kelp-edge");
            // Hold gameplay while real Unity time drives scenery life. Measure
            // actual component transforms across a real-time interval, not poses
            // supplied by the fixture. No player save is involved.
            var sways = scenery.GetComponentsInChildren<KelpRootSway>();
            var poses = new Quaternion[sways.Length];
            for (int i = 0; i < sways.Length; i++) poses[i] = sways[i].transform.localRotation;
            Time.timeScale = 1;
            yield return new WaitForSeconds(1.25f);
            Time.timeScale = 0;
            if (sways.Length != 4) { Fail("four runtime kelp sways"); yield break; }
            for (int i = 0; i < sways.Length; i++)
                if (Quaternion.Angle(poses[i], sways[i].transform.localRotation) < .1f) { Fail("runtime kelp motion " + i); yield break; }
            Debug.Log("[Catchline] MAP11 LIVE MOTION PASS: all four clusters moved over 1.25 real seconds with gameplay frozen");
            yield return Frames("life-kelp-motion");
            // Supplement the unchanged player-camera frames: the raft anchor is
            // largely behind the left HUD at Kelp edge. Keep HUD and deck in a
            // clearly labelled evidence-only camera composition, without moving life.
            yield return Frames("life-otter");
            foreach (string ground in new[] { "sand-clearing", "post-line" })
            {
                if (!Relocate(ground) || !Until(() => CurrentMode == Mode.Fishing && Sailor.Arrived) || ActiveGroundId != ground)
                { Fail(ground + " relocation"); yield break; }
                yield return Frames(ground);
            }
            HeadHome();
            if (!Until(() => CurrentMode == Mode.Harbour)) { Fail("return home"); yield break; }
            File.WriteAllLines(Path.Combine(directory, "capture-complete.txt"), frames);
            Debug.Log("[Catchline] MAP11 NATIVE CAPTURES COMPLETE: chart purchase, normal departure, three anchors and home; " + frames.Count + " frames");
            Application.Quit(0);

            bool Until(Func<bool> done)
            { for (int n = 0; n < 16000 && !done(); n++) Tick(.025f); return done(); }
            void Fail(string stage) { Debug.LogError("[Catchline] MAP11 native failed: " + stage); Application.Quit(8); }
            IEnumerator Frames(string stage)
            {
                toastUntil = catchUntil = 0;
                foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
                {
                    Screen.SetResolution(size.x, size.y, false);
                    for (int n = 0; n < 20; n++) yield return null;
                    PrepareInterface(size.x, size.y); snapCamera = true;
                    for (int n = 0; n < 80; n++) Visual(.025f);
                    for (int n = 0; n < 8; n++)
                    {
                        yield return null;
                        if (stage == "life-otter")
                        {
                            var raft = ArtLibrary.Find(scenery.gameObject, "Otter raft");
                            if (raft == null) { Fail("otter evidence anchor"); yield break; }
                            var view = Cam.WorldToViewportPoint(raft.position);
                            Cam.transform.position += raft.position - Cam.ViewportToWorldPoint(new Vector3(.62f, .5f, view.z));
                        }
                    }
                    yield return new WaitForEndOfFrame();
                    var frame = ScreenCapture.CaptureScreenshotAsTexture();
                    string name = stage + "-" + size.x + ".png";
                    File.WriteAllBytes(Path.Combine(directory, name), frame.EncodeToPNG()); Destroy(frame);
                    string record = name + " mode=" + CurrentMode + " leg=" + Leg + " ground=" + ActiveGroundId + " position=" + (Sailor != null ? Sailor.Position.ToString("F2") : "harbour");
                    frames.Add(record); Debug.Log("[Catchline] MAP11 FRAME " + record);
                }
            }
        }
    }
}

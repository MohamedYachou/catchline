using System;
using System.Collections;
using System.IO;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Native acceptance only. The preview scene is SessionOnly; this flag never
        // stages a real player's voyage or reads/writes their save.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        static void StartSeaCapture()
        {
            var args = Environment.GetCommandLineArgs();
            int flag = Array.IndexOf(args, "-capture-sea");
            if (flag < 0 || flag + 1 >= args.Length) return;
            var game = UnityEngine.Object.FindFirstObjectByType<VoyageGame>();
            if (game == null || !game.SessionOnly) { Debug.LogError("Sea captures require TEST mode."); Application.Quit(7); return; }
            game.StartCoroutine(game.CaptureSea(Path.GetFullPath(args[flag + 1])));
        }

        IEnumerator CaptureSea(string directory)
        {
            yield return null; // Normal Start/scene setup finishes first.
            Directory.CreateDirectory(directory); Application.runInBackground = true;
            for (int map = 0; map < Sea.SeaNav.Maps.Length; map++)
            {
                NewGame(); showTitle = paused = false; Time.timeScale = 0;
                ActiveSpot = SelectedSpot = map; voyageStart = SimTime;
                if (!BeginSeaVoyage() || !BeginSeaRoute(Mode.SailingOut)) { Fail("departure"); yield break; }
                yield return null;
                if (!ArriveSeaCapture()) { Fail("initial arrival"); yield break; }
                yield return SeaFrames("ground-1");
                for (int ground = 1; ground < Navigation.Grounds.Count; ground++)
                {
                    if (!RequestSailMode() || !SailTo(Navigation.Grounds[ground].Centre)) { Fail("ground route"); yield break; }
                    if (ground == 1)
                    {
                        // Advance enough physical time for a full fading wake and cruise framing.
                        for (int n = 0; n < 100 && !Sailor.Arrived; n++) Tick(.05f);
                        yield return SeaFrames("mid-sail");
                    }
                    if (!ArriveSeaCapture() || !FishHere()) { Fail("ground anchor"); yield break; }
                    yield return SeaFrames("ground-" + (ground + 1));
                }
                if (!RequestSailMode()) { Fail("border Sail mode"); yield break; }
                var bounds = Navigation.CameraBounds;
                var border = Navigation.Resolve(Navigation.Snap(new Vector2(bounds.xMax + 100, bounds.center.y)));
                if (!SailTo(border) || !ArriveSeaCapture()) { Fail("fog border"); yield break; }
                yield return SeaFrames("fog-border");
                // A wide inspection of the same native sea shows the unreachable dressing
                // and ocean beyond the buoy line. Anchored captures above use normal zoom.
                ZoomOffset = 100; snapCamera = true; Visual(.05f);
                yield return SeaFrames("horizon");
                ZoomOffset = 0;
                // Return must keep the SeaV2 scene/UI until the navigation harbour is reached.
                HeadHome();
                for (int n = 0; n < 100 && CurrentMode == Mode.SailingHome; n++) Tick(.05f);
                if (CurrentMode != Mode.SailingHome || Navigation == null) { Fail("premature harbour"); yield break; }
                yield return SeaFrames("home-mid");
                for (int n = 0; n < 20000 && CurrentMode == Mode.SailingHome; n++) Tick(.05f);
                if (CurrentMode != Mode.Harbour || Navigation != null) { Fail("harbour arrival"); yield break; }
                for (int n = 0; n < 80; n++) Visual(.05f);
                yield return SeaFrames("home-arrived");
                Debug.Log("[Catchline] SEA MAP CAPTURED " + Sea.SeaNav.Maps[map]);
                yield return null;
            }
            Debug.Log("[Catchline] SEA CAPTURES COMPLETE"); Application.Quit(0);

            void Fail(string stage) { Debug.LogError("[Catchline] Sea capture failed at " + stage + " / " + ActiveSpot); Application.Quit(8); }
            IEnumerator SeaFrames(string state)
            {
                toastUntil = 0;
                foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
                {
                    Screen.SetResolution(size.x, size.y, false);
                    for (int n = 0; n < 20; n++) yield return null;
                    PrepareInterface(size.x, size.y);
                    snapCamera = true; Visual(.05f);
                    for (int n = 0; n < 8; n++) yield return null;
                    string name = Sea.SeaNav.Maps[ActiveSpot] + "-" + state + "-" + size.x;
                    yield return new WaitForEndOfFrame();
                    var frame = ScreenCapture.CaptureScreenshotAsTexture();
                    File.WriteAllBytes(Path.Combine(directory, name + ".png"), frame.EncodeToPNG());
                    Destroy(frame);
                    Debug.Log("[Catchline] SEA FRAME " + name + " position=" + (Sailor != null ? Sailor.Position.ToString() : "harbour") + " mode=" + CurrentMode + " sail=" + SailMode);
                }
            }
        }
        bool ArriveSeaCapture()
        {
            for (int n = 0; n < 12000 && CurrentMode != Mode.Fishing; n++) Tick(.05f);
            // Let camera/bank finish settling without allowing fishing AI to deploy gear.
            for (int n = 0; n < 80; n++) Visual(.05f);
            return CurrentMode == Mode.Fishing && Sailor.Arrived;
        }
    }
}

#if UNITY_EDITOR
namespace Catchline.EditorTools
{
    public static class SeaCaptureBuild
    {
        public static void Run()
        {
            if (!UnityEngine.Application.dataPath.Replace('\\', '/').EndsWith("Catchline-ui2-sim/Assets", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Sea acceptance build is restricted to Catchline-ui2-sim.");
            var scene = UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.EmptyScene);
            var game = new GameObject("Sea acceptance TEST").AddComponent<Catchline.Game.VoyageGame>();
            game.SessionOnly = true;
            const string fixture = "Assets/SeaAcceptance.unity";
            UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene, fixture);
            Directory.CreateDirectory("Builds/SeaCapture"); Directory.CreateDirectory("Logs");
            var result = UnityEditor.BuildPipeline.BuildPlayer(new UnityEditor.BuildPlayerOptions
            {
                scenes = new[] { fixture }, locationPathName = "Builds/SeaCapture/Catchline.exe",
                target = UnityEditor.BuildTarget.StandaloneWindows64,
                options = UnityEditor.BuildOptions.None
            });
            File.WriteAllText("Logs/sea-build.txt", result.summary.result.ToString());
            Debug.Log("[Catchline] Sea TEST native build " + result.summary.result);
        }
    }
}
#endif

using System;
using System.Collections;
using System.IO;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        bool captureFreeze;

        // TEST launches never read or write the save; -capture-uiv2 drives the save-isolated v2 review.
        void Start()
        {
            var args = Environment.GetCommandLineArgs();
            // A batchmode capture can leave the project's saved time scale at 0, and a build made from that project then
            // starts with a frozen clock (10-26: intro stuck, nothing moves). Captures set their own freeze after this.
            if (Time.timeScale != 1f) { Debug.LogWarning($"[Catchline] Time scale was {Time.timeScale}; reset to 1"); Time.timeScale = 1f; }
            Debug.Log($"[Catchline] Launch mode: {(SessionOnly ? "TEST / no save reads or writes" : "REAL / persistent progress")}; save={GameState.SavePath}");
            StartUiV2Capture(args);
            if (SessionOnly && TestDayRequested) StartTestDay();
            if (Array.IndexOf(args, "-native-display") >= 0)
            {
                int width = Display.main.systemWidth, height = Display.main.systemHeight;
                Screen.SetResolution(width, height, FullScreenMode.FullScreenWindow);
                Debug.Log($"[Catchline] Native borderless display requested: {width}x{height}; render scale 1");
            }
        }


        void CaptureUntil(Func<bool> done, string state)
        {
            for (int n = 0; n < 1200 && !done(); n++) Tick(.05f);
            if (!done()) throw new InvalidOperationException("Capture did not reach " + state);
        }

        IEnumerator CaptureFrame(string directory, string name)
        {
            yield return new WaitForEndOfFrame();
            var frame = ScreenCapture.CaptureScreenshotAsTexture();
            if (frame == null) throw new InvalidOperationException("Native capture has no render target.");
            File.WriteAllBytes(Path.Combine(directory, name + ".png"), frame.EncodeToPNG());
            Destroy(frame);
        }


    }
}

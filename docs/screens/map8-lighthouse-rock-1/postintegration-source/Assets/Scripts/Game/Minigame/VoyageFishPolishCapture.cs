using System.Collections;
using System.IO;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // HARBOUR-IMPORT-1: bounded evidence for rod-view polish items 3-5 only.
        IEnumerator CaptureFishPolish(string directory)
        {
            Application.runInBackground = true; captureFreeze = true;
            Directory.CreateDirectory(directory); yield return null; Time.timeScale = 0;
            foreach (var size in UiV2Sizes)
            {
                if (!Application.isEditor)
                { Screen.SetResolution(size.x, size.y, false); for (int n = 0; n < 20; n++) yield return null; }
                if (!StageFishViewCapture()) { QuitCapture(6); yield break; }
                Tick(.6f); yield return Frame("cast-mid");
                Tick(.65f);
                var rod = Manning;
                for (int n = 0; n < 1500 && rod.Reading.Phase != FishPhase.Inspect; n++) Tick(.01f);
                yield return Frame("waiting");
                bool fake = false, bubbles = false;
                for (int n = 0; n < 3000 && rod.Reading.Phase != FishPhase.Take; n++)
                {
                    Tick(.01f);
                    if (!bubbles && rod.Reading.Dart)
                    { bubbles = true; Tick(.08f); yield return Frame("bubbles"); }
                    if (!fake && rod.Reading.Phase == FishPhase.Fake && rod.Reading.Dip > .25f)
                    { fake = true; yield return Frame("fake"); }
                }
                if (!fake || !bubbles || rod.Reading.Phase != FishPhase.Take)
                { Debug.LogError("[Catchline] FISH POLISH fixture missed cue"); QuitCapture(6); yield break; }
                Tick(.2f); yield return Frame("take");
                ReelInRodView();
                for (int n = 0; n < 800 && RodViewActive; n++) Tick(.025f);
                if (RodViewActive) { QuitCapture(6); yield break; }
                yield return Frame("restored-deck");

                IEnumerator Frame(string name)
                {
                    Cam.aspect = size.x / (float)size.y;
                    PrepareInterface(size.x, size.y); Visual(0);
                    for (int n = 0; n < 2; n++) yield return null;
                    if (Application.isEditor) yield return CompositeFrame(directory, name + "-" + size.x, size);
                    else yield return CaptureFrame(directory, name + "-" + size.x);
                    Debug.Log("[Catchline] FISH POLISH frame " + name + "-" + size.x);
                }
            }
            Debug.Log("[Catchline] FISH POLISH CAPTURES COMPLETE"); QuitCapture(0);
        }
    }
}

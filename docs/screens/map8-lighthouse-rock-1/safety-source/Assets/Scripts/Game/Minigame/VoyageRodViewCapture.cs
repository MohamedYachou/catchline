using System;
using System.Collections;
using System.IO;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Deterministic TEST-only fixture. It selects a real cod roll, then uses Cast/Tick/StrikeTap.
        public bool StageFishViewCapture()
        {
            if (!SessionOnly) return false;
            StartTestTier(0); captureFreeze = true; showTitle = paused = false; rodViewCasts = 2;
            State.Charts.Add(4); SelectedSpot = 4; SetSail();
            for (int n = 0; n < 12000 && CurrentMode != Mode.Fishing; n++) Tick(.05f);
            if (CurrentMode != Mode.Fishing) return false;
            Tick(3); toastUntil = catchUntil = 0;
            var rod = Rods[0];
            Captain.Stop(); Captain.Place(rod.Tile); Captain.Face(rod.Outward);
            Manning = rod; AwaitingCast = false; rod.State = RodState.Ready; rod.Scraps = rod.Squid = rod.Chum = false;
            // Species and kg stay selected by the production RollFish API. Rewind only the fixture RNG.
            int seed;
            for (seed = 1; seed < 10000; seed++)
            {
                State.Rng = new System.Random(seed);
                var rolled = State.RollFish(ActiveSpot, .7f);
                if (rolled.Item1 == Species.Cod && rolled.Item2 > 5f) break;
            }
            if (seed == 10000) return false;
            State.Rng = new System.Random(seed); rod.Cast(this, .7f); Visual(0);
            Debug.Log($"[Catchline] FISH VIEW fixture seed={seed} fish={rod.HookedSpecies} kg={rod.HookedKg:F4}");
            return rod.HookedSpecies == Species.Cod;
        }

        IEnumerator CaptureFishView(string directory)
        {
            Application.runInBackground = true; captureFreeze = true;
            Directory.CreateDirectory(directory);
            yield return null;
            // Freeze Unity animation time as well; only the explicit simulation clock advances.
            Time.timeScale = 0;
            foreach (var size in UiV2Sizes)
            {
                if (!Application.isEditor)
                { Screen.SetResolution(size.x, size.y, false); for (int n = 0; n < 20; n++) yield return null; }
                if (!StageFishViewCapture()) { Debug.LogError("[Catchline] FISH VIEW capture fixture failed"); QuitCapture(6); yield break; }
                PrepareInterface(size.x, size.y);
                for (int frame = 0; frame <= 12; frame++)
                {
                    if (frame > 0) Tick(.1f);
                    yield return RodFrame($"cast-{frame:00}", size);
                    if (frame == 6) yield return RodFrame("cast-mid", size);
                }
                var r = Manning;
                while (r.Reading.Phase != FishPhase.Inspect && r.Reading.Phase != FishPhase.Nibble) Tick(.025f);
                yield return RodFrame("waiting", size);
                bool fake = false;
                float previousFakeDip = -1;
                for (int n = 0; n < 2000; n++)
                {
                    Tick(.01f);
                    if (r.Reading.Phase == FishPhase.Fake && r.Reading.RodPull > .35f && Mathf.Abs(r.Reading.Dip - previousFakeDip) < .00001f)
                    { fake = true; yield return RodFrame("fake", size); break; }
                    previousFakeDip = r.Reading.Phase == FishPhase.Fake ? r.Reading.Dip : -1;
                    if (r.Reading.Phase == FishPhase.Take) break;
                }
                if (!fake) { Debug.LogError("[Catchline] FISH VIEW fixture lacked deep fake"); QuitCapture(6); yield break; }
                for (int n = 0; n < 3000 && r.Reading.Phase != FishPhase.Take; n++) Tick(.01f);
                Tick(.2f); yield return RodFrame("take", size);
                StrikeTap();
                int count = Mathf.CeilToInt((r.ReturnAt + Rod.ReturnSeconds) * 10);
                bool lifted = false;
                for (int frame = 0; frame <= count; frame++)
                {
                    if (frame > 0) Tick(.1f);
                    yield return RodFrame($"landing-{frame:00}", size);
                    if (!lifted && r.ResultAge >= r.ThrashSeconds + .75f)
                    { yield return RodFrame("lifted", size); lifted = true; }
                }
                if (RodViewActive || Stats.Landed != 1) { Debug.LogError("[Catchline] FISH VIEW result delivery failed"); QuitCapture(6); yield break; }
                yield return RodFrame("back", size);
            }
            Debug.Log("[Catchline] FISH VIEW CAPTURES COMPLETE"); QuitCapture(0);

            IEnumerator RodFrame(string name, Vector2Int size)
            {
                PrepareInterface(size.x, size.y); Visual(0);
                // These are actual native screen frames, including the retained Canvas.
                for (int n = 0; n < 2; n++) yield return null;
                string filename = name + "-" + size.x;
                if (Application.isEditor) yield return CompositeFrame(directory, filename, size);
                else yield return CaptureFrame(directory, filename);
                Debug.Log($"[Catchline] FISH VIEW frame {filename}");
            }
        }
    }
}

using System;
using System.Collections;
using System.IO;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        bool captureFreeze;

        // Opt-in presentation checks run only in the save-isolated preview scene.
        // These are real player frames including OnGUI, not camera-only mockups.
        void Start()
        {
            var args = Environment.GetCommandLineArgs();
            Debug.Log($"[Catchline] Launch mode: {(SessionOnly ? "TEST / no save reads or writes" : "REAL / persistent progress")}; save={GameState.SavePath}");
            if (!SessionOnly && Application.isBatchMode && Array.IndexOf(args, "-persistence-probe") >= 0)
            {
                int probe = Array.IndexOf(args, "-save-check-root");
                if (probe < 0 || probe + 1 >= args.Length || !System.IO.Path.GetFileName(System.IO.Path.GetFullPath(args[probe + 1]).TrimEnd(System.IO.Path.DirectorySeparatorChar)).StartsWith("net023-probe-")) { Application.Quit(3); return; }
                if (Array.IndexOf(args, "-probe-write") >= 0)
                {
                    State.Coins = 4321; State.Hull = 2; State.Owned.Add(UpgradeId.NetSystem);
                    State.EnsureCrewRoleOffers();
                    State.UnsoldCatch.Clear(); State.UnsoldCatch.Add(new CaughtFish { Species = Species.Cod, Kg = 6 });
                    State.Save();
                    Debug.Log("[Catchline] PERSISTENCE PROBE WRITE PASSED");
                }
                else if (State.Coins == 4321 && State.Hull == 2 && State.Has(UpgradeId.NetSystem) && State.UnsoldCatch.Count == 1 && State.UnsoldCatch[0].Kg == 6
                    && State.Board.FindAll(c => c.Role == CrewRole.Fisherman).Count >= State.HullDef.CrewCap
                    && State.Board.FindAll(c => c.Role == CrewRole.Deckhand).Count >= State.HullDef.CrewCap)
                    Debug.Log("[Catchline] PERSISTENCE PROBE RELOAD PASSED");
                else { Debug.LogError("[Catchline] Persistence probe failed"); Application.Quit(4); return; }
                Application.Quit(0); return;
            }
            if (SessionOnly && Array.IndexOf(args, "-prepboat-trial") >= 0)
            {
                if (!StartPrepBoatTrial()) Debug.LogError("[Catchline] Could not start Tier4 prep boat trial");
                else Debug.Log("[Catchline] TIER033 trial: approved6.8x3.5m hull, four temporary crew, no save reads or writes; processing orders pending");
                if (Array.IndexOf(args, "-prepboat-ice") >= 0) { State.Owned.Add(UpgradeId.IceBox); SyncUpgrades(); }
            }
            else if (SessionOnly && Array.IndexOf(args, "-crew-mix-trial") >= 0)
            {
                if (!StartCrewMixTrial()) Debug.LogError("[Catchline] Could not start the crew mix trial");
                else Debug.Log("[Catchline] Crew mix trial: compact fisher at harbour, empty berths,1000coins,temporary contracts,save isolated");
            }
            else if (SessionOnly && Array.IndexOf(args, "-netboat-trial") >= 0)
            {
                StartNetBoatTrial();
                Debug.Log("[Catchline] Net boat trial: hull2,200coins,2fishers+1deckhand,60bait,full fuel; save isolated");
            }
            else if (SessionOnly && Array.IndexOf(args, "-deep-net-trial") >= 0)
            {
                if (Array.IndexOf(args, "-netboat-trial") < 0) StartNetBoatTrial();
                State.SelectedNet = NetKind.Deep; State.DeepNetUses.Clear(); State.DeepNetUses.AddRange(new[] { 3, 3 });
                Debug.Log($"[Catchline] Weight020 deep net trial: {State.CoolerCapacity:0.#}kg hold, deep3uses+reserve,200coins; save isolated");
            }
            int prepCapture = Array.IndexOf(args, "-capture-tier4");
            if (SessionOnly && prepCapture >= 0 && prepCapture + 1 < args.Length)
            {
                if (!IsPrepFisher) StartPrepBoatTrial();
                StartCoroutine(CapturePrepBoat(Path.GetFullPath(args[prepCapture + 1])));
            }
            if (Array.IndexOf(args, "-native-display") >= 0)
            {
                int width = Display.main.systemWidth, height = Display.main.systemHeight;
                Screen.SetResolution(width, height, FullScreenMode.FullScreenWindow);
                Debug.Log($"[Catchline] Native borderless display requested: {width}x{height}; render scale1");
            }
            if (SessionOnly && Array.IndexOf(args, "-chart-review") >= 0)
            {
                if (Array.IndexOf(args, "-netboat-trial") < 0) StartNetBoatTrial();
                Showcase(-1, 0); hudTab = HudTab.HarbourMaster; panelOpen = true; toastUntil = 0;
                RefreshInterface();
                var plate = Resources.Load<Texture2D>("Charts/gull-coast");
                if (plate == null) Debug.LogError("[Catchline] Illustrated chart resource missing");
                else Debug.Log($"[Catchline] Illustrated chart ready: {plate.width}x{plate.height}; live native markers, routes and navigation; save isolated");
            }
            int flag = Array.IndexOf(args, "-capture-voyage");
            if (SessionOnly && flag >= 0 && Application.isBatchMode)
            {
                Debug.LogError("[Catchline] Native HUD capture needs a rendered player window; use scratch RenderMaps for background camera-only checks.");
                Application.Quit(2);
                return;
            }
            if (SessionOnly && flag >= 0 && flag + 1 < args.Length)
                StartCoroutine(Array.IndexOf(args, "-capture-polish") >= 0 ? CapturePolish(Path.GetFullPath(args[flag + 1]))
                    : Array.IndexOf(args, "-capture-urgent") >= 0 ? CaptureUrgent(Path.GetFullPath(args[flag + 1])) : CaptureVoyage(Path.GetFullPath(args[flag + 1])));
        }

        IEnumerator CapturePolish(string directory)
        {
            Directory.CreateDirectory(directory);
            Application.runInBackground = true;
            captureFreeze = true;
            AutoPlay = showTitle = false;
            State.FoodMinutes = 20;
            for (int spot = 0; spot < GameData.Spots.Length; spot++) State.Charts.Add(spot);
            // Real route actions, frozen at readable manoeuvre stages for framing review.
            for (int spot = 0; spot < GameData.Spots.Length; spot++)
            {
                SelectedSpot = spot;
                SetSail();
                float duration = GameData.Spots[spot].RowSeconds;
                Tick(duration * .17f);
                yield return CaptureFrame(directory, $"route-{spot}-01-clearance");
                Tick(duration * .27f);
                yield return CaptureFrame(directory, $"route-{spot}-02-bearing");
                Tick(duration * .28f);
                yield return CaptureFrame(directory, $"route-{spot}-03-channel-approach");
                CaptureUntil(() => CurrentMode == Mode.Fishing, "route fishing");
                Tick(4f);
                yield return CaptureFrame(directory, $"map-{spot}-03-fishing");
                if (spot == 0)
                {
                    // Native moving-water sequence; no camera-only rendering or compositing.
                    for (int n = 0; n < 12; n++)
                    {
                        Tick(.12f);
                        yield return CaptureFrame(directory, $"water-motion-{n:00}");
                    }
                    captureFreeze = false;
                    yield return null;
                    double total = 0;
                    float worst = 0;
                    for (int frame = 0; frame < 180; frame++)
                    {
                        yield return null;
                        total += Time.unscaledDeltaTime;
                        worst = Mathf.Max(worst, Time.unscaledDeltaTime);
                    }
                    captureFreeze = true;
                    Debug.Log($"[Catchline] NATIVE FRAME SAMPLE: {Screen.width}x{Screen.height}, {180 / total:0.0} fps mean, worst {worst * 1000:0.0}ms, GPU {SystemInfo.graphicsDeviceName}; desktop sample, not mobile hardware validation");
                    Debug.Log($"[Catchline] AUDIO: listeners={FindObjectsByType<AudioListener>(FindObjectsSortMode.None).Length}, sampleRate={AudioSettings.outputSampleRate}, coastalBed={GetComponent<AudioSource>()?.isPlaying}");
                }
                HeadHome();
                Tick(duration * .84f);
                yield return CaptureFrame(directory, $"route-{spot}-04-align");
                Tick(duration * .10f);
                yield return CaptureFrame(directory, $"route-{spot}-05-sideways-berth");
                CaptureUntil(() => CurrentMode == Mode.Harbour, "route home");
                Tick(3.5f);
                yield return CaptureFrame(directory, $"route-{spot}-06-moored");
            }
            // Preserve the existing full fishing/market/settings walkthrough too.
            SelectedSpot = 0;
            yield return CaptureVoyage(directory);
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

        IEnumerator CaptureUrgent(string directory)
        {
            Directory.CreateDirectory(directory);
            Application.runInBackground = true;
            captureFreeze = true;
            AutoPlay = false;
            showTitle = false;
            Ui.Init();
            // Save-isolated fixture: fund the ordinary hire actions, then test being broke.
            State.Coins = 1000;
            OpenShop(HudTab.CrewOffice);
            yield return null;
            yield return CaptureFrame(directory, "01-guaranteed-crew");
            State.Hire(State.Board.Find(c => c.Role == CrewRole.Deckhand));
            State.Hire(State.Board.Find(c => c.Role == CrewRole.Fisherman));
            SyncCrew(); SyncUpgrades();
            yield return CaptureFrame(directory, "02-two-crew-hired");
            State.Coins = 0; State.Bait = 0; State.Squid = 0; State.FoodMinutes = 20;
            SetSail();
            CaptureUntil(() => CurrentMode == Mode.Fishing, "fishing");
            Tick(4f);
            yield return CaptureFrame(directory, "03-free-bait-two-rods");
            var rod = Rods[0];
            CommandRod(rod);
            CaptureUntil(() => rod.State == RodState.Bite, "bite");
            yield return CaptureFrame(directory, "04-bite");
            StrikeTap();
            CaptureUntil(() => AwaitingCast, "throw again choice");
            Tick(2f);
            yield return CaptureFrame(directory, "05-throw-or-leave");
            ThrowAgain();
            CaptureUntil(() => rod.State == RodState.Bite, "second bite");
            StrikeTap();
            CaptureUntil(() => AwaitingCast, "second catch");
            Tick(5f);
            yield return CaptureFrame(directory, "06-haul-value");
            LeaveFishing(); HeadHome();
            CaptureUntil(() => CurrentMode == Mode.Harbour, "port");
            Tick(4f);
            yield return CaptureFrame(directory, "07-sell-preview");
            SellHaul();
            yield return CaptureFrame(directory, "08-paid-receipt");
            Debug.Log($"[Catchline] URGENT PRESENTATION COMPLETE: {Screen.width}x{Screen.height}, {directory}");
            Application.Quit(0);
        }

        IEnumerator CaptureVoyage(string directory)
        {
            Directory.CreateDirectory(directory);
            Application.runInBackground = true;
            captureFreeze = true;
            AutoPlay = false;
            // Consistent typography for review; the user's stored preference is untouched.
            Ui.Init();
            showTitle = true;
            yield return null;
            yield return CaptureFrame(directory, "01-menu");
            showTitle = false;
            yield return CaptureFrame(directory, "02-harbour");
            SetSail();
            CaptureUntil(() => CurrentMode == Mode.Fishing, "fishing");
            Tick(4f); // settle the actual camera and dismiss the arrival toast
            yield return CaptureFrame(directory, "03-fishing");
            var rod = Rods[0];
            CommandRod(rod);
            CaptureUntil(() => rod.State == RodState.Waiting, "waiting");
            Tick(.6f);
            yield return CaptureFrame(directory, "04-waiting");
            CaptureUntil(() => rod.State == RodState.Bite, "bite");
            yield return CaptureFrame(directory, "05-bite");
            StrikeTap();
            CaptureUntil(() => OnDeck.Count > 0 && CanCarry(OnDeck[0]), "landed fish");
            yield return CaptureFrame(directory, "06-catch");
            CommandCarry(OnDeck[0]);
            CaptureUntil(() => Cooler.Count == 1, "stowed fish");
            yield return CaptureFrame(directory, "07-stowed");
            HeadHome();
            CaptureUntil(() => CurrentMode == Mode.Harbour, "sale");
            Tick(3.5f);
            yield return CaptureFrame(directory, "08-unsold");
            SellHaul();
            yield return CaptureFrame(directory, "08-sale");
            OpenShop(HudTab.Chandlery);
            yield return CaptureFrame(directory, "09-chandlery");
            OpenShop(HudTab.HarbourMaster);
            yield return CaptureFrame(directory, "10-chart");
            paused = true;
            yield return CaptureFrame(directory, "11-pause");
            showSettings = true;
            yield return CaptureFrame(directory, "12-settings");
            Debug.Log($"[Catchline] PRESENTATION CAPTURE COMPLETE: {Screen.width}x{Screen.height}, {directory}");
            Application.Quit(0);
        }
    }
}

using System.Linq;
using System.Collections;
using System.IO;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public bool IsPrepFisher => State != null && State.Hull == 3;
        public Vector2Int[] PrepWorkerTiles { get; private set; } = System.Array.Empty<Vector2Int>();
        Transform rawBuckets, rawIceCoolers;

        void ConfigurePrepFisher(GameObject model)
        {
            rawBuckets = ArtLibrary.Find(model, "RawBuckets");
            rawIceCoolers = ArtLibrary.Find(model, "RawIceCoolers");
            SyncPrepStorage(); // Route rasterization must see only the active variant.
            PrepWorkerTiles = new[] { "PrepWorker_1", "PrepWorker_2" }
                .Select(n => Grid.GetTile(Boat.InverseTransformPoint(ArtLibrary.Find(model, n).position))).ToArray();
        }

        void SyncPrepStorage()
        {
            bool ice = State.Has(UpgradeId.IceBox);
            if (rawBuckets != null) rawBuckets.gameObject.SetActive(!ice);
            if (rawIceCoolers != null) rawIceCoolers.gameObject.SetActive(ice);
        }

        IEnumerator CapturePrepBoat(string directory)
        {
            Directory.CreateDirectory(directory);
            Application.runInBackground = true;
            captureFreeze = true;
            State.Owned.Remove(UpgradeId.IceBox); SyncUpgrades();
            foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            {
                Screen.SetResolution(size.x, size.y, FullScreenMode.Windowed);
                // Let the native swapchain, shaders and canvas settle after resize.
                for (int frame = 0; frame < 16; frame++) yield return null;
                Showcase(0, 0); captureFreeze = true; toastUntil = 0; Tick(.01f);
                yield return CaptureFrame(directory, "tier4-buckets-" + size.x);
            }
            Showcase(-1, 0); State.Owned.Add(UpgradeId.IceBox); SyncUpgrades();
            foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            {
                Screen.SetResolution(size.x, size.y, FullScreenMode.Windowed);
                // Let the native swapchain, shaders and canvas settle after resize.
                for (int frame = 0; frame < 16; frame++) yield return null;
                Showcase(0, 0); captureFreeze = true; toastUntil = 0; Tick(.01f);
                yield return CaptureFrame(directory, "tier4-ice-coolers-" + size.x);
            }
            Debug.Log("[Catchline] TIER033 NATIVE CAPTURES COMPLETE " + directory);
            Application.Quit(0);
        }

        // First integration: shipyard trial, not an unbalanced paid progression step.
        // Changing hulls is restricted to port and never touches a real save.
        public bool TrialPrepFisher()
        {
            if (!SessionOnly || CurrentMode != Mode.Harbour || IsPrepFisher) return false;
            State.Hull = 3;
            State.Fuel = State.FuelCapacity;
            State.EnsureCrewRoleOffers();
            RebuildBoat();
            Toast("Prep fisher trial · four crew berths. Preparation and chum orders are coming next.");
            return true;
        }

        public bool StartPrepBoatTrial()
        {
            if (!SessionOnly) return false;
            NewGame();
            if (!TrialPrepFisher()) return false;
            State.Coins = 1000;
            foreach (var role in new[] { CrewRole.Deckhand, CrewRole.Deckhand, CrewRole.Fisherman, CrewRole.Fisherman })
            {
                State.EnsureCrewRoleOffers();
                State.Hire(State.Board.First(c => c.Role == role));
            }
            State.Coins = 200;
            State.Bait = 60;
            SyncCrew();
            showTitle = paused = showSettings = panelOpen = captureFreeze = netOrdersOpen = false;
            ActiveSpot = SelectedSpot = 0;
            voyageStart = SimTime;
            Showcase(0, 0);
            toastUntil = 0;
            return true;
        }
    }
}

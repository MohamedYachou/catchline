using System.Linq;
using System.Collections;
using System.IO;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public bool IsPrepFisher => State != null && State.Hull >= 3;
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


        // First integration: shipyard trial, not an unbalanced paid progression step.
        // Changing hulls is restricted to port and never touches a real save.
        public bool TrialPrepFisher()
        {
            if (!SessionOnly || CurrentMode != Mode.Harbour || IsPrepFisher) return false;
            State.Hull = 3;
            State.Fuel = State.FuelCapacity;
            State.EnsureCrewRoleOffers();
            RebuildBoat();
            Toast("Prep fisher trial · four crew berths. Assign up to two deckhands to the prep table.");
            return true;
        }

        public bool StartPrepBoatTrial()
        {
            if (!SessionOnly) return false;
            NewGame();
            if (!TrialPrepFisher()) return false;
            State.GrantTrialCards();
            State.Coins = 1000;
            foreach (var role in new[] { CrewRole.Deckhand, CrewRole.Deckhand, CrewRole.Fisherman, CrewRole.Fisherman })
            {
                State.EnsureCrewRoleOffers();
                State.Hire(State.Board.First(c => c.Role == role));
            }
            State.ExtraCrew.First(c => c.Role == CrewRole.Deckhand).WorkPreference = DeckhandWork.Prep;
            State.Coins = 2200; // Save-isolated module trial: buy the2000refit and keep200supplies.
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

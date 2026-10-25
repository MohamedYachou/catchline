using System;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // Crab pots for the smaller boats (hulls 1-3): bought in Supplies, set beside the boat at every fishing ground and
    // hauled by the captain once they have soaked, with the same pull / free / sort cage view as the Tier 5 buoys
    // (Minigame/VoyageCageView.cs). They reuse the Tier 5 buoy slots, timers and landing code (VoyageTier5.cs).
    public partial class VoyageGame
    {
        public const int CrabPotCost = 120;
        public int MaxCrabPots => State == null ? 0 : State.Hull == 1 ? 1 : State.Hull is 2 or 3 ? 2 : 0;
        public int PotsSet => IsTier5 ? 0 : buoyAnchors.Length;

        public bool BuyCrabPot()
        {
            if (CurrentMode != Mode.Harbour || State.CrabPots >= MaxCrabPots || State.Coins < CrabPotCost) return false;
            State.Coins -= CrabPotCost; State.CrabPots++;
            RebuildBoat(false); SaveGame();
            return true;
        }

        // Slots for the owned pots in the water beside the boat, each worked from the open deck tile nearest it.
        bool ConfigurePotLine()
        {
            int n = Mathf.Min(State.CrabPots, MaxCrabPots);
            buoyTiles = Array.Empty<Vector2Int>(); buoyAnchors = Array.Empty<Vector3>();
            for (int i = 0; i < 2; i++) { buoyTimers[i] = 0; buoyWorkers[i] = null; }
            if (IsTier5 || n == 0 || Grid == null) return false;
            var open = Enumerable.Range(0, Grid.Width).SelectMany(x => Enumerable.Range(0, Grid.Height).Select(y => new Vector2Int(x, y)))
                .Where(t => !Grid.IsBlocked(t)).ToArray();
            if (open.Length == 0) return false;
            float water = Boat.InverseTransformPoint(new Vector3(0, Rod.WaterY, 0)).y;
            buoyAnchors = new Vector3[n]; buoyTiles = new Vector2Int[n];
            for (int i = 0; i < n; i++)
            {
                Vector2Int tile; Vector3 at;
                if (State.Hull == 1)
                {
                    // The skiff's pot rides behind the outboard.
                    int stern = open.Max(t => t.x);
                    float middle = (Grid.Height - 1) * .5f;
                    tile = open.Where(t => t.x == stern).OrderBy(t => Mathf.Abs(t.y - middle)).First();
                    at = Grid.GetLocal(new Vector2Int(stern, 0)) + new Vector3(1.6f, 0, middle * Grid.CellSize);
                }
                else
                {
                    // The fishers' pots hang off the near rail, well forward and well aft of midships.
                    int rail = open.Min(t => t.y), mid = Mathf.RoundToInt((open.Min(t => t.x) + open.Max(t => t.x)) * .5f) + (i == 0 ? -2 : 2);
                    tile = open.Where(t => t.y == rail).OrderBy(t => Mathf.Abs(t.x - mid)).First();
                    at = Grid.GetLocal(new Vector2Int(tile.x, rail)) + new Vector3(0, 0, -1.5f);
                }
                buoyTiles[i] = tile; buoyAnchors[i] = new Vector3(at.x, water, at.z);
            }
            return true;
        }

        // Pots only soak while the boat lies at a ground; on passage they ride aboard, out of sight.
        bool TickPot(int i)
        {
            bool set = AtFishingGround;
            if (buoyModels[i] != null && buoyModels[i].gameObject.activeSelf != set) buoyModels[i].gameObject.SetActive(set);
            return set;
        }

        void InterfacePotLine()
        {
            if (IsTier5 || buoyAnchors.Length == 0 || CurrentMode != Mode.Fishing || !AtFishingGround || PrepOrdersOpen || netOrdersOpen || baitSettingsCrew != null) return;
            for (int i = 0; i < buoyAnchors.Length; i++)
            {
                bool ready = BuoyRemaining(i) <= 0, busy = buoyWorkers[i] != null;
                if (busy) continue;
                InterfaceBubble("pots/" + i, Boat.TransformPoint(buoyAnchors[i] + Vector3.up * .8f), ready ? "Haul" : Mathf.CeilToInt(BuoyRemaining(i)) + "s",
                    "v2-icon-cage", () => TryBuoyWork(Captain), ready);
            }
        }

        void InterfaceCrabPotProduct()
        {
            if (MaxCrabPots == 0) return;
            bool full = State.CrabPots >= MaxCrabPots;
            string stock = $"{State.CrabPots}/{MaxCrabPots} aboard.";
            Product("supplies/crabpot", "Crab pot",
                "Set beside the boat at every ground. When it has soaked, haul it yourself: tap to winch, drag it free of snags, flick crabs to keep or throw back. " + stock,
                "v2-icon-cage", full ? "Pots full" : $"Buy · {CrabPotCost} coins", !full && State.Coins >= CrabPotCost,
                () => { if (BuyCrabPot()) Toast("Crab pot aboard. Haul it when it has soaked."); },
                full ? stock + (State.Hull < 2 ? " A bigger boat carries two." : "") : State.Coins < CrabPotCost ? CoinShortfall(CrabPotCost) + "." : null);
        }
    }
}

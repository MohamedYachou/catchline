using System;
using System.Linq;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Sum actual cargo, never a rounded HUD value or a separately cached counter.
        public float HoldKg => (float)Cooler.Sum(f => (double)f.Kg);
        // Mo 10-27: once the hold plus every keeper already aboard reaches capacity, no new cast, set or line starts.
        // Whatever is already out (rods in the water, nets set, fish on deck) still comes in and always boards, however far over.
        public bool HoldFull => Cooler.Sum(f => (double)f.Kg) + AboardKeeperKg >= State.CoolerCapacity;
        float AboardKeeperKg
        {
            get
            {
                double kg = 0;
                void Add(Species s, float w) { if (!Deck.FishRules.Undersize(new CaughtFish { Species = s, Kg = w })) kg += w; }
                foreach (var f in OnDeck) Add(f.Species, f.Kg);
                foreach (var p in People) if (p?.Carrying != null) Add(p.Carrying.Species, p.Carrying.Kg);
                foreach (var f in ProcessingInput.Concat(ProcessingOutput)) kg += f.Kg;
                if (Scheduler != null)
                    foreach (var f in DeckGraph.Baskets.SelectMany(b => b.Fish).Concat(Scheduler.Loose.Select(l => l.Fish)).Concat(Scheduler.Workers.SelectMany(w => w.Hands)))
                        Add(f.Species, f.Kg);
                return (float)kg;
            }
        }
        public bool TryStore(CaughtFish fish, bool carried = true)
        {
            if (fish == null || float.IsNaN(fish.Kg) || float.IsInfinity(fish.Kg) || fish.Kg <= 0 || Cooler.Contains(fish)) return false;
            // Unity callbacks execute sequentially. Recheck on every individual insert,
            // including two workers finishing their animations on the same frame.
            Cooler.Add(fish);
            Abilities?.HoldFill(HoldKg / State.CoolerCapacity);
            if (CurrentMode == Mode.Fishing && !flowReturning)
            {
                Flow.Record(FlowTelemetry.Kind.Stored, fish.Kg, carried: carried);

            }
            return true;
        }
    }
}

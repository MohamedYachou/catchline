using System;
using System.Linq;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Sum actual cargo, never a rounded HUD value or a separately cached counter.
        public float HoldKg => (float)Cooler.Sum(f => (double)f.Kg);
        public bool HoldFull => Cooler.Sum(f => (double)f.Kg) >= State.CoolerCapacity;
        public bool TryStore(CaughtFish fish, bool carried = true)
        {
            if (fish == null || float.IsNaN(fish.Kg) || float.IsInfinity(fish.Kg) || fish.Kg <= 0 || HoldFull || Cooler.Contains(fish)) return false;
            // Unity callbacks execute sequentially. Recheck on every individual insert,
            // including two workers finishing their animations on the same frame.
            Cooler.Add(fish);
            if (CurrentMode == Mode.Fishing && !flowReturning)
            {
                Flow.Record(FlowTelemetry.Kind.Stored, fish.Kg, carried: carried);

            }
            return true;
        }
    }
}

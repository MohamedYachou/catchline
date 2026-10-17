using System;
using System.Linq;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Sum actual cargo, never a rounded HUD value or a separately cached counter.
        public float HoldKg => (float)Cooler.Sum(f => (double)f.Kg);
        public bool HoldFull => Cooler.Sum(f => (double)f.Kg) >= State.CoolerCapacity;
        public bool TryStore(CaughtFish fish)
        {
            if (fish == null || float.IsNaN(fish.Kg) || float.IsInfinity(fish.Kg) || fish.Kg <= 0 || HoldFull) return false;
            // Unity callbacks execute sequentially. Recheck on every individual insert,
            // including two workers finishing their animations on the same frame.
            Cooler.Add(fish);
            return true;
        }
    }
}

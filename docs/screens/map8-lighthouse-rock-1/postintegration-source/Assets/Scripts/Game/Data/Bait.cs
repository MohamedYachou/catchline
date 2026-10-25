using System;
using Catchline.Game.Deck;

namespace Catchline.Game
{
    // MASTER-PLAN M3 / BLUEPRINT section 7 / CARDS-AND-SPEEDS section 5. Pure data and logic, not wired yet.
    // Append only: the order is also "worse to better".
    public enum BaitKind { Scraps, Worms, Squid, Chum }

    public sealed class BaitDef
    {
        public readonly BaitKind Kind;
        public readonly string Id, Name;
        public readonly BaitPermission Permission; // the flag a fisher needs to take it (GameStateCrewBait.cs)
        public readonly float BiteFactor;          // CARDS-AND-SPEEDS section 5 baitFactor
        public readonly FishClass Ceiling;         // best class this bait can reach (BLUEPRINT section 7)
        public readonly float[] Weights;           // percent per FishClass White..Red, sums to 100
        public readonly bool Free;                 // scraps only
        // TODO(BLUEPRINT): shop prices for worms and squid are not specified; the departure cost takes bait cost as a number.

        public BaitDef(BaitKind kind, string name, BaitPermission permission, float biteFactor, FishClass ceiling, float[] weights, bool free)
        {
            Kind = kind; Name = name; Id = name.ToLowerInvariant(); Permission = permission; BiteFactor = biteFactor;
            Ceiling = ceiling; Weights = weights; Free = free;
        }
    }

    // Bait stock in the shared bin. Scraps are free and infinite so they have no counter.
    public sealed class BaitStock
    {
        public int Worms, Squid, Chum;

        public BaitStock() { }
        public BaitStock(int worms, int squid, int chum) { Worms = worms; Squid = squid; Chum = chum; }

        public int Count(BaitKind k) => k == BaitKind.Worms ? Worms : k == BaitKind.Squid ? Squid : k == BaitKind.Chum ? Chum : int.MaxValue;

        // Takes one unit. Scraps always succeed; the others fail on an empty bin.
        public bool Take(BaitKind k)
        {
            switch (k)
            {
                case BaitKind.Scraps: return true;
                case BaitKind.Worms: if (Worms <= 0) return false; Worms--; return true;
                case BaitKind.Squid: if (Squid <= 0) return false; Squid--; return true;
                default: if (Chum <= 0) return false; Chum--; return true;
            }
        }
    }

    public static class Bait
    {
        // Class order in every weight array: White, Green, Blue, Purple, Gold, Red.
        public static readonly BaitDef Scraps = new BaitDef(BaitKind.Scraps, "Scraps", BaitPermission.Scraps, 1.0f, FishClass.White,
            new float[] { 100, 0, 0, 0, 0, 0 }, true);
        public static readonly BaitDef Worms = new BaitDef(BaitKind.Worms, "Worms", BaitPermission.Worms, 0.9f, FishClass.Green,
            new float[] { 85, 15, 0, 0, 0, 0 }, false);
        // Squid may luckily reach purple, but never a large one: see ApplyCeiling.
        public static readonly BaitDef Squid = new BaitDef(BaitKind.Squid, "Squid", BaitPermission.Squid, 0.85f, FishClass.Purple,
            new float[] { 55, 30, 13, 2, 0, 0 }, false);
        public static readonly BaitDef Chum = new BaitDef(BaitKind.Chum, "Chum", BaitPermission.Chum, 0.8f, FishClass.Red,
            new float[] { 10, 20, 30, 30, 7, 3 }, false);

        public static readonly BaitDef[] All = { Scraps, Worms, Squid, Chum };

        // DEEP104: deep lines take only chum and keep their own class targets
        // (5% white, 5% green, 10% blue, 75% purple, 3% gold, 2% red).
        public static readonly float[] DeepLineChumWeights = { 5, 5, 10, 75, 3, 2 };

        public static BaitDef Def(BaitKind k) => All[(int)k];

        // Percent chance of `c` for this bait (0 above the bait's ceiling).
        public static float Weight(BaitKind k, FishClass c) => All[(int)k].Weights[(int)c];

        // ---- Rolling -----------------------------------------------------------------------------------------
        // Deterministic given the Random (use new System.Random(seed)). One draw per roll.
        public static FishClass RollClass(float[] weights, Random rng)
        {
            double total = 0;
            for (int i = 0; i < weights.Length; i++) total += weights[i];
            double r = rng.NextDouble() * total, acc = 0;
            int last = 0;
            for (int i = 0; i < weights.Length; i++)
            {
                if (weights[i] <= 0) continue;
                last = i; acc += weights[i];
                if (r < acc) return (FishClass)i;
            }
            return (FishClass)last;
        }

        public static FishClass RollClass(BaitKind kind, Random rng) => RollClass(Def(kind).Weights, rng);
        public static FishClass RollDeepLineChum(Random rng) => RollClass(DeepLineChumWeights, rng);

        // Squid purple is capped at the species' lower half: a purple roll on a fish above the midpoint of its
        // weight range is demoted to blue. Other baits are unchanged (their weights already respect the ceiling).
        // Simplest reading of "never a large one": kg <= (MinKg + MaxKg) / 2 is allowed.
        public static bool PurpleAllowed(BaitKind kind, Species species, float kg)
        {
            if (kind != BaitKind.Squid) return kind == BaitKind.Chum;
            var d = GameData.Get(species);
            return kg <= (d.MinKg + d.MaxKg) * 0.5f;
        }

        public static FishClass ApplyCeiling(BaitKind kind, FishClass rolled, Species species, float kg)
        {
            if (rolled == FishClass.Purple && kind == BaitKind.Squid && !PurpleAllowed(kind, species, kg)) return FishClass.Blue;
            return rolled;
        }

        // ---- Bite wait (CARDS-AND-SPEEDS section 5) ---------------------------------------------------------
        // wait = clamp(6 * spotBiteWait * baitFactor / richness + 2 * power, 4, 12); richness has a 0.3 floor.
        public static float BiteWait(float spotBiteWait, BaitKind kind, float richness, float power)
        {
            float r = Math.Max(0.3f, richness);
            float w = 6f * spotBiteWait * Def(kind).BiteFactor / r + 2f * power;
            return Math.Min(12f, Math.Max(4f, w));
        }

        // ---- Selection ---------------------------------------------------------------------------------------
        // Fishers take the best bait their permissions allow and the bin holds: chum, squid, worms, then scraps.
        // Scraps are free and infinite, and bait never blocks fishing, so scraps are the answer when nothing
        // else is allowed or in stock (even if the scraps flag is off).
        public static BaitKind Best(BaitPermission allowed, BaitStock stock)
        {
            if ((allowed & BaitPermission.Chum) != 0 && stock != null && stock.Chum > 0) return BaitKind.Chum;
            if ((allowed & BaitPermission.Squid) != 0 && stock != null && stock.Squid > 0) return BaitKind.Squid;
            if ((allowed & BaitPermission.Worms) != 0 && stock != null && stock.Worms > 0) return BaitKind.Worms;
            return BaitKind.Scraps;
        }

        // Deep lines accept only self-made chum: allowed and in stock, else the rig stays empty.
        public static bool CanBaitDeepLine(BaitPermission allowed, BaitStock stock) =>
            (allowed & BaitPermission.Chum) != 0 && stock != null && stock.Chum > 0;

        // Pick and spend in one step. Returns the bait used.
        public static BaitKind TakeBest(BaitPermission allowed, BaitStock stock)
        {
            var k = Best(allowed, stock);
            if (stock != null) stock.Take(k);
            return k;
        }
    }
}

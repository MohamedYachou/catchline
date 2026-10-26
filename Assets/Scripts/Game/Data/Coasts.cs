using System.Collections.Generic;

namespace Catchline.Game
{
    // Mo (10-26): the chart has two coasts. The Gull coast (the first five grounds) is the learning water: commons and
    // rares, the odd purple, never gold or red. The Outer coast (every later ground) opens with a tier 3 boat and
    // pays for the trip: bigger specimens, its own big fish, and gold sharks once the boat can land them (tier 4,
    // GameData.MinimumHull). Red (mythical) fish wait for the gold-fight minigame.
    public static class Coasts
    {
        public const int OuterFirstSpot = 5;
        public const int OuterMinimumHull = 2; // Compact fisher, tier 3
        public static readonly string[] Names = { "Gull coast", "Outer coast" };
        public static string OuterLock => "Needs the " + GameData.Hulls[OuterMinimumHull].Name;

        public static int Of(int spot) => spot < OuterFirstSpot ? 0 : 1;
        public static bool Outer(int spot) => Of(spot) == 1;
        public static bool Open(int spot, int hull) => !Outer(spot) || hull >= OuterMinimumHull;

        // Whether a species may bite at this ground at all.
        public static bool Allowed(int spot, Species species)
        {
            var tier = CatchPresentation.Tier(species, 0);
            if (tier == CatchTier.Mythical) return false;
            return Outer(spot) || tier < CatchTier.Legendary;
        }

        // Each Outer coast ground adds its own big fish on top of its ground pools: a signature purple and a gold.
        static readonly Dictionary<int, (Species species, float weight)[]> OuterExtras = new()
        {
            [5] = new[] { (Species.GiantDevilManta, .5f), (Species.GoldTipShark, .3f) },                                  // Seal skerries
            [6] = new[] { (Species.AtlanticSwordfish, .5f), (Species.ScallopedHammerhead, .3f) },                         // Wreck bank
            [7] = new[] { (Species.YellowfinTuna, 3f), (Species.ApexReefShark, .35f) },                                   // Lighthouse rock
            [8] = new[] { (Species.OceanSunfish, 1f), (Species.YellowfinTuna, 4f), (Species.PelagicThresherShark, .45f) }, // Whale shelf
            [9] = new[] { (Species.Barracuda, 4f), (Species.GiantDevilManta, .8f), (Species.ApexReefShark, .5f) },         // Seal cliffs
            [10] = new[] { (Species.SpottedEagleRay, 2f), (Species.MahiMahi, 4f), (Species.GoldTipShark, .6f), (Species.ScallopedHammerhead, .4f) }, // Kelp forest
        };

        // The pool a ground actually bites from: its own table, less anything the coast forbids, plus the coast extras.
        public static (Species species, float weight)[] Shape(int spot, (Species species, float weight)[] table)
        {
            var result = new List<(Species species, float weight)>(table.Length + 4);
            foreach (var e in table) if (Allowed(spot, e.species)) result.Add(e);
            if (OuterExtras.TryGetValue(spot, out var extras))
                foreach (var e in extras) if (!result.Exists(r => r.species == e.species)) result.Add(e);
            return result.ToArray();
        }
    }
}

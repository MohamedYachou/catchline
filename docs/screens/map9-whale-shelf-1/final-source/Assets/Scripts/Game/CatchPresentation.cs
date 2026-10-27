using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public enum CatchTier { Common, BigCommon, Rare, BigRare, Legendary, Mythical }

    public static class CatchPresentation
    {
        // Presentation metadata only: catch tables, prices and saved species IDs stay intact.
        public static bool IsRare(Species species) => species is Species.SeaBass or Species.Conger or Species.Turbot;
        public static bool IsBig(Species species, float kg)
        {
            var fish = GameData.Get(species);
            return kg >= fish.MaxKg * .75f;
        }
        public static CatchTier Tier(Species species, float kg) => species switch
        {
            Species.YellowfinTuna or Species.Barracuda or Species.MahiMahi or Species.Monkfish => CatchTier.BigCommon,
            Species.AbyssalGreatWhite or Species.AbyssalLeviathan or Species.GiantSquid => CatchTier.Mythical,
            Species.ApexReefShark or Species.GoldTipShark or Species.ScallopedHammerhead or Species.PelagicThresherShark => CatchTier.Legendary,
            Species.SpottedEagleRay or Species.GiantDevilManta or Species.AtlanticSwordfish or Species.OceanSunfish => CatchTier.BigRare,
            Species.GoldenPuffer or Species.BlueSpottedStingray or Species.FlyingFish or Species.Lionfish => CatchTier.Rare,
            _ => ExistingTier(species, kg)
        };
        static CatchTier ExistingTier(Species species, float kg) => IsRare(species)
            ? IsBig(species, kg) ? CatchTier.BigRare : CatchTier.Rare
            : IsBig(species, kg) ? CatchTier.BigCommon : CatchTier.Common;
        // Gold/red belong to explicit UI041 species, never expensive common catches.
        public static Color Accent(CatchTier tier) => Palette.Hex(tier switch
        {
            CatchTier.BigCommon => "7AE0A0", CatchTier.Rare => "76BDFA",
            CatchTier.BigRare => "C49BFA", CatchTier.Legendary => "F2C66D",
            CatchTier.Mythical => "FA8A91", _ => "E4ECEB"
        });
        public static string Label(CatchTier tier) => tier switch
        {
            CatchTier.BigCommon => "Big common", CatchTier.Rare => "Rare",
            CatchTier.BigRare => "Big rare", CatchTier.Legendary => "Legendary",
            CatchTier.Mythical => "Big legendary", _ => "Common"
        };
    }

    // Snapshot only fish successfully inserted into the hold. It cannot award coins,
    // update records or mutate the live fish when reopened later.
    public sealed class StoredCatchItem
    {
        public Species Species { get; }
        public float Kg { get; }
        public int Value { get; }
        public CatchTier Tier { get; }
        public StoredCatchItem(CaughtFish fish, GameState state, float now)
        {
            Species = fish.Species; Kg = fish.Kg; Value = state.ValueOf(fish, now);
            Tier = CatchPresentation.Tier(Species, Kg);
        }
    }
    public sealed class NetCatchReceipt
    {
        public IReadOnlyList<StoredCatchItem> Items { get; }
        public float StoredAt { get; }
        public int Count => Items.Count;
        public float Kg => Items.Sum(f => f.Kg);
        public int Value => Items.Sum(f => f.Value);
        public NetCatchReceipt(IEnumerable<CaughtFish> stored, GameState state, float now)
        {
            Items = System.Array.AsReadOnly(stored.Select(f => new StoredCatchItem(f, state, now)).ToArray());
            StoredAt = now;
        }
    }
}

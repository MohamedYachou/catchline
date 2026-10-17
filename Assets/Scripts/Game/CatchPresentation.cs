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
            return kg >= Mathf.Lerp(fish.MinKg, fish.MaxKg, .75f);
        }
        public static CatchTier Tier(Species species, float kg) => IsRare(species)
            ? IsBig(species, kg) ? CatchTier.BigRare : CatchTier.Rare
            : IsBig(species, kg) ? CatchTier.BigCommon : CatchTier.Common;
        // Gold/red styles are ready for future explicitly legendary species. No current
        // fish or large common catch is promoted to those tiers by its sale price.
        public static Color Accent(CatchTier tier) => Palette.Hex(tier switch
        {
            CatchTier.BigCommon => "7AE0A0", CatchTier.Rare => "76BDFA",
            CatchTier.BigRare => "C49BFA", CatchTier.Legendary => "F2C66D",
            CatchTier.Mythical => "FA8A91", _ => "E4ECEB"
        });
        public static string Label(CatchTier tier) => tier switch
        {
            CatchTier.BigCommon => "Common · big", CatchTier.Rare => "Rare",
            CatchTier.BigRare => "Rare · big", CatchTier.Legendary => "Legendary",
            CatchTier.Mythical => "Mythical", _ => "Common"
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

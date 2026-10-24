using System;
using System.Collections.Generic;
using Catchline.Game.Deck;

namespace Catchline.Game
{
    // MASTER-PLAN M5 / BLUEPRINT section 9. Pure data and logic, not wired yet.
    // Append only: stored as ints in SaveV2.BuyerRep (index = (int)BuyerId).
    public enum BuyerId { Market, BaitShop, Restaurant, Cannery, Collector }

    public sealed class BuyerDef
    {
        public readonly BuyerId Id;
        public readonly string Name, Wants;
        public readonly string[] Unlocks;   // shop items behind reputation tier 1 (see Buyers.UnlockTier)
        public readonly string PortraitId;  // art plugs in by id

        public BuyerDef(BuyerId id, string name, string wants, params string[] unlocks)
        {
            Id = id; Name = name; Wants = wants; Unlocks = unlocks; PortraitId = id.ToString().ToLowerInvariant();
        }
    }

    public enum SaleItemKind { Fish, FishOil, Special, Squid }

    // One thing in the haul. BaseValue is the market value in coins (already includes any specimen premium
    // or freshness the caller applies); the buyers' own rules are applied on top of it.
    public sealed class SaleItem
    {
        public SaleItemKind Kind;
        public Species Species;
        public FishClass Class;
        public float Kg;
        public int Units = 1;     // fish oil and squid are counted in units
        public int BaseValue;     // Market price for a fish; ignored for products

        public static SaleItem Fish(Species species, FishClass cls, float kg, int baseValue) =>
            new SaleItem { Kind = SaleItemKind.Fish, Species = species, Class = cls, Kg = kg, BaseValue = baseValue };

        // Caller supplies the live base value (e.g. GameState.ValueOf); the class comes from FishRules.
        public static SaleItem FromFish(CaughtFish f, int baseValue) => Fish(f.Species, FishRules.Class(f), f.Kg, baseValue);

        // Base value straight from the static table (no specimen premium, no freshness): kg x price per kg.
        public static SaleItem FishAtBase(Species species, FishClass cls, float kg) =>
            Fish(species, cls, kg, Math.Max(1, (int)Math.Round(kg * GameData.Get(species).PricePerKg, MidpointRounding.AwayFromZero)));

        public static SaleItem FishOil(int units) => new SaleItem { Kind = SaleItemKind.FishOil, Units = units, Kg = units * Products.FishOilKgPerUnit };
        public static SaleItem Squid(int units) => new SaleItem { Kind = SaleItemKind.Squid, Units = units };
        // A special product is sold at its table price.
        public static SaleItem Special(Species species, float kg) =>
            new SaleItem { Kind = SaleItemKind.Special, Species = species, Kg = kg, BaseValue = Products.SpecialValue(species, kg) };
    }

    // Per-sale context: the map's "named species" the Restaurant cares about.
    // TODO(BLUEPRINT): which species each map names is not specified; an empty set means the Restaurant buys nothing.
    public sealed class SaleContext
    {
        public readonly HashSet<Species> NamedSpecies = new HashSet<Species>();
    }

    public sealed class SaleLine
    {
        public BuyerId Buyer;
        public readonly List<SaleItem> Items = new List<SaleItem>();
        public int Total;
    }

    // Read-model for the sale screen: which buyer took what and for how much.
    public sealed class SaleReport
    {
        public readonly List<SaleLine> Lines = new List<SaleLine>();
        public readonly List<SaleItem> Unsold = new List<SaleItem>();
        public int Total;
        public SaleLine LineFor(BuyerId b) { foreach (var l in Lines) if (l.Buyer == b) return l; return null; }
        public int TotalFor(BuyerId b) { var l = LineFor(b); return l == null ? 0 : l.Total; }
    }

    public static class Buyers
    {
        // M5 pricing constants.
        public const int BaitShopWhiteFloor = 3, BaitShopGreenFloor = 6, BaitShopSquid = 8;
        public const int RestaurantPercent = 130;   // x1.3, in whole percent so the rounding is exact
        public const int CanneryFishOilPerUnit = 8;

        public static readonly BuyerDef[] All =
        {
            new BuyerDef(BuyerId.Market, "Market", "Any fish, flat price"),
            new BuyerDef(BuyerId.BaitShop, "Bait shop", "White and green fish, squid, at a floor price", "bulk_bait_packs"),
            new BuyerDef(BuyerId.Restaurant, "Restaurant", "Named species, blue and above", "squid_lights"),
            new BuyerDef(BuyerId.Cannery, "Cannery", "Fish oil, bulk kg", "heavy_net_system"),
            new BuyerDef(BuyerId.Collector, "Collector", "Special products", "deep_line_rigs", "cage_sets"),
        };

        public static BuyerDef Def(BuyerId id) => All[(int)id];

        static int Round(double v) => (int)Math.Round(v, MidpointRounding.AwayFromZero);

        // What `buyer` pays for `item`, or -1 if it does not buy it. No saturation: the price never depends on
        // how much of anything was sold before.
        public static int Offer(BuyerId buyer, SaleItem item, SaleContext ctx = null)
        {
            switch (buyer)
            {
                case BuyerId.Market:
                    // Everything at base: fish only. Products have their own buyers, and the Market has no base for them.
                    return item.Kind == SaleItemKind.Fish ? item.BaseValue : -1;
                case BuyerId.BaitShop:
                    if (item.Kind == SaleItemKind.Squid) return BaitShopSquid * item.Units;
                    if (item.Kind != SaleItemKind.Fish) return -1;
                    if (item.Class == FishClass.White) return BaitShopWhiteFloor;
                    if (item.Class == FishClass.Green) return BaitShopGreenFloor;
                    return -1;
                case BuyerId.Restaurant:
                    if (item.Kind != SaleItemKind.Fish || item.Class < FishClass.Blue) return -1;
                    if (ctx == null || !ctx.NamedSpecies.Contains(item.Species)) return -1;
                    return Round(item.BaseValue * RestaurantPercent / 100.0);
                case BuyerId.Cannery:
                    return item.Kind == SaleItemKind.FishOil ? CanneryFishOilPerUnit * item.Units : -1;
                case BuyerId.Collector:
                    return item.Kind == SaleItemKind.Special ? item.BaseValue : -1;
            }
            return -1;
        }

        // Best buyer for one item: highest offer, ties to the lowest BuyerId (Market first). Null if nobody buys it.
        public static BuyerId? BestBuyer(SaleItem item, SaleContext ctx, out int price)
        {
            BuyerId? best = null; price = 0;
            for (int i = 0; i < All.Length; i++)
            {
                int o = Offer((BuyerId)i, item, ctx);
                if (o < 0) continue;
                if (best == null || o > price) { best = (BuyerId)i; price = o; }
            }
            return best;
        }

        // The sale auto-splits the haul to the best buyer per item. Every item is paid exactly its winning
        // offer, so line totals add up to the item sums by construction.
        public static SaleReport SplitSale(IEnumerable<SaleItem> items, SaleContext ctx = null)
        {
            var report = new SaleReport();
            if (items == null) return report;
            foreach (var item in items)
            {
                var buyer = BestBuyer(item, ctx, out int price);
                if (buyer == null) { report.Unsold.Add(item); continue; }
                var line = report.LineFor(buyer.Value);
                if (line == null) { line = new SaleLine { Buyer = buyer.Value }; report.Lines.Add(line); }
                line.Items.Add(item);
                line.Total += price;
                report.Total += price;
            }
            report.Lines.Sort((a, b) => a.Buyer.CompareTo(b.Buyer));
            return report;
        }

        // ---- Reputation tiers --------------------------------------------------------------------------------
        public static readonly int[] TierThresholds = { 1000, 5000, 20000 };
        public const int MaxTier = 3;
        public const int CoinsPerRep = 100;

        // Reputation tier 0..3 for a reputation value.
        public static int TierForRep(int rep)
        {
            int tier = 0;
            for (int i = 0; i < TierThresholds.Length; i++) if (rep >= TierThresholds[i]) tier = i + 1;
            return tier;
        }

        // Simplest reading of M5: a buyer's shop items all unlock at tier 1; tiers 1..3 also unlock that
        // buyer's contract tiers 1..3 (tier 0 contracts are always on the board).
        public const int UnlockTier = 1;

        public static bool Unlocked(BuyerId buyer, string itemId, int tier)
        {
            if (tier < UnlockTier) return false;
            return Array.IndexOf(Def(buyer).Unlocks, itemId) >= 0;
        }

        // Every shop item unlocked at `tier`, across all buyers.
        public static List<string> UnlockedItems(int tier)
        {
            var list = new List<string>();
            if (tier < UnlockTier) return list;
            foreach (var b in All) list.AddRange(b.Unlocks);
            return list;
        }
    }

    // Per-buyer reputation: coins sold to them / 100, plus contract rewards and penalties.
    // Matches SaveV2.BuyerRep (one int per buyer); CoinsSold is kept so the divide stays exact.
    public sealed class BuyerReputation
    {
        readonly int[] coinsSold = new int[Buyers.All.Length];
        readonly int[] adjust = new int[Buyers.All.Length];

        public int CoinsSold(BuyerId b) => coinsSold[(int)b];
        public int Rep(BuyerId b) => Math.Max(0, coinsSold[(int)b] / Buyers.CoinsPerRep + adjust[(int)b]);
        public int Tier(BuyerId b) => Buyers.TierForRep(Rep(b));
        public bool Unlocked(BuyerId b, string itemId) => Buyers.Unlocked(b, itemId, Tier(b));

        public void AddSale(BuyerId b, int coins) { if (coins > 0) coinsSold[(int)b] += coins; }
        public void AddSale(SaleReport report) { foreach (var l in report.Lines) AddSale(l.Buyer, l.Total); }
        // Contract rewards (+) and failures (-). Rep never reads below zero.
        public void Adjust(BuyerId b, int delta) { adjust[(int)b] += delta; }
    }
}

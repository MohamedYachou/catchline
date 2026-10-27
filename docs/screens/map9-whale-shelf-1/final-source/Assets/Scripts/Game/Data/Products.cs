using System;
using System.Collections.Generic;
using Catchline.Game.Deck;

namespace Catchline.Game
{
    // MASTER-PLAN M3 / BLUEPRINT section 8: what the processing table makes. Pure data and pure logic,
    // not wired into the game yet. Append only: Kind values may be stored by later saves.
    public enum ProductKind { Chum, FishOil, Special }

    // One row of the product table. Special products have one row per purple+ species.
    public sealed class ProductDef
    {
        public readonly string Id;          // stable key; art plugs in by id (icon id == id)
        public readonly string Name;
        public readonly ProductKind Kind;
        public readonly float Seconds;      // table time per unit at skill 100, level 1
        public readonly float KgPerUnit;    // hold weight of one unit; 0 for chum (not stored as fish) and specials (kg of the fish)
        public readonly BuyerId? Buyer;     // null = not sold (chum feeds lines, cages and rods)
        public readonly Species? Species;   // set for special products
        public string IconId => Id;

        public ProductDef(string id, string name, ProductKind kind, float seconds, float kgPerUnit, BuyerId? buyer, Species? species = null)
        {
            Id = id; Name = name; Kind = kind; Seconds = seconds; KgPerUnit = kgPerUnit; Buyer = buyer; Species = species;
        }
    }

    public static class Products
    {
        // MASTER-PLAN M3 numbers (they supersede the provisional 3.5 s / 4.5 s of BLUEPRINT section 8).
        public const float ChumSeconds = 3.0f, FishOilSeconds = 4.0f, SpecialSeconds = 6.0f;
        public const float FishOilKgPerUnit = 0.25f;

        public static readonly ProductDef Chum = new ProductDef("chum", "Chum", ProductKind.Chum, ChumSeconds, 0f, null);
        public static readonly ProductDef FishOil = new ProductDef("fish_oil", "Fish oil", ProductKind.FishOil, FishOilSeconds, FishOilKgPerUnit, BuyerId.Cannery);

        // Chum per fish: white 1, green 2, blue 3. Purple and above cannot be turned into chum.
        public static int ChumUnits(FishClass c) => c switch { FishClass.White => 1, FishClass.Green => 2, FishClass.Blue => 3, _ => 0 };
        // Fish oil: any white or green fish, one unit per fish.
        public static bool FishOilEligible(FishClass c) => c == FishClass.White || c == FishClass.Green;
        // Purple, gold and red always become their species' special product.
        public static bool IsSpecialClass(FishClass c) => c >= FishClass.Purple;

        public static bool Eligible(ProductKind kind, FishClass c) => kind switch
        {
            ProductKind.Chum => ChumUnits(c) > 0,
            ProductKind.FishOil => FishOilEligible(c),
            _ => IsSpecialClass(c)
        };

        public static ProductDef Def(ProductKind kind) => kind == ProductKind.Chum ? Chum : kind == ProductKind.FishOil ? FishOil : null;

        // ---- Special products: one per purple+ species -------------------------------------------------
        // Open decision (BLUEPRINT section 17.2): which special product each species yields. The docs name
        // marlin bill, shark tooth, ray skin and roe only; everything else gets a neutral placeholder name.
        static Dictionary<Species, ProductDef> specials;

        static string SpecialName(Species s)
        {
            switch (s)
            {
                case Species.SpottedEagleRay: case Species.GiantDevilManta: return "Ray skin";
                case Species.ApexReefShark: case Species.GoldTipShark: case Species.AbyssalGreatWhite:
                case Species.ScallopedHammerhead: case Species.PelagicThresherShark: return "Shark tooth";
                case Species.AtlanticSwordfish: return "Marlin bill";
                // TODO(BLUEPRINT): special product for ocean sunfish, abyssal killer whale, giant squid and the
                // common species that reach purple at specimen size (sea bass, conger, turbot). "Roe" is the
                // only named product left over, but the docs do not assign it to anything.
                default: return GameData.Get(s).Name + " special";
            }
        }

        // A species has a special product when some fish of it can land as purple or above.
        public static bool HasSpecial(Species s) => Special(s) != null;

        public static ProductDef Special(Species s)
        {
            if (specials == null)
            {
                var map = new Dictionary<Species, ProductDef>();
                foreach (var d in GameData.Fish)
                {
                    var atMax = FishRules.Class(new CaughtFish { Species = d.Species, Kg = d.MaxKg });
                    if (!IsSpecialClass(atMax)) continue;
                    // Id is per species so contracts and the Collector can tell them apart.
                    map[d.Species] = new ProductDef("special." + d.Species.ToString().ToLowerInvariant(), SpecialName(d.Species),
                        ProductKind.Special, SpecialSeconds, 0f, BuyerId.Collector, d.Species);
                }
                specials = map;
            }
            return specials.TryGetValue(s, out var p) ? p : null;
        }

        public static IEnumerable<ProductDef> AllSpecials()
        {
            Special(Species.Herring); // force the table to build
            return specials.Values;
        }

        // TODO(BLUEPRINT): "Collector (special products at their table price)" gives no table price. Simplest
        // reading: the product is worth its source fish at the species' base price per kg.
        public static int SpecialValue(Species s, float kg)
        {
            double v = kg * GameData.Get(s).PricePerKg;
            return Math.Max(1, (int)Math.Round(v, MidpointRounding.AwayFromZero));
        }
    }

    // ---- Table orders ------------------------------------------------------------------------------------
    public enum TableOutcome { PassThrough, Product }

    // What the table does with one input fish.
    public struct TableResult
    {
        public TableOutcome Outcome;
        public ProductKind Product;   // valid when Outcome == Product
        public Species Species;       // the input fish
        public int Units;             // chum: 1/2/3; fish oil: 1; special: 1
        public float Kg;              // hold weight of the output (fish oil 0.25 per unit, special = fish kg, chum 0)
        public float Seconds;         // table time for this job
        public int OrderIndex;        // the order that consumed the fish; -1 for pass-through and for specials
        public bool BypassedList;     // purple+ went straight to its special product
    }

    public sealed class TableOrder
    {
        public ProductKind Product;
        public int Target;            // 1, 5, 10 or TableOrders.Infinite
        public int Done;              // fish consumed by this order so far
        public bool IsInfinite => Target == TableOrders.Infinite;
        public bool Satisfied => !IsInfinite && Done >= Target;
        public int Remaining => IsInfinite ? int.MaxValue : Math.Max(0, Target - Done);
    }

    // The captain's short, ordered list. Read-model friendly: Orders is a plain list.
    public sealed class TableOrders
    {
        public const int Infinite = -1;
        public static readonly int[] Targets = { 1, 5, 10, Infinite };

        public readonly List<TableOrder> Orders = new List<TableOrder>();

        public static bool ValidTarget(int target) => Array.IndexOf(Targets, target) >= 0;

        // Only generic products can be ordered. Special products are automatic for purple+ and never listed.
        public bool Add(ProductKind product, int target)
        {
            if (product == ProductKind.Special || !ValidTarget(target)) return false;
            Orders.Add(new TableOrder { Product = product, Target = target });
            return true;
        }

        public void Clear() => Orders.Clear();
        public bool Remove(int index) { if (index < 0 || index >= Orders.Count) return false; Orders.RemoveAt(index); return true; }

        public TableResult Process(CaughtFish fish) => Run(Orders, FishRules.Class(fish), fish.Species, fish.Kg, true);
        public TableResult Process(FishClass cls, Species species, float kg) => Run(Orders, cls, species, kg, true);
        // Same decision without touching the counts.
        public TableResult Peek(CaughtFish fish) => Run(Orders, FishRules.Class(fish), fish.Species, fish.Kg, false);

        // Pure decision function. Purple+ become their special product and skip the list. Otherwise the orders
        // are worked top to bottom: satisfied orders and orders this fish cannot feed (starved for it) are
        // skipped; the first live order takes the fish and its count goes up by one fish. With nothing live
        // the fish passes through to the hold untouched. An order counts fish consumed, not output units
        // (a "Chum 5" order is five fish, which can be up to fifteen chum).
        public static TableResult Run(IList<TableOrder> orders, FishClass cls, Species species, float kg, bool update)
        {
            if (Products.IsSpecialClass(cls))
            {
                var special = Products.Special(species);
                if (special != null)
                    return new TableResult
                    {
                        Outcome = TableOutcome.Product, Product = ProductKind.Special, Species = species, Units = 1,
                        Kg = kg, Seconds = Products.SpecialSeconds, OrderIndex = -1, BypassedList = true
                    };
                // A purple+ fish of a species with no special product cannot occur by construction of Products.Special.
            }
            for (int i = 0; orders != null && i < orders.Count; i++)
            {
                var o = orders[i];
                if (o.Satisfied || !Products.Eligible(o.Product, cls)) continue;
                if (update) o.Done++;
                int units = o.Product == ProductKind.Chum ? Products.ChumUnits(cls) : 1;
                var def = Products.Def(o.Product);
                return new TableResult
                {
                    Outcome = TableOutcome.Product, Product = o.Product, Species = species, Units = units,
                    Kg = def.KgPerUnit * units, Seconds = def.Seconds, OrderIndex = i
                };
            }
            return new TableResult { Outcome = TableOutcome.PassThrough, Species = species, Kg = kg, OrderIndex = -1 };
        }
    }
}

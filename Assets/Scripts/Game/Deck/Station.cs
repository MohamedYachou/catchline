using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game.Deck
{
    // Deck graph types (docs/MASTER-PLAN.md B2). Positions are boat-local metres, tiles are the hull grid.
    public enum StationKind { Rod, Net, Cage, Line, Jig, SortTable, ProcessTable, HoldHatch, BaitBin, NavPost, Lantern, Generator, DeckLight, LineHauler, Unknown }
    public enum BasketKind { RodOut, JigOut, NetOut, CageOut, LineOut, SortIn, SortOut, TableIn, TableOut }

    public enum FishClass { White, Green, Blue, Purple, Gold, Red }

    public static class FishRules
    {
        // Mo 10-27: the bottom 15% of each species' own weight range is undersize and always goes back.
        public const float UndersizeFraction = .15f;
        public static bool Undersize(CaughtFish f)
        {
            var d = GameData.Get(f.Species);
            return f.Kg < d.MinKg + UndersizeFraction * (d.MaxKg - d.MinKg);
        }
        public static FishClass Class(CaughtFish f) => CatchPresentation.Tier(f.Species, f.Kg) switch
        {
            CatchTier.BigCommon => FishClass.Green, CatchTier.Rare => FishClass.Blue, CatchTier.BigRare => FishClass.Purple,
            CatchTier.Legendary => FishClass.Gold, CatchTier.Mythical => FishClass.Red, _ => FishClass.White
        };
        // B2: over 5 kg a fish lands loose beside its station; over 15 kg it needs two carriers.
        public const float BasketMaxKg = 5f, TwoCarrierKg = 15f;
        public static bool FitsBasket(CaughtFish f) => f.Kg <= BasketMaxKg;
        public static bool NeedsTwo(CaughtFish f) => f.Kg > TwoCarrierKg;
    }

    public sealed class Basket
    {
        public readonly string Id;
        public readonly BasketKind Kind;
        public readonly Station Owner;
        public Vector3 Position;
        public int CapacityCount;
        public float CapacityKg = float.MaxValue;
        public readonly List<CaughtFish> Fish = new();
        // A fish is claimed by at most one job; free slots are reserved by jobs bringing fish in.
        readonly Dictionary<CaughtFish, object> claims = new();
        int reservedSlots;

        public Basket(string id, BasketKind kind, Station owner, Vector3 position)
        {
            Id = id; Kind = kind; Owner = owner; Position = position; CapacityCount = DefaultCapacity(kind);
        }

        // B2 default capacities.
        public static int DefaultCapacity(BasketKind k) => k switch
        {
            BasketKind.RodOut => 6, BasketKind.JigOut => 8, BasketKind.NetOut => 16, BasketKind.CageOut => 6, BasketKind.LineOut => 4,
            BasketKind.SortIn => 12, BasketKind.SortOut => 12, BasketKind.TableIn => 10, _ => 8
        };

        public float Kg => Fish.Sum(f => f.Kg);
        public int Count => Fish.Count;
        public int Free => Mathf.Max(0, CapacityCount - Fish.Count - reservedSlots);
        public float Fill => CapacityCount > 0 ? (Fish.Count + reservedSlots) / (float)CapacityCount : 1f;
        public bool Full => Free <= 0;
        public IEnumerable<CaughtFish> Unclaimed => Fish.Where(f => !claims.ContainsKey(f));
        public int UnclaimedCount => Fish.Count(f => !claims.ContainsKey(f));

        public bool Claim(CaughtFish f, object by)
        {
            if (!Fish.Contains(f) || claims.ContainsKey(f)) return false;
            claims[f] = by; return true;
        }
        public void Release(CaughtFish f, object by) { if (claims.TryGetValue(f, out var o) && o == by) claims.Remove(f); }
        public bool IsClaimed(CaughtFish f) => claims.ContainsKey(f);
        public bool Reserve(int slots) { if (Free < slots) return false; reservedSlots += slots; return true; }
        public void Unreserve(int slots) => reservedSlots = Mathf.Max(0, reservedSlots - slots);

        // Moving fish never duplicates or loses one: Take removes only what this claimant holds.
        public bool Take(CaughtFish f, object by)
        {
            if (!claims.TryGetValue(f, out var o) || o != by) return false;
            claims.Remove(f); return Fish.Remove(f);
        }
        public bool Put(CaughtFish f, bool fromReservation)
        {
            if (fromReservation) Unreserve(1);
            else if (Free <= 0) return false;
            if (Fish.Contains(f)) return false;
            Fish.Add(f); return true;
        }
    }

    public sealed class Station
    {
        public string Id;
        public StationKind Kind;
        public Vector3 Position;
        public float Yaw;
        public Vector2Int WorkTile;
        public List<Vector2Int> WorkTiles = new();
        public int Places = 1;
        public Basket In, Out;
        public bool Enabled = true;
        public float PowerDraw;
        public string ModelId, BasketPrefix;
        public object Worker; // the worker currently operating it, if any

        public static StationKind ParseKind(string s) => System.Enum.TryParse(s, out StationKind k) ? k : StationKind.Unknown;
        public static BasketKind? OutKind(StationKind k) => k switch
        {
            StationKind.Rod => BasketKind.RodOut, StationKind.Jig => BasketKind.JigOut, StationKind.Net => BasketKind.NetOut,
            StationKind.Cage => BasketKind.CageOut, StationKind.Line => BasketKind.LineOut,
            StationKind.SortTable => BasketKind.SortOut, StationKind.ProcessTable => BasketKind.TableOut, _ => null
        };
        public static BasketKind? InKind(StationKind k) => k switch
        {
            StationKind.SortTable => BasketKind.SortIn, StationKind.ProcessTable => BasketKind.TableIn, _ => null
        };
        public bool IsGear => Kind is StationKind.Rod or StationKind.Net or StationKind.Cage or StationKind.Line or StationKind.Jig;
    }
}

using System;
using System.Collections.Generic;
using Catchline.Game.Deck;

namespace Catchline.Game
{
    // MASTER-PLAN M5 / BLUEPRINT section 10. Pure data and logic, not wired yet.
    public static class Quota
    {
        public const float Unlimited = float.PositiveInfinity;
        public const int FineMultiplier = 2;      // fine = 2x the excess value
        public const int ClosureVoyages = 3;      // the ground stays closed for three voyages

        // Per map, per voyage, by class. White and green are unlimited.
        // TODO(BLUEPRINT): "per map" is the same four numbers for every map; a per-map override table would go here.
        public static float LimitKg(FishClass c) => c switch
        {
            FishClass.Blue => 30f, FishClass.Purple => 20f, FishClass.Gold => 10f, FishClass.Red => 5f, _ => Unlimited
        };
    }

    // What an inspector finds at the end of a voyage on one map.
    public sealed class QuotaInspection
    {
        public string Map;
        public readonly float[] ExcessKg = new float[6];   // per FishClass
        public int Fine;                                   // 2x excess value, whole coins
        public bool GroundClosed;                          // any excess closes the ground
    }

    // Quota ledger for the voyage in progress, plus ground closures. SaveV2.Quota is a string, so a later
    // serialiser can write Closed as map:voyages pairs; nothing here touches saves.
    public sealed class QuotaLedger
    {
        sealed class Tally { public float Kg; public double Value; }

        readonly Dictionary<string, Tally[]> voyage = new Dictionary<string, Tally[]>();
        readonly Dictionary<string, int> closed = new Dictionary<string, int>();

        public IEnumerable<KeyValuePair<string, int>> ClosedGrounds => closed;

        Tally[] Row(string map)
        {
            if (!voyage.TryGetValue(map, out var row))
            {
                row = new Tally[6];
                for (int i = 0; i < 6; i++) row[i] = new Tally();
                voyage[map] = row;
            }
            return row;
        }

        // Records a kept fish. Throwbacks (undersize or any fish put back) are exempt and ignored.
        public void Record(string map, FishClass cls, float kg, int value, bool throwback = false)
        {
            if (throwback) return;
            var t = Row(map)[(int)cls];
            t.Kg += kg; t.Value += value;
        }

        public float Kept(string map, FishClass cls) => voyage.TryGetValue(map, out var row) ? row[(int)cls].Kg : 0f;

        // Kg still allowed this voyage for the class (infinite for white and green).
        public float Remaining(string map, FishClass cls)
        {
            float limit = Quota.LimitKg(cls);
            return float.IsPositiveInfinity(limit) ? limit : Math.Max(0f, limit - Kept(map, cls));
        }

        // The inspector: excess kg per class; the fine is 2x the excess value, valuing the excess kg at the
        // average price that class fetched on this map this voyage (simplest reading, no per-fish ordering).
        // Any excess closes the ground for three voyages. Does nothing and returns no fine when within quota.
        public QuotaInspection Inspect(string map)
        {
            var result = new QuotaInspection { Map = map };
            if (!voyage.TryGetValue(map, out var row)) return result;
            double excessValue = 0;
            for (int i = 0; i < 6; i++)
            {
                float limit = Quota.LimitKg((FishClass)i);
                if (float.IsPositiveInfinity(limit)) continue;
                float excess = row[i].Kg - limit;
                if (excess <= 0f) continue;
                result.ExcessKg[i] = excess;
                excessValue += row[i].Value * (excess / row[i].Kg);
            }
            if (excessValue > 0)
            {
                result.Fine = (int)Math.Round(excessValue * Quota.FineMultiplier, MidpointRounding.AwayFromZero);
                result.GroundClosed = true;
                closed[map] = Quota.ClosureVoyages;
            }
            return result;
        }

        public bool IsClosed(string map) => closed.TryGetValue(map, out var n) && n > 0;
        public int ClosedVoyagesLeft(string map) => closed.TryGetValue(map, out var n) ? n : 0;

        // Departure. Refused (false) for a closed ground, no voyage counted. Otherwise the new voyage starts
        // with a clean ledger and every closure ticks down by one, so a ground closed by an inspection is
        // out of reach for exactly the next three voyages.
        public bool BeginVoyage(string map)
        {
            if (IsClosed(map)) return false;
            voyage.Clear();
            var keys = new List<string>(closed.Keys);
            foreach (var k in keys)
            {
                int left = closed[k] - 1;
                if (left <= 0) closed.Remove(k); else closed[k] = left;
            }
            return true;
        }
    }

    // Spare rigs and the cost of a trip.
    public static class Stakes
    {
        public const int SpareRigPrice = 5;
        public const float FrayedStrikeWindowMult = 0.8f;   // -20% strike window with no spare rig

        // "This trip costs N" = wages + fuel + bait + lantern oil, paid on Let's go.
        public static int TripCost(int wages, int fuel, int bait, int lanternOil) => wages + fuel + bait + lanternOil;
    }

    public sealed class SpareRigs
    {
        public int Count;

        public SpareRigs(int count = 0) { Count = Math.Max(0, count); }

        // A rod with no spare rig left fishes "frayed". It never becomes unusable.
        public bool Frayed => Count <= 0;
        public bool Usable => true;

        public float StrikeWindow(float baseWindow) => Frayed ? baseWindow * Stakes.FrayedStrikeWindowMult : baseWindow;

        // Buys up to `n` spare rigs with the coins available; returns the coins spent.
        public int Buy(int n, int coins)
        {
            int afford = Math.Min(n, coins / Stakes.SpareRigPrice);
            if (afford <= 0) return 0;
            Count += afford;
            return afford * Stakes.SpareRigPrice;
        }

        // A snag cut spends one spare rig. With none left nothing is spent and the rig stays frayed.
        // Returns true if a spare was spent.
        public bool Snag()
        {
            if (Count <= 0) return false;
            Count--;
            return true;
        }
    }
}

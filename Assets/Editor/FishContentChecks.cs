using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Pure state checks. Run on Windows after water checks release scratch; never uses Mo's save.
    public static class FishContentChecks
    {
        static void Check(bool ok, string message)
        { if (!ok) throw new Exception("[Catchline] Fish content check failed: " + message); }

        public static void Run()
        {
            Check((int)Species.Cod == 6 && (int)Species.Whiting == 7, "legacy species IDs retained");
            Check(GameData.Fish.Length == 10, "ten species have definitions");
            for (int i = 0; i < GameData.Fish.Length; i++)
                Check((int)GameData.Fish[i].Species == i, "definition/enum index " + i);
            var all = GameData.Spots.SelectMany(s => s.Table).Select(e => e.species).Distinct().ToArray();
            Check(all.Length == GameData.Fish.Length, "every species is catchable in existing locations");
            for (int spot = 0; spot < GameData.Spots.Length; spot++)
            {
                var worms = new GameState(4700 + spot); var squid = new GameState(4700 + spot);
                double wormValue = 0, squidValue = 0; int wormSmall = 0, squidSmall = 0;
                const int samples = 12000;
                for (int i = 0; i < samples; i++)
                {
                    var (a, ak) = worms.RollFish(spot, .65f);
                    var (b, bk) = squid.RollFish(spot, .65f + GameData.SquidPowerBonus, false, true);
                    Check(GameData.Spots[spot].Table.Any(e => e.species == a) && GameData.Spots[spot].Table.Any(e => e.species == b), "bait respects location");
                    var def = GameData.Get(b);
                    Check(bk >= def.MinKg + .35f * (def.MaxKg - def.MinKg) - .00001f && bk <= def.MaxKg, "squid specimen bounds");
                    wormValue += worms.ValueOf(new CaughtFish { Species = a, Kg = ak }, 0);
                    squidValue += squid.ValueOf(new CaughtFish { Species = b, Kg = bk }, 0);
                    if (a is Species.Herring or Species.Mackerel) wormSmall++;
                    if (b is Species.Herring or Species.Mackerel) squidSmall++;
                    var (poor, pk) = worms.RollFish(spot, 99, true, true);
                    var pd = GameData.Get(poor);
                    Check((poor is Species.Herring or Species.Mackerel) && pk <= pd.MinKg + .2f * (pd.MaxKg - pd.MinKg) + .00001f, "scraps stay small regardless of squid/power flags");
                }
                Check(squidValue / samples - 3 > wormValue / samples - 1, "squid improves expected landed net value at " + spot);
                if (wormSmall > 0) Check(squidSmall < wormSmall * .65, "squid reduces small-school catches at " + spot);
                if (spot == 0) Check(squidSmall < samples * .20, "harbour squid favours substantial whiting over small schools");
                Debug.Log($"[Catchline] Bait sample {GameData.Spots[spot].Name}: worms {wormValue / samples:0.00}, squid {squidValue / samples:0.00} gross/catch; small {wormSmall}/{squidSmall} of {samples}");
            }
            var s = new GameState(31) { Coins = 23, Bait = 0, Squid = 0 };
            Check(!s.BuyBait(true) && s.Coins == 23 && s.Bait == 0, "bulk shortfall changes nothing");
            s.Coins = 24;
            Check(s.BuyBait(true) && s.Coins == 0 && s.Bait == 30, "bulk worms exact payment");
            s.Coins = 36;
            Check(s.BuySquid(true) && s.Coins == 0 && s.Squid == 15, "bulk squid exact payment");
            s.UseSquid = false;
            Check(!s.WillUseSquid && s.TakeBait(out bool isSquid) && !isSquid && s.Bait == 29, "worm preference matches next-bait UI");
            s.Bait = 0;
            Check(s.WillUseSquid && s.TakeBait(out isSquid) && isSquid && s.Squid == 14, "squid fallback matches next-bait UI");
            s.Squid = 0;
            Check(s.TakeBait(out isSquid) && !isSquid && s.Coins == 0, "unlimited free fallback");
            Check(GameData.Get(Species.Herring).PricePerKg == 12 && GameData.Get(Species.Mackerel).PricePerKg == 13, "small-fish baseline stable");
            var market = new GameState(17) { Coins = 0 };
            var catchList = new[] { Species.Whiting, Species.RedMullet, Species.Turbot }
                .Select(f => new CaughtFish { Species = f, Kg = GameData.Get(f).MaxKg, StowedAt = 0 }).ToList();
            var quote = market.QuoteSale(catchList, 0);
            Check(market.Coins == 0 && market.LogCount.All(n => n == 0) && market.Market.All(m => m == 1), "new fish quote never changes live state");
            var sold = market.Sell(catchList, 0);
            Check(sold.FishSold == 3 && sold.Coins == quote.Coins && market.Coins == quote.Coins && market.Coins > 0, "new fish earn the quoted coins");
            Check(catchList.All(f => market.LogCount[(int)f.Species] == 1 && market.LogBest[(int)f.Species] == f.Kg), "new fish update their own log slots");
            string path = Path.Combine(Path.GetTempPath(), "catchline-fish-check-" + Guid.NewGuid() + ".json");
            try
            {
                File.WriteAllText(path, "{\"Version\":1,\"Coins\":123,\"Bait\":7,\"Squid\":4,\"Voyage\":5,\"UseSquid\":true,\"Owned\":[],\"Charts\":[],\"Board\":[],\"Offers\":[],\"Active\":[],\"Market\":[0.8,1,1,1,1,1,1],\"LogCount\":[2,0,0,0,0,0,1],\"LogBest\":[0.25,0,0,0,0,0,3]}");
                var loaded = GameState.Load(path);
                Check(loaded != null && loaded.Coins == 123 && loaded.LogCount[6] == 1 && loaded.LogCount[7] == 0 && loaded.Market[9] == 1, "seven-species save grows without erasure");
                loaded.UnsoldCatch.Add(new CaughtFish { Species = Species.Turbot, Kg = 4, StowedAt = -30 });
                loaded.Save(path); loaded = GameState.Load(path);
                Check(loaded != null && loaded.UnsoldCatch.Single().Species == Species.Turbot && loaded.UnsoldCatch.Single().Kg == 4, "new-species unsold haul roundtrips");
            }
            finally { if (File.Exists(path)) File.Delete(path); }
            RunBalance();
            Debug.Log("[Catchline] FISH CONTENT STATE CHECKS PASSED; native art/audio/UI review remains required");
        }

        // Expected per-cast value at the real basic fisher's strike rate. This excludes
        // crew fees/food/fuel and deliberately tests poor prices/old fish too.
        public static void RunBalance()
        {
            float hit = GameData.StrikeChance(Grade.Hand);
            foreach (var scenario in new[] { (name: "fresh", market: 1f, age: 0f),
                (name: "depressed", market: .75f, age: 180f), (name: "floor", market: .5f, age: 600f) })
            {
                for (int spot = 0; spot < GameData.Spots.Length; spot++)
                {
                    var s = new GameState(8700 + spot);
                    for (int i = 0; i < s.Market.Length; i++) s.Market[i] = scenario.market;
                    double worms = 0, squid = 0;
                    const int samples = 10000;
                    for (int i = 0; i < samples; i++)
                    {
                        var (a, ak) = s.RollFish(spot, .65f);
                        var (b, bk) = s.RollFish(spot, .65f + GameData.SquidPowerBonus, false, true);
                        worms += s.ValueOf(new CaughtFish { Species = a, Kg = ak }, scenario.age);
                        squid += s.ValueOf(new CaughtFish { Species = b, Kg = bk }, scenario.age);
                    }
                    double w = hit * worms / samples - GameData.BaitPackCost / (double)GameData.BaitPackSize;
                    double q = hit * squid / samples - GameData.SquidPackCost / (double)GameData.SquidPackSize;
                    if (scenario.name == "fresh") Check(q > w && w > 0, "premium bait improves expected per-cast value after misses/cost at " + spot);
                    Debug.Log($"[Catchline] Cast EV {scenario.name}/{GameData.Spots[spot].Name}: worms {w:0.00}, squid {q:0.00} coins after bait; {hit * 100:0}% strikes");
                }
            }
        }
    }
}

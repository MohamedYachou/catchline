using System;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEngine;

namespace Catchline.EditorTools
{
    // M3 data layer: products, table orders and bait. Pure logic, no scene.
    public static class M3DataChecks
    {
        static void Check(bool ok, string message)
        {
            if (!ok) throw new Exception("[Catchline] M3 data check failed: " + message);
        }

        public static void Run()
        {
            ProductTable();
            FishOilFive();
            InfiniteOrder();
            SpecialBypass();
            ChumYields();
            OrderSkipping();
            BaitTable();
            BaitSelection();
            ClassRolls();
            SquidPurpleCap();
            BiteWaitMaths();
            Debug.Log("[Catchline] M3 DATA CHECKS PASSED");
        }

        static void ProductTable()
        {
            Check(Products.ChumSeconds == 3.0f && Products.Chum.Seconds == 3.0f && Products.Chum.Buyer == null, "chum 3.0 s, not sold");
            Check(Products.FishOil.Seconds == 4.0f && Products.FishOilKgPerUnit == 0.25f && Products.FishOil.Buyer == BuyerId.Cannery, "fish oil 4.0 s, 0.25 kg, Cannery");
            Check(Products.SpecialSeconds == 6.0f, "special 6.0 s");
            Check(Products.ChumUnits(FishClass.White) == 1 && Products.ChumUnits(FishClass.Green) == 2 && Products.ChumUnits(FishClass.Blue) == 3, "chum units 1/2/3");
            Check(Products.ChumUnits(FishClass.Purple) == 0 && Products.ChumUnits(FishClass.Gold) == 0 && Products.ChumUnits(FishClass.Red) == 0, "no chum from purple+");
            Check(Products.FishOilEligible(FishClass.White) && Products.FishOilEligible(FishClass.Green) && !Products.FishOilEligible(FishClass.Blue), "fish oil from white or green only");
            int specials = 0;
            foreach (var d in GameData.Fish)
            {
                var cls = FishRules.Class(new CaughtFish { Species = d.Species, Kg = d.MaxKg });
                var sp = Products.Special(d.Species);
                if (cls >= FishClass.Purple)
                {
                    specials++;
                    Check(sp != null && sp.Species == d.Species && sp.Buyer == BuyerId.Collector && sp.Seconds == 6.0f, "special product for " + d.Name);
                }
                else Check(sp == null, "no special product for " + d.Name);
            }
            Check(specials >= 11, "all eleven explicit purple/gold/red species (and any big rare common) have a special product");
            Check(Products.Special(Species.ApexReefShark).Name == "Shark tooth" && Products.Special(Species.SpottedEagleRay).Name == "Ray skin", "named special products");
        }

        // A herring that is certainly white.
        static CaughtFish White() => new CaughtFish { Species = Species.Herring, Kg = 0.15f };

        static void FishOilFive()
        {
            var t = new TableOrders();
            Check(t.Add(ProductKind.FishOil, 5), "add Fish oil 5");
            Check(FishRules.Class(White()) == FishClass.White, "test herring is white");
            int oil = 0, pass = 0;
            for (int i = 0; i < 9; i++)
            {
                var r = t.Process(White());
                if (r.Outcome == TableOutcome.Product && r.Product == ProductKind.FishOil)
                {
                    oil++;
                    Check(r.Units == 1 && r.Kg == 0.25f && r.Seconds == 4.0f, "one oil unit of 0.25 kg per fish");
                }
                else pass++;
            }
            Check(oil == 5 && pass == 4, "Fish oil 5 consumes exactly five fish then stops (got " + oil + ")");
            Check(t.Orders[0].Done == 5 && t.Orders[0].Satisfied, "order satisfied at five");
            // Peek never changes counts.
            var t2 = new TableOrders(); t2.Add(ProductKind.FishOil, 1);
            Check(t2.Peek(White()).Product == ProductKind.FishOil && t2.Orders[0].Done == 0, "peek does not consume");
            // Blue fish cannot feed fish oil: skipped, passes through.
            var t3 = new TableOrders(); t3.Add(ProductKind.FishOil, 5);
            Check(t3.Process(FishClass.Blue, Species.GoldenPuffer, .3f).Outcome == TableOutcome.PassThrough && t3.Orders[0].Done == 0, "blue skips a fish oil order");
            // Bad inputs rejected.
            Check(!t3.Add(ProductKind.Chum, 7) && !t3.Add(ProductKind.Special, 5), "invalid target and special orders refused");
        }

        static void InfiniteOrder()
        {
            var t = new TableOrders();
            t.Add(ProductKind.Chum, TableOrders.Infinite);
            for (int i = 0; i < 500; i++)
                Check(t.Process(White()).Product == ProductKind.Chum, "infinite order keeps going at " + i);
            Check(t.Orders[0].Done == 500 && !t.Orders[0].Satisfied, "infinite never satisfied");
        }

        static void SpecialBypass()
        {
            var empty = new TableOrders();
            var purple = new CaughtFish { Species = Species.SpottedEagleRay, Kg = 9f };
            Check(FishRules.Class(purple) == FishClass.Purple, "eagle ray is purple");
            var r = empty.Process(purple);
            Check(r.Outcome == TableOutcome.Product && r.Product == ProductKind.Special && r.BypassedList && r.Kg == 9f && r.Seconds == 6.0f, "purple becomes its special product with an empty list");
            var gold = empty.Process(new CaughtFish { Species = Species.GoldTipShark, Kg = 20f });
            var red = empty.Process(new CaughtFish { Species = Species.AbyssalGreatWhite, Kg = 30f });
            Check(gold.Product == ProductKind.Special && red.Product == ProductKind.Special, "gold and red become special products");
            // Bypasses the list even when the list would take it, and does not count against any order.
            var full = new TableOrders(); full.Add(ProductKind.Chum, TableOrders.Infinite);
            var r2 = full.Process(purple);
            Check(r2.Product == ProductKind.Special && full.Orders[0].Done == 0, "purple skips the list and counts against nothing");
            // Empty list, white fish: pass-through to the hold.
            Check(empty.Process(White()).Outcome == TableOutcome.PassThrough, "empty list passes common fish through");
        }

        static void ChumYields()
        {
            var t = new TableOrders(); t.Add(ProductKind.Chum, TableOrders.Infinite);
            Check(t.Process(FishClass.White, Species.Herring, .15f).Units == 1, "white -> 1 chum");
            Check(t.Process(FishClass.Green, Species.YellowfinTuna, 6f).Units == 2, "green -> 2 chum");
            Check(t.Process(FishClass.Blue, Species.Lionfish, 1f).Units == 3, "blue -> 3 chum");
            Check(t.Orders[0].Done == 3, "an order counts fish, not chum units");
            var chumOnly = new TableOrders(); chumOnly.Add(ProductKind.Chum, 10);
            Check(chumOnly.Process(FishClass.Gold, Species.GoldTipShark, 20f).Product == ProductKind.Special, "gold is never made into chum");
        }

        static void OrderSkipping()
        {
            // Top to bottom: oil once, then chum forever.
            var t = new TableOrders();
            t.Add(ProductKind.FishOil, 1); t.Add(ProductKind.Chum, TableOrders.Infinite);
            Check(t.Process(FishClass.White, Species.Herring, .15f).Product == ProductKind.FishOil, "first order first");
            Check(t.Process(FishClass.White, Species.Herring, .15f).Product == ProductKind.Chum, "satisfied order skipped");
            Check(t.Process(FishClass.Blue, Species.Lionfish, 1f).Units == 3, "starved order skipped for blue");
            Check(t.Orders[0].Done == 1 && t.Orders[1].Done == 2, "counts after skipping");
            // Chum first, oil second: oil is never reached while chum is infinite, white goes to chum.
            var t2 = new TableOrders();
            t2.Add(ProductKind.Chum, 1); t2.Add(ProductKind.FishOil, 1);
            Check(t2.Process(FishClass.White, Species.Herring, .15f).Product == ProductKind.Chum, "list order is priority");
            Check(t2.Process(FishClass.White, Species.Herring, .15f).Product == ProductKind.FishOil, "second order after first is done");
            Check(t2.Process(FishClass.White, Species.Herring, .15f).Outcome == TableOutcome.PassThrough, "both done: pass through");
        }

        static void BaitTable()
        {
            Check(Bait.All.Length == 4, "four baits");
            float[][] expected =
            {
                new float[] { 100, 0, 0, 0, 0, 0 },
                new float[] { 85, 15, 0, 0, 0, 0 },
                new float[] { 55, 30, 13, 2, 0, 0 },
                new float[] { 10, 20, 30, 30, 7, 3 },
            };
            float[] factor = { 1.0f, 0.9f, 0.85f, 0.8f };
            FishClass[] ceiling = { FishClass.White, FishClass.Green, FishClass.Purple, FishClass.Red };
            for (int k = 0; k < 4; k++)
            {
                var def = Bait.Def((BaitKind)k);
                float sum = 0;
                for (int c = 0; c < 6; c++)
                {
                    Check(def.Weights[c] == expected[k][c], def.Name + " weight " + (FishClass)c);
                    sum += def.Weights[c];
                }
                Check(sum == 100f, def.Name + " weights sum to 100");
                Check(def.BiteFactor == factor[k], def.Name + " bite factor");
                Check(def.Ceiling == ceiling[k], def.Name + " ceiling");
                // The ceiling is the best class with weight.
                for (int c = (int)def.Ceiling + 1; c < 6; c++) Check(def.Weights[c] == 0, def.Name + " has no weight above its ceiling");
            }
            Check(Bait.Scraps.Free && !Bait.Worms.Free && !Bait.Squid.Free && !Bait.Chum.Free, "only scraps are free");
            Check(Bait.DeepLineChumWeights.Length == 6 && Bait.DeepLineChumWeights[3] == 75f, "deep line chum weights kept");
        }

        static void BaitSelection()
        {
            var stock = new BaitStock(10, 10, 10);
            // A fisher with only scraps allowed never consumes chum.
            for (int i = 0; i < 50; i++) Check(Bait.TakeBest(BaitPermission.Scraps, stock) == BaitKind.Scraps, "scraps-only takes scraps");
            Check(stock.Chum == 10 && stock.Squid == 10 && stock.Worms == 10, "scraps-only fisher consumed no stock");
            Check(!Bait.CanBaitDeepLine(BaitPermission.Scraps, stock), "scraps-only fisher cannot bait a deep line");
            Check(Bait.CanBaitDeepLine(BaitPermission.Chum, stock) && !Bait.CanBaitDeepLine(BaitPermission.Chum, new BaitStock(5, 5, 0)), "deep line needs chum allowed and in stock");
            // Best first.
            Check(Bait.Best(BaitPermission.All, stock) == BaitKind.Chum, "chum is best");
            Check(Bait.Best(BaitPermission.Squid | BaitPermission.Worms | BaitPermission.Scraps, stock) == BaitKind.Squid, "squid next");
            Check(Bait.Best(BaitPermission.Worms | BaitPermission.Scraps, stock) == BaitKind.Worms, "worms next");
            Check(Bait.Best(BaitPermission.None, stock) == BaitKind.Scraps, "scraps when nothing is allowed (bait never blocks fishing)");
            // Falls back through empty stock.
            var thin = new BaitStock(3, 0, 0);
            Check(Bait.Best(BaitPermission.All, thin) == BaitKind.Worms, "falls back to worms");
            Check(Bait.TakeBest(BaitPermission.All, thin) == BaitKind.Worms && thin.Worms == 2, "taking spends one");
            thin.Worms = 0;
            Check(Bait.Best(BaitPermission.All, thin) == BaitKind.Scraps, "falls back to scraps");
            Check(Bait.Best(BaitPermission.All, null) == BaitKind.Scraps, "null stock is scraps");
        }

        static float[] RollShares(float[] weights, int seed, int n)
        {
            var rng = new System.Random(seed);
            var counts = new int[6];
            for (int i = 0; i < n; i++) counts[(int)Bait.RollClass(weights, rng)]++;
            var share = new float[6];
            for (int i = 0; i < 6; i++) share[i] = 100f * counts[i] / n;
            return share;
        }

        static void ClassRolls()
        {
            const int n = 20000;
            // Every bait reproduces its weights within 1 percentage point; scraps and worms never exceed their ceiling.
            for (int k = 0; k < 4; k++)
            {
                var def = Bait.Def((BaitKind)k);
                var share = RollShares(def.Weights, 1000 + k, n);
                for (int c = 0; c < 6; c++)
                    Check(Mathf.Abs(share[c] - def.Weights[c]) <= 1f, def.Name + " roll share of " + (FishClass)c + " was " + share[c]);
            }
            var deep = RollShares(Bait.DeepLineChumWeights, 77, n);
            for (int c = 0; c < 6; c++) Check(Mathf.Abs(deep[c] - Bait.DeepLineChumWeights[c]) <= 1f, "deep line chum share of " + (FishClass)c + " was " + deep[c]);
            // Determinism: the same seed gives the same sequence; the Random-taking overloads agree.
            var a = new System.Random(5); var b = new System.Random(5);
            for (int i = 0; i < 1000; i++) Check(Bait.RollClass(BaitKind.Chum, a) == Bait.RollClass(Bait.Chum.Weights, b), "deterministic rolls");
        }

        static void SquidPurpleCap()
        {
            // Sea bass 1..3 kg: midpoint 2 kg. A purple squid roll above that becomes blue.
            Check(Bait.PurpleAllowed(BaitKind.Squid, Species.SeaBass, 1.9f), "lower half allowed");
            Check(!Bait.PurpleAllowed(BaitKind.Squid, Species.SeaBass, 2.6f), "upper half refused");
            Check(Bait.ApplyCeiling(BaitKind.Squid, FishClass.Purple, Species.SeaBass, 2.6f) == FishClass.Blue, "large purple squid catch demoted to blue");
            Check(Bait.ApplyCeiling(BaitKind.Squid, FishClass.Purple, Species.SeaBass, 1.5f) == FishClass.Purple, "small purple squid catch kept");
            Check(Bait.ApplyCeiling(BaitKind.Squid, FishClass.Blue, Species.SeaBass, 2.9f) == FishClass.Blue, "blue untouched");
            Check(Bait.ApplyCeiling(BaitKind.Chum, FishClass.Purple, Species.SeaBass, 2.9f) == FishClass.Purple, "chum purple unrestricted");
        }

        static void BiteWaitMaths()
        {
            // Harbour mouth (0.85) with scraps at full richness: about 5.1 s plus the power term.
            Check(Mathf.Abs(Bait.BiteWait(0.85f, BaitKind.Scraps, 1f, 0f) - 5.1f) < 0.001f, "harbour mouth scraps 5.1 s");
            Check(Bait.BiteWait(0.85f, BaitKind.Scraps, 0.3f, 1f) == 12f, "drained ground hits the 12 s cap");
            Check(Bait.BiteWait(0.5f, BaitKind.Chum, 2f, 0f) == 4f, "floor at 4 s");
            Check(Bait.BiteWait(1f, BaitKind.Chum, 1f, 0f) < Bait.BiteWait(1f, BaitKind.Scraps, 1f, 0f), "better bait bites sooner");
        }
    }
}

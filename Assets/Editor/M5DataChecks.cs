using System;
using System.Collections.Generic;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEngine;

namespace Catchline.EditorTools
{
    // M5 data layer: buyers, reputation, contracts, quota and stakes. Pure logic, no scene.
    public static class M5DataChecks
    {
        static void Check(bool ok, string message)
        {
            if (!ok) throw new Exception("[Catchline] M5 data check failed: " + message);
        }

        public static void Run()
        {
            BuyerRules();
            SplitSaleTotals();
            WhiteHerringToBaitShop();
            ReputationTiers();
            ContractBoard();
            ContractProgressAndFailure();
            QuotaFineAndClosure();
            StakesAndFrayedRig();
            Debug.Log("[Catchline] M5 DATA CHECKS PASSED");
        }

        static void BuyerRules()
        {
            Check(Buyers.All.Length == 5 && Buyers.Def(BuyerId.Collector).Name == "Collector", "five buyers");
            var ctx = new SaleContext();
            ctx.NamedSpecies.Add(Species.Lionfish);
            var lion = SaleItem.Fish(Species.Lionfish, FishClass.Blue, 1f, 100);
            Check(Buyers.Offer(BuyerId.Market, lion, ctx) == 100, "market pays base");
            Check(Buyers.Offer(BuyerId.Restaurant, lion, ctx) == 130, "restaurant pays x1.3 for named blue+");
            Check(Buyers.Offer(BuyerId.Restaurant, lion, new SaleContext()) == -1, "restaurant ignores unnamed species");
            Check(Buyers.Offer(BuyerId.Restaurant, SaleItem.Fish(Species.Lionfish, FishClass.Green, 1f, 100), ctx) == -1, "restaurant wants blue and above");
            Check(Buyers.Offer(BuyerId.BaitShop, SaleItem.Fish(Species.Herring, FishClass.White, .2f, 2), ctx) == 3, "bait shop white floor 3");
            Check(Buyers.Offer(BuyerId.BaitShop, SaleItem.Fish(Species.Pollock, FishClass.Green, 1f, 5), ctx) == 6, "bait shop green floor 6");
            Check(Buyers.Offer(BuyerId.BaitShop, lion, ctx) == -1, "bait shop does not buy blue");
            Check(Buyers.Offer(BuyerId.BaitShop, SaleItem.Squid(2), ctx) == 16, "bait shop squid 8 each");
            Check(Buyers.Offer(BuyerId.Cannery, SaleItem.FishOil(5), ctx) == 40, "cannery fish oil 8 per unit");
            Check(Buyers.Offer(BuyerId.Cannery, lion, ctx) == -1, "cannery buys only oil");
            var tooth = SaleItem.Special(Species.GoldTipShark, 20f);
            Check(Buyers.Offer(BuyerId.Collector, tooth, ctx) == tooth.BaseValue && tooth.BaseValue > 0, "collector pays the table price");
            Check(Buyers.Offer(BuyerId.Market, tooth, ctx) == -1, "market does not buy special products");
            // No saturation: the offer for the same item never changes with volume.
            var many = new List<SaleItem>();
            for (int i = 0; i < 200; i++) many.Add(SaleItem.Fish(Species.Cod, FishClass.White, 3f, 51));
            Check(Buyers.SplitSale(many, ctx).Total == 200 * 51, "no market saturation");
        }

        static void SplitSaleTotals()
        {
            var ctx = new SaleContext();
            ctx.NamedSpecies.Add(Species.Lionfish);
            var items = new List<SaleItem>
            {
                SaleItem.Fish(Species.Herring, FishClass.White, .15f, 2),      // bait shop floor 3
                SaleItem.Fish(Species.Mackerel, FishClass.White, .6f, 8),      // market
                SaleItem.Fish(Species.Pollock, FishClass.Green, 1.2f, 4),      // bait shop floor 6
                SaleItem.Fish(Species.Lionfish, FishClass.Blue, 1f, 45),       // restaurant 59 (58.5 rounds away from zero)
                SaleItem.Fish(Species.Turbot, FishClass.Blue, 3f, 66),         // market (not named)
                SaleItem.FishOil(7),                                            // cannery 56
                SaleItem.Squid(3),                                              // bait shop 24
                SaleItem.Special(Species.SpottedEagleRay, 9f),                  // collector
            };
            var report = Buyers.SplitSale(items, ctx);
            Check(report.Unsold.Count == 0, "everything finds a buyer");
            int expected = 3 + 8 + 6 + 59 + 66 + 56 + 24 + items[7].BaseValue;
            Check(report.Total == expected, "report total equals the sum of the best offers (" + report.Total + " vs " + expected + ")");
            int lines = 0, itemCount = 0;
            foreach (var l in report.Lines)
            {
                int sum = 0;
                foreach (var it in l.Items) { Buyers.BestBuyer(it, ctx, out int p); Check(Buyers.BestBuyer(it, ctx, out _) == l.Buyer, "item sits with its best buyer"); sum += p; }
                Check(sum == l.Total, "line total equals its item sum for " + l.Buyer);
                lines += l.Total; itemCount += l.Items.Count;
            }
            Check(lines == report.Total && itemCount == items.Count, "line totals add up to the report; no item lost or duplicated");
            Check(report.TotalFor(BuyerId.BaitShop) == 3 + 6 + 24 && report.TotalFor(BuyerId.Cannery) == 56 && report.TotalFor(BuyerId.Restaurant) == 59 && report.TotalFor(BuyerId.Market) == 74, "per buyer split");
            // A randomised haul: totals still equal the sum of the winning offers.
            var rng = new System.Random(3);
            var haul = new List<SaleItem>();
            long indep = 0;
            for (int i = 0; i < 400; i++)
            {
                SaleItem it;
                switch (rng.Next(5))
                {
                    case 0: it = SaleItem.Fish(Species.Herring, FishClass.White, .2f, 1 + rng.Next(6)); break;
                    case 1: it = SaleItem.Fish(Species.Cod, FishClass.Green, 3f, 20 + rng.Next(60)); break;
                    case 2: it = SaleItem.Fish(Species.Lionfish, FishClass.Blue, 1f, 20 + rng.Next(60)); break;
                    case 3: it = SaleItem.FishOil(1 + rng.Next(5)); break;
                    default: it = SaleItem.Squid(1 + rng.Next(3)); break;
                }
                haul.Add(it);
                int best = -1;
                for (int b = 0; b < 5; b++) best = Math.Max(best, Buyers.Offer((BuyerId)b, it, ctx));
                indep += best;
            }
            Check(Buyers.SplitSale(haul, ctx).Total == indep, "random haul total equals independent best-offer sum");
        }

        static void WhiteHerringToBaitShop()
        {
            // The static table price of a 0.15 kg herring is about 2 coins, below the Bait shop floor of 3.
            var herring = SaleItem.FishAtBase(Species.Herring, FishClass.White, 0.15f);
            Check(herring.BaseValue < Buyers.BaitShopWhiteFloor, "herring base is below the floor (" + herring.BaseValue + ")");
            var one = Buyers.SplitSale(new[] { herring });
            Check(one.Lines.Count == 1 && one.Lines[0].Buyer == BuyerId.BaitShop && one.Total == 3, "a white herring goes to the Bait shop when the floor beats base");
            // A heavy herring is worth more than the floor at the Market.
            var big = SaleItem.FishAtBase(Species.Herring, FishClass.White, 0.3f);
            Check(big.BaseValue > Buyers.BaitShopWhiteFloor, "0.3 kg herring beats the floor (" + big.BaseValue + ")");
            Check(Buyers.SplitSale(new[] { big }).Lines[0].Buyer == BuyerId.Market, "...and goes to the Market");
            // Real fish through the class rules.
            var fish = new CaughtFish { Species = Species.Herring, Kg = 0.15f };
            var viaFish = SaleItem.FromFish(fish, herring.BaseValue);
            Check(viaFish.Class == FishClass.White && Buyers.BestBuyer(viaFish, null, out _) == BuyerId.BaitShop, "FromFish classifies and routes");
        }

        static void ReputationTiers()
        {
            Check(Buyers.TierForRep(0) == 0 && Buyers.TierForRep(999) == 0, "below 1,000 is tier 0");
            Check(Buyers.TierForRep(1000) == 1 && Buyers.TierForRep(4999) == 1, "1,000 is tier 1");
            Check(Buyers.TierForRep(5000) == 2 && Buyers.TierForRep(19999) == 2, "5,000 is tier 2");
            Check(Buyers.TierForRep(20000) == 3 && Buyers.TierForRep(1000000) == 3, "20,000 is tier 3");
            var rep = new BuyerReputation();
            rep.AddSale(BuyerId.Collector, 199);
            Check(rep.Rep(BuyerId.Collector) == 1, "rep is coins sold / 100");
            rep.AddSale(BuyerId.Collector, 99801);
            Check(rep.Rep(BuyerId.Collector) == 1000 && rep.Tier(BuyerId.Collector) == 1, "100,000 coins = 1,000 rep = tier 1");
            // Exact unlock lists.
            string[] all = { "bulk_bait_packs", "squid_lights", "heavy_net_system", "deep_line_rigs", "cage_sets" };
            Check(Buyers.UnlockedItems(0).Count == 0, "nothing unlocked at tier 0");
            var unlocked = Buyers.UnlockedItems(1);
            Check(unlocked.Count == all.Length, "tier 1 unlocks exactly the five listed items");
            foreach (var id in all) Check(unlocked.Contains(id), "unlocks " + id);
            Check(Buyers.Unlocked(BuyerId.BaitShop, "bulk_bait_packs", 1) && !Buyers.Unlocked(BuyerId.BaitShop, "bulk_bait_packs", 0), "bait shop: bulk bait packs");
            Check(Buyers.Unlocked(BuyerId.Restaurant, "squid_lights", 1), "restaurant: squid lights");
            Check(Buyers.Unlocked(BuyerId.Cannery, "heavy_net_system", 1), "cannery: heavy net system");
            Check(Buyers.Unlocked(BuyerId.Collector, "deep_line_rigs", 1) && Buyers.Unlocked(BuyerId.Collector, "cage_sets", 1), "collector: deep-line rigs and cage sets");
            Check(!Buyers.Unlocked(BuyerId.Market, "squid_lights", 3) && !Buyers.Unlocked(BuyerId.Collector, "squid_lights", 3), "items belong to their own buyer only");
            Check(Buyers.Def(BuyerId.Market).Unlocks.Length == 0, "market unlocks nothing");
            Check(rep.Unlocked(BuyerId.Collector, "cage_sets") && !rep.Unlocked(BuyerId.Cannery, "heavy_net_system"), "reputation gates per buyer");
            // Selling through a report feeds reputation.
            var r2 = new BuyerReputation();
            r2.AddSale(Buyers.SplitSale(new[] { SaleItem.Fish(Species.Cod, FishClass.White, 3f, 500) }));
            Check(r2.CoinsSold(BuyerId.Market) == 500 && r2.Rep(BuyerId.Market) == 5, "sale report adds rep");
        }

        static Contract Make(string id, ContractType type, BuyerId giver, float target, int deadline, Species? species = null, FishClass? cls = null, int tier = 0) =>
            new Contract { Id = id, Type = type, Giver = giver, Target = target, DeadlineVoyages = deadline, VoyagesLeft = deadline,
                Species = species, Class = cls, RewardCoins = 100, RewardRep = 50, RewardChest = true, Tier = tier };

        static void ContractBoard()
        {
            var board = new ContractBoard();
            var rep = new BuyerReputation();
            for (int i = 0; i < 3; i++) Check(board.Offer(Make("o" + i, ContractType.Species, BuyerId.Market, 3, 2, Species.Cod)), "board takes three");
            Check(!board.Offer(Make("o3", ContractType.Species, BuyerId.Market, 3, 2, Species.Cod)), "board holds at most three");
            Check(board.Accept(board.Offers[0]) && board.Accept(board.Offers[0]), "accept two");
            Check(!board.Accept(board.Offers[0]) && board.Active.Count == 2, "max two active");
            Check(board.Offers.Count == 1 && board.Offer(Make("o4", ContractType.Special, BuyerId.Collector, 1, 2)), "accepting frees a board slot");
            // Tiered contracts need reputation.
            var b2 = new ContractBoard();
            Check(!b2.Offer(Make("t1", ContractType.Class, BuyerId.Restaurant, 10, 3, null, FishClass.Blue, 1), rep), "tier 1 contract refused at tier 0");
            rep.AddSale(BuyerId.Restaurant, 100000);
            Check(b2.Offer(Make("t1", ContractType.Class, BuyerId.Restaurant, 10, 3, null, FishClass.Blue, 1), rep), "tier 1 contract offered at tier 1");
            // Fill from a pool with a seeded Random is deterministic and respects the cap.
            var pool = new List<Contract>
            {
                Make("p0", ContractType.Species, BuyerId.Market, 2, 2, Species.Cod),
                Make("p1", ContractType.NightSpecies, BuyerId.Restaurant, 2, 2, Species.Cod, null, 2),
                Make("p2", ContractType.Special, BuyerId.Collector, 1, 3),
            };
            var b3 = new ContractBoard(); var b4 = new ContractBoard();
            int id3 = 0, id4 = 0;
            b3.Fill(pool, new BuyerReputation(), new System.Random(9), ref id3);
            b4.Fill(pool, new BuyerReputation(), new System.Random(9), ref id4);
            Check(b3.Offers.Count == 3 && b4.Offers.Count == 3, "fill reaches three");
            for (int i = 0; i < 3; i++) Check(b3.Offers[i].Type == b4.Offers[i].Type && b3.Offers[i].Tier == 0, "fill is seeded and respects tiers");
        }

        static void ContractProgressAndFailure()
        {
            var rep = new BuyerReputation();
            var board = new ContractBoard();
            var species = Make("s", ContractType.Species, BuyerId.Market, 2, 2, Species.Cod);
            var klass = Make("k", ContractType.Class, BuyerId.Restaurant, 5f, 3, null, FishClass.Blue);
            board.Offer(species); board.Offer(klass);
            board.Accept(species); board.Accept(klass);
            // A fish goes to the first matching active contract only.
            Check(board.Deliver(Delivery.OfFish(Species.Cod, FishClass.White, 3f), rep).Count == 0 && species.Progress == 1, "species counts one per fish");
            Check(board.Deliver(Delivery.OfFish(Species.Lionfish, FishClass.Blue, 2f), rep).Count == 0 && klass.Progress == 2f, "class counts kg");
            Check(board.Deliver(Delivery.OfSpecial(Species.Cod, 1f), rep).Count == 0 && species.Progress == 1, "special product never counts as a fish");
            var done = board.Deliver(Delivery.OfFish(Species.Cod, FishClass.White, 3f), rep);
            Check(done.Count == 1 && done[0].Result == ContractResult.Completed && done[0].Coins == 100 && done[0].Chest && done[0].Rep == 50, "completion pays coins, rep and chest");
            Check(rep.Rep(BuyerId.Market) == 50 && board.Active.Count == 1, "completed contract leaves the active list and pays rep to its giver");
            // Night species only counts at night; special may filter by species.
            var night = Make("n", ContractType.NightSpecies, BuyerId.Restaurant, 1, 1, Species.Cod);
            var spec = Make("sp", ContractType.Special, BuyerId.Collector, 1, 1, Species.GoldTipShark);
            Check(!night.Accepts(Delivery.OfFish(Species.Cod, FishClass.White, 3f, false)) && night.Accepts(Delivery.OfFish(Species.Cod, FishClass.White, 3f, true)), "night species needs a night catch");
            Check(spec.Accepts(Delivery.OfSpecial(Species.GoldTipShark, 20f)) && !spec.Accepts(Delivery.OfSpecial(Species.ApexReefShark, 20f)), "special filters by species when set");
            // Failure: run out of voyages unfinished = -500 rep with the giver, never below zero.
            rep.AddSale(BuyerId.Restaurant, 100000);   // 1,000 rep
            int before = rep.Rep(BuyerId.Restaurant);
            Check(board.EndVoyage(rep).Count == 0 && klass.VoyagesLeft == 2, "deadline counts in voyages");
            board.EndVoyage(rep);
            var failed = board.EndVoyage(rep);
            Check(failed.Count == 1 && failed[0].Result == ContractResult.Failed && failed[0].Rep == -500 && failed[0].Coins == 0, "unfinished contract fails after its deadline");
            Check(rep.Rep(BuyerId.Restaurant) == before - 500 && board.Active.Count == 0, "failure costs 500 rep with that buyer");
            var lowRep = new BuyerReputation();
            lowRep.Adjust(BuyerId.Cannery, -500);
            Check(lowRep.Rep(BuyerId.Cannery) == 0, "rep never reads below zero");
        }

        static void QuotaFineAndClosure()
        {
            Check(Quota.LimitKg(FishClass.Blue) == 30f && Quota.LimitKg(FishClass.Purple) == 20f && Quota.LimitKg(FishClass.Gold) == 10f && Quota.LimitKg(FishClass.Red) == 5f, "quota limits");
            Check(float.IsPositiveInfinity(Quota.LimitKg(FishClass.White)) && float.IsPositiveInfinity(Quota.LimitKg(FishClass.Green)), "white and green unlimited");
            var q = new QuotaLedger();
            Check(q.BeginVoyage("harbour"), "depart");
            // Within quota: no fine, no closure. Unlimited classes never count.
            q.Record("harbour", FishClass.Blue, 30f, 300);
            q.Record("harbour", FishClass.White, 5000f, 60000);
            var ok = q.Inspect("harbour");
            Check(ok.Fine == 0 && !ok.GroundClosed && !q.IsClosed("harbour"), "at quota is fine");
            // Excess: 10 kg gold over, valued at the class average 50/kg -> fine = 2 x 500.
            q.Record("harbour", FishClass.Gold, 20f, 1000);
            // Throwbacks are exempt.
            q.Record("harbour", FishClass.Gold, 100f, 99999, true);
            Check(q.Kept("harbour", FishClass.Gold) == 20f, "throwbacks are exempt");
            Check(q.Remaining("harbour", FishClass.Gold) == 0f && q.Remaining("harbour", FishClass.Blue) == 0f, "remaining quota");
            var r = q.Inspect("harbour");
            Check(r.ExcessKg[(int)FishClass.Gold] == 10f && r.ExcessKg[(int)FishClass.Blue] == 0f, "excess kg");
            Check(r.Fine == 1000, "fine is 2x the excess value (got " + r.Fine + ")");
            Check(r.GroundClosed && q.IsClosed("harbour") && q.ClosedVoyagesLeft("harbour") == 3, "ground closes for three voyages");
            // Closed for exactly three voyages: departures elsewhere tick it down.
            Check(!q.BeginVoyage("harbour"), "cannot depart to the closed ground");
            Check(q.BeginVoyage("reef") && q.ClosedVoyagesLeft("harbour") == 2, "voyage 1 elsewhere");
            Check(!q.BeginVoyage("harbour"), "still closed");
            Check(q.BeginVoyage("reef") && q.ClosedVoyagesLeft("harbour") == 1, "voyage 2 elsewhere");
            Check(q.BeginVoyage("reef") && !q.IsClosed("harbour"), "voyage 3 elsewhere reopens it");
            Check(q.BeginVoyage("harbour"), "open again after three voyages");
            // New voyage = clean ledger.
            Check(q.Kept("harbour", FishClass.Gold) == 0f, "ledger resets on departure");
        }

        static void StakesAndFrayedRig()
        {
            Check(Stakes.TripCost(100, 40, 25, 15) == 180 && Stakes.TripCost(0, 0, 0, 0) == 0, "trip cost is wages + fuel + bait + lantern oil");
            Check(Stakes.SpareRigPrice == 5, "spare rig costs 5");
            var rigs = new SpareRigs(2);
            Check(!rigs.Frayed && rigs.StrikeWindow(1f) == 1f, "with spares the window is normal");
            Check(rigs.Snag() && rigs.Count == 1 && !rigs.Frayed, "a snag spends one");
            Check(rigs.Snag() && rigs.Count == 0 && rigs.Frayed, "none left = frayed");
            Check(Mathf.Abs(rigs.StrikeWindow(1f) - 0.8f) < 0.0001f, "frayed strike window is -20%");
            Check(!rigs.Snag() && rigs.Count == 0, "a snag with none left spends nothing");
            for (int i = 0; i < 20; i++) { rigs.Snag(); Check(rigs.Usable && rigs.StrikeWindow(1f) > 0f, "frayed rig is never unusable"); }
            int spent = rigs.Buy(3, 12);
            Check(spent == 10 && rigs.Count == 2 && !rigs.Frayed, "buying spends 5 each and limits to what coins afford");
            Check(rigs.Buy(5, 4) == 0, "cannot afford");
        }
    }
}

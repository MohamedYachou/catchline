using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Catchline.Game;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Analysis only. No Load/Save, scene, PlayerPrefs, or persistent data mutation.
    public static class CardPacingSim
    {
        const int Seeds = 200, Days = 180, Missing = 181, OperatingCoins = 10;
        const string Focus = "noor";
        static readonly int[] Trips = { 2, 5, 10 };
        static readonly string[] Profiles = { "casual", "regular", "heavy" };
        sealed class Result
        {
            public int Seed, Profile;
            public int[] Reached = { Missing, Missing, Missing, Missing };
            public int[] HullDays = { 1, Missing, Missing, Missing };
            public int[] Road = new int[3], Renown = new int[3];
            public long Earned, Spent, Haul, ChestTokens, RoadTokens, Sales, Wages, Operating, Hulls, Levels, ChestCoins;
            public int ChestCount, SeaCount, Blueprints, FocusBlueprints, Daily, Contract, Missed, EndingCoins, EndingTokens;
            public long[,] Blocked = new long[6, 3]; // rarity; coin, tokens, blueprint; non-exclusive
        }
        static void Require(bool ok, string why) { if (!ok) throw new Exception("Card pacing: " + why); }
        static int TrackTokens(GameState s, Result r, Action action)
        {
            int before = s.Tokens; action(); int diff = s.Tokens - before;
            if (diff >= 0) r.Earned += diff; else r.Spent -= diff;
            return diff;
        }
        static void Record(GameState s, Result r, int day)
        {
            var c = CardRoster.Find(s.Roster, Focus);
            var targets = new[] { CardRarity.Purple, CardRarity.Gold, CardRarity.Mythic };
            for (int i = 0; i < 3; i++) if (c.Rarity >= targets[i] && r.Reached[i] == Missing) r.Reached[i] = day;
            if (c.Maxed && r.Reached[3] == Missing) r.Reached[3] = day;
        }
        static void Settle(GameState s, Result r, int day)
        {
            for (int pass = 0; pass < 100; pass++)
            {
                bool changed = false;
                while (s.PendingChests.Count > 0)
                {
                    ChestKind kind = s.PendingChests[0]; ChestResult chest = null;
                    r.ChestTokens += TrackTokens(s, r, () => chest = s.OpenChest(kind));
                    Require(chest != null, "pending chest must open");
                    r.ChestCount++; if (kind == ChestKind.SeaChest) r.SeaCount++;
                    r.Blueprints += chest.Blueprints.Count + chest.FreeBlueprints;
                    r.FocusBlueprints += chest.Blueprints.Count(id => id == Focus) + (Chests.WantsBlueprints(CardRoster.Find(s.Roster, Focus)) ? chest.FreeBlueprints : 0);
                    changed = true;
                }
                while (s.AssignFreeBlueprint(Focus)) changed = true;
                int beforeCoins = s.Coins;
                int delta = TrackTokens(s, r, () => { while (s.Coins >= CardProgression.CoinsForLevel(CardRoster.Find(s.Roster, Focus).Level) + s.DepartureWages + OperatingCoins + 10 && s.LevelUpCard(Focus)) changed = true; });
                r.Levels += beforeCoins - s.Coins;
                Require(delta <= 0, "levels cannot grant tokens");
                while (s.RankUpCard(Focus)) changed = true;
                while (s.Renown >= RenownRoad.Threshold(s.RenownClaimed + 1))
                {
                    int n = s.RenownClaimed + 1;
                    string choice = Chests.WantsBlueprints(CardRoster.Find(s.Roster, Focus)) ? Focus : s.Roster.First(c => Chests.WantsBlueprints(c)).Id;
                    bool ok = false;
                    r.RoadTokens += TrackTokens(s, r, () => ok = s.ClaimRenown(n, choice));
                    Require(ok, "eligible road claim"); changed = true;
                }
                Record(s, r, day);
                if (!changed) return;
            }
            throw new Exception("Card pacing settlement did not converge");
        }
        static void Deploy(GameState s)
        {
            // Conditional progression experiment: recruit the unlocked tier without acquisition cost.
            s.GrantTrialCards();
            foreach (var c in s.Roster)
                if (s.Deployment.Count < s.CardBerths) s.DeployCard(c.Id, true);
            Require(s.Deployment.Count == s.CardBerths, "fill all real card berths");
        }
        static void BuyHull(GameState s, Result r, int day)
        {
            int before = s.Coins, hull = s.Hull;
            // One necessary hold upgrade clears the real 100kg Prep refit gate.
            if (s.Hull == 2 && !s.Has(UpgradeId.BigCooler) && s.Coins >= s.UpgradeCost(UpgradeId.BigCooler) + s.DepartureWages + OperatingCoins) s.TryBuy(UpgradeId.BigCooler);
            int nextTier = s.Hull == 1 ? 2 : s.Hull == 2 ? 4 : 5;
            int reserve = Cards.All.Where(d => d.TierGranted <= nextTier).Take(CardRoster.BerthsForTier(nextTier)).Sum(d => (CardRoster.Find(s.Roster, d.Id) ?? new CardState(d.Id)).Wage()) + OperatingCoins;
            int cost = s.Hull == 1 ? GameState.CompactFisherCost : s.Hull == 2 ? GameState.PrepFisherCost : GameState.Tier5Cost;
            if (s.Coins < cost + reserve) { r.Hulls += before - s.Coins; return; }
            if (s.Hull == 1) s.RefitCompact();
            else if (s.Hull == 2) s.RefitPrep();
            else if (s.Hull == 3) s.RefitTier5();
            r.Hulls += before - s.Coins;
            if (s.Hull != hull) { r.HullDays[s.Hull - 1] = day; Deploy(s); }
        }
        static List<CaughtFish> Catch(GameState s, System.Random rng, float kg)
        {
            // Equal draws among ordinary early fish eligible on this hull. No rare jackpots; this is an assumed haul, not catch-time simulation.
            Species[] pool = { Species.Herring, Species.Mackerel, Species.Pollock, Species.SeaBass, Species.Cod };
            var eligible = pool.Where(x => GameData.MinimumHull(x) <= s.Hull).ToArray();
            var fish = new List<CaughtFish>();
            while (kg > .0001f)
            {
                Species species = eligible[rng.Next(eligible.Length)]; var d = GameData.Get(species);
                float weight = Math.Min(kg, d.MinKg + (float)rng.NextDouble() * (d.MaxKg - d.MinKg));
                fish.Add(new CaughtFish { Species = species, Kg = weight, StowedAt = 0 }); kg -= weight;
            }
            return fish;
        }
        static Result Simulate(int profile, int seed)
        {
            var r = new Result { Profile = profile, Seed = seed };
            var s = new GameState(seed) { Hull = 1, Coins = GameData.StartCoins };
            // Separate stream keeps fill/income draws identical between chest-odds proposals.
            var rng = new System.Random(seed + 100000);
            s.Active.Clear(); Deploy(s); Require(s.SetFocus(Focus), "focus owned"); Settle(s, r, 1);
            for (int day = 1; day <= Days; day++)
            {
                for (int trip = 0; trip < Trips[profile]; trip++)
                {
                    int coins = s.Coins;
                    if (!s.PayDepartureWages()) { r.Missed++; continue; }
                    r.Wages += coins - s.Coins;
                    // Ten coins covers the assumed fuel/bait reserve; a failed departure never earns rewards.
                    if (s.Coins < OperatingCoins) { int paid = coins - s.Coins; s.Coins += paid; r.Wages -= paid; s.TripDeployment.Clear(); r.Missed++; continue; }
                    s.Coins -= OperatingCoins; r.Operating += OperatingCoins;
                    float fill = .6f + .4f * (float)rng.NextDouble();
                    float kg = s.CoolerCapacity * fill;
                    var sale = s.Sell(Catch(s, rng, kg), 0);
                    r.Sales += sale.Coins + sale.ContractCoins;
                    s.BestVoyageKg = Math.Max(s.BestVoyageKg, kg); // live return path records this outside Sell
                    r.Haul += TrackTokens(s, r, () => s.AwardHaulTokens(kg));
                    if (s.GrantDailyCrate(new DateTime(2030, 1, 1).AddDays(day - 1))) r.Daily++;
                    Require(!s.GrantDailyCrate(new DateTime(2030, 1, 1).AddDays(day - 1)), "daily crate dedup");
                    if (trip == 0 && day % 3 == 0) { s.GrantChest(ChestKind.Crate); r.Contract++; }
                    Settle(s, r, day); // focus spending first
                    BuyHull(s, r, day); // then progression; hull dates derive from actual sale income and prices
                    Settle(s, r, day); // trial recruitment can immediately unlock road rewards
                    while (s.Coins > 3L * s.ChestPrice(ChestKind.SeaChest))
                    {
                        coins = s.Coins; Require(s.BuyChest(ChestKind.SeaChest), "affordable sea chest");
                        r.ChestCoins += coins - s.Coins; Settle(s, r, day);
                    }
                    var c = CardRoster.Find(s.Roster, Focus); int stage = (int)c.Rarity;
                    if (c.AtCap && !c.Maxed && c.Blueprints < c.BlueprintsNeeded) r.Blocked[stage, 2]++;
                    if (!c.AtCap)
                    {
                        if (s.Coins < CardProgression.CoinsForLevel(c.Level) + s.DepartureWages + OperatingCoins + 10) r.Blocked[stage, 0]++;
                        if (s.Tokens < CardProgression.TokensForLevel(c.Level)) r.Blocked[stage, 1]++;
                    }
                }
                int index = day == 30 ? 0 : day == 60 ? 1 : day == 180 ? 2 : -1;
                if (index >= 0) { r.Road[index] = s.RenownClaimed; r.Renown[index] = s.Renown; }
            }
            r.EndingCoins = s.Coins; r.EndingTokens = s.Tokens;
            Require(r.Earned - r.Spent == s.Tokens, "token conservation");
            Require(GameData.StartCoins + r.Sales - r.Wages - r.Operating - r.Hulls - r.Levels - r.ChestCoins == s.Coins, "coin conservation");
            Require(s.PendingChests.Count == 0, "all chests opened");
            Require(r.Missed == 0, "income assumptions must fund all requested trips");
            return r;
        }
        static int Quantile(IEnumerable<int> values, double p)
        { var a = values.OrderBy(x => x).ToArray(); return a[Math.Max(0, (int)Math.Ceiling(p * a.Length) - 1)]; }
        static string Day(int x) => x > Days ? ">180" : x.ToString(CultureInfo.InvariantCulture);
        static string Range(IEnumerable<int> a) => Day(Quantile(a, .5)) + " [" + Day(Quantile(a, .1)) + ", " + Day(Quantile(a, .9)) + "]";
        static string Number(IEnumerable<long> a) => a.Average(x => (double)x).ToString("0.0", CultureInfo.InvariantCulture);
        static void Tables(StringBuilder report, string name, List<Result> all)
        {
            report.AppendLine("## " + name).AppendLine();
            report.AppendLine("Days are median [p10, p90], nearest-rank over all 200 seeds; >180 is right censored, never omitted.");
            report.AppendLine("| Profile | Purple | Gold | Mythic level 30 | Mythic 5 stars | Mythic reached by 180 |").AppendLine("|---|---:|---:|---:|---:|---:|");
            for (int p = 0; p < 3; p++)
            {
                var rows = all.Where(r => r.Profile == p).ToArray();
                report.Append("| " + Profiles[p]);
                for (int k = 0; k < 4; k++) report.Append(" | " + Range(rows.Select(r => r.Reached[k])));
                report.AppendLine(" | " + rows.Count(r => r.Reached[2] <= Days) + "/200 |");
            }
            report.AppendLine().AppendLine("| Profile | Road milestone day 30 / 60 / 180 (median) | Renown day 30 / 60 / 180 (median) | Tier 2 / 4 / 5 days (median [p10,p90]) |").AppendLine("|---|---|---|---|");
            for (int p = 0; p < 3; p++)
            {
                var rows = all.Where(r => r.Profile == p).ToArray();
                report.AppendLine("| " + Profiles[p] + " | " + string.Join(" / ", Enumerable.Range(0, 3).Select(k => Quantile(rows.Select(r => r.Road[k]), .5))) + " | " + string.Join(" / ", Enumerable.Range(0, 3).Select(k => Quantile(rows.Select(r => r.Renown[k]), .5))) + " | " + string.Join(" / ", Enumerable.Range(1, 3).Select(k => Range(rows.Select(r => r.HullDays[k])))) + " |");
            }
            report.AppendLine().AppendLine("180-day means (tokens earned and spent are exact per-run reconciled ledgers):");
            report.AppendLine("| Profile | Haul tokens | Chest tokens | Road tokens | Total earned | Spent | Banked | Chests / sea chests | Dropped BP / focused BP |").AppendLine("|---|---:|---:|---:|---:|---:|---:|---:|---:|");
            for (int p = 0; p < 3; p++)
            {
                var rows = all.Where(r => r.Profile == p).ToArray();
                report.AppendLine("| " + Profiles[p] + " | " + Number(rows.Select(r => r.Haul)) + " | " + Number(rows.Select(r => r.ChestTokens)) + " | " + Number(rows.Select(r => r.RoadTokens)) + " | " + Number(rows.Select(r => r.Earned)) + " | " + Number(rows.Select(r => r.Spent)) + " | " + Number(rows.Select(r => (long)r.EndingTokens)) + " | " + Number(rows.Select(r => (long)r.ChestCount)) + " / " + Number(rows.Select(r => (long)r.SeaCount)) + " | " + Number(rows.Select(r => (long)r.Blueprints)) + " / " + Number(rows.Select(r => (long)r.FocusBlueprints)) + " |");
            }
            report.AppendLine().AppendLine("| Profile | Gross sale coins | Wages | Operating reserve | Hulls + cooler | Levels | Sea chests | Ending coins |").AppendLine("|---|---:|---:|---:|---:|---:|---:|---:|");
            for (int p = 0; p < 3; p++)
            {
                var rows = all.Where(r => r.Profile == p).ToArray();
                report.AppendLine("| " + Profiles[p] + " | " + Number(rows.Select(r => r.Sales)) + " | " + Number(rows.Select(r => r.Wages)) + " | " + Number(rows.Select(r => r.Operating)) + " | " + Number(rows.Select(r => r.Hulls)) + " | " + Number(rows.Select(r => r.Levels)) + " | " + Number(rows.Select(r => r.ChestCoins)) + " | " + Number(rows.Select(r => (long)r.EndingCoins)) + " |");
            }
            report.AppendLine().AppendLine("Blocked post-spend trip observations by current rank, pooled across seeds. Coin/token counters can overlap; blueprint waits count only at level cap. These identify the next progression gate, not a causal economic elasticity test.");
            report.AppendLine("| Profile | Current rank -> next | Coin | Tokens | Blueprints | Dominant gate |").AppendLine("|---|---|---:|---:|---:|---|");
            for (int p = 0; p < 3; p++) for (int k = 0; k < 6; k++)
            {
                var rows = all.Where(r => r.Profile == p).ToArray();
                long[] n = Enumerable.Range(0, 3).Select(b => rows.Sum(r => r.Blocked[k, b])).ToArray();
                int top = Array.IndexOf(n, n.Max());
                report.AppendLine("| " + Profiles[p] + " | " + (CardRarity)k + " -> " + (k == 5 ? "5 stars" : ((CardRarity)(k + 1)).ToString()) + " | " + n[0] + " | " + n[1] + " | " + n[2] + " | " + (n.Max() == 0 ? "none observed" : new[] { "coins", "tokens", "blueprints" }[top]) + " |");
            }
            report.AppendLine();
        }
        public static void Run()
        {
            string logs = Path.GetFullPath(Path.Combine(Application.dataPath, "../Logs")); Directory.CreateDirectory(logs);
            var report = new StringBuilder("# Crew card pacing — measured real API\n\n");
            report.AppendLine("200 seeds (1..200) per profile, 180 days, 2/5/10 trips daily. Focus Noor from White level 1; Mira excluded from focus progression. GrantTrialCards at every hull fills the unlocked roster for free (welcome reward removed); this isolates progression with full deployments and DOES NOT measure recruitment time or cost. All rarity/level/star costs and reward rolls use GameState APIs. No save is read or written. No game data source is edited.\n");
            report.AppendLine("Start already owning tier-1 Skiff, default StartCoins, no other equipment. Refit costs come from live constants (Compact 4000, Prep 9500, Buoy 18000). Buy BigCooler at tier2 (3000) to clear Prep's100kg gate; it persists on later hulls. The real CardTier path is 1/2/4/5: future tier3 is unavailable. Hull days below emerge from actual cash, not invented unlock dates.\n");
            report.AppendLine("Income assumption: each trip's target fill is uniform[0.6,1.0); fill each hold with equal draws of eligible Herring/Mackerel/Pollock/SeaBass/Cod, weight uniform within real species limits. Last fish is clipped to remaining target kg (synthetic haul approximation). Sell at time0 (fresh), with real specimen prices; no rare jackpot, depletion, catch-time, ability productivity, gear upgrades or contract cash. Deduct real wages and an assumed10coins/trip fuel/bait reserve. These are conditional economy estimates, not a one-hour gameplay measurement.\n");
            report.AppendLine("Working capital: level spending keeps departure wages +20coins; hull purchases retain the next deployment wages +10coins. Policy per return: real Sell; AwardHaulTokens using departure deployment; daily crate deduplicated by simulated date; one contract crate every third day. Open all chests, focus-level before rank/stars, claim renown immediately to Noor (after maxing, unused choices go to another eligible card), repeat to convergence. Then buy the next affordable hull/cooler, then repeatedly buy sea chests while coins exceed3xprice, settling after each. Other cards stay at starting rarity/level; deploy navigator then roster order to all real berths. No prestige. Separate seeded fill/income and chest RNG streams; same seeds per scenario, but hull timing can change with costs/rewards.\n");
            var csv = new StringBuilder("scenario,profile,seed,purple,gold,mythic,stars5,tier2,tier4,tier5,road30,road60,road180,tokensEarned,tokensSpent,coinsEnd,chests,seaChests\n");
            var sea = Chests.Def(ChestKind.SeaChest); float original = sea.BlueprintChance; int originalPrice = sea.PriceBase;
            try
            {
                float[] chances = { original, original, original, original }; int[] prices = { originalPrice, 2000, 3000, 6000 }; int scenario = 0;
                foreach (float chance in chances)
                {
                    sea.BlueprintChance = chance; sea.PriceBase = prices[scenario++];
                    string name = sea.PriceBase == originalPrice ? "Baseline" : "Sensitivity: Chests.All SeaChest.PriceBase " + originalPrice + " -> " + sea.PriceBase;
                    var results = new List<Result>();
                    for (int p = 0; p < 3; p++) for (int seed = 1; seed <= Seeds; seed++)
                    {
                        var r = Simulate(p, seed); results.Add(r);
                        csv.AppendLine(string.Join(",", new object[] { sea.PriceBase, Profiles[p], seed, r.Reached[0], r.Reached[1], r.Reached[2], r.Reached[3], r.HullDays[1], r.HullDays[2], r.HullDays[3], r.Road[0], r.Road[1], r.Road[2], r.Earned, r.Spent, r.EndingCoins, r.ChestCount, r.SeaCount }));
                    }
                    Tables(report, name, results);
                    var regular = results.Where(r => r.Profile == 1).ToArray();
                    Debug.Log("[Catchline] PACING " + name + " regular Gold=" + Range(regular.Select(r => r.Reached[1])) + " Mythic=" + Range(regular.Select(r => r.Reached[2])) + " stars5=" + Range(regular.Select(r => r.Reached[3])));
                }
            }
            finally { sea.BlueprintChance = original; sea.PriceBase = originalPrice; }
            Require(sea.BlueprintChance == original && sea.PriceBase == originalPrice, "restore proposal data in memory");
            File.WriteAllText(Path.Combine(logs, "cards-pacing-results.csv"), csv.ToString());
            File.WriteAllText(Path.Combine(logs, "cards-pacing-generated.md"), report.ToString());
            var manifest = new StringBuilder();
            using (var sha = SHA256.Create())
                foreach (string file in new[] { "Editor/CardPacingSim.cs", "Scripts/Game/GameState.cs", "Scripts/Game/GameStateCards.cs", "Scripts/Game/GameStateProgression.cs", "Scripts/Game/GameStateTier5.cs", "Scripts/Game/GameData.cs", "Scripts/Game/Data/CardProgression.cs", "Scripts/Game/Data/Chests.cs", "Scripts/Game/Data/CardState.cs", "Scripts/Game/Data/RenownRoad.cs", "Scripts/Game/Data/Cards.cs" })
                    manifest.AppendLine(BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(Path.Combine(Application.dataPath, file)))).Replace("-", "") + "  " + file);
            File.WriteAllText(Path.Combine(logs, "cards-pacing-sources.sha256"), manifest.ToString());
            Debug.Log("[Catchline] CARD PACING PASSED: 2400 runs; 432000 simulated days; per-run coin/token conservation, no missed departures, all pending chests opened, daily dedup and proposal restoration verified.");
            Debug.Log("[Catchline] Snapshot written to " + Path.Combine(logs, "cards-pacing-generated.md"));
        }
    }
}




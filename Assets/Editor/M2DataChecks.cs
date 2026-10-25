using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Crew cards v2 data layer (docs/plans/CREW-CARDS-V2.md): card table, progression maths, roster rules,
    // tools, chests, the renown road and the version-3 save.
    public static class M2DataChecks
    {
        static void Check(bool ok, string message)
        {
            if (!ok) throw new Exception("[Catchline] M2 data check failed: " + message);
        }

        static bool Near(float a, float b, float eps = 0.0005f) => Mathf.Abs(a - b) < eps;

        // Tokens for level L -> L+1, L = 1..29 (round(L^1.6) + 1).
        static readonly int[] ExpectedTokens =
        {
            2, 4, 7, 10, 14, 19, 23, 29, 35, 41, 47, 54, 62, 69, 77,
            85, 94, 103, 112, 122, 131, 142, 152, 163, 173, 185, 196, 208, 220,
        };

        public static void Run()
        {
            Progression();
            Wages();
            CardTable();
            SkillsAndStrike();
            RosterRules();
            LevelsAndRanks();
            ToolRules();
            ChestRules();
            RenownRules();
            SaveV3();
            Debug.Log("[Catchline] M2 DATA CHECKS PASSED");
        }

        static void Progression()
        {
            int[] caps = { 5, 10, 15, 20, 30, 30 };
            int[] blueprints = { 1, 1, 2, 3, 4, 0 };
            int[] slots = { 1, 1, 2, 2, 3, 3 };
            for (int r = 0; r < 6; r++)
            {
                var rarity = (CardRarity)r;
                Check(CardProgression.LevelCap(rarity) == caps[r], "level cap " + rarity);
                Check(CardProgression.BlueprintsToRankUp(rarity) == blueprints[r], "rank-up blueprints " + rarity);
                Check(CardProgression.ToolSlots(rarity) == slots[r], "tool slots " + rarity);
            }
            Check(!CardProgression.CanRankUp(CardRarity.Mythic) && CardProgression.CanRankUp(CardRarity.Gold), "Mythic is the top rank");
            Check(CardProgression.RarityName(CardRarity.Gold) == "Legendary" && CardProgression.RarityName(CardRarity.Mythic) == "Mythic", "gold is called Legendary");

            int tokens = 0, coins = 0;
            for (int level = 1; level < 30; level++)
            {
                Check(CardProgression.TokensForLevel(level) == ExpectedTokens[level - 1], "token cost row " + level);
                tokens += CardProgression.TokensForLevel(level);
                coins += CardProgression.CoinsForLevel(level);
                if (level == 4) Check(tokens == 23 && coins == 255, "level 1 to 5: 23 tokens, 255 coins");
            }
            Check(tokens == 2579 && coins == 28355, "level 1 to 30: 2579 tokens, 28355 coins");

            Check(Near(CardProgression.LevelMult(1), 1f) && Near(CardProgression.LevelMult(30), 1.348f), "level multiplier 1 + 0.012 per level");
            Check(Near(CardProgression.WorkMult(CardRarity.White, 1, 0), 1f), "fresh White works at 1.0");
            Check(Near(CardProgression.WorkMult(CardRarity.Gold, 30, 0), 1.36f * 1.348f), "Gold 30");
            Check(Near(CardProgression.WorkMult(CardRarity.Mythic, 30, 5), 1.5f * 1.348f * 1.15f), "Mythic 30 five stars");
            Check(CardProgression.WorkMult(CardRarity.Mythic, 30, 5) < 2.4f, "top crew stays under 2.4x a fresh White (before tools)");

            Check(CardProgression.BlueprintsForStar(0) == 2 && CardProgression.BlueprintsForStar(4) == 6 && CardProgression.BlueprintsForStar(5) == 0, "stars cost 2..6");
            Check(CardProgression.BlueprintsToTop(CardRarity.White, 0) == 31, "White to Mythic five stars: 11 + 20 blueprints");
            Check(CardProgression.BlueprintsToTop(CardRarity.Mythic, 5) == 0, "nothing left at the top");

            Check(Near(CardProgression.ToolBonus(CardRarity.White), .03f) && Near(CardProgression.ToolBonus(CardRarity.Mythic), .17f), "tool bonus 3..17%");

            Check(CardProgression.HaulTokens(5, 6, 1f) == 34, "tier 5, six crew, full hold: 34 tokens");
            Check(CardProgression.HaulTokens(5, 6, .5f) == 15, "a half hold pays half (no full bonus)");
            Check(CardProgression.HaulTokens(5, 8, 1f) == 46, "eight crew at tier 5: 40 + 15%");
            Check(CardProgression.HaulTokens(1, 2, 1f) == 2, "skiff, two crew, full: 2");
            Check(CardProgression.HaulTokens(0, 0, 1f) == 0 && CardProgression.HaulTokens(3, 4, 0f) == 0, "no crew or no fish: nothing");
            Check(CardProgression.HaulTokens(2, 3, 1.4f) == CardProgression.HaulTokens(2, 3, 1f), "fill is capped at a full hold");
        }

        static void Wages()
        {
            Check(CardProgression.Wage(1, CardRarity.White, 1) == 8, "White tier-1 wage 8");
            Check(CardProgression.Wage(1, CardRarity.Gold, 1) == 17, "Gold tier-1 wage 17");
            Check(CardProgression.Wage(5, CardRarity.Mythic, 30) == 387, "Mythic tier-5 level-30 wage 387");
            Check(new CardState("noor").Wage() == 8 && new CardState("mira").Wage() == 17, "CardState wage uses tier and start rarity");
        }

        static void CardTable()
        {
            string[] names = { "Mira", "Noor", "Dirk", "Tess", "Sam", "Kofi", "Rosa", "Ana", "Mats", "Lise", "Ines", "Olaf", "Pim", "Tove" };
            int[] tiers = { 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5 };
            Check(Cards.All.Length == names.Length, "14 crew cards");
            var ids = new HashSet<string>();
            var abilityIds = new HashSet<string>();
            for (int i = 0; i < names.Length; i++)
            {
                var def = Cards.All[i];
                Check(def.Name == names[i] && def.TierGranted == tiers[i], "card order and tier " + names[i]);
                Check(def.Id == names[i].ToLowerInvariant() && def.PortraitId == def.Id, "id and portrait id of " + names[i]);
                Check(ids.Add(def.Id) && Cards.ById(def.Id) == def, "unique id and lookup " + def.Id);
                var expectedStart = def.Id == "mira" ? CardRarity.Gold : (CardRarity)Math.Max(0, def.TierGranted - 1);
                Check(def.StartRarity == expectedStart, "start rarity follows the tier (Mira Gold) " + names[i]);
                Check(def.Passive.Unlock == CardRarity.Green && def.Auto.Unlock == CardRarity.Purple && def.Mythic.Unlock == CardRarity.Mythic, "unlock rarities " + names[i]);
                foreach (var a in def.Abilities)
                {
                    Check(!string.IsNullOrEmpty(a.Name) && !string.IsNullOrEmpty(a.Text) && a.Text.EndsWith("."), "ability text " + a.Id);
                    Check(abilityIds.Add(a.Id), "unique ability id " + a.Id);
                }
                Check((def.Trait != null) == (def.Id == "mira"), "only Mira has a trait");
            }
            Check(abilityIds.Count == 43, "42 abilities plus Mira's trait");
            var mira = Cards.ById("mira");
            Check(mira.Role == CardRole.Navigator && mira.Trait.Name == "First mate" && mira.Trait.Unlock == CardRarity.Gold, "Mira: navigator, First mate from the start");
            Check(Cards.ById("ines").Role == CardRole.Engineer && Cards.ById("olaf").Role == CardRole.Engineer, "Ines and Olaf are engineers");
            Check(Cards.ById("rosa").Speciality == Speciality.Nets && Cards.ById("tess").Speciality == Speciality.Rods, "Rosa nets, Tess rods");
            Check(Cards.All.Count(c => c.Role == CardRole.Navigator) == 1, "one navigator");
            Check(Cards.ForTier(1).Count == 2 && Cards.ForTier(2).Count == 3 && Cards.ForTier(3).Count == 3
                && Cards.ForTier(4).Count == 3 && Cards.ForTier(5).Count == 3, "cards per tier 2/3/3/3/3");
            Check(mira.TopAbility(CardRarity.Gold) == mira.Auto && mira.TopAbility(CardRarity.Mythic) == mira.Mythic, "top ability by rarity");
            Check(Cards.ById("noor").TopAbility(CardRarity.White) == null && Cards.ById("noor").AbilityText(CardRarity.Green).StartsWith("Quick sort"), "White has no ability yet, Green the passive");
        }

        static void SkillsAndStrike()
        {
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.White, Speciality.Rods) == 100, "fisher speciality 100");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.White, Speciality.Nets) == 45, "fisher White other gear 45");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Purple, Speciality.Nets) == 62, "fisher Purple other gear 62");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Mythic, Speciality.Jigs) == 80, "fisher Mythic other gear 80");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Gold, Speciality.Sort) == 0, "fisher cannot sort");
            Check(CardProgression.Skill(CardRole.Deckhand, Speciality.Sort, CardRarity.Blue, Speciality.Haul) == 55, "deckhand Blue other work 55");
            Check(CardProgression.Skill(CardRole.Deckhand, Speciality.Sort, CardRarity.Gold, Speciality.Rods) == 0, "deckhand cannot use gear");
            Check(CardProgression.Skill(CardRole.Navigator, Speciality.Navigation, CardRarity.Gold, Speciality.Haul) == 0, "navigator does no deck work");
            Check(CardProgression.Skill(CardRole.Engineer, Speciality.Power, CardRarity.Gold, Speciality.Haul) == 50, "engineer hauls at 50");
            Check(CardProgression.CaptainSkill(Speciality.Sort) == 100 && CardProgression.CaptainSkill(Speciality.Rods) == 100, "captain 100 at deck jobs");

            Check(Near(CardProgression.StrikeChance(CardRarity.White, 1), .78f, .0001f), "White strike 78%");
            Check(Near(CardProgression.StrikeChance(CardRarity.Gold, 1), .88f, .0001f), "Gold strike 88%");
            Check(Near(CardProgression.StrikeChance(CardRarity.Green, 5), .81f, .0001f), "strike +0.25 points per level");
            Check(Near(CardProgression.StrikeChance(CardRarity.Mythic, 30), .97f, .0001f), "strike caps at 97%");

            Check(Near(CardProgression.Duration(1f, 100, 1), 1f, .0001f) && Near(CardProgression.Duration(1f, 50, 1), 2f, .0001f), "duration by skill");
            Check(Near(CardProgression.Duration(1f, 100, 30), 1f / 1.348f, .0001f), "duration at level 30");
            Check(float.IsPositiveInfinity(CardProgression.Duration(1f, 0, 1)), "skill 0 cannot do the job");
        }

        static void RosterRules()
        {
            var cards = new List<CardState>();
            var deployment = new List<string>();
            Check(CardRoster.GrantTier(cards, deployment, 1) == 2, "tier 1 grants Mira and Noor");
            Check(CardRoster.Find(cards, "mira").Rarity == CardRarity.Gold && CardRoster.Find(cards, "noor").Rarity == CardRarity.White, "granted at start rarity");
            Check(cards.TrueForAll(c => c.Level == 1 && c.Blueprints == 0 && c.Stars == 0 && c.ToolUids.Length == 3), "granted cards start level 1, empty");
            Check(CardRoster.GrantTier(cards, deployment, 1) == 0, "tier grant is not repeated");
            Check(deployment.Count == 1 && deployment[0] == "mira", "Mira deployed on grant");
            Check(!CardRoster.TryUndeploy(deployment, "mira"), "navigator cannot be stood down");

            int berths = CardRoster.BerthsForTier(1);
            Check(berths == 2 && CardRoster.BerthsForTier(0) == 0 && CardRoster.BerthsForTier(5) == 6, "berths: navigator + tier hires");
            Check(CardRoster.TryDeploy(cards, deployment, "noor", berths) && CardRoster.TryDeploy(cards, deployment, "noor", berths) && deployment.Count == 2, "deploy Noor once");
            CardRoster.GrantUpToTier(cards, deployment, 2);
            Check(cards.Count == 5, "grant up to tier 2 gives five cards");
            Check(!CardRoster.TryDeploy(cards, deployment, "dirk", berths), "deploying beyond berths is refused");
            Check(!CardRoster.TryDeploy(cards, deployment, "olaf", 99), "cannot deploy a card that is not owned");

            var lise = new CardState("lise");
            Check(!CardRoster.Available(lise, 3) && CardRoster.Available(lise, 4), "a card sails from its own tier");
            lise.Rarity = CardRarity.Mythic; lise.Stars = 1;
            Check(CardRoster.Available(lise, 1) && !CardRoster.Available(lise, 0), "a starred card sails from tier 1");

            var run = new List<CardState>(); var runDeploy = new List<string>();
            CardRoster.GrantUpToTier(run, runDeploy, 2);
            CardRoster.TryDeploy(run, runDeploy, "noor", 3);
            Check(CardRoster.TotalWages(run, runDeploy) == 17 + 8, "wages for Mira (Gold) and Noor (White)");
        }

        static void LevelsAndRanks()
        {
            var noor = new CardState("noor");
            int tokens = 22, coins = 10000;
            for (int i = 0; i < 4; i++) CardRoster.TryLevelUp(noor, ref tokens, ref coins);
            Check(noor.Level == 4 && tokens == 22 - 13, "tokens run out before level 5");
            tokens = 30; coins = 119;
            Check(!CardRoster.TryLevelUp(noor, ref tokens, ref coins) && tokens == 30 && noor.Level == 4, "coins can block, nothing spent");
            tokens = 10; coins = 120;
            Check(CardRoster.TryLevelUp(noor, ref tokens, ref coins) && noor.Level == 5 && tokens == 0 && coins == 0, "level 4 to 5 costs 10 tokens and 120 coins");
            tokens = 999; coins = 99999;
            Check(!CardRoster.TryLevelUp(noor, ref tokens, ref coins) && noor.AtCap, "White stops at level 5");
            Check(!CardRoster.TryRankUp(noor), "rank up needs a blueprint");
            noor.Blueprints = 2;
            Check(CardRoster.TryRankUp(noor) && noor.Rarity == CardRarity.Green && noor.Level == 5 && noor.Blueprints == 1, "rank up keeps the level, spends one blueprint");
            Check(noor.LevelCap == 10 && !noor.AtCap && !CardRoster.TryRankUp(noor), "Green needs level 10 before the next rank");
            Check(noor.Has(Cards.ById("noor").Passive) && !noor.Has(Cards.ById("noor").Auto), "Green unlocks the passive only");

            var tove = new CardState("tove") { Rarity = CardRarity.Mythic, Level = 30, Blueprints = 2 };
            Check(tove.BlueprintsNeeded == 2 && CardRoster.TryRankUp(tove) && tove.Stars == 1 && tove.Rarity == CardRarity.Mythic, "Mythic blueprints buy stars");
            tove.Stars = 5; tove.Blueprints = 10;
            Check(tove.Maxed && !CardRoster.TryRankUp(tove) && tove.BlueprintsNeeded == 0, "five stars is the top");
            Check(!Chests.WantsBlueprints(tove) && Chests.WantsBlueprints(noor), "a maxed card takes no blueprints");
            Check(tove.Renown == 30 + 5 * 1 + 10 * 5, "renown: level + 5 per rank gained + 10 per star");

            var odd = new CardState("dirk") { Level = 40, Stars = 3, Blueprints = -2, ToolUids = new int[1] };
            odd.Normalise();
            Check(odd.Level == 10 && odd.Stars == 0 && odd.Blueprints == 0 && odd.ToolUids.Length == 3, "normalise clamps a bad card");
        }

        static void ToolRules()
        {
            Check(ToolInfo.All.Length == 14, "14 tools");
            Check(ToolInfo.All.Count(k => ToolInfo.Class(k) == CardRole.Fisher) == 4 && ToolInfo.All.Count(k => ToolInfo.Class(k) == CardRole.Deckhand) == 4
                && ToolInfo.All.Count(k => ToolInfo.Class(k) == CardRole.Engineer) == 3 && ToolInfo.All.Count(k => ToolInfo.Class(k) == CardRole.Navigator) == 3, "tools per class 4/4/3/3");
            Check(ToolInfo.Icon(ToolKind.NetNeedle) == "v2-tool-net-needle" && ToolInfo.Icon(ToolKind.Rod) == "v2-tool-rod", "tool icon ids");
            Check(ToolInfo.CanUse(null, ToolKind.Rod) && ToolInfo.CanUse(null, ToolKind.Gloves) && ToolInfo.CanUse(null, ToolKind.OilCan) && !ToolInfo.CanUse(null, ToolKind.Compass), "captain uses every class but navigator");
            Check(ToolInfo.CanUse(CardRole.Navigator, ToolKind.Compass) && !ToolInfo.CanUse(CardRole.Fisher, ToolKind.Gloves), "crew use their own class");

            var a = new ToolState { Uid = 1, Kind = ToolKind.Rod, Rarity = CardRarity.White };
            var b = new ToolState { Uid = 2, Kind = ToolKind.Rod, Rarity = CardRarity.White };
            var c = new ToolState { Uid = 3, Kind = ToolKind.Reel, Rarity = CardRarity.White };
            Check(ToolInfo.CanMerge(a, b) && !ToolInfo.CanMerge(a, a) && !ToolInfo.CanMerge(a, c), "merge needs two of one kind and rarity");
            Check(!ToolInfo.CanMerge(new ToolState { Uid = 4, Rarity = CardRarity.Mythic }, new ToolState { Uid = 5, Rarity = CardRarity.Mythic }), "Mythic tools do not merge");
            var gold = new ToolState { Uid = 6, Kind = ToolKind.Rod, Rarity = CardRarity.Gold };
            Check(Near(ToolInfo.Bonus(new[] { gold, a, c }, ToolKind.Rod), .16f), "bonuses of one kind add up");
            var mythics = Enumerable.Range(0, 3).Select(i => new ToolState { Uid = 10 + i, Kind = ToolKind.Gloves, Rarity = CardRarity.Mythic });
            Check(Near(ToolInfo.Bonus(mythics, ToolKind.Gloves), .5f), "bonus capped at +50%");
        }

        static void ChestRules()
        {
            var crate = Chests.Def(ChestKind.Crate); var sea = Chests.Def(ChestKind.SeaChest); var captain = Chests.Def(ChestKind.CaptainsChest);
            Check(crate.TokensFor(0) == 8 && crate.TokensFor(3) == 24 && sea.TokensFor(5) == 150 && captain.TokensFor(1) == 80, "chest tokens by tier");
            Check(!crate.ForSale && sea.ForSale && !captain.ForSale && sea.Price(1) == 700 && sea.Price(5) == 1900, "only the sea chest sells for coins");
            Check(Chests.ToolOdds.Sum() == 100, "tool odds add to 100");

            var rng = new System.Random(7);
            var roster = new List<CardState>(); var deploy = new List<string>();
            CardRoster.GrantUpToTier(roster, deploy, 3);
            int pity = 0, uid = 1, blueprints = 0, focus = 0, longest = 0, since = 0;
            var rarities = new int[6];
            for (int i = 0; i < 20000; i++)
            {
                var r = Chests.Open(ChestKind.Crate, 3, rng, roster, "kofi", ref pity, ref uid);
                Check(r.Tokens == 24 && r.Tools.Count == 1, "crate contents");
                rarities[(int)r.Tools[0].Rarity]++;
                since++;
                if (r.Blueprints.Count + r.FreeBlueprints > 0)
                {
                    blueprints++; longest = Math.Max(longest, since); since = 0;
                    if (r.Blueprints.Contains("kofi")) focus++;
                }
            }
            Check(uid == 20001, "every tool gets a fresh uid");
            Check(longest <= Chests.PityChests, "pity: a blueprint within 40 chests (longest gap " + longest + ")");
            float rate = blueprints / 20000f, focusShare = focus / (float)blueprints;
            Check(rate > .037f && rate < .049f, "crate blueprint rate with pity (3%, 40-chest pity: 4.26% expected) " + rate);
            Check(focusShare > .72f && focusShare < .84f, "focus crew gets about 75% plus a share of the rest " + focusShare);
            Check(rarities[0] > 11400 && rarities[0] < 12600 && rarities[4] > 100 && rarities[4] < 300 && rarities[5] == 0, "tool rarity odds 60/25/10/4/1, no Mythic drops");

            for (int i = 0; i < 300; i++)
            {
                var s = Chests.Open(ChestKind.SeaChest, 2, rng, roster, "", ref pity, ref uid);
                Check(s.Tools.Count == 2 && s.Tools[0].Rarity >= CardRarity.Green, "sea chest: two tools, one Green+");
                var cc = Chests.Open(ChestKind.CaptainsChest, 2, rng, roster, "", ref pity, ref uid);
                Check(cc.Tools.Count == 3 && cc.Tools[0].Rarity >= CardRarity.Purple, "captain's chest: three tools, one Purple+");
            }

            var maxed = new List<CardState> { new CardState("tove") { Rarity = CardRarity.Mythic, Stars = 5 } };
            int p = Chests.PityChests - 1;
            var free = Chests.Open(ChestKind.Crate, 1, new System.Random(1), maxed, "tove", ref p, ref uid);
            Check(free.PityBlueprint && free.Blueprints.Count == 0 && free.FreeBlueprints == 1 && p == 0, "a blueprint for a maxed card becomes a free blueprint");
        }

        static void RenownRules()
        {
            int[] expected = { 5, 10, 20, 30, 45, 60, 80, 100, 125, 150, 180, 210 };
            for (int n = 1; n <= expected.Length; n++) Check(RenownRoad.Threshold(n) == expected[n - 1], "renown milestone " + n);
            Check(RenownRoad.Reward(1).Kind == RenownRewardKind.BlueprintChoice && RenownRoad.Reward(5).Kind == RenownRewardKind.BlueprintChoice
                && RenownRoad.Reward(15).Kind == RenownRewardKind.BlueprintChoice, "milestone 1 and every 5th: blueprint of choice");
            Check(RenownRoad.Reward(10).Chest == ChestKind.CaptainsChest && RenownRoad.Reward(20).Chest == ChestKind.CaptainsChest, "every 10th: Captain's chest");
            var r2 = RenownRoad.Reward(2); var r3 = RenownRoad.Reward(3); var r4 = RenownRoad.Reward(4); var r6 = RenownRoad.Reward(6);
            Check(r2.Kind == RenownRewardKind.Tokens && r2.Tokens == 30 && r3.Chest == ChestKind.Crate && r4.Chest == ChestKind.SeaChest
                && r6.Kind == RenownRewardKind.Tokens && r6.Tokens == 50, "the rest rotate tokens, crate, sea chest");
        }

        static void SaveV3()
        {
            var save = new SaveV2 { Coins = 321, Hull = 3, Tokens = 55, FocusCard = "noor", ChestPity = 12, FreeBlueprints = 1, RenownClaimed = 2, LastCrateDay = "2026-10-25" };
            Check(save.Version == 3 && SaveV2.CurrentVersion == 3, "version 3");
            CardRoster.GrantTier(save.Cards, save.Deployment, 1);
            save.Cards[1].Level = 4; save.Cards[1].Blueprints = 1; save.Cards[1].ToolUids[0] = 9;
            save.Tools.Add(new ToolState { Uid = 9, Kind = ToolKind.Gloves, Rarity = CardRarity.Blue });
            save.CaptainTools[2] = 9; save.PendingChests.Add((int)ChestKind.SeaChest);
            var back = SaveV2.FromJson(save.ToJson());
            Check(back != null && back.Coins == 321 && back.Tokens == 55 && back.FocusCard == "noor" && back.ChestPity == 12
                && back.FreeBlueprints == 1 && back.RenownClaimed == 2 && back.LastCrateDay == "2026-10-25", "json round trip keeps card economy");
            Check(back.Cards.Count == 2 && back.Cards[0].Rarity == CardRarity.Gold && back.Cards[1].Level == 4 && back.Cards[1].Blueprints == 1
                && back.Cards[1].ToolUids[0] == 9, "json round trip keeps cards");
            Check(back.Tools.Count == 1 && back.Tools[0].Kind == ToolKind.Gloves && back.Tools[0].Rarity == CardRarity.Blue
                && back.CaptainTools[2] == 9 && back.PendingChests.SequenceEqual(new[] { (int)ChestKind.SeaChest }), "json round trip keeps tools and chests");
            string old = save.ToJson().Replace("\"Version\":3", "\"Version\":2");
            Check(SaveV2.FromJson(old) == null, "a version-2 save is discarded");
            Check(SaveV2.FromJson("") == null && SaveV2.FromJson("not json") == null, "empty or broken json gives null");
        }
    }
}

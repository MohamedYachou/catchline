using System;
using System.Collections.Generic;
using Catchline.Game;
using UnityEngine;

namespace Catchline.EditorTools
{
    // M2 data layer: card table, progression maths, roster rules and the SaveV2 v1 import.
    public static class M2DataChecks
    {
        static void Check(bool ok, string message)
        {
            if (!ok) throw new Exception("[Catchline] M2 data check failed: " + message);
        }

        // CARDS-AND-SPEEDS section 2.2, every row (level 1..30).
        static readonly float[] ExpectedMult =
        {
            1.000f, 1.015f, 1.030f, 1.045f, 1.060f, 1.075f, 1.090f, 1.105f, 1.120f, 1.135f,
            1.150f, 1.165f, 1.180f, 1.195f, 1.210f, 1.225f, 1.240f, 1.255f, 1.270f, 1.285f,
            1.300f, 1.315f, 1.330f, 1.345f, 1.360f, 1.375f, 1.390f, 1.405f, 1.420f, 1.435f,
        };
        static readonly int[] ExpectedXp =
        {
            0, 40, 113, 208, 320, 447, 588, 741, 905, 1080,
            1265, 1459, 1663, 1875, 2095, 2324, 2560, 2804, 3055, 3313,
            3578, 3849, 4127, 4412, 4703, 5000, 5303, 5612, 5927, 6247,
        };

        public static void Run()
        {
            LevelTable();
            Wages();
            CardTable();
            SkillsAndStrike();
            RosterRules();
            Upgrades();
            SaveImport();
            Debug.Log("[Catchline] M2 DATA CHECKS PASSED");
        }

        static void LevelTable()
        {
            for (int level = 1; level <= 30; level++)
            {
                Check(CardProgression.XpForLevel(level) == ExpectedXp[level - 1], "xp table row " + level);
                Check(Mathf.Abs(CardProgression.LevelMult(level) - ExpectedMult[level - 1]) < 0.0005f, "level multiplier row " + level);
                Check(CardProgression.LevelForXp(ExpectedXp[level - 1]) == level, "level from exact xp row " + level);
                if (level > 1) Check(CardProgression.LevelForXp(ExpectedXp[level - 1] - 0.5f) == level - 1, "level just below threshold row " + level);
                // The raw formula agrees with the printed table to within 1 kg (the doc rounds L23 and L29 differently).
                Check(Mathf.Abs(CardProgression.XpFormula(level) - ExpectedXp[level - 1]) <= 1, "xp formula row " + level);
            }
            Check(CardProgression.LevelForXp(1000000f) == 30, "level caps at 30");
            Check(CardProgression.LevelForXp(0f) == 1, "level 1 at zero xp");
        }

        static void Wages()
        {
            Check(CardProgression.Wage(1, CardRarity.Blue, 1) == 8, "Noor wage 8");
            Check(CardProgression.Wage(2, CardRarity.Purple, 10) == 26, "Dirk wage 26");
            Check(CardProgression.Wage(5, CardRarity.Gold, 30) == 387, "Olaf wage 387");
            var noor = new CardState("noor");
            Check(noor.Wage() == 8, "CardState wage uses the card's tier");
        }

        static void CardTable()
        {
            Check(Cards.All.Length == 11, "11 cards");
            string[] names = { "Mira", "Noor", "Dirk", "Sam", "Kofi", "Ana", "Mats", "Lise", "Olaf", "Pim", "Tove" };
            var ids = new HashSet<string>();
            for (int i = 0; i < names.Length; i++)
            {
                var def = Cards.All[i];
                Check(def.Name == names[i], "card order " + names[i]);
                Check(def.Id == names[i].ToLowerInvariant() && def.PortraitId == def.Id, "id and portrait id of " + names[i]);
                Check(ids.Add(def.Id), "unique id " + def.Id);
                Check(Cards.ById(def.Id) == def, "lookup " + def.Id);
                Check(!string.IsNullOrEmpty(def.BlueId) && !string.IsNullOrEmpty(def.PurpleId) && !string.IsNullOrEmpty(def.GoldId), "ability ids of " + names[i]);
                Check(!string.IsNullOrEmpty(def.BlueText) && !string.IsNullOrEmpty(def.PurpleText) && !string.IsNullOrEmpty(def.GoldText), "ability text of " + names[i]);
            }
            var lise = Cards.ById("lise");
            Check(lise.Role == CardRole.Fisher && lise.Speciality == Speciality.Jigs && lise.TierGranted == 4, "Lise is a tier-4 Fisher, Jigs");
            Check(lise.BlueText.Contains("Lamp eye") && lise.BlueText.Contains("10%"), "Lise blue: Lamp eye +10% jig cycle");
            Check(lise.PurpleText.Contains("Shares the light"), "Lise purple: Shares the light");
            Check(lise.GoldText.Contains("Ink run") && lise.GoldText.Contains("two squid"), "Lise gold: Ink run, two squid");
            Check(Cards.ById("mira").Role == CardRole.Navigator, "Mira is the navigator");
            Check(Cards.ById("olaf").Role == CardRole.Engineer, "Olaf is the engineer");
            Check(Cards.ForTier(1).Count == 2 && Cards.ForTier(2).Count == 2 && Cards.ForTier(3).Count == 2
                && Cards.ForTier(4).Count == 2 && Cards.ForTier(5).Count == 3, "cards per tier 2/2/2/2/3");
        }

        static void SkillsAndStrike()
        {
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Blue, Speciality.Rods) == 100, "fisher speciality 100");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Blue, Speciality.Nets) == 50, "fisher blue other gear 50");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Purple, Speciality.Nets) == 65, "fisher purple other gear 65");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Gold, Speciality.Jigs) == 80, "fisher gold other gear 80");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Gold, Speciality.Sort) == 0, "fisher cannot sort");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Gold, Speciality.Haul) == 0, "fisher cannot haul");
            Check(CardProgression.Skill(CardRole.Fisher, Speciality.Rods, CardRarity.Gold, Speciality.Table) == 0, "fisher cannot table");
            Check(CardProgression.Skill(CardRole.Deckhand, Speciality.Sort, CardRarity.Blue, Speciality.Sort) == 100, "deckhand speciality 100");
            Check(CardProgression.Skill(CardRole.Deckhand, Speciality.Sort, CardRarity.Purple, Speciality.Haul) == 65, "deckhand purple other work 65");
            Check(CardProgression.Skill(CardRole.Deckhand, Speciality.Sort, CardRarity.Gold, Speciality.Table) == 80, "deckhand gold other work 80");
            Check(CardProgression.Skill(CardRole.Deckhand, Speciality.Sort, CardRarity.Gold, Speciality.Rods) == 0, "deckhand cannot use gear");
            Check(CardProgression.Skill(CardRole.Navigator, Speciality.Navigation, CardRarity.Blue, Speciality.Navigation) == 100, "navigator reads grounds");
            Check(CardProgression.Skill(CardRole.Navigator, Speciality.Navigation, CardRarity.Gold, Speciality.Haul) == 0, "navigator does no deck work");
            Check(CardProgression.Skill(CardRole.Engineer, Speciality.Power, CardRarity.Blue, Speciality.Power) == 100, "engineer power 100");
            Check(CardProgression.Skill(CardRole.Engineer, Speciality.Power, CardRarity.Gold, Speciality.Haul) == 50, "engineer hauls at 50");
            Check(CardProgression.Skill(CardRole.Engineer, Speciality.Power, CardRarity.Gold, Speciality.Sort) == 0, "engineer cannot sort");
            Check(CardProgression.Skill(CardRole.Engineer, Speciality.Power, CardRarity.Gold, Speciality.Rods) == 0, "engineer cannot use gear");
            Check(CardProgression.CaptainSkill(Speciality.Sort) == 100 && CardProgression.CaptainSkill(Speciality.Rods) == 100, "captain 100 at deck jobs");

            Check(Mathf.Abs(CardProgression.StrikeChance(CardRarity.Blue, 1) - 0.80f) < 0.0001f, "blue strike 80%");
            Check(Mathf.Abs(CardProgression.StrikeChance(CardRarity.Purple, 1) - 0.85f) < 0.0001f, "purple strike 85%");
            Check(Mathf.Abs(CardProgression.StrikeChance(CardRarity.Gold, 1) - 0.90f) < 0.0001f, "gold strike 90%");
            Check(Mathf.Abs(CardProgression.StrikeChance(CardRarity.Blue, 5) - 0.81f) < 0.0001f, "strike +0.25 points per level");
            Check(Mathf.Abs(CardProgression.StrikeChance(CardRarity.Gold, 30) - 0.97f) < 0.0001f, "strike caps at 97%");

            // Speed model: base 1.0 s at skill 100, level 1 is 1.0 s; skill 50 doubles it; levelMult shortens it.
            Check(Mathf.Abs(CardProgression.Duration(1f, 100, 1) - 1f) < 0.0001f, "duration at skill 100");
            Check(Mathf.Abs(CardProgression.Duration(1f, 50, 1) - 2f) < 0.0001f, "duration at skill 50");
            Check(Mathf.Abs(CardProgression.Duration(1f, 100, 30) - 1f / 1.435f) < 0.0001f, "duration at level 30");
            Check(float.IsPositiveInfinity(CardProgression.Duration(1f, 0, 1)), "skill 0 cannot do the job");
            Check(Mathf.Abs(CardProgression.WalkSpeed(100, 1) - 2.2f) < 0.0001f, "walk 2.2 m/s");
        }

        static void RosterRules()
        {
            var cards = new List<CardState>();
            var deployment = new List<string>();

            Check(CardRoster.GrantTier(cards, deployment, 1) == 2, "tier 1 grants Mira and Noor");
            Check(CardRoster.Owns(cards, "mira") && CardRoster.Owns(cards, "noor"), "tier-1 cards owned");
            for (int i = 0; i < cards.Count; i++)
                Check(cards[i].Rarity == CardRarity.Blue && cards[i].Level == 1 && cards[i].Xp == 0f, "granted card is blue level 1");
            Check(CardRoster.GrantTier(cards, deployment, 1) == 0, "tier grant is not repeated");
            Check(deployment.Count == 1 && deployment[0] == "mira", "navigator deployed on grant");

            Check(!CardRoster.TryUndeploy(deployment, "mira"), "navigator cannot be undeployed");
            Check(CardRoster.IsDeployed(deployment, "mira"), "navigator still deployed");

            int berths = CardRoster.BerthsForTier(1);
            Check(berths == 2, "tier 1 has two berths (navigator + one hire)");
            Check(CardRoster.TryDeploy(cards, deployment, "noor", berths), "deploy Noor within berths");
            Check(CardRoster.TryDeploy(cards, deployment, "noor", berths), "deploying a deployed card is a no-op");
            Check(deployment.Count == 2, "no duplicate deployment");

            CardRoster.GrantUpToTier(cards, deployment, 2);
            Check(cards.Count == 4, "grant up to tier 2 gives four cards");
            Check(!CardRoster.TryDeploy(cards, deployment, "dirk", berths), "deploying beyond berths is refused");
            Check(!CardRoster.IsDeployed(deployment, "dirk"), "refused card stays ashore");
            Check(!CardRoster.TryDeploy(cards, deployment, "olaf", 99), "cannot deploy a card that is not owned");
            Check(CardRoster.TryUndeploy(deployment, "noor"), "a hire can be stood down");
            Check(CardRoster.TryDeploy(cards, deployment, "dirk", berths), "freed berth can be used");

            // A full tier-5 roster: six deployed (navigator + five hires), a seventh is refused.
            var big = new List<CardState>();
            var bigDeploy = new List<string>();
            CardRoster.GrantUpToTier(big, bigDeploy, 5);
            Check(big.Count == 11, "all 11 cards by tier 5");
            int tier5 = CardRoster.BerthsForTier(5);
            Check(tier5 == 6, "tier 5 has six berths");
            string[] hires = { "noor", "dirk", "sam", "kofi", "ana", "mats" };
            int accepted = 0;
            for (int i = 0; i < hires.Length; i++)
                if (CardRoster.TryDeploy(big, bigDeploy, hires[i], tier5)) accepted++;
            Check(accepted == 5 && bigDeploy.Count == 6, "tier 5 takes five hires beside the navigator, the sixth is refused");

            // XP and wages follow the deployment.
            var run = new List<CardState>();
            var runDeploy = new List<string>();
            CardRoster.GrantUpToTier(run, runDeploy, 2);
            CardRoster.TryDeploy(run, runDeploy, "noor", 3);
            int wages = CardRoster.TotalWages(run, runDeploy);
            Check(wages == 8 + 8, "wages for Mira and Noor at blue level 1 are 16");
            CardRoster.AddKgToDeployed(run, runDeploy, 40f);
            Check(CardRoster.Find(run, "noor").Level == 2 && CardRoster.Find(run, "mira").Level == 2, "deployed cards gain level from kg");
            Check(CardRoster.Find(run, "dirk").Level == 1 && CardRoster.Find(run, "dirk").Xp == 0f, "cards ashore gain nothing");
        }

        static void Upgrades()
        {
            Check(CardProgression.UpgradeWildcards(CardRarity.Blue) == 10 && CardProgression.UpgradeWildcards(CardRarity.Purple) == 25, "wildcard costs 10/25");
            Check(CardProgression.UpgradeCoins(CardRarity.Blue, 2) == 600 && CardProgression.UpgradeCoins(CardRarity.Purple, 5) == 5000, "coin costs 300xT / 1000xT");

            var dirk = new CardState("dirk");
            var wildcards = new int[4];
            int coins = 10000;
            Check(!CardRoster.TryUpgradeRarity(dirk, ref coins, wildcards), "upgrade refused without wildcards");
            wildcards[(int)CardRole.Fisher] = 10;
            Check(CardRoster.TryUpgradeRarity(dirk, ref coins, wildcards), "Blue to Purple");
            Check(dirk.Rarity == CardRarity.Purple && coins == 10000 - 600 && wildcards[(int)CardRole.Fisher] == 0, "upgrade spends wildcards and coins");
            wildcards[(int)CardRole.Fisher] = 25;
            Check(CardRoster.TryUpgradeRarity(dirk, ref coins, wildcards), "Purple to Gold");
            Check(dirk.Rarity == CardRarity.Gold && coins == 10000 - 600 - 2000, "gold costs 1000 x T");
            Check(!CardRoster.TryUpgradeRarity(dirk, ref coins, wildcards), "gold cannot upgrade");
        }

        static void SaveImport()
        {
            var save = new SaveV2 { Coins = 321, Hull = 3 };
            save.Owned.Add((int)UpgradeId.BigCooler); save.Owned.Add((int)UpgradeId.RodCarbon);
            Check(save.Version == 2, "version 2");
            Check(save.Cards.Count == 0 && save.Deployment.Count == 0, "a new save has no cards");
            Check(save.Wildcards.Length == 4 && save.Wildcards[0] + save.Wildcards[1] + save.Wildcards[2] + save.Wildcards[3] == 0, "a new save has no wildcards");

            CardRoster.GrantTier(save.Cards, save.Deployment, 1);
            save.Wildcards[(int)CardRole.Deckhand] = 7;
            var back = SaveV2.FromJson(save.ToJson());
            Check(back != null && back.Coins == 321 && back.Hull == 3 && back.Owned.Count == 2, "json round trip keeps v1 values");
            Check(back.Cards.Count == 2 && back.Cards[0].Id == "mira" && back.Cards[1].Rarity == CardRarity.Blue && back.Cards[1].Level == 1, "json round trip keeps cards");
            Check(back.Deployment.Count == 1 && back.Wildcards[(int)CardRole.Deckhand] == 7, "json round trip keeps deployment and wildcards");
            Check(SaveV2.FromJson("") == null, "empty json gives null");
        }
    }
}

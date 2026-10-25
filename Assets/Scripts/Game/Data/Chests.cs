using System;
using System.Collections.Generic;

namespace Catchline.Game
{
    // Chests (spec section 5). Append only (pending chests are saved as ints).
    public enum ChestKind { Crate, SeaChest, CaptainsChest, Welcome, Crew }

    public sealed class ChestDef
    {
        public ChestKind Kind;
        public string Name;
        public int TokensPerTier, MinTokens, Tools;
        public CardRarity Guarantee;      // one tool of at least this rarity (White = no guarantee)
        public float BlueprintChance;
        public int Pity;                  // a blueprint is guaranteed by this many chests of this kind (0 = none)
        public int PriceBase = -1, PricePerTier; // PriceBase -1: not sold for coins
        public bool ForSale => PriceBase >= 0;
        public int Price(int tier) => PriceBase + PricePerTier * Math.Max(1, tier);
        public int TokensFor(int tier) => Math.Max(MinTokens, TokensPerTier * tier);
    }

    public sealed class ChestResult
    {
        public ChestKind Kind;
        public int Tokens;
        public readonly List<ToolState> Tools = new();
        public readonly List<string> Blueprints = new(); // card ids, one entry per blueprint
        public readonly List<string> Recruits = new();   // crew who joined from this chest (their blueprint recruited them)
        public string CrewId;                             // a crew chest: whose chest it is
        public int FreeBlueprints;                        // blueprints for a 5-star card: the player assigns them
        public bool PityBlueprint;                        // the chest kind's guarantee paid out
    }

    public static class Chests
    {
        public const float FocusShare = 0.75f;
        // Crew chests (Mo, 2026-10-25): each unlocked crew member has an offer of 10 chests centred on them; every one
        // may hold their blueprint and the 10th always does, whatever dropped before.
        public const int CrewChestOffer = 10;
        public const float CrewBlueprintChance = 0.15f;
        public const int WelcomeTokens = 20;

        public static readonly ChestDef[] All =
        {
            // Pity (Mo, 2026-10-25): 50 cheap crates, 30 sea chests, 10 captain's chests (the future gem chest).
            new ChestDef { Kind = ChestKind.Crate, Name = "Crate", TokensPerTier = 8, MinTokens = 8, Tools = 1, Guarantee = CardRarity.White, BlueprintChance = 0.03f, Pity = 50 },
            new ChestDef { Kind = ChestKind.SeaChest, Name = "Sea chest", TokensPerTier = 30, MinTokens = 30, Tools = 2, Guarantee = CardRarity.Green, BlueprintChance = 0.08f, Pity = 30, PriceBase = 400, PricePerTier = 300 },
            new ChestDef { Kind = ChestKind.CaptainsChest, Name = "Captain's chest", TokensPerTier = 80, MinTokens = 80, Tools = 3, Guarantee = CardRarity.Purple, BlueprintChance = 0.20f, Pity = 10 },
            // The tutorial's free chest: Mira, a few tokens and one tool.
            new ChestDef { Kind = ChestKind.Welcome, Name = "Welcome chest", TokensPerTier = 0, MinTokens = WelcomeTokens, Tools = 1, Guarantee = CardRarity.Green },
            // Priced by the crew member's tier: three sea chests' worth. Opened as soon as it is bought.
            new ChestDef { Kind = ChestKind.Crew, Name = "Crew chest", TokensPerTier = 30, MinTokens = 30, Tools = 2, Guarantee = CardRarity.Green, BlueprintChance = CrewBlueprintChance, PriceBase = 1200, PricePerTier = 900 },
        };

        public static ChestDef Def(ChestKind kind) => All[(int)kind];

        // Tool rarity odds per draw, White..Gold (Mythic tools only come from merging).
        public static readonly int[] ToolOdds = { 60, 25, 10, 4, 1 };

        public static CardRarity RollToolRarity(Random rng, CardRarity atLeast)
        {
            int total = 0, from = (int)atLeast;
            for (int i = from; i < ToolOdds.Length; i++) total += ToolOdds[i];
            if (total <= 0) return CardRarity.Gold;
            int roll = rng.Next(total);
            for (int i = from; i < ToolOdds.Length; i++)
            {
                if (roll < ToolOdds[i]) return (CardRarity)i;
                roll -= ToolOdds[i];
            }
            return CardRarity.Gold;
        }

        // A card can still use blueprints until it is Mythic with five stars.
        public static bool WantsBlueprints(CardState card) =>
            card != null && (card.Rarity < CardRarity.Mythic || card.Stars < CardProgression.MaxStars);

        // Who a dropped blueprint belongs to: the focus crew 75% of the time, otherwise anyone who can use one:
        // an owned crew member short of Mythic five stars, or a crew member the boat's tier has unlocked who has
        // not joined yet (their blueprint recruits them). Null means a free blueprint for the player to assign.
        public static string BlueprintTarget(Random rng, List<CardState> roster, string focus, int tier)
        {
            var focusCard = CardRoster.Find(roster, focus);
            if (focusCard != null && rng.NextDouble() < FocusShare) return WantsBlueprints(focusCard) ? focusCard.Id : null;
            var pool = new List<string>();
            if (roster != null)
                foreach (var c in roster) if (c?.Def != null && WantsBlueprints(c)) pool.Add(c.Id);
            foreach (var d in Cards.All) if (CardRoster.Recruitable(roster, d, tier)) pool.Add(d.Id);
            return pool.Count == 0 ? null : pool[rng.Next(pool.Count)];
        }

        static void RollTools(ChestDef def, Random rng, ChestResult result, ref int nextUid)
        {
            for (int i = 0; i < def.Tools; i++)
            {
                var floor = i == 0 ? def.Guarantee : CardRarity.White;
                result.Tools.Add(new ToolState { Uid = nextUid++, Kind = ToolInfo.All[rng.Next(ToolInfo.All.Length)], Rarity = RollToolRarity(rng, floor) });
            }
        }

        // Rolls one chest. `pity` counts this kind's chests since its last blueprint; `nextUid` hands out tool ids.
        public static ChestResult Open(ChestKind kind, int tier, Random rng, List<CardState> roster, string focus, ref int pity, ref int nextUid)
        {
            var def = Def(kind);
            var result = new ChestResult { Kind = kind, Tokens = def.TokensFor(tier) };
            RollTools(def, rng, result, ref nextUid);
            if (kind == ChestKind.Welcome)
            {
                var nav = Array.Find(Cards.All, d => d.Role == CardRole.Navigator);
                if (nav != null && !CardRoster.Owns(roster, nav.Id)) result.Recruits.Add(nav.Id);
                return result;
            }
            bool blueprint = def.BlueprintChance > 0f && rng.NextDouble() < def.BlueprintChance;
            if (!blueprint && def.Pity > 0 && pity + 1 >= def.Pity) { blueprint = true; result.PityBlueprint = true; }
            if (blueprint)
            {
                pity = 0;
                string target = BlueprintTarget(rng, roster, focus, tier);
                if (target == null) result.FreeBlueprints++;
                else result.Blueprints.Add(target);
            }
            else pity++;
            return result;
        }

        public static int CrewChestPrice(CardDef crew) => crew == null ? 0 : Def(ChestKind.Crew).Price(crew.TierGranted);

        // Rolls the `n`th (1-based) chest of `crewId`'s offer. The blueprint is always theirs: it recruits them when
        // they have not joined, and becomes a free blueprint once they are Mythic with five stars.
        public static ChestResult OpenCrew(string crewId, int n, Random rng, List<CardState> roster, ref int nextUid)
        {
            var def = Def(ChestKind.Crew);
            var crew = Cards.ById(crewId);
            var result = new ChestResult { Kind = ChestKind.Crew, CrewId = crewId, Tokens = def.TokensFor(crew?.TierGranted ?? 1) };
            RollTools(def, rng, result, ref nextUid);
            bool blueprint = rng.NextDouble() < def.BlueprintChance;
            if (!blueprint && n >= CrewChestOffer) { blueprint = true; result.PityBlueprint = true; }
            if (blueprint)
            {
                var card = CardRoster.Find(roster, crewId);
                if (card != null && !WantsBlueprints(card)) result.FreeBlueprints++;
                else result.Blueprints.Add(crewId);
            }
            return result;
        }
    }
}

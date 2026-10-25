using System;
using System.Collections.Generic;

namespace Catchline.Game
{
    // Chests (spec section 5). Append only (pending chests are saved as ints).
    public enum ChestKind { Crate, SeaChest, CaptainsChest }

    public sealed class ChestDef
    {
        public ChestKind Kind;
        public string Name;
        public int TokensPerTier, MinTokens, Tools;
        public CardRarity Guarantee;      // one tool of at least this rarity (White = no guarantee)
        public float BlueprintChance;
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
        public int FreeBlueprints;                        // blueprints for a 5-star card: the player assigns them
        public bool PityBlueprint;                        // the 40-chest guarantee paid out
    }

    public static class Chests
    {
        public const int PityChests = 40;
        public const float FocusShare = 0.75f;

        public static readonly ChestDef[] All =
        {
            new ChestDef { Kind = ChestKind.Crate, Name = "Crate", TokensPerTier = 8, MinTokens = 8, Tools = 1, Guarantee = CardRarity.White, BlueprintChance = 0.03f },
            new ChestDef { Kind = ChestKind.SeaChest, Name = "Sea chest", TokensPerTier = 30, MinTokens = 30, Tools = 2, Guarantee = CardRarity.Green, BlueprintChance = 0.08f, PriceBase = 400, PricePerTier = 300 },
            new ChestDef { Kind = ChestKind.CaptainsChest, Name = "Captain's chest", TokensPerTier = 80, MinTokens = 80, Tools = 3, Guarantee = CardRarity.Purple, BlueprintChance = 0.20f },
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

        // Who a dropped blueprint belongs to: the focus crew 75% of the time, otherwise a random owned crew
        // member who can still use one. Null means a free blueprint for the player to assign: the focus crew
        // is already Mythic with five stars, or nobody can use one.
        public static string BlueprintTarget(Random rng, List<CardState> roster, string focus)
        {
            var focusCard = CardRoster.Find(roster, focus);
            if (focusCard != null && rng.NextDouble() < FocusShare) return WantsBlueprints(focusCard) ? focusCard.Id : null;
            var pool = new List<string>();
            if (roster != null)
                foreach (var c in roster) if (c?.Def != null && WantsBlueprints(c)) pool.Add(c.Id);
            return pool.Count == 0 ? null : pool[rng.Next(pool.Count)];
        }

        // Rolls one chest. `pity` counts chests since the last blueprint; `nextUid` hands out tool ids.
        public static ChestResult Open(ChestKind kind, int tier, Random rng, List<CardState> roster, string focus, ref int pity, ref int nextUid)
        {
            var def = Def(kind);
            var result = new ChestResult { Kind = kind, Tokens = def.TokensFor(tier) };
            for (int i = 0; i < def.Tools; i++)
            {
                var floor = i == 0 ? def.Guarantee : CardRarity.White;
                var tool = new ToolState { Uid = nextUid++, Kind = ToolInfo.All[rng.Next(ToolInfo.All.Length)], Rarity = RollToolRarity(rng, floor) };
                result.Tools.Add(tool);
            }
            bool blueprint = rng.NextDouble() < def.BlueprintChance;
            if (!blueprint && pity + 1 >= PityChests) { blueprint = true; result.PityBlueprint = true; }
            if (blueprint)
            {
                pity = 0;
                string target = BlueprintTarget(rng, roster, focus);
                if (target == null) result.FreeBlueprints++;
                else result.Blueprints.Add(target);
            }
            else pity++;
            return result;
        }
    }
}

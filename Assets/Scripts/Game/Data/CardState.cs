using System;
using System.Collections.Generic;

namespace Catchline.Game
{
    // One owned crew card (crew cards v2, docs/plans/CREW-CARDS-V2.md section 10). JsonUtility friendly.
    // Cards are owned permanently; there is no hire fee or expiry.
    [Serializable]
    public class CardState
    {
        public string Id;
        public CardRarity Rarity;
        public int Level = 1;
        public int Blueprints;   // banked towards the next rank (or the next star once Mythic)
        public int Stars;        // 0..5, Mythic only
        public int[] ToolUids = new int[CardProgression.MaxToolSlots]; // ToolState.Uid per slot, 0 = empty

        public CardState() { }
        public CardState(string id)
        {
            Id = id;
            var def = Cards.ById(id);
            Rarity = def == null ? CardRarity.White : def.StartRarity;
        }

        public CardDef Def => Cards.ById(Id);
        public int LevelCap => CardProgression.LevelCap(Rarity);
        public bool AtCap => Level >= LevelCap;
        public bool IsMythic => Rarity >= CardRarity.Mythic;
        public bool Maxed => IsMythic && Stars >= CardProgression.MaxStars;

        // Blueprints the next step costs: a rank below Mythic, a star at Mythic, 0 once fully starred.
        public int BlueprintsNeeded => IsMythic ? CardProgression.BlueprintsForStar(Stars) : CardProgression.BlueprintsToRankUp(Rarity);
        // Ranking up needs the level cap; stars only need blueprints.
        public bool CanRankUp => !IsMythic && AtCap && Blueprints >= BlueprintsNeeded;
        public bool CanStar => IsMythic && !Maxed && Blueprints >= BlueprintsNeeded;

        public bool Has(AbilityDef ability) => CardProgression.HasAbility(Rarity, ability);

        // Renown this card adds to the road: its level, 5 per rank gained since it joined, 10 per star.
        public int Renown
        {
            get
            {
                var def = Def;
                int ranks = def == null ? 0 : Math.Max(0, (int)Rarity - (int)def.StartRarity);
                return Level + 5 * ranks + 10 * Stars;
            }
        }

        // Wage per voyage, paid at departure. 0 for an unknown card id.
        public int Wage()
        {
            var def = Def;
            return def == null ? 0 : CardProgression.Wage(def.TierGranted, Rarity, Level);
        }

        // Repairs values a hand-edited or partial save could carry.
        public void Normalise()
        {
            if (ToolUids == null || ToolUids.Length != CardProgression.MaxToolSlots)
            {
                var slots = new int[CardProgression.MaxToolSlots];
                if (ToolUids != null) Array.Copy(ToolUids, slots, Math.Min(ToolUids.Length, slots.Length));
                ToolUids = slots;
            }
            Level = Math.Min(CardProgression.ClampLevel(Level), LevelCap);
            Stars = IsMythic ? Math.Max(0, Math.Min(CardProgression.MaxStars, Stars)) : 0;
            Blueprints = Math.Max(0, Blueprints);
        }
    }

    // Roster and deployment rules over a card list plus a deployment list of card ids
    // (the two lists SaveV2 stores). Pure functions; no scene dependencies.
    public static class CardRoster
    {
        // BLUEPRINT section 5: tier N = N hires + navigator (+ the captain, who is not a card).
        // Berths here means the most cards that may be deployed, navigator included.
        // Tier 0 has no hires and no navigator.
        public static int BerthsForTier(int tier) => tier <= 0 ? 0 : tier + 1;

        public static CardState Find(List<CardState> cards, string id)
        {
            if (cards == null || string.IsNullOrEmpty(id)) return null;
            for (int i = 0; i < cards.Count; i++)
                if (cards[i] != null && cards[i].Id == id) return cards[i];
            return null;
        }

        public static bool Owns(List<CardState> cards, string id) => Find(cards, id) != null;

        public static bool IsDeployed(List<string> deployment, string id) => deployment != null && deployment.Contains(id);

        // A card sails from its own tier; a starred card sails from tier 1 (it carries through a prestige).
        public static bool Available(CardState card, int tier) =>
            card?.Def != null && tier >= 1 && (card.Def.TierGranted <= tier || card.Stars > 0);

        // Reaching tier N grants every tier-N card at its starting rarity, level 1 (owned cards are skipped).
        // Makes sure the navigator is deployed afterwards. Returns the number of cards granted.
        public static int GrantTier(List<CardState> cards, List<string> deployment, int tier)
        {
            int granted = 0;
            for (int i = 0; i < Cards.All.Length; i++)
            {
                var def = Cards.All[i];
                if (def.TierGranted != tier || Owns(cards, def.Id)) continue;
                cards.Add(new CardState(def.Id));
                granted++;
            }
            EnsureNavigator(cards, deployment);
            return granted;
        }

        // Grants every tier from 1 up to and including `tier`. Returns the number of cards granted.
        public static int GrantUpToTier(List<CardState> cards, List<string> deployment, int tier)
        {
            int granted = 0;
            for (int t = 1; t <= tier; t++) granted += GrantTier(cards, deployment, t);
            return granted;
        }

        // The navigator is fixed: if an owned navigator card is not deployed, deploy it (at the front).
        public static void EnsureNavigator(List<CardState> cards, List<string> deployment)
        {
            if (cards == null || deployment == null) return;
            for (int i = 0; i < deployment.Count; i++)
            {
                var d = Cards.ById(deployment[i]);
                if (d != null && d.Role == CardRole.Navigator) return;
            }
            for (int i = 0; i < cards.Count; i++)
            {
                var d = cards[i] == null ? null : cards[i].Def;
                if (d != null && d.Role == CardRole.Navigator)
                {
                    deployment.Insert(0, cards[i].Id);
                    return;
                }
            }
        }

        // Deploys an owned card. Refused when not owned, when the roster is already at `berths`
        // deployed cards, or when it is a second navigator. Deploying an already deployed card is a no-op (true).
        public static bool TryDeploy(List<CardState> cards, List<string> deployment, string id, int berths)
        {
            if (!Owns(cards, id) || deployment == null) return false;
            if (deployment.Contains(id)) return true;
            if (deployment.Count >= berths) return false;
            var def = Cards.ById(id);
            if (def == null) return false;
            if (def.Role == CardRole.Navigator)
            {
                for (int i = 0; i < deployment.Count; i++)
                {
                    var d = Cards.ById(deployment[i]);
                    if (d != null && d.Role == CardRole.Navigator) return false;
                }
            }
            deployment.Add(id);
            return true;
        }

        // Stands a card down. Refused for the navigator (always deployed) and for cards not deployed.
        public static bool TryUndeploy(List<string> deployment, string id)
        {
            if (deployment == null || !deployment.Contains(id)) return false;
            var def = Cards.ById(id);
            if (def != null && def.Role == CardRole.Navigator) return false;
            deployment.Remove(id);
            return true;
        }

        // Wages owed at departure for the deployed cards (the captain draws none).
        public static int TotalWages(List<CardState> cards, List<string> deployment)
        {
            int total = 0;
            if (deployment == null) return 0;
            for (int i = 0; i < deployment.Count; i++)
            {
                var card = Find(cards, deployment[i]);
                if (card != null) total += card.Wage();
            }
            return total;
        }

        // One level for tokens plus coins (spec section 2). Spends both only on success.
        public static bool TryLevelUp(CardState card, ref int tokens, ref int coins)
        {
            if (card?.Def == null || card.AtCap) return false;
            int needTokens = CardProgression.TokensForLevel(card.Level), needCoins = CardProgression.CoinsForLevel(card.Level);
            if (tokens < needTokens || coins < needCoins) return false;
            tokens -= needTokens;
            coins -= needCoins;
            card.Level++;
            return true;
        }

        // Rank up at the level cap (the level is kept), or add a star once Mythic. Spends banked blueprints.
        public static bool TryRankUp(CardState card)
        {
            if (card?.Def == null) return false;
            if (card.CanRankUp)
            {
                card.Blueprints -= card.BlueprintsNeeded;
                card.Rarity = (CardRarity)((int)card.Rarity + 1);
                return true;
            }
            if (card.CanStar)
            {
                card.Blueprints -= card.BlueprintsNeeded;
                card.Stars++;
                return true;
            }
            return false;
        }
    }
}

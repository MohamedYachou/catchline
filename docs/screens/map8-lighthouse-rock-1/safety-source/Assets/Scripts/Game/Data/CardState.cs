using System;
using System.Collections.Generic;

namespace Catchline.Game
{
    // One owned crew card (MASTER-PLAN B6: Cards[] {Id, Rarity, Level, Xp}). JsonUtility friendly.
    // Cards are owned permanently; there is no hire fee or expiry.
    [Serializable]
    public class CardState
    {
        public string Id;
        public CardRarity Rarity;
        public int Level = 1;
        public float Xp;    // cumulative kg landed while deployed

        public CardState() { }
        public CardState(string id) { Id = id; Rarity = CardRarity.Blue; Level = 1; Xp = 0f; }

        public CardDef Def => Cards.ById(Id);

        // Adds kg landed and recomputes the level. Returns how many levels were gained.
        public int AddKg(float kg)
        {
            if (kg <= 0f) return 0;
            int before = Level;
            Xp += kg;
            Level = CardProgression.LevelForXp(Xp);
            return Level - before;
        }

        // Wage per voyage, paid at departure. 0 for an unknown card id.
        public int Wage()
        {
            var def = Def;
            return def == null ? 0 : CardProgression.Wage(def.TierGranted, Rarity, Level);
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

        // Reaching tier N grants every tier-N card at blue level 1 (cards already owned are skipped).
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

        // XP at sale: every deployed card gains the same kg landed by the boat.
        public static void AddKgToDeployed(List<CardState> cards, List<string> deployment, float kg)
        {
            if (deployment == null) return;
            for (int i = 0; i < deployment.Count; i++)
            {
                var card = Find(cards, deployment[i]);
                if (card != null) card.AddKg(kg);
            }
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

        // Rarity upgrade: needs role wildcards (indexed by CardRole) plus coins scaled by the card's tier.
        // Spends both only on success.
        public static bool TryUpgradeRarity(CardState card, ref int coins, int[] wildcards)
        {
            if (card == null || wildcards == null) return false;
            var def = card.Def;
            if (def == null || !CardProgression.CanUpgrade(card.Rarity)) return false;
            int role = (int)def.Role;
            if (role < 0 || role >= wildcards.Length) return false;
            int needCards = CardProgression.UpgradeWildcards(card.Rarity);
            int needCoins = CardProgression.UpgradeCoins(card.Rarity, def.TierGranted);
            if (wildcards[role] < needCards || coins < needCoins) return false;
            wildcards[role] -= needCards;
            coins -= needCoins;
            card.Rarity = (CardRarity)((int)card.Rarity + 1);
            return true;
        }
    }
}

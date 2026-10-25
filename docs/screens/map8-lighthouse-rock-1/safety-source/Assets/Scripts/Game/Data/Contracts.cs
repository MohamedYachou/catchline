using System;
using System.Collections.Generic;
using Catchline.Game.Deck;

namespace Catchline.Game
{
    // MASTER-PLAN M5 / BLUEPRINT section 9. Pure data and logic, not wired yet.
    // Append only. Fillet-style contracts are deleted: no type asks for a processed common fish.
    public enum ContractType { Species, Class, Special, NightSpecies }

    // A contract on the board or in progress. One instance per contract; Progress is in fish (Species, Special,
    // NightSpecies) or kg (Class). Plain fields so a save can store it later.
    public sealed class ContractV2
    {
        public string Id;
        public ContractType Type;
        public BuyerId Giver;             // giver = buyer
        public Species? Species;          // Species, NightSpecies; optional filter for Special
        public FishClass? Class;          // Class
        public float Target;              // N fish, or kg for Class
        public float Progress;
        public int DeadlineVoyages;       // voyages allowed once accepted
        public int VoyagesLeft;           // counts down on accepted contracts
        public int RewardCoins, RewardRep;
        public bool RewardChest;
        public int Tier;                  // 0 = always available; N needs giver reputation tier N

        public bool Complete => Progress >= Target;

        // Does this delivery count toward the contract?
        public bool Accepts(Delivery d)
        {
            switch (Type)
            {
                case ContractType.Species: return !d.IsSpecialProduct && Species.HasValue && d.Species == Species.Value;
                case ContractType.Class: return !d.IsSpecialProduct && Class.HasValue && d.Class == Class.Value;
                case ContractType.Special: return d.IsSpecialProduct && (!Species.HasValue || d.Species == Species.Value);
                case ContractType.NightSpecies: return !d.IsSpecialProduct && d.Night && Species.HasValue && d.Species == Species.Value;
            }
            return false;
        }

        // Class contracts count kg; everything else counts one per delivered item.
        public float Amount(Delivery d) => Type == ContractType.Class ? d.Kg : 1f;
    }

    // One delivered fish or special product, as the sale or the hold reports it.
    public struct Delivery
    {
        public Species Species;
        public FishClass Class;
        public float Kg;
        public bool IsSpecialProduct;
        public bool Night;      // caught on a night voyage

        public static Delivery OfFish(Species species, FishClass cls, float kg, bool night = false) =>
            new Delivery { Species = species, Class = cls, Kg = kg, Night = night };
        public static Delivery OfSpecial(Species species, float kg) =>
            new Delivery { Species = species, Kg = kg, IsSpecialProduct = true };
    }

    public enum ContractResult { Completed, Failed }

    public struct ContractOutcome
    {
        public ContractV2 Contract;
        public ContractResult Result;
        public int Coins, Rep;      // Rep is signed: negative on failure
        public bool Chest;
    }

    public static class Contracts
    {
        public const int BoardSize = 3, MaxActive = 2;
        public const int FailureRep = -500;

        // Content table: rows only, no code branch needed to add one.
        // TODO(BLUEPRINT): the docs fix the contract types and the reward axes (coins + rep + chest) but give no
        // concrete contract rows, targets or payouts. Add rows here; the board and delivery logic need no change.
        public static readonly ContractV2[] Templates = new ContractV2[0];

        // A fresh copy of a template, ready for the board.
        public static ContractV2 Instantiate(ContractV2 t, string id) => new ContractV2
        {
            Id = id, Type = t.Type, Giver = t.Giver, Species = t.Species, Class = t.Class, Target = t.Target,
            DeadlineVoyages = t.DeadlineVoyages, VoyagesLeft = t.DeadlineVoyages, RewardCoins = t.RewardCoins,
            RewardRep = t.RewardRep, RewardChest = t.RewardChest, Tier = t.Tier
        };
    }

    // The board of three and the (at most two) accepted contracts.
    public sealed class ContractBoard
    {
        public readonly List<ContractV2> Offers = new List<ContractV2>();
        public readonly List<ContractV2> Active = new List<ContractV2>();

        public bool BoardFull => Offers.Count >= Contracts.BoardSize;
        public bool ActiveFull => Active.Count >= Contracts.MaxActive;

        // Puts a contract on the board. Refused when the board is full, or when the giver's reputation tier
        // is below the contract's tier (rep may be null to skip the tier check).
        public bool Offer(ContractV2 c, BuyerReputation rep = null)
        {
            if (c == null || BoardFull) return false;
            if (rep != null && rep.Tier(c.Giver) < c.Tier) return false;
            Offers.Add(c);
            return true;
        }

        // Fills empty board slots from a pool of templates the player may see, using the given seeded Random.
        public int Fill(IList<ContractV2> pool, BuyerReputation rep, Random rng, ref int nextId)
        {
            int added = 0;
            if (pool == null) return 0;
            var candidates = new List<ContractV2>();
            foreach (var t in pool) if (rep == null || rep.Tier(t.Giver) >= t.Tier) candidates.Add(t);
            while (!BoardFull && candidates.Count > 0)
            {
                var t = candidates[rng.Next(candidates.Count)];
                Offers.Add(Contracts.Instantiate(t, "c" + (nextId++)));
                added++;
            }
            return added;
        }

        // Max two active. The accepted contract leaves the board, which frees the slot for a new offer.
        public bool Accept(ContractV2 c)
        {
            if (c == null || ActiveFull || !Offers.Remove(c)) return false;
            c.VoyagesLeft = c.DeadlineVoyages;
            Active.Add(c);
            return true;
        }

        public bool Decline(ContractV2 c) => Offers.Remove(c);

        // A delivery counts toward the first active contract that accepts it (no double dipping).
        // Completed contracts pay out on the spot: rep goes to the giver, coins and the chest flag are returned.
        public List<ContractOutcome> Deliver(Delivery d, BuyerReputation rep)
        {
            var outcomes = new List<ContractOutcome>();
            for (int i = 0; i < Active.Count; i++)
            {
                var c = Active[i];
                if (!c.Accepts(d)) continue;
                c.Progress += c.Amount(d);
                if (c.Complete)
                {
                    Active.RemoveAt(i);
                    if (rep != null) rep.Adjust(c.Giver, c.RewardRep);
                    outcomes.Add(new ContractOutcome { Contract = c, Result = ContractResult.Completed, Coins = c.RewardCoins, Rep = c.RewardRep, Chest = c.RewardChest });
                }
                break;
            }
            return outcomes;
        }

        // Called once when a voyage ends. Each active contract loses a voyage; one that runs out unfinished
        // fails: -500 reputation with its giver, no reward.
        public List<ContractOutcome> EndVoyage(BuyerReputation rep)
        {
            var outcomes = new List<ContractOutcome>();
            for (int i = Active.Count - 1; i >= 0; i--)
            {
                var c = Active[i];
                c.VoyagesLeft--;
                if (c.VoyagesLeft > 0) continue;
                Active.RemoveAt(i);
                if (rep != null) rep.Adjust(c.Giver, Contracts.FailureRep);
                outcomes.Add(new ContractOutcome { Contract = c, Result = ContractResult.Failed, Rep = Contracts.FailureRep });
            }
            outcomes.Reverse();
            return outcomes;
        }
    }
}

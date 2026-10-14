using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    public class CaughtFish
    {
        public Species Species;
        public float Kg;
        public float StowedAt;
    }

    public class CrewMember
    {
        public string Name;
        public Grade Grade;
        public int VoyagesLeft;
        public Color Suit;
        public int Fee => GameData.Fee(Grade);
    }

    public class Contract
    {
        public Species Species;
        public int Count, Delivered, VoyagesLeft, Reward;
        public string Title => $"{Count} {GameData.Get(Species).Name.ToLower()}";
    }

    public class SaleReport
    {
        public int FishSold, Coins, ToContracts, ContractCoins;
        public float Minutes;
        public int Caught;
        public readonly List<string> Lines = new();
    }

    // Everything that survives between voyages: money, supplies, upgrades, crew, contracts,
    // spot stocks and market prices. No Unity objects in here.
    public class GameState
    {
        public int Coins = GameData.StartCoins;
        public int Bait = GameData.StartBait;
        public float FoodMinutes = 4f;
        public int Voyage = 1;
        public int BestVoyageFish;
        public readonly HashSet<UpgradeId> Owned = new();
        public readonly float[] Richness;
        public readonly float[] Market;
        public CrewMember Deckhand;
        public readonly List<CrewMember> Board = new();
        public readonly List<Contract> Offers = new();
        public readonly List<Contract> Active = new();
        public SaleReport LastSale;
        public readonly System.Random Rng;

        public GameState(int seed)
        {
            Rng = new System.Random(seed);
            Richness = new float[GameData.Spots.Length];
            Market = new float[GameData.Fish.Length];
            for (int i = 0; i < Richness.Length; i++) Richness[i] = 1f;
            for (int i = 0; i < Market.Length; i++) Market[i] = 1f;
            RollBoard();
            while (Offers.Count < 3) Offers.Add(NewContract());
        }

        public bool Has(UpgradeId id) => Owned.Contains(id);
        public int CoolerCapacity => Has(UpgradeId.BigCooler) ? 16 : 10;
        public float FoodCapacity => Has(UpgradeId.LunchTin) ? 12f : 6f;
        public int FoodFillCost => Mathf.CeilToInt(FoodCapacity - FoodMinutes) * GameData.FoodCostPerMinute;

        public float PricePerKg(Species s) => GameData.Get(s).PricePerKg * Market[(int)s];

        public float Freshness(CaughtFish f, float now)
        {
            if (Has(UpgradeId.IceBox)) return 1f;
            return Mathf.Max(GameData.MinFreshness, 1f - GameData.FreshnessLossPerMinute * (now - f.StowedAt) / 60f);
        }

        public int ValueOf(CaughtFish f, float now) => Mathf.Max(1, Mathf.RoundToInt(f.Kg * PricePerKg(f.Species) * Freshness(f, now)));

        float Rand() => (float)Rng.NextDouble();

        // ---- harbour actions ----------------------------------------------------------

        public bool TryBuy(UpgradeId id)
        {
            var u = GameData.Upgrade(id);
            if (Has(id) || Coins < u.Cost) return false;
            Coins -= u.Cost;
            Owned.Add(id);
            return true;
        }

        public bool BuyBait()
        {
            if (Coins < GameData.BaitPackCost) return false;
            Coins -= GameData.BaitPackCost;
            Bait += GameData.BaitPackSize;
            return true;
        }

        public bool FillFood()
        {
            int cost = FoodFillCost;
            if (cost <= 0 || Coins < cost) return false;
            Coins -= cost;
            FoodMinutes = FoodCapacity;
            return true;
        }

        public bool Hire(CrewMember c)
        {
            if (Deckhand != null || Coins < c.Fee) return false;
            Coins -= c.Fee;
            Board.Remove(c);
            Deckhand = c;
            return true;
        }

        public bool TakeContract(Contract c)
        {
            if (Active.Count >= GameData.MaxActiveContracts) return false;
            Offers.Remove(c);
            Active.Add(c);
            return true;
        }

        // ---- end of a voyage --------------------------------------------------------------

        public SaleReport Sell(List<CaughtFish> catchList, float now)
        {
            var r = new SaleReport { Caught = catchList.Count };
            foreach (var f in catchList)
            {
                var c = Active.Find(k => k.Species == f.Species && k.Delivered < k.Count);
                if (c != null)
                {
                    c.Delivered++;
                    r.ToContracts++;
                    continue;
                }
                int v = ValueOf(f, now);
                r.Coins += v;
                r.FishSold++;
                Coins += v;
                Market[(int)f.Species] = Mathf.Max(0.5f, Market[(int)f.Species] * GameData.MarketDropPerFish);
            }
            for (int i = Active.Count - 1; i >= 0; i--)
            {
                var c = Active[i];
                if (c.Delivered < c.Count) continue;
                Coins += c.Reward;
                r.ContractCoins += c.Reward;
                r.Lines.Add($"Contract done: {c.Title}  +{c.Reward}");
                Active.RemoveAt(i);
            }
            BestVoyageFish = Mathf.Max(BestVoyageFish, catchList.Count);
            LastSale = r;
            return r;
        }

        public void EndVoyage(SaleReport r)
        {
            Voyage++;
            for (int i = Active.Count - 1; i >= 0; i--)
            {
                if (--Active[i].VoyagesLeft > 0) continue;
                r.Lines.Add($"Contract missed: {Active[i].Title}");
                Active.RemoveAt(i);
            }
            if (Deckhand != null && --Deckhand.VoyagesLeft <= 0)
            {
                r.Lines.Add($"{Deckhand.Name}'s contract ended. Hire someone new on the crew board.");
                Deckhand = null;
            }
            for (int i = 0; i < Richness.Length; i++) Richness[i] = Mathf.Min(1f, Richness[i] + GameData.RichnessRecovery);
            for (int i = 0; i < Market.Length; i++) Market[i] += (1f - Market[i]) * GameData.MarketRecovery;
            RollBoard();
            if (Offers.Count > 0) Offers.RemoveAt(0);
            while (Offers.Count < 3) Offers.Add(NewContract());
        }

        // The board is never guaranteed: usually a hand, often someone experienced, rarely a veteran.
        void RollBoard()
        {
            Board.Clear();
            if (Rand() < 0.75f) Board.Add(NewCrew(Grade.Hand));
            if (Rand() < 0.4f) Board.Add(NewCrew(Grade.Experienced));
            if (Rand() < 0.06f) Board.Add(NewCrew(Grade.Veteran));
        }

        CrewMember NewCrew(Grade g)
        {
            string name;
            do name = GameData.Names[Rng.Next(GameData.Names.Length)];
            while (Board.Exists(b => b.Name == name) || Deckhand != null && Deckhand.Name == name);
            return new CrewMember
            {
                Name = name, Grade = g, VoyagesLeft = GameData.ContractVoyages(g),
                Suit = GameData.Suits[Rng.Next(GameData.Suits.Length)],
            };
        }

        Contract NewContract()
        {
            // Pick a species that lives in one of the spots, weighted by how common it is.
            var pool = new List<(Species, float)>();
            foreach (var spot in GameData.Spots)
                foreach (var e in spot.Table)
                    pool.Add(e);
            float total = 0f;
            foreach (var e in pool) total += e.Item2;
            float roll = Rand() * total;
            var species = pool[0].Item1;
            foreach (var e in pool)
            {
                roll -= e.Item2;
                if (roll <= 0f) { species = e.Item1; break; }
            }

            var def = GameData.Get(species);
            int count = species switch
            {
                Species.Herring or Species.Mackerel => 5 + Rng.Next(5),
                Species.Pollock => 3 + Rng.Next(3),
                Species.SeaBass => 2 + Rng.Next(2),
                _ => 1,
            };
            int reward = Mathf.Max(20, Mathf.RoundToInt(count * def.AvgValue * 1.8f / 5f) * 5);
            return new Contract { Species = species, Count = count, VoyagesLeft = 2 + Rng.Next(2), Reward = reward };
        }

        // ---- fishing rolls ----------------------------------------------------------------

        // Longer casts shift the odds toward heavier fish and bigger specimens.
        public (Species, float) RollFish(int spot, float power)
        {
            var table = GameData.Spots[spot].Table;
            float total = 0f;
            var weights = new float[table.Length];
            for (int i = 0; i < table.Length; i++)
            {
                float h = GameData.Get(table[i].species).Heaviness;
                weights[i] = table[i].weight * Mathf.Lerp(1f - 0.7f * h, 1f + 1.6f * h, power);
                total += weights[i];
            }
            float roll = Rand() * total;
            int pick = table.Length - 1;
            for (int i = 0; i < table.Length; i++)
            {
                roll -= weights[i];
                if (roll <= 0f) { pick = i; break; }
            }
            var def = GameData.Get(table[pick].species);
            float kg = Mathf.Lerp(def.MinKg, def.MaxKg, Mathf.Pow(Rand(), 1.5f - power));
            return (def.Species, kg);
        }

        public float RollBiteWait(int spot, float power)
            => (5f + Rand() * 4f + power * 5f) * GameData.Spots[spot].BiteWait / Mathf.Max(0.3f, Richness[spot]);

        public void OnCatch(int spot) => Richness[spot] = Mathf.Max(0.3f, Richness[spot] - GameData.RichnessPerCatch);
    }
}

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

    [System.Serializable]
    public class CrewMember
    {
        public string Name;
        public Grade Grade;
        public int VoyagesLeft;
        public Color Suit;
        public int Fee => GameData.Fee(Grade);
    }

    [System.Serializable]
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
        public int Squid;
        public bool UseSquid = true;
        public readonly HashSet<int> Charts = new();
        public float FoodMinutes = 4f;
        public int Voyage = 1;
        public int BestVoyageFish;
        public readonly HashSet<UpgradeId> Owned = new();
        public readonly float[] Richness;
        public readonly float[] Market;
        // Fish log: how many of each species you have landed, and the biggest one.
        public readonly int[] LogCount;
        public readonly float[] LogBest;
        public bool UnseenSale;
        public CrewMember Deckhand;
        public readonly List<CrewMember> Board = new();
        public readonly List<Contract> Offers = new();
        public readonly List<Contract> Active = new();
        public SaleReport LastSale;
        public System.Random Rng;

        public GameState(int seed)
        {
            Rng = new System.Random(seed);
            Richness = new float[GameData.Spots.Length];
            Market = new float[GameData.Fish.Length];
            LogCount = new int[GameData.Fish.Length];
            LogBest = new float[GameData.Fish.Length];
            for (int i = 0; i < Richness.Length; i++) Richness[i] = 1f;
            for (int i = 0; i < Market.Length; i++) Market[i] = 1f;
            RollBoard();
            while (Offers.Count < 3) Offers.Add(NewContract());
        }

        public bool Has(UpgradeId id) => Owned.Contains(id);
        public int CoolerCapacity => Has(UpgradeId.BigCooler) ? 16 : 10;
        public float FoodCapacity => Has(UpgradeId.LunchTin) ? 12f : 6f;
        public bool Known(int spot) => GameData.Spots[spot].ChartCost == 0 || Charts.Contains(spot);
        public float BiteWindow => Has(UpgradeId.RodCarbon) ? 1.4f : Has(UpgradeId.RodFibreglass) ? 1.15f : GameData.BiteWindow;
        public float ReelSpeed => Has(UpgradeId.RodCarbon) ? 1.5f : Has(UpgradeId.RodFibreglass) ? 1.25f : 1f;
        public float SelfHookChance => Has(UpgradeId.RodCarbon) ? 0.45f : GameData.SelfHookChance;
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
            if (Has(id) || Coins < u.Cost || u.Requires.HasValue && !Has(u.Requires.Value)) return false;
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

        public bool BuySquid()
        {
            if (Coins < GameData.SquidPackCost) return false;
            Coins -= GameData.SquidPackCost;
            Squid += GameData.SquidPackSize;
            return true;
        }

        public bool BuyChart(int spot)
        {
            int cost = GameData.Spots[spot].ChartCost;
            if (Known(spot) || Coins < cost) return false;
            Coins -= cost;
            Charts.Add(spot);
            return true;
        }

        public bool HasAnyBait => Bait > 0 || Squid > 0;

        // Takes one bait for a hook. Returns true when it was squid.
        public bool TakeBait(out bool squid)
        {
            squid = UseSquid && Squid > 0 || Bait <= 0 && Squid > 0;
            if (squid) { Squid--; return true; }
            if (Bait > 0) { Bait--; return true; }
            return false;
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
            foreach (var f in catchList)
            {
                int i = (int)f.Species;
                if (LogCount[i] == 0) r.Lines.Insert(0, $"New in your fish log: {GameData.Get(f.Species).Name}!");
                LogCount[i]++;
                LogBest[i] = Mathf.Max(LogBest[i], f.Kg);
            }
            UnseenSale = true;
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
            for (int i = 0; i < GameData.Spots.Length; i++)
                if (Known(i))
                    foreach (var e in GameData.Spots[i].Table)
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

        // ---- save / load ----------------------------------------------------------------
        // Saved in the harbour (after selling, after every purchase). A voyage in progress is not saved.

        [System.Serializable]
        class SaveData
        {
            public int Version = 1;
            public int Coins, Bait, Squid, Voyage, BestVoyageFish;
            public bool UseSquid;
            public float FoodMinutes;
            public List<int> Owned = new(), Charts = new();
            public float[] Richness, Market, LogBest;
            public int[] LogCount;
            public bool HasDeckhand;
            public CrewMember Deckhand;
            public List<CrewMember> Board = new();
            public List<Contract> Offers = new(), Active = new();
        }

        public static string SavePath => System.IO.Path.Combine(Application.persistentDataPath, "catchline-save.json");

        public void Save()
        {
            var d = new SaveData
            {
                Coins = Coins, Bait = Bait, Squid = Squid, Voyage = Voyage, BestVoyageFish = BestVoyageFish, UseSquid = UseSquid,
                FoodMinutes = FoodMinutes, Richness = Richness, Market = Market, LogCount = LogCount, LogBest = LogBest, HasDeckhand = Deckhand != null, Deckhand = Deckhand,
            };
            foreach (var u in Owned) d.Owned.Add((int)u);
            d.Charts.AddRange(Charts);
            d.Board.AddRange(Board);
            d.Offers.AddRange(Offers);
            d.Active.AddRange(Active);
            try { System.IO.File.WriteAllText(SavePath, JsonUtility.ToJson(d, true)); }
            catch (System.Exception e) { Debug.LogWarning("[Catchline] Save failed: " + e.Message); }
        }

        public static GameState Load()
        {
            try
            {
                if (!System.IO.File.Exists(SavePath)) return null;
                var d = JsonUtility.FromJson<SaveData>(System.IO.File.ReadAllText(SavePath));
                if (d == null || d.Version != 1) return null;
                var s = new GameState(System.Environment.TickCount);
                s.Coins = d.Coins; s.Bait = d.Bait; s.Squid = d.Squid; s.Voyage = d.Voyage; s.BestVoyageFish = d.BestVoyageFish;
                s.UseSquid = d.UseSquid; s.FoodMinutes = d.FoodMinutes;
                foreach (var u in d.Owned) s.Owned.Add((UpgradeId)u);
                foreach (var c in d.Charts) s.Charts.Add(c);
                // Arrays can grow between versions (new seas, new fish): copy what fits.
                if (d.Richness != null) System.Array.Copy(d.Richness, s.Richness, Mathf.Min(d.Richness.Length, s.Richness.Length));
                if (d.Market != null) System.Array.Copy(d.Market, s.Market, Mathf.Min(d.Market.Length, s.Market.Length));
                if (d.LogCount != null) System.Array.Copy(d.LogCount, s.LogCount, Mathf.Min(d.LogCount.Length, s.LogCount.Length));
                if (d.LogBest != null) System.Array.Copy(d.LogBest, s.LogBest, Mathf.Min(d.LogBest.Length, s.LogBest.Length));
                s.Deckhand = d.HasDeckhand ? d.Deckhand : null;
                s.Board.Clear(); s.Board.AddRange(d.Board);
                s.Offers.Clear(); s.Offers.AddRange(d.Offers);
                s.Active.Clear(); s.Active.AddRange(d.Active);
                return s;
            }
            catch (System.Exception e)
            {
                Debug.LogWarning("[Catchline] Could not load the save: " + e.Message);
                return null;
            }
        }

        public static void DeleteSave()
        {
            try { if (System.IO.File.Exists(SavePath)) System.IO.File.Delete(SavePath); } catch { }
        }
    }
}

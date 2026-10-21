using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    [System.Serializable]
    public class CaughtFish
    {
        public Species Species;
        public float Kg;
        public float StowedAt;
        public bool Prepared;
        public float PreparedQuality;
        public float PreparedBonus; // Missing in older saves means legacy1.25x.
    }

    [System.Serializable]
    public class CrewMember
    {
        public string Name;
        public Grade Grade;
        public CrewRole Role;
        public bool HasBaitPolicy;
        public BaitPermission AllowedBait;
        public BaitPermission BaitPolicy => HasBaitPolicy ? AllowedBait & BaitPermission.All : BaitPermission.All;
        public DeckhandWork WorkPreference; // Missing in older saves means Fish.
        public bool HasFisherWork;
        public FisherWork FisherPreference;
        // Old fishers already worked rods and opportunistic cages; preserve that default.
        public FisherWork FishingWork => HasFisherWork && System.Enum.IsDefined(typeof(FisherWork), FisherPreference)
            ? FisherPreference : FisherWork.CrabAndDeepFirst;
        public bool HasFisherTasks;
        public FisherTask AllowedTasks;
        public FisherTask FishingTasks => HasFisherTasks ? AllowedTasks & FisherTask.All
            : FishingWork == FisherWork.RodsOnly ? FisherTask.Rods
            : FishingWork == FisherWork.CrabsOnly ? FisherTask.Crabs
            : FishingWork == FisherWork.DeepLinesOnly ? FisherTask.DeepLines
            : FisherTask.Rods | FisherTask.Crabs | FisherTask.DeepLines;
        public bool Allows(FisherTask task) => (FishingTasks & task) != 0;
        public int VoyagesLeft;
        public Color Suit;
        public int Fee => GameData.Fee(Grade) * (Role == CrewRole.Fisherman ? 2 : 1);
        public string RoleName => Role == CrewRole.Engineer ? "Engineer" : Role == CrewRole.Fisherman ? "Fisherman" : "Deckhand";
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
    public partial class GameState
    {
        public int Coins = GameData.StartCoins;
        public int Bait = GameData.StartBait;
        public int Squid;
        [System.NonSerialized] public int Chum; // Voyage stock: never saved or bought.
        public PrepOrderSettings PrepOrders = new();
        public bool UseSquid = true;
        public readonly HashSet<int> Charts = new();
        // Legacy save/fixture field only. Early boats have no food mechanic.
        public float FoodMinutes = 4f;
        public int Voyage = 1;
        public int BestVoyageFish;
        public float BestVoyageKg;
        public int Hull;
        public float Fuel;
        // Includes the fitted net. Successful cycles reuse it; a tear removes one.
        public int NetInventory = 3;
        public HullDef HullDef => GameData.Hulls[Mathf.Clamp(Hull, 0, GameData.Hulls.Length - 1)];
        public bool CanRefit => Hull == 0 && BestVoyageFish >= GameData.SkiffFishGoal && Coins >= GameData.SkiffCost;
        public readonly HashSet<UpgradeId> Owned = new();
        public readonly float[] Richness;
        public readonly float[] Market;
        // Fish log: how many of each species you have landed, and the biggest one.
        public readonly int[] LogCount;
        public readonly float[] LogBest;
        public bool UnseenSale;
        public CrewMember Deckhand;
        public readonly List<CrewMember> ExtraCrew = new();
        public readonly List<CrewMember> InactiveEngineers = new();
        public IEnumerable<CrewMember> Crew
        {
            get { if (Deckhand != null) yield return Deckhand; foreach (var c in ExtraCrew) yield return c; }
        }
        public int CrewCount => ExtraCrew.Count + (Deckhand != null ? 1 : 0);
        public readonly List<CrewMember> Board = new();
        public readonly List<Contract> Offers = new();
        public readonly List<Contract> Active = new();
        public SaleReport LastSale;
        // Unsold fish are saved at port with StowedAt = negative age on arrival.
        // Harbour storage freezes freshness; it never silently sells or discards a haul.
        public readonly List<CaughtFish> UnsoldCatch = new();
        public float UnsoldMinutes;
        [System.Serializable]
        public class CoinCredit { public string Id; public int Amount; }
        public readonly List<CoinCredit> CoinCredits = new();
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
        public float CoolerCapacity => Hull == 0 ? (Has(UpgradeId.BigCooler) ? 35f : 20f) : HullDef.Capacity * (Has(UpgradeId.BigCooler) ? 1.5f : 1f);
        public float FuelCapacity => Has(UpgradeId.LunchTin) ? 20f : 10f;
        public float FuelFraction => Mathf.Clamp01(Fuel / FuelCapacity);
        public int FuelFillCost => Mathf.CeilToInt(Mathf.Max(0, FuelCapacity - Fuel) - .00001f);
        public float FoodCapacity => (Has(UpgradeId.LunchTin) ? 12f : 6f) * (Hull > 0 ? 4f : 1f);
        public bool Known(int spot) => GameData.Spots[spot].ChartCost == 0 || Charts.Contains(spot);
        public float BiteWindow => Has(UpgradeId.RodCarbon) ? 1.4f : Has(UpgradeId.RodFibreglass) ? 1.15f : GameData.BiteWindow;
        public float ReelSpeed => Has(UpgradeId.RodCarbon) ? 1.5f : Has(UpgradeId.RodFibreglass) ? 1.25f : 1f;
        public float SelfHookChance => Has(UpgradeId.RodCarbon) ? 0.45f : GameData.SelfHookChance;
        public int FoodFillCost => Mathf.CeilToInt(FoodCapacity - FoodMinutes) * GameData.FoodCostPerMinute;

        public float PricePerKg(Species s) => GameData.Get(s).PricePerKg * Market[(int)s];

        public float Freshness(CaughtFish f, float now)
        {
            if (f.Prepared) return f.PreparedQuality > 0 ? f.PreparedQuality : 1f;
            if (Has(UpgradeId.IceBox)) return 1f;
            return Mathf.Max(GameData.MinFreshness, 1f - GameData.FreshnessLossPerMinute * Mathf.Max(0f, now - f.StowedAt - GameData.FreshnessGraceSeconds) / 60f);
        }

        public float SpecimenPricePerKg(Species species, float kg)
        {
            var d = GameData.Get(species);
            float size = Mathf.InverseLerp(d.MinKg, d.MaxKg, kg);
            return PricePerKg(species) * (1f + .5f * size);
        }
        public int ValueOf(CaughtFish f, float now) => Mathf.Max(1, Mathf.RoundToInt(f.Kg * SpecimenPricePerKg(f.Species, f.Kg) * Freshness(f, now) * (f.Prepared ? f.PreparedBonus >= 1f ? f.PreparedBonus : 1.25f : 1f)));

        float Rand() => (float)Rng.NextDouble();

        // ---- harbour actions ----------------------------------------------------------

        public bool RefitSkiff()
        {
            if (!CanRefit) return false;
            Coins -= GameData.SkiffCost;
            Hull = 1;
            // The shipyard supplies the first tank, avoiding a stranded first refit.
            Fuel = FuelCapacity;
            RollBoard();
            return true;
        }

        public bool BuyFuel()
        {
            int cost = FuelFillCost;
            if (Hull == 0 || cost <= 0 || Coins < cost) return false;
            Coins -= cost;
            Fuel = FuelCapacity;
            return true;
        }

        public bool TryBuy(UpgradeId id)
        {
            var u = GameData.Upgrade(id);
            int cost = UpgradeCost(id);
            if (!UpgradeAvailable(id) || Has(id) || Coins < cost || u.Requires.HasValue && !Has(u.Requires.Value)) return false;
            Coins -= cost;
            Owned.Add(id);
            return true;
        }

        public bool BuyBait(bool bulk = false)
        {
            int cost = bulk ? GameData.BaitBulkCost : GameData.BaitPackCost;
            if (Coins < cost) return false;
            Coins -= cost;
            Bait += bulk ? GameData.BaitBulkSize : GameData.BaitPackSize;
            return true;
        }

        public bool BuyNet()
        {
            if (NetInventory < 0 || NetInventory >= GameData.NetInventoryCapacity || Coins < GameData.NetReplacementCost) return false;
            Coins -= GameData.NetReplacementCost;
            NetInventory++;
            return true;
        }

        public bool BuySquid(bool bulk = false)
        {
            int cost = bulk ? GameData.SquidBulkCost : GameData.SquidPackCost;
            if (Coins < cost) return false;
            Coins -= cost;
            Squid += bulk ? GameData.SquidBulkSize : GameData.SquidPackSize;
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

        public bool HasPaidBait => Chum > 0 || Bait > 0 || Squid > 0;
        public bool WillUseSquid => Chum <= 0 && Squid > 0 && (UseSquid || Bait <= 0);
        public bool HasAnyBait => true; // Unlimited harbour scraps prevent a bait soft lock.

        // Takes paid bait if available, otherwise free scraps. Always succeeds; out flag identifies squid.
        public bool TakeBait(out bool squid) => TakeBait(out squid, out _);
        public bool TakeBait(out bool squid, out bool chum)
        {
            return TakeBait(null, out squid, out chum, out _);
        }

        public bool FillFood() => false; // Retired; cannot charge for inactive food.

        public bool Hire(CrewMember c)
        {
            if (!Board.Contains(c) || CrewCount >= HullDef.CrewCap || Coins < c.Fee) return false;
            Coins -= c.Fee;
            Board.Remove(c);
            if (c.Role == CrewRole.Deckhand && Deckhand == null) Deckhand = c;
            else ExtraCrew.Add(c);
            EnsureCrewRoleOffers();
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

        public SaleReport QuoteSale(List<CaughtFish> catchList, float now)
        {
            var quote = new GameState(0) { Hull = Hull };
            System.Array.Copy(Market, quote.Market, Market.Length);
            quote.Owned.UnionWith(Owned);
            foreach (var c in Active)
                quote.Active.Add(new Contract { Species = c.Species, Count = c.Count,
                    Delivered = c.Delivered, VoyagesLeft = c.VoyagesLeft, Reward = c.Reward });
            return quote.Sell(catchList, now);
        }

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
                    // Contract progress is a bonus objective, never an unpaid fish sink.
                    // Pay normal market value below even when this contract is unfinished.
                }
                int v = ValueOf(f, now);
                r.Coins += v;
                r.FishSold++;
                Coins += v;
                Market[(int)f.Species] = Mathf.Max(0.5f, Market[(int)f.Species] * Mathf.Pow(GameData.MarketDropPerFish, f.Kg / (Hull >= 2 ? 5f : .5f)));
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
            for (int i = ExtraCrew.Count - 1; i >= 0; i--)
                if (--ExtraCrew[i].VoyagesLeft <= 0)
                {
                    r.Lines.Add($"{ExtraCrew[i].Name}'s {ExtraCrew[i].RoleName.ToLower()} contract ended.");
                    ExtraCrew.RemoveAt(i);
                }
            if (Deckhand == null)
            {
                int i = ExtraCrew.FindIndex(c => c.Role == CrewRole.Deckhand);
                if (i >= 0) { Deckhand = ExtraCrew[i]; ExtraCrew.RemoveAt(i); }
            }
            for (int i = 0; i < Richness.Length; i++) Richness[i] = Mathf.Min(1f, Richness[i] + GameData.RichnessRecovery);
            for (int i = 0; i < Market.Length; i++) Market[i] += (1f - Market[i]) * GameData.MarketRecovery;
            RollBoard();
            if (Offers.Count > 0) Offers.RemoveAt(0);
            while (Offers.Count < 3) Offers.Add(NewContract());
        }

        // Grades vary, but each role always has enough candidates to fill every berth.
        void RollBoard()
        {
            Board.Clear();
            if (Rand() < 0.75f) Board.Add(NewCrew(Grade.Hand));
            if (Rand() < 0.4f) Board.Add(NewCrew(Grade.Experienced));
            if (Rand() < 0.06f) Board.Add(NewCrew(Grade.Veteran));
            if (Hull > 0)
            {
                if (Rand() < .8f) Board.Add(NewCrew(Grade.Hand, CrewRole.Fisherman));
                if (Rand() < .5f) Board.Add(NewCrew(Grade.Experienced, CrewRole.Fisherman));
                if (Rand() < .08f) Board.Add(NewCrew(Grade.Veteran, CrewRole.Fisherman));
            }
            EnsureCrewRoleOffers();
        }

        public void EnsureCrewRoleOffers()
        {
            // Retain paid legacy Engineers off the active boat, without consuming a berth.
            foreach (var c in System.Linq.Enumerable.ToArray(Crew))
                if (c.Role == CrewRole.Engineer) { InactiveEngineers.Add(c); if (Deckhand == c) Deckhand = null; ExtraCrew.Remove(c); }
            Board.RemoveAll(c => c.Role == CrewRole.Engineer);
            int required = HullDef.CrewCap;
            foreach (CrewRole role in new[] { CrewRole.Deckhand, CrewRole.Fisherman })
            {
                int available = Board.FindAll(c => c.Role == role).Count;
                while (available < required)
                {
                    Board.Add(NewCrew(Grade.Hand, role));
                    available++;
                }
            }
            var engineers = Board.FindAll(c => c.Role == CrewRole.Engineer);
            var deckhands = Board.FindAll(c => c.Role == CrewRole.Deckhand);
            var fishermen = Board.FindAll(c => c.Role == CrewRole.Fisherman);
            deckhands.Sort((left, right) => left.Grade.CompareTo(right.Grade));
            fishermen.Sort((left, right) => left.Grade.CompareTo(right.Grade));
            Board.Clear();
            for (int i = 0; i < Mathf.Max(engineers.Count, Mathf.Max(deckhands.Count, fishermen.Count)); i++)
            {
                if (i < deckhands.Count) Board.Add(deckhands[i]);
                if (i < fishermen.Count) Board.Add(fishermen[i]);
                if (i < engineers.Count) Board.Add(engineers[i]);
            }
        }

        CrewMember NewCrew(Grade g, CrewRole role = CrewRole.Deckhand)
        {
            string name; int attempts = 0;
            do { name = GameData.Names[Rng.Next(GameData.Names.Length)]; if (++attempts > 32) name += " " + attempts; }
            while (Board.Exists(b => b.Name == name) || System.Linq.Enumerable.Any(Crew, c => c.Name == name));
            return new CrewMember
            {
                Name = name, Grade = g, Role = role, VoyagesLeft = GameData.ContractVoyages(g),
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
                        if (Hull >= GameData.MinimumHull(e.species)) pool.Add(e);
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
                Species.Pollock or Species.Whiting => 3 + Rng.Next(3),
                Species.SeaBass or Species.RedMullet => 2 + Rng.Next(2),
                _ => 1,
            };
            int reward = Mathf.Max(20, Mathf.RoundToInt(count * def.AvgValue * 1.8f / 5f) * 5);
            return new Contract { Species = species, Count = count, VoyagesLeft = 2 + Rng.Next(2), Reward = reward };
        }

        // ---- fishing rolls ----------------------------------------------------------------

        // Longer casts shift the odds toward heavier fish and bigger specimens.
        public (Species, float) RollFish(int spot, float power, bool scraps = false, bool squid = false, bool chum = false)
        {
            // Poor bait is unlimited, but cannot roll a large species or specimen.
            if (scraps)
            {
                var small = GameData.Get(Rng.Next(2) == 0 ? Species.Herring : Species.Mackerel);
                return (small.Species, Mathf.Lerp(small.MinKg, small.MinKg + (small.MaxKg - small.MinKg) * .2f, Rand()));
            }
            power = Mathf.Clamp(power, 0f, 1.4f);
            var table = GameData.Spots[spot].Table;
            float total = 0f;
            var weights = new float[table.Length];
            for (int i = 0; i < table.Length; i++)
            {
                if (Hull < GameData.MinimumHull(table[i].species)) { weights[i] = 0; continue; }
                float h = GameData.Get(table[i].species).Heaviness;
                weights[i] = table[i].weight * Mathf.Lerp(1f - 0.7f * h, 1f + 1.6f * h, power);
                // Premium bait targets substantial fish; small schools remain possible, not dominant.
                if (chum) weights[i] *= .01f + h * h * 8f;
                if (squid) weights[i] *= h < .35f ? .04f : .65f + h * 1.6f;
                total += weights[i];
            }
            float roll = Rand() * total;
            int pick = table.Length - 1;
            for (int i = 0; i < table.Length; i++)
            {
                if (weights[i] <= 0) continue;
                roll -= weights[i];
                if (roll <= 0f) { pick = i; break; }
            }
            var def = GameData.Get(table[pick].species);
            float specimen = Mathf.Pow(Rand(), 1.5f - power);
            if (squid) specimen = Mathf.Lerp(.35f, 1f, specimen);
            if (chum) specimen = Mathf.Lerp(.75f, 1f, specimen);
            float kg = Mathf.Lerp(def.MinKg, def.MaxKg, specimen);
            return (def.Species, kg);
        }

        public float RollBiteWait(int spot, float power)
            => Mathf.Min(GameData.MaxBiteWait, (5f + Rand() * 4f + power * 5f) * GameData.Spots[spot].BiteWait / Mathf.Max(0.3f, Richness[spot]));

        public void OnCatch(int spot, float kg) => Richness[spot] = Mathf.Max(0.3f, Richness[spot] - (Hull >= 2 ? .0035f * kg : GameData.RichnessPerCatch));

        // ---- save / load ----------------------------------------------------------------
        // Saved in the harbour (after selling, after every purchase). A voyage in progress is not saved.

        [System.Serializable]
        class SaveData
        {
            public int Version = 1;
            public int Coins, Bait, Squid, Voyage, BestVoyageFish, Hull;
            public float Fuel, BestVoyageKg;
            public bool HasTimedFuel;
            public bool SecondNetOwned, SecondNetEnabled;
            public bool HasTier5Condition; public float[] Tier5Condition; public bool[] Tier5Broken;
            public int NetInventory;
            // Presence bit distinguishes legacy saves from an explicitly exhausted rack.
            public bool HasNetInventory;
            public int SelectedNet;
            public List<int> DeepNetUses = new();
            public bool UseSquid;
            public PrepOrderSettings PrepOrders;
            public List<CaughtFish> UnsoldCatch = new();
            public List<CoinCredit> CoinCredits = new();
            public float UnsoldMinutes;
            public float FoodMinutes;
            public List<int> Owned = new(), Charts = new();
            public float[] Richness, Market, LogBest;
            public int[] LogCount;
            public bool HasDeckhand;
            public CrewMember Deckhand;
            public List<CrewMember> ExtraCrew = new();
            public List<CrewMember> InactiveEngineers = new();
            public List<CrewMember> Board = new();
            public List<Contract> Offers = new(), Active = new();
        }

        public static string SavePath
        {
            get
            {
                // Standalone verification can never target the real save through this probe.
                var args = System.Environment.GetCommandLineArgs();
                int flag = System.Array.IndexOf(args, "-save-check-root");
                if (flag >= 0 && flag + 1 < args.Length && (Application.isBatchMode ||
                    System.Array.IndexOf(args,"-dashboard087-probe")>=0 && System.IO.Path.GetFileName(System.IO.Path.GetFullPath(args[flag+1]).TrimEnd(System.IO.Path.DirectorySeparatorChar)).StartsWith("dash087-probe-")))
                {
                    string root = System.IO.Path.GetFullPath(args[flag + 1]);
                    System.IO.Directory.CreateDirectory(root);
                    return System.IO.Path.Combine(root, "catchline-save.json");
                }
                return System.IO.Path.Combine(Application.persistentDataPath, "catchline-save.json");
            }
        }

        public void Save(string path = null)
        {
            // Preserve an authorized external one-time credit if a live, older in-memory
            // state saves afterwards. NewGame deletes the save, so credits do not respawn.
            path ??= SavePath;
            try
            {
                if (System.IO.File.Exists(path))
                {
                    var previous = JsonUtility.FromJson<SaveData>(System.IO.File.ReadAllText(path));
                    if (previous?.CoinCredits != null)
                        foreach (var credit in previous.CoinCredits)
                            if (!CoinCredits.Exists(c => c.Id == credit.Id))
                            {
                                Coins += credit.Amount;
                                CoinCredits.Add(credit);
                            }
                }
            }
            catch (System.Exception e) { Debug.LogWarning("[Catchline] Credit reconciliation failed: " + e.Message); }
            var d = new SaveData
            {
                Coins = Coins, Bait = Bait, Squid = Squid, Voyage = Voyage, BestVoyageFish = BestVoyageFish, BestVoyageKg = BestVoyageKg, UseSquid = UseSquid, PrepOrders = PrepOrders,
                SecondNetOwned = SecondNetOwned, SecondNetEnabled = SecondNetEnabled,
                HasTier5Condition = true, Tier5Condition = Tier5Condition, Tier5Broken = Tier5Broken,
                Hull = Hull, Fuel = Fuel, HasTimedFuel = true, NetInventory = NetInventory, HasNetInventory = true,
                SelectedNet = (int)SelectedNet, DeepNetUses = new List<int>(DeepNetUses),
                FoodMinutes = FoodMinutes, Richness = Richness, Market = Market, LogCount = LogCount, LogBest = LogBest, HasDeckhand = Deckhand != null, Deckhand = Deckhand,
            };
            foreach (var u in Owned) d.Owned.Add((int)u);
            d.Charts.AddRange(Charts);
            d.UnsoldCatch.AddRange(UnsoldCatch); d.UnsoldMinutes = UnsoldMinutes;
            d.CoinCredits.AddRange(CoinCredits);
            d.Board.AddRange(Board);
            d.ExtraCrew.AddRange(ExtraCrew); d.InactiveEngineers.AddRange(InactiveEngineers);
            d.Offers.AddRange(Offers);
            d.Active.AddRange(Active);
            try { System.IO.File.WriteAllText(path ?? SavePath, JsonUtility.ToJson(d, true)); }
            catch (System.Exception e) { Debug.LogWarning("[Catchline] Save failed: " + e.Message); }
        }

        public static GameState Load(string path = null)
        {
            try
            {
                path ??= SavePath;
                if (!System.IO.File.Exists(path)) return null;
                var d = JsonUtility.FromJson<SaveData>(System.IO.File.ReadAllText(path));
                if (d == null || d.Version != 1) return null;
                var s = new GameState(System.Environment.TickCount);
                s.Coins = d.Coins; s.Bait = d.Bait; s.Squid = d.Squid; s.Voyage = d.Voyage; s.BestVoyageFish = d.BestVoyageFish;
                s.BestVoyageKg = float.IsNaN(d.BestVoyageKg) || float.IsInfinity(d.BestVoyageKg) ? 0 : Mathf.Max(0, d.BestVoyageKg);
                s.PrepOrders = d.PrepOrders ?? new PrepOrderSettings();
                s.UseSquid = d.UseSquid; s.FoodMinutes = d.FoodMinutes;
                s.Hull = Mathf.Clamp(d.Hull, 0, GameData.Hulls.Length - 1); s.Fuel = d.Fuel;
                s.RestoreTier5Condition(d.HasTier5Condition, d.Tier5Condition, d.Tier5Broken);
                s.SecondNetOwned = d.SecondNetOwned; s.SecondNetEnabled = d.SecondNetEnabled && d.SecondNetOwned;
                s.NetInventory = d.HasNetInventory ? Mathf.Clamp(d.NetInventory, 0, GameData.NetInventoryCapacity) : 3;
                s.SelectedNet = d.SelectedNet == 1 ? NetKind.Deep : NetKind.Shallow;
                if (d.DeepNetUses != null)
                    foreach (int uses in d.DeepNetUses)
                        if (uses > 0 && s.DeepNetUses.Count < GameData.DeepNetRackCapacity)
                            s.DeepNetUses.Add(Mathf.Clamp(uses, 1, GameData.DeepNetUses));
                foreach (var u in d.Owned) s.Owned.Add((UpgradeId)u);
                s.Fuel = Mathf.Clamp(float.IsNaN(s.Fuel) ? 0 : s.Fuel, 0, s.FuelCapacity);
                foreach (var c in d.Charts) s.Charts.Add(c);
                // Arrays can grow between versions (new seas, new fish): copy what fits.
                if (d.Richness != null) System.Array.Copy(d.Richness, s.Richness, Mathf.Min(d.Richness.Length, s.Richness.Length));
                if (d.Market != null) System.Array.Copy(d.Market, s.Market, Mathf.Min(d.Market.Length, s.Market.Length));
                if (d.LogCount != null) System.Array.Copy(d.LogCount, s.LogCount, Mathf.Min(d.LogCount.Length, s.LogCount.Length));
                if (d.LogBest != null) System.Array.Copy(d.LogBest, s.LogBest, Mathf.Min(d.LogBest.Length, s.LogBest.Length));
                s.Deckhand = d.HasDeckhand ? d.Deckhand : null;
                if (d.ExtraCrew != null) s.ExtraCrew.AddRange(d.ExtraCrew);
                if (d.InactiveEngineers != null) s.InactiveEngineers.AddRange(d.InactiveEngineers);
                s.Board.Clear(); s.Board.AddRange(d.Board);
                s.EnsureCrewRoleOffers();
                if (d.UnsoldCatch != null) s.UnsoldCatch.AddRange(d.UnsoldCatch);
                s.UnsoldMinutes = d.UnsoldMinutes;
                if (d.CoinCredits != null) s.CoinCredits.AddRange(d.CoinCredits);
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

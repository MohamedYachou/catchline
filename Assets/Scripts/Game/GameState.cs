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
        public float ValueBonus; // crew abilities: sale value x (1 + ValueBonus)
    }

    [System.Serializable]
    public class CrewMember
    {
        public string Name;
        public string CardId;
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
        public int Tokens, Crates; // crew cards: haul tokens and crates earned by this sale
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
        public int TornNets; // shallow nets torn at sea, waiting in the net loft to be mended
        public int CrabPots; // pots the captain sets beside a hull 1-3 boat at every ground (VoyageCrabPots.cs)
        public int Tier => GameData.HullTier(Hull);
        public HullDef HullDef => GameData.Hulls[Mathf.Clamp(Hull, 0, GameData.Hulls.Length - 1)];
        public bool CanRefit => Tier == 0 && SkiffHaulDone && Coins >= GameData.SkiffCost;
        public bool SkiffHaulDone => BestVoyageKg >= GameData.SkiffKgGoal - .001f;
        public readonly HashSet<UpgradeId> Owned = new();
        public readonly float[] Richness;
        // M4: richness per ground per species (Grounds.Slot), the ground the boat is anchored at (-1 = none, legacy map tables)
        // and the school bonus (1.0 to 1.3) at the boat's position. Set each tick by VoyageGame.TickGrounds.
        public float[] GroundRich = Grounds.NewRichness();
        public int CurrentGround = -1;
        public float SchoolBonus = 1f;
        public bool NightVoyage;
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
            LogCount = new int[GameData.Fish.Length];
            LogBest = new float[GameData.Fish.Length];
            for (int i = 0; i < Richness.Length; i++) Richness[i] = 1f;
            RollBoard();
            while (Offers.Count < 3) Offers.Add(NewContract());
        }

        public bool Has(UpgradeId id) => Owned.Contains(id);
        public float CoolerCapacity => Tier == 0 ? (Has(UpgradeId.BigCooler) ? GameData.RowboatBigCoolerKg : GameData.RowboatHoldKg) : HullDef.Capacity * (Has(UpgradeId.BigCooler) ? 1.5f : 1f);
        public float FuelCapacity => Has(UpgradeId.LunchTin) ? 20f : 10f;
        public float FuelFraction => Mathf.Clamp01(Fuel / FuelCapacity);
        public int FuelFillCost => Mathf.CeilToInt(Mathf.Max(0, FuelCapacity - Fuel) - .00001f);
        public float FoodCapacity => (Has(UpgradeId.LunchTin) ? 12f : 6f) * (Tier > 0 ? 4f : 1f);
        public bool Known(int spot) => GameData.Spots[spot].ChartCost == 0 || Charts.Contains(spot);
        public float BiteWindow => RodTier >= 2 ? 1.4f : RodTier >= 1 ? 1.15f : GameData.BiteWindow;
        public float ReelSpeed => RodTier >= 2 ? 1.5f : RodTier >= 1 ? 1.25f : 1f;
        public float SelfHookChance => RodTier >= 2 ? 0.45f : GameData.SelfHookChance;
        public int FoodFillCost => Mathf.CeilToInt(FoodCapacity - FoodMinutes) * GameData.FoodCostPerMinute;

        // Selling never moves a price: there is no market saturation.
        public float PricePerKg(Species s) => GameData.Get(s).PricePerKg;

        public float Freshness(CaughtFish f, float now)
        {
            if (Has(UpgradeId.IceBox)) return 1f;
            return Mathf.Max(GameData.MinFreshness, 1f - GameData.FreshnessLossPerMinute * Mathf.Max(0f, now - f.StowedAt - GameData.FreshnessGraceSeconds) / 60f);
        }

        public float SpecimenPricePerKg(Species species, float kg)
        {
            var d = GameData.Get(species);
            float size = Mathf.InverseLerp(d.MinKg, d.MaxKg, kg);
            return PricePerKg(species) * (1f + .5f * size);
        }
        public int ValueOf(CaughtFish f, float now) => Mathf.Max(1, Mathf.RoundToInt(f.Kg * SpecimenPricePerKg(f.Species, f.Kg) * Freshness(f, now) * (1f + Mathf.Max(0f, f.ValueBonus))));

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
            if (Tier == 0 || cost <= 0 || Coins < cost) return false;
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

        // A mended net goes back on the rack (docs/plans/MINIGAMES.md, section 5).
        public bool MendNet()
        {
            if (TornNets <= 0 || NetInventory >= GameData.NetInventoryCapacity) return false;
            TornNets--; NetInventory++;
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
            if (Known(spot) || Coins < cost || !Coasts.Open(spot, Hull)) return false;
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
            }
            for (int i = Active.Count - 1; i >= 0; i--)
            {
                var c = Active[i];
                if (c.Delivered < c.Count) continue;
                Coins += c.Reward;
                r.ContractCoins += c.Reward;
                r.Lines.Add($"Contract done: {c.Title}  +{c.Reward}, and a crate");
                GrantChest(ChestKind.Crate);
                r.Crates++;
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
            if (Deckhand != null && string.IsNullOrEmpty(Deckhand.CardId) && --Deckhand.VoyagesLeft <= 0)
            {
                r.Lines.Add($"{Deckhand.Name}'s contract ended. Hire someone new on the crew board.");
                Deckhand = null;
            }
            for (int i = ExtraCrew.Count - 1; i >= 0; i--)
                if (string.IsNullOrEmpty(ExtraCrew[i].CardId) && --ExtraCrew[i].VoyagesLeft <= 0)
                {
                    r.Lines.Add($"{ExtraCrew[i].Name}'s {ExtraCrew[i].RoleName.ToLower()} contract ended.");
                    ExtraCrew.RemoveAt(i);
                }
            if (Deckhand == null)
            {
                int i = ExtraCrew.FindIndex(c => c.Role == CrewRole.Deckhand);
                if (i >= 0) { Deckhand = ExtraCrew[i]; ExtraCrew.RemoveAt(i); }
            }
            Grounds.Recover(GroundRich); RefreshLegacyRichness();
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
            if (Tier > 0)
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
                if (c.Role == CrewRole.Engineer && string.IsNullOrEmpty(c.CardId)) { InactiveEngineers.Add(c); if (Deckhand == c) Deckhand = null; ExtraCrew.Remove(c); }
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
                        if (Tier >= GameData.MinimumHull(e.species) && Coasts.Allowed(i, e.species)) pool.Add(e);
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
            var table = FishTable(spot);
            float total = 0f;
            var weights = new float[table.Length];
            for (int i = 0; i < table.Length; i++)
            {
                if (Tier < GameData.MinimumHull(table[i].species)) { weights[i] = 0; continue; }
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
            // Outer coast fish run big; on the Gull coast a rare species gets one re-roll down, so purples stay a treat.
            if (Coasts.Outer(spot)) specimen = .25f + .75f * specimen;
            else if (CatchPresentation.IsRare(def.Species)) specimen = Mathf.Min(specimen, Rand());
            if (squid) specimen = Mathf.Lerp(.35f, 1f, specimen);
            if (chum) specimen = Mathf.Lerp(.75f, 1f, specimen);
            float kg = Mathf.Lerp(def.MinKg, def.MaxKg, specimen);
            return (def.Species, kg);
        }

        public float RollBiteWait(int spot, float power)
            => Mathf.Min(GameData.MaxBiteWait, (5f + Rand() * 4f + power * 5f) * GameData.Spots[spot].BiteWait / Mathf.Max(0.3f, BiteRichness(spot)));

        // Bite-rate richness: ground average x school bonus while anchored at a ground, otherwise the legacy per-map value.
        public float BiteRichness(int spot)
            => CurrentGround >= 0 && Grounds.Get(spot, CurrentGround) != null ? Grounds.Score(GroundRich, spot, CurrentGround) * SchoolBonus : Richness[spot];

        // The pool a roll draws from: the anchored ground's day or night pool with each species weight scaled by its richness.
        public (Species species, float weight)[] FishTable(int spot)
        {
            var ground = CurrentGround >= 0 ? Grounds.Get(spot, CurrentGround) : null;
            if (ground == null) return Coasts.Shape(spot, GameData.Spots[spot].Table);
            var pool = ground.Pool(NightVoyage);
            var result = new (Species species, float weight)[pool.Length];
            for (int i = 0; i < pool.Length; i++) result[i] = (pool[i].species, pool[i].weight * Grounds.Richness(GroundRich, spot, CurrentGround, pool[i].species));
            return Coasts.Shape(spot, result);
        }

        // Legacy per-map richness is the mean of that map's ground-species richness.
        public void RefreshLegacyRichness()
        {
            for (int m = 0; m < Richness.Length; m++)
            {
                var grounds = Grounds.ForMap(m);
                if (grounds.Length == 0) continue;
                float sum = 0; int n = 0;
                for (int g = 0; g < grounds.Length; g++) foreach (var e in grounds[g].Day) { sum += Grounds.Richness(GroundRich, m, g, e.species); n++; }
                Richness[m] = sum / n;
            }
        }

        public void OnCatch(int spot, float kg) => Richness[spot] = Mathf.Max(0.3f, Richness[spot] - (Tier >= 2 ? .0035f * kg : GameData.RichnessPerCatch));

        // M4: at a ground the catch drains that species there: rods and lines -0.02 per catch, nets -0.004 per kg.
        public void OnCatch(int spot, float kg, Species species, bool net)
        {
            if (CurrentGround < 0 || Grounds.Get(spot, CurrentGround) == null) { OnCatch(spot, kg); return; }
            Grounds.Drain(GroundRich, spot, CurrentGround, species, net ? Grounds.NetDrainPerKg * kg : Grounds.RodDrain);
            RefreshLegacyRichness();
        }

        // ---- save / load ----------------------------------------------------------------
        // Saved in the harbour (after selling, after every purchase). A voyage in progress is not saved.

        [System.Serializable]
        public class HarbourSave
        {
            public int Version = 1;
            public int Coins, Bait, Squid, Voyage, BestVoyageFish, Hull;
            public float Fuel, BestVoyageKg;
            public bool HasTimedFuel;
            public bool SecondNetOwned, SecondNetEnabled;
            public int NetInventory;
            // Presence bit distinguishes legacy saves from an explicitly exhausted rack.
            public bool HasNetInventory;
            public int TornNets;
            public int CrabPots;
            public int SelectedNet;
            public List<int> DeepNetUses = new();
            public bool UseSquid;
            public PrepOrderSettings PrepOrders;
            public List<CaughtFish> UnsoldCatch = new();
            public List<CoinCredit> CoinCredits = new();
            public float UnsoldMinutes;
            public float FoodMinutes;
            public List<int> Owned = new(), Charts = new();
            public float[] Richness, LogBest;
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
                if (flag >= 0 && flag + 1 < args.Length && Application.isBatchMode)
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
                    string previousJson = System.IO.File.ReadAllText(path);
                    var previous = SaveV2.FromJson(previousJson)?.Runtime;
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
            var d = new HarbourSave
            {
                Coins = Coins, Bait = Bait, Squid = Squid, Voyage = Voyage, BestVoyageFish = BestVoyageFish, BestVoyageKg = BestVoyageKg, UseSquid = UseSquid, PrepOrders = PrepOrders,
                SecondNetOwned = SecondNetOwned, SecondNetEnabled = SecondNetEnabled,
                Hull = Hull, Fuel = Fuel, HasTimedFuel = true, NetInventory = NetInventory, HasNetInventory = true, TornNets = TornNets, CrabPots = CrabPots,
                SelectedNet = (int)SelectedNet, DeepNetUses = new List<int>(DeepNetUses),
                FoodMinutes = FoodMinutes, Richness = Richness, LogCount = LogCount, LogBest = LogBest, HasDeckhand = Deckhand != null, Deckhand = Deckhand,
            };
            foreach (var u in Owned) d.Owned.Add((int)u);
            d.Charts.AddRange(Charts);
            d.UnsoldCatch.AddRange(UnsoldCatch); d.UnsoldMinutes = UnsoldMinutes;
            d.CoinCredits.AddRange(CoinCredits);
            d.Board.AddRange(Board);
            d.ExtraCrew.AddRange(ExtraCrew); d.InactiveEngineers.AddRange(InactiveEngineers);
            d.Offers.AddRange(Offers);
            d.Active.AddRange(Active);
            var v2 = new SaveV2 { Coins = Coins, Hull = Hull, Runtime = d,
                CrewSettings = new List<CrewMember>(Crew), GroundRichness = new List<float>(GroundRich) };
            WriteCards(v2);
            v2.Owned.AddRange(d.Owned);
            try { System.IO.File.WriteAllText(path ?? SavePath, JsonUtility.ToJson(v2, true)); }
            catch (System.Exception e) { Debug.LogWarning("[Catchline] Save failed: " + e.Message); }
        }

        public static GameState Load(string path = null)
        {
            try
            {
                path ??= SavePath;
                if (!System.IO.File.Exists(path)) return null;
                string json = System.IO.File.ReadAllText(path);
                var v2 = SaveV2.FromJson(json);
                var d = v2?.Runtime;
                var s = new GameState(System.Environment.TickCount);
                if (v2 == null)
                {
                    return null; // Only the v2 payload is read; there is no v1 import.
                }
                s.Coins = v2.Coins; s.Hull = Mathf.Clamp(v2.Hull, 0, GameData.Hulls.Length - 1);
                if (v2.Owned != null) foreach (int u in v2.Owned) s.Owned.Add((UpgradeId)u);
                s.ReadCards(v2);
                if (v2.CrewSettings != null) s.cardCrew.AddRange(v2.CrewSettings);
                if (v2.GroundRichness != null)
                    for (int i = 0; i < Mathf.Min(v2.GroundRichness.Count, s.GroundRich.Length); i++)
                        s.GroundRich[i] = float.IsNaN(v2.GroundRichness[i]) ? Grounds.Start : Mathf.Clamp(v2.GroundRichness[i], Grounds.Floor, Grounds.Start);
                s.RefreshLegacyRichness();
                s.EnsureCards(); s.SyncCardCrew();
                if (d == null) return s;
                s.Coins = d.Coins; s.Bait = d.Bait; s.Squid = d.Squid; s.Voyage = d.Voyage; s.BestVoyageFish = d.BestVoyageFish;
                s.BestVoyageKg = float.IsNaN(d.BestVoyageKg) || float.IsInfinity(d.BestVoyageKg) ? 0 : Mathf.Max(0, d.BestVoyageKg);
                s.PrepOrders = d.PrepOrders ?? new PrepOrderSettings();
                s.UseSquid = d.UseSquid; s.FoodMinutes = d.FoodMinutes;
                s.Hull = Mathf.Clamp(d.Hull, 0, GameData.Hulls.Length - 1); s.Fuel = d.Fuel;
                s.SecondNetOwned = d.SecondNetOwned; s.SecondNetEnabled = d.SecondNetEnabled && d.SecondNetOwned;
                s.NetInventory = d.HasNetInventory ? Mathf.Clamp(d.NetInventory, 0, GameData.NetInventoryCapacity) : 3;
                s.TornNets = Mathf.Clamp(d.TornNets, 0, GameData.NetInventoryCapacity);
                s.CrabPots = Mathf.Clamp(d.CrabPots, 0, 2);
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
                if (d.LogCount != null) System.Array.Copy(d.LogCount, s.LogCount, Mathf.Min(d.LogCount.Length, s.LogCount.Length));
                if (d.LogBest != null) System.Array.Copy(d.LogBest, s.LogBest, Mathf.Min(d.LogBest.Length, s.LogBest.Length));
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

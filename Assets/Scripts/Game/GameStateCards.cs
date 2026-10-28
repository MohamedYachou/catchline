using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public sealed class RosterReport
    {
        public sealed class Row
        {
            public string Id, Name, Role, Ability;
            public int Level, Cap, Wage, Blueprints, BlueprintsNeeded, Stars, LevelTokens, LevelCoins, ToolSlots;
            public CardRarity Rarity;
            public bool Deployed, Available, Focus, CanLevelUp, CanRankUp, CanStar, Maxed;
        }
        public Row[] Cards;
        public int Berths, Wages, Deployed, Tokens, Renown, PendingChests, FreeBlueprints;
    }

    // Crew cards v2 state and rules (docs/plans/CREW-CARDS-V2.md section 10).
    public partial class GameState
    {
        public const string CaptainToolOwner = "captain"; // tool owner id for the captain's three slots

        public readonly List<CardState> Roster = new();
        public readonly List<string> Deployment = new();
        // Crew aboard for the trip being sold, fixed at departure: haul tokens count that trip's crew.
        public readonly List<string> TripDeployment = new();
        public int Tokens;                                   // universal upgrade tokens
        public readonly List<ToolState> Tools = new();       // every tool owned, equipped or not
        public int[] CaptainTools = new int[CardProgression.MaxToolSlots];
        public int NextToolUid = 1;
        public string FocusCard = "";
        public int[] ChestPities = new int[Chests.All.Length]; // per kind: chests opened since its last blueprint
        public int RestaurantPopularity = 1;
        public int RestaurantDay, RestaurantWeather;            // nights served; tomorrow's Restaurant.Weather
        public string RestaurantLayout = "";                    // RestaurantState JSON (stage, items, upgrades)
        public readonly List<string> RestaurantPriorities = new(); // "crewId=Work,Work,Work", set on S9
        public readonly List<string> RestaurantCards = new();      // night cards kept: gadget/dish ids, and "next=<night id>" for tomorrow
        public readonly List<string> RestaurantNights = new();   // "day|net|dishes|drinks|tips|popularity|served|left|Dish=n;..."
        public int Tutorial = int.MaxValue;                  // VoyageGame.TutStep; only a fresh game from the title starts it
        public readonly Dictionary<string, int> CrewChestsBought = new(); // crew id -> chests bought from their offer
        public int FreeBlueprints;                           // blueprints the player assigns to any crew
        public int RenownClaimed;                            // renown road milestones claimed, in order
        public readonly List<ChestKind> PendingChests = new();
        public string LastCrateDay = "";                     // yyyy-MM-dd of the last first-sale crate
        readonly List<CrewMember> cardCrew = new();
        // Crew progression follows tiers; append-only hull IDs are a separate identity.
        public int CardTier => Tier;
        public int CardBerths => CardRoster.BerthsForTier(CardTier);
        public int DepartureWages { get { EnsureCards(); return CardRoster.TotalWages(Roster, Deployment); } }
        public bool CardAvailable(CardState card) => CardRoster.Available(card, CardTier);
        public int Renown { get { int r = 0; foreach (var c in Roster) r += c.Renown; return r; } }

        public void EnsureCards()
        {
            // Crew are no longer free with a tier (Mo, 2026-10-25): the first boat brings the welcome chest with Mira,
            // everyone else joins through blueprints and their crew chests.
            if (CardTier >= 1 && !Roster.Exists(c => c.Def?.Role == CardRole.Navigator) && !PendingChests.Contains(ChestKind.Welcome))
                PendingChests.Insert(0, ChestKind.Welcome);
            foreach (var c in Roster) c.Normalise();
            var seen = new HashSet<string>();
            Deployment.RemoveAll(id => !CardAvailable(CardRoster.Find(Roster, id)) || !seen.Add(id));
            if (CardTier >= 1) CardRoster.EnsureNavigator(Roster, Deployment);
            if (!CardRoster.Owns(Roster, FocusCard)) FocusCard = "";
        }
        // Test trials only: every crew member up to the boat's tier at their starting rarity, the navigator aboard.
        public void GrantTrialCards() { CardRoster.GrantUpToTier(Roster, Deployment, CardTier); PendingChests.RemoveAll(k => k == ChestKind.Welcome); EnsureCards(); }
        public bool DeployCard(string id, bool deploy)
        {
            EnsureCards();
            if (deploy && !CardAvailable(CardRoster.Find(Roster, id))) return false;
            bool ok = deploy ? CardRoster.TryDeploy(Roster, Deployment, id, CardBerths) : CardRoster.TryUndeploy(Deployment, id);
            if (ok) SyncCardCrew();
            return ok;
        }
        // Suit colours follow the original card order, so reordering Cards.All never recolours anyone.
        static readonly string[] SuitOrder = { "mira", "noor", "dirk", "tess", "sam", "kofi", "rosa", "ana", "mats", "lise", "ines", "olaf", "pim", "tove" };
        public void SyncCardCrew()
        {
            EnsureCards();
            // Legacy members are retained only for old editor fixtures. Active UI exclusively deploys cards.
            if (Deckhand != null && !string.IsNullOrEmpty(Deckhand.CardId)) Deckhand = null;
            ExtraCrew.RemoveAll(c => !string.IsNullOrEmpty(c.CardId));
            foreach (string id in Deployment)
            {
                var card = CardRoster.Find(Roster, id); var d = card.Def;
                var c = cardCrew.Find(x => x.CardId == id);
                if (c == null)
                {
                    c = new CrewMember { CardId = id, Name = d.Name, VoyagesLeft = int.MaxValue,
                        Role = d.Role == CardRole.Fisher ? CrewRole.Fisherman : d.Role == CardRole.Navigator ? CrewRole.Navigator : d.Role == CardRole.Engineer ? CrewRole.Engineer : CrewRole.Deckhand,
                        WorkPreference = d.Speciality == Speciality.Sort ? DeckhandWork.Nets : d.Speciality == Speciality.Table ? DeckhandWork.Prep : DeckhandWork.Fish,
                        Suit = GameData.Suits[Math.Max(0, Array.IndexOf(SuitOrder, d.Id)) % GameData.Suits.Length] };
                    cardCrew.Add(c);
                }
                if (c.Role == CrewRole.Deckhand && Deckhand == null) Deckhand = c;
                else ExtraCrew.Add(c);
            }
        }
        public bool PayDepartureWages()
        {
            int wage = DepartureWages;
            if (Coins < wage || UnsoldCatch.Count > 0) return false;
            Coins -= wage; TripDeployment.Clear(); TripDeployment.AddRange(Deployment); return true;
        }

        // ---- levels, ranks, stars and focus ----------------------------------------------------

        public bool LevelUpCard(string id)
        {
            EnsureCards();
            return CardRoster.TryLevelUp(CardRoster.Find(Roster, id), ref Tokens, ref Coins);
        }
        // Levels as far as tokens and coins reach, up to the rarity cap. Returns the levels gained.
        public int LevelUpCardToCap(string id)
        {
            EnsureCards();
            var card = CardRoster.Find(Roster, id);
            int gained = 0;
            while (CardRoster.TryLevelUp(card, ref Tokens, ref Coins)) gained++;
            return gained;
        }
        // Rank up at the level cap, or add a star once Mythic.
        public bool RankUpCard(string id)
        {
            EnsureCards();
            return CardRoster.TryRankUp(CardRoster.Find(Roster, id));
        }
        // An empty id clears the focus.
        public bool SetFocus(string id)
        {
            if (string.IsNullOrEmpty(id)) { FocusCard = ""; return true; }
            if (!CardRoster.Owns(Roster, id)) return false;
            FocusCard = id;
            return true;
        }
        public bool AssignFreeBlueprint(string id)
        {
            var card = CardRoster.Find(Roster, id);
            if (FreeBlueprints <= 0 || !Chests.WantsBlueprints(card)) return false;
            FreeBlueprints--;
            card.Blueprints++;
            return true;
        }

        // ---- tools -----------------------------------------------------------------------------

        public ToolState FindTool(int uid)
        {
            if (uid == 0) return null;
            foreach (var t in Tools) if (t.Uid == uid) return t;
            return null;
        }
        public ToolState AddTool(ToolKind kind, CardRarity rarity)
        {
            var tool = new ToolState { Uid = NextToolUid++, Kind = kind, Rarity = rarity };
            Tools.Add(tool);
            return tool;
        }
        int[] ToolSlotsOf(string owner) => owner == CaptainToolOwner ? CaptainTools : CardRoster.Find(Roster, owner)?.ToolUids;
        public int ToolSlotCount(string owner)
        {
            if (owner == CaptainToolOwner) return CardProgression.MaxToolSlots;
            var card = CardRoster.Find(Roster, owner);
            return card == null ? 0 : CardProgression.ToolSlots(card.Rarity);
        }
        // The class whose tools `owner` may use; null for the captain (every class but navigator).
        CardRole? ToolRole(string owner) => owner == CaptainToolOwner ? null : CardRoster.Find(Roster, owner)?.Def?.Role;
        // Card id (or CaptainToolOwner) holding the tool; null when it is in the inventory.
        public string ToolOwner(int uid)
        {
            if (uid == 0) return null;
            if (Array.IndexOf(CaptainTools, uid) >= 0) return CaptainToolOwner;
            foreach (var c in Roster) if (c.ToolUids != null && Array.IndexOf(c.ToolUids, uid) >= 0) return c.Id;
            return null;
        }
        void ClearToolSlots(int uid)
        {
            for (int i = 0; i < CaptainTools.Length; i++) if (CaptainTools[i] == uid) CaptainTools[i] = 0;
            foreach (var c in Roster)
                if (c.ToolUids != null)
                    for (int i = 0; i < c.ToolUids.Length; i++) if (c.ToolUids[i] == uid) c.ToolUids[i] = 0;
        }
        public bool EquipTool(string owner, int slot, int uid)
        {
            var tool = FindTool(uid); var slots = ToolSlotsOf(owner);
            if (tool == null || slots == null || slot < 0 || slot >= ToolSlotCount(owner)) return false;
            if (!ToolInfo.CanUse(ToolRole(owner), tool.Kind)) return false;
            ClearToolSlots(uid);
            slots[slot] = uid;
            return true;
        }
        public bool UnequipTool(string owner, int slot)
        {
            var slots = ToolSlotsOf(owner);
            if (slots == null || slot < 0 || slot >= slots.Length || slots[slot] == 0) return false;
            slots[slot] = 0;
            return true;
        }
        public IEnumerable<ToolState> EquippedTools(string owner)
        {
            var slots = ToolSlotsOf(owner);
            if (slots == null) yield break;
            int n = Math.Min(slots.Length, ToolSlotCount(owner));
            for (int i = 0; i < n; i++)
            {
                var tool = FindTool(slots[i]);
                if (tool != null) yield return tool;
            }
        }
        // Summed bonus of `owner`'s equipped tools of one kind, capped at +50%.
        public float ToolBonus(string owner, ToolKind kind) => ToolInfo.Bonus(EquippedTools(owner), kind);
        // Two tools of one kind and rarity become one of the next rarity. `keep` stays where it is equipped.
        public bool MergeTools(int keep, int feed)
        {
            var a = FindTool(keep); var b = FindTool(feed);
            if (!ToolInfo.CanMerge(a, b)) return false;
            ClearToolSlots(feed);
            Tools.Remove(b);
            a.Rarity = (CardRarity)((int)a.Rarity + 1);
            return true;
        }
        // The captain's best rod tool picks the boat's rods (fibreglass and carbon left the market):
        // 0 standard, 1 fibreglass (Blue+), 2 carbon (Gold+).
        public int RodTier
        {
            get
            {
                int best = -1;
                for (int i = 0; i < CaptainTools.Length; i++)
                {
                    var tool = FindTool(CaptainTools[i]);
                    if (tool != null && tool.Kind == ToolKind.Rod && (int)tool.Rarity > best) best = (int)tool.Rarity;
                }
                return best >= (int)CardRarity.Gold ? 2 : best >= (int)CardRarity.Blue ? 1 : 0;
            }
        }

        // ---- chests, tokens and the renown road ------------------------------------------------

        public int ChestPrice(ChestKind kind) => Chests.Def(kind).Price(CardTier);
        public bool BuyChest(ChestKind kind)
        {
            var def = Chests.Def(kind);
            if (!def.ForSale) return false;
            int price = def.Price(CardTier);
            if (Coins < price) return false;
            Coins -= price;
            PendingChests.Add(kind);
            return true;
        }
        public void GrantChest(ChestKind kind) => PendingChests.Add(kind);
        public int PendingChestCount(ChestKind kind) => PendingChests.Count(k => k == kind);
        // Opens one pending chest of `kind` and banks everything in it. Null when none is pending.
        public ChestResult OpenChest(ChestKind kind)
        {
            int i = PendingChests.IndexOf(kind);
            if (i < 0) return null;
            EnsureCards();
            PendingChests.RemoveAt(i);
            if (ChestPities == null || ChestPities.Length != Chests.All.Length) Array.Resize(ref ChestPities, Chests.All.Length);
            var result = Chests.Open(kind, CardTier, Rng, Roster, FocusCard, ref ChestPities[(int)kind], ref NextToolUid);
            Bank(result);
            return result;
        }
        // Banks a rolled chest: tokens, tools, free blueprints; a blueprint for someone not aboard the roster recruits them.
        void Bank(ChestResult result)
        {
            Tokens += result.Tokens;
            Tools.AddRange(result.Tools);
            foreach (var id in result.Recruits) CardRoster.Recruit(Roster, id);
            foreach (var id in result.Blueprints)
            {
                if (CardRoster.Recruit(Roster, id)) { result.Recruits.Add(id); continue; }
                CardRoster.Find(Roster, id).Blueprints++;
            }
            FreeBlueprints += result.FreeBlueprints;
            CardRoster.EnsureNavigator(Roster, Deployment);
            if (result.Recruits.Count > 0) SyncCardCrew();
        }
        public int ChestsToPity(ChestKind kind)
        {
            int pity = Chests.Def(kind).Pity;
            int done = ChestPities != null && (int)kind < ChestPities.Length ? ChestPities[(int)kind] : 0;
            return pity <= 0 ? 0 : Math.Max(1, pity - done);
        }

        // ---- crew chests: ten per crew member, the tenth always holds their blueprint ----------

        public int CrewChestsBoughtFor(string id) => CrewChestsBought.TryGetValue(id ?? "", out int n) ? n : 0;
        public int CrewChestsLeft(string id) => Math.Max(0, Chests.CrewChestOffer - CrewChestsBoughtFor(id));
        // Offered once the boat's tier unlocks them; the navigator joins from the welcome chest instead.
        public bool CrewChestOffered(CardDef def) => def != null && def.Role != CardRole.Navigator && def.TierGranted <= CardTier && CrewChestsLeft(def.Id) > 0;
        public bool CanBuyCrewChest(string id) { var d = Catchline.Game.Cards.ById(id); return CrewChestOffered(d) && Coins >= Chests.CrewChestPrice(d); }
        // Buys and opens the next chest of `id`'s offer. Null when it is not offered or unaffordable.
        public ChestResult BuyCrewChest(string id)
        {
            EnsureCards();
            if (!CanBuyCrewChest(id)) return null;
            var def = Catchline.Game.Cards.ById(id);
            Coins -= Chests.CrewChestPrice(def);
            int n = CrewChestsBoughtFor(id) + 1;
            CrewChestsBought[id] = n;
            var result = Chests.OpenCrew(id, n, Rng, Roster, ref NextToolUid);
            Bank(result);
            return result;
        }
        // The first sale of each calendar day brings a crate. True when one was granted.
        public bool GrantDailyCrate(DateTime today)
        {
            string day = today.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
            if (LastCrateDay == day) return false;
            LastCrateDay = day;
            GrantChest(ChestKind.Crate);
            return true;
        }
        // Tokens for a sold haul (tier x crew aboard x hold fill, +15% full), paid to the trip's crew size.
        public int AwardHaulTokens(float kgSold)
        {
            float capacity = CoolerCapacity;
            int tokens = CardProgression.HaulTokens(CardTier, TripDeployment.Count, capacity > 0f ? kgSold / capacity : 0f);
            Tokens += tokens;
            TripDeployment.Clear();
            return tokens;
        }
        // Claims milestone n (1-based, in order) once renown reaches it. A blueprint of choice needs `choiceCardId`.
        public bool ClaimRenown(int n, string choiceCardId = null)
        {
            if (n != RenownClaimed + 1 || Renown < RenownRoad.Threshold(n)) return false;
            var reward = RenownRoad.Reward(n);
            switch (reward.Kind)
            {
                case RenownRewardKind.BlueprintChoice:
                    var card = CardRoster.Find(Roster, choiceCardId);
                    if (card == null && CardRoster.Recruitable(Roster, Catchline.Game.Cards.ById(choiceCardId), CardTier)) { CardRoster.Recruit(Roster, choiceCardId); SyncCardCrew(); break; }
                    if (!Chests.WantsBlueprints(card)) return false;
                    card.Blueprints++;
                    break;
                case RenownRewardKind.Tokens: Tokens += reward.Tokens; break;
                default: GrantChest(reward.Chest); break;
            }
            RenownClaimed = n;
            return true;
        }

        // ---- save --------------------------------------------------------------------------------

        // Drops tool slots that point at tools no longer owned.
        void NormaliseTools()
        {
            if (CaptainTools == null || CaptainTools.Length != CardProgression.MaxToolSlots) CaptainTools = new int[CardProgression.MaxToolSlots];
            Tools.RemoveAll(t => t == null || t.Uid <= 0);
            var owned = new HashSet<int>(Tools.Select(t => t.Uid));
            for (int i = 0; i < CaptainTools.Length; i++) if (!owned.Contains(CaptainTools[i])) CaptainTools[i] = 0;
            foreach (var c in Roster)
            {
                c.Normalise();
                for (int i = 0; i < c.ToolUids.Length; i++) if (!owned.Contains(c.ToolUids[i])) c.ToolUids[i] = 0;
            }
            int top = Tools.Count == 0 ? 0 : Tools.Max(t => t.Uid);
            if (NextToolUid <= top) NextToolUid = top + 1;
        }
        void WriteCards(SaveV2 v2)
        {
            EnsureCards();
            v2.Cards = new List<CardState>(Roster); v2.Deployment = new List<string>(Deployment);
            v2.TripDeployment = new List<string>(TripDeployment);
            v2.Tokens = Tokens; v2.Tools = new List<ToolState>(Tools); v2.CaptainTools = (int[])CaptainTools.Clone();
            v2.NextToolUid = NextToolUid; v2.FocusCard = FocusCard; v2.ChestPities = (int[])ChestPities.Clone(); v2.Tutorial = Tutorial; v2.RestaurantPopularity = RestaurantPopularity; v2.RestaurantDay = RestaurantDay; v2.RestaurantWeather = RestaurantWeather; v2.RestaurantNights = new List<string>(RestaurantNights); v2.RestaurantPriorities = new List<string>(RestaurantPriorities); v2.RestaurantCards = new List<string>(RestaurantCards); v2.RestaurantLayout = RestaurantLayout; v2.CrewChests = CrewChestsBought.Select(kv => kv.Key + ":" + kv.Value).ToList(); v2.FreeBlueprints = FreeBlueprints;
            v2.RenownClaimed = RenownClaimed; v2.PendingChests = PendingChests.Select(k => (int)k).ToList(); v2.LastCrateDay = LastCrateDay;
        }
        void ReadCards(SaveV2 v2)
        {
            if (v2.Cards != null) Roster.AddRange(v2.Cards.FindAll(c => c?.Def != null));
            if (v2.Deployment != null) Deployment.AddRange(v2.Deployment);
            if (v2.TripDeployment != null) TripDeployment.AddRange(v2.TripDeployment);
            Tokens = Mathf.Max(0, v2.Tokens);
            if (v2.Tools != null) Tools.AddRange(v2.Tools);
            CaptainTools = v2.CaptainTools;
            NextToolUid = Mathf.Max(1, v2.NextToolUid);
            FocusCard = v2.FocusCard ?? "";
            Tutorial = v2.Tutorial >= 0 ? v2.Tutorial : int.MaxValue;
            RestaurantPopularity = Mathf.Max(1, v2.RestaurantPopularity);
            RestaurantDay = Mathf.Max(0, v2.RestaurantDay); RestaurantWeather = v2.RestaurantWeather;
            if (v2.RestaurantNights != null) RestaurantNights.AddRange(v2.RestaurantNights);
            if (v2.RestaurantPriorities != null) RestaurantPriorities.AddRange(v2.RestaurantPriorities);
            if (v2.RestaurantCards != null) RestaurantCards.AddRange(v2.RestaurantCards);
            RestaurantLayout = v2.RestaurantLayout ?? "";
            ChestPities = new int[Chests.All.Length];
            if (v2.ChestPities != null && v2.ChestPities.Length > 0)
                for (int i = 0; i < ChestPities.Length && i < v2.ChestPities.Length; i++) ChestPities[i] = Mathf.Max(0, v2.ChestPities[i]);
            else ChestPities[(int)ChestKind.SeaChest] = Mathf.Max(0, v2.ChestPity);
            for (int i = 0; i < ChestPities.Length; i++) if (Chests.All[i].Pity > 0) ChestPities[i] = Mathf.Min(ChestPities[i], Chests.All[i].Pity - 1);
            CrewChestsBought.Clear();
            if (v2.CrewChests != null)
                foreach (var entry in v2.CrewChests)
                {
                    int colon = entry == null ? -1 : entry.LastIndexOf(':');
                    if (colon > 0 && int.TryParse(entry.Substring(colon + 1), out int n) && Catchline.Game.Cards.ById(entry.Substring(0, colon)) != null)
                        CrewChestsBought[entry.Substring(0, colon)] = Mathf.Clamp(n, 0, Chests.CrewChestOffer);
                }
            FreeBlueprints = Mathf.Max(0, v2.FreeBlueprints);
            RenownClaimed = Mathf.Max(0, v2.RenownClaimed);
            if (v2.PendingChests != null)
                foreach (int k in v2.PendingChests)
                    if (k >= 0 && k < Chests.All.Length) PendingChests.Add((ChestKind)k);
            LastCrateDay = v2.LastCrateDay ?? "";
            NormaliseTools();
        }

        public RosterReport ReadRoster()
        {
            EnsureCards();
            return new RosterReport { Berths = CardBerths, Wages = DepartureWages, Deployed = Deployment.Count, Tokens = Tokens,
                Renown = Renown, PendingChests = PendingChests.Count, FreeBlueprints = FreeBlueprints,
                Cards = Roster.Select(c => new RosterReport.Row { Id = c.Id, Name = c.Def.Name, Role = c.Def.Role.ToString(),
                    Ability = AbilityLine(c), Level = c.Level, Cap = c.LevelCap, Wage = c.Wage(), Rarity = c.Rarity,
                    Blueprints = c.Blueprints, BlueprintsNeeded = c.BlueprintsNeeded, Stars = c.Stars,
                    LevelTokens = CardProgression.TokensForLevel(c.Level), LevelCoins = CardProgression.CoinsForLevel(c.Level),
                    ToolSlots = CardProgression.ToolSlots(c.Rarity), Deployed = Deployment.Contains(c.Id), Available = CardAvailable(c),
                    Focus = c.Id == FocusCard, CanLevelUp = !c.AtCap && Tokens >= CardProgression.TokensForLevel(c.Level) && Coins >= CardProgression.CoinsForLevel(c.Level),
                    CanRankUp = c.CanRankUp, CanStar = c.CanStar, Maxed = c.Maxed }).ToArray() };
        }
        // The strongest unlocked ability, or what Green unlocks.
        static string AbilityLine(CardState c)
        {
            var def = c.Def;
            var top = def.TopAbility(c.Rarity);
            return top != null ? top.Name + ": " + top.Text : $"At Green: {def.Passive.Name}. {def.Passive.Text}";
        }
    }

    public partial class VoyageGame
    {
        bool CardsEditable => CurrentMode == Mode.Harbour;
        bool CardChange(bool ok, bool boat = false)
        {
            if (!ok) return false;
            SyncCrew();
            if (boat) SyncUpgrades();
            SaveGame();
            return true;
        }
        public bool DeployCard(string id, bool deploy) => CardsEditable && CardChange(State.DeployCard(id, deploy));
        public bool LevelUpCard(string id) => CardsEditable && CardChange(State.LevelUpCard(id));
        public int LevelUpCardToCap(string id)
        {
            int gained = CardsEditable ? State.LevelUpCardToCap(id) : 0;
            CardChange(gained > 0);
            return gained;
        }
        public bool RankUpCard(string id) => CardsEditable && CardChange(State.RankUpCard(id));
        public bool SetFocusCard(string id) => CardsEditable && CardChange(State.SetFocus(id));
        public bool AssignFreeBlueprint(string id) => CardsEditable && CardChange(State.AssignFreeBlueprint(id));
        public bool EquipTool(string owner, int slot, int uid) => CardsEditable && CardChange(State.EquipTool(owner, slot, uid), true);
        public bool UnequipTool(string owner, int slot) => CardsEditable && CardChange(State.UnequipTool(owner, slot), true);
        public bool MergeTools(int keep, int feed) => CardsEditable && CardChange(State.MergeTools(keep, feed), true);
        public bool BuyChest(ChestKind kind) => CardsEditable && CardChange(State.BuyChest(kind));
        public ChestResult OpenChest(ChestKind kind)
        {
            var result = CardsEditable ? State.OpenChest(kind) : null;
            CardChange(result != null);
            return result;
        }
        public ChestResult BuyCrewChest(string id)
        {
            var result = CardsEditable ? State.BuyCrewChest(id) : null;
            CardChange(result != null);
            return result;
        }
        public bool ClaimRenown(int n, string choiceCardId = null) => CardsEditable && CardChange(State.ClaimRenown(n, choiceCardId));

        // One line for a toast: "Crate: 8 tokens, White Rod, blueprint for Noor".
        public static string ChestSummary(ChestResult r)
        {
            if (r == null) return "";
            var parts = new List<string> { r.Tokens + " tokens" };
            foreach (var t in r.Tools) parts.Add(t.Rarity + " " + ToolInfo.Name(t.Kind).ToLowerInvariant());
            foreach (var id in r.Recruits) parts.Add((Cards.ById(id)?.Name ?? id) + " joins the crew");
            foreach (var id in r.Blueprints) if (!r.Recruits.Contains(id)) parts.Add("blueprint for " + (Cards.ById(id)?.Name ?? id));
            if (r.FreeBlueprints > 0) parts.Add("a blueprint of your choice");
            return Chests.Def(r.Kind).Name + ": " + string.Join(", ", parts);
        }
    }
}

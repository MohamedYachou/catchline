using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public sealed class RosterReport
    {
        public sealed class Row
        {
            public string Id, Name, Role, Ability;
            public int Level, Wage; public float Xp; public CardRarity Rarity; public bool Deployed;
        }
        public Row[] Cards; public int Berths, Wages, Deployed;
    }

    public partial class GameState
    {
        public readonly List<CardState> Roster = new();
        public readonly List<string> Deployment = new();
        public int[] Wildcards = new int[4];
        public readonly List<string> TripDeployment = new();
        public float PendingXpKg;
        readonly List<CrewMember> cardCrew = new();
        // Existing hull indexes skip the future tier-3 jig boat.
        public int CardTier => Hull >= 3 ? Hull + 1 : Hull;
        public int CardBerths => CardRoster.BerthsForTier(CardTier);
        public int DepartureWages { get { EnsureCards(); return CardRoster.TotalWages(Roster, Deployment); } }
        public void EnsureCards()
        {
            CardRoster.GrantUpToTier(Roster, Deployment, CardTier);
            var seen = new HashSet<string>();
            Deployment.RemoveAll(id => !CardRoster.Owns(Roster, id) || !seen.Add(id));
            CardRoster.EnsureNavigator(Roster, Deployment);
        }
        public bool DeployCard(string id, bool deploy)
        {
            EnsureCards();
            bool ok = deploy ? CardRoster.TryDeploy(Roster, Deployment, id, CardBerths) : CardRoster.TryUndeploy(Deployment, id);
            if (ok) SyncCardCrew();
            return ok;
        }
        public bool UpgradeCard(string id)
        {
            EnsureCards();
            return CardRoster.TryUpgradeRarity(CardRoster.Find(Roster, id), ref Coins, Wildcards);
        }
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
                        Suit = GameData.Suits[Array.IndexOf(Catchline.Game.Cards.All, d) % GameData.Suits.Length] };
                    cardCrew.Add(c);
                }
                if (c.Role == CrewRole.Deckhand && Deckhand == null) Deckhand = c;
                else ExtraCrew.Add(c);
            }
        }
        public bool PayDepartureWages()
        {
            int wage = DepartureWages;
            if (Coins < wage || PendingXpKg > 0) return false;
            Coins -= wage; TripDeployment.Clear(); TripDeployment.AddRange(Deployment); return true;
        }
        public void AwardSaleXp()
        {
            CardRoster.AddKgToDeployed(Roster, TripDeployment, PendingXpKg);
            PendingXpKg = 0; TripDeployment.Clear();
        }
        public RosterReport ReadRoster()
        {
            EnsureCards();
            return new RosterReport { Berths = CardBerths, Wages = DepartureWages, Deployed = Deployment.Count,
                Cards = Roster.Select(c => new RosterReport.Row { Id = c.Id, Name = c.Def.Name,
                    Role = c.Def.Role.ToString(), Ability = c.Def.AbilityText(c.Rarity), Level = c.Level,
                    Xp = c.Xp, Wage = c.Wage(), Rarity = c.Rarity, Deployed = Deployment.Contains(c.Id) }).ToArray() };
        }
    }
    public partial class VoyageGame
    {
        public bool DeployCard(string id, bool deploy)
        {
            if (CurrentMode != Mode.Harbour || !State.DeployCard(id, deploy)) return false;
            SyncCrew(); SaveGame(); return true;
        }
        public bool UpgradeCard(string id)
        {
            if (CurrentMode != Mode.Harbour || !State.UpgradeCard(id)) return false;
            SyncCrew(); SaveGame(); return true;
        }
        void InterfaceRoster()
        {
            var report = State.ReadRoster();
            CatalogHeading("crew/heading", $"Crew / {report.Deployed} of {report.Berths} berths", $"Wages next departure: {report.Wages} coins. Cards stay with you; stand down crew to reduce wages.");
            foreach (var row in report.Cards)
            {
                string id = "crew/roster/" + row.Id; float y = catalogY, w = catalogWidth;
                coastalUi.Box(id, new Rect(0,y,w,164), "card-white", null, catalog);
                coastalUi.Label(id+"/name", new Rect(16,y+8,w-190,36), $"{row.Name} · {row.Role}", 23, null, TextAnchor.MiddleLeft, catalog);
                coastalUi.Label(id+"/detail", new Rect(16,y+46,w-32,35), $"{row.Rarity} / Level {row.Level} / {row.Xp:0} kg / {row.Wage} coins per voyage", 16, SeaInk, TextAnchor.MiddleLeft, catalog);
                coastalUi.Label(id+"/ability", new Rect(16,y+82,w-32,44), row.Ability, 16, SeaInk, TextAnchor.MiddleLeft, catalog);
                coastalUi.Button(id+"/deploy", new Rect(w-168,y+8,152,36), row.Deployed ? "Stand down" : "Deploy", () => DeployCard(row.Id,!row.Deployed), "button-secondary-normal", row.Role != "Navigator" && (row.Deployed || report.Deployed<report.Berths), catalog,16);
                var card = CardRoster.Find(State.Roster,row.Id);
                string cost = row.Rarity == CardRarity.Gold ? "Gold" : $"Upgrade / {CardProgression.UpgradeWildcards(row.Rarity)} wildcards + {CardProgression.UpgradeCoins(row.Rarity,card.Def.TierGranted)} coins";
                bool can = row.Rarity != CardRarity.Gold && State.Wildcards[(int)card.Def.Role]>=CardProgression.UpgradeWildcards(row.Rarity) && State.Coins>=CardProgression.UpgradeCoins(row.Rarity,card.Def.TierGranted);
                coastalUi.Button(id+"/upgrade",new Rect(16,y+128,w-32,30),cost,()=>UpgradeCard(row.Id),"button-secondary-normal",can,catalog,15);
                catalogY += 180;
            }
        }
    }
}

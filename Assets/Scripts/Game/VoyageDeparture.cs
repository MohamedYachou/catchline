using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        bool departureReady;
        public void RequestDeparture()
        {
            if (CurrentMode != Mode.Harbour || State.UnsoldCatch.Count > 0) return;
            departureReady = true;
            toastUntil = 0;
        }
        void DepartureBuy(System.Func<bool> buy)
        {
            if (!departureReady || CurrentMode != Mode.Harbour) return;
            if (buy()) { SaveGame(); audio?.Play(VoyageAudio.Cue.Purchase, .6f); }
        }
        void InterfaceDeparture()
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Box("depart/shade", new Rect(0, 0, iw, ih), "", new Color(.04f, .14f, .19f, .68f));
            float w = Mathf.Min(iw - 32, compactInterface ? 960 : 990);
            float h = compactInterface ? 448 : 612;
            float x = (iw - w) / 2, y = (ih - h) / 2;
            coastalUi.ReferenceScale = 1;
            coastalUi.ReferencePanel("depart/paper", new Rect(x, y, w, h), FishReferenceStyle.PanelKind.Crew);
            coastalUi.Art("depart/anchor", new Rect(x + 25, y + 20, 42, 42), "icon-home-anchor");
            coastalUi.Label("depart/title", new Rect(x + 82, y + 15, w - 310, 42), "Ready to leave?", compactInterface ? 29 : 34, Palette.HullNavy);
            coastalUi.Label("depart/route", new Rect(x + 83, y + 57, w - 310, 30), $"Gull Harbour  ·  {GameData.Spots[SelectedSpot].Name}", 17, SeaInk);
            coastalUi.Art("depart/coin", new Rect(x + w - 164, y + 30, 30, 30), "icon-coin");
            coastalUi.Label("depart/wallet", new Rect(x + w - 125, y + 22, 98, 44), State.Coins.ToString("N0"), 25, Palette.HullNavy, TextAnchor.MiddleRight);

            float left = x + 26, top = y + (compactInterface ? 87 : 105), lw = w * .53f - 34, right = x + w * .56f, rw = w * .44f - 28;
            float fuelH = compactInterface ? 88 : 140;
            coastalUi.ReferencePanel("depart/fuel", new Rect(left, top, lw, fuelH), FishReferenceStyle.PanelKind.Goal);
            coastalUi.Art("depart/fuel/icon", new Rect(left + 15, top + 15, 32, 32), "icon-fuel");
            coastalUi.Label("depart/fuel/title", new Rect(left + 60, top + 9, lw - 220, 32), State.Hull > 0 ? "Fuel" : "Under oars", 23);
            coastalUi.Label("depart/fuel/amount", new Rect(left + lw - 160, top + 9, 142, 32), State.Hull > 0 ? State.FuelFraction.ToString("P0") : "Ready", 23, Palette.HullNavy, TextAnchor.MiddleRight);
            coastalUi.ReferenceBar("depart/fuel/bar", new Rect(left + 18, top + 48, lw - (compactInterface ? 205 : 36), 12), State.Hull > 0 ? State.FuelFraction : 1);
            int fill = State.FuelFillCost;
            string fuelDetail = State.Hull == 0 ? "No fuel needed for this boat." : $"{State.FuelCapacity:0} minute tank · return at 10%";
            coastalUi.Label("depart/fuel/detail", new Rect(left + 18, top + 64, lw - 197, compactInterface ? 21 : 54), fuelDetail, 15, SeaInk);
            IButton("depart/refuel", new Rect(left + lw - 174, top + (compactInterface ? 43 : 70), 156, 54), State.Hull == 0 ? "Oars ready" : fill > 0 ? $"Fill · {fill} coins" : "Tank full", () => DepartureBuy(State.BuyFuel), false, State.Hull > 0 && fill > 0 && State.Coins >= fill);

            float by = top + fuelH + 16;
            coastalUi.Label("depart/bait/title", new Rect(left + 3, by - 4, lw - 6, 40), "Bait aboard", 23);
            float row = compactInterface ? 56 : 66;
            void BaitRow(string id, string name, string icon, int count, int size, int cost, System.Func<bool> buy, float ry)
            {
                coastalUi.Art(id + "/icon", new Rect(left + 5, ry + 7, 34, 34), icon);
                coastalUi.Label(id + "/name", new Rect(left + 52, ry, lw - 235, 28), name, 19);
                coastalUi.Label(id + "/count", new Rect(left + 52, ry + 25, lw - 235, 25), $"{count} hooks aboard", 15, SeaInk);
                IButton(id + "/buy", new Rect(left + lw - 174, ry, 174, 54), $"+{size} · {cost} coins", () => DepartureBuy(buy), false, State.Coins >= cost);
            }
            BaitRow("depart/worms", "Worms", "icon-bait-worm", State.Bait, GameData.BaitPackSize, GameData.BaitPackCost, () => State.BuyBait(), by + 40);
            BaitRow("depart/squid", "Squid", "icon-squid", State.Squid, GameData.SquidPackSize, GameData.SquidPackCost, () => State.BuySquid(), by + 40 + row);
            if (!compactInterface) coastalUi.Label("depart/scraps", new Rect(left + 4, by + 37 + row * 2, lw - 8, 27), "Free scraps are always aboard.", 15, SeaInk);

            coastalUi.Label("depart/crew/title", new Rect(right, top, rw, 32), $"Crew · {State.CrewCount + 1} aboard", 23);
            float cy = top + (compactInterface ? 32 : 38), crewRow = compactInterface ? 40 : 59;
            var people = People.ToList();
            for (int i = 0; i < people.Count; i++)
            {
                var p = people[i]; bool captain = p == Captain;
                string portrait = captain ? "captain" : p.Contract.Role == CrewRole.Fisherman ? "fisherman" : "deckhand";
                coastalUi.ReferencePortrait($"depart/crew/{i}/portrait", new Rect(right, cy, crewRow - 5, crewRow - 3), portrait);
                coastalUi.Label($"depart/crew/{i}/name", new Rect(right + crewRow + 6, cy - 1, rw - crewRow - 8, 27), captain ? "You · Captain" : $"{p.Name} · {p.Contract.RoleName}", 18);
                coastalUi.Label($"depart/crew/{i}/detail", new Rect(right + crewRow + 6, cy + 24, rw - crewRow - 8, 20), captain ? "At the helm" : $"{p.Contract.VoyagesLeft} voyages on contract", 13, SeaInk);
                cy += crewRow;
            }
            float ny = compactInterface ? cy + 4 : Mathf.Max(cy + 8, y + h - 152);
            coastalUi.Art("depart/nets/icon", new Rect(right, ny + 3, 34, 34), "icon-net");
            coastalUi.Label("depart/nets/title", new Rect(right + 48, ny - 3, rw - 48, 38), State.Hull == 0 ? "Nets" : $"Nets · {State.NetCapacityKg:0}kg each", 18);
            coastalUi.Label("depart/nets/detail", new Rect(right + 48, ny + 28, rw - 48, compactInterface ? 28 : 44), State.Hull == 0 ? "Rod fishing · no net fitted" : (DeepNetSelected ? $"Deep { (State.DeepNetUses.Count > 0 ? State.DeepNetUses[0] : 0)}/3 uses · {State.DeepNetUses.Count} deep · {State.NetInventory} shallow" : $"Shallow selected · {State.NetInventory} shallow · {State.DeepNetUses.Count} deep"), 15, SeaInk);

            float fy = y + h - 77;
            string blocker = SailBlocker();
            coastalUi.Label("depart/status", new Rect(left, fy - 25, w - 52, 24), blocker ?? (State.Hull > 0 && State.ActiveNetStock == 0 ? "No nets aboard · rods and bait are ready." : "Supplies checked. Your next catch is waiting."), 15, blocker != null ? Palette.Hex("B14535") : SeaInk);
            IButton("depart/back", new Rect(left, fy + 5, 172, 54), "Back to port", () => departureReady = false, false);
            IButton("depart/go", new Rect(x + w - 260, fy + 5, 234, 54), "Let's go", () => { if (departureReady) SetSail(); }, true, blocker == null);
        }
    }
}

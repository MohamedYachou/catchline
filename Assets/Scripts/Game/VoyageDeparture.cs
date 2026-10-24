using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        bool departureReady;
        bool departureCrewWarning;

        public bool ConfirmDeparture()
        {
            if (!departureReady || SailBlocker() != null) return false;
            if (ExcessFishermen > 0) { departureCrewWarning = true; return false; }
            SetSail(); return true;
        }
        public void RequestDeparture()
        {
            if (CurrentMode != Mode.Harbour || State.UnsoldCatch.Count > 0) return;
            departureCrewWarning = false;
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
            coastalUi.Scrim("depart/shade", null, .8f);
            bool phone = compactInterface;
            float w = Mathf.Min(iw - 32, 960), h = Mathf.Min(ih - 24, phone ? 456 : 540);
            var panel = new Rect((iw - w) / 2, (ih - h) / 2, w, h);
            var slab = coastalUi.Slab("depart/paper", panel, "Ready to leave?", true);
            float pill = phone ? 130 : 160;
            coastalUi.PricePill("depart/wallet", new Rect(w - pill - 16, 6, pill, Skin.HeaderBand - 8), State.Coins, true, slab);
            float pad = Skin.SlabPad + 8, y = Skin.HeaderBand + (phone ? 6 : 12);
            coastalUi.Icon("depart/anchor", new Rect(pad, y + 2, 32, 32), "v2-icon-anchor", slab, null, "icon-home-anchor");
            coastalUi.Text("depart/route", new Rect(pad + 42, y, w - pad * 2 - 42, 36), $"Gull Harbour  ›  {GameData.Spots[SelectedSpot].Name}", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, slab);
            y += phone ? 42 : 52;

            // Left column: fuel and bait.
            float lw = w * .54f - pad, rx = w * .56f + 8, rw = w - rx - pad;
            float tileH = phone ? 52 : 70, bw = phone ? 150 : 176;
            int fill = State.FuelFillCost;
            if (State.Hull > 0)
            {
                coastalUi.StatTile("depart/fuel", new Rect(pad, y, lw - bw - 10, tileH), "v2-icon-fuel", "Fuel", $"{State.FuelFraction * 100:0}%", State.FuelFraction, State.FuelFraction < .2f ? Skin.Bar.Bad : Skin.Bar.Good, slab, "icon-fuel");
                coastalUi.Secondary("depart/refuel", new Rect(pad + lw - bw, y + (tileH - 48) / 2, bw, 48), fill > 0 ? $"Fill · {fill}" : "Tank full",
                    () => DepartureBuy(State.BuyFuel), fill > 0 ? "v2-icon-coin" : null, fill > 0 && State.Coins >= fill, slab);
            }
            else coastalUi.StatTile("depart/fuel", new Rect(pad, y, lw, tileH), "v2-icon-fuel", "Under oars", "No fuel needed", null, Skin.Bar.Good, slab, "icon-fuel");
            float by = y + tileH + (phone ? 8 : 14);
            coastalUi.Text("depart/bait/title", new Rect(pad, by, lw, phone ? 24 : 30), "Bait aboard", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, slab);
            by += phone ? 26 : 34;
            float row = phone ? 52 : 62;
            void BaitRow(string id, string name, string icon, string fallback, int count, int size, int cost, System.Func<bool> buy, float ry)
            {
                var card = coastalUi.Card(id, new Rect(pad, ry, lw, row - 6), Skin.Card.Soft, slab);
                float s = row - 18;
                coastalUi.Icon(id + "/icon", new Rect(10, 6, s, s), icon, card, null, fallback);
                coastalUi.Text(id + "/name", new Rect(s + 20, 2, lw - s - bw - 40, (row - 6) * .52f), name, Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, card);
                coastalUi.Text(id + "/count", new Rect(s + 20, (row - 6) * .52f, lw - s - bw - 40, (row - 6) * .44f), $"{count} hooks aboard", Skin.Type.Small, Skin.InkSoft, TextAnchor.UpperLeft, card);
                coastalUi.Secondary(id + "/buy", new Rect(lw - bw - 6, 4, bw, row - 14), $"+{size} · {cost}", () => DepartureBuy(buy), "v2-icon-coin", State.Coins >= cost, card);
            }
            BaitRow("depart/worms", "Worms", "v2-icon-worms", "icon-bait-worm", State.Bait, GameData.BaitPackSize, GameData.BaitPackCost, () => State.BuyBait(), by);
            BaitRow("depart/squid", "Squid", "v2-icon-squid", "icon-squid", State.Squid, GameData.SquidPackSize, GameData.SquidPackCost, () => State.BuySquid(), by + row);
            if (!phone) coastalUi.Text("depart/scraps", new Rect(pad, by + row * 2, lw, 26), "Free scraps are always aboard.", Skin.Type.Small, Skin.Teal, TextAnchor.MiddleLeft, slab);

            // Right column: who sails, and the net loadout.
            var people = People.ToList();
            coastalUi.Text("depart/crew/title", new Rect(rx, y - 2, rw, phone ? 24 : 30), $"Crew · {people.Count} aboard", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, slab);
            float cy = y + (phone ? 26 : 34), crewRow = phone ? 44 : 60;
            float footer = h - (phone ? 56 : 64) - 18 - (phone ? 22 : 28);
            float netsH = phone ? 46 : 58;
            int shown = Mathf.Max(1, Mathf.Min(people.Count, Mathf.FloorToInt((footer - netsH - 8 - cy) / crewRow)));
            for (int i = 0; i < shown; i++)
            {
                var p = people[i]; bool captain = p == Captain;
                coastalUi.CrewCard($"depart/crew/{i}", new Rect(rx, cy, rw, crewRow - 6), PortraitKey(p, Captain), captain ? "You · Captain" : $"{p.Name} · {RoleTitle(p, Captain)}",
                    null, captain ? "At the helm" : p.Contract.VoyagesLeft == int.MaxValue ? "Deployed" : $"{p.Contract.VoyagesLeft} voyages on contract", Speciality(p, Captain), null, false, null, slab);
                cy += crewRow;
            }
            float ny = footer - netsH - 4;
            coastalUi.Icon("depart/nets/icon", new Rect(rx, ny + 4, 36, 36), "v2-icon-net", slab, null, "icon-net");
            coastalUi.Text("depart/nets/title", new Rect(rx + 46, ny, rw - 46, netsH * .46f), State.Hull == 0 ? "Nets" : $"Nets · {State.NetCapacityKg:0} kg each", Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, slab);
            coastalUi.Text("depart/nets/detail", new Rect(rx + 46, ny + netsH * .48f, rw - 46, netsH * .52f), State.Hull == 0 ? "Rod fishing · no net fitted" : (DeepNetSelected ? $"Deep {(State.DeepNetUses.Count > 0 ? State.DeepNetUses[0] : 0)}/3 uses · {State.DeepNetUses.Count} deep · {State.NetInventory} shallow" : $"Shallow selected · {State.NetInventory} shallow · {State.DeepNetUses.Count} deep"), Skin.Type.Small, Skin.InkSoft, TextAnchor.UpperLeft, slab);

            string blocker = SailBlocker();
            coastalUi.Text("depart/status", new Rect(pad, footer, w - pad * 2, phone ? 22 : 28), blocker ?? (State.Hull > 0 && State.ActiveNetStock == 0 ? "No nets aboard · rods and bait are ready." : SecondNetActive ? "Loadout: 1 rod / 2 nets. Supplies checked." : "Supplies checked. Your next catch is waiting."),
                Skin.Type.Small, blocker != null ? Skin.BadInk : Skin.Teal, TextAnchor.MiddleLeft, slab);
            float bh = phone ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight, fy = h - bh - 16;
            coastalUi.Secondary("depart/back", new Rect(pad, fy, phone ? 180 : 220, bh), "Back to port", () => { departureReady = false; MenuSound(); }, "v2-icon-back", true, slab);
            coastalUi.Primary("depart/go", new Rect(w - pad - (phone ? 240 : 300), fy, phone ? 240 : 300, bh), "Let's go", () => ConfirmDeparture(), "v2-icon-anchor", blocker == null, slab);
            if (departureCrewWarning) InterfaceFisherWarning();
        }
    }
}

using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        bool netOrdersOpen;

        // Kept separate from Codex2's reference HUD. Its lead chooses the hook/placement.
        void InterfaceNetOrders()
        {
            if (State.Hull == 0) return;
            var access = NetAccess;
            var anchor = Boat.TransformPoint(Grid.GetLocal(access) + new Vector3(.5f, .8f, 0));
            var view = Cam.WorldToViewportPoint(anchor);
            bool enabled = CanCaptainNet && (Net == NetState.Ready || Net == NetState.Stowed && (NetBasketBlocked || State.ActiveNetStock > 0));
            string status = NetUnloadRig == 0 ? "Unloading catch" : Net switch {
                NetState.Soaking => $"{NetRemaining:0}s", NetState.Ready => $"Haul {NetCatchKg:0.0} kg", NetState.Setting => "Setting…",
                NetState.Hauling => "Winching…", _ => HoldFull ? "Hold full" : NetBasketBlocked ? "Unload catch" : State.ActiveNetStock == 0 ? "No nets · buy supplies" : DeepNetSelected ? $"Deep {State.DeepNetUses[0]}/3 · {State.ActiveNetStock - 1} spare" : $"Shallow · {State.ActiveNetStock} aboard" };
            // One speech bubble on the net: icon and status; tapping it is the captain's net action.
            Block(coastalUi.Bubble("net", new Vector2(view.x * iw, (1 - view.y) * ih), "v2-icon-net", status, Net == NetState.Ready,
                enabled ? () => CaptainNetAction() : (System.Action)null, "icon-net"));
            if (IsNetFisher)
            {
                var hands = State.Crew.Where(c => c.Role == CrewRole.Deckhand).ToList();
                if (!IsTier5) IButton("net/orders", FishingFooter(1), "Crew duties", () => { netOrdersOpen = true; PrepOrdersOpen = false; toastUntil = 0; }, false, hands.Count > 0);
            }
            InterfaceSecondNet();
            if (NetGameActive) InterfaceNetHaulGame();
            InterfacePrepOrders();
            if (netOrdersOpen && IsTier5) { netOrdersOpen=false; OpenManagement(); managementTab=2; return; }
            if (!netOrdersOpen || !IsNetFisher) return;
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Box("orders/shade", new Rect(0, 0, iw, ih), "chip-dark", new Color(1, 1, 1, .7f));
            var crew = State.Crew.Where(c => c.Role == CrewRole.Deckhand).ToList();
            float height = 174 + crew.Count * 70 + (IsPrepFisher ? 60 : 0);
            var panel = new Rect((iw - (IsPrepFisher ? 550 : 450)) / 2, (ih - height) / 2, IsPrepFisher ? 550 : 450, height);
            coastalUi.Box("orders/panel", panel);
            coastalUi.Label("orders/title", new Rect(panel.x + 20, panel.y + 8, 335, 40), "Deckhand duties", 25);
            IButton("net/orders/close", new Rect(panel.xMax - 70, panel.y + 9, 54, 42), "X", () => netOrdersOpen = false, false);
            coastalUi.Label("orders/help", new Rect(panel.x + 20, panel.y + 53, 410, 48), "Fish: carry rod catches and bait.\nNets: net work, then fish/bait during soak.", 16, SeaInk);
            for (int i = 0; i < crew.Count; i++)
            {
                var c = crew[i]; float y = panel.y + 108 + i * 70;
                var person = People.FirstOrDefault(h => h.Contract == c);
                int rig = c.WorkPreference == DeckhandWork.Nets ? AssignedNet(person) : -1;
                coastalUi.Label("orders/" + i + "/name", new Rect(panel.x + 20, y, 166, 52),
                    rig >= 0 ? c.Name + " / Net " + (rig + 1) : c.Name, 18);
                IButton("net/orders/" + i + "/fish", new Rect(panel.x + 190, y, 108, 50), "Fish", () => SetDeckhandWork(c, DeckhandWork.Fish), c.WorkPreference == DeckhandWork.Fish);
                IButton("net/orders/" + i + "/nets", new Rect(panel.x + 308, y, 122, 50), "Nets", () => SetDeckhandWork(c, DeckhandWork.Nets), c.WorkPreference == DeckhandWork.Nets);
                if (IsPrepFisher) IButton("net/orders/" + i + "/prep", new Rect(panel.x + 440, y, 90, 50), "Prep", () => SetDeckhandWork(c, DeckhandWork.Prep), c.WorkPreference == DeckhandWork.Prep, c.WorkPreference == DeckhandWork.Prep || crew.Count(h => h.WorkPreference == DeckhandWork.Prep) < 2);
            }
            if (IsPrepFisher)
            {
                float y = panel.yMax - 118;
                coastalUi.Label("orders/prep/priority-label", new Rect(panel.x + 20, y, 104, 46), "Prep order:", 15, SeaInk);
                IButton("net/orders/prep-priority", new Rect(panel.x + 128, y, 208, 46),
                    State.PrepOrders.ChumFirst ? "Make chum first" : "Sort fish first", ChangePrepPriority, false);
                coastalUi.Label("orders/prep/status", new Rect(panel.x + 344, y, 186, 46),
                    $"{PrepWorkersActive} of 2 deckhands working", 14, SeaInk, TextAnchor.MiddleCenter);
            }
            coastalUi.Label("orders/footer", new Rect(panel.x + 20, panel.yMax - 60, 410, 50), "80% safe. Deep failure: catch + one use lost.\nShallow tear: net lost. Captain: timing decides.", 15, SeaInk);
        }

        Rect NetGamePanel => new Rect((iw - 450) / 2, ih - 234, 450, 216);
        Rect NetGameCancelRect => new Rect(NetGamePanel.x + 312, NetGamePanel.y + 164, 122, 40);

        void InterfaceNetHaulGame()
        {
            var panel = NetGamePanel;
            float width = panel.width;
            Block(panel); coastalUi.Box("net/haul/panel", panel);
            coastalUi.Label("net/haul/title", new Rect(panel.x + 18, panel.y + 8, width - 36, 30), NetGameSetting ? "Spread the net" : "Work the net", 24);
            string help = NetGameSetting ? "Tap in the green · 3 clean casts" : NetGameTension >= NetHaulRedTension ? "Too tight! Wait — red loses progress." : "Tap to pull · stay close to red, then ease";
            coastalUi.Label("net/haul/help", new Rect(panel.x + 18, panel.y + 42, width - 36, 28), help, 16, SeaInk);
            var meter = new Rect(panel.x + 18, panel.y + 80, width - 36, 16);
            coastalUi.Bar("net/haul/tension", meter, NetGameSetting ? NetGamePhase : NetGameTension, !NetGameSetting && NetGameTension >= NetHaulRedTension);
            float lo = NetGameSetting ? .35f : .65f, hi = NetGameSetting ? .65f : .84f;
            coastalUi.Box("net/haul/sweet", new Rect(meter.x + meter.width * lo, meter.y, meter.width * (hi - lo), meter.height), "", new Color(.3f, .75f, .49f, .8f), blocks: false);
            if (!NetGameSetting) coastalUi.Box("net/haul/red", new Rect(meter.x + meter.width * .85f, meter.y, meter.width * .15f, meter.height), "", new Color(.88f, .28f, .2f, .9f), blocks: false);
            float cursor = NetGameSetting ? NetGamePhase : NetGameTension;
            coastalUi.Box("net/haul/cursor", new Rect(meter.x + meter.width * cursor - 2, meter.y - 3, 4, meter.height + 6), "", SeaInk, blocks: false);
            coastalUi.Label("net/haul/progresslabel", new Rect(panel.x + 18, panel.y + 102, 145, 22), NetGameSetting ? $"Spread {NetGameProgress * 3:0}/3" : $"Net aboard {NetGameProgress * 100:0}%", 14, SeaInk);
            coastalUi.Bar("net/haul/progress", new Rect(panel.x + 160, panel.y + 108, width - 178, 8), NetGameProgress);
            coastalUi.Label("net/haul/risk", new Rect(panel.x + 18, panel.y + 127, width - 36, 28), NetGameDamage > 0 ? "Fraying — one more mistake loses this haul!" : DeepNetSelected ? "2 mistakes lose catch + one use · other uses kept" : $"2 mistakes tear it · {State.NetInventory} shallow nets", 15, NetGameDamage > 0 ? Palette.Accent : SeaInk);
            // Raw press handling gives exactly one pull. UI release never repeats it.
            IButton("net/haul/tap", new Rect(panel.x + 16, panel.y + 164, 280, 40), "Tap screen or press Space", () => { }, true);
            IButton("net/haul/cancel", NetGameCancelRect, "Leave net", CancelNetHaulGame, false);
        }
    }
}

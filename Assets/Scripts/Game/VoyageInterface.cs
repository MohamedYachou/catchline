using System;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        CoastalCanvas coastalUi;
        int interfaceWidth, interfaceHeight;
        float interfaceTextScale;
        float iw, ih;
        bool compactInterface => ih < 600;
        Color SeaInk => Palette.Hex("3E626D");
        public void PrepareInterface(int width, int height, float textScale = 0)
        {
            interfaceWidth = width; interfaceHeight = height;
            interfaceTextScale = textScale;
            RefreshInterface();
        }
        public bool InvokeInterface(string control) => coastalUi != null && coastalUi.Invoke(control);
        void RefreshInterface()
        {
            if (coastalUi == null) coastalUi = CoastalCanvas.Create(transform, Cam);
            if (MenuOpen || confirmHeadHome || SimTime < refitUntil) { coastalUi.Hide(); return; }
            int width = interfaceWidth > 0 ? interfaceWidth : Screen.width;
            int height = interfaceHeight > 0 ? interfaceHeight : Screen.height;
            coastalUi.Begin(width, height, interfaceTextScale > 0 ? interfaceTextScale : UiScales[UiScaleIndex], interfaceWidth > 0 ? new Rect(0, 0, width, height) : Screen.safeArea);
            iw = coastalUi.Width; ih = coastalUi.Height;
            hudRects.Clear();
            if (departureReady && CurrentMode == Mode.Harbour) InterfaceDeparture();
            else if (CurrentMode == Mode.Harbour) InterfaceHarbour();
            else if (CurrentMode == Mode.Fishing && ManagementOpen) InterfaceManagementPages();
            else if (CurrentMode == Mode.Fishing) InterfaceFishing();
            else InterfaceTravel();
            if (!departureReady && toast != null && SimTime < toastUntil)
            {
                if (CurrentMode == Mode.Fishing && !ManagementOpen) coastalUi.Toast("toast", toast, null, Edge, HudGapLeft, HudGapRight);
                else coastalUi.Toast("toast", toast, null, 18);
            }
            InterfaceCrewBait();
            if (!ManagementOpen) { InterfaceTier5Operations(); ManagementEntry(); }
            coastalUi.End();
        }
        void Block(Rect rect) => hudRects.Add(rect);
        void IButton(string id, Rect r, string label, Action action, bool primary = true, bool enabled = true)
        {
            if (compactInterface) r.height = Mathf.Max(r.height, 54);
            Block(r);
            coastalUi.Button(id, r, label, () => { action(); audio?.Play(VoyageAudio.Cue.Select, .45f); },
                primary ? "button-primary-normal" : "button-secondary-normal", enabled);
        }
        void InterfaceCoins()
        {
            var c = new Rect(iw - 230, 18, 150, 46);
            coastalUi.Box("wallet", c, "chip-dark"); Block(c);
            coastalUi.Art("wallet/icon", new Rect(c.x + 12, c.y + 10, 24, 24), "icon-coin");
            coastalUi.Label("wallet/coins", new Rect(c.x + 44, c.y, 92, 42), State.Coins.ToString("N0"), 21, Palette.Cream);
            IButton("pause", new Rect(iw - 70, 18, 54, 46), "II", () => paused = true, false);
        }
        void InterfaceFishing()
        {
            InterfaceVoyageHud();
            foreach (var rod in Rods.Where(r => r.Unlocked && CanCommandRod(r)))
                InterfaceBubble("rod/" + Rods.IndexOf(rod), Boat.TransformPoint(rod.TipLocal + Vector3.up * .25f),
                    rod.State == RodState.Bite ? "Bite!" : rod.InWater ? "Watch" : "Fish", "icon-rod", () => CommandRod(rod), rod.State == RodState.Bite);
            for (int i = 0; i < OnDeck.Count; i++)
            {
                var fish = OnDeck[i];
                if (!fish.FromNetBasket && CanCarry(fish)) InterfaceBubble("carry/" + i, fish.Root.position + Vector3.up * .35f, "Carry", "icon-fish", () => CommandCarry(fish));
            }
            if (UsesDeckGraph) InterfaceDeckBubbles();
            InterfaceFishingAction();
            InterfaceCatchRewards();
            // Windows owns net/orders implementation; draw last so its modal stays on top.
            InterfaceNetOrders();
        }
        void InterfaceBubble(string id, Vector3 worldPosition, string caption, string icon, Action action, bool hot = false)
        {
            Vector3 view = Cam.WorldToViewportPoint(worldPosition);
            if (view.z <= 0) return;
            string art = icon == "icon-rod" ? "v2-icon-rod" : icon == "icon-fish" ? "v2-icon-fish" : icon;
            Block(coastalUi.Bubble(id, new Vector2(view.x * iw, (1 - view.y) * ih), art, caption, hot, action, icon));
        }
        void InterfaceFishingAction()
        {
            float width = Mathf.Min(390, iw - 530);
            if (width < 270) width = 270;
            float x = (iw - width) / 2;
            if(IsNetFisher)
            {
                // Keep the fishing task clear of the bottom-right action cluster.
                float right=iw-420,left=Mathf.Min(276,Mathf.Max(16,right-270));
                width=Mathf.Min(390,Mathf.Max(270,right-left));x=left+Mathf.Max(0,(right-left-width)/2);
            }
            var rod = MinigameRod;
            if (AwaitingCast)
            {
                var r = new Rect(x, ih - 122, width, 104);
                coastalUi.Box("cast/choice", r); Block(r);
                coastalUi.Label("cast/title", new Rect(x + 14, r.y + 7, width - 28, 28), "Ready for another?", 21, null, TextAnchor.MiddleCenter);
                IButton("cast/again", new Rect(x + 12, r.y + 43, width * .56f - 16, 48), HoldFull ? "Cooler full" : "Throw again", () => ThrowAgain(), true, !HoldFull);
                IButton("cast/leave", new Rect(x + width * .56f + 4, r.y + 43, width * .44f - 16, 48), "Leave rod", LeaveFishing, false);
                return;
            }
            if (rod == null)
            {
                string hint = ShowTips ? VoyageHint() : null;
                // Guidance sits top centre between the status slab and the crew rail; a toast takes its place.
                if (hint != null && (toast == null || SimTime >= toastUntil)) coastalUi.Toast("guide", hint, "v2-icon-tick", Edge, HudGapLeft, HudGapRight);
                return;
            }
            float height = compactInterface ? 146 : 172;
            var box = new Rect(x, ih - height - 18, width, height);
            coastalUi.Box("strike", box); Block(box);
            coastalUi.Art("strike/sea", new Rect(x + 8, box.y + 43, width - 16, height - 52), "strike-water");
            string title = rod.State == RodState.Bite ? "The bobber is under!" : rod.State == RodState.Waiting ? rod.Nibbling ? "A nibble… wait for it" : "Watch the bobber" : rod.State == RodState.Reeling ? "You've hooked one!" : "Casting your line…";
            coastalUi.Label("strike/title", new Rect(x + 12, box.y + 6, width - 24, 32), title, 21, null, TextAnchor.MiddleCenter);
            float cy = box.y + height * .60f;
            coastalUi.Art("strike/fish", new Rect(x + width * .25f + Mathf.Sin(SimTime) * 18, cy, 76, 32), "fish-shadow");
            coastalUi.Art("strike/bobber", new Rect(x + width / 2 - 25, cy - 24, 50, 50), rod.State == RodState.Bite ? "bobber-underwater" : rod.Nibbling ? "bobber-dipped" : "bobber-floating");
            if (rod.State == RodState.Bite)
            {
                IButton("strike/tap", new Rect(x + width - 104, cy - 24, 88, 48), "Strike!", StrikeTap);
                coastalUi.Bar("strike/time", new Rect(x + 22, box.yMax - 23, width - 44, 9), 1 - rod.BiteProgress, true);
            }
            else if (rod.State == RodState.Reeling) coastalUi.Bar("strike/progress", new Rect(x + 22, box.yMax - 23, width - 44, 9), rod.ReelProgress);
            else coastalUi.Label("strike/help", new Rect(x + 12, box.yMax - 30, width - 24, 24), "Wait for the dip · then tap or Space", 14, Palette.Cream, TextAnchor.MiddleCenter);
        }
        void InterfaceTravel()
        {
            InterfaceCoins();
            var r = new Rect((iw - 440) / 2, 22, 440, 110);
            coastalUi.Box("journey", r); Block(r);
            coastalUi.Art("journey/icon", new Rect(r.x + 18, r.y + 18, 52, 52), "icon-home-anchor");
            coastalUi.Label("journey/title", new Rect(r.x + 86, r.y + 10, 334, 34), CurrentMode == Mode.SailingHome ? "Home to Gull Harbour" : GameData.Spots[ActiveSpot].Name, 24);
            coastalUi.Label("journey/stage", new Rect(r.x + 86, r.y + 47, 334, 25), TravelStage, 16, SeaInk);
            coastalUi.Bar("journey/progress", new Rect(r.x + 20, r.y + 84, 400, 10), TravelProgress);
        }
    }
}

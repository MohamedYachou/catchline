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
        public void PrepareInterface(int width, int height, float textScale = 0, float density = 0)
        {
            interfaceWidth = width; interfaceHeight = height; interfaceDensity = density;
            interfaceTextScale = textScale;
            RefreshInterface();
        }
        public bool InvokeInterface(string control) => coastalUi != null && coastalUi.Invoke(control);
        float interfaceDensity;
        void RefreshInterface()
        {
            if (coastalUi == null) coastalUi = CoastalCanvas.Create(transform, Cam);
            int width = interfaceWidth > 0 ? interfaceWidth : Screen.width;
            int height = interfaceHeight > 0 ? interfaceHeight : Screen.height;
            coastalUi.Begin(width, height, interfaceTextScale > 0 ? interfaceTextScale : UiScales[UiScaleIndex], interfaceWidth > 0 ? new Rect(0, 0, width, height) : Screen.safeArea,
                interfaceDensity > 0 ? interfaceDensity : Application.isMobilePlatform && Screen.dpi > 0 ? Mathf.Max(1, Screen.dpi / 160f) : 1);
            iw = coastalUi.Width; ih = coastalUi.Height;
            hudRects.Clear();
            foreach (Transform t in coastalUi.Root)
            {
                var group = t.GetComponent<CanvasGroup>();
                if (group != null) { group.alpha = 1; group.interactable = group.blocksRaycasts = true; }
            }
            if (MenuOpen || confirmHeadHome || SimTime < refitUntil) { InterfaceMenus(); coastalUi.End(); return; }
            if (IntroActive && !MenuOpen) { InterfaceIntro(); coastalUi.End(); return; }
            InterfaceCastFx(); if (RodViewActive) { InterfaceRodView(); coastalUi.End(); return; }
            if (CageViewActive) { InterfaceCageView(); coastalUi.End(); return; }
            if (GutViewActive) { InterfaceGutView(); coastalUi.End(); return; }
            if (RepairViewActive) { InterfaceRepairView(); coastalUi.End(); return; }
            if (NetViewActive) { InterfaceNetView(); coastalUi.End(); return; }
            if (InterfaceRestaurant()) { coastalUi.End(); return; }
            if (departureReady && CurrentMode == Mode.Harbour) InterfaceDeparture();
            else if (CurrentMode == Mode.Harbour) InterfaceHarbour();
            else if (CurrentMode == Mode.Fishing && ManagementOpen) InterfaceManagementPages();
            else if (CurrentMode == Mode.Fishing) InterfaceFishing();
            else { InterfaceTravel(); if (UsesDeckGraph) InterfaceDeckBubbles(); InterfaceTripChart(); }
            if (CurrentMode == Mode.Fishing && !ManagementOpen || CurrentMode == Mode.Harbour && !panelOpen && !departureReady)
                InterfaceV3(InterfaceHudOverlays);
            else InterfaceHudOverlays();
            coastalUi.End();
        }
        void InterfaceHudOverlays()
        {
            InterfaceSeaGrounds();
            InterfaceCardOverlays();
            if (!departureReady && toast != null && SimTime < toastUntil)
            {
                if (CurrentMode == Mode.Fishing && !ManagementOpen) coastalUi.Toast("toast", toast, null, Edge, HudGapLeft, HudGapRight);
                else coastalUi.Toast("toast", toast, null, CurrentMode == Mode.Harbour ? ih - Edge - TabBarHeight - 76 : 18);
            }
            InterfaceCrewBait();
            if (!ManagementOpen) { InterfaceTier5Operations(); InterfacePotLine(); ManagementEntry(); }
            InterfaceCoinFx();
            InterfaceTutorial();
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
            float h = compactInterface ? 48 : 56, pill = compactInterface ? 150 : 190;
            var c = new Rect(iw - Edge - h - 10 - pill, Edge, pill, h);
            coastalUi.PricePill("wallet", c, State.Coins); Block(c);
            var p = new Rect(iw - Edge - h, Edge, h, h);
            coastalUi.IconButton("pause", p, "v2-icon-menu", null, () => paused = true, null, "icon-menu"); Block(p);
        }
        void InterfaceFishing() => InterfaceV3(InterfaceFishingV3);
        void InterfaceFishingV3()
        {
            InterfaceVoyageHud();
            // On a phone a row of identical "Fish" bubbles hides the deck: only the first idle rod keeps its word.
            bool labelled = false;
            foreach (var rod in Rods.Where(r => r.Unlocked && CanCommandRod(r)))
            {
                bool idle = rod.State != RodState.Bite && !rod.InWater;
                string caption = rod.State == RodState.Bite ? "Bite!" : rod.InWater ? "Watch" : compactInterface && labelled ? "" : "Fish";
                labelled |= idle;
                InterfaceBubble("rod/" + Rods.IndexOf(rod), Boat.TransformPoint(rod.TipLocal + Vector3.up * .25f), caption, "icon-rod", () => CommandRod(rod), rod.State == RodState.Bite);
            }
            for (int i = 0; i < OnDeck.Count; i++)
            {
                var fish = OnDeck[i];
                if (!fish.FromNetBasket && CanCarry(fish)) InterfaceBubble("carry/" + i, fish.Root.position + Vector3.up * .35f, "Carry", "icon-fish", () => CommandCarry(fish));
            }
            if (UsesDeckGraph) InterfaceDeckBubbles();
            InterfaceFishingAction();
            InterfaceCatchRewards();
            if (UsesDeckGraph) InterfaceSortDecision();
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
        // The rod task floats in the open water above the bottom action row, between the ground slab and the crew rail.
        Rect FishingActionRect(float height)
        {
            float left = HudGapLeft, right = HudGapRight;
            float width = Mathf.Clamp(right - left, 280, 420);
            float bottom = ih - Edge - HudButtonHeight - 12;
            return new Rect(left + Mathf.Max(0, (right - left - width) / 2), bottom - height, width, height);
        }
        void InterfaceFishingAction()
        {
            if (RodViewActive) return;
            var rod = MinigameRod;
            if (AwaitingCast)
            {
                var r = FishingActionRect(compactInterface ? 112 : 128);
                var slab = coastalUi.Slab("cast/choice", r, null, true); Block(r);
                coastalUi.Text("cast/title", new Rect(16, 8, r.width - 32, 34), "Ready for another?", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, slab);
                float bh = compactInterface ? 48 : 56, by = r.height - bh - 14, half = (r.width - 40) / 2;
                coastalUi.Primary("cast/again", new Rect(16, by, half, bh), HoldFull ? "Cooler full" : "Throw again", () => { ThrowAgain(); MenuSound(); }, null, !HoldFull, slab);
                coastalUi.Secondary("cast/leave", new Rect(24 + half, by, half, bh), "Leave rod", () => { LeaveFishing(); MenuSound(); }, null, true, slab);
                return;
            }
            if (rod == null)
            {
                string hint = ShowTips ? VoyageHint() : null;
                // Guidance sits top centre between the status slab and the crew rail; a toast takes its place.
                if (hint != null && (toast == null || SimTime >= toastUntil)) coastalUi.Toast("guide", hint, "v2-icon-tick", Edge, HudGapLeft, HudGapRight);
                return;
            }
            // Captain casts are presented by the full-screen rod view. No sprite strike slab.
        }
        void InterfaceTravel()
        {
            InterfaceV3(InterfaceTravelV3);
        }
        void InterfaceTravelV3()
        {
            InterfaceCoins();
            float h = compactInterface ? 84 : 100, w = Mathf.Min(480, iw - Edge * 2 - (compactInterface ? 240 : 300) * 2);
            var r = new Rect((iw - w) / 2, Edge, w, h);
            var slab = coastalUi.Slab("journey", r, null, true); Block(r); journeySlab = slab;
            bool home = CurrentMode == Mode.SailingHome;
            float s = h - 46;
            coastalUi.Icon("journey/icon", new Rect(16, 12, s, s), home ? "v2-icon-home" : "v2-icon-anchor", slab, null, "icon-home-anchor");
            coastalUi.Text("journey/title", new Rect(s + 28, 8, w - s - 44, h * .36f), home ? "Home to Gull Harbour" : GameData.Spots[ActiveSpot].Name, Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, slab);
            coastalUi.Text("journey/stage", new Rect(s + 28, 8 + h * .36f, w - s - 44, h * .26f), TravelStage, Skin.Type.Small, Skin.Teal, TextAnchor.UpperLeft, slab);
            coastalUi.ProgressBar("journey/progress", new Rect(16, h - 28, w - 32, 14), TravelProgress, Skin.Bar.Teal, slab);
            if (Leg != TripLeg.None)
            {
                var fast = new Rect(r.xMax - 168, r.yMax + 8, 168, compactInterface ? 40 : 48);
                coastalUi.Secondary("journey/fast", fast, TripFast ? "Normal speed" : "Faster", () => TripFast = !TripFast); Block(fast);
            }
            InterfaceRadio(); // restaurant day: Mira's notebook, calls and the prep on deck
        }
    }
}

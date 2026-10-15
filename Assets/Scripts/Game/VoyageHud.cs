using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Catchline.Game
{
    // Input and the IMGUI HUD for the voyage game (placeholder until the real UI kit).
    // On the water everything is one tap: bubbles above rods and fish, and a strike minigame.
    public partial class VoyageGame
    {
        public enum HudTab { Market, HarbourMaster, CrewOffice, Chandlery, Supplies }

        static string TabName(HudTab t) => t switch { HudTab.Market => "Market", HudTab.HarbourMaster => "Harbour Master", HudTab.CrewOffice => "Crew Office", HudTab.Chandlery => "Chandlery", _ => "Supplies" };
        bool panelOpen = true;
        bool confirmNewGame;

        HudTab hudTab = HudTab.Market;
        Vector2 scroll;
        readonly List<Rect> hudRects = new();

        float GuiScale => Screen.height / 720f * UiScales[UiScaleIndex];
        float VW => Screen.width / GuiScale;

        Vector2 ToGui(Vector2 screen) => new(screen.x / GuiScale, (Screen.height - screen.y) / GuiScale);
        bool OverHud(Vector2 gui) => hudRects.Any(r => r.Contains(gui));

        // ---- input --------------------------------------------------------------------------

        void HandleInput()
        {
            var kb = Keyboard.current;
            if (kb != null && kb.escapeKey.wasPressedThisFrame && !showTitle)
            {
                if (showSettings) showSettings = false;
                else paused = !paused;
            }
            if (MenuOpen) return;
            if (kb != null && CurrentMode == Mode.Fishing)
            {
                if (kb.spaceKey.wasPressedThisFrame) StrikeTap();
                if (kb.hKey.wasPressedThisFrame) HeadHome();
            }

            var mouse = Mouse.current;
            if (mouse != null)
            {
                float s = mouse.scroll.ReadValue().y;
                if (Mathf.Abs(s) > 0.01f) ZoomOffset = Mathf.Clamp(ZoomOffset - Mathf.Sign(s) * 0.3f, -1.5f, 3f);
            }

            // While the minigame is up, a tap anywhere that isn't a button strikes (on press, so it feels instant).
            var pointer = Pointer.current;
            if (pointer == null || !pointer.press.wasPressedThisFrame) return;
            if (CurrentMode == Mode.Fishing && MinigameRod != null && !OverHud(ToGui(pointer.position.ReadValue()))) StrikeTap();
        }

        // ---- drawing ------------------------------------------------------------------------

        void OnGUI()
        {
            if (!built) return;
            Ui.Init();
            GUI.matrix = Matrix4x4.Scale(new Vector3(GuiScale, GuiScale, 1f));
            if (Event.current.type == EventType.Layout) hudRects.Clear();

            // Menus replace the HUD so nothing underneath can be clicked.
            if (showTitle) { DrawTitle(); return; }
            if (paused) { DrawPause(); return; }
            if (SimTime < refitUntil)
            {
                Dim(Mathf.Clamp01((refitUntil - SimTime) / 1.2f));
                GUI.Label(new Rect(VW / 2f - 200f, 310f, 400f, 80f), "Your skiff is ready", Ui.TitleCenter);
                return;
            }

            switch (CurrentMode)
            {
                case Mode.Harbour: DrawHarbour(); break;
                case Mode.Fishing: DrawFishing(); break;
                default: DrawSailing(); break;
            }

            if (toast != null && SimTime < toastUntil)
            {
                var r = new Rect(VW / 2f - 280f, 16f, 560f, 56f);
                GUI.Box(r, toast, Ui.ToastStyle);
            }
        }

        Rect Panel(Rect r, GUIStyle style = null)
        {
            Track(r);
            GUI.Box(r, GUIContent.none, style ?? Ui.Panel);
            return r;
        }

        void Track(Rect r)
        {
            if (Event.current.type == EventType.Layout) hudRects.Add(r);
        }

        void CoinChip(float y = 16f)
        {
            var r = Panel(new Rect(VW - 196f, y, 180f, 46f), Ui.Chip);
            Icon(new Rect(r.x + 14f, r.y + 10f, 26f, 26f), "icon-coin");
            GUI.Label(new Rect(r.x + 20f, r.y, r.width - 20f, r.height), $"<b>{State.Coins}</b> coins", Ui.WhiteCenter);
            var pause = new Rect(r.x - 56f, y, 46f, 46f);
            Track(pause);
            if (GUI.Button(pause, "II", Ui.Tab)) paused = true;
        }

        static void Icon(Rect r, string name)
        {
            var t = Ui.Tex(name);
            if (t != null) GUI.DrawTexture(r, t, ScaleMode.ScaleToFit, true);
        }

        void DrawSailing()
        {
            CoinChip();
            bool home = CurrentMode == Mode.SailingHome;
            var r = Panel(new Rect(VW / 2f - 220f, 90f, 440f, 92f));
            string verb = State.Hull > 0 ? "Sailing" : "Rowing";
            GUI.Label(new Rect(r.x + 18, r.y + 14, r.width - 36, 26), home ? $"{verb} home to {GameData.HarbourName}" : $"{verb} out to {GameData.Spots[ActiveSpot].Name}", Ui.H2);
            Ui.Bar(new Rect(r.x + 18, r.y + 52, r.width - 36, 16), modeTimer / Mathf.Max(0.1f, modeDuration));
        }

        void DrawFishing()
        {
            // Status panel, top left.
            int lines = State.Active.Count + Rods.Count(r => r.Unlocked) + (FirstVoyage ? 1 : 0);
            var p = Panel(new Rect(16f, 16f, 330f, 150f + lines * 22f));
            float x = p.x + 16, y = p.y + 12, w = p.width - 32;
            GUI.Label(new Rect(x, y, w, 26), GameData.Spots[ActiveSpot].Name, Ui.H2);
            y += 32;
            Row(ref y, x, w, "icon-cooler", $"Cooler  {Cooler.Count}/{State.CoolerCapacity}", Cooler.Count / (float)State.CoolerCapacity, Cooler.Count >= State.CoolerCapacity ? Ui.BarWarn : Ui.BarFill);
            Row(ref y, x, w, "icon-food", State.FoodMinutes > 0 ? $"Food  {State.FoodMinutes:0.0} min" : "Food  none: 70% speed", State.FoodMinutes / State.FoodCapacity, State.FoodMinutes < 1f ? Ui.BarWarn : Ui.BarGood);
            Icon(new Rect(x, y, 20, 20), "icon-bait-worm");
            GUI.Label(new Rect(x + 26, y, w - 26, 20), $"Bait  {State.Bait}   Squid  {State.Squid}     Stocks here  {State.Richness[ActiveSpot] * 100f:0}%", Ui.Small);
            y += 26;
            if (FirstVoyage)
            {
                GUI.Label(new Rect(x, y, w, 22), $"First trip: {Mathf.Min(Cooler.Count, 3)}/3 fish safely stowed", Ui.Body);
                y += 22;
            }
            foreach (var r in Rods.Where(r => r.Unlocked))
            {
                Icon(new Rect(x, y, 20, 20), "icon-rod");
                GUI.Label(new Rect(x + 26, y, w - 26, 20), $"Rod {r.Index + 1}:  {(r.State == RodState.Bite ? "<b>BITE!</b>" : r.StateText)}", Ui.Small);
                y += 22;
            }
            foreach (var c in State.Active)
            {
                int have = c.Delivered + Cooler.Count(f => f.Species == c.Species);
                Icon(new Rect(x, y, 20, 20), "icon-contract-scroll");
                GUI.Label(new Rect(x + 26, y, w - 26, 20), $"Contract {c.Title}:  {Mathf.Min(have, c.Count)}/{c.Count}  ({c.VoyagesLeft} voyage{(c.VoyagesLeft == 1 ? "" : "s")} left)", Ui.Mutedish);
                y += 22;
            }

            CoinChip();
            var homeRect = new Rect(VW - 196f, 70f, 180f, 50f);
            Track(homeRect);
            if (GUI.Button(homeRect, "Head home", Ui.BtnAlt)) HeadHome();
            if (State.Hull > 0)
            {
                var nr = Panel(new Rect(VW - 266f, 132f, 250f, 140f));
                string label = Net switch { NetState.Soaking => $"Net soaking · {NetRemaining:0}s · {NetCatch} fish", NetState.Ready => $"Net ready · {NetCatch} fish", NetState.Hauling => "Cranking the hand winch…", NetState.Setting => "Setting the net…", _ => "Gill net · ready to set" };
                GUI.Label(new Rect(nr.x + 12, nr.y + 12, nr.width - 24, 44), label, Ui.Body);
                bool enabled = CanWorkNet && Net is NetState.Stowed or NetState.Ready;
                if (GUI.Button(new Rect(nr.x + 12, nr.y + 62, nr.width - 24, 44), Net == NetState.Ready ? "Haul net" : "Set net", enabled ? Ui.Btn : Ui.BtnOff) && enabled)
                {
                    if (Net == NetState.Ready) HaulNet(); else SetNet();
                }
                GUI.Label(new Rect(nr.x + 12, nr.y + 112, nr.width - 24, 20), Manning != null ? "Finish the rod action to work the net." : "One tap. The captain does the work.", Ui.Small);
            }

            // Crew chips, bottom left.
            float cy = 720f - 16f;
            foreach (var person in People.Where(p => p != Captain))
            {
                cy -= 54f;
                var hr = Panel(new Rect(16f, cy, 330f, 50f), Ui.Chip);
                GUI.Label(new Rect(hr.x + 14, hr.y + 6, hr.width - 28, 40), $"<b>{person.Name}</b> ({person.Contract.RoleName}, {person.Contract.VoyagesLeft} voyages left)\n{person.State}", Ui.WhiteSmall);
                cy -= 6f;
            }
            cy -= 50f;
            var cr = Panel(new Rect(16f, cy, 330f, 50f), Ui.Chip);
            GUI.Label(new Rect(cr.x + 14, cr.y + 6, cr.width - 28, 40), $"<b>Captain</b> (you)\n{Captain.State}", Ui.WhiteSmall);

            // Speech bubbles in the world.
            foreach (var r in Rods.Where(r => r.Unlocked))
            {
                if (!CanCommandRod(r)) continue;
                string label = r.State == RodState.Bite ? "!" : r.InWater ? "Watch" : "Fish";
                if (Bubble(Boat.TransformPoint(r.TipLocal + Vector3.up * 0.25f), label, r.State == RodState.Bite, 88f, "icon-rod")) CommandRod(r);
            }
            foreach (var f in OnDeck.ToList())
                if (CanCarry(f) && Bubble(f.Root.position + Vector3.up * 0.35f, "Carry", f.Age > GameData.DeckFishLifetime - 8f, 88f, "icon-fish"))
                    CommandCarry(f);

            DrawMinigame();
            DrawCatchFeedback();
            DrawVoyageGuide();
        }

        bool Bubble(Vector3 world, string label, bool hot, float width = 88f, string icon = null, bool badge = false)
        {
            var sp = Cam.WorldToScreenPoint(world);
            if (sp.z < 0f) return false;
            var g = ToGui(sp);
            float bob = Mathf.Sin(SimTime * 3f + world.x) * 3f;
            var tex = icon != null ? Ui.Tex(icon) : null;
            if (tex != null) width += 26f;
            var r = new Rect(g.x - width / 2f, g.y - 52f + bob, width, 46f);
            if (CurrentMode == Mode.Harbour)
            {
                // World shop labels must yield to the fixed harbour cards and their controls.
                float shopWidth = Mathf.Min(620f, VW - 410f);
                if (r.Overlaps(new Rect(16f, 16f, 360f, 150f))
                    || r.Overlaps(new Rect(16f, 594f, 360f, 110f))
                    || panelOpen && r.Overlaps(new Rect(VW - shopWidth - 16f, 16f, shopWidth, 688f))) return false;
            }
            Track(r);
            bool flash = hot && Mathf.Repeat(SimTime * 4f, 1f) < 0.6f;
            if (!Ui.Sprite(new Rect(g.x - 12f, r.yMax - 6f, 24f, 18f), flash ? "bubble-hot-tail" : "bubble-white-tail"))
                GUI.Box(new Rect(g.x - 7f, r.yMax - 5f, 14f, 14f), GUIContent.none, hot ? Ui.DotGold : Ui.DotWhite);
            bool clicked = GUI.Button(r, tex != null ? "      " + label : label, flash ? Ui.BubbleHot : Ui.Bubble);
            if (tex != null) GUI.DrawTexture(new Rect(r.x + 14f, r.y + 9f, 24f, 24f), tex, ScaleMode.ScaleToFit, true);
            if (badge)
            {
                var b = new Rect(r.xMax - 16f, r.y - 8f, 24f, 24f);
                GUI.Box(b, GUIContent.none, Ui.DotRed);
                GUI.Label(b, "!", Ui.WhiteCenter);
            }
            return clicked;
        }

        // The strike minigame: a close-up of the bobber with the fish circling in.
        void DrawMinigame()
        {
            var rod = MinigameRod;
            if (rod == null) return;
            var p = new Rect(VW / 2f - 230f, 720f - 16f - 220f, 460f, 220f);
            if (!Ui.Sprite(p, "strike-water")) GUI.Box(p, GUIContent.none, Ui.Water);
            var c = new Vector2(p.center.x, p.y + 118f);
            string title = rod.State switch
            {
                RodState.Flying => "Casting...",
                RodState.Waiting => rod.Nibbling ? "Nibble... not yet!" : "Wait for the bite...",
                RodState.Bite => "TAP NOW!",
                RodState.Reeling => $"Reeling in a {GameData.Get(rod.HookedSpecies).Name.ToLower()}!",
                _ => "",
            };
            GUI.Label(new Rect(p.x, p.y + 12f, p.width, 34f), title, rod.State == RodState.Bite ? Ui.MiniHot : Ui.MiniTitle);

            float time = SimTime;
            if (rod.State is RodState.Waiting or RodState.Bite)
            {
                float dist = rod.State == RodState.Bite ? 4f : Mathf.Lerp(150f, 50f, rod.WaitProgress) * (rod.Nibbling ? 0.25f : 1f);
                float ang = rod.SwimAngle * Mathf.Deg2Rad;
                var fpos = new Vector2(c.x + Mathf.Cos(ang) * dist, c.y + 22f + Mathf.Sin(ang) * dist * 0.35f);
                if (!Ui.Sprite(new Rect(fpos.x - 44f, fpos.y - 22f, 88f, 44f), "fish-shadow", 0.85f)) GUI.Box(new Rect(fpos.x - 30f, fpos.y - 10f, 60f, 20f), GUIContent.none, Ui.FishShape);
            }
            if (rod.State == RodState.Bite)
            {
                float ring = 30f + Mathf.Repeat(time * 2.5f, 1f) * 70f;
                if (!Ui.Sprite(new Rect(c.x - ring / 2f, c.y - ring / 2f + 6f, ring, ring), "ripple-ring", 1f - (ring - 30f) / 90f)) GUI.Box(new Rect(c.x - ring / 2f, c.y - ring / 2f + 6f, ring, ring), GUIContent.none, Ui.Ring);
                if (!Ui.Sprite(new Rect(c.x - 36f, c.y - 30f, 72f, 72f), "bobber-underwater")) GUI.Box(new Rect(c.x - 9f, c.y + 2f, 18f, 18f), GUIContent.none, Ui.DotRed);
                Ui.Sprite(new Rect(c.x + 70f, c.y - 50f, 120f, 90f), "tap-burst");
                Ui.Bar(new Rect(p.x + 40f, p.yMax - 30f, p.width - 80f, 12f), 1f - rod.BiteProgress, Ui.BarWarn);
            }
            else if (rod.State == RodState.Reeling)
            {
                float fy = Mathf.Lerp(c.y + 30f, p.y + 64f, rod.ReelProgress);
                if (!Ui.Sprite(new Rect(c.x - 48f, fy - 24f, 96f, 48f), "fish-shadow")) GUI.Box(new Rect(c.x - 34f, fy - 11f, 68f, 22f), GUIContent.none, Ui.FishShape);
                Ui.Bar(new Rect(p.x + 40f, p.yMax - 30f, p.width - 80f, 12f), rod.ReelProgress, Ui.BarGood);
            }
            else
            {
                float dip = rod.Nibbling ? 7f : Mathf.Sin(time * 2.2f) * 2f;
                if (!Ui.Sprite(new Rect(c.x - 36f, c.y - 40f + dip, 72f, 72f), rod.Nibbling ? "bobber-dipped" : "bobber-floating"))
                {
                    GUI.Box(new Rect(c.x - 13f, c.y - 6f + dip, 26f, 26f), GUIContent.none, Ui.DotWhite);
                    GUI.Box(new Rect(c.x - 13f, c.y - 18f + dip, 26f, 26f), GUIContent.none, Ui.DotRed);
                }
                if (rod.State == RodState.Waiting)
                    GUI.Label(new Rect(p.x, p.yMax - 36f, p.width, 24f), "Tap anywhere when the bobber goes under. Not on a nibble!", Ui.WhiteCenterSmall);
            }
        }

        void Row(ref float y, float x, float w, string icon, string label, float t, GUIStyle fill)
        {
            Icon(new Rect(x, y - 1, 20, 20), icon);
            GUI.Label(new Rect(x + 26, y, 130, 20), label, Ui.Small);
            Ui.Bar(new Rect(x + 160, y + 1, w - 160, 18), t, fill);
            y += 24;
        }

        // ---- harbour ------------------------------------------------------------------------
        //
        // The quay has five shops. Tap a building's bubble (or a tab) to open its panel.

        static string ShopIcon(HudTab t) => t switch { HudTab.Market => "icon-coin", HudTab.HarbourMaster => "icon-map-pin", HudTab.CrewOffice => "icon-crew", HudTab.Chandlery => "icon-home-anchor", _ => "icon-food" };

        void OpenShop(HudTab tab)
        {
            hudTab = tab;
            panelOpen = true;
            scroll = Vector2.zero;
            confirmNewGame = false;
        }

        void DrawHarbour()
        {
            // Left: harbour card with the hull goal.
            var l = Panel(new Rect(16f, 16f, 360f, 150f));
            GUI.Label(new Rect(l.x + 16, l.y + 12, l.width - 32, 34), GameData.HarbourName, Ui.Title);
            GUI.Label(new Rect(l.x + 16, l.y + 50, l.width - 32, 22), $"Voyage {State.Voyage}  ·  <b>{State.Coins}</b> coins", Ui.Body);
            GUI.Label(new Rect(l.x + 16, l.y + 80, l.width - 32, 20), FirstVoyage ? "First trip: bring home 3 fish" : State.Hull > 0 ? "Skiff · 40-fish hold · outboard" : "Next hull: skiff refit", Ui.Small);
            float goal = Mathf.Min(State.BestVoyageFish / (float)GameData.SkiffFishGoal, 1f) * 0.5f + Mathf.Min(State.Coins / (float)GameData.SkiffCost, 1f) * 0.5f;
            Ui.Bar(new Rect(l.x + 16, l.y + 102, l.width - 32, 12), FirstVoyage ? 0f : State.Hull > 0 ? 1f : goal);
            GUI.Label(new Rect(l.x + 16, l.y + 118, l.width - 32, 20), FirstVoyage ? "Bait and food aboard. Set sail when you're ready." : State.Hull > 0 ? $"Fuel {State.Fuel} · trip uses {GameData.TripFuel(SelectedSpot)} (return included)" : $"Land {GameData.SkiffFishGoal} fish in one voyage (best {State.BestVoyageFish}) + {GameData.SkiffCost} coins", Ui.Mutedish);

            // Bottom left: set sail toward the chosen sea.
            var blocker = SailBlocker();
            var sail = new Rect(16f, 720f - 16f - 70f, 360f, 70f);
            Track(sail);
            if (GUI.Button(sail, blocker ?? $"Set sail  →  {GameData.Spots[SelectedSpot].Name}", blocker == null ? Ui.Btn : Ui.BtnOff) && blocker == null) SetSail();
            var change = new Rect(16f, sail.y - 40f, 360f, 34f);
            Track(change);
            if (GUI.Button(change, "Change sea at the Harbour Master", Ui.Tab)) OpenShop(HudTab.HarbourMaster);

            // Shop bubbles over the buildings.
            foreach (var (anchor, tab) in Shops)
                if (Bubble(anchor.position, TabName(tab), false, tab == HudTab.HarbourMaster ? 150f : 116f, ShopIcon(tab), ShopHasNews(tab)))
                    OpenShop(tab);

            if (!panelOpen) return;

            // Right: the open shop.
            float pw = Mathf.Min(620f, VW - 410f);
            var p = Panel(new Rect(VW - pw - 16f, 16f, pw, 720f - 32f));
            float x = p.x + 16, w = p.width - 32;
            var tabs = (HudTab[])System.Enum.GetValues(typeof(HudTab));
            float closeW = 44f;
            float tw = (w - closeW - 6f - (tabs.Length - 1) * 6f) / tabs.Length;
            for (int i = 0; i < tabs.Length; i++)
                if (GUI.Button(new Rect(x + i * (tw + 6f), p.y + 14, tw, 40), TabName(tabs[i]), hudTab == tabs[i] ? Ui.TabOn : Ui.Tab))
                    OpenShop(tabs[i]);
            if (GUI.Button(new Rect(p.xMax - 16 - closeW, p.y + 14, closeW, 40), "X", Ui.Tab)) panelOpen = false;

            var content = new Rect(x, p.y + 66, w, p.height - 80);
            GUILayout.BeginArea(content);
            scroll = GUILayout.BeginScrollView(scroll, false, false, GUIStyle.none, GUI.skin.verticalScrollbar);
            switch (hudTab)
            {
                case HudTab.Market: TabMarket(); break;
                case HudTab.HarbourMaster: TabHarbourMaster(); break;
                case HudTab.CrewOffice: TabCrew(); break;
                case HudTab.Chandlery: TabChandlery(); break;
                case HudTab.Supplies: TabSupplies(); break;
            }
            GUILayout.EndScrollView();
            GUILayout.EndArea();
        }

        bool ShopButton(string label, bool can, float width = 120f)
        {
            bool clicked = GUILayout.Button(label, can ? Ui.Btn : Ui.BtnOff, GUILayout.Width(width), GUILayout.Height(44)) && can;
            return clicked;
        }

        void TabMarket()
        {
            var s = State.LastSale;
            if (s == null)
            {
                GUILayout.Label("Welcome to Gull Harbour", Ui.H2);
                GUILayout.Space(6);
                GUILayout.Label(
                    "Your rowboat is ready, with bait and food aboard.\n\n" +
                    "<b>Bring home your first 3 fish.</b> Set sail for the harbour mouth; the hints on the water will show you what to do.\n\n" +
                    "Fish sell automatically when you return. Spend your catch on a bigger cooler, another rod, and eventually a crew.\n\n" +
                    "Keep fishing as long as you like. Head home whenever you're ready; progress saves here.", Ui.Body);
            }
            else
            {
                GUILayout.Label($"Voyage {State.Voyage - 1}: sold", Ui.H2);
                GUILayout.Space(4);
                GUILayout.Label($"Caught {s.Caught} fish in {s.Minutes:0.0} minutes.", Ui.Body);
                GUILayout.Label($"Sold {s.FishSold} fish for <b>{s.Coins}</b> coins." + (s.ToContracts > 0 ? $"  {s.ToContracts} went to contracts." : ""), Ui.Body);
                if (s.ContractCoins > 0) GUILayout.Label($"Contract rewards: <b>{s.ContractCoins}</b> coins.", Ui.Body);
                int earned = s.Coins + s.ContractCoins;
                GUILayout.Label($"That's {earned / Mathf.Max(0.1f, s.Minutes):0} coins per minute.", Ui.Mutedish);
                if (!State.Has(UpgradeId.IceBox) && s.FishSold > 0) GUILayout.Label("Without an ice box, fish lose value the longer they sit in the cooler.", Ui.Mutedish);
                foreach (var line in s.Lines) GUILayout.Label("• " + line, Ui.Body);
            }

            State.UnseenSale = false;
            DrawNextUpgrade();

            // Fish log: every species in Gull Harbour, with your record. Unknown ones hint at where they live.
            GUILayout.Space(12);
            int found = State.LogCount.Count(c => c > 0);
            GUILayout.Label($"Fish log  <size=14>{found}/{GameData.Fish.Length}</size>", Ui.H2);
            foreach (var f in GameData.Fish)
            {
                int i = (int)f.Species;
                GUILayout.BeginHorizontal(Ui.Card);
                GUILayout.Label(Ui.Tex(State.LogCount[i] > 0 ? FishPortrait(f.Species) : "fish-unknown"), GUILayout.Width(48), GUILayout.Height(48));
                if (State.LogCount[i] > 0)
                {
                    GUILayout.Label($"<b>{f.Name}</b>", Ui.Body, GUILayout.Width(150));
                    GUILayout.Label($"caught {State.LogCount[i]} · record {State.LogBest[i]:0.00} kg", Ui.Mutedish);
                }
                else
                {
                    var seas = Enumerable.Range(0, GameData.Spots.Length)
                        .Where(s => GameData.Spots[s].Table.Any(e => e.species == f.Species))
                        .Select(s => GameData.Spots[s].Name);
                    GUILayout.Label("<b>???</b>", Ui.Body, GUILayout.Width(150));
                    GUILayout.Label("Lives at: " + string.Join(", ", seas), Ui.Mutedish);
                }
                GUILayout.EndHorizontal();
            }

            GUILayout.Space(12);
            GUILayout.Label("Today's prices", Ui.H2);
            GUILayout.Label("Selling a lot of one fish pushes its price down. Prices recover over a few voyages.", Ui.Mutedish);
            foreach (var f in GameData.Fish)
            {
                float m = State.Market[(int)f.Species];
                GUILayout.Label($"{f.Name}: {State.PricePerKg(f.Species):0.0} per kg  <size=12>({(m >= 0.995f ? "normal" : $"{(1f - m) * 100f:0}% down")})</size>", Ui.Body);
            }

            GUILayout.Space(16);
            GUILayout.BeginHorizontal();
            GUILayout.FlexibleSpace();
            if (GUILayout.Button(confirmNewGame ? "Tap again to wipe the save" : "Start a new game", confirmNewGame ? Ui.Btn : Ui.Tab, GUILayout.Width(220), GUILayout.Height(34)))
            {
                if (confirmNewGame) { NewGame(); confirmNewGame = false; }
                else confirmNewGame = true;
            }
            GUILayout.EndHorizontal();
        }

        void TabHarbourMaster()
        {
            GUILayout.Label("Sea chart", Ui.H2);
            GUILayout.Label("Tap a sea to select it. New seas need a chart. Stocks drop as you fish a sea and recover every voyage.", Ui.Mutedish);

            // The chart: land on the left (the harbour), seas as pins.
            var map = GUILayoutUtility.GetRect(10, 230, GUILayout.ExpandWidth(true));
            GUI.Box(map, GUIContent.none, Ui.Water);
            GUI.Box(new Rect(map.x + 6, map.y + 30, 70, map.height - 60), GUIContent.none, Ui.Card);
            GUI.Label(new Rect(map.x + 6, map.y + map.height / 2f - 10, 70, 20), "Gull\nHarbour", Ui.Center);
            for (int i = 0; i < GameData.Spots.Length; i++)
            {
                var s = GameData.Spots[i];
                var pos = new Vector2(map.x + 90 + s.MapPos.x * (map.width - 140), map.y + 20 + s.MapPos.y * (map.height - 60));
                bool known = State.Known(i);
                var pin = new Rect(pos.x - 13, pos.y - 13, 26, 26);
                GUI.Box(pin, GUIContent.none, i == SelectedSpot ? Ui.DotGold : known ? Ui.DotWhite : Ui.FishShape);
                GUI.Label(new Rect(pos.x - 70, pos.y + 14, 140, 20), known ? s.Name : $"{s.Name} (locked)", Ui.WhiteCenterSmall);
                if (GUI.Button(new Rect(pos.x - 40, pos.y - 20, 80, 56), GUIContent.none, GUIStyle.none)) chartFocus = i;
            }

            // Detail card for the focused sea.
            var f = GameData.Spots[chartFocus];
            bool k = State.Known(chartFocus);
            GUILayout.Space(8);
            GUILayout.BeginVertical(chartFocus == SelectedSpot ? Ui.CardOn : Ui.Card);
            GUILayout.Label($"{f.Name}   <size=13>{f.RowSeconds:0} s row</size>", Ui.H2);
            GUILayout.Label(f.Blurb, Ui.Body);
            GUILayout.Label("Fish: " + string.Join(", ", f.Table.Select(e => GameData.Get(e.species).Name)), Ui.Mutedish);
            var r = GUILayoutUtility.GetRect(10, 16, GUILayout.ExpandWidth(true));
            GUI.Label(new Rect(r.x, r.y, 110, 16), $"Stocks {State.Richness[chartFocus] * 100f:0}%", Ui.Small);
            Ui.Bar(new Rect(r.x + 110, r.y + 2, r.width - 110, 12), State.Richness[chartFocus], State.Richness[chartFocus] < 0.6f ? Ui.BarWarn : Ui.BarGood);
            GUILayout.Space(6);
            if (k)
            {
                if (chartFocus == SelectedSpot) GUILayout.Label("<b>Selected.</b> Set sail from the quay.", Ui.Body);
                else if (ShopButton("Fish here", true, 160f)) SelectedSpot = chartFocus;
            }
            else if (ShopButton($"Buy chart: {f.ChartCost}", State.Coins >= f.ChartCost, 200f) && State.BuyChart(chartFocus))
            {
                SelectedSpot = chartFocus;
                Toast($"You can now fish {f.Name}.");
                SaveGame();
            }
            GUILayout.EndVertical();

            GUILayout.Space(14);
            GUILayout.Label($"Your contracts ({State.Active.Count}/{GameData.MaxActiveContracts})", Ui.H2);
            if (State.Active.Count == 0) GUILayout.Label("None yet. Fish that match a contract go to it instead of the market.", Ui.Mutedish);
            foreach (var c in State.Active)
            {
                GUILayout.BeginVertical(Ui.Card);
                GUILayout.Label($"Deliver {c.Title}: {c.Delivered}/{c.Count}", Ui.Body);
                GUILayout.Label($"Reward {c.Reward} coins · {c.VoyagesLeft} voyage{(c.VoyagesLeft == 1 ? "" : "s")} left", Ui.Mutedish);
                GUILayout.EndVertical();
                GUILayout.Space(4);
            }
            GUILayout.Space(8);
            GUILayout.Label("Contract board", Ui.H2);
            foreach (var c in State.Offers.ToList())
            {
                GUILayout.BeginHorizontal(Ui.Card);
                GUILayout.BeginVertical();
                GUILayout.Label($"Deliver {c.Title}", Ui.Body);
                GUILayout.Label($"within {c.VoyagesLeft} voyages · reward <b>{c.Reward}</b> (market value about {Mathf.RoundToInt(c.Count * GameData.Get(c.Species).AvgValue)})", Ui.Mutedish);
                GUILayout.EndVertical();
                if (ShopButton("Take", State.Active.Count < GameData.MaxActiveContracts, 90f))
                {
                    State.TakeContract(c);
                    SaveGame();
                }
                GUILayout.EndHorizontal();
                GUILayout.Space(4);
            }
        }

        int chartFocus;

        void TabCrew()
        {
            GUILayout.Label($"Your crew ({State.CrewCount}/{State.HullDef.CrewCap})", Ui.H2);
            foreach (var d in State.Crew)
            {
                GUILayout.BeginVertical(Ui.Card);
                GUILayout.Label($"{d.Name}, {d.RoleName} · {d.Grade}", Ui.Body);
                GUILayout.Label($"Works at {GameData.Speed(d.Grade):0.0}x speed · {d.VoyagesLeft} voyage{(d.VoyagesLeft == 1 ? "" : "s")} left on contract", Ui.Mutedish);
                GUILayout.EndVertical();
            }
            if (State.CrewCount == 0) GUILayout.Label("Just you. Deckhands bait hooks and carry fish. The skiff also has room for fishermen who cast and strike their own rods.", Ui.Mutedish);

            GUILayout.Space(10);
            GUILayout.Label("Looking for work", Ui.H2);
            GUILayout.Label("Who's here changes every voyage. Nobody signs on for good: contracts run for a few voyages.", Ui.Mutedish);
            if (State.Board.Count == 0) GUILayout.Label("Nobody is looking for work today. Try after your next voyage.", Ui.Body);
            foreach (var c in State.Board.ToList())
            {
                GUILayout.BeginHorizontal(Ui.Card);
                GUILayout.BeginVertical();
                GUILayout.Label($"{c.Name}, {c.RoleName} · {c.Grade}" + (c.Grade == Grade.Veteran ? "  <size=12>(rare)</size>" : ""), Ui.Body);
                GUILayout.Label($"{GameData.Speed(c.Grade):0.0}x speed · {c.VoyagesLeft} voyages · fee <b>{c.Fee}</b> coins", Ui.Mutedish);
                if (c.Role == CrewRole.Fisherman) GUILayout.Label($"Strikes {GameData.StrikeChance(c.Grade) * 100f:0}% of bites; leaves fish for deckhands.", Ui.Mutedish);
                GUILayout.EndVertical();
                if (ShopButton("Hire", State.CrewCount < State.HullDef.CrewCap && State.Coins >= c.Fee, 90f))
                {
                    State.Hire(c);
                    SyncCrew();
                    SaveGame();
                }
                GUILayout.EndHorizontal();
                GUILayout.Space(4);
            }
        }

        void UpgradeCards(string shop)
        {
            foreach (var u in GameData.Upgrades.Where(u => u.Shop == shop))
            {
                GUILayout.BeginHorizontal(Ui.Card);
                GUILayout.BeginVertical();
                GUILayout.Label(u.Name, Ui.Body);
                GUILayout.Label(u.Desc + (u.Requires.HasValue && !State.Has(u.Requires.Value) ? $" Needs {GameData.Upgrade(u.Requires.Value).Name.ToLower()} first." : ""), Ui.Mutedish);
                GUILayout.EndVertical();
                bool owned = State.Has(u.Id);
                bool can = !owned && State.Coins >= u.Cost && (!u.Requires.HasValue || State.Has(u.Requires.Value));
                if (ShopButton(owned ? "Owned" : $"{u.Cost}", can, 110f) && State.TryBuy(u.Id))
                {
                    SyncUpgrades();
                    Toast($"Bought: {u.Name}.");
                    SaveGame();
                }
                GUILayout.EndHorizontal();
                GUILayout.Space(4);
            }
        }

        void TabChandlery()
        {
            GUILayout.Label("Boat and gear", Ui.H2);
            GUILayout.Space(4);
            UpgradeCards("Chandlery");
            GUILayout.Space(12);
            GUILayout.BeginVertical(Ui.Card);
            GUILayout.Label("Skiff refit", Ui.Body);
            GUILayout.Label(State.Hull > 0 ? "Refitted: 5 × 3 deck, 40-fish hold, three rods, outboard and gill net. Hire fishermen and deckhands at the Crew Office." : $"Bring home {GameData.SkiffFishGoal} fish in one voyage (best {State.BestVoyageFish}) and pay {GameData.SkiffCost} coins. Refit to a skiff with a 40-fish hold, three rods and an outboard. Includes a gill net and the first tank of fuel.", Ui.Mutedish);
            if (State.Hull == 0 && ShopButton($"Refit for {GameData.SkiffCost}", State.CanRefit, 180f)) RefitSkiff();
            GUILayout.EndVertical();
        }

        void TabSupplies()
        {
            GUILayout.Label("Bait", Ui.H2);
            GUILayout.BeginHorizontal(Ui.Card);
            GUILayout.Label($"Worms: {State.Bait}\n<size=12>One per hook. A spooked or missed fish takes the bait.</size>", Ui.Body);
            if (ShopButton($"+{GameData.BaitPackSize} for {GameData.BaitPackCost}", State.Coins >= GameData.BaitPackCost, 150f) && State.BuyBait()) SaveGame();
            GUILayout.EndHorizontal();
            GUILayout.Space(4);
            GUILayout.BeginHorizontal(Ui.Card);
            GUILayout.Label($"Squid: {State.Squid}\n<size=12>Draws bigger fish and bigger species. Used first when you have it.</size>", Ui.Body);
            if (ShopButton($"+{GameData.SquidPackSize} for {GameData.SquidPackCost}", State.Coins >= GameData.SquidPackCost, 150f) && State.BuySquid()) SaveGame();
            GUILayout.EndHorizontal();
            bool use = GUILayout.Toggle(State.UseSquid, "  Use squid first when I have it", GUILayout.Height(24));
            if (use != State.UseSquid) { State.UseSquid = use; SaveGame(); }

            GUILayout.Space(12);
            GUILayout.Label("Food", Ui.H2);
            GUILayout.BeginHorizontal(Ui.Card);
            GUILayout.Label($"Food: {State.FoodMinutes:0.0}/{State.FoodCapacity:0} min\n<size=12>Each crew member eats one minute per minute. No food: 70% speed.</size>", Ui.Body);
            int cost = State.FoodFillCost;
            if (ShopButton(cost > 0 ? $"Fill up for {cost}" : "Full", cost > 0 && State.Coins >= cost, 150f) && State.FillFood()) SaveGame();
            GUILayout.EndHorizontal();
            GUILayout.Space(4);
            UpgradeCards("Supplies");
            if (State.Hull > 0)
            {
                GUILayout.Space(12);
                GUILayout.Label("Fuel", Ui.H2);
                GUILayout.BeginHorizontal(Ui.Card);
                GUILayout.Label($"Fuel: {State.Fuel}\n<size=12>This trip uses {GameData.TripFuel(SelectedSpot)}. Return fuel is reserved at launch.</size>", Ui.Body);
                if (ShopButton($"+{GameData.FuelPackSize} for {GameData.FuelPackCost}", State.Coins >= GameData.FuelPackCost, 150f) && State.BuyFuel()) SaveGame();
                GUILayout.EndHorizontal();
            }
        }
    }
}

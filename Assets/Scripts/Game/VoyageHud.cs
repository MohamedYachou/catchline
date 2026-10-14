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
        public enum HudTab { Catch, Map, Contracts, Crew, Shop }

        HudTab hudTab = HudTab.Catch;
        Vector2 scroll;
        readonly List<Rect> hudRects = new();

        float GuiScale => Screen.height / 720f;
        float VW => Screen.width / GuiScale;

        Vector2 ToGui(Vector2 screen) => new(screen.x / GuiScale, (Screen.height - screen.y) / GuiScale);
        bool OverHud(Vector2 gui) => hudRects.Any(r => r.Contains(gui));

        // ---- input --------------------------------------------------------------------------

        void HandleInput()
        {
            var kb = Keyboard.current;
            if (kb != null && CurrentMode == Mode.Fishing)
            {
                if (kb.spaceKey.wasPressedThisFrame) StrikeTap();
                if (kb.hKey.wasPressedThisFrame) HeadHome();
            }

            var mouse = Mouse.current;
            if (mouse != null)
            {
                float s = mouse.scroll.ReadValue().y;
                if (Mathf.Abs(s) > 0.01f) Cam.orthographicSize = Mathf.Clamp(Cam.orthographicSize - Mathf.Sign(s) * 0.3f, 2.4f, 7f);
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
            GUI.Label(r, $"<b>{State.Coins}</b> coins", Ui.WhiteCenter);
        }

        void DrawSailing()
        {
            CoinChip();
            bool home = CurrentMode == Mode.SailingHome;
            var r = Panel(new Rect(VW / 2f - 220f, 90f, 440f, 92f));
            GUI.Label(new Rect(r.x + 18, r.y + 14, r.width - 36, 26), home ? $"Rowing home to {GameData.HarbourName}" : $"Rowing out to {GameData.Spots[ActiveSpot].Name}", Ui.H2);
            Ui.Bar(new Rect(r.x + 18, r.y + 52, r.width - 36, 16), modeTimer / Mathf.Max(0.1f, modeDuration));
        }

        void DrawFishing()
        {
            // Status panel, top left.
            int lines = State.Active.Count + Rods.Count(r => r.Unlocked);
            var p = Panel(new Rect(16f, 16f, 330f, 150f + lines * 22f));
            float x = p.x + 16, y = p.y + 12, w = p.width - 32;
            GUI.Label(new Rect(x, y, w, 26), GameData.Spots[ActiveSpot].Name, Ui.H2);
            y += 32;
            Row(ref y, x, w, $"Cooler  {Cooler.Count}/{State.CoolerCapacity}", Cooler.Count / (float)State.CoolerCapacity, Cooler.Count >= State.CoolerCapacity ? Ui.BarWarn : Ui.BarFill);
            Row(ref y, x, w, State.FoodMinutes > 0 ? $"Food  {State.FoodMinutes:0.0} min" : "Food  none: 70% speed", State.FoodMinutes / State.FoodCapacity, State.FoodMinutes < 1f ? Ui.BarWarn : Ui.BarGood);
            GUI.Label(new Rect(x, y, w, 20), $"Bait  {State.Bait}     Stocks here  {State.Richness[ActiveSpot] * 100f:0}%", Ui.Small);
            y += 26;
            foreach (var r in Rods.Where(r => r.Unlocked))
            {
                GUI.Label(new Rect(x, y, w, 20), $"Rod {r.Index + 1}:  {(r.State == RodState.Bite ? "<b>BITE!</b>" : r.StateText)}", Ui.Small);
                y += 22;
            }
            foreach (var c in State.Active)
            {
                int have = c.Delivered + Cooler.Count(f => f.Species == c.Species);
                GUI.Label(new Rect(x, y, w, 20), $"Contract {c.Title}:  {Mathf.Min(have, c.Count)}/{c.Count}  ({c.VoyagesLeft} voyage{(c.VoyagesLeft == 1 ? "" : "s")} left)", Ui.Mutedish);
                y += 22;
            }

            CoinChip();
            var homeRect = new Rect(VW - 196f, 70f, 180f, 50f);
            Track(homeRect);
            if (GUI.Button(homeRect, "Head home", Ui.BtnAlt)) HeadHome();

            // Crew chips, bottom left.
            float cy = 720f - 16f;
            if (Hand != null)
            {
                cy -= 54f;
                var hr = Panel(new Rect(16f, cy, 330f, 50f), Ui.Chip);
                GUI.Label(new Rect(hr.x + 14, hr.y + 6, hr.width - 28, 40), $"<b>{Hand.Name}</b> ({GameData.GradeName(Hand.Contract.Grade)}, {Hand.Contract.VoyagesLeft} voyage{(Hand.Contract.VoyagesLeft == 1 ? "" : "s")} left)\n{Hand.State}", Ui.WhiteSmall);
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
                if (Bubble(Boat.TransformPoint(r.TipLocal + Vector3.up * 0.25f), label, r.State == RodState.Bite)) CommandRod(r);
            }
            foreach (var f in OnDeck.ToList())
                if (CanCarry(f) && Bubble(f.Root.position + Vector3.up * 0.35f, "Carry", f.Age > GameData.DeckFishLifetime - 8f))
                    CommandCarry(f);

            DrawMinigame();

            if (State.Voyage <= 3 && MinigameRod == null)
            {
                string hint = Hint();
                if (hint != null) GUI.Box(new Rect(VW / 2f - 260f, 720f - 64f, 520f, 44f), hint, Ui.ToastStyle);
            }
        }

        string Hint()
        {
            if (OnDeck.Any(CanCarry)) return "Tap Carry to take the fish to the cooler before it flops overboard.";
            if (Captain.Busy || Captain.Walking || Captain.Carrying != null) return null;
            if (Rods.Any(CanCommandRod)) return "Tap the Fish bubble: the captain baits and casts.";
            return null;
        }

        bool Bubble(Vector3 world, string label, bool hot)
        {
            var sp = Cam.WorldToScreenPoint(world);
            if (sp.z < 0f) return false;
            var g = ToGui(sp);
            float bob = Mathf.Sin(SimTime * 3f + world.x) * 3f;
            var r = new Rect(g.x - 44f, g.y - 50f + bob, 88f, 42f);
            Track(r);
            GUI.Box(new Rect(g.x - 7f, r.yMax - 5f, 14f, 14f), GUIContent.none, hot ? Ui.DotGold : Ui.DotWhite);
            return GUI.Button(r, label, hot && Mathf.Repeat(SimTime * 4f, 1f) < 0.6f ? Ui.BubbleHot : Ui.Bubble);
        }

        // The strike minigame: a close-up of the bobber with the fish circling in.
        void DrawMinigame()
        {
            var rod = MinigameRod;
            if (rod == null) return;
            var p = new Rect(VW / 2f - 230f, 720f - 16f - 220f, 460f, 220f);
            GUI.Box(p, GUIContent.none, Ui.Water);
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
                GUI.Box(new Rect(fpos.x - 30f, fpos.y - 10f, 60f, 20f), GUIContent.none, Ui.FishShape);
            }
            if (rod.State == RodState.Bite)
            {
                float ring = 30f + Mathf.Repeat(time * 2.5f, 1f) * 70f;
                GUI.Box(new Rect(c.x - ring / 2f, c.y - ring / 2f + 6f, ring, ring), GUIContent.none, Ui.Ring);
                GUI.Box(new Rect(c.x - 9f, c.y + 2f, 18f, 18f), GUIContent.none, Ui.DotRed);
                Ui.Bar(new Rect(p.x + 40f, p.yMax - 30f, p.width - 80f, 12f), 1f - rod.BiteProgress, Ui.BarWarn);
            }
            else if (rod.State == RodState.Reeling)
            {
                float fy = Mathf.Lerp(c.y + 30f, p.y + 64f, rod.ReelProgress);
                GUI.Box(new Rect(c.x - 34f, fy - 11f, 68f, 22f), GUIContent.none, Ui.FishShape);
                Ui.Bar(new Rect(p.x + 40f, p.yMax - 30f, p.width - 80f, 12f), rod.ReelProgress, Ui.BarGood);
            }
            else
            {
                float dip = rod.Nibbling ? 7f : Mathf.Sin(time * 2.2f) * 2f;
                GUI.Box(new Rect(c.x - 13f, c.y - 6f + dip, 26f, 26f), GUIContent.none, Ui.DotWhite);
                GUI.Box(new Rect(c.x - 13f, c.y - 18f + dip, 26f, 26f), GUIContent.none, Ui.DotRed);
                if (rod.State == RodState.Waiting)
                    GUI.Label(new Rect(p.x, p.yMax - 36f, p.width, 24f), "Tap anywhere when the bobber goes under. Not on a nibble!", Ui.WhiteCenterSmall);
            }
        }

        void Row(ref float y, float x, float w, string label, float t, GUIStyle fill)
        {
            GUI.Label(new Rect(x, y, 150, 20), label, Ui.Small);
            Ui.Bar(new Rect(x + 150, y + 3, w - 150, 13), t, fill);
            y += 24;
        }

        // ---- harbour ------------------------------------------------------------------------

        void DrawHarbour()
        {
            // Left: harbour title and the hull goal.
            var l = Panel(new Rect(16f, 16f, 360f, 150f));
            GUI.Label(new Rect(l.x + 16, l.y + 12, l.width - 32, 34), GameData.HarbourName, Ui.Title);
            GUI.Label(new Rect(l.x + 16, l.y + 50, l.width - 32, 22), $"Voyage {State.Voyage}  ·  <b>{State.Coins}</b> coins", Ui.Body);
            GUI.Label(new Rect(l.x + 16, l.y + 80, l.width - 32, 20), $"Next hull: skiff refit", Ui.Small);
            float goal = Mathf.Min(State.BestVoyageFish / (float)GameData.SkiffFishGoal, 1f) * 0.5f + Mathf.Min(State.Coins / (float)GameData.SkiffCost, 1f) * 0.5f;
            Ui.Bar(new Rect(l.x + 16, l.y + 102, l.width - 32, 12), goal);
            GUI.Label(new Rect(l.x + 16, l.y + 118, l.width - 32, 20), $"Land {GameData.SkiffFishGoal} fish in one voyage (best {State.BestVoyageFish}) + {GameData.SkiffCost} coins", Ui.Mutedish);

            // Right: tabbed panel.
            float pw = Mathf.Min(620f, VW - 410f);
            var p = Panel(new Rect(VW - pw - 16f, 16f, pw, 720f - 32f));
            float x = p.x + 16, w = p.width - 32;
            var tabs = (HudTab[])System.Enum.GetValues(typeof(HudTab));
            float tw = (w - (tabs.Length - 1) * 6f) / tabs.Length;
            for (int i = 0; i < tabs.Length; i++)
            {
                string name = tabs[i] switch { HudTab.Catch => "Catch", HudTab.Map => "Map", HudTab.Contracts => "Contracts", HudTab.Crew => "Crew", _ => "Shop" };
                if (GUI.Button(new Rect(x + i * (tw + 6f), p.y + 14, tw, 40), name, hudTab == tabs[i] ? Ui.TabOn : Ui.Tab))
                {
                    hudTab = tabs[i];
                    scroll = Vector2.zero;
                }
            }

            var content = new Rect(x, p.y + 66, w, p.height - 66 - 92);
            GUILayout.BeginArea(content);
            scroll = GUILayout.BeginScrollView(scroll, false, false, GUIStyle.none, GUI.skin.verticalScrollbar);
            switch (hudTab)
            {
                case HudTab.Catch: TabCatch(); break;
                case HudTab.Map: TabMap(); break;
                case HudTab.Contracts: TabContracts(); break;
                case HudTab.Crew: TabCrew(); break;
                case HudTab.Shop: TabShop(); break;
            }
            GUILayout.EndScrollView();
            GUILayout.EndArea();

            // Set sail.
            var blocker = SailBlocker();
            var spot = GameData.Spots[SelectedSpot];
            var sail = new Rect(x, p.yMax - 80, w, 64);
            if (GUI.Button(sail, blocker ?? $"Set sail  →  {spot.Name}", blocker == null ? Ui.Btn : Ui.BtnOff) && blocker == null) SetSail();
        }

        void TabCatch()
        {
            var s = State.LastSale;
            if (s == null)
            {
                GUILayout.Label("Welcome aboard", Ui.H2);
                GUILayout.Space(6);
                GUILayout.Label(
                    "You start with a rowboat, one rod and a cooler.\n\n" +
                    "<b>On the water:</b> tap the rod to walk to it, then use the action button (or Space):\n" +
                    "  1. Bait the hook.\n  2. Hold to cast, release. Longer casts catch bigger fish but bite slower.\n" +
                    "  3. Watch the bobber. Little twitches are nibbles: wait. When it goes fully under, <b>strike</b>.\n" +
                    "  4. Pick the fish up and carry it to the cooler before it flops back overboard.\n\n" +
                    "When the cooler is full, head home. Fish sell automatically when you arrive.\n\n" +
                    "<b>Next:</b> pick a spot on the Map tab, then Set sail.", Ui.Body);
                return;
            }
            GUILayout.Label($"Voyage {State.Voyage - 1} result", Ui.H2);
            GUILayout.Space(6);
            GUILayout.Label($"Caught {s.Caught} fish in {s.Minutes:0.0} minutes.", Ui.Body);
            GUILayout.Label($"Sold {s.FishSold} fish for <b>{s.Coins}</b> coins." + (s.ToContracts > 0 ? $"  {s.ToContracts} went to contracts." : ""), Ui.Body);
            if (s.ContractCoins > 0) GUILayout.Label($"Contract rewards: <b>{s.ContractCoins}</b> coins.", Ui.Body);
            int earned = s.Coins + s.ContractCoins;
            GUILayout.Label($"That's {earned / Mathf.Max(0.1f, s.Minutes):0} coins per minute.", Ui.Mutedish);
            if (!State.Has(UpgradeId.IceBox) && s.FishSold > 0) GUILayout.Label("Without an ice box, fish lose value the longer they sit in the cooler.", Ui.Mutedish);
            GUILayout.Space(8);
            foreach (var line in s.Lines) GUILayout.Label("• " + line, Ui.Body);
        }

        void TabMap()
        {
            GUILayout.Label("Pick a fishing spot. Stocks drop as you fish a spot and recover every voyage.", Ui.Mutedish);
            GUILayout.Space(6);
            for (int i = 0; i < GameData.Spots.Length; i++)
            {
                var s = GameData.Spots[i];
                GUILayout.BeginVertical(i == SelectedSpot ? Ui.CardOn : Ui.Card);
                GUILayout.Label($"{s.Name}   <size=13>{s.RowSeconds:0} s row</size>", Ui.H2);
                GUILayout.Label(s.Blurb, Ui.Body);
                GUILayout.Label(string.Join(", ", s.Table.Select(e => GameData.Get(e.species).Name)), Ui.Mutedish);
                var r = GUILayoutUtility.GetRect(10, 16, GUILayout.ExpandWidth(true));
                GUI.Label(new Rect(r.x, r.y, 110, 16), $"Stocks {State.Richness[i] * 100f:0}%", Ui.Small);
                Ui.Bar(new Rect(r.x + 110, r.y + 2, r.width - 110, 12), State.Richness[i], State.Richness[i] < 0.6f ? Ui.BarWarn : Ui.BarGood);
                GUILayout.EndVertical();
                if (Event.current.type == EventType.MouseUp && GUILayoutUtility.GetLastRect().Contains(Event.current.mousePosition))
                {
                    SelectedSpot = i;
                    Event.current.Use();
                }
                GUILayout.Space(8);
            }
        }

        void TabContracts()
        {
            GUILayout.Label($"Your contracts ({State.Active.Count}/{GameData.MaxActiveContracts})", Ui.H2);
            if (State.Active.Count == 0) GUILayout.Label("None yet. Take one below. Fish that match a contract go to it instead of the market.", Ui.Mutedish);
            foreach (var c in State.Active)
            {
                GUILayout.BeginVertical(Ui.Card);
                GUILayout.Label($"Deliver {c.Title}: {c.Delivered}/{c.Count}", Ui.Body);
                GUILayout.Label($"Reward {c.Reward} coins · {c.VoyagesLeft} voyage{(c.VoyagesLeft == 1 ? "" : "s")} left", Ui.Mutedish);
                GUILayout.EndVertical();
                GUILayout.Space(4);
            }
            GUILayout.Space(10);
            GUILayout.Label("Harbour board", Ui.H2);
            foreach (var c in State.Offers.ToList())
            {
                GUILayout.BeginHorizontal(Ui.Card);
                GUILayout.BeginVertical();
                GUILayout.Label($"Deliver {c.Title}", Ui.Body);
                GUILayout.Label($"within {c.VoyagesLeft} voyages · reward <b>{c.Reward}</b> coins (market value about {Mathf.RoundToInt(c.Count * GameData.Get(c.Species).AvgValue)})", Ui.Mutedish);
                GUILayout.EndVertical();
                bool can = State.Active.Count < GameData.MaxActiveContracts;
                if (GUILayout.Button("Take", can ? Ui.Btn : Ui.BtnOff, GUILayout.Width(90), GUILayout.Height(44)) && can) State.TakeContract(c);
                GUILayout.EndHorizontal();
                GUILayout.Space(4);
            }
            GUILayout.Space(10);
            GUILayout.Label("Market prices", Ui.H2);
            GUILayout.Label("Selling a lot of one fish pushes its price down. Prices recover over a few voyages.", Ui.Mutedish);
            foreach (var f in GameData.Fish)
            {
                float m = State.Market[(int)f.Species];
                GUILayout.Label($"{f.Name}: {State.PricePerKg(f.Species):0.0} per kg  <size=12>({(m >= 0.995f ? "normal" : $"{(1f - m) * 100f:0}% down")})</size>", Ui.Body);
            }
        }

        void TabCrew()
        {
            GUILayout.Label("Your crew", Ui.H2);
            if (State.Deckhand != null)
            {
                var d = State.Deckhand;
                GUILayout.BeginVertical(Ui.Card);
                GUILayout.Label($"{d.Name}, {GameData.GradeName(d.Grade)}", Ui.Body);
                GUILayout.Label($"Works at {GameData.Speed(d.Grade):0.0}x speed · {d.VoyagesLeft} voyage{(d.VoyagesLeft == 1 ? "" : "s")} left on contract", Ui.Mutedish);
                GUILayout.EndVertical();
            }
            else GUILayout.Label("Just you. The rowboat has room for one deckhand: they bait hooks and carry fish to the cooler, so you only cast and strike.", Ui.Mutedish);

            GUILayout.Space(10);
            GUILayout.Label("Crew board", Ui.H2);
            GUILayout.Label("Who's available changes every voyage. Nobody signs on for good.", Ui.Mutedish);
            if (State.Board.Count == 0) GUILayout.Label("Nobody is looking for work today.", Ui.Body);
            foreach (var c in State.Board.ToList())
            {
                GUILayout.BeginHorizontal(Ui.Card);
                GUILayout.BeginVertical();
                GUILayout.Label($"{c.Name}, {GameData.GradeName(c.Grade)}" + (c.Grade == Grade.Veteran ? "  <size=12>(rare)</size>" : ""), Ui.Body);
                GUILayout.Label($"{GameData.Speed(c.Grade):0.0}x speed · {c.VoyagesLeft} voyages · fee <b>{c.Fee}</b> coins", Ui.Mutedish);
                GUILayout.EndVertical();
                bool can = State.Deckhand == null && State.Coins >= c.Fee;
                if (GUILayout.Button("Hire", can ? Ui.Btn : Ui.BtnOff, GUILayout.Width(90), GUILayout.Height(44)) && can)
                {
                    State.Hire(c);
                    SyncCrew();
                }
                GUILayout.EndHorizontal();
                GUILayout.Space(4);
            }
        }

        void TabShop()
        {
            GUILayout.Label("Supplies", Ui.H2);
            GUILayout.BeginHorizontal(Ui.Card);
            GUILayout.Label($"Bait: {State.Bait}\n<size=12>One per cast. A spooked or missed fish takes the bait.</size>", Ui.Body);
            bool canBait = State.Coins >= GameData.BaitPackCost;
            if (GUILayout.Button($"+{GameData.BaitPackSize} for {GameData.BaitPackCost}", canBait ? Ui.Btn : Ui.BtnOff, GUILayout.Width(150), GUILayout.Height(44)) && canBait) State.BuyBait();
            GUILayout.EndHorizontal();
            GUILayout.Space(4);
            GUILayout.BeginHorizontal(Ui.Card);
            GUILayout.Label($"Food: {State.FoodMinutes:0.0}/{State.FoodCapacity:0} min\n<size=12>Each crew member eats one minute per minute. No food: 70% speed.</size>", Ui.Body);
            int cost = State.FoodFillCost;
            bool canFood = cost > 0 && State.Coins >= cost;
            if (GUILayout.Button(cost > 0 ? $"Fill up for {cost}" : "Full", canFood ? Ui.Btn : Ui.BtnOff, GUILayout.Width(150), GUILayout.Height(44)) && canFood) State.FillFood();
            GUILayout.EndHorizontal();

            GUILayout.Space(12);
            GUILayout.Label("Boat upgrades", Ui.H2);
            foreach (var u in GameData.Upgrades)
            {
                GUILayout.BeginHorizontal(Ui.Card);
                GUILayout.BeginVertical();
                GUILayout.Label(u.Name, Ui.Body);
                GUILayout.Label(u.Desc, Ui.Mutedish);
                GUILayout.EndVertical();
                bool owned = State.Has(u.Id);
                bool can = !owned && State.Coins >= u.Cost;
                if (GUILayout.Button(owned ? "Owned" : $"{u.Cost}", can ? Ui.Btn : Ui.BtnOff, GUILayout.Width(110), GUILayout.Height(44)) && can)
                {
                    State.TryBuy(u.Id);
                    SyncUpgrades();
                }
                GUILayout.EndHorizontal();
                GUILayout.Space(4);
            }
            GUILayout.Space(12);
            GUILayout.BeginVertical(Ui.Card);
            GUILayout.Label("Skiff refit", Ui.Body);
            GUILayout.Label($"Land {GameData.SkiffFishGoal} fish in one voyage and pay {GameData.SkiffCost} coins. Your boat becomes a skiff: room for a fisherman and the first net. Arrives in the next build.", Ui.Mutedish);
            GUILayout.EndVertical();
        }
    }
}

using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // Voyage HUD in the UI v2 system (docs/screens/ui-concept/voyage-hud.webp): status slab and ground
    // slab on the left, crew rail on the right, Head home with Crew / Ops at the bottom right.
    public partial class VoyageGame
    {
        const float Edge = 16;
        float HudLeftWidth => compactInterface ? 250 : 300;
        float HudRailWidth => compactInterface ? 84 : 300;
        float HudButtonHeight => compactInterface ? 64 : 84;

        // The open water between the left cluster and the crew rail, for toasts and guidance.
        float HudGapLeft => Edge + HudLeftWidth + (compactInterface ? 0 : 36) + 12;
        float HudGapRight => iw - Edge - HudRailWidth - 12;
        void InterfaceVoyageHud()
        {
            coastalUi.BubbleTop = Edge + 72 + 8;
            coastalUi.BubbleLeft = Edge + HudLeftWidth + 8; coastalUi.BubbleRight = iw - Edge - HudRailWidth - 8;
            InterfaceVoyageStatus();
            InterfaceVoyageGround();
            InterfaceVoyageCrewRail();
            InterfaceVoyageActions();
        }

        void InterfaceVoyageStatus()
        {
            var r = new Rect(Edge, Edge, HudLeftWidth + (compactInterface ? 0 : 36), compactInterface ? 56 : 72);
            var slab = coastalUi.Slab("voyage/status", r); Block(r);
            float h = r.height, icon = h - 22, half = r.width * .44f;
            coastalUi.Icon("voyage/status/sun", new Rect(12, 11, icon, icon), "v2-icon-sun", slab, null, "icon-sun");
            coastalUi.Text("voyage/status/day", new Rect(icon + 20, 6, half - icon - 24, h * .42f), $"DAY {State.Voyage}", Skin.Type.Small, Skin.Ink, TextAnchor.LowerLeft, slab);
            // Elapsed voyage time, not a time of day; it pauses with the simulation.
            int seconds = Mathf.FloorToInt(Mathf.Max(0, SimTime - voyageStart));
            string elapsed = seconds < 6000 ? $"{seconds / 60:00}:{seconds % 60:00}" : seconds < 360000 ? $"{seconds / 3600}h{seconds % 3600 / 60:00}" : $"{seconds / 86400}d{seconds % 86400 / 3600:00}";
            coastalUi.Text("voyage/status/time", new Rect(icon + 20, h * .44f, half - icon - 24, h * .44f), elapsed, Skin.Type.Heading, Skin.Ink, TextAnchor.UpperLeft, slab);
            coastalUi.Sliced("voyage/status/rule", new Rect(half, 12, 2, h - 24), "v2-rule", slab);
            coastalUi.Icon("voyage/status/coin", new Rect(half + 14, 11, icon, icon), "v2-icon-coin", slab, null, "icon-coin");
            coastalUi.Text("voyage/status/coins", new Rect(half + icon + 22, 0, r.width - half - icon - 30, h - 2), ReferenceCoinBalance(), Skin.Type.Number, Skin.Ink, TextAnchor.MiddleLeft, slab);
        }

        (string text, float progress) VoyageGoal()
        {
            // Contracts advance when fish are sold, so fish still in the hold do not complete a goal.
            if (State.Active.Count > 0)
            {
                var contract = State.Active[0];
                return ($"Sell {contract.Title} · {contract.Delivered}/{contract.Count}", contract.Delivered / (float)Mathf.Max(1, contract.Count));
            }
            if (State.Hull == 0 && State.BestVoyageFish < GameData.SkiffFishGoal)
                return ($"Sell {GameData.SkiffFishGoal} in one haul · {State.BestVoyageFish}/{GameData.SkiffFishGoal}", State.BestVoyageFish / (float)Mathf.Max(1, GameData.SkiffFishGoal));
            if (State.Hull == 0)
                return (State.CanRefit ? "Skiff refit ready" : $"Save {GameData.SkiffCost:N0} coins", State.Coins / (float)Mathf.Max(1, GameData.SkiffCost));
            return ("fill the hold", HoldKg / Mathf.Max(.01f, State.CoolerCapacity));
        }

        void InterfaceVoyageGround()
        {
            float top = Edge + (compactInterface ? 56 : 72) + 12, tileH = compactInterface ? 52 : 74, gap = compactInterface ? 6 : 8;
            var r = new Rect(Edge, top, HudLeftWidth, Skin.HeaderBand + 12 + tileH * 4 + gap * 3 + 14);
            var slab = coastalUi.Slab("voyage/ground", r, GameData.Spots[ActiveSpot].Name); Block(r);
            coastalUi.Icon("voyage/ground/boat", new Rect(12, 9, 30, 30), "v2-icon-anchor", slab, Skin.Cream, "icon-home-anchor");
            coastalUi.Text("voyage/ground/title", new Rect(48, 4, r.width - 60, Skin.HeaderBand), GameData.Spots[ActiveSpot].Name.ToUpperInvariant(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, slab);
            float x = 10, w = r.width - 20, y = Skin.HeaderBand + 12;
            float hold = HoldKg / Mathf.Max(.01f, State.CoolerCapacity);
            coastalUi.StatTile("voyage/hold", new Rect(x, y, w, tileH), "v2-icon-hold", "Hold", $"{HoldKg:0} / {State.CoolerCapacity:0} kg", hold, hold > .9f ? Skin.Bar.Warn : Skin.Bar.Good, slab, "icon-cooler");
            y += tileH + gap;
            if (State.Hull > 0)
                coastalUi.StatTile("voyage/fuel", new Rect(x, y, w, tileH), "v2-icon-fuel", "Fuel", $"{State.FuelFraction * 100:0}%", State.FuelFraction, State.FuelFraction < .2f ? Skin.Bar.Bad : Skin.Bar.Good, slab, "icon-fuel");
            else coastalUi.StatTile("voyage/fuel", new Rect(x, y, w, tileH), "v2-icon-fuel", "Oars", "No fuel needed", null, Skin.Bar.Good, slab, "icon-fuel");
            y += tileH + gap;
            if (State.Chum > 0) coastalUi.StatTile("voyage/bait", new Rect(x, y, w, tileH), "v2-icon-chum", "Chum", State.Chum.ToString(), null, Skin.Bar.Good, slab);
            else if (State.WillUseSquid) coastalUi.StatTile("voyage/bait", new Rect(x, y, w, tileH), "v2-icon-squid", "Squid", State.Squid.ToString(), null, Skin.Bar.Good, slab, "icon-bait-squid");
            else if (State.Bait > 0) coastalUi.StatTile("voyage/bait", new Rect(x, y, w, tileH), "v2-icon-worms", "Worms", State.Bait.ToString(), null, Skin.Bar.Good, slab, "icon-bait-worm");
            else coastalUi.StatTile("voyage/bait", new Rect(x, y, w, tileH), "v2-icon-bait-scraps", "Bait", "Scraps", null, Skin.Bar.Good, slab);
            y += tileH + gap;
            var goal = VoyageGoal();
            coastalUi.StatTile("voyage/goal", new Rect(x, y, w, tileH), "v2-icon-goal", null, "Goal: " + char.ToLowerInvariant(goal.text[0]) + goal.text.Substring(1), null, Skin.Bar.Good, slab, "icon-target");

            // Fish waiting to be stowed hang off the ground slab as a tag.
            var pending = UnstowedHaul();
            var haul = CurrentHaul();
            if (pending.Count == 0 && haul.Count == 0) return;
            // Phone: the tag joins the bottom-left row beside the last-net review.
            var tag = compactInterface ? new Rect(Edge, ih - Edge - 56, 250, 56) : new Rect(Edge + 12, r.yMax + 12, HudLeftWidth - 12, 74);
            var t = coastalUi.Slab("voyage/stow", tag); Block(tag);
            float s = tag.height - 24;
            coastalUi.Icon("voyage/stow/icon", new Rect(14, 12, s * 1.3f, s), "v2-icon-fish", t, null, "icon-fish");
            coastalUi.Text("voyage/stow/title", new Rect(s * 1.3f + 24, 6, tag.width - s * 1.3f - 34, tag.height * .5f), pending.Count > 0 ? $"{pending.Count} fish to stow" : "Haul stowed", Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, t);
            coastalUi.Text("voyage/stow/time", new Rect(s * 1.3f + 24, tag.height * .5f + 2, tag.width - s * 1.3f - 34, tag.height * .4f), FreshnessStatus(haul, SimTime), Skin.Type.Small, Skin.Ink, TextAnchor.UpperLeft, t);
        }

        static string RoleTitle(Person person, Person captain)
        {
            if (person == captain) return "Captain";
            return person.Contract.Role == CrewRole.Engineer ? "Engineer" : person.Contract.Role == CrewRole.Fisherman ? "Fisher"
                : person.Contract.WorkPreference == DeckhandWork.Prep ? "Processor" : "Deckhand";
        }
        static string Speciality(Person person, Person captain) => person == captain ? "v2-icon-wheel"
            : person.Contract.Role == CrewRole.Engineer ? "v2-icon-engine" : person.Contract.Role == CrewRole.Fisherman ? "v2-icon-fish" : "v2-icon-net";
        // Fishers wear the navy beanie, deckhands and processors the orange one (concept crew rail).
        static string PortraitKey(Person person, Person captain) => person == captain ? "captain"
            : person.Contract.Role == CrewRole.Engineer ? "engineer" : person.Contract.Role == CrewRole.Fisherman ? person.Name : person.Name + "-deck";

        void InterfaceVoyageCrewRail()
        {
            var people = People.ToList();
            float bottom = ih - Edge - HudButtonHeight - 12;
            float w = HudRailWidth, rowGap = 6;
            if (compactInterface) rowGap = 4;
            float rowH = Mathf.Clamp((bottom - Edge - Skin.HeaderBand - 22 - rowGap * (people.Count - 1)) / Mathf.Max(1, people.Count), compactInterface ? 30 : 56, compactInterface ? 56 : 80);
            var r = new Rect(iw - Edge - w, Edge, w, Skin.HeaderBand + (compactInterface ? 36 : 22) + people.Count * rowH + (people.Count - 1) * rowGap);
            if (compactInterface)
            {
                // Phone rail: portraits only, under a compact count header.
                var slab = coastalUi.Slab("voyage/crew", r); Block(r);
                // The header is the menu: the existing pause action under its stable id, with the crew count.
                coastalUi.IconButton("pause", new Rect(6, 6, w - 12, Skin.HeaderBand + 4), "v2-icon-menu", null, () => paused = true, slab, "icon-menu");
                coastalUi.Text("voyage/crew/title", new Rect(6, Skin.HeaderBand + 8, w - 12, 18), $"{people.Count}/{State.HullDef.CrewCap + 1}", Skin.Type.Caption, Skin.Ink, TextAnchor.MiddleCenter, slab);
                for (int i = 0; i < people.Count; i++)
                    coastalUi.Portrait($"voyage/crew/{i}", new Rect((w - rowH) / 2, Skin.HeaderBand + 28 + i * (rowH + rowGap), rowH, rowH), PortraitKey(people[i], Captain), slab);
                return;
            }
            // The hamburger keeps the existing pause action under its stable "pause" id.
            var rail = coastalUi.CrewRail("voyage/crew", r, people.Count, State.HullDef.CrewCap + 1, () => paused = true, "pause"); Block(r);
            for (int i = 0; i < people.Count; i++)
            {
                var person = people[i];
                bool captain = person == Captain;
                var rod = Rods.FirstOrDefault(rd => rd.Fisher == person);
                string activity = captain && Manning != null ? AwaitingCast ? "Ready to cast" : Manning.StateText : rod?.StateText ?? person.State;
                string status = captain ? State.Hull > 0 ? $"Fuel {State.FuelFraction * 100:0}% · {activity}" : activity : $"{person.Contract.VoyagesLeft} trips · {activity}";
                // The bar shows only a timed job: reeling, a bite window or a busy task.
                float? job = rod != null && rod.State == RodState.Reeling ? rod.ReelProgress : person.Busy ? person.BusyProgress : (float?)null;
                coastalUi.CrewCard($"voyage/crew/{i}", new Rect(10, Skin.HeaderBand + 14 + i * (rowH + rowGap), w - 20, rowH), PortraitKey(person, Captain),
                    RoleTitle(person, Captain), captain ? "You" : person.Name, Capitalise(status), Speciality(person, Captain), job, false, null, rail);
            }
        }
        static string Capitalise(string s) => string.IsNullOrEmpty(s) ? s : char.ToUpperInvariant(s[0]) + s.Substring(1);

        void InterfaceVoyageActions()
        {
            float h = HudButtonHeight, tile = compactInterface ? 64 : 80;
            var ops = new Rect(iw - Edge - tile, ih - Edge - h, tile, h);
            var crew = new Rect(ops.x - 10 - tile, ops.y, tile, h);
            bool panels = !(ManagementOpen || netOrdersOpen || PrepOrdersOpen || baitSettingsCrew != null || NetGameActive);
            if (panels)
            {
                coastalUi.IconButton("management/open", ops, "v2-icon-ops", "Ops", () => { OpenManagement(); managementTab = 1; audio?.Play(VoyageAudio.Cue.Select, .45f); }, null, "icon-crate"); Block(ops);
                coastalUi.IconButton("management/crew", crew, "v2-icon-crew", "Crew", () => { OpenManagement(); managementTab = 2; audio?.Play(VoyageAudio.Cue.Select, .45f); }, null, "icon-crew"); Block(crew);
            }
            float pw = compactInterface ? 230 : 330, ph = compactInterface ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight + 16;
            var home = new Rect(crew.x - 14 - pw, ih - Edge - ph, pw, ph);
            coastalUi.Primary("home", home, "Head home", () => { RequestHeadHome(); audio?.Play(VoyageAudio.Cue.Select, .45f); }, "v2-icon-home"); Block(home);
        }
    }
}

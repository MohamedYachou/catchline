using System;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // Operations and Crew pages in the UI v2 system (docs/screens/ui-concept/operations.webp, crew.webp;
    // BLUEPRINT section 15). Status is a word, queues are fish, and there is one primary action per page.
    public partial class VoyageGame
    {
        static readonly string[] StageTitles = { "Fishing", "Hauling in", "Processing", "To hold" };
        static readonly string[] StageIcons = { "v2-icon-rod", "v2-icon-haul", "v2-icon-table", "v2-icon-hold" };
        static readonly string[] StageArt = { "v2-stage-fishing", "v2-stage-hauling", "v2-stage-processing", "v2-stage-hold" };

        // Measuring (-1) has no word of its own: a stage that is not yet measured is steady.
        static Skin.Status StageStatus(int s) => s == 2 ? Skin.Status.BackedUp : s == 1 ? Skin.Status.Busy : Skin.Status.Steady;
        int StageQueue(int stage) => stage switch
        {
            1 => OnDeck.Count + People.Count(p => p.Carrying != null),
            2 => IsPrepFisher ? ProcessingInput.Count : 0,
            3 => IsPrepFisher ? ProcessingOutput.Count : 0,
            _ => 0
        };
        static string Rate(float perMinute) => perMinute >= 9.95f || perMinute <= 0 ? Mathf.RoundToInt(perMinute).ToString() : perMinute.ToString("0.#");

        float PageRailWidth => compactInterface ? 84 : 300;
        Rect PageBody => new(Edge, Edge, iw - Edge * 2 - PageRailWidth - 12, ih - Edge * 2);

        void InterfaceManagementPages()
        {
            ReportManagement(); Block(new Rect(0, 0, iw, ih));
            if (managementTab != 2) managementTab = 1; // the income dashboard is retired in UI v2
            coastalUi.Planks("management/planks");
            var body = PageBody;
            float headH = compactInterface ? 56 : 80;
            coastalUi.PageHeader("management/header", new Rect(body.x, body.y, body.width, headH), managementTab == 1 ? "Operations" : "Crew",
                $"{GameData.Spots[ActiveSpot].Name}\nDay {State.Voyage}", CloseManagement, "v2-icon-sun", "management/close", (compactInterface ? 240 : 300) + 24);
            float sw = compactInterface ? 240 : 300;
            coastalUi.PageSwitch("management/tab", new Rect(body.xMax - sw - 12, body.y + (headH - (compactInterface ? 44 : 56)) / 2, sw, compactInterface ? 44 : 56),
                new[] { "Operations", "Crew" }, managementTab == 1 ? 0 : 1, i => { managementTab = i == 0 ? 1 : 2; dashboardDetail = -1; audio?.Play(VoyageAudio.Cue.Select, .35f); },
                new[] { "management/tab/operations", "management/tab/crew" });
            var content = new Rect(body.x, body.y + headH + 12, body.width, body.height - headH - 12);
            if (managementTab == 1) OperationsPage(content); else CrewPage(content);
            ManagementRail();
            if (dashboardDetail >= 0) StageDetail();
        }

        void OperationsPage(Rect area)
        {
            float holdH = compactInterface ? 0 : 76, warnH = compactInterface ? 72 : 96, gap = compactInterface ? 8 : 12;
            float cardsH = area.height - warnH - holdH - gap * (compactInterface ? 1 : 2);
            float arrow = compactInterface ? 18 : 28, cw = (area.width - arrow * 3 - 12) / 4;
            for (int i = 0; i < 4; i++)
            {
                int stage = i;
                var r = new Rect(area.x + i * (cw + arrow + 4), area.y, cw, cardsH);
                bool fitted = i != 2 || IsPrepFisher;
                coastalUi.StageCard($"management/stage-card/{i}", r, StageTitles[i], StageIcons[i], StageArt[i],
                    fitted ? Rate(stageOutput[i]) : "—", "fish/min", StageStatus(stageStatus[i]), StageQueue(i), () => dashboardDetail = 3 + stage,
                    fitted ? null : "No processing station", $"management/stage/{i}");
                if (i < 3) coastalUi.Icon($"management/flow/{i}", new Rect(r.xMax + (arrow - arrow * .9f) / 2 + 2, r.y + cardsH * .36f, arrow * .9f, arrow * 1.15f), "v2-arrow-flow");
            }
            // One recommendation with one action.
            var w = new Rect(area.x, area.y + cardsH + gap, area.width, warnH);
            string title, line, action; Action act; string icon;
            bool blockedOrders = ProcessingInput.Count > 0 && !ProcessingInput.Any(f => State.PrepOrders.Allows(f, false) || State.Chum < State.PrepOrders.ChumTarget && State.PrepOrders.Allows(f, true));
            if (HoldFull) { title = "The hold is full"; line = "Head home to sell your haul."; action = "Head home"; act = () => { CloseManagement(); RequestHeadHome(); }; icon = "v2-icon-home"; }
            else if (blockedOrders) { title = "Processing is waiting"; line = "Allow the queued fish in the table orders."; action = "Table orders"; act = () => { CloseManagement(); PrepOrdersOpen = true; }; icon = "v2-icon-table"; }
            else if (Bottleneck >= 0) { title = $"{StageTitles[Bottleneck]} is backing up"; line = Recommendation.Replace('\n', ' '); action = "Assign crew"; act = () => { managementTab = 2; }; icon = "v2-icon-crew"; }
            else { title = "Every stage is steady"; line = "Capacity is free. Keep an eye on the queues."; action = "Back to sea"; act = CloseManagement; icon = "v2-icon-anchor"; }
            var slab = coastalUi.Slab("management/advice", w, null, true);
            float s = warnH - 28;
            coastalUi.Icon("management/advice/icon", new Rect(18, 14, s, s), Bottleneck >= 0 || HoldFull || blockedOrders ? "v2-icon-warning" : "v2-icon-tick", slab);
            float bw = compactInterface ? 220 : 300;
            coastalUi.Text("management/advice/title", new Rect(s + 34, 8, w.width - s - bw - 60, (warnH - 16) * .55f), title, compactInterface ? Skin.Type.Heading : Skin.Type.Display, Skin.Ink, TextAnchor.LowerLeft, slab);
            coastalUi.Text("management/advice/line", new Rect(s + 34, 8 + (warnH - 16) * .55f, w.width - s - bw - 60, (warnH - 16) * .45f), line, Skin.Type.Body, Skin.Ink, TextAnchor.UpperLeft, slab);
            float bh = compactInterface ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight;
            coastalUi.Primary("management/recommendation", new Rect(w.width - bw - 18, (warnH - bh) / 2 - 2, bw, bh), action, () => { act(); audio?.Play(VoyageAudio.Cue.Select, .45f); }, icon, true, slab);
            if (compactInterface) return;
            var h = new Rect(area.x, w.yMax + gap, area.width, holdH);
            var hold = coastalUi.Slab("management/hold", h, null, true);
            coastalUi.Icon("management/hold/icon", new Rect(20, 8, 72, 60), "v2-icon-hold", hold);
            coastalUi.Text("management/hold/label", new Rect(106, 6, 260, 26), "MAIN HOLD", Skin.Type.Small, Skin.Ink, TextAnchor.LowerLeft, hold);
            coastalUi.Text("management/hold/value", new Rect(106, 30, 260, 40), $"{HoldKg:0} / {State.CoolerCapacity:0} kg", Skin.Type.Number, Skin.Ink, TextAnchor.UpperLeft, hold);
            coastalUi.ProgressBar("management/hold/bar", new Rect(380, (holdH - 22) / 2, h.width - 420, 22), HoldKg / Mathf.Max(.01f, State.CoolerCapacity), HoldFull ? Skin.Bar.Bad : Skin.Bar.Good, hold);
        }

        void CrewPage(Rect area)
        {
            var crew = State.Crew.ToArray();
            var panel = coastalUi.Slab("management/crew/panel", new Rect(area.x, area.y, area.width, area.height - (compactInterface ? 72 : 96) - 12), null, true);
            float pw = area.width, ph = area.height - (compactInterface ? 72 : 96) - 12;
            if (crew.Length == 0)
            {
                coastalUi.Text("management/crew/empty", new Rect(24, 24, pw - 48, ph - 48), "Hire fishers and deckhands at the Crew Office.", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, panel);
                CrewFooter(area, "Hire crew in the harbour.");
                return;
            }
            selectedManagementCrew = Mathf.Clamp(selectedManagementCrew, 0, crew.Length - 1);
            var c = crew[selectedManagementCrew];
            var person = People.FirstOrDefault(p => p.Contract == c);
            bool fisher = c.Role == CrewRole.Fisherman;
            // Large portrait card, name and role.
            float big = compactInterface ? Mathf.Min(150, ph - 32) : Mathf.Min(260, ph * .62f);
            coastalUi.Card("management/crew/portrait", new Rect(16, 16, big, big), Skin.Card.Soft, panel);
            string key = c.Role == CrewRole.Engineer ? "engineer" : fisher ? c.Name : c.Name + "-deck";
            coastalUi.Icon("management/crew/portrait/art", new Rect(24, 22, big - 16, big - 14), "v2-portrait-" + key.ToLowerInvariant(), panel);
            float x = big + 36, wRight = pw - x - 16;
            coastalUi.Text("management/crew/name", new Rect(x, 8, wRight * .5f, compactInterface ? 40 : 64), c.Name.ToUpperInvariant(), Skin.Type.Display, Skin.Ink, TextAnchor.LowerLeft, panel);
            if (!compactInterface) coastalUi.SetTextSize("management/crew/name", 56);
            string role = person != null ? RoleTitle(person, Captain) : c.RoleName;
            coastalUi.Text("management/crew/role", new Rect(x, compactInterface ? 46 : 72, wRight * .5f, 30), role, Skin.Type.Heading, Skin.Teal, TextAnchor.UpperLeft, panel);
            // Grade stands in for the concept's speciality until crew specialities exist. TODO(BLUEPRINT)
            coastalUi.Portrait("management/crew/grade", new Rect(x + wRight * .52f, 14, 64, 64), fisher ? "fish" : "net", panel);
            coastalUi.Icon("management/crew/grade/icon", new Rect(x + wRight * .52f + 12, 26, 40, 40), fisher ? "v2-icon-net" : "v2-icon-haul", panel);
            coastalUi.Text("management/crew/grade/label", new Rect(x + wRight * .52f + 76, 14, wRight * .48f - 80, 64), GradeLabel(c.Grade), Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, panel);
            float top = compactInterface ? 88 : 116;
            var choices = new Rect(x, top, wRight, ph - top - 16);
            if (fisher) FisherChoices(c, choices, panel); else DeckhandChoices(c, choices, panel);
            CrewFooter(area, "Changes apply after the current job.");
        }

        void FisherChoices(CrewMember c, Rect r, Transform panel)
        {
            // Gear family toggles: the game's own work ticks, in its priority order.
            var tasks = new[] { FisherTask.Nets, FisherTask.Crabs, FisherTask.DeepLines, FisherTask.Rods };
            string[] names = { "Nets", compactInterface ? "Cages" : "Crab cages", "Deep lines", "Rods" }, icons = { "v2-icon-net", "v2-icon-cage", "v2-icon-line", "v2-icon-rod" };
            // Desktop stacks gear over bait; the phone panel is too short, so the two sit side by side.
            bool side = compactInterface;
            float half = side ? r.height : (r.height - 12) / 2, sw = side ? (r.width - 12) / 2 : r.width, gw = (sw - 36) / 4;
            var gear = coastalUi.Card("management/crew/gear", new Rect(r.x, r.y, sw, half), Skin.Card.Ink, panel, "");
            coastalUi.Text("management/crew/gear/title", new Rect(Skin.CardPad + 4, 4, sw - 32, Skin.HeaderBand), "GEAR", Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, gear);
            for (int i = 0; i < 4; i++)
            {
                var task = tasks[i]; bool on = c.Allows(task);
                bool fitted = task == FisherTask.Rods ? FittedRodCount > 0 : task == FisherTask.Nets ? FittedNetCount > 0 : task == FisherTask.Crabs ? FittedTrapCount > 0 : DeepLinesActive;
                ChoiceCard("management/crew/task/" + task, new Rect(12 + i * (gw + 4), Skin.HeaderBand + 10, gw, half - Skin.HeaderBand - 18), icons[i], names[i], on,
                    fitted ? null : "Not fitted", () => ToggleFisherTask(c, task), gear);
            }
            var bait = coastalUi.Card("management/crew/bait", side ? new Rect(r.x + sw + 12, r.y, sw, half) : new Rect(r.x, r.y + half + 12, r.width, half), Skin.Card.Ink, panel, "");
            coastalUi.Text("management/crew/bait/title", new Rect(Skin.CardPad + 4, 4, sw - 32, Skin.HeaderBand), "ALLOWED BAIT", Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, bait);
            var baits = new[] { BaitPermission.Scraps, BaitPermission.Worms, BaitPermission.Squid, BaitPermission.Chum };
            string[] baitIcons = { "v2-icon-bait-scraps", "v2-icon-worms", "v2-icon-squid", "v2-icon-chum" };
            for (int i = 0; i < 4; i++)
            {
                var b = baits[i];
                ChoiceCard("management/crew/bait/" + b, new Rect(12 + i * (gw + 4), Skin.HeaderBand + 10, gw, half - Skin.HeaderBand - 18), baitIcons[i], b.ToString(), (c.BaitPolicy & b) != 0,
                    null, () => ToggleCrewBait(c, b), bait);
            }
        }

        void DeckhandChoices(CrewMember c, Rect r, Transform panel)
        {
            // One chosen duty; the hauling that fills idle time is shown, not chosen. TODO(BLUEPRINT): true secondary duty.
            var duties = IsPrepFisher ? new[] { DeckhandWork.Fish, DeckhandWork.Nets, DeckhandWork.Prep } : new[] { DeckhandWork.Fish, DeckhandWork.Nets };
            string Name(DeckhandWork d) => d == DeckhandWork.Fish ? "Haul catch" : d == DeckhandWork.Nets ? "Nets first" : "Prep table";
            string Icon(DeckhandWork d) => d == DeckhandWork.Fish ? "v2-icon-haul" : d == DeckhandWork.Nets ? "v2-icon-net" : "v2-icon-table";
            int index = Mathf.Max(0, Array.IndexOf(duties, c.WorkPreference));
            float half = (r.width - 16) / 2, h = Mathf.Min(compactInterface ? 120 : 190, r.height - (IsPrepFisher ? (compactInterface ? 60 : 76) : 0));
            coastalUi.DutySlot("management/crew/duty", new Rect(r.x, r.y, half, h), "Primary", Icon(c.WorkPreference), Name(c.WorkPreference),
                () => { var next = duties[(index + 1) % duties.Length]; SetDeckhandWork(c, next); audio?.Play(VoyageAudio.Cue.Select, .35f); }, "Tap to cycle", panel);
            var follow = c.WorkPreference == DeckhandWork.Fish ? DeckhandWork.Prep : DeckhandWork.Fish;
            coastalUi.DutySlot("management/crew/secondary", new Rect(r.x + half + 16, r.y, half, h), "Secondary", c.WorkPreference == DeckhandWork.Fish ? "v2-icon-hold" : "v2-icon-haul",
                c.WorkPreference == DeckhandWork.Fish ? "Carry to hold" : Name(follow), null, "When the primary is free", panel);
            if (IsPrepFisher)
                coastalUi.Secondary("management/crew/table-orders", new Rect(r.x, r.y + h + 12, r.width, compactInterface ? 48 : 60), $"Table orders · chum {State.Chum}",
                    () => { CloseManagement(); PrepOrdersOpen = true; }, "v2-icon-table", true, panel);
        }

        void ChoiceCard(string id, Rect r, string icon, string label, bool on, string lockReason, Action toggle, Transform parent)
        {
            coastalUi.Toggle(id, r, on, toggle, parent);
            float s = Mathf.Min(r.width * .55f, r.height - 40);
            coastalUi.Icon(id + "/art", new Rect((r.width - s) / 2, 8, s, s), icon, coastalUi.ElementRect(id), lockReason != null ? new Color(1, 1, 1, .6f) : (Color?)null);
            coastalUi.Text(id + "/label", new Rect(4, r.height - 34, r.width - 8, 28), label, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, coastalUi.ElementRect(id));
            if (lockReason != null) coastalUi.LockChip(id + "/lock", new Rect(6, s - 16, r.width - 12, 28), lockReason, coastalUi.ElementRect(id));
        }

        // The game's lowest grade is called "Deckhand"; on a crew card that reads as a role, so say "New hand".
        static string GradeLabel(Grade g) => g == Grade.Hand ? "New hand" : GameData.GradeName(g);

        void CrewFooter(Rect area, string hint)
        {
            float h = compactInterface ? 72 : 96;
            var r = new Rect(area.x, area.yMax - h, area.width, h);
            var slab = coastalUi.Slab("management/crew/footer", r, null, true);
            coastalUi.Icon("management/crew/footer/icon", new Rect(20, (h - 44) / 2, 44, 44), "v2-icon-clock", slab);
            coastalUi.Text("management/crew/footer/hint", new Rect(78, 0, r.width - 400, h), hint, Skin.Type.Body, Skin.Teal, TextAnchor.MiddleLeft, slab);
            float bh = compactInterface ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight, bw = compactInterface ? 220 : 300;
            coastalUi.Primary("management/crew/done", new Rect(r.width - bw - 18, (h - bh) / 2 - 2, bw, bh), "Done", () => { CloseManagement(); audio?.Play(VoyageAudio.Cue.Select, .45f); }, "v2-icon-tick", true, slab);
        }

        // Crew rail on the management pages: tap a crew member to open their duties.
        void ManagementRail()
        {
            var people = People.ToList();
            float w = PageRailWidth, rowGap = compactInterface ? 4 : 6;
            float rowH = Mathf.Clamp((ih - Edge * 2 - Skin.HeaderBand - 26 - rowGap * (people.Count - 1)) / Mathf.Max(1, people.Count), compactInterface ? 30 : 56, compactInterface ? 56 : 84);
            var r = new Rect(iw - Edge - w, Edge, w, Skin.HeaderBand + (compactInterface ? 36 : 22) + people.Count * rowH + (people.Count - 1) * rowGap);
            var crewList = State.Crew.ToList();
            if (compactInterface)
            {
                var slab = coastalUi.Slab("management/rail", r);
                coastalUi.Text("management/rail/title", new Rect(6, 8, w - 12, 30), $"{people.Count}/{State.HullDef.CrewCap + 1}", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, slab);
                for (int i = 0; i < people.Count; i++)
                {
                    int ci = crewList.IndexOf(people[i].Contract);
                    var pr = new Rect((w - rowH) / 2, Skin.HeaderBand + i * (rowH + rowGap), rowH, rowH);
                    coastalUi.Portrait($"management/rail/{i}", pr, PortraitKey(people[i], Captain), slab);
                    if (ci >= 0) coastalUi.HitArea($"management/crew/select/{ci}", pr, () => { selectedManagementCrew = ci; managementTab = 2; }, slab);
                }
                return;
            }
            var rail = coastalUi.CrewRail("management/rail", r, people.Count, State.HullDef.CrewCap + 1, null);
            for (int i = 0; i < people.Count; i++)
            {
                var person = people[i]; bool captain = person == Captain;
                int ci = captain ? -1 : crewList.IndexOf(person.Contract);
                var rod = Rods.FirstOrDefault(rd => rd.Fisher == person);
                string activity = captain && Manning != null ? AwaitingCast ? "Ready to cast" : Manning.StateText : rod?.StateText ?? person.State;
                float? job = rod != null && rod.State == RodState.Reeling ? rod.ReelProgress : person.Busy ? person.BusyProgress : (float?)null;
                coastalUi.CrewCard(ci >= 0 ? $"management/crew/select/{ci}" : "management/rail/captain", new Rect(10, Skin.HeaderBand + 14 + i * (rowH + rowGap), w - 20, rowH), PortraitKey(person, Captain),
                    captain ? "Captain" : person.Name, null, RoleTitle(person, Captain) + " · " + Capitalise(activity), null, job,
                    managementTab == 2 && ci == selectedManagementCrew, ci >= 0 ? () => { selectedManagementCrew = ci; managementTab = 2; } : null, rail);
            }
        }

        void StageDetail()
        {
            int stage = Mathf.Clamp(dashboardDetail == 7 && Bottleneck >= 0 ? Bottleneck : dashboardDetail - 3, 0, 3);
            string body = $"{Recommendation.Replace('\n', ' ')}\n\nWorking at {Rate(stageOutput[stage])} fish/min · status {Skin.Word(StageStatus(stageStatus[stage])).ToLowerInvariant()}.\n" +
                $"On deck or carried: {WaitingDeckKg:0.#} kg. Waiting to process: {ProcessingInput.Count}. Ready to carry: {ProcessingOutput.Count}.\nMain hold: {HoldKg:0} / {State.CoolerCapacity:0} kg.";
            bool canHelp = ProcessingOutput.Count > 0 && !HoldFull;
            var slab = coastalUi.Modal("management/detail", StageTitles[stage], body,
                canHelp ? "Help carry" : IsPrepFisher ? "Table orders" : "Crew duties",
                canHelp ? () => { CloseManagement(); HelpCarryProcessed(); } : IsPrepFisher ? () => { CloseManagement(); PrepOrdersOpen = true; } : () => { dashboardDetail = -1; managementTab = 2; },
                "Close", () => dashboardDetail = -1, () => dashboardDetail = -1, canHelp ? "v2-icon-haul" : IsPrepFisher ? "v2-icon-table" : "v2-icon-crew", 640, 380);
            coastalUi.Alias("management/detail/close", "management/detail/secondary");
            coastalUi.Alias(canHelp ? "management/help" : IsPrepFisher ? "management/orders" : "management/duties", "management/detail/primary");
        }

    }
}

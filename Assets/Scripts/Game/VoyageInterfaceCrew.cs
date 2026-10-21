using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        Rect ReferenceRect(float x, float y, float width, float height)
        {
            float scale = ih / FishReferenceStyle.Height;
            return new Rect(x * scale, y * scale, width * scale, height * scale);
        }
        Rect ReferenceRightRect(float x, float y, float width, float height)
        {
            var r = ReferenceRect(x, y, width, height);
            r.x += iw - FishReferenceStyle.Width * ih / FishReferenceStyle.Height;
            return r;
        }
        static float ReferenceRowTop(int i) => i switch { 0 => 130, 1 => 215, 2 => 301, 3 => 387, 4 => 475, _ => 562 + (i - 5) * 86 };
        float ReferenceCrewBottom => (ReferenceRowTop(Mathf.Max(1, People.Count()) - 1) + 91) * ih / FishReferenceStyle.Height;
        void InterfaceReferenceCrew()
        {
            var people = People.ToList();
            var toolbar = ReferenceRightRect(1407, 25, 248, 49);
            coastalUi.ReferencePanel("reference/crew/toolbar", toolbar, FishReferenceStyle.PanelKind.Toolbar);
            Block(toolbar);
            coastalUi.ReferenceIcon("reference/crew/badge", ReferenceRightRect(1418, 31, 40, 38), FishReferenceStyle.Icon.Badge);
            coastalUi.ReferenceIcon("reference/crew/group", ReferenceRightRect(1470, 39, 28, 26), FishReferenceStyle.Icon.Crew);
            coastalUi.ReferenceLabel("reference/crew/title", ReferenceRightRect(1501, 38, 58, 28), "Crew", 18, true);
            // Reference includes captain in its total. Gameplay CrewCap excludes captain.
            coastalUi.ReferenceLabel("reference/crew/count", ReferenceRightRect(1560, 38, 43, 27),
                $"{people.Count}/{State.HullDef.CrewCap + 1}", 18, true, TextAnchor.MiddleCenter);
            coastalUi.ReferenceIcon("reference/crew/menu/icon", ReferenceRightRect(1620, 39, 22, 24), FishReferenceStyle.Icon.Menu);
            var menu = ReferenceRightRect(1609, 25, 46, 49);

            var panel = ReferenceRightRect(1365, 85, 290, ReferenceRowTop(Mathf.Max(1, people.Count) - 1) + 91 - 85);
            coastalUi.ReferencePanel("reference/crew/panel", panel, FishReferenceStyle.PanelKind.Crew); Block(panel);
            coastalUi.ReferenceIcon("reference/crew/dot", ReferenceRightRect(1377, 100, 11, 12), FishReferenceStyle.Icon.Bullet);
            coastalUi.ReferenceLabel("reference/crew/heading", ReferenceRightRect(1395, 96, 245, 23), "Crew Roles", 20, true);
            for (int i = 0; i < people.Count; i++)
            {
                var person = people[i];
                float y = ReferenceRowTop(i);
                bool captain = person == Captain;
                bool fisher = !captain && person.Contract.Role == CrewRole.Fisherman;
                string role = captain ? "Captain" : person.Contract.Role == CrewRole.Engineer ? "Engineer" : fisher ? "Fisher" : person.Contract.WorkPreference == DeckhandWork.Prep ? "Processor" : "Deckhand";
                string portrait = captain ? "captain" : fisher ? "fisherman" : "deckhand";
                var row = ReferenceRightRect(1377, y, 268, i == 0 ? 77 : 78);
                coastalUi.ReferencePanel($"reference/crew/{i}/row", row, FishReferenceStyle.PanelKind.Row);
                coastalUi.ReferencePortrait($"reference/crew/{i}/portrait", ReferenceRightRect(1387, y + 8, 57, 60), portrait);
                coastalUi.ReferenceLabel($"reference/crew/{i}/role", ReferenceRightRect(1454, y + (role == "Deckhand" ? 8 : 7), 145, 23), role, 16, true);
                string grade = captain ? "You" : person.Name;
                coastalUi.ReferenceLabel($"reference/crew/{i}/grade", ReferenceRightRect(1599, y + 6, 37, 23), grade, 13, false, TextAnchor.MiddleRight);
                coastalUi.ReferenceIcon($"reference/crew/{i}/icon", ReferenceRightRect(captain ? 1608 : 1606, y + (captain ? 26 : fisher ? 26 : 25), captain ? 28 : fisher ? 30 : 31, captain ? 27 : fisher ? 27 : 29),
                    captain ? FishReferenceStyle.Icon.Wheel : fisher ? FishReferenceStyle.Icon.Fish : FishReferenceStyle.Icon.Net);

                // These are existing resources, NOT invented experience/stamina statistics.
                // Caption explicitly names the quantity represented by the reference-style bar.
                float remaining = captain ? State.Hull > 0 ? State.FuelFraction : 1f
                    : person.Contract.VoyagesLeft / (float)Mathf.Max(1, GameData.ContractVoyages(person.Contract.Grade));
                var rod = Rods.FirstOrDefault(r => r.Fisher == person);
                string activity = captain && Manning != null ? AwaitingCast ? "Ready to cast" : Manning.StateText : rod?.StateText ?? person.State;
                string detail = captain ? State.Hull > 0 ? $"Fuel {State.FuelFraction:P0} · {activity}" : activity : $"{person.Contract.VoyagesLeft} trips · {activity}";
                coastalUi.ReferenceLabel($"reference/crew/{i}/detail", ReferenceRightRect(1455, y + 35, 142, 18), detail, 12);
                coastalUi.ReferenceBar($"reference/crew/{i}/progress", ReferenceRightRect(1455, y + 55, 143, 14), remaining);
                coastalUi.ReferenceLabel($"reference/crew/{i}/percent", ReferenceRightRect(1605, y + 54, 32, 20),
                    $"{Mathf.FloorToInt(Mathf.Clamp01(remaining) * 100)}%", 13, false, TextAnchor.MiddleCenter);
            }
            // Hit area is last so the neighbouring noninteractive header cannot swallow touch.
            Block(coastalUi.ReferenceButton("pause", menu, () => paused = true));
        }
        void InterfaceReferenceSupplies()
        {
            // Retain vital existing haul/bait/fuel information below the requested goal panel.
            var r = ReferenceRect(20, 252, 260, 152);
            coastalUi.ReferencePanel("instruments", r, FishReferenceStyle.PanelKind.Goal); Block(r);
            coastalUi.ReferenceLabel("instruments/place", ReferenceRect(32, 260, 236, 26), GameData.Spots[ActiveSpot].Name, 17, true);
            var secured = State.QuoteSale(Cooler, SimTime);
            coastalUi.ReferenceLabel("hold/amount", ReferenceRect(32, 292, 235, 22), $"Hold {HoldKg:0.00}/{State.CoolerCapacity:0.#} kg", 15, true);
            coastalUi.ReferenceLabel("hold/value", ReferenceRect(150, 292, 117, 22), $"~{secured.Coins + secured.ContractCoins} coins", 14, false, TextAnchor.MiddleRight);
            coastalUi.ReferenceBar("hold/bar", ReferenceRect(32, 321, 235, 10), HoldKg / Mathf.Max(.01f, State.CoolerCapacity));
            coastalUi.ReferenceLabel("fuel/text", ReferenceRect(32, 339, 236, 22), State.Hull > 0 ? $"Fuel · {State.FuelFraction:P0} · return at10%" : "Oars ready · no fuel needed", 14);
            coastalUi.ReferenceLabel("bait/text", ReferenceRect(32, 367, 236, 22), State.Chum > 0 ? $"Chum {State.Chum} / premium hooks" : State.WillUseSquid ? $"Bait · {State.Squid} squid" : State.Bait > 0 ? $"Bait · {State.Bait} worms" : "Bait · unlimited scraps", 14);
            var pending = UnstowedHaul();
            var haul = ReferenceRect(20, 416, 260, pending.Count > 0 ? 100 : 72);
            coastalUi.ReferencePanel("hold/freshness", haul, FishReferenceStyle.PanelKind.Goal); Block(haul);
            coastalUi.ReferenceLabel("hold/freshness/title", ReferenceRect(32, 423, 236, 24), pending.Count > 0 ? $"{pending.Count} fish to stow" : "Haul secured", 16, true);
            coastalUi.ReferenceLabel("hold/freshness/time", ReferenceRect(32, 451, 236, 30), FreshnessStatus(CurrentHaul(), SimTime), 13);
            if (pending.Count > 0)
                coastalUi.ReferenceLabel("hold/pending", ReferenceRect(32, 482, 236, 24), "On deck / carried · needs space", 12);
        }
    }
}

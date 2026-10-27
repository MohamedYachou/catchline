using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Rectangles are measured in the 1672 x 941 reference, then mapped by
        // the shared left-anchored transform. Style and typography stay shared.
        void InterfaceReferenceGoals()
        {
            var status = ReferenceRect(20, 25, 320, 65);
            coastalUi.ReferencePanel("reference/status", status, FishReferenceStyle.PanelKind.Status);
            Block(status);
            coastalUi.ReferenceIcon("reference/status/sun", ReferenceRect(31, 36, 44, 44), FishReferenceStyle.Icon.Sun);
            coastalUi.ReferenceLabel("reference/status/day", ReferenceRect(91, 35, 80, 23), $"Day {State.Voyage}", 18);

            // This is elapsed voyage time, not an invented time of day. SetSail
            // resets voyageStart; simulation pause also pauses this display.
            int seconds = Mathf.FloorToInt(Mathf.Max(0, SimTime - voyageStart));
            // Keep extended sessions inside the same clock slot: minutes below
            // 100 minutes, hours/minutes below 100 hours, then days/hours.
            string elapsed = seconds < 6000 ? $"{seconds / 60:00}:{seconds % 60:00}"
                : seconds < 360000 ? $"{seconds / 3600}h{seconds % 3600 / 60:00}"
                : $"{seconds / 86400}d{seconds % 86400 / 3600:00}";
            coastalUi.ReferenceLabel("reference/status/time", ReferenceRect(91, 58, 80, 24), elapsed, 20, true);
            coastalUi.ReferenceIcon("reference/status/coin", ReferenceRect(194, 37, 38, 41), FishReferenceStyle.Icon.Coin);
            coastalUi.ReferenceLabel("reference/status/coins", ReferenceRect(238, 40, 95, 38), ReferenceCoinBalance(), 30, true);

            string objective;
            string count;
            float progress;
            if (State.Active.Count > 0)
            {
                // Contracts advance when fish are sold. Fish still in the hold
                // are not delivered and cannot claim this goal as complete.
                var contract = State.Active[0];
                int target = Mathf.Max(1, contract.Count);
                objective = $"Sell {contract.Title}";
                count = $"{contract.Delivered}/{contract.Count}";
                progress = contract.Delivered / (float)target;
            }
            else if (State.Hull == 0 && State.BestVoyageFish < GameData.SkiffFishGoal)
            {
                // BestVoyageFish is the actual largest sold haul, not catches
                // lying on deck or a projected record before returning home.
                objective = $"Sell {GameData.SkiffFishGoal} in one haul";
                count = $"{State.BestVoyageFish}/{GameData.SkiffFishGoal}";
                progress = State.BestVoyageFish / (float)Mathf.Max(1, GameData.SkiffFishGoal);
            }
            else if (State.Hull == 0)
            {
                progress = State.Coins / (float)Mathf.Max(1, GameData.SkiffCost);
                objective = State.CanRefit ? "Skiff refit ready" : $"Save {GameData.SkiffCost:N0} coins";
                // A percentage fits the reference counter without squeezing a
                // four-digit coin fraction into the fish-sized counter slot.
                count = $"{Mathf.FloorToInt(Mathf.Clamp01(progress) * 100)}%";
            }
            else
            {
                progress = HoldKg / Mathf.Max(.01f, State.CoolerCapacity);
                objective = $"Hold {HoldKg:0.0}/{State.CoolerCapacity:0.#} kg";
                count = $"{Mathf.Clamp01(progress) * 100:0}%";
            }

            var goal = ReferenceRect(20, 130, 220, 104);
            coastalUi.ReferencePanel("reference/goal", goal, FishReferenceStyle.PanelKind.Goal);
            Block(goal);
            coastalUi.ReferenceIcon("reference/goal/target", ReferenceRect(31, 137, 24, 25), FishReferenceStyle.Icon.Target);
            coastalUi.ReferenceLabel("reference/goal/title", ReferenceRect(64, 138, 166, 23), "Current Goal", 16, true);
            coastalUi.ReferenceIcon("reference/goal/crate", ReferenceRect(30, 178, 39, 43), FishReferenceStyle.Icon.Crate);
            coastalUi.ReferenceLabel("reference/goal/objective", ReferenceRect(75, 172, 155, 20), objective, 13);
            coastalUi.ReferenceBar("reference/goal/progress", ReferenceRect(75, 200, 114, 13), Mathf.Clamp01(progress));
            coastalUi.ReferenceLabel("reference/goal/count", ReferenceRect(197, 198, 34, 20), count, 13, true, TextAnchor.MiddleCenter);
        }

        string ReferenceCoinBalance()
        {
            // Preserve the reference's full balance at ordinary values. Large
            // balances use conventional units rather than overflowing the card.
            // Decimal also handles int.MinValue without an Abs(int) overflow.
            decimal value = State.Coins;
            decimal magnitude = System.Math.Abs(value);
            if (magnitude >= 1000000000m) return (value / 1000000000m).ToString("0.##") + "B";
            if (magnitude >= 100000000m) return (value / 1000000m).ToString("0") + "M";
            if (magnitude >= 1000000m) return (value / 1000000m).ToString("0.#") + "M";
            if (magnitude >= 10000m) return (value / 1000m).ToString("0") + "k";
            return State.Coins.ToString("N0");
        }
    }
}

using UnityEngine;

namespace Catchline.Game
{
    // Under the port slab: what the player is saving for. The jar fills (and counts up with the sale's coin flight)
    // toward the next boat; a haul goal still to meet is shown instead of the coins. Tapping opens the Gear shop.
    public partial class VoyageGame
    {
        (string name, int cost, string blocker)? NextBoat => State.Hull switch
        {
            0 => ("Skiff", GameData.SkiffCost, !State.SkiffHaulDone ? $"Best haul {State.BestVoyageKg:0.#}/{GameData.SkiffKgGoal:0} kg" : null),
            1 => ("Compact fisher", GameState.CompactFisherCost, null),
            2 => ("Jig boat", GameState.JigBoatCost, null),
            5 => ("Prep fisher", GameState.PrepFisherCost, State.BestVoyageKg < GameState.PrepFisherKgGoal ? $"Best haul {State.BestVoyageKg:0}/{GameState.PrepFisherKgGoal} kg" : null),
            3 => ("Buoy fisher", GameState.Tier5Cost, null),
            _ => null,
        };

        bool savingsGoalWasReady;
        void InterfaceSavingsGoal(Rect r)
        {
            if (NextBoat is not { } next) { savingsGoalWasReady = false; return; }
            float progress = Mathf.Clamp01(ShownCoins / (float)next.cost);
            bool ready = progress >= 1 && next.blocker == null;
            if (ready && !savingsGoalWasReady) audio?.Play(VoyageAudio.Cue.GoalReady, .35f);
            savingsGoalWasReady = ready;
            int level = ready ? 4 : Mathf.Min(3, Mathf.FloorToInt(progress * 4));
            string jar = HasUi("goal-jar-" + level) ? "goal-jar-" + level : "v2-icon-coin";
            // Boat name with the coins on the right, the jar's bar under it, then what is still missing.
            var card = coastalUi.Card("port/goal", r, Skin.Card.Soft);
            bool small = compactInterface;
            float icon = r.height - (small ? 12 : 16), x = icon + (small ? 14 : 20), tw = r.width - x - (small ? 10 : 14);
            float row = small ? 22 : 26, top = small ? 4 : 6;
            coastalUi.Icon("port/goal/jar", new Rect(small ? 6 : 8, (r.height - icon) / 2, icon, icon), jar, card, null, "icon-coin");
            coastalUi.Text("port/goal/name", new Rect(x, top, tw * .55f, row), next.name, small ? Skin.Type.Body : Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, card);
            coastalUi.Text("port/goal/coins", new Rect(x + tw * .5f, top, tw * .5f, row), $"{ShownCoins:N0} / {next.cost:N0}", Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleRight, card);
            coastalUi.Bar("port/goal/bar", new Rect(x, top + row + (small ? 2 : 4), tw, small ? 8 : 10), progress, false, card);
            string caption = ready ? "Ready to refit · tap" : next.blocker ?? "Saving for the next boat";
            coastalUi.Text("port/goal/caption", new Rect(x, top + row + (small ? 12 : 14), tw, small ? 18 : 20), caption, Skin.Type.Caption, ready ? Skin.Teal : Skin.InkSoft, TextAnchor.MiddleLeft, card);
            // Ready: a slow pulse invites the tap.
            coastalUi.Pose("port/goal", 0, ready ? 1 + .025f * Mathf.Sin(Time.unscaledTime * 4) : 1);
            coastalUi.HitArea("port/goal/tap", r, () => { OpenShop(HudTab.Chandlery); audio?.Play(VoyageAudio.Cue.Select, .45f); });
            Block(r);
        }
    }
}

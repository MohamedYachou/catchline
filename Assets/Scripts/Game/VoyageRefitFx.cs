using UnityEngine;

namespace Catchline.Game
{
    // A new boat is a milestone: the harbour dims a little (the boat stays in view), the tier badge pops over turning
    // rays, a NEW BOAT ribbon unrolls with the boat's name and what it brings, and confetti falls. A tap skips ahead.
    public partial class VoyageGame
    {
        public const float RefitFxSeconds = 3.6f;
        float refitStart;

        void BeginRefitFx() { refitStart = SimTime; refitUntil = SimTime + RefitFxSeconds; }

        void InterfaceRefitFx()
        {
            float t = SimTime - refitStart, left = refitUntil - SimTime;
            float fade = Ease.Clamp(left / .4f);
            // The refit's toast (what the boat brings, where the welcome chest is) waits until the celebration ends.
            if (toast != null) toastUntil = Mathf.Max(toastUntil, refitUntil + 4f);
            coastalUi.Scrim("refit/dim", () => refitUntil = Mathf.Min(refitUntil, SimTime + .4f), .5f * Ease.Clamp(t / .25f) * fade);

            int tier = Mathf.Clamp(State.CardTier, 1, 5);
            var hull = State.HullDef;
            Color gold = new Color(1f, .82f, .35f);
            float cx = iw / 2, cy = ih * (coastalUi.Phone ? .28f : .3f), badge = coastalUi.Phone ? 92 : 128;

            float pop = Ease.OutBack(Ease.Clamp((t - .12f) / .45f));
            coastalUi.Icon("refit/rays", Centered(cx, cy, badge * 3f, badge * 3f), "fx-rays", null, Tint(gold, .45f * Ease.Clamp(t / .4f) * fade));
            coastalUi.Pose("refit/rays", t * 14f, .85f + .15f * pop);
            coastalUi.Icon("refit/glow", Centered(cx, cy, badge * 2f, badge * 2f), "fx-glow", null, Tint(gold, .75f * fade));
            coastalUi.Icon("refit/badge", Centered(cx, cy, badge, badge), "v2-tier-" + tier, null, Tint(Color.white, fade));
            coastalUi.Pose("refit/badge", (1 - pop) * -18f, pop);
            Sparkles("refit/sparkles", cx, cy, badge * .9f, 8, fade * Ease.Clamp((t - .3f) / .3f));

            float unroll = Ease.OutBack(Ease.Clamp((t - .35f) / .45f));
            float rw = Mathf.Min(iw - 32, coastalUi.Phone ? 380 : 500), rh = rw / 4, ry = cy + badge * .5f + rh * .45f;
            coastalUi.Icon("refit/ribbon", Centered(cx, ry, rw, rh), "fx-rank-ribbon", null, Tint(Color.white, fade));
            coastalUi.Pose("refit/ribbon", 0, 1, unroll);
            coastalUi.Text("refit/ribbon/text", Centered(cx, ry - rh * .06f, rw * .7f, rh * .6f), "NEW BOAT", Skin.Type.Heading, Tint(Skin.Ink, fade * unroll), TextAnchor.MiddleCenter);

            float rise = Ease.OutCubic(Ease.Clamp((t - .6f) / .4f));
            float ny = ry + rh * .5f + (coastalUi.Phone ? 26 : 36) + (1 - rise) * 24;
            coastalUi.Text("refit/name", Centered(cx, ny, iw - 32, coastalUi.Phone ? 44 : 56), hull.Name, Skin.Type.Display, Tint(Skin.Cream, fade * rise), TextAnchor.MiddleCenter, null, true);
            int berths = CardRoster.BerthsForTier(State.CardTier);
            string stats = $"{hull.Capacity} kg hold · {hull.RodTiles.Length} rods · {berths} crew berths";
            float sr = Ease.Clamp((t - .85f) / .4f);
            coastalUi.Text("refit/stats", Centered(cx, ny + (coastalUi.Phone ? 36 : 46), iw - 32, 30), stats, Skin.Type.Body, Tint(Skin.Cream, fade * sr), TextAnchor.MiddleCenter, null, true);

            Confetti("refit/confetti", cx, cy, t - .3f, 40, gold, ih);
            float hint = Ease.Clamp((t - 1.4f) / .4f) * fade;
            coastalUi.Text("refit/hint", new Rect(0, ih - 64, iw, 30), "Tap to continue", Skin.Type.Caption, Tint(Skin.Cream, .8f * hint), TextAnchor.MiddleCenter, null, true);
        }
    }
}

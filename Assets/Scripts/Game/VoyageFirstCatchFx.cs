using UnityEngine;

namespace Catchline.Game
{
    // A species landed for the first time gets a short reveal before its catch card: a trophy card pops up over turning
    // rays, the fish leaps out of a splash into the card's window, a NEW SPECIES ribbon unrolls above it, the name and
    // weight fill the card's band and a NEW stamp slams onto the corner; then the fish drops into the catch card's
    // portrait. Fishing carries on underneath; nothing blocks input.
    public partial class VoyageGame
    {
        const float FirstCatchRevealSeconds = 2.4f, FirstCatchFly = .4f;
        bool firstCatchStampPlayed;

        void InterfaceFirstCatchReveal(float t)
        {
            if (t >= .8f && !firstCatchStampPlayed) { firstCatchStampPlayed = true; audio?.Play(VoyageAudio.Cue.StampThud, .4f); }
            var species = lastCatchSpecies;
            float fade = Ease.Clamp((FirstCatchRevealSeconds - t) / .3f);
            Color teal = new Color(.55f, .9f, .95f), gold = new Color(1f, .82f, .35f);

            // The trophy card (catch-card.png, 512x640; its sea-blue window is x40 y44 w432 h344 from the top left).
            // Phones get a smaller card set lower, so the ribbon above it clears the tutorial banner.
            float cx = (HudGapLeft + HudGapRight) / 2, cy = ih * (compactInterface ? .53f : .48f);
            float cw = compactInterface ? 136 : 250, ch = cw * 1.25f;
            var card = Centered(cx, cy, cw, ch);
            var window = new Rect(card.x + cw * 40 / 512f, card.y + ch * 44 / 640f, cw * 432 / 512f, ch * 344 / 640f);
            float wx = window.center.x, wy = window.center.y;

            coastalUi.Icon("first/rays", Centered(cx, cy, cw * 2.4f, cw * 2.4f), "fx-rays", null, Tint(gold, .4f * Ease.Clamp((t - .1f) / .4f) * fade));
            coastalUi.Pose("first/rays", t * 16f);
            coastalUi.Icon("first/glow", Centered(cx, cy, cw * 1.9f, cw * 1.9f), "fx-glow", null, Tint(teal, .7f * Ease.Clamp(t / .3f) * fade));

            float cardPop = Ease.OutBack(Ease.Clamp(t / .35f));
            coastalUi.Icon("first/card", card, "catch-card", null, Tint(Color.white, fade));
            coastalUi.Pose("first/card", (1 - Ease.Clamp(t / .35f)) * -6f, Mathf.Max(.01f, cardPop));

            // The splash bursts at the bottom of the window and is gone by the time the ribbon lands.
            float sk = Ease.Clamp(t / .55f);
            bool realSplash = HasUi("fx-splash");
            coastalUi.Icon("first/splash", Centered(wx, window.yMax - window.height * .1f, window.width * 1.1f, window.width * 1.1f), realSplash ? "fx-splash" : "fx-burst", null, Tint(realSplash ? Color.white : teal, (1 - sk) * .9f));
            coastalUi.Pose("first/splash", 0, .4f + Ease.OutCubic(sk) * .9f);
            Sparkles("first/sparkles", wx, wy, window.width * .55f, 8, fade * Ease.Clamp((t - .35f) / .3f));

            // The fish leaps up out of the splash into the window, wriggles, then drops into the catch card's portrait frame.
            float fw = window.width * .9f, fh = fw * 2 / 3f;
            if (fh > window.height * .86f) { fh = window.height * .86f; fw = fh * 1.5f; }
            float pop = Ease.OutBack(Ease.Clamp((t - .05f) / .45f)), rise = Ease.OutCubic(Ease.Clamp(t / .4f));
            var fish = Centered(wx, wy + (1 - rise) * window.height * .7f, fw, fh);
            float fly = Ease.InCubic(Ease.Clamp((t - (FirstCatchRevealSeconds - FirstCatchFly)) / FirstCatchFly));
            if (fly > 0)
            {
                float h = compactInterface ? 112 : 132, ph = h - Skin.HeaderBand - 16, art = ph * 1.5f;
                var catchCard = CatchCardRect(h);
                var slot = new Rect(catchCard.x + 18, catchCard.y + Skin.HeaderBand + 10, art - 12, ph - 4);
                fish = Rect.MinMaxRect(Mathf.Lerp(fish.xMin, slot.xMin, fly), Mathf.Lerp(fish.yMin, slot.yMin, fly),
                                       Mathf.Lerp(fish.xMax, slot.xMax, fly), Mathf.Lerp(fish.yMax, slot.yMax, fly));
            }
            coastalUi.Icon("first/fish", fish, FishPortrait(species), null, null, FishPortrait(species));
            coastalUi.Pose("first/fish", Mathf.Sin(t * 10f) * 7f * (1 - Ease.Clamp(t / 1.2f)), Mathf.Lerp(pop, 1, fly));

            // NEW SPECIES unrolls just above the card, its lower edge tucked over the card's top rail.
            float unroll = Ease.OutBack(Ease.Clamp((t - .4f) / .45f));
            float rw = Mathf.Min(HudGapRight - HudGapLeft - 16, compactInterface ? 220 : 380), rh = rw / 4, ry = card.y - rh * .35f;
            coastalUi.Icon("first/ribbon", Centered(cx, ry, rw, rh), "fx-rank-ribbon", null, Tint(Color.white, fade));
            coastalUi.Pose("first/ribbon", 0, 1, unroll);
            coastalUi.Text("first/ribbon/text", Centered(cx, ry - rh * .06f, rw * .7f, rh * .6f), "NEW SPECIES", Skin.Type.Heading, Tint(Skin.Ink, fade * unroll), TextAnchor.MiddleCenter);

            // Name and weight sit in the card's cream band.
            float name = Ease.OutCubic(Ease.Clamp((t - .65f) / .35f));
            float bandTop = card.y + ch * .63f, bandH = ch * .29f;
            coastalUi.Text("first/name", new Rect(card.x + cw * .08f, bandTop + (1 - name) * 10, cw * .84f, bandH * .58f),
                GameData.Get(species).Name, compactInterface ? Skin.Type.Heading : Skin.Type.Display, Tint(Skin.Ink, fade * name), TextAnchor.MiddleCenter);
            coastalUi.Text("first/kg", new Rect(card.x + cw * .08f, bandTop + bandH * .56f + (1 - name) * 10, cw * .84f, bandH * .4f),
                $"{lastCatchKg:0.0} kg", compactInterface ? Skin.Type.Small : Skin.Type.Body, Tint(Skin.Ink, .75f * fade * name), TextAnchor.MiddleCenter);

            // The NEW stamp slams onto the window's top-right corner (only once its sprite is in).
            if (HasUi("fx-stamp-new"))
            {
                float slam = Ease.Clamp((t - .8f) / .16f), size = compactInterface ? 56 : 92;
                coastalUi.Icon("first/stamp", Centered(window.xMax - size * .22f, window.y + size * .3f, size, size), "fx-stamp-new", null, Tint(Color.white, slam * fade));
                coastalUi.Pose("first/stamp", -14f, Mathf.Lerp(2.2f, 1, Ease.OutCubic(slam)));
            }
            Confetti("first/confetti", cx, cy, t - .3f, 24, gold, ih);
        }

        // Captures: put a first-catch reveal on screen, `at` seconds in.
        public void PreviewFirstCatch(Species species, float kg, float at)
        {
            toast = null; lastCatchSpecies = species; lastCatchKg = kg; catchNew = true; catchRecord = false;
            firstCatchStampPlayed = false;
            catchUntil = SimTime + CatchDisplaySeconds + FirstCatchRevealSeconds - at;
        }
    }
}

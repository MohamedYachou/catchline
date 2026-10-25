using UnityEngine;

namespace Catchline.Game
{
    // A species landed for the first time gets a short reveal before its catch card: a splash, the fish popping up over
    // turning rays, a NEW SPECIES ribbon with its name and a NEW stamp, then the fish drops into the card's portrait.
    // Fishing carries on underneath; nothing blocks input.
    public partial class VoyageGame
    {
        const float FirstCatchRevealSeconds = 2.4f, FirstCatchFly = .4f;
        bool firstCatchStampPlayed;

        void InterfaceFirstCatchReveal(float t)
        {
            if (t >= .8f && !firstCatchStampPlayed) { firstCatchStampPlayed = true; audio?.Play(VoyageAudio.Cue.StampThud, .4f); }
            var species = lastCatchSpecies;
            float fade = Ease.Clamp((FirstCatchRevealSeconds - t) / .3f);
            float cx = (HudGapLeft + HudGapRight) / 2, cy = ih * (compactInterface ? .42f : .4f);
            float fw = compactInterface ? 190 : 300, fh = fw * 2 / 3f;
            Color teal = new Color(.55f, .9f, .95f), gold = new Color(1f, .82f, .35f);

            // The splash bursts under the fish and is gone by the time the ribbon lands.
            float sk = Ease.Clamp(t / .55f);
            bool realSplash = HasUi("fx-splash");
            coastalUi.Icon("first/splash", Centered(cx, cy + fh * .3f, fw * 1.3f, fw * 1.3f), realSplash ? "fx-splash" : "fx-burst", null, Tint(realSplash ? Color.white : teal, (1 - sk) * .9f));
            coastalUi.Pose("first/splash", 0, .4f + Ease.OutCubic(sk) * .9f);

            coastalUi.Icon("first/rays", Centered(cx, cy, fw * 2.2f, fw * 2.2f), "fx-rays", null, Tint(gold, .4f * Ease.Clamp((t - .1f) / .4f) * fade));
            coastalUi.Pose("first/rays", t * 16f);
            coastalUi.Icon("first/glow", Centered(cx, cy, fw * 1.6f, fw * 1.6f), "fx-glow", null, Tint(teal, .7f * Ease.Clamp(t / .3f) * fade));
            Sparkles("first/sparkles", cx, cy, fw * .6f, 8, fade * Ease.Clamp((t - .35f) / .3f));

            // The fish leaps up out of the splash, wriggles, then drops into the catch card's portrait frame.
            float pop = Ease.OutBack(Ease.Clamp((t - .05f) / .45f)), rise = Ease.OutCubic(Ease.Clamp(t / .4f));
            var fish = Centered(cx, cy + (1 - rise) * fh * .7f, fw, fh);
            float fly = Ease.InCubic(Ease.Clamp((t - (FirstCatchRevealSeconds - FirstCatchFly)) / FirstCatchFly));
            if (fly > 0)
            {
                float h = compactInterface ? 112 : 132, ph = h - Skin.HeaderBand - 16, art = ph * 1.5f;
                var card = CatchCardRect(h);
                var slot = new Rect(card.x + 18, card.y + Skin.HeaderBand + 10, art - 12, ph - 4);
                fish = Rect.MinMaxRect(Mathf.Lerp(fish.xMin, slot.xMin, fly), Mathf.Lerp(fish.yMin, slot.yMin, fly),
                                       Mathf.Lerp(fish.xMax, slot.xMax, fly), Mathf.Lerp(fish.yMax, slot.yMax, fly));
            }
            coastalUi.Icon("first/fish", fish, FishPortrait(species), null, null, FishPortrait(species));
            coastalUi.Pose("first/fish", Mathf.Sin(t * 10f) * 7f * (1 - Ease.Clamp(t / 1.2f)), Mathf.Lerp(pop, 1, fly));

            float unroll = Ease.OutBack(Ease.Clamp((t - .4f) / .45f));
            float rw = Mathf.Min(HudGapRight - HudGapLeft - 16, compactInterface ? 300 : 420), rh = rw / 4, ry = cy + fh * .5f + rh * .5f;
            coastalUi.Icon("first/ribbon", Centered(cx, ry, rw, rh), "fx-rank-ribbon", null, Tint(Color.white, fade));
            coastalUi.Pose("first/ribbon", 0, 1, unroll);
            coastalUi.Text("first/ribbon/text", Centered(cx, ry - rh * .06f, rw * .7f, rh * .6f), "NEW SPECIES", Skin.Type.Heading, Tint(Skin.Ink, fade * unroll), TextAnchor.MiddleCenter);
            float name = Ease.OutCubic(Ease.Clamp((t - .65f) / .35f));
            coastalUi.Text("first/name", Centered(cx, ry + rh * .5f + (compactInterface ? 22 : 30) + (1 - name) * 16, rw + 40, compactInterface ? 40 : 52),
                GameData.Get(species).Name, Skin.Type.Display, Tint(Skin.Cream, fade * name), TextAnchor.MiddleCenter, null, true);

            // The NEW stamp slams onto the fish's corner (only once its sprite is in).
            if (HasUi("fx-stamp-new"))
            {
                float slam = Ease.Clamp((t - .8f) / .16f), size = compactInterface ? 64 : 92;
                coastalUi.Icon("first/stamp", Centered(cx + fw * .42f, cy - fh * .38f, size, size), "fx-stamp-new", null, Tint(Color.white, slam * fade));
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

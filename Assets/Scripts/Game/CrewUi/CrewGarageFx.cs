using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // Crew office v2: chests (and the reveal), tools (and merging), the renown road, and the level and rank effects.
    public partial class VoyageGame
    {
        float tokenFxAt = -9, levelFxAt = -9, rankFxAt = -9, mergeFxAt = -9, claimFxAt = -9;
        string fxCard;                 // card the last level or rank effect belongs to
        float levelBarFrom = -1;       // level before the last level up, for the sliding bar
        CardRarity rankFrom; int starsFrom;
        int mergeFxUid, claimFxN;
        ChestReveal reveal;

        sealed class ChestReveal
        {
            public ChestResult Result;
            public float Start;
            public readonly List<(string kind, CardRarity rarity, string a, int n)> Items = new();
            public float[] FlipAt;
            public int Stage;          // sounds fired: 1 landed, 2 popped, 3 + i card i out
            public CardRarity Best;
        }

        // ---- level and rank ----------------------------------------------------------------------------

        void LevelUpWithFx(string id, bool toCap)
        {
            var c = CardRoster.Find(State.Roster, id); if (c == null) return;
            int from = c.Level;
            bool done = toCap ? LevelUpCardToCap(id) > 0 : LevelUpCard(id);
            if (!done) { Toast("Not enough tokens or coins for that level."); return; }
            fxCard = id; levelBarFrom = from; levelFxAt = tokenFxAt = Now;
            audio?.Play(VoyageAudio.Cue.TokenPour, .4f);
            if (c.AtCap) audio?.Play(VoyageAudio.Cue.Bell, .45f);
        }

        void RankUpWithFx(string id)
        {
            var c = CardRoster.Find(State.Roster, id); if (c == null) return;
            rankFrom = c.Rarity; starsFrom = c.Stars;
            if (!RankUpCard(id)) return;
            fxCard = id; rankFxAt = Now;
            audio?.Play(VoyageAudio.Cue.Creak, .5f);
        }

        // Full-screen rank-up: the card rises over rays, flashes, and its frame turns to the new rarity.
        void RankUpOverlay()
        {
            var c = CardRoster.Find(State.Roster, fxCard);
            float t = Now - rankFxAt;
            if (c == null || t > 3.2f) { rankFxAt = -9; return; }
            const float Turn = .9f;
            if (t >= Turn && t - Time.unscaledDeltaTime < Turn)
            {
                audio?.Play(VoyageAudio.Cue.RewardChime, .7f); audio?.Play(VoyageAudio.Cue.Bell, .45f);
            }
            DarkScrim("rankfx/dim", () => rankFxAt = -9, Ease.Clamp(t / .3f) * (t > 2.8f ? 1 - (t - 2.8f) / .4f : 1));
            bool after = t >= Turn;
            var rarity = after ? c.Rarity : rankFrom;
            var col = RarityColour(c.Rarity);
            float ch = Mathf.Min(ih * .62f, 420), cw = ch * .75f, cx = iw / 2f, cy = ih * .46f;
            float rise = Ease.OutBack(t / .5f), fade = t > 2.8f ? 1 - (t - 2.8f) / .4f : 1;
            if (after)
            {
                float k = t - Turn;
                coastalUi.Icon("rankfx/rays", Centered(cx, cy, ch * 1.9f, ch * 1.9f), "fx-rays", null, Tint(col, .55f * fade * Ease.Clamp(k / .25f)));
                coastalUi.Pose("rankfx/rays", Now * 18, 1 + .05f * Mathf.Sin(Now * 2));
                coastalUi.Icon("rankfx/glow", Centered(cx, cy, ch * 1.4f, ch * 1.4f), "fx-glow", null, Tint(col, .8f * fade));
                coastalUi.Icon("rankfx/burst", Centered(cx, cy, ch, ch), "fx-burst", null, Tint(Color.Lerp(Color.white, col, .4f), .55f * (1 - Ease.Clamp(k / .5f)) * fade));
                coastalUi.Pose("rankfx/burst", 0, .4f + 1.6f * Ease.OutCubic(k / .5f));
                Sparkles("rankfx/spark", cx, cy, ch * .62f, 7, fade);
            }
            var rect = Centered(cx, cy + (1 - rise) * ih * .4f, cw, ch);
            CardFace("rankfx/card", rect, c, null, rarity, true);
            // Before the turn the card trembles; at the turn it pops.
            float shake = !after ? Mathf.Sin(t * 60) * 2.5f * Ease.Clamp((t - .45f) / .45f) : 0;
            float pop = after ? 1 + .12f * Ease.Pulse((t - Turn) / .35f) : 1;
            coastalUi.Pose("rankfx/card", shake, pop * fade);
            if (!after) coastalUi.Icon("rankfx/flash", rect, "fx-glow", null, Tint(Color.white, Ease.Clamp((t - .6f) / .3f) * .9f));
            else coastalUi.Icon("rankfx/flash", rect, "fx-glow", null, Tint(Color.white, (1 - Ease.Clamp((t - Turn) / .3f)) * .9f));
            string title = c.IsMythic && starsFrom < c.Stars && rankFrom == CardRarity.Mythic ? $"STAR {c.Stars}" : CardProgression.RarityName(c.Rarity).ToUpperInvariant();
            if (after)
            {
                float k = Ease.OutBack((t - Turn) / .4f);
                float rw = Mathf.Min(iw - 32, 520), rh = rw / 4;
                coastalUi.Icon("rankfx/ribbon", Centered(cx, rect.y - rh * .35f, rw, rh), "fx-rank-ribbon", null);
                coastalUi.Pose("rankfx/ribbon", 0, k * fade, Ease.OutBack((t - Turn) / .5f));
                coastalUi.Text("rankfx/title", Centered(cx, rect.y - rh * .4f, rw * .7f, rh * .6f), title, Skin.Type.Display, Darker(col), TextAnchor.MiddleCenter);
                coastalUi.Pose("rankfx/title", 0, k * fade);
                Confetti("rankfx/confetti", cx, cy - ch * .3f, t - Turn, 34, col, ih);
                var gained = c.Def.Abilities.FirstOrDefault(a => a.Unlock == c.Rarity && a != c.Def.Trait);
                string line = gained != null && rankFrom != CardRarity.Mythic ? $"New ability · {gained.Name}" : $"Level cap {c.LevelCap} · {CardProgression.ToolSlots(c.Rarity)} tool slots";
                coastalUi.Text("rankfx/line", new Rect(0, rect.yMax + 14, iw, 40), line, Skin.Type.Display, Skin.Cream, TextAnchor.MiddleCenter, null, true);
                coastalUi.Pose("rankfx/line", 0, Ease.OutCubic((t - Turn - .25f) / .3f) * fade);
            }
        }

        // Two layers of the dim: celebrations sit on a darker sea than ordinary dialogs.
        void DarkScrim(string id, Action dismiss, float alpha)
        {
            coastalUi.Box(id + "/under", new Rect(-50, -50, iw + 100, ih + 100), "", new Color(.03f, .08f, .14f, .88f * alpha), null, false);
            coastalUi.Scrim(id, dismiss, alpha);
        }

        // Confetti thrown up from a point, falling under gravity and fading; stable per piece.
        void Confetti(string id, float x, float y, float t, int count, Color main, float floor)
        {
            if (t < 0 || t > 2.6f) return;
            Color[] tints = { main, RarityColour(CardRarity.Gold), Skin.Teal, Skin.Cream, Palette.Hex("E2683A") };
            for (int i = 0; i < count; i++)
            {
                float a = i * 2.399f, speed = 380 + 260 * Mathf.Repeat(i * .618f, 1), dir = -Mathf.PI / 2 + Mathf.Sin(a) * 1.25f;
                float px = x + Mathf.Cos(dir) * speed * t, py = y + Mathf.Sin(dir) * speed * t + 900 * t * t * .5f;
                if (py > floor + 40) continue;
                float s = 14 + 10 * Mathf.Repeat(i * .37f, 1), alpha = 1 - Ease.Clamp((t - 1.8f) / .8f);
                string pid = $"{id}{i}";
                coastalUi.Icon(pid, Centered(px, py, s, s), "fx-confetti-" + (1 + i % 4), null, Tint(tints[i % tints.Length], alpha));
                coastalUi.Pose(pid, t * (200 + 160 * (i % 3)) * (i % 2 == 0 ? 1 : -1), 1, Mathf.Abs(Mathf.Cos(t * 7 + i)) * .8f + .2f);
            }
        }

        static Rect Centered(float x, float y, float w, float h) => new Rect(x - w / 2, y - h / 2, w, h);
        static Color Tint(Color c, float a) => new Color(c.r, c.g, c.b, Mathf.Clamp01(a));

        // Twinkling sparkles on a ring; stable positions per id.
        void Sparkles(string id, float cx, float cy, float radius, int count, float alpha)
        {
            for (int i = 0; i < count; i++)
            {
                float seed = i * 2.399f, a = seed + Now * .35f, r = radius * (.75f + .3f * Mathf.Sin(seed * 3.1f));
                float tw = Mathf.Max(0, Mathf.Sin(Now * 3.3f + seed * 5)), s = radius * .22f * (.5f + tw);
                string sid = $"{id}{i}";
                coastalUi.Icon(sid, Centered(cx + Mathf.Cos(a) * r, cy + Mathf.Sin(a) * r * .8f, s, s), "fx-sparkle", null, Tint(Color.white, tw * alpha));
                coastalUi.Pose(sid, Now * 90 + i * 40);
            }
        }

        // ---- chests page ------------------------------------------------------------------------------

        static readonly ChestKind[] ChestOrder = { ChestKind.Crate, ChestKind.SeaChest, ChestKind.CaptainsChest };

        static string ChestSource(ChestKind k) => k switch
        {
            ChestKind.Crate => "First sale each day and finished contracts",
            ChestKind.SeaChest => "Buy here, or from the renown road",
            _ => "Every tenth renown milestone",
        };

        void ChestsPage(Rect body)
        {
            if (State.PendingChestCount(ChestKind.Welcome) > 0) { WelcomeChestCard(body); return; }
            float gap = compactInterface ? 10 : 16, oddsH = compactInterface ? 58 : 70;
            float cw = (body.width - gap * 2) / 3, ch = body.height - oddsH - gap;
            for (int i = 0; i < 3; i++)
            {
                var kind = ChestOrder[i]; var def = Chests.Def(kind); int count = State.PendingChestCount(kind);
                string id = "chests/" + i;
                var card = coastalUi.Card(id, new Rect(body.x + i * (cw + gap), body.y, cw, ch), Skin.Card.Soft);
                float th = compactInterface ? 34 : 42;
                coastalUi.Text(id + "/name", new Rect(12, 8, cw - 24, th), def.Name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, card);
                float bh = compactInterface ? 46 : 56;
                // Short cards (phones) put the chest beside its text and the two buttons side by side.
                bool tight = ch < 320;
                float art = tight ? ch - th - bh - 30 : Mathf.Min(cw - 40, ch - th - bh - 86 - (def.Pity > 0 ? 34 : 0));
                var artRect = tight ? new Rect(12, th + 10, art, art) : new Rect((cw - art) / 2, th + 14, art, art);
                coastalUi.Icon(id + "/shadow", new Rect(artRect.x + art * .1f, artRect.yMax - art * .2f, art * .8f, art * .2f), "fx-chest-shadow", card);
                // The chest art carries wide transparent padding: draw it well past its slot so the chest itself fills the card.
                var drawn = tight ? artRect : new Rect(artRect.center.x - art * .725f, artRect.center.y - art * .82f, art * 1.45f, art * 1.45f);
                coastalUi.Icon(id + "/art", drawn, ChestArt(kind, false), card, count > 0 ? Color.white : new Color(.8f, .82f, .84f, 1));
                // Waiting chests bob and give a little wiggle every few seconds.
                float phase = (Now + i * .7f) % 3.2f;
                float wiggle = count > 0 && phase < .5f ? Mathf.Sin(phase * 40) * 5 * (1 - phase / .5f) : 0;
                coastalUi.Pose(id + "/art", wiggle, count > 0 ? 1 + .02f * Mathf.Sin(Now * 2.4f + i) : .94f);
                if (count > 0)
                {
                    float pw = tight ? 40 : 52, ph = tight ? 30 : 40;
                    var pill = new Rect(artRect.xMax - pw * (tight ? .7f : 1), artRect.y - (tight ? 6 : 0), pw, ph);
                    coastalUi.Sliced(id + "/count", pill, "v2-pill-cream", card, RarityColour(CardRarity.Gold));
                    coastalUi.Text(id + "/count/n", pill, "x" + count, tight ? Skin.Type.Body : Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, card);
                }
                coastalUi.Text(id + "/what", tight ? new Rect(art + 24, th + 6, cw - art - 34, art + 8) : new Rect(12, artRect.yMax + 2, cw - 24, 46),
                    $"{def.TokensFor(State.CardTier)} tokens · {def.Tools} tool{(def.Tools > 1 ? "s" : "")}" + (def.Guarantee > CardRarity.White ? $", one {CardProgression.RarityName(def.Guarantee)}+" : "") + $"\n{ChestSource(kind)}",
                    Skin.Type.Caption, Skin.InkSoft, tight ? TextAnchor.MiddleLeft : TextAnchor.UpperCenter, card);
                float by = ch - bh - (tight ? 10 : 12), half = (cw - 32) / 2; var k = kind;
                if (!tight && def.Pity > 0)
                {
                    // The blueprint guarantee as a meter in the card's open band, above the buttons.
                    int left = State.ChestsToPity(kind);
                    float my = artRect.yMax + 50, label = Mathf.Min(170, cw * .45f);
                    coastalUi.Text(id + "/pity", new Rect(cw - 16 - label, my, label, 22), left <= 1 ? "Blueprint next" : $"Blueprint in {left}", Skin.Type.Caption, Skin.Ink, TextAnchor.MiddleRight, card);
                    coastalUi.ProgressBar(id + "/pity/bar", new Rect(16, my + 6, cw - 40 - label, 10), 1 - left / (float)def.Pity, Skin.Bar.Teal, card);
                }
                // A chest for sale puts Buy and Open side by side, so every chest gets the same room for its art.
                bool split = def.ForSale;
                coastalUi.Primary(id + "/open", split ? new Rect(20 + half, by, half, bh) : new Rect(12, by, cw - 24, bh), count > 0 ? "Open" : split ? "None" : "None waiting", () => StartReveal(k), null, count > 0, card);
                if (def.ForSale)
                {
                    int price = State.ChestPrice(kind);
                    coastalUi.Secondary(id + "/buy", split ? new Rect(12, by, half, bh) : new Rect(12, by - bh - 8, cw - 24, bh), $"{price:N0}",
                        () => { if (BuyChest(k)) audio?.Play(VoyageAudio.Cue.Purchase, .6f); }, "v2-icon-coin", State.Coins >= price, card);
                }
            }
            var odds = coastalUi.Card("chests/odds", new Rect(body.x, body.yMax - oddsH, body.width, oddsH), Skin.Card.Soft);
            string focus = string.IsNullOrEmpty(State.FocusCard) ? "no focus: blueprints go to whoever needs one" : $"focus {Cards.ById(State.FocusCard)?.Name} gets 75%";
            coastalUi.Text("chests/odds/text", new Rect(16, 0, body.width - 32, oddsH),
                $"Tool odds  White 60% · Green 25% · Blue 10% · Purple 4% · Legendary 1%\nBlueprints: {focus}",
                Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, odds);
        }

        void StartReveal(ChestKind kind) => StartReveal(OpenChest(kind));
        void StartReveal(ChestResult result)
        {
            if (result == null) return;
            var r = new ChestReveal { Result = result, Start = Now, Best = CardRarity.White };
            r.Items.Add(("tokens", CardRarity.White, null, result.Tokens));
            foreach (var t in result.Tools.OrderBy(t => t.Rarity)) r.Items.Add(("tool", t.Rarity, ToolInfo.Name(t.Kind), (int)t.Kind));
            // A blueprint that recruited someone shows as the new crew member instead, last and biggest.
            var recruited = new List<string>(result.Recruits);
            foreach (var id in result.Blueprints) if (!recruited.Remove(id)) r.Items.Add(("blueprint", CardRarity.Purple, id, 1));
            foreach (var id in result.Recruits) r.Items.Add(("recruit", (CardRarity)Mathf.Max((int)CardRarity.Purple, (int)(Cards.ById(id)?.StartRarity ?? CardRarity.White)), id, 1));
            for (int i = 0; i < result.FreeBlueprints; i++) r.Items.Add(("free", CardRarity.Gold, null, 1));
            foreach (var it in r.Items) if (it.rarity > r.Best) r.Best = it.rarity;
            r.FlipAt = Enumerable.Repeat(-1f, r.Items.Count).ToArray();
            reveal = r;
            audio?.Play(VoyageAudio.Cue.Creak, .55f);
        }

        // Drop, shake, pop with burst and rays, then the cards fly out face down; tap each to flip it.
        void ChestRevealOverlay()
        {
            var r = reveal; float t = Now - r.Start;
            const float Drop = .45f, Pop = 1.25f, Out = 1.45f, Stagger = .12f, Fly = .45f;
            DarkScrim("reveal/dim", null, Ease.Clamp(t / .25f));
            Block(new Rect(0, 0, iw, ih));
            var col = RarityColour(r.Best);
            int n = r.Items.Count;
            float size = Mathf.Min(ih * .34f, 280), cx = iw / 2f, restY = ih * .3f;
            bool popped = t >= Pop;
            if (r.Stage < 1 && t >= Drop) { r.Stage = 1; audio?.Play(VoyageAudio.Cue.Winch, .4f); }
            if (r.Stage < 2 && popped)
            {
                r.Stage = 2;
                audio?.Play(r.Result.Kind is ChestKind.Crate or ChestKind.Welcome ? VoyageAudio.Cue.ChestOpen : VoyageAudio.Cue.ChestHeavy, .75f);
                if (r.Best >= CardRarity.Purple) audio?.Play(VoyageAudio.Cue.RewardChime, .5f);
            }

            // Light behind the chest once it opens, tinted by the best thing inside.
            if (popped)
            {
                float k = t - Pop;
                coastalUi.Icon("reveal/rays", Centered(cx, restY, size * 2.6f, size * 2.6f), "fx-rays", null, Tint(col, .5f * Ease.Clamp(k / .3f)));
                coastalUi.Pose("reveal/rays", Now * 14, 1);
                coastalUi.Icon("reveal/glow", Centered(cx, restY, size * 1.8f, size * 1.8f), "fx-glow", null, Tint(col, .85f));
                coastalUi.Pose("reveal/glow", 0, 1 + .06f * Mathf.Sin(Now * 3));
                coastalUi.Icon("reveal/burst", Centered(cx, restY, size, size), "fx-burst", null, Tint(Color.Lerp(Color.white, col, .4f), .7f * (1 - Ease.Clamp(k / .5f))));
                coastalUi.Pose("reveal/burst", k * 40, .5f + 1.9f * Ease.OutCubic(k / .5f));
            }
            float y = t < Drop ? Mathf.Lerp(-size, restY, Ease.OutBack(t / Drop, 1.2f)) : restY;
            float angle = 0, sx = 1, sy = 1;
            if (t >= Drop && t < Pop)
            {
                float k = (t - Drop) / (Pop - Drop);
                angle = Mathf.Sin(k * 38) * 9 * k;
                sy = 1 - .06f * Mathf.Abs(Mathf.Sin(k * 19)) * k; sx = 2 - sy;
            }
            else if (popped) { float k = (t - Pop) / .3f; sy = 1 + .14f * Ease.Pulse(k); sx = 1 - .06f * Ease.Pulse(k); }
            if (t < Drop + .15f && t > Drop) { float k = (t - Drop) / .15f; sy = 1 - .12f * Ease.Pulse(k); sx = 1 + .1f * Ease.Pulse(k); }
            float near = Ease.Clamp(t / Drop);
            coastalUi.Icon("reveal/shadow", Centered(cx, restY + size * .36f, size * (.5f + .45f * near), size * .2f), "fx-chest-shadow", null, new Color(1, 1, 1, .9f * near));
            var chest = coastalUi.Group("reveal/chest", Centered(cx, y, size, size));
            if (popped)
            {
                if (r.Result.CrewId != null) CrewPorthole("reveal/chest/crewopen", size, r.Result.CrewId, chest, Color.white, false);
                coastalUi.Icon("reveal/chest/open", new Rect(0, 0, size, size), ChestArt(r.Result.Kind, true), chest);
            }
            else
            {
                // The lid rattles as the shake builds: the dark interior shows through the gap.
                float k = t < Drop ? 0 : (t - Drop) / (Pop - Drop), lift = Mathf.Abs(Mathf.Sin(k * 27)) * size * .05f * k * k;
                if (r.Result.CrewId != null) CrewPorthole("reveal/chest/crew", size, r.Result.CrewId, chest, Color.white, true);
                coastalUi.Icon("reveal/chest/base", new Rect(0, 0, size, size), ChestLayer(r.Result.Kind, "base"), chest);
                if (lift > .5f) coastalUi.Icon("reveal/chest/inside", new Rect(0, 0, size, size), ChestLayer(r.Result.Kind, "interior"), chest);
                coastalUi.Icon("reveal/chest/lid", new Rect(0, -lift, size, size), ChestLayer(r.Result.Kind, "lid"), chest);
                coastalUi.Pose("reveal/chest/lid", Mathf.Sin(k * 23) * 3 * k);
            }
            coastalUi.Pose("reveal/chest", angle, sy, sx / sy);
            if (popped)
            {
                float k = t - Pop;
                Sparkles("reveal/spark", cx, restY, size * .7f, 8, Ease.Clamp(k / .4f));
                if (r.Best >= CardRarity.Purple) Confetti("reveal/confetti", cx, restY - size * .2f, k, 26, RarityColour(r.Best), ih);
            }

            // Cards: slots in up to two rows under the chest.
            int cols = Mathf.Min(n, compactInterface ? 5 : 6), rows = Mathf.CeilToInt(n / (float)cols);
            float gap = compactInterface ? 10 : 16, areaTop = restY + size * .55f, areaH = ih - areaTop - (compactInterface ? 70 : 96);
            float cardH = Mathf.Min(areaH / rows - gap, ((iw - 48) / cols - gap) / .75f, 240), cardW = cardH * .75f;
            bool allOut = true, allFlipped = true;
            for (int i = 0; i < n; i++)
            {
                int row = i / cols, inRow = Mathf.Min(cols, n - row * cols), col_ = i % cols;
                float tx = cx + (col_ - (inRow - 1) / 2f) * (cardW + gap), ty = areaTop + row * (cardH + gap) + cardH / 2;
                float start = Out + i * Stagger, k = (t - start) / Fly;
                if (k < 0) { allOut = false; allFlipped = false; continue; }
                if (r.Stage < 3 + i) { r.Stage = 3 + i; audio?.Play(VoyageAudio.Cue.CardFlip, .35f); }
                if (k < 1) allOut = false;
                float e = Ease.OutCubic(k), arc = Mathf.Sin(Mathf.Clamp01(k) * Mathf.PI) * size * .5f;
                float px = Mathf.Lerp(cx, tx, e), py = Mathf.Lerp(restY, ty, e) - arc;
                string id = "reveal/item" + i; int index = i;
                float flip = r.FlipAt[i] < 0 ? 0 : Ease.Clamp((Now - r.FlipAt[i]) / .35f);
                bool face = flip >= .5f;
                if (r.FlipAt[i] < 0 || flip < 1) allFlipped = false;
                var rect = Centered(px, py, cardW, cardH);
                var item = r.Items[i];
                if (face && item.rarity >= CardRarity.Blue)
                {
                    float g = Now - r.FlipAt[i] - .17f;
                    coastalUi.Icon(id + "/glow", Centered(px, py, cardW * 1.7f, cardH * 1.5f), "fx-glow", null, Tint(RarityColour(item.rarity), .7f + .15f * Mathf.Sin(Now * 3 + i)));
                    coastalUi.Icon(id + "/burst", Centered(px, py, cardW * 1.6f, cardW * 1.6f), "fx-burst", null, Tint(Color.white, .7f * (1 - Ease.Clamp(g / .45f))));
                    coastalUi.Pose(id + "/burst", 0, .4f + 1.4f * Ease.OutCubic(g / .45f));
                }
                if (!face) coastalUi.Icon(id, rect, "v2-card-back", null);
                else RevealFace(id, rect, item);
                float spin = k < 1 ? (1 - e) * (i % 2 == 0 ? -25 : 25) : 0;
                coastalUi.Pose(id, spin, Mathf.Lerp(.35f, 1, e) * (face && flip < 1 ? 1 + .08f * Ease.Pulse(flip) : 1), Mathf.Max(.02f, Mathf.Abs(Mathf.Cos(flip * Mathf.PI))));
                if (r.FlipAt[i] < 0 && k >= 1)
                    coastalUi.HitArea(id + "/tap", rect, () => FlipReveal(index));
            }
            float bw = compactInterface ? 220 : 280, bh = compactInterface ? 52 : 62, by = ih - bh - (compactInterface ? 10 : 22);
            if (allOut && !allFlipped && r.FlipAt.Any(f => f < 0))
                coastalUi.Primary("reveal/all", new Rect(cx - bw / 2, by, bw, bh), "Open all", () => { for (int i = 0; i < n; i++) FlipReveal(i, i * .1f); }, null);
            else if (allFlipped)
                coastalUi.Primary("reveal/collect", new Rect(cx - bw / 2, by, bw, bh), "Collect", CollectReveal, "v2-icon-token");
            else if (t < Out) coastalUi.HitArea("reveal/skip", new Rect(0, 0, iw, ih), () => r.Start = Now - Out);
        }

        void FlipReveal(int i, float delay = 0)
        {
            var r = reveal; if (r == null || r.FlipAt[i] >= 0) return;
            r.FlipAt[i] = Now + delay;
            var rarity = r.Items[i].rarity;
            audio?.Play(VoyageAudio.Cue.CardFlip, .55f);
            if (rarity >= CardRarity.Purple) audio?.Play(VoyageAudio.Cue.RewardChime, .55f);
        }

        void CollectReveal()
        {
            var r = reveal; reveal = null;
            tokenFxAt = Now;
            audio?.Play(VoyageAudio.Cue.TokenPour, .5f);
            if (r.Result.FreeBlueprints > 0) { crewTab = 0; renownChoice = -1; }
            else if (r.Result.Recruits.Count > 0) { crewTab = 0; cardPanelId = r.Result.Recruits[0]; }
        }

        void RevealFace(string id, Rect rect, (string kind, CardRarity rarity, string a, int n) item)
        {
            var g = coastalUi.Group(id, rect);
            float w = rect.width, h = rect.height;
            coastalUi.Card(id + "/bg", new Rect(0, 0, w, h), Skin.Card.Soft, g);
            var col = RarityColour(item.rarity);
            // The rarity ribbon across the top: the folded band sprite, or a tinted pill without it.
            string band = RewardBand(item.rarity);
            if (band != null) coastalUi.Icon(id + "/band", new Rect(-6, 2, w + 12, (w + 12) * 40 / 256f), band, g);
            else coastalUi.Sliced(id + "/band", new Rect(6, 6, w - 12, h * .1f), "v2-pill-cream", g, col);
            string caption, title;
            switch (item.kind)
            {
                case "tokens":
                    coastalUi.Icon(id + "/icon", new Rect(w * .18f, h * .2f, w * .64f, w * .64f), "v2-icon-token", g);
                    title = "+" + item.n; caption = "Tokens"; break;
                case "tool":
                    ToolTileFace(id + "/tool", new Rect(w * .14f, h * .18f, w * .72f, w * .72f), new ToolState { Kind = (ToolKind)item.n, Rarity = item.rarity }, g);
                    title = item.a; caption = CardProgression.RarityName(item.rarity) + $" · +{CardProgression.ToolBonus(item.rarity) * 100:0}%"; break;
                case "recruit":
                {
                    var c = CardRoster.Find(State.Roster, item.a) ?? new CardState(item.a);
                    CardFace(id + "/card", new Rect(0, 0, w, h), c, g, c.Rarity, w > 130);
                    float rw = w * 1.15f, rh = rw / 4;
                    coastalUi.Icon(id + "/ribbon", new Rect((w - rw) / 2, -rh * .45f, rw, rh), "fx-rank-ribbon", g);
                    coastalUi.Text(id + "/ribbon/text", new Rect((w - rw) / 2, -rh * .5f, rw, rh * .9f), "NEW CREW", w > 130 ? Skin.Type.Heading : Skin.Type.Caption, Darker(RarityColour(c.Rarity)), TextAnchor.MiddleCenter, g);
                    return;
                }
                case "blueprint":
                    coastalUi.Icon(id + "/icon", new Rect(w * .1f, h * .16f, w * .8f, w * .8f), "v2-icon-blueprint", g);
                    coastalUi.Icon(id + "/who", new Rect(w * .3f, h * .25f, w * .4f, w * .4f), "art108-" + item.a + "-96", g);
                    title = Cards.ById(item.a)?.Name ?? item.a; caption = "Blueprint"; break;
                default:
                    coastalUi.Icon(id + "/icon", new Rect(w * .1f, h * .16f, w * .8f, w * .8f), "v2-icon-blueprint", g, RarityColour(CardRarity.Gold));
                    title = "Any crew"; caption = "Blueprint of your choice"; break;
            }
            coastalUi.Text(id + "/title", new Rect(6, h * .7f, w - 12, h * .14f), title, w > 130 ? Skin.Type.Heading : Skin.Type.Body, Skin.Ink, TextAnchor.MiddleCenter, g);
            coastalUi.Text(id + "/caption", new Rect(6, h * .84f, w - 12, h * .12f), caption, Skin.Type.Caption, Darker(col), TextAnchor.MiddleCenter, g);
        }

        // ---- tools page -------------------------------------------------------------------------------

        void ToolsPage(Rect body)
        {
            float gap = compactInterface ? 10 : 14, detailW = Mathf.Min(body.width * .4f, 400);
            var gridArea = new Rect(body.x, body.y, body.width - detailW - gap, body.height);
            var tools = State.Tools.OrderBy(t => ToolInfo.Class(t.Kind)).ThenBy(t => t.Kind).ThenByDescending(t => t.Rarity).ToList();
            if (State.FindTool(selectedTool) == null) selectedTool = tools.Count > 0 ? tools[0].Uid : 0;
            float s = compactInterface ? 76 : 92;
            int cols = Mathf.Max(1, Mathf.FloorToInt((gridArea.width - 12 + gap) / (s + gap)));
            var content = coastalUi.Scroll("tools/grid", gridArea, Mathf.Ceil(tools.Count / (float)cols) * (s + gap) + 8);
            if (tools.Count == 0)
                coastalUi.Text("tools/empty", new Rect(8, 8, gridArea.width - 24, 80), "No tools yet. Every chest holds at least one.", Skin.Type.Body, Skin.Cream, TextAnchor.UpperLeft, content);
            for (int i = 0; i < tools.Count; i++)
            {
                var t = tools[i]; string id = "tools/grid/" + i; int uid = t.Uid;
                var cell = new Rect(i % cols * (s + gap), 4 + i / cols * (s + gap), s, s);
                coastalUi.CardButton(id, cell, null, () => { selectedTool = uid; MenuSound(); }, null, true, content);
                var btn = coastalUi.ElementRect(id);
                if (t.Uid == selectedTool) coastalUi.Sliced(id + "/ring", new Rect(-5, -5, s + 10, s + 10), "v2-pill-cream", btn, Skin.Teal);
                ToolTileFace(id + "/face", new Rect(3, 3, s - 6, s - 6), t, btn);
                string holder = State.ToolOwner(t.Uid);
                if (holder != null)
                    coastalUi.Icon(id + "/holder", new Rect(s - 28, s - 28, 26, 26), holder == GameState.CaptainToolOwner ? "v2-icon-anchor" : "art108-" + holder + "-56", btn);
                if (tools.Any(o => ToolInfo.CanMerge(t, o)))
                {
                    float bob = Mathf.Sin(Now * 4 + i) * 3;
                    coastalUi.Sliced(id + "/merge", new Rect(-6, -8 + bob, 30, 30), "v2-pill-cream", btn, RarityColour(t.Rarity + 1));
                    coastalUi.Text(id + "/merge/up", new Rect(-6, -8 + bob, 30, 30), "+", Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleCenter, btn, true);
                }
                float m = Now - mergeFxAt;
                coastalUi.Pose(id, 0, t.Uid == mergeFxUid && m < .5f ? 1 + .25f * Ease.Pulse(m / .5f) : 1);
            }
            ToolDetail(new Rect(body.xMax - detailW, body.y, detailW, body.height), tools);
        }

        void ToolDetail(Rect r, List<ToolState> tools)
        {
            var panel = coastalUi.Card("tools/detail", r, Skin.Card.Soft);
            var t = State.FindTool(selectedTool);
            float w = r.width, pad = 14;
            float bh = compactInterface ? 48 : 58;
            int pairs = MergeablePairs().Count;
            bool tight = r.height < 400;
            float half = (w - pad * 3) / 2;
            coastalUi.Secondary("tools/detail/all", tight ? new Rect(pad * 2 + half, r.height - bh - pad, half, bh) : new Rect(pad, r.height - bh - pad, w - pad * 2, bh), pairs > 0 ? $"Merge all · {pairs}" : "Nothing to merge", MergeAll, null, pairs > 0, panel);
            if (t == null) return;
            var col = RarityColour(t.Rarity);
            float tile = tight ? Mathf.Min(r.height - bh - pad * 2 - 12, 84) : Mathf.Min(w * .45f, r.height * .32f), m = Now - mergeFxAt;
            var tileRect = tight ? new Rect(pad, pad, tile, tile) : new Rect((w - tile) / 2, pad, tile, tile);
            if (t.Uid == mergeFxUid && m < 1.2f)
            {
                coastalUi.Icon("tools/detail/rays", Centered(tileRect.center.x, pad + tile / 2, tile * 2.2f, tile * 2.2f), "fx-rays", panel, Tint(col, .6f * (1 - Ease.Clamp((m - .6f) / .6f))));
                coastalUi.Pose("tools/detail/rays", Now * 30, 1);
                coastalUi.Icon("tools/detail/burst", Centered(tileRect.center.x, pad + tile / 2, tile * 1.2f, tile * 1.2f), "fx-burst", panel, Tint(Color.white, .7f * (1 - Ease.Clamp(m / .5f))));
                coastalUi.Pose("tools/detail/burst", 0, .5f + 1.4f * Ease.OutCubic(m / .5f));
            }
            ToolTileFace("tools/detail/tile", tileRect, t, panel);
            coastalUi.Pose("tools/detail/tile", 0, t.Uid == mergeFxUid && m < .6f ? 1 + .18f * Ease.Pulse(m / .6f) : 1);
            float y = tight ? pad - 4 : pad + tile + 8, tx = tight ? pad * 2 + tile : pad, tw = w - tx - pad;
            var align = tight ? TextAnchor.MiddleLeft : TextAnchor.MiddleCenter;
            coastalUi.Text("tools/detail/name", new Rect(tx, y, tw, tight ? 28 : 34), ToolInfo.Name(t.Kind), Skin.Type.Heading, Skin.Ink, align, panel);
            coastalUi.Text("tools/detail/rarity", new Rect(tx, y + (tight ? 26 : 32), tw, 24), $"{CardProgression.RarityName(t.Rarity)} · {ToolInfo.Class(t.Kind)} tool", Skin.Type.Small, Darker(col), align, panel);
            string holder = State.ToolOwner(t.Uid);
            string who = holder == null ? "Spare" : holder == GameState.CaptainToolOwner ? "Fitted on the captain" : $"Fitted on {Cards.ById(holder)?.Name}";
            coastalUi.Text("tools/detail/body", tight ? new Rect(tx, y + 50, tw, tile - 40) : new Rect(pad, y + 62, w - pad * 2, 64), $"+{CardProgression.ToolBonus(t.Rarity) * 100:0}% {ToolInfo.Job(t.Kind)}\n{who}", tight ? Skin.Type.Caption : Skin.Type.Body, Skin.InkSoft, tight ? TextAnchor.UpperLeft : TextAnchor.UpperCenter, panel);
            var partner = MergePartner(t);
            string next = t.Rarity < CardRarity.Mythic ? CardProgression.RarityName(t.Rarity + 1) : null;
            string label = next == null ? "Mythic is the top" : partner != null ? $"Merge into {next}" : $"Needs a second {CardProgression.RarityName(t.Rarity)} {ToolInfo.Name(t.Kind).ToLowerInvariant()}";
            coastalUi.Primary("tools/detail/merge", tight ? new Rect(pad, r.height - bh - pad, half, bh) : new Rect(pad, r.height - bh * 2 - pad - 10, w - pad * 2, bh), tight && partner != null ? "Merge" : tight && partner == null ? "Need a pair" : label, () => MergeWithFx(t.Uid, partner.Uid), null, partner != null, panel);
        }

        // The other copy to merge with: a spare first so fitted tools stay fitted.
        ToolState MergePartner(ToolState t) =>
            State.Tools.Where(o => ToolInfo.CanMerge(t, o)).OrderBy(o => State.ToolOwner(o.Uid) != null).FirstOrDefault();

        List<(int keep, int feed)> MergeablePairs()
        {
            var pairs = new List<(int, int)>();
            foreach (var g in State.Tools.Where(t => t.Rarity < CardRarity.Mythic).GroupBy(t => (t.Kind, t.Rarity)))
            {
                // Fitted copies keep their slot; spares feed them.
                var list = g.OrderBy(t => State.ToolOwner(t.Uid) == null).ToList();
                for (int i = 0; i + 1 < list.Count; i += 2) pairs.Add((list[i].Uid, list[i + 1].Uid));
            }
            return pairs;
        }

        void MergeWithFx(int keep, int feed)
        {
            // Keep whichever copy is fitted.
            if (State.ToolOwner(keep) == null && State.ToolOwner(feed) != null) (keep, feed) = (feed, keep);
            if (!MergeTools(keep, feed)) return;
            selectedTool = mergeFxUid = keep; mergeFxAt = Now;
            audio?.Play(VoyageAudio.Cue.Winch, .5f); audio?.Play(VoyageAudio.Cue.Bell, .5f);
        }

        // Merges until no pair is left, one rarity at a time (two Whites make a Green that can merge again).
        void MergeAll()
        {
            int merged = 0, last = 0;
            for (var pairs = MergeablePairs(); pairs.Count > 0 && merged < 200; pairs = MergeablePairs())
                foreach (var (keep, feed) in pairs)
                    if (State.MergeTools(keep, feed)) { merged++; last = keep; }
            if (merged == 0) return;
            CardChange(true, true);
            selectedTool = mergeFxUid = last; mergeFxAt = Now;
            audio?.Play(VoyageAudio.Cue.Winch, .5f); audio?.Play(VoyageAudio.Cue.Bell, .55f);
            Toast($"{merged} merge{(merged > 1 ? "s" : "")} done.");
        }

        // ---- renown road ------------------------------------------------------------------------------

        bool RenownClaimable => State.Renown >= RenownRoad.Threshold(State.RenownClaimed + 1);

        static string RewardIcon(RenownReward r) => r.Kind switch
        {
            RenownRewardKind.BlueprintChoice => "v2-icon-blueprint", RenownRewardKind.Tokens => "v2-icon-token", _ => ChestArt(r.Chest, false),
        };

        void RenownPage(Rect body)
        {
            int renown = State.Renown, next = State.RenownClaimed + 1;
            float headH = compactInterface ? 64 : 76;
            var head = coastalUi.Card("renown/head", new Rect(body.x, body.y, body.width, headH), Skin.Card.Soft);
            float ic = headH - 20;
            coastalUi.Icon("renown/head/icon", new Rect(12, 10, ic, ic), "v2-icon-renown", head);
            coastalUi.Text("renown/head/value", new Rect(ic + 24, 4, body.width * .4f, headH * .55f), $"Renown {renown}", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, head);
            coastalUi.Text("renown/head/how", new Rect(ic + 24, headH * .5f, body.width * .5f, headH * .45f), "Every level, rank and star your crew earns adds renown.", Skin.Type.Caption, Skin.InkSoft, TextAnchor.MiddleLeft, head);
            int prev = next > 1 ? RenownRoad.Threshold(next - 1) : 0, goal = RenownRoad.Threshold(next);
            coastalUi.ProgressBar("renown/head/bar", new Rect(body.width * .55f, headH / 2 - 6, body.width * .3f, 12), Mathf.Clamp01((renown - prev) / (float)Mathf.Max(1, goal - prev)), Skin.Bar.Teal, head);
            coastalUi.Text("renown/head/next", new Rect(body.width * .86f, 0, body.width * .14f - 12, headH), renown >= goal ? "Claim ready" : $"{renown}/{goal}", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleRight, head);

            var list = new Rect(body.x, body.y + headH + 10, body.width, body.height - headH - 10);
            int first = Mathf.Max(1, next - 2), last = next + 14;
            float rowH = compactInterface ? 66 : 78, gap = 8;
            var content = coastalUi.Scroll("renown/road", list, (last - first + 1) * (rowH + gap) + 8);
            float lineX = 44;
            coastalUi.Sliced("renown/road/line", new Rect(lineX - 4, rowH / 2, 8, (last - first) * (rowH + gap)), "v2-inset", content);
            for (int n = first; n <= last; n++)
            {
                int index = n; var reward = RenownRoad.Reward(n);
                bool claimed = n <= State.RenownClaimed, ready = n == next && renown >= RenownRoad.Threshold(n), locked = !claimed && !ready;
                string id = "renown/road/" + (n - first);
                float y = 4 + (n - first) * (rowH + gap);
                float node = rowH * .62f, fx = n == claimFxN ? Now - claimFxAt : 9;
                coastalUi.Sliced(id + "/node", new Rect(lineX - node / 2, y + (rowH - node) / 2, node, node), "v2-pill-cream", content,
                    claimed ? Skin.Green : ready ? RarityColour(CardRarity.Gold) : new Color(.75f, .78f, .8f, 1));
                coastalUi.Pose(id + "/node", 0, ready ? 1 + .08f * Mathf.Sin(Now * 4) : fx < .5f ? 1 + .3f * Ease.Pulse(fx / .5f) : 1);
                coastalUi.Text(id + "/n", new Rect(lineX - node / 2, y + (rowH - node) / 2, node, node), claimed ? "✓" : n.ToString(), Skin.Type.Small, Skin.Ink, TextAnchor.MiddleCenter, content);
                var card = coastalUi.Card(id, new Rect(lineX + node / 2 + 14, y, list.width - lineX - node / 2 - 30, rowH), Skin.Card.Soft, content);
                float cw = list.width - lineX - node / 2 - 30, ic2 = rowH - 16;
                coastalUi.Icon(id + "/icon", new Rect(10, 8, ic2, ic2), RewardIcon(reward), card, locked ? new Color(1, 1, 1, .55f) : Color.white);
                coastalUi.Text(id + "/label", new Rect(ic2 + 22, 4, cw * .55f, rowH * .55f), reward.Label, Skin.Type.Heading, locked ? Skin.InkSoft : Skin.Ink, TextAnchor.MiddleLeft, card);
                coastalUi.Text(id + "/at", new Rect(ic2 + 22, rowH * .5f, cw * .55f, rowH * .45f), $"At {RenownRoad.Threshold(n)} renown", Skin.Type.Caption, Skin.InkSoft, TextAnchor.MiddleLeft, card);
                float bw = Mathf.Min(cw * .3f, 200), bh = rowH - 18;
                if (ready) coastalUi.Primary(id + "/claim", new Rect(cw - bw - 10, 9, bw, bh), "Claim", () => ClaimRenownWithFx(index), null, true, card);
                else if (claimed) coastalUi.Text(id + "/done", new Rect(cw - bw - 10, 9, bw, bh), "Claimed", Skin.Type.Small, Skin.Green, TextAnchor.MiddleCenter, card);
            }
        }

        void ClaimRenownWithFx(int n)
        {
            var reward = RenownRoad.Reward(n);
            if (reward.Kind == RenownRewardKind.BlueprintChoice) { renownChoice = n; MenuSound(); return; }
            if (!ClaimRenown(n)) return;
            claimFxN = n; claimFxAt = Now;
            audio?.Play(VoyageAudio.Cue.Bell, .55f);
            if (reward.Kind == RenownRewardKind.Tokens) { tokenFxAt = Now; audio?.Play(VoyageAudio.Cue.TokenPour, .5f); }
            else Toast($"{Chests.Def(reward.Chest).Name} added to Chests.");
        }

        // Blueprint chooser: renownChoice > 0 claims that milestone, -1 assigns a free blueprint.
        void BlueprintChooser()
        {
            var wants = State.Roster.Where(Chests.WantsBlueprints).ToList();
            coastalUi.Scrim("choose/dim", () => { renownChoice = 0; MenuSound(); });
            float W = Mathf.Min(iw - 24, 1000), H = Mathf.Min(ih - 24, 560);
            var r = new Rect((iw - W) / 2, (ih - H) / 2, W, H);
            var slab = coastalUi.Slab("choose", r, null, true); Block(r);
            float pad = compactInterface ? 12 : 18;
            coastalUi.Text("choose/title", new Rect(pad, pad - 4, W - pad * 2 - 70, 44), "Choose who gets the blueprint", Skin.Type.Display, Skin.Ink, TextAnchor.MiddleLeft, slab);
            coastalUi.CardButton("choose/close", new Rect(W - pad - 56, pad, 56, 52), null, () => { renownChoice = 0; MenuSound(); }, "v2-icon-back", true, slab);
            var list = new Rect(r.x + pad, r.y + pad + 54, W - pad * 2, H - pad * 2 - 54);
            float gap = 12, cw = compactInterface ? 120 : 150, ch = cw * 4 / 3f;
            int cols = Mathf.Max(1, Mathf.FloorToInt((list.width - 12 + gap) / (cw + gap)));
            var content = coastalUi.Scroll("choose/list", list, Mathf.Ceil(wants.Count / (float)cols) * (ch + gap) + 8);
            for (int i = 0; i < wants.Count; i++)
            {
                var c = wants[i]; string id = "choose/list/" + c.Id, cardId = c.Id;
                var cell = new Rect(i % cols * (cw + gap), 4 + i / cols * (ch + gap), cw, ch);
                CardFace(id, cell, c, content, c.Rarity, false);
                coastalUi.Pose(id);
                coastalUi.HitArea(id + "/tap", new Rect(0, 0, cw, ch), () => ChooseBlueprint(cardId), coastalUi.ElementRect(id));
            }
        }

        void ChooseBlueprint(string cardId)
        {
            int n = renownChoice;
            bool ok = n > 0 ? ClaimRenown(n, cardId) : AssignFreeBlueprint(cardId);
            if (!ok) return;
            renownChoice = 0; claimFxN = n; claimFxAt = Now; fxCard = cardId; levelFxAt = Now;
            audio?.Play(VoyageAudio.Cue.Bell, .55f);
            Toast($"Blueprint for {Cards.ById(cardId)?.Name}.");
            if (n < 0 && State.FreeBlueprints > 0) renownChoice = -1;
        }
    }
}

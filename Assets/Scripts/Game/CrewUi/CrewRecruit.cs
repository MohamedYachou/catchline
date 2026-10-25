using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // Crew office v2: recruiting (Mo, 2026-10-25). Crew are not free with a tier: each unlocked crew member has an
    // offer of ten crew chests centred on them, and the tenth always holds their blueprint. The first boat brings a
    // welcome chest with Mira.
    public partial class VoyageGame
    {
        float recruitFlashAt = -9; string recruitFlashId;

        static readonly string[] TierBoat = { "Rowboat", "Skiff", "Compact fisher", "Jig boat", "Prep fisher", "Buoy fisher" };

        void OpenRecruit(CardDef d)
        {
            MenuSound();
            if (d.Role == CardRole.Navigator) { crewTab = 1; return; }
            if (d.TierGranted > State.CardTier) { Toast($"{d.Name} joins crews from tier {d.TierGranted} ({TierBoat[d.TierGranted]})."); return; }
            crewTab = 2; recruitFlashId = d.Id; recruitFlashAt = Now;
        }

        void BuyCrewChestWithFx(string id)
        {
            var result = BuyCrewChest(id);
            if (result == null) { Toast("Not enough coins for that crew chest."); return; }
            audio?.Play(VoyageAudio.Cue.Purchase, .6f);
            StartReveal(result);
        }

        // ---- a locked crew card in the garage ---------------------------------------------------------

        void LockedFace(string id, Rect r, CardDef def, Transform parent)
        {
            var g = coastalUi.Group(id, r, parent);
            float w = r.width, h = r.height;
            bool open = def.TierGranted <= State.CardTier && def.Role != CardRole.Navigator;
            coastalUi.Box(id + "/window", new Rect(w * .1f, h * .075f, w * .8f, h * .43f), "", Palette.Hex("1C3A5A"), g, false);
            coastalUi.Icon(id + "/frame", new Rect(0, 0, w, h), "art108-frame-locked", g);
            coastalUi.Icon(id + "/portrait", new Rect(w * .1f, h * .075f, w * .8f, h * .43f), "art108-" + def.Id, g, open ? new Color(.55f, .62f, .68f, 1) : new Color(.16f, .24f, .32f, 1));
            coastalUi.Text(id + "/name", new Rect(w * .08f, h * .512f, w * .84f, h * .086f), def.Name.ToUpperInvariant(), Skin.Type.Caption, Skin.Cream, TextAnchor.MiddleCenter, g);
            float[] rowY = { .613f, .726f, .839f }; float rh = h * .092f, ix = w * .125f, isz = Mathf.Min(w * .1f, rh * .8f);
            int bought = State.CrewChestsBoughtFor(def.Id);
            string[] rows =
            {
                def.Role == CardRole.Navigator ? "Welcome chest" : open ? "Recruit now" : $"Joins at tier {def.TierGranted}",
                def.Role.ToString(),
                def.Role == CardRole.Navigator ? "Your navigator" : $"Crew chests {bought}/{Chests.CrewChestOffer}",
            };
            string[] icons = { open ? "v2-icon-coin" : "v2-icon-lock", RoleIcon(def.Role), "v2-icon-blueprint" };
            for (int i = 0; i < 3; i++)
            {
                float y = h * rowY[i];
                coastalUi.Icon($"{id}/row{i}/icon", new Rect(ix + (w * .1f - isz) / 2, y + (rh - isz) / 2, isz, isz), icons[i], g);
                coastalUi.Text($"{id}/row{i}/text", new Rect(w * .25f, y, w * .66f, rh), rows[i], Skin.Type.Caption, open && i == 0 ? Skin.Teal : Skin.InkSoft, TextAnchor.MiddleLeft, g);
            }
            TierBadge(id + "/tier", new Rect(w * .02f, h * .015f, w * .22f, w * .22f), def.TierGranted, g);
            if (!open) coastalUi.Icon(id + "/lock", new Rect(w * .36f, h * .2f, w * .28f, w * .28f), "v2-icon-lock", g);
            else
            {
                // Recruitable: a coin bobbing on the corner, like the spend badge on owned cards.
                float bob = Mathf.Sin(Now * 5 + r.x * .02f) * h * .012f, b = w * .2f;
                coastalUi.Icon(id + "/ready", new Rect(w * .74f, h * .6f + bob - b * .2f, b, b), "v2-icon-coin", g);
            }
        }

        // Round tier badge: the art when it lands, a teal pill with the numeral until then.
        void TierBadge(string id, Rect r, int tier, Transform parent)
        {
            string art = "v2-tier-" + tier;
            if (ArtLibrary.Get()?.UiTex(art) != null) { coastalUi.Icon(id, r, art, parent); return; }
            coastalUi.Sliced(id, r, "v2-pill-cream", parent, Skin.Teal);
            coastalUi.Text(id + "/n", r, tier.ToString(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleCenter, parent, true);
        }

        // ---- recruit page -----------------------------------------------------------------------------

        void RecruitPage(Rect body)
        {
            float gap = compactInterface ? 10 : 14, headH = compactInterface ? 34 : 40;
            float target = compactInterface ? 230 : 196;
            int cols = Mathf.Max(2, Mathf.FloorToInt((body.width - 12 + gap) / (target + gap)));
            float cw = (body.width - 12 - gap * (cols - 1)) / cols, ch = Mathf.Min(cw * 1.42f, compactInterface ? 250 : 320);
            // Measure: one header per tier, then its crew in rows.
            var tiers = Enumerable.Range(1, 5).Select(t => (t, crew: Cards.ForTier(t).Where(d => d.Role != CardRole.Navigator).ToList())).Where(x => x.crew.Count > 0).ToList();
            float total = 0;
            foreach (var (t, crew) in tiers) total += headH + Mathf.Ceil(crew.Count / (float)cols) * (ch + gap) + gap;
            var content = coastalUi.Scroll("recruit/list", body, total + 8);
            float y = 4;
            foreach (var (t, crew) in tiers)
            {
                bool open = t <= State.CardTier;
                string head = $"Tier {t} · {TierBoat[t]}" + (open ? "" : t == 3 ? " · opens with the prep fisher" : " · locked");
                if (t == 3 && open && State.CardTier > 3) head = $"Tier 3 · joins from the prep fisher";
                coastalUi.Text($"recruit/tier{t}", new Rect(4, y, body.width - 20, headH), head, Skin.Type.Heading, open ? Skin.Cream : new Color(.75f, .8f, .84f, 1), TextAnchor.MiddleLeft, content, true);
                y += headH;
                for (int i = 0; i < crew.Count; i++)
                {
                    var r = new Rect(i % cols * (cw + gap), y + i / cols * (ch + gap), cw, ch);
                    CrewOffer("recruit/" + crew[i].Id, r, crew[i], open, content);
                }
                y += Mathf.Ceil(crew.Count / (float)cols) * (ch + gap) + gap;
            }
        }

        // One crew member's offer: their chest with the portrait in its window, ten pips, the price.
        void CrewOffer(string id, Rect r, CardDef def, bool open, Transform parent)
        {
            var card = coastalUi.Card(id, r, Skin.Card.Soft, parent);
            float w = r.width, h = r.height, pad = compactInterface ? 8 : 12;
            var owned = CardRoster.Find(State.Roster, def.Id);
            int bought = State.CrewChestsBoughtFor(def.Id), left = Chests.CrewChestOffer - bought;
            // A tap on a locked card in the garage lands here: that offer pulses once.
            float flash = recruitFlashId == def.Id ? 1 - Ease.Clamp((Now - recruitFlashAt) / 1.2f) : 0;
            if (flash > 0) coastalUi.Icon(id + "/flash", new Rect(-w * .12f, -h * .08f, w * 1.24f, h * 1.16f), "fx-glow", card, Tint(Skin.Teal, .8f * flash));
            float nameH = compactInterface ? 26 : 32;
            coastalUi.Text(id + "/name", new Rect(pad, pad - 2, w - pad * 2 - 40, nameH), def.Name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, card);
            coastalUi.Text(id + "/role", new Rect(pad, pad + nameH - 6, w - pad * 2, nameH * .7f), owned != null ? $"Joined · {CardProgression.RarityName(owned.Rarity)}" : $"{def.Role} · starts {CardProgression.RarityName(def.StartRarity)}", Skin.Type.Caption, owned != null ? Darker(RarityColour(owned.Rarity)) : Skin.InkSoft, TextAnchor.MiddleLeft, card);
            TierBadge(id + "/tier", new Rect(w - pad - 34, pad, 34, 34), def.TierGranted, card);
            float bh = compactInterface ? 40 : 48, pipH = compactInterface ? 12 : 14;
            float artTop = pad + nameH * 1.55f, artH = h - artTop - bh - pipH - pad * 3 - (compactInterface ? 14 : 18);
            float art = Mathf.Min(artH, w - pad * 2);
            CrewChestArt(id + "/chest", new Rect((w - art) / 2, artTop, art, art), def, open, card);
            if (flash > 0) coastalUi.Pose(id + "/chest", 0, 1 + .08f * Ease.Pulse(1 - flash));
            // Ten pips: filled for chests bought; the tenth is gold, it always holds the blueprint.
            float py = artTop + art + (compactInterface ? 4 : 6), pg = 3, pw = Mathf.Min(16, (w - pad * 2 - pg * 9) / 10), px = (w - (pw * 10 + pg * 9)) / 2;
            for (int i = 0; i < Chests.CrewChestOffer; i++)
            {
                bool done = i < bought, last = i == Chests.CrewChestOffer - 1;
                var c = done ? Skin.Teal : last ? RarityColour(CardRarity.Gold) : new Color(.78f, .8f, .8f, 1);
                coastalUi.Box($"{id}/pip{i}", new Rect(px + i * (pw + pg), py, pw, pipH * (last ? 1 : .7f)), "", c, card, false);
            }
            string line = !open ? $"Unlocks at tier {def.TierGranted}" : left <= 0 ? "Offer complete" : left == 1 ? "Last chest: blueprint guaranteed" : $"Blueprint guaranteed in {left}";
            coastalUi.Text(id + "/left", new Rect(pad, py + pipH + 2, w - pad * 2, compactInterface ? 14 : 18), line, Skin.Type.Caption, Skin.InkSoft, TextAnchor.MiddleCenter, card);
            int price = Chests.CrewChestPrice(def); string cid = def.Id;
            var br = new Rect(pad, h - bh - pad, w - pad * 2, bh);
            if (!open) coastalUi.Secondary(id + "/buy", br, "Locked", null, "v2-icon-lock", false, card);
            else if (left <= 0) coastalUi.Secondary(id + "/buy", br, "Sold out", null, null, false, card);
            else coastalUi.Primary(id + "/buy", br, $"{price:N0}", () => BuyCrewChestWithFx(cid), "v2-icon-coin", State.Coins >= price, card);
        }

        // The crew chest with the crew member's face in its porthole (or on the lid until the crew chest art lands).
        void CrewChestArt(string id, Rect r, CardDef def, bool open, Transform parent)
        {
            var g = coastalUi.Group(id, r, parent);
            float s = r.width;
            coastalUi.Icon(id + "/shadow", new Rect(s * .1f, s * .8f, s * .8f, s * .2f), "fx-chest-shadow", g);
            CrewPorthole(id, s, def.Id, g, open ? Color.white : new Color(.3f, .36f, .42f, 1), open);
            coastalUi.Icon(id + "/art", new Rect(0, 0, s, s), ChestArt(ChestKind.Crew, false), g, open ? Color.white : new Color(.62f, .66f, .7f, 1));
            if (!open) coastalUi.Icon(id + "/lock", new Rect(s * .38f, s * .7f, s * .24f, s * .24f), "v2-icon-lock", g);
            // Offers you can afford breathe.
            coastalUi.Pose(id, 0, open ? 1 + .015f * Mathf.Sin(Now * 2.2f + r.x * .01f) : 1);
        }

        // The crew member's face in the crew chest's porthole, for a chest drawn at (0, 0, s, s) in `parent`. Draw it
        // before the chest: the glass is a transparent hole (Art/Source/CrewChests; centre 37% across and 61% down,
        // 26% of the chest wide) and the brass ring frames the face.
        void CrewPorthole(string id, float s, string crewId, Transform parent, Color tint, bool glint)
        {
            bool own = ArtLibrary.Get()?.UiTex("v2-chest-crew-closed") != null;
            float d = s * (own ? .26f : .34f);
            var glass = coastalUi.Sliced(id + "/glass", own ? Centered(s * .37f, s * .615f, d, d) : Centered(s * .5f, s * .56f, d, d), "v2-btn-round", parent, Color.white);
            var mask = glass.GetComponent<UnityEngine.UI.Mask>() ?? glass.gameObject.AddComponent<UnityEngine.UI.Mask>();
            mask.showMaskGraphic = false;
            coastalUi.Icon(id + "/face", new Rect(-d * .08f, -d * .02f, d * 1.16f, d * 1.16f), "art108-" + crewId + "-96", glass, tint);
            if (glint && ArtLibrary.Get()?.UiTex("fx-porthole-glint") != null)
            {
                float p = (Now * .3f + s * .01f) % 1f;
                coastalUi.Icon(id + "/glint", new Rect(0, 0, d, d), "fx-porthole-glint", glass, new Color(1, 1, 1, p < .35f ? Ease.Pulse(p / .35f) : 0));
            }
        }

        // ---- welcome chest (tutorial) -----------------------------------------------------------------

        void WelcomeChestCard(Rect body)
        {
            float W = Mathf.Min(body.width, 560), H = Mathf.Min(body.height, compactInterface ? 300 : 440);
            var card = coastalUi.Card("chests/welcome", new Rect(body.x + (body.width - W) / 2, body.y, W, H), Skin.Card.Soft);
            float pad = compactInterface ? 12 : 20, bh = compactInterface ? 48 : 60;
            bool side = compactInterface;
            float art = side ? H - pad * 2 : Mathf.Min(W * .42f, H - bh - 210);
            var artRect = side ? new Rect(pad, pad, art, art) : new Rect((W - art) / 2, pad + 64, art, art);
            coastalUi.Icon("chests/welcome/glow", new Rect(artRect.x - art * .3f, artRect.y - art * .3f, art * 1.6f, art * 1.6f), "fx-glow", card, Tint(Skin.Teal, .45f + .1f * Mathf.Sin(Now * 2)));
            coastalUi.Icon("chests/welcome/shadow", new Rect(artRect.x + art * .1f, artRect.yMax - art * .2f, art * .8f, art * .2f), "fx-chest-shadow", card);
            coastalUi.Icon("chests/welcome/art", artRect, ChestArt(ChestKind.Welcome, false), card);
            float phase = Now % 2.6f;
            coastalUi.Pose("chests/welcome/art", phase < .5f ? Mathf.Sin(phase * 40) * 6 * (1 - phase / .5f) : 0, 1 + .025f * Mathf.Sin(Now * 2.4f));
            Sparkles("chests/welcome/spark", body.x + (body.width - W) / 2 + artRect.center.x, body.y + artRect.center.y, art * .6f, 5, 1);
            float tx = side ? pad * 2 + art : pad, tw = side ? W - tx - pad : W - pad * 2;
            coastalUi.Text("chests/welcome/title", new Rect(tx, side ? pad : pad, tw, 40), "A welcome chest", Skin.Type.Display, Skin.Ink, side ? TextAnchor.MiddleLeft : TextAnchor.MiddleCenter, card);
            coastalUi.Text("chests/welcome/body", new Rect(tx, side ? pad + 44 : artRect.yMax + 14, tw, side ? H - pad * 3 - bh - 44 : 60),
                "Your new boat needs a navigator. Open it to meet Mira, your first mate.", Skin.Type.Body, Skin.Teal, side ? TextAnchor.UpperLeft : TextAnchor.UpperCenter, card);
            coastalUi.Primary("chests/welcome/open", side ? new Rect(tx, H - pad - bh, tw, bh) : new Rect((W - 280) / 2, H - pad - bh, 280, bh), "Open", () => StartReveal(ChestKind.Welcome), null, true, card);
        }
    }
}

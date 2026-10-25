using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // Crew office v2 (docs/plans/CREW-CARDS-V2.md): the crew garage, card panel, chests, tools and the renown road.
    // Motion lives in CrewGarageFx.cs. Every action goes through the VoyageGame card wrappers (harbour only, saved).
    public partial class VoyageGame
    {
        int crewTab;                 // 0 crew, 1 chests, 2 recruit, 3 tools, 4 renown
        string cardPanelId;          // card shown in the panel, null when closed
        int toolPickSlot = -1;       // panel slot whose tool picker is open
        int selectedTool;            // tools page selection (uid)
        int renownChoice;            // renown milestone waiting for a blueprint choice, 0 when none

        internal float cardUiClock = -1;      // fixed clock for captures; -1 = real time
        float Now => cardUiClock >= 0 ? cardUiClock : Time.unscaledTime;

        public static Color RarityColour(CardRarity r) => r switch
        {
            CardRarity.White => Palette.Hex("A9B2B5"), CardRarity.Green => Skin.Green, CardRarity.Blue => Skin.Blue,
            CardRarity.Purple => Skin.Purple, CardRarity.Gold => Skin.Gold, _ => Skin.Red,
        };
        static string FrameArt(CardRarity r) => "art108-frame-" + r.ToString().ToLowerInvariant();
        static string ToolTile(CardRarity r) => "v2-tool-tile-" + r.ToString().ToLowerInvariant();
        static string RoleIcon(CardRole role) => role switch
        {
            CardRole.Fisher => "v2-icon-rod", CardRole.Deckhand => "v2-icon-sort", CardRole.Navigator => "v2-icon-wheel", _ => "v2-icon-engine",
        };
        static string SpecialityWord(Catchline.Game.Speciality s) => s switch
        {
            Catchline.Game.Speciality.CagesLines => "Pots and lines", Catchline.Game.Speciality.Navigation => "Navigation", _ => s.ToString(),
        };
        static string ChestArt(ChestKind k, bool open) => ChestLayer(k, open ? "open" : "closed");
        // Chest art by kind; the welcome and crew chests fall back to the crate and captain's chest until their own art lands.
        static string ChestLayer(ChestKind k, string layer)
        {
            string own = "v2-chest-" + k switch { ChestKind.Crate => "crate", ChestKind.SeaChest => "sea", ChestKind.Welcome => "welcome", ChestKind.Crew => "crew", _ => "captain" } + "-" + layer;
            if (k is ChestKind.Welcome or ChestKind.Crew && ArtLibrary.Get()?.UiTex(own) == null)
                return "v2-chest-" + (k == ChestKind.Welcome ? "crate" : "captain") + "-" + layer;
            return own;
        }

        // ---- page ------------------------------------------------------------------------------------

        void CrewOfficePage(Rect area)
        {
            if (State.Roster.Count == 0 && State.CardTier < 1) { EmptyCrewPage(area); return; }
            var report = State.ReadRoster();
            float sh = compactInterface ? 48 : 56, pill = compactInterface ? 132 : 170;
            bool claimable = RenownClaimable;
            string[] labels = { "Crew", "Chests", "Recruit", "Tools", "Renown" };
            float sw = Mathf.Min(area.width - pill - 12, compactInterface ? 560 : 780);
            coastalUi.PageSwitch("crew/tabs", new Rect(area.x, area.y, sw, sh), labels, crewTab, i => { crewTab = i; toolPickSlot = -1; MenuSound(); }, new[] { "crew/tab/crew", "crew/tab/chests", "crew/tab/recruit", "crew/tab/tools", "crew/tab/renown" });
            TabBadge("crew/tab/chests", report.PendingChests > 0 ? report.PendingChests.ToString() : null);
            TabBadge("crew/tab/renown", claimable ? "!" : null);
            TokenPill("crew/tokens", new Rect(area.xMax - pill, area.y, pill, sh), report.Tokens);
            var body = new Rect(area.x, area.y + sh + 12, area.width, area.height - sh - 12);
            // A chest reveal covers the page: leave the page under it empty so nothing reads through the dim.
            if (reveal != null) return;
            switch (crewTab)
            {
                case 1: ChestsPage(body); break;
                case 2: RecruitPage(body); break;
                case 3: ToolsPage(body); break;
                case 4: RenownPage(body); break;
                default: CrewGrid(body, report); break;
            }
        }

        void EmptyCrewPage(Rect list)
        {
            // The rowboat has no berths: say where crew comes from instead of an empty page.
            float ew = list.width * .7f, eh = Mathf.Min(list.height - 24, compactInterface ? 150 : 200), p = eh - 40;
            var empty = coastalUi.Slab("crew/empty", new Rect(list.x + list.width * .15f, list.y + 12, ew, eh), null, true);
            coastalUi.Portrait("crew/empty/portrait", new Rect(24, 20, p, p), "captain", empty);
            coastalUi.Text("crew/empty/title", new Rect(p + 48, 16, ew - p - 72, eh * .4f), "Just you and the oars", Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, empty);
            coastalUi.Text("crew/empty/body", new Rect(p + 48, eh * .4f + 22, ew - p - 72, eh * .6f - 40), "The rowboat has no berths. Refit to a skiff at the Chandlery: a welcome chest brings Mira, your navigator.", Skin.Type.Body, Skin.Teal, TextAnchor.UpperLeft, empty);
        }

        // A coral count badge on a tab's top-right corner, bobbing gently; null hides it.
        void TabBadge(string tabId, string text)
        {
            string id = tabId + "/badge";
            if (text == null || !coastalUi.TryFind(tabId, out var tab)) return;
            float s = compactInterface ? 22 : 30, bob = Mathf.Sin(Now * 4 + tab.x * .01f) * 1.5f;
            var r = new Rect(tab.xMax - s * .9f, tab.y - s * .3f + bob, s, s);
            coastalUi.Sliced(id, r, "v2-pill-cream", null, Palette.Hex("E2683A"));
            coastalUi.Text(id + "/n", r, text, Skin.Type.Caption, Skin.Cream, TextAnchor.MiddleCenter, null, true);
        }

        // A small cream chip (icon and words) laid out left to right from x.
        void InfoChip(string id, ref float x, float y, float h, string icon, string text)
        {
            float w = h + 10 + text.Length * (compactInterface ? 5.6f : 6.6f) + 12;
            var chip = coastalUi.Sliced(id, new Rect(x, y, w, h), "v2-pill-cream");
            coastalUi.Icon(id + "/icon", new Rect(6, 4, h - 8, h - 8), icon, chip);
            coastalUi.Text(id + "/text", new Rect(h + 4, 0, w - h - 10, h), text, Skin.Type.Caption, Skin.Ink, TextAnchor.MiddleLeft, chip);
            x += w + 8;
        }

        void TokenPill(string id, Rect r, int tokens)
        {
            var pill = coastalUi.Sliced(id, r, "v2-pill-cream");
            float s = Mathf.Min(40, r.height - 10);
            float bump = Now - tokenFxAt < .5f ? Ease.Pulse((Now - tokenFxAt) / .5f) * .25f : 0;
            coastalUi.Icon(id + "/icon", new Rect(10, (r.height - s) / 2, s, s), "v2-icon-token", pill);
            coastalUi.Pose(id + "/icon", 0, 1 + bump);
            coastalUi.Text(id + "/value", new Rect(s + 16, 0, r.width - s - 24, r.height - 2), tokens.ToString("N0"), Skin.Type.Number, Skin.Ink, TextAnchor.MiddleLeft, pill);
        }

        // ---- crew grid ---------------------------------------------------------------------------------

        void CrewGrid(Rect body, RosterReport report)
        {
            float infoH = 30;
            // Three chips: berths filled, the next departure's wages, renown.
            float cx = body.x;
            InfoChip("crew/info/berths", ref cx, body.y, infoH, "v2-badge-tick", $"{report.Deployed} / {report.Berths} aboard");
            InfoChip("crew/info/wages", ref cx, body.y, infoH, "v2-icon-coin", $"{report.Wages:N0} wages per trip");
            InfoChip("crew/info/renown", ref cx, body.y, infoH, "v2-icon-renown", $"Renown {report.Renown}");
            if (report.FreeBlueprints > 0)
                coastalUi.CardButton("crew/give", new Rect(body.xMax - 200, body.y - 2, 200, infoH + 4), "Give blueprint", () => { renownChoice = -1; MenuSound(); }, "v2-icon-blueprint");
            var list = new Rect(body.x, body.y + infoH + 6, body.width, body.height - infoH - 6);
            float gap = compactInterface ? 10 : 14, target = compactInterface ? 128 : 170;
            int cols = Mathf.Max(2, Mathf.FloorToInt((list.width - 12 + gap) / (target + gap)));
            float cw = (list.width - 12 - gap * (cols - 1)) / cols, ch = cw * 4 / 3f;
            var cards = State.Roster;
            // Crew who have not joined follow the roster, locked, in tier order.
            var missing = Cards.All.Where(d => !CardRoster.Owns(cards, d.Id)).ToList();
            int total = cards.Count + missing.Count;
            var content = coastalUi.Scroll("crew/grid", list, Mathf.Ceil(total / (float)cols) * (ch + gap) + 8);
            for (int m = 0; m < missing.Count; m++)
            {
                int n = cards.Count + m; var d = missing[m];
                var r = new Rect(n % cols * (cw + gap), 4 + n / cols * (ch + gap), cw, ch);
                LockedFace("crew/grid/" + d.Id, r, d, content);
                coastalUi.HitArea("crew/grid/" + d.Id + "/tap", new Rect(0, 0, cw, ch), () => OpenRecruit(d), coastalUi.ElementRect("crew/grid/" + d.Id));
            }
            for (int n = 0; n < cards.Count; n++)
            {
                var c = cards[n]; string id = "crew/grid/" + c.Id, cardId = c.Id;
                var r = new Rect(n % cols * (cw + gap), 4 + n / cols * (ch + gap), cw, ch);
                CardFace(id, r, c, content, c.Rarity, false);
                coastalUi.HitArea(id + "/tap", new Rect(0, 0, cw, ch), () => { cardPanelId = cardId; toolPickSlot = -1; MenuSound(); }, coastalUi.ElementRect(id));
                float bump = fxCard == c.Id && Now - levelFxAt < .4f ? Ease.Pulse((Now - levelFxAt) / .4f) * .06f : 0;
                coastalUi.Pose(id, 0, 1 + bump);
            }
        }

        // One card face: rarity frame, portrait, name plate and three rows (level, role, blueprints).
        void CardFace(string id, Rect r, CardState c, Transform parent, CardRarity rarity, bool big)
        {
            var def = c.Def; bool avail = State.CardAvailable(c);
            var g = coastalUi.Group(id, r, parent);
            float w = r.width, h = r.height;
            if (avail && rarity >= CardRarity.Purple)
            {
                // Rare cards breathe a soft glow of their colour.
                var glow = RarityColour(rarity); glow.a = .28f + .12f * Mathf.Sin(Now * 2.2f + r.x * .01f);
                coastalUi.Icon(id + "/glow", new Rect(-w * .18f, -h * .14f, w * 1.36f, h * 1.28f), "fx-glow", g, glow);
            }
            // Solid sea behind the portrait window so nothing underneath shows through the frame.
            coastalUi.Box(id + "/window", new Rect(w * .1f, h * .075f, w * .8f, h * .43f), "", Palette.Hex("1C3A5A"), g, false);
            coastalUi.Icon(id + "/frame", new Rect(0, 0, w, h), avail ? FrameArt(rarity) : "art108-frame-locked", g);
            coastalUi.Icon(id + "/portrait", new Rect(w * .1f, h * .075f, w * .8f, h * .43f), "art108-" + def.Id, g, avail ? Color.white : new Color(.5f, .56f, .6f, 1));
            if (avail && rarity == CardRarity.Mythic)
            {
                // Shine sweep across Mythic cards: a pass every four seconds.
                var clip = coastalUi.Group(id + "/shine", new Rect(0, 0, w, h), g); coastalUi.Clip(id + "/shine");
                float p = (Now * .25f + r.y * .002f) % 1f;
                coastalUi.Icon(id + "/shine/sweep", new Rect(Mathf.Lerp(-w * 1.1f, w * 1.1f, Ease.OutCubic(p / .45f)), 0, w, h), "art108-frame-mythic-shine", clip, new Color(1, 1, 1, p < .45f ? .9f : 0));
            }
            coastalUi.Text(id + "/name", new Rect(w * .08f, h * .512f, w * .84f, h * .086f), def.Name.ToUpperInvariant(), big ? Skin.Type.Heading : Skin.Type.Caption, Skin.Cream, TextAnchor.MiddleCenter, g);
            float[] rowY = { .613f, .726f, .839f }; float rh = h * .092f, ix = w * .125f, isz = Mathf.Min(w * .1f, rh * .8f);
            var type = big ? Skin.Type.Body : Skin.Type.Caption;
            string levelText = avail ? (c.AtCap ? $"Lv {c.Level} max" : $"Lv {c.Level} / {c.LevelCap}") : $"Joins at tier {def.TierGranted}";
            string bpText = c.Maxed ? "Fully starred" : c.IsMythic ? $"Stars {c.Stars} · {c.Blueprints}/{c.BlueprintsNeeded}" : $"Blueprints {c.Blueprints}/{c.BlueprintsNeeded}";
            string[] rows = { levelText, big && def.Role != CardRole.Navigator ? $"{def.Role} · {SpecialityWord(def.Speciality)}" : def.Role.ToString(), bpText };
            string[] icons = { "v2-icon-token", RoleIcon(def.Role), "v2-icon-blueprint" };
            for (int i = 0; i < 3; i++)
            {
                float y = h * rowY[i];
                coastalUi.Icon($"{id}/row{i}/icon", new Rect(ix + (w * .1f - isz) / 2, y + (rh - isz) / 2, isz, isz), icons[i], g);
                coastalUi.Text($"{id}/row{i}/text", new Rect(w * .25f, y, w * .66f, rh), rows[i], type, Skin.Ink, TextAnchor.MiddleLeft, g);
            }
            float b = w * .2f;
            if (State.Deployment.Contains(c.Id)) coastalUi.Icon(id + "/aboard", new Rect(w * .02f, h * .015f, b, b), "v2-badge-tick", g);
            if (State.FocusCard == c.Id) coastalUi.Icon(id + "/focus", new Rect(w - b * 1.02f, h * .015f, b, b), "v2-icon-focus", g);
            for (int s = 0; s < c.Stars; s++)
                coastalUi.Icon($"{id}/star{s}", new Rect(w * .5f + (s - c.Stars / 2f) * w * .13f, h * .43f, w * .13f, w * .13f), "v2-icon-star", g);
            if (!avail) coastalUi.Icon(id + "/lock", new Rect(w * .36f, h * .2f, w * .28f, w * .28f), "v2-icon-lock", g);
            else if (!big && (c.CanRankUp || c.CanStar || CanAffordLevel(c)))
            {
                // Something to spend: a bobbing badge, a blueprint when a rank is ready.
                float bob = Mathf.Sin(Now * 5 + r.x * .02f) * h * .012f;
                coastalUi.Icon(id + "/ready", new Rect(w * .74f, h * .6f + bob - b * .2f, b, b), c.CanRankUp || c.CanStar ? "v2-icon-blueprint" : "v2-icon-token", g);
                coastalUi.Pose(id + "/ready", Mathf.Sin(Now * 3) * 6, 1);
            }
        }

        bool CanAffordLevel(CardState c) => !c.AtCap && State.Tokens >= CardProgression.TokensForLevel(c.Level) && State.Coins >= CardProgression.CoinsForLevel(c.Level);

        // ---- card panel -------------------------------------------------------------------------------

        void InterfaceCardOverlays()
        {
            if (CurrentMode != Mode.Harbour) { reveal = null; cardPanelId = null; renownChoice = 0; InterfaceAbilityPops(); return; }
            if (reveal != null) { ChestRevealOverlay(); return; }
            bool office = panelOpen && hudTab == HudTab.CrewOffice;
            if (!office) { cardPanelId = null; renownChoice = 0; return; }
            if (cardPanelId != null) CardPanel();
            if (renownChoice != 0) BlueprintChooser();
            if (rankFxAt > 0) RankUpOverlay();
        }

        void CloseCardPanel() { cardPanelId = null; toolPickSlot = -1; MenuSound(); }

        void CardPanel()
        {
            var c = CardRoster.Find(State.Roster, cardPanelId);
            if (c == null) { cardPanelId = null; return; }
            var def = c.Def;
            coastalUi.Scrim("cardpanel/dim", CloseCardPanel);
            float W = Mathf.Min(iw - 24, 980), H = Mathf.Min(ih - 24, 640), pad = compactInterface ? 12 : 18;
            var r = new Rect((iw - W) / 2, (ih - H) / 2, W, H);
            var slab = coastalUi.Slab("cardpanel", r, null, true); Block(r);

            // Left: the card, with level and rank animations.
            float cardH = H - pad * 2, cardW = cardH * .75f;
            if (cardW > W * .36f) { cardW = W * .36f; cardH = cardW / .75f; }
            var cardRect = new Rect(pad, (H - cardH) / 2, cardW, cardH);
            CardPanelCard(cardRect, c, slab);

            // Right: header, then a scroll of level, abilities and tools.
            float x = pad * 2 + cardW, cw = W - x - pad, headH = compactInterface ? 64 : 78;
            coastalUi.Text("cardpanel/name", new Rect(x, pad - 4, cw - 70, headH * .6f), def.Name.ToUpperInvariant(), Skin.Type.Display, Skin.Ink, TextAnchor.MiddleLeft, slab);
            string rank = CardProgression.RarityName(c.Rarity).ToUpperInvariant() + (c.Stars > 0 ? $" · {c.Stars} STARS" : "");
            coastalUi.Text("cardpanel/rank", new Rect(x, pad - 4 + headH * .58f, cw - 70, headH * .4f), $"{rank} · {def.Role} · {SpecialityWord(def.Speciality)}", Skin.Type.Small, Darker(RarityColour(c.Rarity)), TextAnchor.MiddleLeft, slab);
            coastalUi.CardButton("cardpanel/close", new Rect(W - pad - 56, pad, 56, 52), null, CloseCardPanel, "v2-icon-back", true, slab);

            var area = new Rect(r.x + x, r.y + pad + headH, cw, H - pad * 2 - headH);
            float contentH = CardPanelBody(area, c, true);
            CardPanelBody(area, c, false, contentH);
        }

        // The big card in the panel: glows in its rarity and pops on a level up.
        void CardPanelCard(Rect r, CardState c, Transform parent)
        {
            var col = RarityColour(c.Rarity); float k = fxCard == c.Id ? Now - levelFxAt : 9;
            coastalUi.Icon("cardpanel/glow", new Rect(r.x - r.width * .15f, r.y - r.height * .1f, r.width * 1.3f, r.height * 1.2f), "fx-glow", parent, Tint(col, .35f + .1f * Mathf.Sin(Now * 2)));
            CardFace("cardpanel/card", r, c, parent, c.Rarity, true);
            coastalUi.Pose("cardpanel/card", 0, k < .45f ? 1 + .05f * Ease.Pulse(k / .45f) : 1);
            if (k < .7f)
            {
                coastalUi.Icon("cardpanel/burst", new Rect(r.x, r.y + r.height * .1f, r.width, r.width), "fx-burst", parent, Tint(Color.white, .5f * (1 - Ease.Clamp(k / .7f))));
                coastalUi.Pose("cardpanel/burst", 0, .5f + Ease.OutCubic(k / .7f));
                float up = Ease.OutCubic(k / .7f);
                coastalUi.Icon("cardpanel/arrow", new Rect(r.x + r.width * .3f, r.y + r.height * (.45f - .3f * up), r.width * .4f, r.width * .4f), "fx-levelup-arrow", parent, Tint(Color.white, 1 - Ease.Clamp((k - .35f) / .35f)));
                coastalUi.Text("cardpanel/plus", new Rect(r.x, r.y + r.height * (.3f - .12f * Ease.OutCubic(k / .7f)), r.width, 50), $"LEVEL {c.Level}", Skin.Type.Display, Skin.Cream, TextAnchor.MiddleCenter, parent, true);
            }
        }

        static Color Darker(Color c) => new Color(c.r * .62f, c.g * .62f, c.b * .62f, 1);

        // Measures (measure = true) or draws the panel body. Returns the content height.
        float CardPanelBody(Rect area, CardState c, bool measure, float contentH = 0)
        {
            var def = c.Def; float w = area.width - 14, y = 0, gap = compactInterface ? 10 : 14;
            Transform content = measure ? null : coastalUi.Scroll("cardpanel/scroll", area, contentH);
            const string P = "cardpanel/scroll/";

            // Stats.
            float th = compactInterface ? 58 : 66, tw = (w - gap * 2) / 3;
            if (!measure)
            {
                coastalUi.StatTile(P + "speed", new Rect(0, y, tw, th), "v2-icon-clock", "Work speed", $"x{CardProgression.WorkMult(c):0.00}", null, Skin.Bar.Good, content);
                coastalUi.StatTile(P + "wage", new Rect(tw + gap, y, tw, th), "v2-icon-coin", "Wage", $"{c.Wage()} / trip", null, Skin.Bar.Good, content);
                if (def.Role == CardRole.Fisher)
                    coastalUi.StatTile(P + "third", new Rect((tw + gap) * 2, y, tw, th), "v2-icon-rod", "Strike", $"{CardProgression.StrikeChance(c.Rarity, c.Level) * 100:0}%", null, Skin.Bar.Good, content);
                else
                    coastalUi.StatTile(P + "third", new Rect((tw + gap) * 2, y, tw, th), "v2-icon-renown", "Renown", c.Renown.ToString(), null, Skin.Bar.Good, content);
            }
            y += th + gap;

            // Level or rank.
            float bh = compactInterface ? 52 : 60, blockH = 44 + bh + 16;
            if (!measure)
            {
                var block = coastalUi.Card(P + "level", new Rect(0, y, w, blockH), Skin.Card.Soft, content);
                string cardId = c.Id;
                if (!c.AtCap)
                {
                    float shown = levelBarFrom >= 0 && fxCard == c.Id && Now - levelFxAt < .6f
                        ? Mathf.Lerp(levelBarFrom, c.Level, Ease.OutCubic((Now - levelFxAt) / .6f)) : c.Level;
                    coastalUi.Text(P + "level/title", new Rect(14, 6, w * .45f, 34), $"Level {c.Level} / {c.LevelCap}", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, block);
                    coastalUi.ProgressBar(P + "level/bar", new Rect(w * .45f, 18, w * .55f - 16, 12), (shown - 1) / Mathf.Max(1, c.LevelCap - 1), Skin.Bar.Teal, block);
                    int tok = CardProgression.TokensForLevel(c.Level), coins = CardProgression.CoinsForLevel(c.Level);
                    bool can = CanAffordLevel(c);
                    coastalUi.Primary(P + "level/up", new Rect(14, 44, w * .66f - 20, bh), $"{tok} tokens · {coins:N0} coins", () => LevelUpWithFx(cardId, false), "v2-icon-token", can, block);
                    coastalUi.Secondary(P + "level/cap", new Rect(w * .66f + 2, 44, w * .34f - 16, bh), "To max", () => LevelUpWithFx(cardId, true), null, can, block);
                }
                else if (!c.Maxed)
                {
                    int need = c.BlueprintsNeeded;
                    string title = c.IsMythic ? $"Star {c.Stars + 1} of 5" : $"Rank up to {CardProgression.RarityName(c.Rarity + 1)}";
                    coastalUi.Text(P + "level/title", new Rect(14, 6, w * .5f, 34), title, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, block);
                    coastalUi.Icon(P + "level/bp", new Rect(w * .5f, 6, 34, 34), "v2-icon-blueprint", block);
                    coastalUi.ProgressBar(P + "level/bar", new Rect(w * .5f + 42, 18, w * .5f - 140, 12), c.Blueprints / (float)Mathf.Max(1, need), Skin.Bar.Good, block);
                    coastalUi.Text(P + "level/count", new Rect(w - 90, 6, 76, 34), $"{c.Blueprints}/{need}", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleRight, block);
                    bool can = c.CanRankUp || c.CanStar;
                    string label = can ? (c.IsMythic ? "Add a star" : "Rank up") : "Blueprints come from chests and the renown road";
                    coastalUi.Primary(P + "level/up", new Rect(14, 44, w - 28, bh), label, () => RankUpWithFx(cardId), can ? "v2-icon-blueprint" : null, can, block);
                }
                else
                {
                    coastalUi.Text(P + "level/title", new Rect(14, 6, w - 28, 34), "Mythic, fully starred. The top of the ladder.", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, block);
                    coastalUi.Text(P + "level/body", new Rect(14, 44, w - 28, bh), "Blueprints for this crew member now become blueprints of your choice.", Skin.Type.Body, Skin.InkSoft, TextAnchor.MiddleLeft, block);
                }
            }
            y += blockH + gap;

            // Abilities: unlocked ones in full colour, locked ones greyed with the rarity that unlocks them.
            if (!measure) coastalUi.Text(P + "abilities", new Rect(4, y, w, 28), "ABILITIES", Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleLeft, content);
            y += 30;
            float rowH = compactInterface ? 64 : 70;
            foreach (var a in def.Abilities)
            {
                if (!measure)
                {
                    bool on = c.Has(a), isTrait = a == def.Trait;
                    string aid = P + "ability/" + a.Id;
                    var row = coastalUi.Card(aid, new Rect(0, y, w, rowH), Skin.Card.Soft, content);
                    var col = RarityColour(isTrait ? CardRarity.Gold : a.Unlock);
                    coastalUi.Sliced(aid + "/dot", new Rect(10, (rowH - 36) / 2, 36, 36), "v2-pill-cream", row, on ? col : new Color(col.r, col.g, col.b, .35f));
                    // Inside the rarity disc: the role's emblem (a star for the always-on trait), or a lock until unlocked.
                    coastalUi.Icon(aid + "/lock", new Rect(16, (rowH - 24) / 2, 24, 24), !on ? "v2-icon-lock" : isTrait ? "v2-icon-star" : RoleIcon(def.Role), row);
                    string tag = isTrait ? "Always" : on ? CardProgression.RarityName(a.Unlock) : "Unlocks at " + CardProgression.RarityName(a.Unlock);
                    coastalUi.Text(aid + "/name", new Rect(54, 4, w * .5f, 28), a.Name, Skin.Type.Heading, on ? Skin.Ink : Skin.InkSoft, TextAnchor.MiddleLeft, row);
                    coastalUi.Text(aid + "/tag", new Rect(w * .5f, 4, w * .5f - 14, 28), tag, Skin.Type.Caption, on ? Darker(col) : Skin.InkSoft, TextAnchor.MiddleRight, row);
                    coastalUi.Text(aid + "/text", new Rect(54, 30, w - 66, rowH - 34), a.Text, Skin.Type.Small, on ? Skin.InkSoft : Tint(Skin.InkSoft, .6f), TextAnchor.UpperLeft, row);
                    bool fresh = fxCard == c.Id && Now - rankFxAt < 2.2f && a.Unlock == c.Rarity && !isTrait;
                    if (fresh) coastalUi.Pose(aid, 0, 1 + Ease.Pulse(Mathf.Clamp01((Now - rankFxAt - .8f) / .6f)) * .04f);
                    else coastalUi.Pose(aid);
                }
                y += rowH + 8;
            }
            y += gap - 8;

            // Tools.
            if (!measure) coastalUi.Text(P + "tools", new Rect(4, y, w, 28), $"TOOLS · {def.Role} tools", Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleLeft, content);
            y += 30;
            float slot = compactInterface ? 76 : 88;
            if (!measure) ToolSlots(P + "slot", new Rect(0, y, w, slot), c.Id, content);
            y += slot + gap;
            if (toolPickSlot >= 0)
            {
                float pickH = ToolPicker(P + "pick", new Rect(0, y, w, 0), c.Id, measure ? null : content, measure);
                y += pickH + gap;
            }

            // Focus and deployment.
            float ah = compactInterface ? 52 : 60;
            if (!measure)
            {
                string cardId = c.Id; bool focus = State.FocusCard == c.Id, aboard = State.Deployment.Contains(c.Id);
                coastalUi.Secondary(P + "focus", new Rect(0, y, w * .5f - 6, ah), focus ? "Focused: 75% of blueprints" : "Make focus", () => { SetFocusCard(focus ? "" : cardId); MenuSound(); }, "v2-icon-focus", true, content);
                bool canDeploy = def.Role != CardRole.Navigator && State.CardAvailable(c) && (aboard || State.Deployment.Count < State.CardBerths);
                coastalUi.Secondary(P + "deploy", new Rect(w * .5f + 6, y, w * .5f - 6, ah), def.Role == CardRole.Navigator ? "First mate, always aboard" : aboard ? "Stand down" : "Bring aboard",
                    () => { DeployCard(cardId, !aboard); MenuSound(); }, "v2-icon-crew", canDeploy, content);
            }
            y += ah + 8;
            return y;
        }

        void ToolSlots(string id, Rect r, string owner, Transform parent)
        {
            var card = CardRoster.Find(State.Roster, owner);
            int open = State.ToolSlotCount(owner);
            float s = r.height, gap = 12;
            for (int i = 0; i < CardProgression.MaxToolSlots; i++)
            {
                string sid = $"{id}{i}"; int slotIndex = i;
                var rect = new Rect(r.x + i * (s + gap), r.y, s, s);
                if (i >= open)
                {
                    coastalUi.Sliced(sid, rect, "v2-inset", parent);
                    coastalUi.Icon(sid + "/lock", new Rect(s * .3f, s * .16f, s * .4f, s * .4f), "v2-icon-lock", coastalUi.ElementRect(sid));
                    coastalUi.Text(sid + "/at", new Rect(0, s * .58f, s, s * .36f), i == 1 ? "Blue" : "Legendary", Skin.Type.Caption, Skin.InkSoft, TextAnchor.MiddleCenter, coastalUi.ElementRect(sid));
                    continue;
                }
                var tool = State.FindTool(card.ToolUids[i]);
                bool picking = toolPickSlot == i;
                coastalUi.CardButton(sid, rect, null, () => { toolPickSlot = picking ? -1 : slotIndex; MenuSound(); }, null, true, parent);
                var btn = coastalUi.ElementRect(sid);
                if (tool != null) ToolTileFace(sid + "/tool", new Rect(4, 4, s - 8, s - 8), tool, btn);
                else coastalUi.Text(sid + "/plus", new Rect(0, 0, s, s), "+", Skin.Type.Display, picking ? Skin.Teal : Skin.InkSoft, TextAnchor.MiddleCenter, btn);
            }
            float tx = r.x + CardProgression.MaxToolSlots * (s + gap) + 4;
            var bonuses = State.EquippedTools(owner).GroupBy(t => t.Kind).Select(g => $"+{State.ToolBonus(owner, g.Key) * 100:0}% {ToolInfo.Job(g.Key)}");
            string text = bonuses.Any() ? string.Join("\n", bonuses) : "Tap a slot to fit a tool. Tools come from chests; two alike merge into the next rarity.";
            coastalUi.Text(id + "/bonus", new Rect(tx, r.y, r.xMax - tx, s), text, Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleLeft, parent);
        }

        // Tools that fit the open slot. Returns its height.
        float ToolPicker(string id, Rect r, string owner, Transform parent, bool measure)
        {
            var role = CardRoster.Find(State.Roster, owner)?.Def?.Role;
            var fits = State.Tools.Where(t => ToolInfo.CanUse(role, t.Kind)).OrderByDescending(t => t.Rarity).ThenBy(t => t.Kind).ToList();
            float s = compactInterface ? 62 : 70, gap = 8;
            int cols = Mathf.Max(1, Mathf.FloorToInt((r.width - 20 + gap) / (s + gap)));
            int rows = Mathf.Max(1, Mathf.CeilToInt((fits.Count + 1) / (float)cols));
            float h = 44 + rows * (s + gap) + 8;
            if (measure) return h;
            var box = coastalUi.Card(id, new Rect(r.x, r.y, r.width, h), Skin.Card.Selected, parent);
            coastalUi.Text(id + "/title", new Rect(14, 6, r.width - 28, 32), fits.Count == 0 ? $"No {role} tools yet. Open chests to find some." : $"Fit a tool in slot {toolPickSlot + 1}", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, box);
            var card = CardRoster.Find(State.Roster, owner); int current = card.ToolUids[toolPickSlot];
            for (int i = 0; i <= fits.Count; i++)
            {
                var cell = new Rect(10 + i % cols * (s + gap), 44 + i / cols * (s + gap), s, s);
                string cid = $"{id}/t{i}";
                if (i == fits.Count)
                {
                    if (current == 0) break;
                    int slotRemove = toolPickSlot; string o = owner;
                    coastalUi.Secondary(cid, cell, "Off", () => { UnequipTool(o, slotRemove); toolPickSlot = -1; MenuSound(); }, null, true, box);
                    break;
                }
                var t = fits[i]; int uid = t.Uid, slotIndex = toolPickSlot; string ownerId = owner;
                coastalUi.CardButton(cid, cell, null, () => { if (EquipTool(ownerId, slotIndex, uid)) { audio?.Play(VoyageAudio.Cue.Click, .7f); toolPickSlot = -1; } }, null, true, box);
                ToolTileFace(cid + "/face", new Rect(3, 3, s - 6, s - 6), t, coastalUi.ElementRect(cid));
                string holder = State.ToolOwner(t.Uid);
                if (holder != null && holder != owner)
                    coastalUi.Icon(cid + "/holder", new Rect(s - 26, s - 26, 24, 24), holder == GameState.CaptainToolOwner ? "v2-icon-anchor" : "art108-" + holder + "-56", coastalUi.ElementRect(cid));
            }
            return h;
        }

        void ToolTileFace(string id, Rect r, ToolState t, Transform parent)
        {
            coastalUi.Icon(id, r, ToolTile(t.Rarity), parent);
            coastalUi.Icon(id + "/icon", new Rect(r.x + r.width * .14f, r.y + r.height * .12f, r.width * .72f, r.height * .72f), ToolInfo.Icon(t.Kind), parent);
        }
    }
}

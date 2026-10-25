using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace Catchline.Game
{
    // UI v2 tokens (docs/UI-SYSTEM.md section 1). Every colour, size and type style comes from here.
    public static class Skin
    {
        public static readonly Color Plank = Palette.Hex("1E4D7B"), PlankDark = Palette.Hex("163A5E"), Rope = Palette.Hex("C9A46A"),
            Brass = Palette.Hex("D9A441"), Cream = Palette.Hex("F4EFE3"), CreamDeep = Palette.Hex("E8E0CC"), Ink = Palette.Hex("173F57"),
            InkSoft = Palette.Hex("52747C"), HeaderNavy = Palette.Hex("1F4E79"), Orange = Palette.Hex("E36A35"), OrangeDeep = Palette.Hex("B84D22"),
            Teal = Palette.Hex("168F9F"), Good = Palette.Hex("3E9A5B"), Warn = Palette.Hex("E6AD38"), Bad = Palette.Hex("C8443A"),
            White = Color.white, Green = Palette.Hex("4CAF50"), Blue = Palette.Hex("3B82F6"), Purple = Palette.Hex("8E44AD"),
            Gold = Palette.Hex("E6B422"), Red = Palette.Hex("D7263D");
        // Status ink is a darker step of the status colour so words read on pale pills.
        public static readonly Color GoodInk = Palette.Hex("2C7344"), WarnInk = Palette.Hex("9A6A0E"), BadInk = Palette.Hex("A3302A");
        // Every kit surface is drawn through this tint: the white kit reads as a light cream paper (Mo, 2026-10-24).
        public static readonly Color Paper = Palette.Hex("FBF5E6");

        public const float Grid = 8, SlabRadius = 18, CardRadius = 14, Outline = 3, HeaderBand = 44, SlabPad = 16, CardPad = 12,
            ButtonPad = 10, MinTouch = 44, PrimaryHeight = 64, PrimaryHeightPhone = 56, IconButton = 56;

        public enum Type { Display, Number, Heading, Body, Small, Caption }
        public static int Size(Type t) => t switch { Type.Display => 36, Type.Number => 32, Type.Heading => 22, Type.Body => 18, Type.Small => 15, _ => 13 };
        public static bool IsDisplayFace(Type t) => t <= Type.Heading;

        public enum Status { Steady, Busy, BackedUp }
        public static string Word(Status s) => s switch { Status.Steady => "Steady", Status.Busy => "Busy", _ => "Backed up" };
        public static Color Tone(Status s) => s switch { Status.Steady => Good, Status.Busy => Warn, _ => Bad };
        public static Color ToneInk(Status s) => s switch { Status.Steady => GoodInk, Status.Busy => WarnInk, _ => BadInk };
        static string Key(Status s) => s switch { Status.Steady => "good", Status.Busy => "warn", _ => "bad" };

        public enum Bar { Good, Warn, Bad, Teal }
        public enum Card { Soft, Ink, Selected, Alert }
        public enum FishClass { White, Green, Blue, Purple, Gold, Red }
        public static Color ClassColour(FishClass c) => c switch { FishClass.White => White, FishClass.Green => Green, FishClass.Blue => Blue, FishClass.Purple => Purple, FishClass.Gold => Gold, _ => Red };

        internal static string LightSprite(Status s) => "v2-light-" + Key(s);
        internal static string PillSprite(Status s) => "v2-pill-" + Key(s);
        internal static string StatusIcon(Status s) => s switch { Status.Steady => "v2-icon-tick", Status.Busy => "v2-icon-clock", _ => "v2-icon-warning" };
    }

    // UI v2 components (UI-SYSTEM section 2). Logical top-left rects like the rest of CoastalCanvas;
    // every child id is prefixed by its parent id so retained elements never collide.
    public sealed partial class CoastalCanvas
    {
        Font display;
        Font DisplayFont => display != null ? display : display = ArtLibrary.Get()?.DisplayFont ?? font;
        public bool Phone => Height < 600;
        float MinHit => Skin.MinTouch / Mathf.Max(.001f, canvas.scaleFactor);

        Sprite V2(string name, float multiplier = 2)
        {
            if (name == null) return null;
            string key = "v2:" + name;
            if (sprites.TryGetValue(key, out var cached)) return cached;
            var texture = ArtLibrary.Get()?.UiTex(name);
            Sprite result = null;
            if (texture != null)
            {
                SkinSlices.Border.TryGetValue(name, out var border);
                result = UnityEngine.Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), Vector2.one * .5f, 100, 0, SpriteMeshType.FullRect, border);
                result.name = name;
            }
            sprites[key] = result;
            return result;
        }

        // Sliced kit sprites are 2x; the multiplier draws their borders at logical size.
        public RectTransform Sliced(string id, Rect r, string sprite, Transform parent = null, Color? tint = null, bool blocks = false)
        {
            var e = Get(id, r, parent);
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<Image>();
            var s = V2(sprite);
            e.Image.sprite = s; e.Image.type = s != null && s.border != Vector4.zero ? Image.Type.Sliced : Image.Type.Simple;
            e.Image.pixelsPerUnitMultiplier = 2; e.Image.preserveAspect = false; e.Image.fillCenter = true;
            e.Image.color = s == null && tint == null ? Color.clear : tint ?? Skin.Paper; e.Image.raycastTarget = blocks;
            return e.Rect;
        }

        // Icons and illustrations keep their aspect; falls back to the old kit name while art lands.
        public void Icon(string id, Rect r, string sprite, Transform parent = null, Color? tint = null, string fallback = null)
        {
            var e = Get(id, r, parent);
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<Image>();
            var s = V2(sprite) ?? (fallback != null ? Sprite(fallback, false) : null);
            e.Image.sprite = s; e.Image.type = Image.Type.Simple; e.Image.preserveAspect = true;
            e.Image.color = s == null ? Color.clear : tint ?? Color.white; e.Image.raycastTarget = false;
        }

        public void Text(string id, Rect r, string value, Skin.Type type, Color? colour = null, TextAnchor align = TextAnchor.MiddleLeft,
            Transform parent = null, bool outline = false)
        {
            var e = Get(id, r, parent);
            var t = ClippedText(e, id);
            t.font = Skin.IsDisplayFace(type) ? DisplayFont : font;
            int size = Mathf.RoundToInt(Skin.Size(type) * TypeScale);
            t.fontSize = size; t.resizeTextForBestFit = true; t.resizeTextMaxSize = size;
            t.resizeTextMinSize = Mathf.Min(size, Mathf.Max(13, Mathf.RoundToInt(size * .72f)));
            t.color = colour ?? Skin.Ink; t.alignment = align; t.supportRichText = false; t.lineSpacing = .9f;
            t.horizontalOverflow = HorizontalWrapMode.Wrap; t.verticalOverflow = VerticalWrapMode.Truncate; t.raycastTarget = false;
            var o = t.GetComponent<UnityEngine.UI.Outline>();
            if (outline && o == null) { o = t.gameObject.AddComponent<UnityEngine.UI.Outline>(); o.effectColor = Skin.Ink; o.effectDistance = new Vector2(2, -2); }
            if (o != null) o.enabled = outline;
            if (t.text != value) t.text = value;
        }
        float TextWidth(string id) => elements.TryGetValue(id, out var e) && e.Text != null ? Mathf.Min(e.Text.preferredWidth, e.Rect.rect.width) : 0;

        Element Pressable(string id, Rect r, Transform parent, string normal, string pressed, Action action, bool enabled)
        {
            Sliced(id, r, enabled ? normal : "v2-btn-disabled", parent, null, true);
            var e = elements[id];
            if (e.Button == null)
            {
                e.Button = e.Rect.gameObject.AddComponent<Button>();
                e.Button.targetGraphic = e.Image;
                e.Button.onClick.AddListener(() => e.Action?.Invoke());
                e.Button.transition = Selectable.Transition.SpriteSwap;
            }
            e.Button.spriteState = new SpriteState { pressedSprite = enabled && pressed != null ? V2(pressed) : null };
            e.Button.interactable = enabled; e.Action = enabled ? action : null;
            // Hit area grows invisibly to 44 physical px; the artwork keeps its size.
            float min = MinHit;
            bool small = r.width < min || r.height < min;
            if (small)
            {
                var hit = Get(id + "/hit", new Rect(Mathf.Min(0, (r.width - min) / 2), Mathf.Min(0, (r.height - min) / 2), Mathf.Max(min, r.width), Mathf.Max(min, r.height)), e.Rect);
                if (hit.Image == null) hit.Image = hit.Rect.gameObject.AddComponent<Image>();
                hit.Image.sprite = null; hit.Image.color = Color.clear; hit.Image.raycastTarget = true;
            }
            return e;
        }

        // Stable control ids: an alias lets Invoke(alias) press a control drawn under a composite's id.
        readonly Dictionary<string, string> aliases = new();
        public void Alias(string alias, string target) => aliases[alias] = target;
        public RectTransform ElementRect(string id) => elements.TryGetValue(id, out var e) ? e.Rect : null;
        public void SetTextSize(string id, int size)
        {
            if (!elements.TryGetValue(id, out var e) || e.Text == null) return;
            e.Text.fontSize = e.Text.resizeTextMaxSize = Mathf.RoundToInt(size * TypeScale);
        }
        public void SetText(string id, string value)
        {
            if (elements.TryGetValue(id, out var e) && e.Text != null && e.Text.text != value) e.Text.text = value;
        }
        // Invisible, unclickable control that keeps a stable id for Invoke (tests and captures).
        public void HiddenButton(string id, Action action, Transform parent = null)
        {
            var e = Get(id, Rect.zero, parent);
            if (e.Button == null)
            {
                e.Button = e.Rect.gameObject.AddComponent<Button>();
                e.Button.transition = Selectable.Transition.None;
                e.Button.onClick.AddListener(() => e.Action?.Invoke());
            }
            e.Button.interactable = action != null; e.Action = action;
        }
        public void HitArea(string id, Rect r, Action action, Transform parent = null)
        {
            var e = Pressable(id, r, parent, null, null, action, true);
            e.Image.color = Color.clear;
        }
        // Toggle card: selected shows the blue ring and tick badge, off is a plain soft card.
        public RectTransform Toggle(string id, Rect r, bool on, Action toggle, Transform parent = null)
        {
            if (on) Sliced(id + "/glow", new Rect(r.x - 4, r.y - 4, r.width + 8, r.height + 8), "v2-card-selected", parent);
            else Sliced(id + "/glow", Rect.zero, null, parent);
            var e = Pressable(id, r, parent, on ? "v2-card-ink" : "v2-card", "v2-btn-card-pressed", toggle, true);
            e.Image.color = on ? Palette.Hex("EEF4FF") : Skin.Paper;
            Icon(id + "/tick", on ? new Rect(r.width - 30, -10, 40, 40) : Rect.zero, "v2-badge-tick", e.Rect);
            return e.Rect;
        }

        // ---- containers ------------------------------------------------------------------------

        public RectTransform Slab(string id, Rect r, string title = null, bool nails = false, Transform parent = null)
        {
            var slab = Sliced(id, r, title != null ? "v2-slab-titled" : "v2-slab", parent, null, true);
            if (title != null) Text(id + "/title", new Rect(Skin.SlabPad, 4, r.width - Skin.SlabPad * 2, Skin.HeaderBand), title.ToUpperInvariant(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, slab);
            if (nails)
            {
                float top = title != null ? 52 : 8;
                Icon(id + "/nail0", new Rect(8, top, 12, 12), "v2-nail", slab); Icon(id + "/nail1", new Rect(r.width - 20, top, 12, 12), "v2-nail", slab);
                Icon(id + "/nail2", new Rect(8, r.height - 24, 12, 12), "v2-nail", slab); Icon(id + "/nail3", new Rect(r.width - 20, r.height - 24, 12, 12), "v2-nail", slab);
            }
            return slab;
        }

        public RectTransform Card(string id, Rect r, Skin.Card kind = Skin.Card.Soft, Transform parent = null, string headerTitle = null)
        {
            // Selected and alert glows sit 4px outside the card body.
            if (kind == Skin.Card.Selected || kind == Skin.Card.Alert)
                Sliced(id + "/glow", new Rect(r.x - 4, r.y - 4, r.width + 8, r.height + 8), kind == Skin.Card.Selected ? "v2-card-selected" : "v2-card-alert", parent);
            var card = Sliced(id, r, headerTitle != null ? "v2-slab-titled" : kind == Skin.Card.Soft ? "v2-card" : "v2-card-ink", parent, null, true);
            if (headerTitle != null) Text(id + "/title", new Rect(Skin.CardPad, 4, r.width - Skin.CardPad * 2, Skin.HeaderBand), headerTitle.ToUpperInvariant(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleCenter, card);
            if (kind == Skin.Card.Selected) Icon(id + "/tick", new Rect(r.width - 30, -10, 40, 40), "v2-badge-tick", card);
            return card;
        }

        public void LockChip(string id, Rect r, string reason, Transform parent = null)
        {
            var chip = Sliced(id, r, "v2-pill-lock", parent);
            Icon(id + "/icon", new Rect(10, (r.height - 20) / 2, 20, 20), "v2-icon-lock", chip, Skin.InkSoft, "icon-lock");
            Text(id + "/text", new Rect(34, 0, r.width - 42, r.height), reason, Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleLeft, chip);
        }

        public void Inset(string id, Rect r, Transform parent = null) => Sliced(id, r, "v2-inset", parent);

        // ---- buttons ---------------------------------------------------------------------------

        void ButtonFace(string id, Rect r, Element e, string label, string icon, bool primary, bool enabled)
        {
            float h = r.height - (primary || enabled ? 6 : 0);
            Color ink = !enabled ? Skin.InkSoft : primary ? Skin.Cream : Skin.Ink;
            float iconSize = Mathf.Min(44, h - 16);
            // Fat primaries (64+) carry the Number face like the concept's Head home / Buy.
            var face = primary && r.height >= 60 ? Skin.Type.Number : Skin.Type.Heading;
            Text(id + "/label", new Rect(Skin.ButtonPad, 0, r.width - Skin.ButtonPad * 2, h), label, face, ink, TextAnchor.MiddleCenter, e.Rect, primary && enabled);
            if (icon == null) return;
            // Centre the icon + label pair; label width comes from the live text.
            float labelWidth = TextWidth(id + "/label"), group = labelWidth + iconSize + 8, x = (r.width - group) / 2;
            Icon(id + "/icon", new Rect(Mathf.Max(Skin.ButtonPad, x), (h - iconSize) / 2, iconSize, iconSize), icon, e.Rect, enabled ? null : new Color(1, 1, 1, .5f));
            Text(id + "/label", new Rect(Mathf.Max(Skin.ButtonPad, x) + iconSize + 8, 0, r.width - Mathf.Max(Skin.ButtonPad, x) - iconSize - 8 - Skin.ButtonPad, h),
                label, face, ink, TextAnchor.MiddleLeft, e.Rect, primary && enabled);
        }

        // The one fat orange action per screen.
        public RectTransform Primary(string id, Rect r, string label, Action action, string icon = null, bool enabled = true, Transform parent = null)
        {
            var e = Pressable(id, r, parent, "v2-btn-primary", "v2-btn-primary-pressed", action, enabled);
            ButtonFace(id, r, e, label, icon, true, enabled);
            return e.Rect;
        }

        public RectTransform Secondary(string id, Rect r, string label, Action action, string icon = null, bool enabled = true, Transform parent = null)
        {
            var e = Pressable(id, r, parent, "v2-btn-secondary", "v2-btn-secondary-pressed", action, enabled);
            ButtonFace(id, r, e, label, icon, false, enabled);
            return e.Rect;
        }

        // Card-shaped secondary (radius 14): Details ›, back, cycle.
        public RectTransform CardButton(string id, Rect r, string label, Action action, string icon = null, bool enabled = true, Transform parent = null)
        {
            var e = Pressable(id, r, parent, "v2-btn-card", "v2-btn-card-pressed", action, enabled);
            if (label == null) { Icon(id + "/icon", new Rect((r.width - 28) / 2, (r.height - 4 - 28) / 2, 28, 28), icon, e.Rect, enabled ? null : new Color(1, 1, 1, .5f)); return e.Rect; }
            ButtonFace(id, new Rect(r.x, r.y, r.width, r.height - 2), e, label, icon, false, enabled);
            return e.Rect;
        }

        // Icon tile with its label inside, as in the voyage HUD concept (Crew, Ops).
        public void IconButton(string id, Rect r, string icon, string label, Action action, Transform parent = null, string fallback = null)
        {
            var e = Pressable(id, r, parent, "v2-btn-card", "v2-btn-card-pressed", action, true);
            float iconSize = label != null ? Mathf.Min(40, r.height - 34) : 32;
            Icon(id + "/icon", new Rect((r.width - iconSize) / 2, label != null ? 8 : (r.height - 4 - iconSize) / 2, iconSize, iconSize), icon, e.Rect, null, fallback);
            if (label != null) Text(id + "/label", new Rect(4, r.height - 30, r.width - 8, 22), label, Skin.Type.Small, Skin.Ink, TextAnchor.MiddleCenter, e.Rect);
        }

        // ---- navigation ------------------------------------------------------------------------

        public void TabBar(string id, Rect r, string[] labels, string[] icons, int active, Action<int> select, string[] ids = null)
        {
            float gap = 12, w = (r.width - gap * (labels.Length - 1)) / labels.Length;
            for (int i = 0; i < labels.Length; i++)
            {
                int index = i; bool on = i == active;
                var tr = new Rect(r.x + i * (w + gap), r.y - (on ? 4 : 0), w, r.height);
                var e = Pressable($"{id}/{i}", tr, null, on ? "v2-tab-on" : "v2-tab-off", null, () => select(index), true);
                if (ids != null) Alias(ids[i], $"{id}/{i}");
                float iconSize = Phone ? 32 : 40;
                bool beside = tr.width > tr.height * 2.2f;
                if (beside)
                {
                    Icon($"{id}/{i}/icon", new Rect(16, (tr.height - 4 - iconSize) / 2, iconSize, iconSize), icons[i], e.Rect);
                    Text($"{id}/{i}/label", new Rect(24 + iconSize, 0, tr.width - 36 - iconSize, tr.height - 4), labels[i], Skin.Type.Heading, on ? Skin.Cream : Skin.Ink, TextAnchor.MiddleLeft, e.Rect);
                }
                else
                {
                    Icon($"{id}/{i}/icon", new Rect((tr.width - iconSize) / 2, 6, iconSize, iconSize), icons[i], e.Rect);
                    Text($"{id}/{i}/label", new Rect(6, iconSize + 6, tr.width - 12, tr.height - iconSize - 14), labels[i], Skin.Type.Heading, on ? Skin.Cream : Skin.Ink, TextAnchor.MiddleCenter, e.Rect);
                }
            }
        }

        public void PageSwitch(string id, Rect r, string[] labels, int active, Action<int> select, string[] ids = null, Transform parent = null, bool[] enabled = null)
        {
            var capsule = Sliced(id, r, "v2-switch", parent, null, true);
            float w = (r.width - 8) / labels.Length;
            for (int i = 0; i < labels.Length; i++)
            {
                int index = i; bool on = i == active;
                string pid = ids != null ? ids[i] : $"{id}/{i}";
                bool live = enabled == null || enabled[i];
                var e = Pressable(pid, new Rect(4 + i * w, 4, w, r.height - 8), capsule, on ? "v2-switch-on" : null, null, () => select(index), live);
                if (!on) e.Image.color = Color.clear;
                Text($"{pid}/label", new Rect(8, 0, w - 16, r.height - 8), labels[i], Skin.Type.Heading, on ? Skin.Cream : live ? Skin.Ink : Skin.InkSoft, TextAnchor.MiddleCenter, e.Rect);
            }
        }

        // Page header slab: back, display title, context line, optional right-hand content.
        public RectTransform PageHeader(string id, Rect r, string title, string context, Action back, string contextIcon = null, string backId = null, float rightReserve = 0)
        {
            var slab = Slab(id, r);
            float h = r.height, pad = 12;
            if (back != null) CardButton(backId ?? id + "/back", new Rect(pad, (h - 56) / 2, 64, 56), null, back, "v2-icon-back", true, slab);
            float x = back != null ? pad + 64 + 16 : Skin.SlabPad;
            Text(id + "/title", new Rect(x, 2, Phone ? 200 : 300, h - 4), title.ToUpperInvariant(), Skin.Type.Display, Skin.Ink, TextAnchor.MiddleLeft, slab);
            float tw = TextWidth(id + "/title");
            if (context != null)
            {
                float cx = x + tw + 16;
                if (contextIcon != null) { Icon(id + "/context/icon", new Rect(cx, (h - 32) / 2, 32, 32), contextIcon, slab); cx += 40; }
                else Sliced(id + "/rule", new Rect(cx, h * .3f, 2, h * .4f), "v2-rule", slab);
                float ch = context.Contains('\n') ? Mathf.Min(h - 12, 60) : 30;
                Text(id + "/context", new Rect(cx + (contextIcon != null ? 0 : 14), (h - ch) / 2, Mathf.Max(80, r.width - cx - 24 - rightReserve), ch), context, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, slab);
            }
            return slab;
        }

        // Full page backdrop: painted planks with a rope border.
        public void Planks(string id, bool rope = true)
        {
            var e = Get(id, new Rect(-200, -200, Width + 400, Height + 400));
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<Image>();
            var s = V2("v2-plank-tile");
            e.Image.sprite = s; e.Image.type = s != null ? Image.Type.Tiled : Image.Type.Simple; e.Image.pixelsPerUnitMultiplier = 4;
            e.Image.color = s != null ? Color.white : Skin.Plank; e.Image.raycastTarget = true;
            if (!rope) return;
            var top = Get(id + "/rope-top", new Rect(0, 0, Width, 16)); var bottom = Get(id + "/rope-bottom", new Rect(0, Height - 16, Width, 16));
            foreach (var edge in new[] { top, bottom })
            {
                if (edge.Image == null) edge.Image = edge.Rect.gameObject.AddComponent<Image>();
                var rs = V2("v2-rope-h"); edge.Image.sprite = rs; edge.Image.type = Image.Type.Tiled; edge.Image.pixelsPerUnitMultiplier = 4;
                edge.Image.color = rs != null ? Color.white : Color.clear; edge.Image.raycastTarget = false;
            }
        }

        // ---- status ----------------------------------------------------------------------------

        public void Light(string id, Rect r, Skin.Status status, Transform parent = null)
        {
            var pill = Sliced(id, r, Skin.PillSprite(status), parent);
            Icon(id + "/dot", new Rect(12, (r.height - 16) / 2, 16, 16), Skin.LightSprite(status), pill);
            float x = 36;
            if (r.width >= 200 && V2(Skin.StatusIcon(status)) != null) { Icon(id + "/icon", new Rect(x, (r.height - 22) / 2, 22, 22), Skin.StatusIcon(status), pill); x += 28; }
            else Icon(id + "/icon", Rect.zero, null, pill);
            Text(id + "/word", new Rect(x, 0, r.width - x - 10, r.height), Skin.Word(status), Skin.Type.Heading, Skin.ToneInk(status), TextAnchor.MiddleLeft, pill);
        }

        public void ProgressBar(string id, Rect r, float value, Skin.Bar tone = Skin.Bar.Good, Transform parent = null)
        {
            Sliced(id, r, "v2-bar-track", parent);
            value = Mathf.Clamp01(value);
            // The fill keeps its full width and is clipped, so its round caps never squash.
            // A started bar always shows at least a round dot of fill.
            var clip = Get(id + "/clip", new Rect(r.x, r.y, value > .001f ? Mathf.Max(r.height, r.width * value) : 0, r.height), parent);
            if (clip.Rect.GetComponent<RectMask2D>() == null) clip.Rect.gameObject.AddComponent<RectMask2D>();
            clip.Rect.gameObject.SetActive(value > .001f);
            Sliced(id + "/fill", new Rect(0, 0, Mathf.Max(r.width, r.height), r.height), "v2-bar-" + tone.ToString().ToLowerInvariant(), clip.Rect);
        }

        public void StatTile(string id, Rect r, string icon, string label, string value, float? bar = null, Skin.Bar tone = Skin.Bar.Good, Transform parent = null, string fallback = null)
        {
            var card = Card(id, r, Skin.Card.Soft, parent);
            float iconSize = Mathf.Min(Phone ? 40 : 56, r.height - 16);
            Icon(id + "/icon", new Rect(10, (r.height - iconSize) / 2, iconSize, iconSize), icon, card, null, fallback);
            float x = iconSize + 22, w = r.width - x - 12;
            bool hasBar = bar.HasValue && r.height >= 60;
            float textH = hasBar ? r.height - 24 : r.height;
            // Short readings get the Number face; sentences drop to Heading/Body so they never overflow.
            var face = value.Length <= 7 ? Skin.Type.Number : value.Length <= 16 ? Skin.Type.Heading : Skin.Type.Body;
            if (label != null && hasBar)
            {
                // Label and reading share the top row; the bar sits underneath.
                Text(id + "/label", new Rect(x, 2, w * .4f, textH - 2), label, Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, card);
                Text(id + "/value", new Rect(x + w * .3f, 0, w * .7f, textH), value, value.Length <= 12 ? Skin.Type.Heading : Skin.Type.Body, Skin.Ink, TextAnchor.MiddleRight, card);
            }
            else if (label != null)
            {
                Text(id + "/label", new Rect(x, 4, w, textH * .36f), label, Skin.Type.Small, Skin.Ink, TextAnchor.LowerLeft, card);
                Text(id + "/value", new Rect(x, textH * .36f + 2, w, textH * .64f - 6), value, face, Skin.Ink, TextAnchor.MiddleLeft, card);
            }
            else Text(id + "/value", new Rect(x, 0, w, textH), value, face == Skin.Type.Number ? Skin.Type.Heading : face, Skin.Ink, TextAnchor.MiddleLeft, card);
            if (hasBar) ProgressBar(id + "/bar", new Rect(x, r.height - 26, w, 14), bar.Value, tone, card);
        }

        public void PricePill(string id, Rect r, int price, bool affordable = true, Transform parent = null)
        {
            var pill = Sliced(id, r, "v2-pill-cream", parent);
            float coin = Mathf.Min(36, r.height - 10);
            Text(id + "/value", new Rect(0, 0, r.width, r.height - 2), price.ToString("N0"), Skin.Type.Number, affordable ? Skin.Ink : Skin.Bad, TextAnchor.MiddleCenter, pill);
            float tw = TextWidth(id + "/value"), x = (r.width - tw - coin - 10) / 2;
            Icon(id + "/coin", new Rect(x, (r.height - coin) / 2 - 1, coin, coin), "v2-icon-coin", pill, null, "icon-coin");
            Text(id + "/value", new Rect(x + coin + 10, 0, r.width - x - coin - 14, r.height - 2), price.ToString("N0"), Skin.Type.Number, affordable ? Skin.Ink : Skin.Bad, TextAnchor.MiddleLeft, pill);
        }

        // ---- people ----------------------------------------------------------------------------

        // Cards without generated art yet (new hires) show their role portrait, never an empty ring.
        public static string PortraitFallback(string key)
        {
            key = key.ToLowerInvariant();
            return key == "captain" || key == "engineer" ? "portrait-captain" : key.EndsWith("-deck") ? "portrait-deckhand" : "portrait-fisherman";
        }

        public void Portrait(string id, Rect r, string key, Transform parent = null)
        {
            var frame = Sliced(id, r, "v2-portrait-frame", parent);
            var mask = frame.GetComponent<Mask>() ?? frame.gameObject.AddComponent<Mask>();
            mask.showMaskGraphic = true;
            Icon(id + "/art", new Rect(r.width * .02f, r.height * .04f, r.width * .96f, r.height * .96f), "v2-portrait-" + key.ToLowerInvariant(), frame, null, PortraitFallback(key));
            Icon(id + "/ring", r, "v2-portrait-ring", parent);
        }

        // One crew rail row. Status is a word; the bar shows only during a timed job.
        public void CrewCard(string id, Rect r, string portrait, string title, string name, string status, string specialityIcon,
            float? progress, bool selected, Action action, Transform parent = null)
        {
            if (selected) Sliced(id + "/glow", new Rect(r.x - 3, r.y - 3, r.width + 6, r.height + 6), "v2-card-selected", parent);
            var e = Pressable(id, r, parent, "v2-card", null, action, true);
            if (selected) e.Image.color = Palette.Hex("EEF4FF");
            float p = Mathf.Min(56, r.height - 12);
            Portrait(id + "/portrait", new Rect(8, (r.height - p) / 2, p, p), portrait, e.Rect);
            if (r.width < 120) return; // phone rail: portraits only
            float x = p + 16, right = specialityIcon != null ? 44 : 10, w = r.width - x - right;
            bool bar = progress.HasValue;
            float lineH = bar ? (r.height - 22) / 2 : r.height / 2;
            Text(id + "/title", new Rect(x, 4, w, lineH), title, Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, e.Rect);
            Text(id + "/status", new Rect(x, 4 + lineH, w, lineH - 2), status, Skin.Type.Small, Skin.Ink, TextAnchor.UpperLeft, e.Rect);
            if (name != null) Text(id + "/name", new Rect(r.width - 90, 6, 82, 20), name, Skin.Type.Caption, Skin.InkSoft, TextAnchor.UpperRight, e.Rect);
            if (specialityIcon != null) Icon(id + "/speciality", new Rect(r.width - 40, name != null ? 26 : (r.height - 30) / 2, 30, 30), specialityIcon, e.Rect);
            if (bar) ProgressBar(id + "/bar", new Rect(x, r.height - 20, r.width - x - 14, 12), progress.Value, Skin.Bar.Good, e.Rect);
        }

        public RectTransform CrewRail(string id, Rect r, int count, int capacity, Action menu, string menuId = null)
        {
            menuId ??= id + "/menu";
            var slab = Slab(id, r, null);
            Sliced(id + "/band", new Rect(3, 3, r.width - 6, Skin.HeaderBand + 6), "v2-slab-header", slab);
            Icon(id + "/icon", new Rect(14, 10, 34, 34), "v2-icon-crew", slab, Skin.Cream, "icon-crew");
            Text(id + "/title", new Rect(56, 5, r.width - 120, Skin.HeaderBand), $"CREW {count}/{capacity}", Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, slab);
            if (menu != null)
            {
                var e = Pressable(menuId, new Rect(r.width - 52, 7, 40, 40), slab, null, null, menu, true);
                e.Image.color = Color.clear;
                for (int i = 0; i < 3; i++) Sliced($"{menuId}/{i}", new Rect(8, 10 + i * 8, 24, 4), "v2-rule", e.Rect, Skin.Cream);
            }
            return slab;
        }

        // ---- operations ------------------------------------------------------------------------

        public void StageCard(string id, Rect r, string title, string icon, string illustration, string number, string unit,
            Skin.Status status, int queue, Action details, string lockReason = null, string detailsId = null)
        {
            var card = Card(id, r, status == Skin.Status.BackedUp ? Skin.Card.Alert : Skin.Card.Ink, null, "");
            Icon(id + "/head-icon", new Rect(12, 9, 30, 30), icon, card, Skin.Cream);
            Text(id + "/title", new Rect(48, 4, r.width - 56, Skin.HeaderBand), title.ToUpperInvariant(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, card);
            float y = Skin.HeaderBand + 12, art = Phone ? 64 : Mathf.Min(96, r.height * .26f);
            Icon(id + "/art", new Rect((r.width - art * 1.5f) / 2, y, art * 1.5f, art), illustration, card);
            y += art + 6;
            Text(id + "/number", new Rect(12, y, r.width / 2 - 8, 44), number, Skin.Type.Number, Skin.Ink, TextAnchor.MiddleRight, card, false);
            elements[id + "/number"].Text.fontSize = Mathf.RoundToInt(44 * TypeScale);
            elements[id + "/number"].Text.resizeTextMaxSize = Mathf.RoundToInt(44 * TypeScale);
            Text(id + "/unit", new Rect(r.width / 2 + 6, y + 10, r.width / 2 - 18, 30), unit, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, card);
            y += 50;
            if (lockReason != null) { Sliced(id + "/light", Rect.zero, null, card); LockChip(id + "/lock", new Rect(12, y + 4, r.width - 24, 32), lockReason, card); }
            else { Sliced(id + "/lock", Rect.zero, null, card); Light(id + "/light", new Rect(16, y, r.width - 32, 40), status, card); }
            y += 50;
            float queueH = r.height - y - (Phone ? 58 : 66);
            if (queueH < 30) { queue = 0; queueH = 0; }
            Inset(id + "/queue", new Rect(12, y, r.width - 24, queueH), card);
            int shown = Mathf.Min(queue, 8);
            if (shown == 0) Text(id + "/queue/none", new Rect(12, y, r.width - 24, queueH), queueH > 0 ? "No queue" : "", Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleCenter, card);
            else
            {
                int cols = Mathf.Min(shown, 4), rows = (shown + 3) / 4;
                float fw = Mathf.Min(48, (r.width - 40) / cols), fh = Mathf.Min(26, (queueH - 8) / rows);
                for (int i = 0; i < 8; i++)
                {
                    bool on = i < shown && !(queue > 8 && i == 7);
                    var fr = new Rect(r.width / 2 - cols * fw / 2 + (i % 4) * fw, y + queueH / 2 - rows * fh / 2 + (i / 4) * fh, fw - 4, fh - 2);
                    if (on) Icon($"{id}/queue/{i}", fr, "v2-icon-fish", card, null, "icon-fish");
                    else if (i < shown) Text($"{id}/queue/more", fr, "+" + (queue - 7), Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, card);
                }
            }
            if (details != null) CardButton(detailsId ?? id + "/details", new Rect(12, r.height - (Phone ? 50 : 58), r.width - 24, Phone ? 42 : 48), "Details ›", details, null, true, card);
        }

        // ---- speech, toast, modal --------------------------------------------------------------

        readonly List<Rect> bubbles = new();
        public float BubbleTop = 12; // bubbles stay inside the open water between HUD clusters
        public float BubbleLeft = 12, BubbleRight, BubbleBottom; // BubbleBottom: top of a bottom bar, 0 for none
        public Rect Bubble(string id, Vector2 anchor, string icon, string text, bool hot, Action action, string fallback = null)
        {
            float w = Mathf.Max(96, 56 + text.Length * 11), h = 52;
            float right = BubbleRight > BubbleLeft ? BubbleRight : Width - 12;
            float bottom = BubbleBottom > 0 ? BubbleBottom - h - 22 : Height - h - 30; // room for the tail
            Rect At(float x, float y) => new Rect(Mathf.Clamp(x, BubbleLeft, right - w), Mathf.Clamp(y, BubbleTop, bottom), w, h);
            bool Free(Rect c) => !bubbles.Exists(b => b.Overlaps(new Rect(c.x - 4, c.y - 4, c.width + 8, c.height + 8)));
            var r = At(anchor.x - w / 2, anchor.y - h - 14);
            // Bubbles never stack: take the free spot nearest the anchor (above first, then sideways, then below).
            if (!Free(r))
            {
                float best = float.MaxValue; var home = r;
                // Wide enough that a crowded deck pinned against the top edge (tier-5 boats on a phone) still finds room.
                for (int j = -3; j <= 5; j++)
                    for (int k = -8; k <= 8; k++)
                    {
                        var c = At(home.x + k * (w * .5f + 6), home.y + j * (h + 8));
                        float cost = (c.x - home.x) * (c.x - home.x) + (c.y - home.y) * (c.y - home.y) * (c.y > home.y ? 2.5f : 1.2f);
                        if (cost < best && Free(c)) { best = cost; r = c; }
                    }
            }
            bubbles.Add(r);
            bool attached = anchor.y > r.yMax - 4 && anchor.y < r.yMax + 40;
            Icon(id + "/tail", attached ? new Rect(Mathf.Clamp(anchor.x, r.x + 18, r.xMax - 18) - 13, r.yMax - 5, 26, 16) : Rect.zero, hot ? "v2-bubble-hot-tail" : "v2-bubble-tail");
            var e = Pressable(id, r, null, hot ? "v2-bubble-hot" : "v2-bubble", null, action, true);
            Icon(id + "/icon", new Rect(12, 9, 30, 30), icon, e.Rect, null, fallback);
            Text(id + "/text", new Rect(48, 0, w - 56, h - 4), text, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, e.Rect);
            return r;
        }

        // Toasts centre in [left, right] (whole width by default) so they never cover the side clusters.
        public void Toast(string id, string text, string icon = null, float y = 18, float left = 0, float right = 0)
        {
            if (right <= left) { left = 24; right = Width - 24; }
            float w = Mathf.Min(right - left, 140 + text.Length * 10), h = ToastHeight(text, right - left);
            var r = new Rect(left + (right - left - w) / 2, y, w, h);
            var pill = Sliced(id, r, "v2-pill-navy");
            float x = 24;
            if (icon != null) { Icon(id + "/icon", new Rect(x, (h - 36) / 2, 30, 30), icon, pill, Skin.Cream); x += 40; }
            Text(id + "/text", new Rect(x, 2, w - x - 24, h - 10), text, Skin.Type.Body, Skin.Cream, TextAnchor.MiddleCenter, pill);
        }
        // Text that does not fit one line wraps to two inside a taller pill.
        public static float ToastHeight(string text, float span) => 140 + text.Length * 10 > span ? 92 : 64;

        // Full-screen dim that swallows taps; dismiss runs when the dim itself is tapped.
        public void Scrim(string id, Action dismiss = null, float alpha = 1)
        {
            var dim = Pressable(id, new Rect(-50, -50, Width + 100, Height + 100), null, "v2-dim", null, dismiss, true);
            dim.Button.transition = Selectable.Transition.None; dim.Image.type = Image.Type.Simple;
            dim.Image.color = new Color(1, 1, 1, alpha);
        }

        // Full-bleed picture that covers the screen (crop, never letterbox) and blocks taps to the world.
        public void Backdrop(string id, string art, float drift = 0)
        {
            var texture = ArtLibrary.Get()?.UiTex(art);
            float aspect = texture != null ? (float)texture.width / texture.height : 16f / 9;
            float w = Mathf.Max(Width + 40, (Height + 24) * aspect), h = w / aspect;
            var e = Get(id, new Rect((Width - w) / 2 + drift, (Height - h) / 2, w, h));
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<Image>();
            e.Image.sprite = Sprite(art, false); e.Image.type = Image.Type.Simple;
            e.Image.preserveAspect = false; e.Image.color = Color.white; e.Image.raycastTarget = true;
        }

        // Dimmed page with one centred slab; tapping the dim cancels only reversible choices.
        public RectTransform Modal(string id, string title, string body, string primaryLabel, Action primary, string secondaryLabel, Action secondary,
            Action dismiss = null, string primaryIcon = null, float width = 560, float height = 300)
        {
            Scrim(id + "/dim", dismiss);
            width = Mathf.Min(width, Width - 32); height = Mathf.Min(height, Height - 32);
            var r = new Rect((Width - width) / 2, (Height - height) / 2, width, height);
            var slab = Slab(id, r, title, true);
            Text(id + "/body", new Rect(Skin.SlabPad + 8, Skin.HeaderBand + 18, width - Skin.SlabPad * 2 - 16, height - Skin.HeaderBand - 110), body, Skin.Type.Body, Skin.Ink, TextAnchor.MiddleCenter, slab);
            float bh = Phone ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight, by = height - bh - 18;
            if (secondaryLabel != null)
            {
                Secondary(id + "/secondary", new Rect(Skin.SlabPad, by, width * .4f - Skin.SlabPad, bh), secondaryLabel, secondary, null, true, slab);
                Primary(id + "/primary", new Rect(width * .4f + 8, by, width * .6f - Skin.SlabPad - 8, bh), primaryLabel, primary, primaryIcon, true, slab);
            }
            else Primary(id + "/primary", new Rect(width * .2f, by, width * .6f, bh), primaryLabel, primary, primaryIcon, true, slab);
            return slab;
        }

        // ---- inputs ----------------------------------------------------------------------------

        public void ClassChip(string id, Rect r, Skin.FishClass c, string label, bool on, Action toggle, Transform parent = null)
        {
            string key = c.ToString().ToLowerInvariant();
            var e = Pressable(id, r, parent, "v2-chip-" + key + (on ? "-on" : ""), null, toggle, true);
            float s = r.height - 12;
            Icon(id + "/fish", new Rect(10, 6, s * 1.3f, s), "v2-icon-fish-mono", e.Rect, Skin.ClassColour(c), "icon-fish");
            Text(id + "/label", new Rect(16 + s * 1.3f, 0, r.width - s * 1.3f - (on ? 44 : 24), r.height), label, Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, e.Rect);
            if (on) Icon(id + "/tick", new Rect(r.width - 28, (r.height - 20) / 2, 20, 20), "v2-badge-tick", e.Rect);
        }

        public static readonly string[] StepperLabels = { "1", "5", "10", "∞" };
        public void OrderStepper(string id, Rect r, string icon, string name, int active, Action<int> select, Action remove, Transform parent = null)
        {
            var card = Card(id, r, Skin.Card.Soft, parent);
            float s = Mathf.Min(40, r.height - 16);
            Icon(id + "/icon", new Rect(12, (r.height - s) / 2, s, s), icon, card);
            float segW = Phone ? 44 : 52, trashW = remove != null ? 52 : 0, segX = r.width - trashW - segW * 4 - 12;
            Text(id + "/name", new Rect(s + 22, 0, segX - s - 30, r.height), name, Skin.Type.Body, Skin.Ink, TextAnchor.MiddleLeft, card);
            var capsule = Sliced(id + "/seg", new Rect(segX, (r.height - 44) / 2, segW * 4 + 8, 44), "v2-switch", card);
            for (int i = 0; i < 4; i++)
            {
                int index = i; bool on = i == active;
                var e = Pressable($"{id}/seg/{i}", new Rect(4 + i * segW, 4, segW, 36), capsule, "v2-switch-on", null, () => select(index), true);
                e.Image.color = on ? Skin.Paper : Color.clear;
                if (i == 3) Icon($"{id}/seg/{i}/glyph", new Rect((segW - 26) / 2, 8, 26, 16), "v2-infinity", e.Rect, on ? Skin.Cream : Skin.Ink);
                else Text($"{id}/seg/{i}/label", new Rect(0, 0, segW, 36), StepperLabels[i], Skin.Type.Heading, on ? Skin.Cream : Skin.Ink, TextAnchor.MiddleCenter, e.Rect);
            }
            if (remove != null) CardButton(id + "/trash", new Rect(r.width - 50, (r.height - 44) / 2, 42, 44), null, remove, "v2-icon-trash", true, card);
        }

        // Primary / Secondary duty: tap anywhere on the card to cycle.
        public void DutySlot(string id, Rect r, string header, string icon, string name, Action cycle, string hint = "Tap to cycle", Transform parent = null)
        {
            var slab = Card(id, r, Skin.Card.Ink, parent, "");
            Text(id + "/title", new Rect(Skin.CardPad + 4, 4, r.width - 32, Skin.HeaderBand), header.ToUpperInvariant(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, slab);
            float y = Skin.HeaderBand + 10, h = r.height - y - (hint != null ? 34 : 12);
            var e = Pressable(id + "/body", new Rect(12, y, r.width - 24, h), slab, "v2-card", "v2-btn-card-pressed", cycle, cycle != null);
            float bw = r.width - 24, s = Mathf.Min(64, h - 16), cw = cycle != null ? 64 : 0;
            Icon(id + "/body/icon", new Rect(12, (h - s) / 2, s * 1.2f, s), icon, e.Rect);
            float nw = bw - s * 1.2f - 36 - cw;
            Text(id + "/body/name", new Rect(s * 1.2f + 24, (h - 64) / 2, nw, 64), name, nw < 170 ? Skin.Type.Heading : Skin.Type.Number, Skin.Ink, TextAnchor.MiddleLeft, e.Rect);
            Sliced(id + "/body/cycle", cycle != null ? new Rect(bw - 64, (h - 52) / 2, 52, 52) : Rect.zero, cycle != null ? "v2-btn-card" : null, e.Rect);
            Icon(id + "/body/cycle/icon", cycle != null ? new Rect(bw - 52, (h - 52) / 2 + 10, 28, 28) : Rect.zero, "v2-icon-cycle", e.Rect);
            if (hint != null) Text(id + "/hint", new Rect(12, r.height - 32, r.width - 24, 24), hint, Skin.Type.Small, Skin.Teal, TextAnchor.MiddleCenter, slab);
        }
    }
}

using UnityEngine;

namespace Catchline.Game
{
    // IMGUI styles in the Catchline palette: cream cards, navy text, orange buttons.
    // Placeholder until the real UI kit; rounded corners come from generated 9-slice textures.
    public static class Ui
    {
        public static readonly Color Ink = Palette.HullNavy;
        public static readonly Color Muted = new(0.09f, 0.25f, 0.34f, 0.65f);

        public static GUIStyle Panel, Card, CardOn, Title, H2, Body, Small, Mutedish, Center, Btn, BtnAlt, BtnOff, Tab, TabOn,
            Action, ActionHot, ActionOff, Chip, ToastStyle, BarBg, BarFill, BarWarn, BarGood,
            WhiteCenter, WhiteSmall, WhiteCenterSmall, Bubble, BubbleHot, DotWhite, DotRed, DotGold, Ring, FishShape, Water, MiniTitle, MiniHot;

        static bool ready;

        public static void Init()
        {
            if (ready && Panel.normal.background != null) return;
            ready = true;
            Panel = Box(Round(Palette.Cream, 16, new Color(0.09f, 0.25f, 0.34f, 0.25f)), 16, 16);
            Card = Box(Round(Color.white, 12, new Color(0.09f, 0.25f, 0.34f, 0.15f)), 12, 12);
            CardOn = Box(Round(Color.white, 12, Palette.Accent, 3), 12, 12);
            Title = Text(28, Ink, FontStyle.Bold);
            H2 = Text(19, Ink, FontStyle.Bold);
            Body = Text(15, Ink);
            Small = Text(13, Ink);
            Mutedish = Text(13, Muted);
            Center = Text(15, Ink, FontStyle.Normal, TextAnchor.MiddleCenter);
            Btn = Button(Palette.Accent, Color.white, 16);
            BtnAlt = Button(Palette.Sea, Color.white, 16);
            BtnOff = Button(new Color(0.78f, 0.77f, 0.74f), new Color(1f, 1f, 1f, 0.85f), 16);
            Tab = Button(new Color(0.88f, 0.84f, 0.76f), Ink, 15);
            TabOn = Button(Palette.HullNavy, Color.white, 15);
            Action = Button(Palette.Accent, Color.white, 26);
            ActionHot = Button(Palette.Oilskin, Palette.HullNavy, 30);
            ActionOff = Button(new Color(0.55f, 0.6f, 0.62f, 0.9f), Color.white, 20);
            Chip = Box(Round(new Color(0.09f, 0.25f, 0.34f, 0.88f), 12), 12, 12);
            Chip.normal.textColor = Color.white;
            Chip.fontSize = 15;
            Chip.wordWrap = true;
            ToastStyle = Box(Round(new Color(0.09f, 0.25f, 0.34f, 0.94f), 14), 16, 14);
            ToastStyle.normal.textColor = Color.white;
            ToastStyle.fontSize = 17;
            ToastStyle.alignment = TextAnchor.MiddleCenter;
            ToastStyle.wordWrap = true;
            BarBg = Box(Round(new Color(0.09f, 0.25f, 0.34f, 0.15f), 6), 0, 6);
            BarFill = Box(Round(Palette.Sea, 6), 0, 6);
            BarWarn = Box(Round(Palette.Bad, 6), 0, 6);
            BarGood = Box(Round(Palette.Good, 6), 0, 6);

            WhiteCenter = Text(20, Color.white, FontStyle.Normal, TextAnchor.MiddleCenter);
            WhiteSmall = Text(13, Color.white);
            WhiteCenterSmall = Text(14, new Color(1f, 1f, 1f, 0.9f), FontStyle.Normal, TextAnchor.MiddleCenter);
            MiniTitle = Text(22, Color.white, FontStyle.Bold, TextAnchor.MiddleCenter);
            MiniHot = Text(30, Palette.Oilskin, FontStyle.Bold, TextAnchor.MiddleCenter);
            Bubble = Button(Color.white, Ink, 18);
            Bubble.normal.background = Round(Color.white, 14, Palette.Accent, 3);
            BubbleHot = Button(Palette.Oilskin, Ink, 24);
            DotWhite = Box(Round(Color.white, 13), 0, 13);
            DotRed = Box(Round(Palette.Bad, 13), 0, 13);
            DotGold = Box(Round(Palette.Oilskin, 13), 0, 13);
            Ring = Box(Round(new Color(1f, 1f, 1f, 0.35f), 20), 0, 20);
            FishShape = Box(Round(new Color(0.04f, 0.2f, 0.25f, 0.85f), 10), 0, 10);
            Water = Box(Round(new Color(0.08f, 0.5f, 0.58f, 0.93f), 18, new Color(1f, 1f, 1f, 0.5f), 3), 0, 18);

            ApplyKit();
        }

        // ---- Codex's UI kit (Assets/Art/UI), imported at 1x. Borders are the slices.json values halved. ----

        public static Font KitFont;
        static ArtLibrary lib;

        public static Texture2D Tex(string name) => lib != null ? lib.UiTex(name) : null;

        static void ApplyKit()
        {
            lib = ArtLibrary.Get();
            if (lib == null) return;
            KitFont = lib.UiFont;
            if (KitFont != null)
                foreach (var s in new[] { Title, H2, Body, Small, Mutedish, Center, Btn, BtnAlt, BtnOff, Tab, TabOn, Chip, ToastStyle, WhiteCenter, WhiteSmall, WhiteCenterSmall, Bubble, BubbleHot, MiniTitle, MiniHot })
                {
                    s.font = KitFont;
                    if (s.fontStyle == FontStyle.Bold) s.fontStyle = FontStyle.Normal; // Fredoka Medium is already heavy
                }

            Skin(Panel, "panel-cream", 28, 28, 28, 32);
            Skin(Card, "card-white", 28, 28, 28, 32);
            Skin(CardOn, "card-selected", 28, 28, 28, 32);
            Skin(Chip, "chip-dark", 28, 28, 28, 32);
            Skin(ToastStyle, "toast-dark", 28, 28, 28, 32);
            Button(Btn, "button-primary");
            Button(BtnAlt, "button-secondary");
            Button(BtnOff, "button-disabled");
            Button(Tab, "button-tab-off");
            Button(TabOn, "button-tab-on");
            Skin(Bubble, "bubble-white", 24, 24, 20, 20);
            Skin(BubbleHot, "bubble-hot", 24, 24, 20, 20);
            Skin(BarBg, "bar-background", 12, 12, 9, 9);
            Skin(BarFill, "bar-teal", 12, 12, 9, 9);
            Skin(BarGood, "bar-green", 12, 12, 9, 9);
            Skin(BarWarn, "bar-red", 12, 12, 9, 9);
            // Kit panels carry a drop shadow at the bottom: keep content clear of it.
            foreach (var s in new[] { Card, CardOn })
                s.padding = new RectOffset(16, 16, 12, 16);
        }

        static void Skin(GUIStyle s, string tex, int left, int right, int top, int bottom)
        {
            var t = Tex(tex);
            if (t == null) return;
            s.normal.background = t;
            s.hover.background = t;
            s.border = new RectOffset(left, right, top, bottom);
        }

        static void Button(GUIStyle s, string prefix)
        {
            var normal = Tex(prefix + "-normal");
            var pressed = Tex(prefix + "-pressed");
            if (normal == null) return;
            s.normal.background = s.hover.background = normal;
            s.active.background = pressed != null ? pressed : normal;
            s.border = new RectOffset(22, 22, 20, 20);
            s.padding = new RectOffset(14, 14, 6, 10);
        }

        // Draws a kit sprite scaled to a rect; returns false when the kit is missing so callers can fall back.
        public static bool Sprite(Rect r, string name, float alpha = 1f)
        {
            var t = Tex(name);
            if (t == null) return false;
            var prev = GUI.color;
            GUI.color = new Color(1f, 1f, 1f, alpha);
            GUI.DrawTexture(r, t, ScaleMode.StretchToFill, true);
            GUI.color = prev;
            return true;
        }

        public static void Bar(Rect r, float t, GUIStyle fill = null)
        {
            if (Tex("bar-background") != null) r.height = Mathf.Max(r.height, 18f);
            GUI.Box(r, GUIContent.none, BarBg);
            t = Mathf.Clamp01(t);
            if (t > 0.01f) GUI.Box(new Rect(r.x, r.y, Mathf.Max(24f, r.width * t), r.height), GUIContent.none, fill ?? BarFill);
        }

        static GUIStyle Box(Texture2D bg, int pad, int radius)
        {
            var s = new GUIStyle
            {
                border = new RectOffset(radius, radius, radius, radius),
                padding = new RectOffset(pad, pad, pad, pad),
            };
            s.normal.background = bg;
            return s;
        }

        static GUIStyle Text(int size, Color c, FontStyle fs = FontStyle.Normal, TextAnchor a = TextAnchor.UpperLeft)
        {
            var s = new GUIStyle { fontSize = size, fontStyle = fs, alignment = a, wordWrap = true, richText = true };
            s.normal.textColor = c;
            return s;
        }

        static GUIStyle Button(Color fill, Color text, int size)
        {
            var s = Box(Round(fill, 12), 10, 12);
            s.hover.background = Round(Color.Lerp(fill, Color.white, 0.12f), 12);
            s.active.background = Round(Color.Lerp(fill, Color.black, 0.12f), 12);
            s.normal.textColor = s.hover.textColor = s.active.textColor = text;
            s.fontSize = size;
            s.fontStyle = FontStyle.Bold;
            s.alignment = TextAnchor.MiddleCenter;
            s.wordWrap = true;
            return s;
        }

        // Anti-aliased rounded rectangle, optionally with a border, for 9-slicing.
        static Texture2D Round(Color fill, int r, Color? border = null, int borderWidth = 2)
        {
            int size = r * 2 + 4;
            var tex = new Texture2D(size, size, TextureFormat.RGBA32, false) { wrapMode = TextureWrapMode.Clamp, hideFlags = HideFlags.HideAndDontSave };
            var px = new Color[size * size];
            for (int y = 0; y < size; y++)
                for (int x = 0; x < size; x++)
                {
                    float cx = Mathf.Clamp(x + 0.5f, r, size - r);
                    float cy = Mathf.Clamp(y + 0.5f, r, size - r);
                    float d = Mathf.Sqrt((x + 0.5f - cx) * (x + 0.5f - cx) + (y + 0.5f - cy) * (y + 0.5f - cy));
                    float alpha = Mathf.Clamp01(r - d + 0.5f);
                    var c = fill;
                    if (border.HasValue && d > r - borderWidth) c = Color.Lerp(fill, border.Value, Mathf.Clamp01(d - (r - borderWidth) + 0.5f) * border.Value.a / Mathf.Max(0.01f, border.Value.a));
                    c.a *= alpha;
                    px[y * size + x] = c;
                }
            tex.SetPixels(px);
            tex.Apply();
            return tex;
        }
    }
}

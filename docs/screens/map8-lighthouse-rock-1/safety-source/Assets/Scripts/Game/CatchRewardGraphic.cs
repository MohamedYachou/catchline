using UnityEngine;
using UnityEngine.UI;

namespace Catchline.Game
{
    // Native Canvas geometry: soft specimen backlight and a quiet navy enamel frame.
    // Reuses the production canvas/capture/input lifecycle; no extra camera or texture.
    public sealed class CatchRewardGraphic : MaskableGraphic
    {
        public bool Halo { get; private set; }
        Color accent;
        float opacity = 1;
        public void Style(Color value, bool halo, float alpha)
        {
            raycastTarget = false;
            if (value == accent && halo == Halo && Mathf.Approximately(alpha, opacity)) return;
            accent = value; Halo = halo; opacity = alpha; SetVerticesDirty();
        }
        Color Alpha(Color c, float amount = 1) { c.a *= opacity * amount; return c; }
        protected override void OnPopulateMesh(VertexHelper vh)
        {
            vh.Clear(); var r = rectTransform.rect;
            if (Halo) { Glow(vh, r); return; }
            var shadow = r; shadow.y -= 5;
            Rounded(vh, shadow, 18, Alpha(new Color(.02f, .09f, .13f, .25f)), Alpha(new Color(.02f, .09f, .13f, .25f)));
            Rounded(vh, r, 18, Alpha(Color.Lerp(Palette.Hex("496574"), accent, .28f)), Alpha(Palette.Hex("355361")));
            r = new Rect(r.x + 1, r.y + 1, r.width - 2, r.height - 2);
            Rounded(vh, r, 17, Alpha(Palette.Hex("193D50")), Alpha(Palette.Hex("102C3D")));
        }
        static void Rounded(VertexHelper vh, Rect r, float radius, Color top, Color bottom)
        {
            radius = Mathf.Min(radius, Mathf.Min(r.width, r.height) * .5f);
            int first = vh.currentVertCount;
            vh.AddVert(r.center, Color.Lerp(bottom, top, .5f), Vector2.zero);
            for (int corner = 0; corner < 4; corner++)
            {
                float cx = corner is 0 or 3 ? r.xMax - radius : r.xMin + radius;
                float cy = corner < 2 ? r.yMax - radius : r.yMin + radius;
                for (int step = 0; step <= 10; step++)
                {
                    float angle = (corner * 90 + step * 9) * Mathf.Deg2Rad;
                    var p = new Vector2(cx + Mathf.Cos(angle) * radius, cy + Mathf.Sin(angle) * radius);
                    vh.AddVert(p, Color.Lerp(bottom, top, Mathf.InverseLerp(r.yMin, r.yMax, p.y)), Vector2.zero);
                }
            }
            const int count = 44;
            for (int i = 0; i < count; i++) vh.AddTriangle(first, first + 1 + i, first + 1 + (i + 1) % count);
        }
        void Glow(VertexHelper vh, Rect r)
        {
            const int segments = 64, rings = 8;
            var center = r.center;
            vh.AddVert(center, Alpha(accent, .30f), Vector2.zero);
            for (int ring = 1; ring <= rings; ring++)
            {
                float t = ring / (float)rings;
                float alpha = Mathf.Pow(1 - t * t, 3) * .30f;
                for (int i = 0; i < segments; i++)
                {
                    float a = i * Mathf.PI * 2 / segments;
                    vh.AddVert(center + new Vector2(Mathf.Cos(a) * r.width * .5f * t,
                        Mathf.Sin(a) * r.height * .5f * t), Alpha(accent, alpha), Vector2.zero);
                    int index = 1 + (ring - 1) * segments + i;
                    int next = 1 + (ring - 1) * segments + (i + 1) % segments;
                    if (ring == 1) vh.AddTriangle(0, index, next);
                    else
                    {
                        vh.AddTriangle(index - segments, index, next);
                        vh.AddTriangle(index - segments, next, next - segments);
                    }
                }
            }
        }
    }
}

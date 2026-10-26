using UnityEngine;
using UnityEngine.UI;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        static T ChartGraphic<T>(RectTransform parent) where T : Graphic
        {
            var graphic = parent.GetComponentInChildren<T>(true);
            if (graphic != null) return graphic;
            var go = new GameObject(typeof(T).Name, typeof(RectTransform), typeof(CanvasRenderer));
            go.layer = 5; go.transform.SetParent(parent, false);
            var rect = (RectTransform)go.transform; rect.anchorMin = Vector2.zero; rect.anchorMax = Vector2.one;
            rect.offsetMin = rect.offsetMax = Vector2.zero;
            return go.AddComponent<T>();
        }
    }
    public abstract class CoastGraphic : MaskableGraphic
    {
        protected VertexHelper mesh;
        protected Vector2 Pixel(Vector2 p) => new(rectTransform.rect.xMin + p.x, rectTransform.rect.yMax - p.y);
        protected void Tri(Vector2 a, Vector2 b, Vector2 c, Color color)
        {
            int i = mesh.currentVertCount;
            mesh.AddVert(Pixel(a), color, Vector2.zero); mesh.AddVert(Pixel(b), color, Vector2.zero); mesh.AddVert(Pixel(c), color, Vector2.zero);
            mesh.AddTriangle(i, i + 1, i + 2);
        }
        protected void Line(Vector2 a, Vector2 b, float width, Color color)
        {
            var n = new Vector2(-(b - a).y, (b - a).x).normalized * width * .5f;
            Tri(a + n, b + n, b - n, color); Tri(a + n, b - n, a - n, color);
        }
        protected void Circle(Vector2 center, float radius, Color color, int sides = 36)
        {
            for (int i = 0; i < sides; i++)
            {
                float a = i * Mathf.PI * 2 / sides, b = (i + 1) * Mathf.PI * 2 / sides;
                Tri(center, center + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * radius,
                    center + new Vector2(Mathf.Cos(b), Mathf.Sin(b)) * radius, color);
            }
        }
    }
    public sealed class IllustratedRoutesGraphic : CoastGraphic
    {
        protected override void OnPopulateMesh(VertexHelper vh)
        {
            vh.Clear(); mesh = vh;
            var size = rectTransform.rect.size;
            var start = Vector2.Scale(VoyageGame.ChartHarbour + new Vector2(0, -.035f), size);
            for (int spot = 0; spot < GameData.Spots.Length; spot++)
            {
                var end = Vector2.Scale(VoyageGame.NauticalChartPoint(spot), size);
                end.y += 27;
                var delta = end - start;
                var c1 = start + new Vector2(delta.x * .25f, delta.y * .43f);
                var c2 = end - new Vector2(delta.x * .43f, delta.y * .22f);
                Vector2 Curve(float u) => Mathf.Pow(1 - u, 3) * start + 3 * Mathf.Pow(1 - u, 2) * u * c1 + 3 * (1 - u) * u * u * c2 + u * u * u * end;
                float length = delta.magnitude; int steps = Mathf.Max(10, Mathf.CeilToInt(length / 13));
                for (int n = 0; n < steps; n++)
                {
                    float a = n / (float)steps, b = (n + .58f) / steps;
                    Line(Curve(a), Curve(b), 2.6f, new Color(1, 1, .96f, .95f));
                }
                var tangent = (end - Curve(.97f)).normalized; var normal = new Vector2(-tangent.y, tangent.x);
                Tri(end, end - tangent * 13 + normal * 5, end - tangent * 13 - normal * 5, Color.white);
            }
        }
    }
    public sealed class ChartPinGraphic : CoastGraphic
    {
        int glyph; bool selected, pin;
        public void Configure(int kind, bool chosen, bool isPin)
        { if (glyph == kind && selected == chosen && pin == isPin) return; glyph = kind; selected = chosen; pin = isPin; SetVerticesDirty(); }
        protected override void OnPopulateMesh(VertexHelper vh)
        {
            vh.Clear(); mesh = vh;
            float w = rectTransform.rect.width, h = rectTransform.rect.height;
            var c = new Vector2(w / 2, pin ? w / 2 : h / 2);
            float r = w * .46f;
            Color ink = FishReferenceStyle.Ink, symbol = pin ? Color.white : ink;
            if (pin)
            {
                Color rim = selected ? Palette.Hex("E8B444") : Palette.Hex("FFF9E9");
                Tri(c + new Vector2(-r * .72f, r * .42f), c + new Vector2(r * .72f, r * .42f), new Vector2(w / 2, h), rim);
                Circle(c, r, rim); Circle(c, r * .78f, ink); r *= .63f;
            }
            Vector2 P(float x, float y) => c + new Vector2(x, y) * r;
            void L(float x, float y, float a, float b, float width = .14f) => Line(P(x, y), P(a, b), r * width, symbol);
            void C(float x, float y, float radius) => Circle(P(x, y), r * radius, symbol);
            switch (glyph)
            {
                case 0: // wave
                    for (int row = 0; row < 2; row++)
                    {
                        var previous = P(-.85f, row * .52f - .2f);
                        for (int i = 1; i <= 16; i++) { float x = -.85f + i * 1.7f / 16; var next = P(x, Mathf.Sin(x * 5) * .19f + row * .52f - .2f); Line(previous, next, r * .13f, symbol); previous = next; }
                    }
                    break;
                case 1: // kelp fronds
                    for (int stem = -1; stem <= 1; stem++)
                    {
                        L(0, .8f, stem * .55f, -.75f);
                        for (int j = 0; j < 3; j++) { float y = .45f - j * .42f, x = stem * (.8f - y) * .34f; L(x, y, x - .28f, y - .3f); L(x, y, x + .28f, y - .3f); }
                    }
                    break;
                case 2: // scallop shell
                    for (int i = 0; i <= 7; i++) { float angle = Mathf.PI + i * Mathf.PI / 7; var edge = P(Mathf.Cos(angle) * .85f, Mathf.Sin(angle) * .85f); Line(P(0, .7f), edge, r * .13f, symbol); Circle(edge, r * .10f, symbol); }
                    L(-.25f, .74f, .25f, .74f, .22f); break;
                case 3: // rock
                    Tri(P(-.85f, .65f), P(-.6f, -.5f), P(.15f, -.8f), symbol);
                    Tri(P(-.85f, .65f), P(.15f, -.8f), P(.75f, .62f), symbol); break;
                case 4: // fish
                    Circle(P(-.05f, 0), r * .58f, symbol);
                    Tri(P(.2f, 0), P(.95f, -.52f), P(.95f, .52f), symbol); Circle(P(-.33f, -.14f), r * .09f, ink); break;
                case 5: // home
                    Tri(P(-.95f, -.05f), P(0, -.85f), P(.95f, -.05f), symbol);
                    L(-.6f, -.05f, -.6f, .8f, .25f); L(.6f, -.05f, .6f, .8f, .25f); L(-.6f, .7f, .6f, .7f, .25f); L(0, .8f, 0, .1f, .28f); break;
                case 6: // boat
                    Tri(P(-.95f, .2f), P(.95f, .2f), P(.55f, .8f), symbol); Tri(P(-.95f, .2f), P(.55f, .8f), P(-.55f, .8f), symbol);
                    L(-.45f, -.55f, -.45f, .15f, .16f); L(-.45f, -.55f, .45f, -.55f, .16f); L(.45f, -.55f, .45f, .15f, .16f); L(0, -.95f, 0, -.55f, .13f); break;
                case 7: // crew
                    C(0, -.48f, .31f); C(-.65f, -.28f, .25f); C(.65f, -.28f, .25f);
                    C(0, .48f, .51f); C(-.65f, .55f, .33f); C(.65f, .55f, .33f); break;
                case 8: // map
                    Circle(P(0, -.3f), r * .58f, symbol); Tri(P(-.46f, 0), P(.46f, 0), P(0, .87f), symbol); Circle(P(0, -.3f), r * .22f, Palette.Hex("AEE5EE")); break;
                case 9: // gear
                    C(0, 0, .65f);
                    for (int i = 0; i < 8; i++) { float a = i * Mathf.PI / 4; var v = new Vector2(Mathf.Cos(a), Mathf.Sin(a)); Line(c + v * r * .55f, c + v * r, r * .3f, symbol); }
                    Circle(c, r * .25f, Palette.Hex("FFF9E9")); break;
                case 10: // seal head above a wave
                    C(-.1f, -.2f, .5f); C(.38f, -.08f, .26f); C(-.24f, -.32f, .07f);
                    for (int i = -1; i <= 1; i += 2) L(.42f, -.02f, .42f + i * .38f, .06f, .06f);
                    L(-.85f, .55f, -.3f, .4f, .16f); L(-.3f, .4f, .25f, .55f, .16f); L(.25f, .55f, .85f, .4f, .16f); break;
                case 11: // steamer wreck: a listing hull and a leaning funnel above a wave
                    Tri(P(-.85f, .05f), P(.7f, .35f), P(.5f, .62f), symbol); Tri(P(-.85f, .05f), P(.5f, .62f), P(-.6f, .38f), symbol);
                    L(-.05f, .15f, .2f, -.6f, .3f); L(-.55f, .1f, -.5f, -.75f, .08f);
                    L(-.9f, .78f, -.3f, .66f, .14f); L(-.3f, .66f, .3f, .8f, .14f); L(.3f, .8f, .9f, .66f, .14f); break;
                case 12: // lighthouse: a tapering tower, its lamp and two beams, on a wave
                    Tri(P(-.32f, .62f), P(.32f, .62f), P(.16f, -.38f), symbol); Tri(P(-.32f, .62f), P(.16f, -.38f), P(-.16f, -.38f), symbol);
                    C(0, -.56f, .17f); L(.24f, -.6f, .85f, -.82f, .08f); L(-.24f, -.6f, -.85f, -.82f, .08f);
                    L(-.9f, .8f, -.3f, .68f, .14f); L(-.3f, .68f, .3f, .82f, .14f); L(.3f, .82f, .9f, .68f, .14f); break;
                case 13: // whale tail: a fluke rising from a wave
                    L(0, .55f, 0, -.1f, .26f);
                    Tri(P(0, -.05f), P(-.9f, -.55f), P(-.2f, -.25f), symbol); Tri(P(0, -.05f), P(.9f, -.55f), P(.2f, -.25f), symbol);
                    Tri(P(-.9f, -.55f), P(-.55f, -.7f), P(-.2f, -.25f), symbol); Tri(P(.9f, -.55f), P(.55f, -.7f), P(.2f, -.25f), symbol);
                    L(-.9f, .8f, -.3f, .68f, .14f); L(-.3f, .68f, .3f, .82f, .14f); L(.3f, .82f, .9f, .68f, .14f); break;
                default: // port office
                    L(-.75f, .85f, -.75f, -.2f, .2f); L(.75f, .85f, .75f, -.2f, .2f); L(-.8f, -.2f, .8f, -.2f, .2f);
                    L(-.3f, -.3f, -.3f, -.75f, .2f); L(.3f, -.3f, .3f, -.75f, .2f); L(-.4f, -.75f, .4f, -.75f, .2f);
                    for (int i = -1; i <= 1; i++) { C(i * .45f, .15f, .1f); C(i * .45f, .55f, .1f); } break;
            }
        }
    }
}

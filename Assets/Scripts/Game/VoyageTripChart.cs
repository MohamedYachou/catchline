using UnityEngine;
using UnityEngine.UI;

namespace Catchline.Game
{
    // The chart leg of the trip (docs/plans/HARBOUR-PLAN.md section 2): the illustrated Gull coast fades in over the
    // 3D world zoomed on the start, a boat token sails the dotted route past two landmarks, and the chart zooms into
    // the end pin as it fades out over the new world. Tap anywhere to speed the trip up.
    public partial class VoyageGame
    {
        static readonly string[][] ChartLandmarks =
        {
            new[] { "Bell buoy", "The narrows" },
            new[] { "Seal rocks", "The kelp edge" },
            new[] { "The old wreck", "Shoal markers" },
            new[] { "Gull stacks", "The breakers" },
            new[] { "Bell buoy", "The dark water" },
            new[] { "Seal colony", "Reef breakers" },
            new[] { "Shoal markers", "Cardinal buoy" },
        };
        static readonly float[] ChartLandmarkAt = { .36f, .7f };
        RectTransform journeySlab;

        // The route curve of IllustratedRoutesGraphic, in chart pixels for a chart drawn size.x by size.y.
        public static Vector2 ChartRoutePoint(int spot, float u, Vector2 size)
        {
            var start = Vector2.Scale(ChartHarbour + new Vector2(0, -.035f), size);
            var end = Vector2.Scale(NauticalChartPoint(spot), size); end.y += 27;
            var delta = end - start;
            var c1 = start + new Vector2(delta.x * .25f, delta.y * .43f);
            var c2 = end - new Vector2(delta.x * .43f, delta.y * .22f);
            float v = 1 - u;
            return v * v * v * start + 3 * v * v * u * c1 + 3 * v * u * u * c2 + u * u * u * end;
        }

        string ChartLandmark(float route, bool home)
        {
            float u = home ? 1 - route : route;
            var names = ChartLandmarks[Mathf.Clamp(ActiveSpot, 0, ChartLandmarks.Length - 1)];
            for (int i = 0; i < names.Length; i++)
                if (Mathf.Abs(u - ChartLandmarkAt[i]) < .12f) return "Passing " + names[i];
            return null;
        }

        void InterfaceTripChart()
        {
            if (ChartAlpha <= .01f) return;
            var full = new Rect(0, 0, iw, ih);
            var host = coastalUi.Box("trip/chart", full, "", Color.clear, null, true);
            var group = host.GetComponent<CanvasGroup>();
            if (group == null) group = host.gameObject.AddComponent<CanvasGroup>();
            group.alpha = ChartAlpha;
            // Zoom about the start pin while fading in and about the end pin while fading out.
            bool leaving = chartAt < ChartFade;
            var harbourPin = Vector2.Scale(ChartHarbour, new Vector2(iw, ih));
            var spotPin = Vector2.Scale(NauticalChartPoint(ActiveSpot), new Vector2(iw, ih));
            var focus = leaving ? (chartHome ? spotPin : harbourPin) : (chartHome ? harbourPin : spotPin);
            var chart = new Rect(focus.x - focus.x * ChartZoom, focus.y - focus.y * ChartZoom, iw * ChartZoom, ih * ChartZoom);
            var art = coastalUi.ResourceArt("trip/chart/art", chart, "Charts/gull-coast", true, host);
            var route = coastalUi.Box("trip/chart/route", new Rect(chart.x, chart.y, chart.width, chart.height), "", Color.clear, host, false);
            var graphic = ChartGraphic<TripRouteGraphic>(route);
            graphic.raycastTarget = false;
            float u = chartHome ? 1 - ChartRoute : ChartRoute;
            graphic.Configure(SpotGlyph(ActiveSpot), u, chartHome);

            var size = new Vector2(chart.width, chart.height);
            var names = ChartLandmarks[Mathf.Clamp(ActiveSpot, 0, ChartLandmarks.Length - 1)];
            for (int i = 0; i < names.Length; i++)
            {
                var p = chart.position + ChartRoutePoint(ActiveSpot, ChartLandmarkAt[i], size);
                bool near = Mathf.Abs(u - ChartLandmarkAt[i]) < .12f;
                float w = compactInterface ? 132 : 160, h = compactInterface ? 34 : 40;
                var card = coastalUi.Card("trip/chart/mark/" + i, new Rect(p.x + 14, p.y - h - 6, w, h), near ? Skin.Card.Selected : Skin.Card.Soft, host);
                card.localScale = Vector3.one * (near ? 1.06f : .92f);
                coastalUi.Text("trip/chart/mark/" + i + "/name", new Rect(10, 0, w - 20, h), names[i], Skin.Type.Small, near ? Skin.Ink : Skin.InkSoft, TextAnchor.MiddleLeft, card);
            }
            var boat = chart.position + ChartRoutePoint(ActiveSpot, u, size);
            var token = coastalUi.Box("trip/chart/boat", new Rect(boat.x - 24, boat.y - 58, 48, 62), "", Color.clear, host, false);
            var pin = ChartGraphic<ChartPinGraphic>(token);
            pin.raycastTarget = false; pin.Configure(6, true, true);
            coastalUi.HitArea("trip/chart/faster", full, () => TripFast = !TripFast, host);
            journeySlab?.SetAsLastSibling();
        }
    }

    // One route on the chart: dotted ahead of the boat, a solid wake behind it.
    public sealed class TripRouteGraphic : CoastGraphic
    {
        int spot; float u; bool home;
        public void Configure(int s, float progress, bool homeward)
        {
            if (spot == s && Mathf.Abs(u - progress) < .001f && home == homeward) return;
            spot = s; u = progress; home = homeward; SetVerticesDirty();
        }
        protected override void OnPopulateMesh(VertexHelper vh)
        {
            vh.Clear(); mesh = vh;
            var size = rectTransform.rect.size;
            float length = (VoyageGame.ChartRoutePoint(spot, 1, size) - VoyageGame.ChartRoutePoint(spot, 0, size)).magnitude;
            int steps = Mathf.Max(16, Mathf.CeilToInt(length / 11));
            var wake = new Color(1, 1, .96f, .95f);
            for (int n = 0; n < steps; n++)
            {
                float a = n / (float)steps, b = (n + 1f) / steps;
                bool travelled = home ? a >= u : b <= u;
                if (travelled) Line(VoyageGame.ChartRoutePoint(spot, a, size), VoyageGame.ChartRoutePoint(spot, b, size), 5f, wake);
                else Line(VoyageGame.ChartRoutePoint(spot, a, size), VoyageGame.ChartRoutePoint(spot, a + .55f / steps, size), 2.6f, new Color(1, 1, .96f, .8f));
            }
            for (int i = 0; i < 2; i++)
                Circle(VoyageGame.ChartRoutePoint(spot, i == 0 ? .36f : .7f, size), 6f, FishReferenceStyle.Ink);
        }
    }
}

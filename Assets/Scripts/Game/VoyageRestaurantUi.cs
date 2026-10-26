using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // The restaurant's own screens (docs/plans/RESTAURANT.md section 10), built to the accepted mockups in
    // Art/Source/Restaurant/concepts/ui-*.png. Each screen draws from a small view model so it can be shown with sample
    // numbers before the restaurant logic is wired in; art not delivered yet falls back to the nearest kit icon.
    public partial class VoyageGame
    {
        public enum RestaurantScreen { None, Plan, Prep, Closing, Service }
        public RestaurantScreen RestaurantPreview;

        public sealed class RestaurantDish { public string Name, Art, Fallback; public int Low, High; }
        public sealed class RestaurantFish { public string Name, Art, Amount; }
        public sealed class RestaurantPrepRow { public string Name, Art, Fallback; public int Portions, ForecastLow, ForecastHigh; }
        public sealed class RestaurantReview { public string Portrait, Quote; public int Stars; }

        public sealed class RestaurantPlanView
        {
            public string Day = "Friday", Hours = "18:00 – 23:00";
            public int GuestsLow = 18, GuestsHigh = 22; public float GroupsPerHour = 4;
            public List<RestaurantDish> Dishes = new()
            {
                new() { Name = "Grilled fish", Art = "v2-dish-grilled-fish", Fallback = "fish-mackerel", Low = 8, High = 10 },
                new() { Name = "Fish soup", Art = "v2-dish-fish-soup", Fallback = "icon-food", Low = 6, High = 8 },
                new() { Name = "Coffee", Art = "v2-dish-coffee", Fallback = "v2-icon-clock", Low = 10, High = 14 },
            };
            public List<RestaurantFish> BringBack = new()
            {
                new() { Name = "mackerel", Art = "fish-mackerel", Amount = "8" },
                new() { Name = "pollock", Art = "fish-pollock", Amount = "3 kg" },
            };
            public string SpecialTitle = "A birthday table for four", SpecialReward = "+120";
            public bool? SpecialAccepted;
        }

        public sealed class RestaurantPrepView
        {
            public List<RestaurantFish> Catch = new()
            {
                new() { Name = "Mackerel", Art = "fish-mackerel", Amount = "12" },
                new() { Name = "Pollock", Art = "fish-pollock", Amount = "5 kg" },
            };
            public List<RestaurantPrepRow> Rows = new()
            {
                new() { Name = "Grilled fish", Art = "v2-dish-grilled-fish", Fallback = "fish-mackerel", Portions = 10, ForecastLow = 8, ForecastHigh = 10 },
                new() { Name = "Fish soup", Art = "v2-dish-fish-soup", Fallback = "icon-food", Portions = 8, ForecastLow = 6, ForecastHigh = 8 },
                new() { Name = "Fillets", Art = "v2-dish-fillets", Fallback = "fish-pollock", Portions = 12, ForecastLow = 10, ForecastHigh = 12 },
            };
            public int Margin = 1; // 0 tight, 1 +10%, 2 +20%
            public int Fridge = 30, FridgeCapacity = 30, MarketFish = 2, MarketCoins = 18;
            public bool CaptainsCut = true;
            public int RestaurantPortions { get { int n = 0; foreach (var r in Rows) n += r.Portions; return n; } }
        }

        public sealed class RestaurantClosingView
        {
            public int Served = 22, Left = 2, Dishes = 420, Drinks = 96, Tips = 48, CatPortions = 3, CatValue = 18;
            public int Stars = 3, PopularityFrom = 42, PopularityTo = 46; public float Popularity = .82f, PopularityBefore = .74f;
            public string CrewOfTheNight = "Jo", CrewPortrait = "deckhand";
            public string MiraLine = "Same time tomorrow?";
            public List<RestaurantReview> Reviews = new()
            {
                new() { Portrait = "fisher", Stars = 5, Quote = "Fish worth the wait." },
                new() { Portrait = "deckhand", Stars = 4, Quote = "Cosy, even in the rain." },
                new() { Portrait = "captain", Stars = 4, Quote = "More coffee, please!" },
            };
            public int Total => Dishes + Drinks + Tips;
        }

        public RestaurantPlanView RestaurantPlan = new();
        public RestaurantPrepView RestaurantPrep = new();
        public RestaurantClosingView RestaurantClosing = new();


        public sealed class RestaurantStock { public string Name, Art, Fallback; public int Count, Max; public bool Alert; }
        public sealed class RestaurantStaff { public string Portrait, Job, Icon, Fallback; public float Busy; }
        // How the staff rail shows a crew bigger than the mockup's five (Mo 10-26: compare these before choosing).
        public enum RestaurantRailMode { Mockup, Jobs, Scroll, Chips }
        public sealed class RestaurantServiceView
        {
            public string Name = "Mira's";
            public float Hour = 18 + 40 / 60f, Open = 18, Close = 23;
            public int Coins = 320, Popularity = 42, Speed = 1; public bool Paused;
            public List<RestaurantStock> Stock = new()
            {
                new() { Name = "Fish", Art = "v2-icon-fish", Fallback = "icon-fish", Count = 8, Max = 12, Alert = true },
                new() { Name = "Soup", Art = "v2-icon-soup", Fallback = "icon-food", Count = 5, Max = 10 },
                new() { Name = "Coffee", Art = "v2-icon-cup", Fallback = "v2-icon-clock", Count = 12, Max = 20 },
            };
            public string Alert = "Fryer\nneeds repair";
            public string QuestionTitle = "A late table?", QuestionBody = "A party of four\nhas arrived.", QuestionBodyShort = "A group just arrived.\nShall we seat them?", QuestionYes = "Seat them", QuestionNo = "Not tonight";
            // Expected guests per half hour, 18:00-23:00, for the phone's arrival strip.
            public float[] Arrivals = { .4f, .7f, 1f, .9f, .75f, .6f, .45f, .3f, .2f, .1f };
            public RestaurantRailMode Rail;
            // A full stage-4 night: eight sailed crew, Mira, and the captain walking around.
            public List<RestaurantStaff> Crew = new()
            {
                new() { Portrait = "kofi", Job = "Cook", Icon = "v2-icon-pan", Fallback = "icon-food", Busy = .8f },
                new() { Portrait = "rosa", Job = "Cook", Icon = "v2-icon-pan", Fallback = "icon-food", Busy = .6f },
                new() { Portrait = "sam", Job = "Serve", Icon = "v2-icon-cloche", Fallback = "v2-icon-haul", Busy = .95f },
                new() { Portrait = "jo", Job = "Serve", Icon = "v2-icon-cloche", Fallback = "v2-icon-haul", Busy = .75f },
                new() { Portrait = "mei", Job = "Serve", Icon = "v2-icon-cloche", Fallback = "v2-icon-haul", Busy = .5f },
                new() { Portrait = "dirk", Job = "Fix", Icon = "v2-icon-wrench", Fallback = "v2-icon-engine", Busy = .45f },
                new() { Portrait = "ines", Job = "Coffee", Icon = "v2-icon-cup", Fallback = "v2-icon-clock", Busy = .85f },
                new() { Portrait = "mats", Job = "Coffee", Icon = "v2-icon-cup", Fallback = "v2-icon-clock", Busy = .7f },
                new() { Portrait = "mira", Job = "Host", Icon = "v2-icon-bell", Fallback = "v2-icon-anchor", Busy = 1f },
                new() { Portrait = "captain", Job = "Help", Icon = "v2-icon-crew", Fallback = "icon-crew", Busy = .6f },
            };
            public List<RestaurantStaff> Staff = new()
            {
                new() { Portrait = "kofi", Job = "Cook", Icon = "v2-icon-pan", Fallback = "icon-food", Busy = .7f },
                new() { Portrait = "sam", Job = "Serve", Icon = "v2-icon-cloche", Fallback = "v2-icon-haul", Busy = .9f },
                new() { Portrait = "ines", Job = "Fix", Icon = "v2-icon-wrench", Fallback = "v2-icon-engine", Busy = .55f },
                new() { Portrait = "mats", Job = "Coffee", Icon = "v2-icon-cup", Fallback = "v2-icon-clock", Busy = .85f },
                new() { Portrait = "mira", Job = "Reception", Icon = "v2-icon-bell", Fallback = "v2-icon-anchor", Busy = 1f },
            };
        }
        public RestaurantServiceView RestaurantService = new();

        // A task ring: the kit's portrait ring filled clockwise, green when steady, amber when busy.
        void RestaurantRing(string id, Rect r, float value, Transform parent)
        {
            coastalUi.Icon(id + "/track", r, "v2-ring-task", parent, new Color(.84f, .82f, .77f));
            coastalUi.Icon(id, r, "v2-ring-task", parent, value >= .7f ? Skin.Good : Skin.Warn);
            var img = coastalUi.ElementRect(id)?.GetComponent<UnityEngine.UI.Image>();
            if (img != null) { img.type = UnityEngine.UI.Image.Type.Filled; img.fillMethod = UnityEngine.UI.Image.FillMethod.Radial360; img.fillOrigin = 2; img.fillClockwise = true; img.fillAmount = Mathf.Clamp01(value); }
        }

        // S2: the evening service HUD, laid out from ui-service-desktop.png (1440x900) as fractions of the screen.
        void InterfaceRestaurantService(RestaurantServiceView v)
        {
            if (compactInterface) { InterfaceRestaurantServicePhone(v); return; }
            bool phone = false;
            float sx = iw / 1440f, sy = ih / 900f, u = Mathf.Min(sx, sy);
            Rect R(float x, float y, float w, float h) => new(x * sx, y * sy, w * sx, h * sy);

            // Top band: back, title, the evening timeline, coins, stars, speed.
            float barH = Mathf.Max(phone ? 44 : 0, 78 * sy);
            coastalUi.Sliced("rsvc/bar", new Rect(0, 0, iw, barH), "v2-pill-navy", null, Skin.HeaderNavy, true);
            float bs = barH - 16 * sy;
            coastalUi.Secondary("rsvc/back", new Rect(24 * sx, (barH - bs) / 2, bs * 1.36f, bs), "", () => RestaurantPreview = RestaurantScreen.None, "v2-icon-back");
            coastalUi.Text("rsvc/title", new Rect(24 * sx + bs * 1.36f + 22 * sx, 0, 430 * sx, barH), $"{v.Name} · Evening service", Skin.Type.Display, Skin.Cream, TextAnchor.MiddleLeft, null, true);
            coastalUi.SetTextSize("rsvc/title", Mathf.RoundToInt(Mathf.Max(phone ? 20 : 24, 34 * u)));
            float tx = 570 * sx, tw = 265 * sx, ty = barH * .48f;
            coastalUi.Sliced("rsvc/time/line", new Rect(tx, ty - 1.5f, tw, 3), "v2-bar-track", null, Skin.Cream);
            float At(float h) => h <= 20 ? Mathf.InverseLerp(v.Open, 20, h) * .54f : .54f + Mathf.InverseLerp(20, v.Close, h) * .46f;
            float t = At(v.Hour);
            coastalUi.Sliced("rsvc/time/done", new Rect(tx, ty - 1.5f, tw * t, 3), "v2-bar-warn", null, Skin.Orange);
            float[] dots = { 18, 19, 20, 21.5f, 23 };
            for (int i = 0; i < dots.Length; i++)
            {
                float dx = tx + tw * At(dots[i]); bool past = dots[i] <= v.Hour;
                coastalUi.Icon($"rsvc/time/dot{i}", new Rect(dx - 5, ty - 5, 10, 10), "v2-light-good", null, past ? Skin.Orange : Skin.Cream);
            }
            string[] labels = { "18:00", "20:00", "23:00" }; float[] at = { 0, .54f, 1 };
            for (int i = 0; i < 3; i++)
                coastalUi.Text($"rsvc/time/l{i}", new Rect(tx + tw * at[i] - 40, ty + 6, 80, barH - ty - 6), labels[i], Skin.Type.Small, Skin.Cream, TextAnchor.UpperCenter);
            float nowX = tx + tw * t;
            coastalUi.Sliced("rsvc/time/flag", new Rect(nowX - 26, 3, 52, ty - 10), "v2-btn-primary", null, Color.white);
            int hh = Mathf.FloorToInt(v.Hour), mm = Mathf.FloorToInt((v.Hour - hh) * 60);
            coastalUi.Text("rsvc/time/now", new Rect(nowX - 26, 3, 52, ty - 12), $"{hh}:{mm:00}", Skin.Type.Caption, Skin.Cream, TextAnchor.MiddleCenter);
            coastalUi.Icon("rsvc/time/pin", new Rect(nowX - 7, ty - 7, 14, 14), "v2-light-good", null, Skin.Orange);

            float ph = barH - 26 * sy, py = (barH - ph) / 2;
            var cr = R(938, 0, 120, 0);
            var coins = coastalUi.Sliced("rsvc/coins", new Rect(cr.x, py, cr.width, ph), "v2-pill-navy", null, Skin.PlankDark);
            coastalUi.Icon("rsvc/coins/icon", new Rect(-6, -4, ph + 8, ph + 8), "v2-icon-coin", coins, null, "icon-coin");
            coastalUi.Text("rsvc/coins/n", new Rect(ph + 6, 0, cr.width - ph - 10, ph), v.Coins.ToString("N0"), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, coins, true);
            var sr = R(1084, 0, 116, 0);
            var stars = coastalUi.Sliced("rsvc/stars", new Rect(sr.x, py, sr.width, ph), "v2-pill-navy", null, Skin.PlankDark);
            coastalUi.Icon("rsvc/stars/icon", new Rect(-4, -4, ph + 8, ph + 8), "v2-icon-star-blue", stars, null, "icon-star");
            coastalUi.Text("rsvc/stars/n", new Rect(ph + 8, 0, sr.width - ph - 12, ph), v.Popularity.ToString(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, stars, true);
            var spd = R(1226, 0, 194, 0);
            var speed = coastalUi.Sliced("rsvc/speed", new Rect(spd.x, py, spd.width, ph), "v2-pill-navy", null, Skin.PlankDark);
            float seg = spd.width / 3f;
            string[] sl = { "II", "1×", "2×" };
            for (int i = 0; i < 3; i++)
            {
                int k = i; bool on = i == 0 ? v.Paused : !v.Paused && v.Speed == i;
                if (on) coastalUi.Sliced($"rsvc/speed/{i}/on", new Rect(seg * i + 3, 3, seg - 6, ph - 6), "v2-btn-primary", speed, Color.white);
                coastalUi.Text($"rsvc/speed/{i}", new Rect(seg * i, 0, seg, ph), sl[i], Skin.Type.Heading, on ? Skin.Cream : new Color(.8f, .85f, .9f), TextAnchor.MiddleCenter, speed, on);
                coastalUi.HitArea($"rsvc/speed/{i}/hit", new Rect(seg * i, 0, seg, ph), () => { if (k == 0) v.Paused = !v.Paused; else { v.Paused = false; v.Speed = k; } }, speed);
            }

            // Left: tonight's stock and the repair alert.
            var st = R(18, 92, 190, 0);
            float rowH = Mathf.Max(phone ? 40 : 0, 62 * sy), stockH = 36 * sy + rowH * v.Stock.Count + (v.Alert != null ? rowH * 1.15f : 0) + 12 * sy;
            var stock = coastalUi.Slab("rsvc/stock", new Rect(st.x, st.y, st.width, stockH));
            coastalUi.Text("rsvc/stock/title", new Rect(14 * sx, 4, st.width - 20 * sx, 34 * sy), "Tonight's stock", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, stock);
            for (int i = 0; i < v.Stock.Count; i++)
            {
                var s = v.Stock[i];
                var c = coastalUi.Card($"rsvc/stock/{i}", new Rect(10 * sx, 38 * sy + i * rowH, st.width - 20 * sx, rowH - 6 * sy), Skin.Card.Soft, stock);
                float ch = rowH - 6 * sy;
                coastalUi.Icon($"rsvc/stock/{i}/icon", new Rect(8 * sx, 3, ch * 1.3f, ch - 6), s.Art, c, null, s.Fallback);
                coastalUi.Text($"rsvc/stock/{i}/n", new Rect(ch * 1.3f + 20 * sx, 0, st.width * .4f, ch), s.Count.ToString(), Skin.Type.Number, s.Count <= 2 ? Skin.BadInk : Skin.Ink, TextAnchor.MiddleLeft, c);
            }
            if (v.Alert != null)
            {
                var a = coastalUi.Card("rsvc/alert", new Rect(10 * sx, 38 * sy + v.Stock.Count * rowH, st.width - 20 * sx, rowH * 1.1f), Skin.Card.Alert, stock);
                coastalUi.Icon("rsvc/alert/icon", new Rect(6 * sx, rowH * .25f, rowH * .55f, rowH * .55f), "v2-icon-wrench", a, Skin.Bad, "v2-icon-warning");
                coastalUi.Text("rsvc/alert/text", new Rect(rowH * .55f + 12 * sx, 0, st.width - rowH * .55f - 36 * sx, rowH * 1.1f), v.Alert, Skin.Type.Small, Skin.BadInk, TextAnchor.MiddleLeft, a);
            }

            // Right: Mira asks you something.
            if (v.QuestionTitle != null)
            {
                var q = R(1155, 84, 272, 262);
                var card = coastalUi.Slab("rsvc/ask", q);
                float face = Mathf.Min(q.width * .44f, q.height * .44f);
                coastalUi.Icon("rsvc/ask/mira", new Rect(4, 2, face, face), "v2-mira-wave", card, null, "v2-portrait-mira");
                coastalUi.Text("rsvc/ask/title", new Rect(face + 6, 10 * sy, q.width - face - 12, 34 * sy), v.QuestionTitle, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, card);
                coastalUi.Text("rsvc/ask/body", new Rect(face + 6, 44 * sy, q.width - face - 12, face - 46 * sy), v.QuestionBody, Skin.Type.Small, Skin.InkSoft, TextAnchor.UpperLeft, card);
                float bw = q.width - 28 * sx, bh = Mathf.Max(phone ? 40 : 0, 50 * sy);
                coastalUi.Primary("rsvc/ask/yes", new Rect(14 * sx, face + 4 * sy, bw, bh), v.QuestionYes, () => v.QuestionTitle = null, null, true, card);
                coastalUi.Secondary("rsvc/ask/no", new Rect(14 * sx, face + bh + 12 * sy, bw, bh), v.QuestionNo, () => v.QuestionTitle = null, null, true, card);
            }

            // Bottom: the staff rail, one card per crew member with their fixed job and how busy they are.
            if (v.Rail != RestaurantRailMode.Mockup) { RestaurantRail("rsvc/crew", R(36, 762, 1368, 108), false, v); return; }
            var rail = R(36, 762, 1368, 108);
            coastalUi.Slab("rsvc/rail", rail);
            float cw = (rail.width - 16 * sx) / Mathf.Max(1, v.Staff.Count);
            for (int i = 0; i < v.Staff.Count; i++)
            {
                var s = v.Staff[i];
                var c = coastalUi.Card($"rsvc/staff/{i}", new Rect(rail.x + 8 * sx + i * cw, rail.y + 6 * sy, cw - 8 * sx, rail.height - 12 * sy), Skin.Card.Soft);
                float h = rail.height - 12 * sy, bust = h * 1.06f;
                coastalUi.Icon($"rsvc/staff/{i}/bust", new Rect(6 * sx, h - bust, bust * .9f, bust), $"v2-bust-{s.Portrait}", c, null, $"v2-portrait-{s.Portrait}-deck");
                coastalUi.Text($"rsvc/staff/{i}/job", new Rect(bust * .9f + 10 * sx, 4, cw - 8 * sx - bust * .9f - h * .64f - 30 * sx, h * .42f), s.Job, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, c);
                coastalUi.Icon($"rsvc/staff/{i}/icon", new Rect(bust * .9f + 14 * sx, h * .44f, h * .46f, h * .46f), s.Icon, c, null, s.Fallback);
                float ring = h * .64f;
                RestaurantRing($"rsvc/staff/{i}/ring", new Rect(cw - 8 * sx - ring - 14 * sx, (h - ring) / 2, ring, ring), s.Busy, c);
            }
        }


        // S2 on a phone, laid out from ui-2-service.png (844x390): clock left, the arrival strip, stock cards with bars,
        // Mira's question with icon buttons, four staff cards with bars along the bottom.
        void InterfaceRestaurantServicePhone(RestaurantServiceView v)
        {
            float sx = iw / 844f, sy = ih / 390f;
            Rect R(float x, float y, float w, float h) => new(x * sx, y * sy, w * sx, h * sy);

            var bar = R(0, 0, 844, 46);
            coastalUi.Sliced("rsph/bar", bar, "v2-pill-navy", null, Skin.HeaderNavy, true);
            coastalUi.Icon("rsph/sun", R(8, 5, 36, 36), "v2-icon-sun", null, null, "icon-Sun");
            int hh = Mathf.FloorToInt(v.Hour), mm = Mathf.FloorToInt((v.Hour - hh) * 60);
            coastalUi.Text("rsph/clock", R(52, 2, 110, 26), $"{hh}:{mm:00}", Skin.Type.Number, Skin.Cream, TextAnchor.MiddleLeft, null, true);
            coastalUi.Text("rsph/clock/sub", R(52, 25, 120, 18), "Evening service", Skin.Type.Small, Skin.Cream, TextAnchor.MiddleLeft);

            // Arrival strip: who is expected when; past half hours dim, a NOW flag over the present.
            var strip = R(178, 6, 324, 32);
            coastalUi.Sliced("rsph/strip", strip, "v2-pill-navy", null, Skin.PlankDark);
            float t = Mathf.InverseLerp(v.Open, v.Close, v.Hour), sw = strip.width - 24, sh = strip.height;
            coastalUi.Sliced("rsph/strip/line", new Rect(strip.x + 12, strip.y + sh - 8, sw, 3), "v2-bar-track", null, new Color(1, 1, 1, .35f));
            coastalUi.Sliced("rsph/strip/done", new Rect(strip.x + 12, strip.y + sh - 8, sw * t, 3), "v2-bar-warn", null, Skin.Orange);
            for (int i = 0; i < v.Arrivals.Length; i++)
            {
                float f = (i + .5f) / v.Arrivals.Length, ph = (sh - 12) * (.45f + .55f * v.Arrivals[i]);
                bool past = f < t;
                coastalUi.Icon($"rsph/strip/g{i}", new Rect(strip.x + 12 + sw * f - ph * .4f, strip.y + sh - 9 - ph, ph * .8f, ph), "v2-icon-crew", null,
                    past ? new Color(1, 1, 1, .3f) : new Color(Skin.Warn.r, Skin.Warn.g, Skin.Warn.b, .85f), "icon-crew");
            }
            float nx = strip.x + 12 + sw * t;
            coastalUi.Sliced("rsph/strip/now", new Rect(nx - 22 * sx, 0, 44 * sx, 15 * sy), "v2-btn-primary", null, Color.white);
            coastalUi.Text("rsph/strip/now/t", new Rect(nx - 22 * sx, 0, 44 * sx, 15 * sy), "NOW", Skin.Type.Caption, Skin.Cream, TextAnchor.MiddleCenter);
            coastalUi.Icon("rsph/strip/pin", new Rect(nx - 6, strip.y + sh - 12, 12, 12), "v2-light-good", null, Skin.Orange);

            var coins = coastalUi.Sliced("rsph/coins", R(527, 8, 78, 30), "v2-pill-navy", null, Skin.PlankDark);
            coastalUi.Icon("rsph/coins/icon", new Rect(-2, -2, 34 * sy, 34 * sy), "v2-icon-coin", coins, null, "icon-coin");
            coastalUi.Text("rsph/coins/n", new Rect(34 * sy, 0, 78 * sx - 36 * sy, 30 * sy), v.Coins.ToString("N0"), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, coins, true);
            var stars = coastalUi.Sliced("rsph/stars", R(617, 8, 72, 30), "v2-pill-navy", null, Skin.PlankDark);
            coastalUi.Icon("rsph/stars/icon", new Rect(0, -2, 34 * sy, 34 * sy), "icon-star", stars);
            coastalUi.Text("rsph/stars/n", new Rect(36 * sy, 0, 72 * sx - 38 * sy, 30 * sy), v.Popularity.ToString(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, stars, true);
            for (int i = 1; i <= 2; i++)
            {
                int k = i; bool on = !v.Paused && v.Speed == i;
                var b = R(703 + (i - 1) * 49, 6, 45, 34);
                if (on) coastalUi.Primary($"rsph/speed/{i}", b, $"{i}×", () => { v.Paused = false; v.Speed = k; });
                else coastalUi.Secondary($"rsph/speed/{i}", b, $"{i}×", () => { v.Paused = false; v.Speed = k; });
            }
            coastalUi.Secondary("rsph/speed/0", R(800, 6, 36, 34), v.Paused ? "▶" : "II", () => v.Paused = !v.Paused);

            // Left: stock cards.
            for (int i = 0; i < v.Stock.Count; i++)
            {
                var s = v.Stock[i];
                var c = coastalUi.Card($"rsph/stock/{i}", R(10, 55 + i * 64, 147, 60), Skin.Card.Soft);
                coastalUi.Icon($"rsph/stock/{i}/icon", new Rect(6 * sx, 8 * sy, 50 * sx, 44 * sy), s.Art, c, null, s.Fallback);
                coastalUi.Text($"rsph/stock/{i}/name", new Rect(60 * sx, 4 * sy, 70 * sx, 20 * sy), s.Name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, c);
                coastalUi.Text($"rsph/stock/{i}/n", new Rect(60 * sx, 21 * sy, 60 * sx, 20 * sy), s.Count.ToString(), Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, c);
                float f = s.Max > 0 ? (float)s.Count / s.Max : 0;
                coastalUi.ProgressBar($"rsph/stock/{i}/bar", new Rect(60 * sx, 43 * sy, 76 * sx, 9 * sy), f, f < .25f ? Skin.Bar.Bad : f < .6f ? Skin.Bar.Warn : Skin.Bar.Good, c);
                if (s.Alert) coastalUi.Icon($"rsph/stock/{i}/alert", new Rect(118 * sx, 4 * sy, 22 * sy, 22 * sy), "v2-icon-warning", c, Skin.Bad);
            }

            // Right: Mira asks.
            if (v.QuestionTitle != null)
            {
                var q = R(655, 55, 184, 168);
                var card = coastalUi.Slab("rsph/ask", q);
                coastalUi.Icon("rsph/ask/mira", new Rect(6 * sx, 4 * sy, 68 * sy, 68 * sy), "v2-mira-wave", card, null, "v2-portrait-mira");
                coastalUi.Text("rsph/ask/title", new Rect(78 * sx, 8 * sy, 104 * sx, 22 * sy), v.QuestionTitle, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, card);
                coastalUi.Text("rsph/ask/body", new Rect(78 * sx, 30 * sy, 104 * sx, 40 * sy), v.QuestionBodyShort, Skin.Type.Caption, Skin.InkSoft, TextAnchor.UpperLeft, card);
                coastalUi.Primary("rsph/ask/yes", new Rect(8 * sx, 82 * sy, 166 * sx, 36 * sy), v.QuestionYes, () => v.QuestionTitle = null, "v2-icon-crew", true, card);
                coastalUi.Secondary("rsph/ask/no", new Rect(8 * sx, 124 * sy, 166 * sx, 36 * sy), v.QuestionNo, () => v.QuestionTitle = null, null, true, card);
            }

            // Bottom: staff cards (Mira hosts from her card, so the rail shows the other four).
            if (v.Rail != RestaurantRailMode.Mockup) { RestaurantRail("rsph/crew", R(10, 318, 824, 68), true, v); return; }
            int n = 0;
            foreach (var s in v.Staff)
            {
                if (s.Portrait == "mira") continue;
                var c = coastalUi.Card($"rsph/staff/{n}", R(18 + n * 163, 322, 156, 62), Skin.Card.Soft);
                coastalUi.Icon($"rsph/staff/{n}/bust", new Rect(4 * sx, 0, 54 * sx, 62 * sy), $"v2-bust-{s.Portrait}", c, null, $"v2-portrait-{s.Portrait}-deck");
                coastalUi.Icon($"rsph/staff/{n}/icon", new Rect(62 * sx, 8 * sy, 22 * sy, 22 * sy), s.Icon, c, Skin.Ink, s.Fallback);
                coastalUi.Text($"rsph/staff/{n}/job", new Rect(62 * sx + 26 * sy, 6 * sy, 70 * sx, 26 * sy), s.Job, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, c);
                coastalUi.ProgressBar($"rsph/staff/{n}/bar", new Rect(62 * sx, 38 * sy, 86 * sx, 12 * sy), s.Busy, s.Busy >= .7f ? Skin.Bar.Good : Skin.Bar.Warn, c);
                n++;
            }
        }


        // The staff rail for a whole crew, in one of the three layouts Mo is choosing between.
        void RestaurantRail(string id, Rect rail, bool phone, RestaurantServiceView v)
        {
            coastalUi.Slab(id, rail);
            var groups = new List<List<RestaurantStaff>>();
            foreach (var s in v.Crew)
            {
                var g = groups.Find(x => x[0].Job == s.Job);
                if (g == null) groups.Add(g = new List<RestaurantStaff>());
                g.Add(s);
            }
            float pad = phone ? 5 : 8, h = rail.height - pad * 2;
            switch (v.Rail)
            {
                case RestaurantRailMode.Jobs:
                {
                    // One card per job: its people as overlapping faces, a count, one ring for the job's load.
                    float cw = (rail.width - pad) / groups.Count;
                    for (int i = 0; i < groups.Count; i++)
                    {
                        var g = groups[i]; string gid = $"{id}/job/{i}";
                        var c = coastalUi.Card(gid, new Rect(rail.x + pad + i * cw, rail.y + pad, cw - pad, h), Skin.Card.Soft);
                        float face = h * (phone ? .58f : .56f), step = face * .5f, load = 0;
                        foreach (var s in g) load += s.Busy;
                        load /= g.Count;
                        for (int k = 0; k < g.Count && k < 3; k++)
                            coastalUi.Portrait($"{gid}/face{k}", new Rect(6 + k * step, h - face - 4, face, face), g[k].Portrait, c);
                        float tx = 6 + Mathf.Min(g.Count, 3) * step + face * .5f;
                        coastalUi.Icon($"{gid}/icon", new Rect(8, 4, h * .3f, h * .3f), g[0].Icon, c, null, g[0].Fallback);
                        coastalUi.Text($"{gid}/job", new Rect(12 + h * .3f, 2, cw - h * .3f - 20, h * .34f), g[0].Job, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, c);
                        float ring = h * (phone ? .46f : .56f);
                        if (g.Count > 1) coastalUi.Text($"{gid}/n", new Rect(tx - 2, h * .45f, cw - pad - ring - 12 - tx, h * .5f), $"×{g.Count}", Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleLeft, c);
                        RestaurantRing($"{gid}/ring", new Rect(cw - pad - ring - 8, h - ring - 6, ring, ring), load, c);
                    }
                    break;
                }
                case RestaurantRailMode.Scroll:
                {
                    // One card per person; whatever does not fit waits behind the arrow.
                    float arrow = h * .7f, cw = phone ? 150 : 250 * rail.width / 1368f, x0 = rail.x + pad + arrow + pad;
                    int fit = Mathf.Max(1, Mathf.FloorToInt((rail.width - (arrow + pad) * 2 - pad) / cw));
                    coastalUi.Secondary($"{id}/left", new Rect(rail.x + pad, rail.y + (rail.height - arrow) / 2, arrow, arrow), "‹", () => { }, null, false);
                    for (int i = 0; i < fit && i < v.Crew.Count; i++)
                    {
                        var s = v.Crew[i]; string cid = $"{id}/card/{i}";
                        var c = coastalUi.Card(cid, new Rect(x0 + i * cw, rail.y + pad, cw - pad, h), Skin.Card.Soft);
                        float face = h - 10;
                        coastalUi.Portrait($"{cid}/face", new Rect(5, 5, face, face), s.Portrait, c);
                        coastalUi.Text($"{cid}/job", new Rect(face + 8, 2, cw - face - h * .5f - 14, h * .5f), s.Job, phone ? Skin.Type.Small : Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, c);
                        coastalUi.Icon($"{cid}/icon", new Rect(face + 10, h * .52f, h * .36f, h * .36f), s.Icon, c, null, s.Fallback);
                        float ring = h * .5f;
                        RestaurantRing($"{cid}/ring", new Rect(cw - pad - ring - 6, (h - ring) / 2, ring, ring), s.Busy, c);
                    }
                    int more = v.Crew.Count - fit;
                    var right = new Rect(rail.xMax - pad - arrow, rail.y + (rail.height - arrow) / 2, arrow, arrow);
                    coastalUi.Secondary($"{id}/right", right, more > 0 ? $"+{more}" : "›", () => { });
                    break;
                }
                default:
                {
                    // Chips: every person as a round face in its own task ring, grouped under the job.
                    float head = h * .34f, chip = h - head - 2, gap = phone ? 10 : 22;
                    float total = 0;
                    foreach (var g in groups) total += g.Count * (chip + 4);
                    float extra = (rail.width - pad * 2 - total - gap * (groups.Count - 1)) / groups.Count;
                    float x = rail.x + pad;
                    for (int i = 0; i < groups.Count; i++)
                    {
                        var g = groups[i]; string gid = $"{id}/group/{i}";
                        float gw = g.Count * (chip + 4) + extra;
                        coastalUi.Icon($"{gid}/icon", new Rect(x + 4, rail.y + pad + 2, head - 4, head - 4), g[0].Icon, null, null, g[0].Fallback);
                        coastalUi.Text($"{gid}/job", new Rect(x + head + 4, rail.y + pad, gw - head, head), g[0].Job, Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft);
                        float cx = x + (gw - g.Count * (chip + 4)) / 2;
                        for (int k = 0; k < g.Count; k++)
                        {
                            var r = new Rect(cx + k * (chip + 4), rail.y + pad + head, chip, chip);
                            RestaurantRing($"{gid}/ring{k}", r, g[k].Busy, null);
                            float inset = chip * .13f;
                            coastalUi.Portrait($"{gid}/face{k}", new Rect(r.x + inset, r.y + inset, chip - inset * 2, chip - inset * 2), g[k].Portrait);
                        }
                        x += gw;
                        if (i < groups.Count - 1) coastalUi.Sliced($"{gid}/split", new Rect(x + gap / 2 - 1, rail.y + pad + 4, 2, h - 8), "v2-bar-track", null, Skin.CreamDeep);
                        x += gap;
                    }
                    break;
                }
            }
        }

        // Returns true when a restaurant screen took the frame.
        bool InterfaceRestaurant()
        {
            switch (RestaurantPreview)
            {
                case RestaurantScreen.Plan: InterfaceRestaurantPlan(RestaurantPlan); return true;
                case RestaurantScreen.Prep: InterfaceRestaurantPrep(RestaurantPrep); return true;
                case RestaurantScreen.Closing: InterfaceRestaurantClosing(RestaurantClosing); return true;
                case RestaurantScreen.Service: InterfaceRestaurantService(RestaurantService); return true;
            }
            return false;
        }

        // A hanging plank sign with the screen's title; the generated sign art when it exists, a navy slab otherwise.
        void RestaurantSign(string id, Rect r, string title, Transform parent = null)
        {
            if (HasUi("v2-sign-plank")) coastalUi.Sliced(id, r, "v2-sign-plank", parent);
            else coastalUi.Slab(id, r, null, false, parent);
            coastalUi.Text(id + "/title", new Rect(r.x + 16, r.y + 4, r.width - 32, r.height - 8), title, Skin.Type.Display,
                HasUi("v2-sign-plank") ? Skin.Cream : Skin.Ink, TextAnchor.MiddleCenter, parent, HasUi("v2-sign-plank"));
        }

        // The soft evening restaurant behind full-screen cards; navy planks until that painting exists.
        void RestaurantBackdrop(string id)
        {
            if (HasUi("v2-restaurant-backdrop")) coastalUi.Backdrop(id, "v2-restaurant-backdrop");
            else coastalUi.Planks(id, false);
        }

        void RestaurantStars(string id, Rect r, int stars, Transform parent)
        {
            float s = Mathf.Min(r.height, r.width / 5f);
            for (int i = 0; i < 5; i++)
                coastalUi.Icon($"{id}/{i}", new Rect(r.x + i * s, r.y + (r.height - s) / 2, s - 2, s - 2), "icon-star", parent,
                    i < stars ? Color.white : new Color(1, 1, 1, .28f));
        }

        // The card screens are laid out in their mockup's own 844x390 frame and scaled as one piece, so every size
        // shows the same composition; whatever is left around it shows the backdrop.
        Transform RestaurantFrame(string id)
        {
            float k = Mathf.Min(iw / 844f, ih / 390f);
            var frame = coastalUi.Sliced(id, new Rect((iw - 844 * k) / 2, (ih - 390 * k) / 2, 844, 390), "");
            frame.localScale = new Vector3(k, k, 1);
            return frame;
        }

        // A green kit pill used as a button (the mockups' Accept).
        void RestaurantGoodButton(string id, Rect r, string label, System.Action action, Transform parent)
        {
            var b = coastalUi.Sliced(id, r, "v2-btn-secondary", parent, Skin.Good);
            coastalUi.Icon(id + "/icon", new Rect(14, (r.height - 20) / 2, 20, 20), "v2-icon-tick", b, Skin.Cream);
            coastalUi.Text(id + "/label", new Rect(38, 0, r.width - 46, r.height), label, Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleCenter, b, true);
            coastalUi.HitArea(id + "/hit", new Rect(0, 0, r.width, r.height), action, b);
        }

        // S3: Mira's plan card on the way out (ui-3-mira-plan.png).
        void InterfaceRestaurantPlan(RestaurantPlanView v)
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rplan/planks", false);
            var f = RestaurantFrame("rplan/frame");
            coastalUi.Secondary("rplan/back", new Rect(14, 12, 124, 46), "Back", () => RestaurantPreview = RestaurantScreen.None, "v2-icon-back", true, f);
            coastalUi.Icon("rplan/mira", new Rect(-14, 38 + Mathf.Sin(SimTime * 1.6f) * 1.5f, 300, 356), "mira-pose-explain", f, null, "art108-mira");
            RestaurantSign("rplan/sign", new Rect(236, 6, 392, 56), "Tonight at Mira's", f);

            var card = coastalUi.Slab("rplan/card", new Rect(260, 82, 394, 276), null, false, f);
            coastalUi.Icon("rplan/cal", new Rect(32, 12, 40, 40), "v2-icon-calendar", card, null, "v2-icon-clock");
            coastalUi.Text("rplan/day", new Rect(90, 8, 300, 28), $"{v.Day.ToUpperInvariant()} · {v.Hours}", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, card);
            coastalUi.Text("rplan/guests", new Rect(90, 34, 300, 22), $"{v.GuestsLow} – {v.GuestsHigh} guests + walk-ins", Skin.Type.Body, Skin.Ink, TextAnchor.MiddleLeft, card);
            for (int i = 0; i < v.Dishes.Count && i < 3; i++)
            {
                var d = v.Dishes[i];
                var dc = coastalUi.Card($"rplan/dish/{i}", new Rect(16 + i * 126, 80, 118, 120), Skin.Card.Soft, card);
                coastalUi.Icon($"rplan/dish/{i}/art", new Rect(8, 6, 102, 66), d.Art, dc, null, d.Fallback);
                coastalUi.Text($"rplan/dish/{i}/name", new Rect(4, 72, 110, 22), d.Name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, dc);
                coastalUi.Icon($"rplan/dish/{i}/who", new Rect(30, 96, 18, 18), "v2-icon-guests", dc, Skin.Ink, "v2-icon-crew");
                coastalUi.Text($"rplan/dish/{i}/range", new Rect(52, 94, 60, 22), $"{d.Low} – {d.High}", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, dc);
            }
            var bring = coastalUi.Card("rplan/bring", new Rect(16, 210, 362, 56), Skin.Card.Soft, card);
            coastalUi.Icon("rplan/bring/fish", new Rect(6, 4, 106, 48), "v2-catch-pile", bring, null, "fish-mackerel");
            coastalUi.Text("rplan/bring/title", new Rect(124, 4, 120, 20), "Bring back:", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, bring);
            for (int i = 0; i < v.BringBack.Count && i < 2; i++)
            {
                var fish = v.BringBack[i]; float x = 124 + i * 118;
                coastalUi.Icon($"rplan/bring/{i}/icon", new Rect(x, 28, 30, 20), fish.Art, bring, null, "v2-icon-fish");
                coastalUi.Text($"rplan/bring/{i}/n", new Rect(x + 34, 24, 60, 28), fish.Amount, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, bring);
                coastalUi.Text($"rplan/bring/{i}/name", new Rect(x + 38 + fish.Amount.Length * 9, 26, 64, 26), fish.Name, Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, bring);
                if (i == 0) coastalUi.Sliced("rplan/bring/split", new Rect(x + 112, 26, 2, 24), "v2-bar-track", bring, Skin.CreamDeep);
            }

            var special = coastalUi.Slab("rplan/special", new Rect(668, 70, 170, 214), null, false, f);
            coastalUi.Icon("rplan/special/icon", new Rect(12, 14, 26, 26), "v2-icon-special", special, null, "v2-icon-goal");
            coastalUi.Text("rplan/special/head", new Rect(42, 12, 124, 30), "Special request", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, special);
            coastalUi.Text("rplan/special/body", new Rect(10, 52, 150, 48), v.SpecialTitle, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, special);
            if (v.SpecialAccepted == null)
            {
                RestaurantGoodButton("rplan/special/yes", new Rect(14, 116, 142, 40), "Accept", () => v.SpecialAccepted = true, special);
                coastalUi.Secondary("rplan/special/no", new Rect(14, 162, 142, 40), "Not tonight", () => v.SpecialAccepted = false, "v2-icon-cross", true, special);
            }
            else coastalUi.Text("rplan/special/state", new Rect(10, 116, 150, 86), v.SpecialAccepted == true ? $"Accepted\n{v.SpecialReward}" : "Not tonight.",
                Skin.Type.Heading, v.SpecialAccepted == true ? Skin.GoodInk : Skin.InkSoft, TextAnchor.MiddleCenter, special);
            coastalUi.Primary("rplan/go", new Rect(672, 298, 162, 56), "Got it", () => RestaurantPreview = RestaurantScreen.None, "v2-icon-tick", true, f);
        }

        // A navy kit square with a glyph, used for the mockups' blue minus buttons.
        void RestaurantInkButton(string id, Rect r, string glyph, System.Action action, bool enabled, Transform parent)
        {
            var b = coastalUi.Sliced(id, r, "v2-btn-secondary", parent, Skin.Plank);
            coastalUi.Text(id + "/glyph", new Rect(0, 0, r.width, r.height), glyph, Skin.Type.Display, enabled ? Skin.Cream : Skin.InkSoft, TextAnchor.MiddleCenter, b);
            if (enabled) coastalUi.HitArea(id + "/hit", new Rect(0, 0, r.width, r.height), action, b);
        }

        // S4: what to prepare on the way home (ui-4-prep.png).
        void InterfaceRestaurantPrep(RestaurantPrepView v)
        {
            Block(new Rect(0, 0, iw, ih));
            RestaurantBackdrop("rprep/backdrop");
            float scale = Mathf.Min(iw / 844f, ih / 390f);
            coastalUi.Sliced("rprep/band", new Rect(0, 0, iw, (ih - 390 * scale) / 2 + 58 * scale), "v2-pill-navy", null, Skin.HeaderNavy);
            var f = RestaurantFrame("rprep/frame");
            coastalUi.IconButton("rprep/back", new Rect(12, 8, 52, 44), "v2-icon-back", null, () => RestaurantPreview = RestaurantScreen.None, f);
            coastalUi.Icon("rprep/sign", new Rect(230, 4, 62, 50), "v2-sign-fish", f, null, "v2-icon-fish");
            coastalUi.Text("rprep/title", new Rect(296, 4, 320, 50), "Prepare for tonight", Skin.Type.Display, Skin.Cream, TextAnchor.MiddleLeft, f, true);
            var fridge = coastalUi.Card("rprep/fridge", new Rect(628, 8, 152, 44), Skin.Card.Soft, f);
            coastalUi.Icon("rprep/fridge/icon", new Rect(10, 4, 46, 36), "v2-icon-fridge", fridge, null, "icon-cooler");
            coastalUi.Text("rprep/fridge/n", new Rect(62, 0, 84, 44), $"{v.Fridge} / {v.FridgeCapacity}", Skin.Type.Heading,
                v.Fridge > v.FridgeCapacity ? Skin.BadInk : Skin.Ink, TextAnchor.MiddleCenter, fridge);

            var left = coastalUi.Slab("rprep/catch", new Rect(70, 64, 268, 248), "Today's catch", false, f);
            for (int i = 0; i < v.Catch.Count && i < 2; i++)
            {
                var c = v.Catch[i];
                var card = coastalUi.Card($"rprep/catch/{i}", new Rect(14, 54 + i * 94, 240, 86), Skin.Card.Soft, left);
                coastalUi.Icon($"rprep/catch/{i}/art", new Rect(6, 10, 126, 66), c.Art, card, null, "v2-icon-fish");
                coastalUi.Text($"rprep/catch/{i}/name", new Rect(138, 12, 100, 26), c.Name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, card);
                coastalUi.Text($"rprep/catch/{i}/n", new Rect(138, 38, 100, 34), c.Amount, Skin.Type.Number, Skin.Ink, TextAnchor.MiddleLeft, card);
            }

            var right = coastalUi.Slab("rprep/portions", new Rect(346, 64, 460, 252), "Portions", false, f);
            for (int i = 0; i < v.Rows.Count && i < 3; i++)
            {
                var r = v.Rows[i]; int k = i; float y = 50 + i * 58;
                var row = coastalUi.Card($"rprep/row/{i}", new Rect(10, y, 440, 54), Skin.Card.Soft, right);
                coastalUi.Icon($"rprep/row/{i}/art", new Rect(8, 4, 80, 46), r.Art, row, null, r.Fallback);
                coastalUi.Text($"rprep/row/{i}/name", new Rect(98, 0, 120, 54), r.Name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, row);
                RestaurantInkButton($"rprep/row/{i}/minus", new Rect(214, 6, 48, 42), "-", () => v.Rows[k].Portions = Mathf.Max(0, v.Rows[k].Portions - 1), r.Portions > 0, row);
                coastalUi.Inset($"rprep/row/{i}/box", new Rect(270, 4, 98, 30), row);
                coastalUi.Text($"rprep/row/{i}/n", new Rect(270, 4, 98, 30), r.Portions.ToString(), Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, row);
                // Forecast track: the range in teal, the chosen amount as an amber marker.
                int hi = Mathf.Max(r.ForecastHigh + 4, r.Portions + 1);
                coastalUi.ProgressBar($"rprep/row/{i}/track", new Rect(274, 38, 90, 8), 0, Skin.Bar.Good, row);
                coastalUi.Sliced($"rprep/row/{i}/range", new Rect(274 + 90f * r.ForecastLow / hi, 38, Mathf.Max(6, 90f * (r.ForecastHigh - r.ForecastLow) / hi), 8), "v2-bar-good", row, Skin.Teal);
                coastalUi.Sliced($"rprep/row/{i}/mark", new Rect(274 + 90f * r.Portions / hi - 4, 34, 8, 16), "v2-bar-warn", row);
                coastalUi.Primary($"rprep/row/{i}/plus", new Rect(380, 6, 48, 42), "+", () => v.Rows[k].Portions++, null, true, row);
            }
            coastalUi.Icon("rprep/margin/icon", new Rect(74, 222, 20, 20), "v2-icon-ops", right, Skin.Ink);
            coastalUi.Text("rprep/margin/label", new Rect(98, 218, 84, 28), "Forecast", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, right);
            string[] margins = { "Tight", "+10%", "+20%" };
            coastalUi.PageSwitch("rprep/margin", new Rect(184, 218, 240, 28), margins, v.Margin, i => v.Margin = i, null, right);

            var sum = coastalUi.Card("rprep/sum", new Rect(200, 322, 418, 60), Skin.Card.Soft, f);
            coastalUi.Icon("rprep/sum/rest/icon", new Rect(14, 14, 32, 32), "v2-icon-cutlery", sum, Skin.Ink, "icon-food");
            coastalUi.Text("rprep/sum/rest/l", new Rect(52, 8, 100, 20), "Restaurant:", Skin.Type.Caption, Skin.Ink, TextAnchor.MiddleLeft, sum);
            coastalUi.Text("rprep/sum/rest", new Rect(52, 26, 100, 26), $"{v.RestaurantPortions} portions", Skin.Type.Body, Skin.Ink, TextAnchor.MiddleLeft, sum);
            coastalUi.Sliced("rprep/sum/split1", new Rect(156, 10, 2, 40), "v2-bar-track", sum, Skin.CreamDeep);
            coastalUi.Icon("rprep/sum/market/icon", new Rect(166, 14, 44, 32), "v2-icon-fish", sum, null, "icon-fish");
            coastalUi.Text("rprep/sum/market/l", new Rect(214, 8, 70, 20), "Market:", Skin.Type.Caption, Skin.Ink, TextAnchor.MiddleLeft, sum);
            coastalUi.Text("rprep/sum/market", new Rect(214, 26, 74, 26), $"{v.MarketFish} fish", Skin.Type.Body, Skin.Ink, TextAnchor.MiddleLeft, sum);
            coastalUi.Sliced("rprep/sum/split2", new Rect(288, 10, 2, 40), "v2-bar-track", sum, Skin.CreamDeep);
            coastalUi.Toggle("rprep/sum/cut", new Rect(298, 17, 26, 26), v.CaptainsCut, () => v.CaptainsCut = !v.CaptainsCut, sum);
            coastalUi.Text("rprep/sum/cut/label", new Rect(346, 0, 70, 60), "Captain's cut", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, sum);
            coastalUi.Primary("rprep/go", new Rect(632, 324, 198, 56), "Prepare", () => RestaurantPreview = RestaurantScreen.None, "v2-icon-cloche", true, f);
        }

        // S5: the closing card after service (ui-5-closing.png).
        void InterfaceRestaurantClosing(RestaurantClosingView v)
        {
            Block(new Rect(0, 0, iw, ih));
            RestaurantBackdrop("rclose/backdrop");
            var f = RestaurantFrame("rclose/frame");
            var slab = coastalUi.Slab("rclose/slab", new Rect(120, 12, 604, 360), null, false, f);
            coastalUi.Sliced("rclose/head", new Rect(0, 0, 604, 46), "v2-slab-header", slab, Skin.HeaderNavy);
            coastalUi.Text("rclose/title", new Rect(0, 0, 590, 46), "A good night on the quay", Skin.Type.Display, Skin.Cream, TextAnchor.MiddleCenter, slab, true);
            coastalUi.Icon("rclose/moon", new Rect(500, 10, 26, 26), "v2-icon-moon", slab, Skin.Warn);

            // Column 1: the till.
            var served = coastalUi.Card("rclose/served", new Rect(10, 54, 190, 32), Skin.Card.Soft, slab);
            coastalUi.Icon("rclose/served/icon", new Rect(20, 4, 24, 24), "v2-icon-guests", served, Skin.Ink, "v2-icon-crew");
            coastalUi.Text("rclose/served/text", new Rect(52, 0, 136, 32), $"{v.Served} served · {v.Left} left", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, served);
            void Line(string id, float y, string icon, string fallback, string label, int value)
            {
                var c = coastalUi.Card(id, new Rect(10, y, 190, 46), Skin.Card.Soft, slab);
                coastalUi.Icon(id + "/icon", new Rect(6, 4, 60, 38), icon, c, null, fallback);
                coastalUi.Text(id + "/label", new Rect(76, 2, 110, 20), label, Skin.Type.Small, Skin.Ink, TextAnchor.LowerLeft, c);
                coastalUi.Text(id + "/n", new Rect(76, 20, 110, 24), value.ToString(), Skin.Type.Heading, Skin.Ink, TextAnchor.UpperLeft, c);
            }
            Line("rclose/dishes", 90, "v2-dish-grilled-fish", "icon-food", "Dishes", v.Dishes);
            Line("rclose/drinks", 140, "v2-icon-drink", "v2-icon-clock", "Drinks", v.Drinks);
            Line("rclose/tips", 190, "v2-icon-coins", "icon-coin", "Tips", v.Tips);
            var total = coastalUi.Card("rclose/total", new Rect(10, 240, 190, 50), Skin.Card.Selected, slab);
            coastalUi.Icon("rclose/total/icon", new Rect(10, 4, 42, 42), "v2-icon-coin", total, null, "icon-coin");
            coastalUi.Text("rclose/total/label", new Rect(76, 2, 110, 18), "Tonight", Skin.Type.Small, Skin.Ink, TextAnchor.LowerLeft, total);
            coastalUi.Text("rclose/total/n", new Rect(76, 18, 110, 30), $"+{v.Total}", Skin.Type.Number, Skin.Ink, TextAnchor.UpperLeft, total);
            var cats = coastalUi.Card("rclose/cats", new Rect(10, 294, 190, 58), Skin.Card.Soft, slab);
            coastalUi.Icon("rclose/cats/art", new Rect(4, 2, 80, 54), "v2-illus-cats", cats, null, "v2-icon-cat");
            coastalUi.Text("rclose/cats/text", new Rect(88, 2, 98, 34), $"{v.CatPortions} portions for the alley cats", Skin.Type.Caption, Skin.Ink, TextAnchor.MiddleCenter, cats);
            coastalUi.Icon("rclose/cats/coin", new Rect(124, 36, 16, 16), "v2-icon-coin", cats, null, "icon-coin");
            coastalUi.Text("rclose/cats/value", new Rect(90, 34, 96, 20), $"Value       {v.CatValue}", Skin.Type.Caption, Skin.Ink, TextAnchor.MiddleLeft, cats);

            // Column 2: reviews and the crew of the night.
            for (int i = 0; i < v.Reviews.Count && i < 3; i++)
            {
                var r = v.Reviews[i];
                var c = coastalUi.Card($"rclose/review/{i}", new Rect(208, 54 + i * 76, 214, 72), Skin.Card.Soft, slab);
                coastalUi.Portrait($"rclose/review/{i}/face", new Rect(6, 6, 58, 58), r.Portrait, c);
                RestaurantStars($"rclose/review/{i}/stars", new Rect(70, 6, 96, 20), r.Stars, c);
                coastalUi.Text($"rclose/review/{i}/quote", new Rect(70, 28, 140, 40), $"“{r.Quote}”", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, c);
            }
            var crew = coastalUi.Card("rclose/crew", new Rect(208, 284, 214, 68), Skin.Card.Soft, slab);
            coastalUi.Portrait("rclose/crew/face", new Rect(6, 4, 60, 60), v.CrewPortrait, crew);
            coastalUi.Text("rclose/crew/label", new Rect(72, 6, 136, 22), "Crew of the night", Skin.Type.Caption, Skin.Ink, TextAnchor.LowerLeft, crew);
            coastalUi.Text("rclose/crew/name", new Rect(72, 28, 136, 32), v.CrewOfTheNight, Skin.Type.Heading, Skin.Ink, TextAnchor.UpperLeft, crew);

            // Column 3: popularity; Mira and Sleep stand over the board's corner.
            var pop = coastalUi.Card("rclose/pop", new Rect(430, 54, 164, 160), Skin.Card.Soft, slab);
            coastalUi.Text("rclose/pop/title", new Rect(10, 4, 150, 28), "Popularity", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, pop);
            var pv = coastalUi.Card("rclose/pop/value", new Rect(8, 36, 148, 50), Skin.Card.Soft, pop);
            coastalUi.Icon("rclose/pop/star", new Rect(4, 6, 38, 38), "icon-star", pv);
            coastalUi.Text("rclose/pop/from", new Rect(44, 0, 64, 50), $"{v.PopularityFrom} →", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, pv);
            coastalUi.Text("rclose/pop/to", new Rect(104, 0, 44, 50), v.PopularityTo.ToString(), Skin.Type.Heading, v.PopularityTo >= v.PopularityFrom ? Skin.Orange : Skin.BadInk, TextAnchor.MiddleLeft, pv);
            coastalUi.ProgressBar("rclose/pop/bar", new Rect(10, 94, 132, 14), v.Popularity, v.Popularity >= v.PopularityBefore ? Skin.Bar.Good : Skin.Bar.Bad, pop);
            coastalUi.Icon("rclose/pop/barstar", new Rect(132, 88, 26, 26), "icon-star", pop);
            coastalUi.Text("rclose/pop/rep", new Rect(4, 112, 156, 20), "Harbour reputation", Skin.Type.Caption, Skin.Ink, TextAnchor.MiddleCenter, pop);
            coastalUi.Text("rclose/pop/delta", new Rect(4, 132, 156, 20), v.Popularity >= v.PopularityBefore ? "A warmer welcome" : "A quieter night",
                Skin.Type.Caption, Skin.InkSoft, TextAnchor.MiddleCenter, pop);
            coastalUi.Icon("rclose/mira", new Rect(596, 222, 136, 168), "mira-pose-wave", f, null, "art108-mira");
            var say = coastalUi.Card("rclose/say", new Rect(490, 262, 100, 50), Skin.Card.Soft, f);
            coastalUi.Text("rclose/say/text", new Rect(4, 2, 88, 46), v.MiraLine, Skin.Type.Small, Skin.Ink, TextAnchor.MiddleCenter, say);
            coastalUi.Primary("rclose/sleep", new Rect(532, 320, 184, 54), "Sleep", () => RestaurantPreview = RestaurantScreen.None, "v2-icon-bed", true, f);
        }
    }
}

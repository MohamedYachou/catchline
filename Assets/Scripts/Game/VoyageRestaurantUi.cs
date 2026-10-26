using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // The restaurant's own screens (docs/plans/RESTAURANT.md section 10), built to the accepted mockups in
    // Art/Source/Restaurant/concepts/ui-*.png. Each screen draws from a small view model so it can be shown with sample
    // numbers before the restaurant logic is wired in; art not delivered yet falls back to the nearest kit icon.
    public partial class VoyageGame
    {
        public enum RestaurantScreen { None, Plan, Prep, Closing, Service, Arrange }
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
            public RestaurantRailMode Rail = RestaurantRailMode.Scroll; // Mo 10-26 picked one card per person
            public int RailFirst;
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
            coastalUi.Sliced("rsvc/bar", new Rect(0, 0, iw, barH), "v3-topbar", null, Color.white, true);
            float bs = barH - 16 * sy;
            coastalUi.Secondary("rsvc/back", new Rect(24 * sx, (barH - bs) / 2, bs * 1.36f, bs), "", () => { if (RestaurantPhase == DayPhase.Service) v.Paused = !v.Paused; else RestaurantPreview = RestaurantScreen.None; }, "v2-icon-back");
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
                var a = coastalUi.Sliced("rsvc/alert", new Rect(10 * sx, 38 * sy + v.Stock.Count * rowH, st.width - 20 * sx, rowH * 1.1f), "v2-card-alert", stock, Color.white);
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
                coastalUi.Icon($"rsvc/staff/{i}/bust", new Rect(6 * sx, h - bust, bust * .9f, bust), $"v2-bust-{s.Portrait}", c, null, s.Portrait == "captain" ? "v2-portrait-captain" : $"v2-portrait-{s.Portrait}-deck");
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
            coastalUi.Sliced("rsph/bar", bar, "v3-topbar", null, Color.white, true);
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
                coastalUi.Icon($"rsph/staff/{n}/bust", new Rect(4 * sx, 0, 54 * sx, 62 * sy), $"v2-bust-{s.Portrait}", c, null, s.Portrait == "captain" ? "v2-portrait-captain" : $"v2-portrait-{s.Portrait}-deck");
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
                    // Mo's pick: one card per person in the mockup's style; the arrows page through a bigger crew.
                    float arrow = h * (phone ? .8f : .6f), cw = (phone ? 158 : 236) * rail.width / (phone ? 824f : 1368f);
                    float x0 = rail.x + pad + arrow + pad;
                    int fit = Mathf.Max(1, Mathf.FloorToInt((rail.width - (arrow + pad) * 2 - pad) / cw));
                    cw = (rail.width - (arrow + pad) * 2 - pad) / fit;
                    v.RailFirst = Mathf.Clamp(v.RailFirst, 0, Mathf.Max(0, v.Crew.Count - fit));
                    int first = v.RailFirst, before = first, after = Mathf.Max(0, v.Crew.Count - first - fit);
                    coastalUi.Secondary($"{id}/left", new Rect(rail.x + pad, rail.y + (rail.height - arrow) / 2, arrow, arrow), before > 0 ? $"‹{before}" : "‹",
                        () => v.RailFirst -= fit, null, before > 0);
                    for (int i = 0; i < fit && first + i < v.Crew.Count; i++)
                    {
                        var s = v.Crew[first + i]; string cid = $"{id}/card/{i}";
                        var c = coastalUi.Card(cid, new Rect(x0 + i * cw, rail.y + pad, cw - pad, h), Skin.Card.Soft);
                        float bust = h * 1.06f, bw = bust * .9f, ring = h * (phone ? .5f : .6f);
                        coastalUi.Icon($"{cid}/bust", new Rect(4, h - bust, bw, bust), $"v2-bust-{s.Portrait}", c, null, s.Portrait == "captain" ? "v2-portrait-captain" : $"v2-portrait-{s.Portrait}-deck");
                        float tw = cw - pad - bw - ring - 18;
                        coastalUi.Text($"{cid}/job", new Rect(bw + 6, 2, tw, h * .46f), s.Job, phone ? Skin.Type.Small : Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, c);
                        coastalUi.Icon($"{cid}/icon", new Rect(bw + 8, h * .5f, h * .4f, h * .4f), s.Icon, c, null, s.Fallback);
                        RestaurantRing($"{cid}/ring", new Rect(cw - pad - ring - 8, (h - ring) / 2, ring, ring), s.Busy, c);
                    }
                    coastalUi.Secondary($"{id}/right", new Rect(rail.xMax - pad - arrow, rail.y + (rail.height - arrow) / 2, arrow, arrow), after > 0 ? $"{after}›" : "›",
                        () => v.RailFirst += fit, null, after > 0);
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


        public sealed class RestaurantShopItem { public string Name, Art, Fallback, Footprint; public int Price; }
        public sealed class RestaurantArrangeView
        {
            public int Coins = 2450, Category = 1, Selected;
            public string[] Categories = { "Kitchen", "Guests", "Bar", "Decor", "Expand" };
            public string[] CategoryIcons = { "v2-icon-kitchen-pot", "v2-icon-chair", "v2-icon-bar-glass", "v2-icon-decor-plant", "v2-icon-expand" };
            public List<RestaurantShopItem> Items = new()
            {
                new() { Name = "Table for 2", Art = "v2-item-rest-table2", Fallback = "v2-icon-table", Footprint = "1×1", Price = 120 },
                new() { Name = "Table for 4", Art = "v2-item-rest-table4", Fallback = "v2-icon-table", Footprint = "2×1", Price = 220 },
                new() { Name = "Booth", Art = "v2-item-rest-booth", Fallback = "v2-icon-table", Footprint = "2×1", Price = 380 },
            };
            // The item being placed: its label and where its action bubble sits (screen fractions until the room is live).
            public string Placing = "Table for 2 · 1×1"; public Vector2 PlacingAt = new(.69f, .44f);
        }
        public RestaurantArrangeView RestaurantArrange = new();

        // S1: arrange mode over the room (ui-1-arrange.png): top bar, the placing bubble, the shop tray.
        void InterfaceRestaurantArrange(RestaurantArrangeView v)
        {
            float k = Mathf.Min(iw / 844f, ih / 390f);
            Rect L(float x, float y, float w, float h) => new(x * k, y * k, w * k, h * k);                 // top-left anchored
            Rect TR(float x, float y, float w, float h) => new(iw - (844 - x) * k, y * k, w * k, h * k);    // top-right
            Rect BL(float x, float y, float w, float h) => new(x * k, ih - (390 - y) * k, w * k, h * k);   // bottom-left
            Rect BR(float x, float y, float w, float h) => new(iw - (844 - x) * k, ih - (390 - y) * k, w * k, h * k);

            coastalUi.Sliced("rarr/bar", new Rect(0, 0, iw, 42 * k), "v3-topbar", null, Color.white, true);
            coastalUi.IconButton("rarr/back", L(22, 5, 56, 32), "v2-icon-back", null, () => RestaurantPreview = RestaurantScreen.None);
            coastalUi.Icon("rarr/icon", L(94, 8, 24, 26), "v2-icon-chair", null, Skin.Cream);
            coastalUi.Text("rarr/title", L(124, 0, 200, 42), "Arrange", Skin.Type.Display, Skin.Cream, TextAnchor.MiddleLeft, null, true);
            var coins = coastalUi.Card("rarr/coins", TR(602, 5, 98, 32), Skin.Card.Soft);
            coastalUi.Icon("rarr/coins/icon", new Rect(6 * k, 4 * k, 24 * k, 24 * k), "v2-icon-coin", coins, null, "icon-coin");
            coastalUi.Text("rarr/coins/n", new Rect(32 * k, 0, 62 * k, 32 * k), v.Coins.ToString("N0"), Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, coins);
            coastalUi.Secondary("rarr/undo", TR(736, 5, 88, 32), "Undo", () => { }, "v2-icon-undo");

            // The placing bubble: rotate, cancel, confirm, and the item's name and footprint.
            if (v.Placing != null)
            {
                float bx = v.PlacingAt.x * iw, by = v.PlacingAt.y * ih, b = 44 * k;
                coastalUi.HitArea("rarr/rotate", new Rect(bx - b * 1.6f, by - b, b, b), () => { });
                coastalUi.Icon("rarr/rotate/art", new Rect(bx - b * 1.6f, by - b, b, b), "v2-btn-rotate", null, null, "v2-icon-cycle");
                coastalUi.HitArea("rarr/cancel", new Rect(bx - b * .5f, by - b, b, b), () => v.Placing = null);
                coastalUi.Icon("rarr/cancel/art", new Rect(bx - b * .5f, by - b, b, b), "v2-btn-cancel", null, null, "v2-icon-warning");
                coastalUi.HitArea("rarr/confirm", new Rect(bx + b * .6f, by - b, b, b), () => v.Placing = null);
                coastalUi.Icon("rarr/confirm/art", new Rect(bx + b * .6f, by - b, b, b), "v2-btn-confirm", null, null, "v2-icon-tick");
                var tag = coastalUi.Card("rarr/tag", new Rect(bx + b * 1.8f, by - b * 1.4f, 170 * k, 36 * k), Skin.Card.Soft);
                coastalUi.Icon("rarr/tag/art", new Rect(6 * k, 3 * k, 34 * k, 30 * k), v.Items[v.Selected].Art, tag, null, v.Items[v.Selected].Fallback);
                coastalUi.Text("rarr/tag/text", new Rect(44 * k, 0, 122 * k, 36 * k), v.Placing, Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, tag);
            }

            // The shop tray: categories on the left, this category's items on the right.
            coastalUi.Sliced("rarr/tray", new Rect(0, ih - 92 * k, iw, 92 * k), "v2-slab", null, Skin.Paper, true);
            for (int i = 0; i < v.Categories.Length; i++)
            {
                int c = i; bool on = v.Category == i; var r = BL(16 + i * 66, 306, 60, 70);
                var t = on ? coastalUi.Sliced($"rarr/cat/{i}", r, "v2-btn-primary", null, Color.white) : coastalUi.Card($"rarr/cat/{i}", r, Skin.Card.Soft);
                coastalUi.Icon($"rarr/cat/{i}/icon", new Rect(16 * k, 8 * k, 28 * k, 30 * k), v.CategoryIcons[i], t, on ? Skin.Cream : null);
                coastalUi.Text($"rarr/cat/{i}/label", new Rect(0, 42 * k, 60 * k, 24 * k), v.Categories[i], Skin.Type.Small, on ? Skin.Cream : Skin.Ink, TextAnchor.MiddleCenter, t, on);
                coastalUi.HitArea($"rarr/cat/{i}/hit", new Rect(0, 0, r.width, r.height), () => v.Category = c, t);
            }
            float[] cardX = { 350, 507, 664 }, cardW = { 150, 150, 164 };
            for (int i = 0; i < v.Items.Count && i < 3; i++)
            {
                int s = i; var it = v.Items[i]; bool on = v.Selected == i; var r = BR(cardX[i], 306, cardW[i], 72);
                if (on) coastalUi.Sliced($"rarr/item/{i}/glow", new Rect(r.x - 3 * k, r.y - 3 * k, r.width + 6 * k, r.height + 6 * k), "v2-btn-primary", null, Color.white);
                var c = coastalUi.Card($"rarr/item/{i}", r, Skin.Card.Soft);
                float w = r.width / k;
                coastalUi.Icon($"rarr/item/{i}/art", new Rect(4 * k, 4 * k, (w * .48f) * k, 64 * k), it.Art, c, null, it.Fallback);
                coastalUi.Text($"rarr/item/{i}/name", new Rect(w * .5f * k, 4 * k, w * .5f * k, 22 * k), it.Name, Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, c);
                coastalUi.Icon($"rarr/item/{i}/coin", new Rect(w * .5f * k, 28 * k, 18 * k, 18 * k), "v2-icon-coin", c, null, "icon-coin");
                coastalUi.Text($"rarr/item/{i}/price", new Rect((w * .5f + 22) * k, 24 * k, 60 * k, 26 * k), it.Price.ToString(), Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, c);
                coastalUi.Text($"rarr/item/{i}/size", new Rect((w * .5f + 22) * k, 48 * k, 60 * k, 20 * k), it.Footprint, Skin.Type.Caption, Skin.InkSoft, TextAnchor.MiddleLeft, c);
                coastalUi.HitArea($"rarr/item/{i}/hit", new Rect(0, 0, r.width, r.height), () => { v.Selected = s; v.Placing = $"{v.Items[s].Name} · {v.Items[s].Footprint}"; }, c);
            }
        }

        // Returns true when a restaurant screen took the frame.
        Font restaurantDisplay, restaurantBody;

        bool InterfaceRestaurant()
        {
            if (RestaurantPreview == RestaurantScreen.None) return false;
            // The restaurant draws in the mockups' kit and rounded face; the rest of the game keeps v2 for now (TODO.md).
            coastalUi.Kit = "v3-";
            coastalUi.DisplayOverride = restaurantDisplay ??= Resources.Load<Font>("Fonts/Fredoka-Bold");
            coastalUi.BodyOverride = restaurantBody ??= Resources.Load<Font>("Fonts/Fredoka-SemiBold");
            try
            {
                switch (RestaurantPreview)
                {
                    case RestaurantScreen.Plan: InterfaceRestaurantPlan(RestaurantPlan); break;
                    case RestaurantScreen.Prep: InterfaceRestaurantPrep(RestaurantPrep); break;
                    case RestaurantScreen.Closing: InterfaceRestaurantClosing(RestaurantClosing); break;
                    case RestaurantScreen.Service: InterfaceRestaurantService(RestaurantService); break;
                    case RestaurantScreen.Arrange: InterfaceRestaurantArrange(RestaurantArrange); break;
                }
            }
            finally { coastalUi.Kit = null; coastalUi.DisplayOverride = coastalUi.BodyOverride = null; }
            return true;
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
            frameScale = k;
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

        // ---- 1:1 mockup pieces (Codex's RESTAURANT-UI-EXACT-1, RestaurantExact.cs) ----------------------------------
        float frameScale = 1;

        // A measured piece at its mockup rect (or at a given rect in the same frame).
        RectTransform Rx(string id, int screen, string piece, Transform parent, Rect? at = null, string sprite = null)
        {
            if (!RestaurantExact.Pieces.TryGetValue($"{screen}:{piece}", out var p)) p = (at ?? default, Vector2.zero, Vector4.zero);
            var r = at ?? p.rect;
            // Repeated instances ("name#use") share the measured base piece's source size and borders.
            if (p.size == Vector2.zero && piece.Contains("#") && RestaurantExact.Pieces.TryGetValue($"{screen}:{piece.Split('#')[0]}", out var b))
                p = (p.rect, b.size * (p.rect.width > 0 ? 1 : 0), b.border);
            const float perUnit = 3; // every exact piece is cut at 3x the 844x390 layout
            string name = sprite ?? "rx-" + piece.Split('#')[0].Substring(3);
            return coastalUi.Piece(id, r, name, parent, p.border, perUnit);
        }

        // Text in a measured mockup style, at its measured rect or a given one.
        void RxText(string id, int screen, string style, string text, Transform parent, Rect? at = null, TextAnchor align = TextAnchor.MiddleCenter, Color? fill = null)
        {
            var s = RestaurantExact.Texts[$"{screen}:{style}"];
            coastalUi.StyledText(id, at ?? s.Rect, text, s.Size, fill ?? s.Fill, s.StrokeColour, s.Stroke, s.ShadowY, s.Shadow, s.Bold, align, parent, frameScale);
        }

        static string FishPicture(string art) => art != null && art.StartsWith("fish-") ? "rx-fishart-" + art.Substring(5) : art;

        // S3: Mira's plan card on the way out (ui-3-mira-plan.png), every piece and text at its measured place.
        void InterfaceRestaurantPlan(RestaurantPlanView v)
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rplan/planks", false);
            var f = RestaurantFrame("rplan/frame");
            Rx("rplan/bg", 3, "v2-bg-plan", f);
            // As in the mockup: big, cut at mid-thigh by the frame's bottom edge.
            var miraClip = coastalUi.Clip("rplan/mira/clip", new Rect(0, 0, 300, 390), f);
            Rx("rplan/mira", 3, "v2-mira-plan", miraClip, new Rect(-78, 10 + Mathf.Sin(SimTime * 1.6f) * 1.5f, 434, 543));

            Rx("rplan/back", 3, "v2-btn-back", f);
            Rx("rplan/back/icon", 3, "v2-icon-back", f);
            RxText("rplan/back/label", 3, "back", "Back", f, null, TextAnchor.MiddleLeft);
            coastalUi.HitArea("rplan/back/hit", new Rect(12, 8, 130, 51), () => { if (RestaurantPhase == DayPhase.Plan) RestaurantPhase = DayPhase.Off; RestaurantPreview = RestaurantScreen.None; }, f);

            Rx("rplan/sign", 3, "v2-sign-plank", f);
            RxText("rplan/title", 3, "title-wood", "Tonight at Mira's", f);

            Rx("rplan/paper", 3, "v2-plan-paper", f);
            Rx("rplan/cal", 3, "v2-icon-calendar", f);
            RxText("rplan/day", 3, "date", $"{v.Day.ToUpperInvariant()} · {v.Hours}", f, null, TextAnchor.MiddleLeft);
            RxText("rplan/guests", 3, "forecast-guests", $"{v.GuestsLow} – {v.GuestsHigh} guests + walk-ins", f, null, TextAnchor.MiddleLeft);
            float[] cardX = { 275, 402, 529 };
            for (int i = 0; i < v.Dishes.Count && i < 3; i++)
            {
                var d = v.Dishes[i]; float x = cardX[i];
                Rx($"rplan/dish/{i}", 3, "v2-plan-dish-card", f, new Rect(x, 162, 122, 123));
                coastalUi.Icon($"rplan/dish/{i}/art", new Rect(x + 6, 166, 110, 75), d.Art, f, null, d.Fallback);
                RxText($"rplan/dish/{i}/name", 3, "dish-label", d.Name, f, new Rect(x, 235, 122, 22));
                Rx($"rplan/dish/{i}/who", 3, "v2-icon-guests", f, new Rect(x + 26, 257, 21, 20));
                RxText($"rplan/dish/{i}/range", 3, "dish-guests", $"{d.Low} – {d.High}", f, new Rect(x + 50, 258, 66, 22), TextAnchor.MiddleLeft);
            }
            Rx("rplan/bring", 3, "v2-paper-row#bring-back inset", f, null, "rx-paper-row");
            Rx("rplan/bring/pile", 3, "v2-catch-pile", f);
            RxText("rplan/bring/title", 3, "bring-back-heading", "Bring back:", f, null, TextAnchor.MiddleLeft);
            for (int i = 0; i < v.BringBack.Count && i < 2; i++)
            {
                var fish = v.BringBack[i]; float x = i == 0 ? 399 : 520;
                coastalUi.Icon($"rplan/bring/{i}/icon", new Rect(x, 321, 32, 20), FishPicture(fish.Art), f, null, fish.Art);
                RxText($"rplan/bring/{i}/text", 3, "bring-back-items", $"{fish.Amount} {fish.Name}", f, new Rect(x + 35, 321, 110, 22), TextAnchor.MiddleLeft);
            }
            if (v.BringBack.Count > 1) Rx("rplan/bring/split", 3, "v2-divider#catch request separator", f, null, "rx-divider");

            Rx("rplan/special", 3, "v2-ticket", f);
            Rx("rplan/special/icon", 3, "v2-icon-special", f);
            RxText("rplan/special/head", 3, "special-heading", "Special request", f, null, TextAnchor.MiddleLeft);
            RxText("rplan/special/body", 3, "special-copy", v.SpecialTitle, f);
            if (v.SpecialReward != null && v.SpecialAccepted == null)
            {
                Rx("rplan/special/yes", 3, "v2-btn-accept", f);
                Rx("rplan/special/yes/icon", 3, "v2-icon-tick#accept button check; cream glyph", f, null, "rx-icon-tick");
                RxText("rplan/special/yes/label", 3, "accept", "Accept", f);
                coastalUi.HitArea("rplan/special/yes/hit", new Rect(681, 184, 139, 51), () => v.SpecialAccepted = true, f);
                Rx("rplan/special/no", 3, "v2-btn-secondary", f);
                Rx("rplan/special/no/icon", 3, "v2-icon-cross", f);
                RxText("rplan/special/no/label", 3, "not-tonight", "Not tonight", f);
                coastalUi.HitArea("rplan/special/no/hit", new Rect(679, 230, 140, 51), () => v.SpecialAccepted = false, f);
            }
            else if (v.SpecialReward != null)
                RxText("rplan/special/state", 3, "special-copy", v.SpecialAccepted == true ? $"Accepted  {v.SpecialReward}" : "Not tonight.", f, new Rect(688, 200, 133, 42));

            Rx("rplan/go", 3, "v2-btn-primary", f);
            Rx("rplan/go/icon", 3, "v2-icon-tick", f);
            RxText("rplan/go/label", 3, "got-it", "Got it", f);
            coastalUi.HitArea("rplan/go/hit", new Rect(668, 297, 165, 70), () => { if (RestaurantPhase == DayPhase.Plan) RestaurantPlanAccepted(); else RestaurantPreview = RestaurantScreen.None; }, f);
        }

        // A navy kit square with a glyph, used for the mockups' blue minus buttons.
        void RestaurantInkButton(string id, Rect r, string glyph, System.Action action, bool enabled, Transform parent)
        {
            var b = coastalUi.Sliced(id, r, "v2-btn-secondary", parent, Skin.Plank);
            coastalUi.Text(id + "/glyph", new Rect(0, 0, r.width, r.height), glyph, Skin.Type.Display, enabled ? Skin.Cream : Skin.InkSoft, TextAnchor.MiddleCenter, b);
            if (enabled) coastalUi.HitArea(id + "/hit", new Rect(0, 0, r.width, r.height), action, b);
        }

        // S4: what to prepare on the way home (ui-4-prep.png), every piece and text at its measured place.
        void InterfaceRestaurantPrep(RestaurantPrepView v)
        {
            Block(new Rect(0, 0, iw, ih));
            RestaurantBackdrop("rprep/backdrop");
            float scale = Mathf.Min(iw / 844f, ih / 390f);
            coastalUi.Sliced("rprep/band", new Rect(0, 0, iw, (ih - 390 * scale) / 2 + 52 * scale), "v3-topbar", null, Color.white);
            var f = RestaurantFrame("rprep/frame");
            Rx("rprep/back", 4, "v2-btn-back#square back control; nine-slice", f, null, "rx-btn-back");
            Rx("rprep/back/icon", 4, "v2-icon-back#back arrow", f, null, "rx-icon-back");
            coastalUi.HitArea("rprep/back/hit", new Rect(13, 6, 53, 46), () => { if (RestaurantPhase != DayPhase.Prep) RestaurantPreview = RestaurantScreen.None; }, f);
            Rx("rprep/sign", 4, "v2-sign-fish", f);
            RxText("rprep/title", 4, "prep-title", "Prepare for tonight", f, null, TextAnchor.MiddleLeft);
            Rx("rprep/fridge", 4, "v2-number-field", f, new Rect(630, 8, 150, 42));
            Rx("rprep/fridge/icon", 4, "v2-icon-cooler", f);
            RxText("rprep/fridge/n", 4, "capacity", $"{v.Fridge} / {v.FridgeCapacity}", f, null, TextAnchor.MiddleCenter, v.Fridge > v.FridgeCapacity ? Skin.BadInk : null);

            Rx("rprep/catch", 4, "v2-prep-catch-panel", f);
            Rx("rprep/catch/icon", 4, "v2-icon-fish-white", f);
            RxText("rprep/catch/title", 4, "panel-heading", "Today's catch", f, new Rect(134, 71, 196, 31), TextAnchor.MiddleLeft);
            float[] catchY = { 118, 207 };
            for (int i = 0; i < v.Catch.Count && i < 2; i++)
            {
                var c = v.Catch[i]; float y = catchY[i];
                Rx($"rprep/catch/{i}", 4, i == 0 ? "v2-paper-row" : "v2-paper-row#second fish row", f, null, "rx-paper-row");
                coastalUi.Icon($"rprep/catch/{i}/art", new Rect(88, y + 12, 126, 64), FishPicture(c.Art), f, null, c.Art);
                RxText($"rprep/catch/{i}/name", 4, "catch-species", c.Name, f, new Rect(222, y + 16, 104, 22), TextAnchor.MiddleLeft);
                RxText($"rprep/catch/{i}/n", 4, "catch-count", c.Amount, f, new Rect(223, y + 38, 98, 32), TextAnchor.MiddleLeft);
            }

            Rx("rprep/portions", 4, "v2-prep-portions-panel", f);
            Rx("rprep/portions/icon", 4, "v2-icon-cutlery-white", f);
            RxText("rprep/portions/title", 4, "panel-heading", "Portions", f, new Rect(405, 71, 160, 31), TextAnchor.MiddleLeft);
            for (int i = 0; i < v.Rows.Count && i < 3; i++)
            {
                var r = v.Rows[i]; int k = i; float y = 112 + i * 57.5f;
                Rx($"rprep/row/{i}", 4, "v2-paper-row#portion row 1; slice to rect", f, new Rect(359, y, 435, 55), "rx-paper-row");
                coastalUi.Icon($"rprep/row/{i}/art", new Rect(363, y + 2, 91, 51), r.Art, f, null, r.Fallback);
                RxText($"rprep/row/{i}/name", 4, "portion-label", r.Name, f, new Rect(463, y + 16, 103, 22), TextAnchor.MiddleLeft);
                Rx($"rprep/row/{i}/minus", 4, "v2-btn-minus", f, new Rect(570, y, 52, 51));
                coastalUi.HitArea($"rprep/row/{i}/minus/hit", new Rect(570, y, 52, 51), () => v.Rows[k].Portions = Mathf.Max(0, v.Rows[k].Portions - 1), f);
                Rx($"rprep/row/{i}/box", 4, "v2-number-field", f, new Rect(629, y, 99, 38));
                RxText($"rprep/row/{i}/n", 4, "portion-count", r.Portions.ToString(), f, new Rect(629, y + 2, 99, 34));
                // The forecast track under the number: the knob sits at the chosen amount within the forecast range.
                Rx($"rprep/row/{i}/track", 4, "v2-bar-track", f, new Rect(628, y + 38, 102, 14));
                int hi = Mathf.Max(r.ForecastHigh + 4, r.Portions + 1);
                Rx($"rprep/row/{i}/knob", 4, "v2-bar-knob", f, new Rect(628 + 96f * Mathf.Clamp01(r.Portions / (float)hi), y + 36, 12, 18));
                Rx($"rprep/row/{i}/plus", 4, "v2-btn-plus", f, new Rect(734, y - 1, 57, 52));
                coastalUi.HitArea($"rprep/row/{i}/plus/hit", new Rect(734, y - 1, 57, 52), () => v.Rows[k].Portions++, f);
            }
            Rx("rprep/margin/icon", 4, "v2-icon-forecast", f);
            RxText("rprep/margin/label", 4, "forecast-label", "Forecast", f, null, TextAnchor.MiddleLeft);
            string[] margins = { "Tight", "+10%", "+20%" };
            float[] marginX = { 529, 611, 692 };
            var pill = RestaurantExact.Texts["4:forecast-pill"];
            for (int i = 0; i < 3; i++)
            {
                int m = i; bool on = v.Margin == i; var r = new Rect(marginX[i], 285, 80, 30);
                Rx($"rprep/margin/{i}", 4, on ? "v2-toggle-selected" : "v2-toggle-unselected", f, r);
                coastalUi.StyledText($"rprep/margin/{i}/label", r, margins[i], pill.Size, on ? new Color(1, .973f, .91f) : pill.Fill, pill.StrokeColour, 0, 0, Color.clear, true, TextAnchor.MiddleCenter, f, frameScale);
                coastalUi.HitArea($"rprep/margin/{i}/hit", r, () => v.Margin = m, f);
            }

            Rx("rprep/sum", 4, "v2-summary-strip", f);
            Rx("rprep/sum/rest/icon", 4, "v2-icon-cutlery", f);
            RxText("rprep/sum/rest/l", 4, "summary-label", "Restaurant:", f, new Rect(252, 334, 100, 14), TextAnchor.MiddleLeft);
            RxText("rprep/sum/rest", 4, "summary-value", $"{v.RestaurantPortions} portions", f, new Rect(251, 349, 100, 20), TextAnchor.MiddleLeft);
            Rx("rprep/sum/split1", 4, "v2-divider", f);
            Rx("rprep/sum/market/icon", 4, "v2-icon-fish-market", f);
            RxText("rprep/sum/market/l", 4, "summary-label", "Market:", f, new Rect(414, 334, 60, 14), TextAnchor.MiddleLeft);
            RxText("rprep/sum/market", 4, "summary-value", $"{v.MarketFish} fish", f, new Rect(414, 349, 60, 20), TextAnchor.MiddleLeft);
            Rx("rprep/sum/split2", 4, "v2-divider#market/captain separator", f, null, "rx-divider");
            Rx("rprep/sum/cut", 4, v.CaptainsCut ? "v2-checkbox-on" : "v2-checkbox-off", f);
            coastalUi.HitArea("rprep/sum/cut/hit", new Rect(486, 326, 140, 50), () => v.CaptainsCut = !v.CaptainsCut, f);
            var cutStyle = RestaurantExact.Texts["4:summary-label"]; // the mockup sets it larger, on one line before the button
            coastalUi.StyledText("rprep/sum/cut/label", new Rect(532, 338, 96, 26), "Captain's cut", 13, cutStyle.Fill, cutStyle.StrokeColour, cutStyle.Stroke, cutStyle.ShadowY, cutStyle.Shadow, cutStyle.Bold, TextAnchor.MiddleLeft, f, frameScale);
            Rx("rprep/go", 4, "v2-btn-primary#Prepare button; nine-slice", f, null, "rx-btn-primary");
            Rx("rprep/go/icon", 4, "v2-icon-cloche", f);
            RxText("rprep/go/label", 4, "prepare", "Prepare", f);
            coastalUi.HitArea("rprep/go/hit", new Rect(631, 322, 200, 58), () => { if (RestaurantPhase == DayPhase.Prep) RestaurantPrepared(); else RestaurantPreview = RestaurantScreen.None; }, f);
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
            coastalUi.Primary("rclose/sleep", new Rect(532, 320, 184, 54), "Sleep", () => { if (RestaurantPhase == DayPhase.Closing) RestaurantSleep(); else RestaurantPreview = RestaurantScreen.None; }, "v2-icon-bed", true, f);
        }
    }
}

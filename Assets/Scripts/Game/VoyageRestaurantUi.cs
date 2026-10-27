using System.Collections.Generic;
using System.Linq;
using Catchline.Game.Restaurant;
using SimStaff = Catchline.Game.Restaurant.RestaurantStaff;
using UnityEngine;

namespace Catchline.Game
{
    // The restaurant's own screens (docs/plans/RESTAURANT.md section 10), built to the accepted mockups in
    // Art/Source/Restaurant/concepts/ui-*.png. Each screen draws from a small view model so it can be shown with sample
    // numbers before the restaurant logic is wired in; art not delivered yet falls back to the nearest kit icon.
    public partial class VoyageGame
    {
        public enum RestaurantScreen { None, Plan, Prep, Closing, Service, Arrange, Sleep, Dashboard, Market, Upgrades, Crew, StageUp, FirstNight, Week }
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
            public string ReservationName = "Ada", ReservationFace = "v2-guest-ada", ReservationDish = "Grilled fish", ReservationDishArt = "v2-dish-grilled-fish";
            public int ReservationParty = 4;
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

        // S12: the card between closing and the next morning.
        public sealed class RestaurantSleepView
        {
            public int Net = 564, Popularity = 4, TomorrowWeather = (int)Weather.Sun; // the mockup's sample: sun, clear skies
            public string Tomorrow = "Saturday · Clear skies", Booking = "Expect a lively terrace";
        }
        public RestaurantSleepView RestaurantSleepCard = new();

        // S16: the week report after the seventh night (sample = Codex 1's illustrative values).
        public sealed class RestaurantWeekView
        {
            public int[] Nights = { 280, 360, 320, 410, 450, 560, 460 };
            public string Days = "MTWTFSS";
            public string Dish = "Grilled fish", DishArt = "v2-dish-grilled-fish", Crew = "Jo", CrewId = "jo", Quote = "Always one step ahead.";
            public int DishCount = 48, PopularityFrom = 40, PopularityTo = 46;
        }
        public RestaurantWeekView RestaurantWeek = new();

        // S7: the morning market after prep.
        public sealed class RestaurantMarketRow { public Species Species; public string Name, Art; public float Kg; public int Value; public bool Keep; }
        public sealed class RestaurantMarketView
        {
            public List<RestaurantMarketRow> Rows = new()
            {
                new() { Species = Species.Mackerel, Name = "Mackerel", Art = "fish-mackerel", Kg = 2.4f, Value = 28 },
                new() { Species = Species.Pollock, Name = "Pollock", Art = "fish-pollock", Kg = 3f, Value = 54 },
                new() { Species = Species.Plaice, Name = "Plaice", Art = "fish-plaice", Kg = 1f, Value = 16 },
            };
            public int Wallet = 2840, Room = 4; public string Mood = "keen", Demand = "Good demand today.";
        }
        public RestaurantMarketView RestaurantMarket = new();

        // S6 / S8: the next stage, shared by the dashboard strip and the upgrades shop.
        public sealed class RestaurantStageCard { public int Current = 1, Next = 2, Stars = 3, Cost = 3500, Have = 2840; public bool StarsMet = true; public string Name = "Bistro", Pitch = "More tables and a terrace"; }
        public sealed class RestaurantDashboardView
        {
            public int Week = 2, Income = 2840, Dishes = 2160, Drinks = 480, Tips = 200, Popularity = 3, PopularityChange = 1;
            public int[] DayIncome = { 260, 380, 460, 330, 450, 640, 410 };
            public int[] DayPopularity = { 18, 19, 21, 21, 23, 26, 27 }; // after each night, -1 = closed
            public string IncomeChange = "+18% last week";
            public List<(Dish dish, int sold)> Menu = new() { (Dish.GrilledFish, 48), (Dish.Soup, 32), (Dish.Coffee, 40) };
            public RestaurantStageCard Stage = new();
        }
        public RestaurantDashboardView RestaurantDashboard = new();
        public RestaurantStageCard RestaurantShopStage = new();

        // S11: a new stage opened.
        public sealed class RestaurantStageUpView { public int Stage = 2; public string From = "Cafe", To = "Bistro", Reward = "Terrace unlocked!"; public string[] Unlocks = { "More dining room", "A bigger kitchen", "Quayside tables" }; }
        public RestaurantStageUpView RestaurantStageUp = new();

        public sealed class RestaurantClosingView
        {
            public int Served = 22, Left = 2, Dishes = 420, Drinks = 96, Tips = 48, CatPortions = 3, CatValue = 18;
            public int Stars = 3, PopularityFrom = 42, PopularityTo = 46; public float Popularity = .82f, PopularityBefore = .74f;
            public string CrewOfTheNight = "Jo", CrewPortrait = "deckhand";
            public string MiraLine = "Same time tomorrow?", Title = "A good night on the quay";
            public bool BestNight = true, FullHouse = true;
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

        // S2 on a desktop: the service HUD over the 3D room (ui-service-desktop.png), in the mockup's own 1440x900 frame.
        void InterfaceRestaurantService(RestaurantServiceView v)
        {
            // The room under the HUD takes the manager's taps (drawn first, so every HUD piece sits above it).
            if (night != null && restaurantWorld != null && restaurantWorld.Sim == night) { coastalUi.HitArea("rsvc/room", new Rect(0, 0, iw, ih), ServiceTap); ServiceMarkers(); }
            if (compactInterface) { InterfaceRestaurantServicePhone(v); return; }
            float k = Mathf.Min(iw / 1440f, ih / 900f);
            var f = coastalUi.Sliced("rsvc/frame", new Rect((iw - 1440 * k) / 2, (ih - 900 * k) / 2, 1440, 900), "");
            f.localScale = new Vector3(k, k, 1); frameScale = k;
            float ox = (iw - 1440 * k) / 2 / k, oy = (ih - 900 * k) / 2 / k;
            // With Codex 1's Close door the title shortens and the timeline moves left (s2-call headerReflow: 545 -> 467).
            bool door = HasUi("rx-s2-close-door-button");
            RectTransform D(string id, string key, Rect? at = null, string sprite = null, Transform into = null) =>
                Rx(id, "desktop", key, into ?? f, at ?? RestaurantExact.Pieces["desktop:" + key].rect, sprite ?? "rx-" + key.Split('#')[0].Substring(3));
            void T(string id, string style, string text, Rect? at = null, TextAnchor align = TextAnchor.MiddleLeft, Color? fill = null, Transform into = null) =>
                RxText(id, "desktop", style, text, into ?? f, at, align, fill);
            var cream = new Color(1, .973f, .92f);

            D("rsvc/bar", "v2-bar-service#desktop-bar-service-01", new Rect(-ox, -oy, iw / k, 80 + oy));
            D("rsvc/back", "v2-btn-back#desktop-btn-back-01", null, "rx-s12-btn-back");
            coastalUi.HitArea("rsvc/back/hit", new Rect(21, 12, 73, 58), () => { if (RestaurantPhase != DayPhase.Service) RestaurantPreview = RestaurantScreen.None; }, f);
            if (door) T("rsvc/title", "service-title", $"{v.Name} · Service");
            else T("rsvc/title", "title", $"{v.Name} · Evening service", new Rect(114, 20, 430, 41));

            // The evening: 18:00-23:00 with the clock in a flag riding the curve (its holder made here, so it sits over the bar).
            var tl = coastalUi.Sliced("rsvc/tl", new Rect(door ? -78 : 0, 0, 1440, 900), "", f);
            D("rsvc/strip", "v2-timeline-track#desktop-timeline-track-01", null, null, tl);
            D("rsvc/strip/curve", "v2-timeline-curve-desktop#desktop-timeline-curve-desktop-01", null, null, tl);
            float t = Mathf.InverseLerp(v.Open, v.Close, v.Hour), nowX = 566 + 256 * t;
            D("rsvc/strip/dot", "v2-timeline-dot#desktop-timeline-dot-01", new Rect(nowX - 7.5f, 30, 15, 15), null, tl);
            D("rsvc/strip/flag", "v2-timeline-flag#desktop-timeline-flag-01", new Rect(nowX - 28, 3, 56, 31), null, tl);
            int hh = Mathf.FloorToInt(v.Hour), mm = Mathf.FloorToInt((v.Hour - hh) * 60);
            T("rsvc/strip/clock", "clock", $"{hh}:{mm:00}", new Rect(nowX - 28, 6, 56, 21), TextAnchor.MiddleCenter, null, tl);
            T("rsvc/strip/l0", "timeline-label-1", "18:00", new Rect(548, 52, 50, 18), TextAnchor.MiddleCenter, null, tl);
            T("rsvc/strip/l1", "timeline-label-2", "20:00", new Rect(693, 52, 50, 18), TextAnchor.MiddleCenter, null, tl);
            T("rsvc/strip/l2", "timeline-label-3", "23:00", new Rect(814, 52, 50, 18), TextAnchor.MiddleCenter, null, tl);
            if (door) ServiceDoorAndCall("desktop", "rsvc", f);
            if (door) ServiceCoach("desktop", "rsvc", f);
            ServicePause("desktop", "rsvc", f);

            D("rsvc/coins", "v2-wallet-pill#desktop-wallet-pill-01");
            D("rsvc/coins/icon", "v2-icon-coin-service#desktop-icon-coin-service-01", null, "rx-s12-icon-coin-service");
            T("rsvc/coins/n", "wallet-1", v.Coins.ToString("N0"), new Rect(993, 25, 64, 30));
            D("rsvc/stars", "v2-wallet-pill#desktop-wallet-pill-02");
            D("rsvc/stars/icon", "v2-icon-star-blue#desktop-icon-star-blue-01");
            T("rsvc/stars/n", "wallet-2", v.Popularity.ToString(), new Rect(1146, 25, 52, 30));
            D("rsvc/speed", "v2-speed-pill#desktop-speed-pill-01");
            if (v.Paused) D("rsvc/speed/p", "v2-speed-selected#desktop-speed-selected-01", new Rect(1229, 15, 59, 51));
            D("rsvc/speed/pi", "v2-icon-pause#desktop-icon-pause-01");
            coastalUi.HitArea("rsvc/speed/p/hit", new Rect(1229, 15, 59, 51), () => v.Paused = !v.Paused, f);
            var speedStyle = RestaurantExact.Texts["desktop:speed-1"];
            Rect[] speedAt = { new(1292, 15, 62, 51), new(1358, 15, 59, 51) };
            for (int i = 1; i <= 2; i++)
            {
                int s = i; bool on = !v.Paused && v.Speed == i; var r = speedAt[i - 1];
                if (on) D($"rsvc/speed/{i}", "v2-speed-selected#desktop-speed-selected-01", r);
                coastalUi.StyledText($"rsvc/speed/{i}/t", r, $"{i}×", speedStyle.Size, on ? cream : speedStyle.Fill, speedStyle.StrokeColour, 0, 0, Color.clear, true, TextAnchor.MiddleCenter, f, frameScale);
                coastalUi.HitArea($"rsvc/speed/{i}/hit", r, () => { v.Paused = false; v.Speed = s; }, f);
            }

            // Left: tonight's stock and the repair chip.
            // The slab ends under the last row unless the repair chip needs its place.
            D("rsvc/stock", "v2-stock-slab#desktop-stock-slab-01", string.IsNullOrEmpty(v.Alert) ? new Rect(16, 90, 194, 248) : null);
            T("rsvc/stock/title", "stock-title", "Tonight's stock", new Rect(33, 105, 170, 25));
            string[] stockIcon = { "v2-icon-fish-stock#desktop-icon-fish-stock-01", "v2-icon-soup#desktop-icon-soup-01", "v2-icon-cup#desktop-icon-cup-02" };
            for (int i = 0; i < v.Stock.Count && i < 3; i++)
            {
                var row = RestaurantExact.Pieces[$"desktop:v2-stock-row#desktop-stock-row-0{i + 1}"].rect;
                D($"rsvc/stock/{i}", $"v2-stock-row#desktop-stock-row-0{i + 1}");
                D($"rsvc/stock/{i}/icon", stockIcon[i]);
                T($"rsvc/stock/{i}/n", $"stock-count-{i + 1}", v.Stock[i].Count.ToString(), new Rect(124, row.y + 12, 60, 34), TextAnchor.MiddleLeft, v.Stock[i].Count == 0 ? Skin.BadInk : null);
            }
            if (!string.IsNullOrEmpty(v.Alert))
            {
                D("rsvc/repair", "v2-chip-repair#desktop-chip-repair-01");
                D("rsvc/repair/icon", "v2-icon-wrench-repair#desktop-icon-wrench-repair-01");
                T("rsvc/repair/t", "repair", v.Alert, new Rect(81, 343, 110, 42));
            }

            // Right: Mira asks.
            if (v.QuestionTitle != null)
            {
                D("rsvc/ask", "v2-service-card#desktop-service-card-01");
                D("rsvc/ask/mira", "v2-mira-service-bust#desktop-mira-service-bust-01");
                T("rsvc/ask/title", "late-title", v.QuestionTitle, new Rect(1284, 121, 136, 27));
                T("rsvc/ask/body", "late-copy", v.QuestionBody, new Rect(1292, 151, 124, 48), TextAnchor.UpperLeft);
                D("rsvc/ask/yes", "v2-btn-primary#desktop-btn-primary-01", null, "rx-s12-btn-primary");
                T("rsvc/ask/yes/t", "seat", v.QuestionYes, new Rect(1179, 238, 233, 28), TextAnchor.MiddleCenter);
                coastalUi.HitArea("rsvc/ask/yes/hit", new Rect(1179, 228, 233, 49), () => v.QuestionTitle = null, f);
                D("rsvc/ask/no", "v2-btn-secondary#desktop-btn-secondary-01", null, "rx-s12-btn-secondary");
                T("rsvc/ask/no/t", "decline", v.QuestionNo, new Rect(1179, 294, 233, 27), TextAnchor.MiddleCenter);
                coastalUi.HitArea("rsvc/ask/no/hit", new Rect(1179, 286, 233, 45), () => v.QuestionTitle = null, f);
            }

            // Bottom: one card per person (Mo 10-26), five at a time as in the mockup.
            D("rsvc/rail", "v2-staff-rail#desktop-staff-rail-01");
            Rect[] card = { new(44, 769, 246, 89), new(298, 769, 270, 89), new(575, 769, 246, 89), new(828, 769, 255, 89), new(1090, 769, 305, 89) };
            float[] roleX = { 146, 406, 658, 931, 1210 }, ringX = { 218, 490, 741, 999, 1316 };
            var crew = v.Crew;
            int first = crew.Count > 5 ? Mathf.Clamp(v.RailFirst, 0, crew.Count - 5) : 0;
            for (int n = 0; n < 5 && first + n < crew.Count; n++)
            {
                var s = crew[first + n]; var c = card[n];
                D($"rsvc/staff/{n}", "v2-staff-card#desktop-staff-card-01", c);
                Rx($"rsvc/staff/{n}/bust", "desktop", "", f, new Rect(c.x + 12, 770, 80, 87), ServiceBust(s.Portrait));
                T($"rsvc/staff/{n}/job", "staff-role-1", s.Job, new Rect(roleX[n], 783, 110, 25));
                Rx($"rsvc/staff/{n}/icon", "desktop", "", f, new Rect(roleX[n] + 4, 802, 50, 46), RoleIcon(s.Icon));
                var ring = new Rect(ringX[n], 785, 63, 62);
                D($"rsvc/staff/{n}/track", "v2-meter-ring-track#desktop-meter-ring-track-01", ring);
                var fill = D($"rsvc/staff/{n}/ring", s.Busy >= .7f ? "v2-meter-ring-fill#server-ring" : "v2-s12x-meter-ring-fill-orange#desktop-s12x-meter-ring-fill-orange-01", ring);
                var img = fill.GetComponent<UnityEngine.UI.Image>();
                if (img != null) { img.type = UnityEngine.UI.Image.Type.Filled; img.fillMethod = UnityEngine.UI.Image.FillMethod.Radial360; img.fillOrigin = 2; img.fillClockwise = true; img.fillAmount = Mathf.Clamp01(s.Busy); }
            }
            if (crew.Count > 5) coastalUi.HitArea("rsvc/staff/more", new Rect(34, 758, 1374, 112), () => v.RailFirst = first + 5 >= crew.Count ? 0 : first + 5, f);
        }

        // S2 on a phone: the service HUD over the 3D room (ui-2-service.png), every piece and text at its measured place.
        void InterfaceRestaurantServicePhone(RestaurantServiceView v)
        {
            var f = RestaurantFrame("rsph/frame");
            float ox = (iw - 844 * frameScale) / 2 / frameScale;
            // The bar runs the full screen width even when the frame is narrower.
            Rx("rsph/bar", "phone", "v2-bar-service#phone-bar-service-01", f, new Rect(-ox, 0, iw / frameScale, 46), "rx-bar-service");
            P("rsph/sun", "v2-icon-sun#phone-icon-sun-01");
            int hh = Mathf.FloorToInt(v.Hour), mm = Mathf.FloorToInt((v.Hour - hh) * 60);
            RxText("rsph/clock", "phone", "clock", $"{hh}:{mm:00}", f, new Rect(61, 6, 80, 23), TextAnchor.MiddleLeft);
            RxText("rsph/clock/sub", "phone", "subtitle", "Evening service", f, new Rect(62, 28, 110, 12), TextAnchor.MiddleLeft);

            // The evening's arrivals: the curve, guests ahead of NOW bright, those behind dimmed. With Close door the strip
            // narrows into Codex 1's measured 238 px (s2-call headerReflow 177+326 -> 176+238): sizes stay, places compress.
            bool door = HasUi("rx-s2-close-door-button");
            float X(float x) => door ? 176 + (x - 177) * (238f / 326) : x;
            Rect Wide(string key) { var r = RestaurantExact.Pieces["phone:" + key].rect; return door ? new Rect(X(r.x), r.y, r.width * 238f / 326, r.height) : r; }
            Rect Keep(Rect r) => new(X(r.center.x) - r.width / 2, r.y, r.width, r.height);
            P("rsph/strip", "v2-timeline-track#phone-timeline-track-01", Wide("v2-timeline-track#phone-timeline-track-01"));
            P("rsph/strip/curve", "v2-timeline-curve#phone-timeline-curve-01", Wide("v2-timeline-curve#phone-timeline-curve-01"));
            float t = Mathf.InverseLerp(v.Open, v.Close, v.Hour), nowX = X(186 + 308 * t);
            string[] guests = { "timeline-guest-1", "phone-timeline-guest-01", "timeline-guest-3", "timeline-future-guest-4", "timeline-future-guest-5" };
            foreach (var g in guests)
            {
                var gr = Keep(RestaurantExact.Pieces["phone:v2-timeline-guest#" + g].rect);
                var e = P($"rsph/strip/{g}", "v2-timeline-guest#" + g, gr);
                var img = e.GetComponent<UnityEngine.UI.Image>();
                if (img != null && img.sprite != null) img.color = gr.center.x < nowX ? new Color(1, 1, 1, .45f) : Color.white;
            }
            var flag = RestaurantExact.Pieces["phone:v2-timeline-flag#phone-timeline-flag-01"].rect;
            P("rsph/strip/now", "v2-timeline-flag#phone-timeline-flag-01", new Rect(nowX - flag.width / 2, flag.y, flag.width, flag.height));
            RxText("rsph/strip/now/t", "phone", "now", "NOW", f, new Rect(nowX - flag.width / 2, 5, flag.width, 12));
            if (door) ServiceDoorAndCall("phone", "rsph", f);
            if (door) ServiceCoach("phone", "rsph", f);
            ServicePause("phone", "rsph", f);

            P("rsph/coins", "v2-wallet-pill#phone-wallet-pill-01");
            Rx("rsph/coins/icon", "phone", "", f, new Rect(527, 7, 32, 32), "rx-s12-icon-coin-service");
            RxText("rsph/coins/n", "phone", "wallet-1", v.Coins.ToString("N0"), f, new Rect(560, 13, 44, 20), TextAnchor.MiddleLeft);
            P("rsph/stars", "v2-wallet-pill#phone-wallet-pill-02");
            P("rsph/stars/icon", "v2-icon-star#phone-icon-star-01");
            RxText("rsph/stars/n", "phone", "wallet-2", v.Popularity.ToString(), f, new Rect(654, 13, 34, 20), TextAnchor.MiddleLeft);
            P("rsph/speed", "v2-speed-pill#phone-speed-pill-01");
            var speedStyle = RestaurantExact.Texts["phone:speed-1"];
            Rect[] speedAt = { new(701, 6, 44, 33), new(745, 6, 44, 33) };
            for (int i = 1; i <= 2; i++)
            {
                int k = i; bool on = !v.Paused && v.Speed == i; var r = speedAt[i - 1];
                P($"rsph/speed/{i}", on ? "v2-speed-selected#phone-speed-selected-01" : "v2-speed-idle#phone-speed-idle-01", r);
                coastalUi.StyledText($"rsph/speed/{i}/t", r, $"{i}×", speedStyle.Size, on ? new Color(1, .973f, .92f) : speedStyle.Fill, speedStyle.StrokeColour, 0, 0, Color.clear, true, TextAnchor.MiddleCenter, f, frameScale);
                coastalUi.HitArea($"rsph/speed/{i}/hit", r, () => { v.Paused = false; v.Speed = k; }, f);
            }
            P("rsph/pause", v.Paused ? "v2-speed-selected#phone-speed-selected-01" : "v2-speed-idle#phone-speed-idle-02", new Rect(797, 6, 36, 34));
            P("rsph/pause/icon", "v2-icon-pause#phone-icon-pause-01");
            coastalUi.HitArea("rsph/pause/hit", new Rect(797, 6, 36, 34), () => v.Paused = !v.Paused, f);

            // Left: stock cards.
            string[] stockIcon = { "v2-icon-fish-stock#phone-icon-fish-stock-01", "v2-icon-soup#phone-icon-soup-01", "v2-icon-cup#phone-icon-cup-01" };
            for (int i = 0; i < v.Stock.Count && i < 3; i++)
            {
                var s = v.Stock[i];
                var card = P($"rsph/stock/{i}", $"v2-stock-card#phone-stock-card-0{i + 1}");
                var at = RestaurantExact.Pieces[$"phone:v2-stock-card#phone-stock-card-0{i + 1}"].rect;
                P($"rsph/stock/{i}/icon", stockIcon[i]);
                RxText($"rsph/stock/{i}/name", "phone", $"stock-label-{i + 1}", s.Name, f, new Rect(70, at.y + 8, 60, 17), TextAnchor.MiddleLeft);
                RxText($"rsph/stock/{i}/n", "phone", $"stock-count-{i + 1}", s.Count.ToString(), f, new Rect(70, at.y + 25, 40, 20), TextAnchor.MiddleLeft);
                float fill = s.Max > 0 ? Mathf.Clamp01((float)s.Count / s.Max) : 0;
                P($"rsph/stock/{i}/track", "v2-meter-track#phone-meter-track-01", new Rect(71, at.y + 44, 75, 10));
                if (fill > 0) P($"rsph/stock/{i}/fill", fill < .6f ? "v2-meter-fill-orange#phone-meter-fill-orange-01" : "v2-meter-fill#stock-coffee-fill", new Rect(71, at.y + 44, Mathf.Max(10, 75 * fill), 10));
                if (s.Alert) P($"rsph/stock/{i}/alert", "v2-icon-warning#phone-icon-warning-01", new Rect(127, at.y + 9, 20, 22));
            }

            // Right: Mira asks.
            if (v.QuestionTitle != null)
            {
                P("rsph/ask", "v2-service-card#phone-service-card-01");
                P("rsph/ask/mira", "v2-mira-service-bust#phone-mira-service-bust-01");
                RxText("rsph/ask/title", "phone", "late-title", v.QuestionTitle, f, new Rect(736, 68, 96, 18), TextAnchor.MiddleLeft);
                RxText("rsph/ask/body", "phone", "late-copy", v.QuestionBodyShort, f, new Rect(737, 86, 94, 30), TextAnchor.UpperLeft);
                P("rsph/ask/yes", "v2-btn-primary#phone-btn-primary-01", null, "rx-s12-btn-primary");
                P("rsph/ask/yes/icon", "v2-s12x-icon-group#phone-s12x-icon-group-01");
                RxText("rsph/ask/yes/t", "phone", "seat", v.QuestionYes, f, new Rect(724, 146, 96, 21));
                coastalUi.HitArea("rsph/ask/yes/hit", new Rect(665, 139, 161, 35), () => v.QuestionTitle = null, f);
                P("rsph/ask/no", "v2-btn-secondary#phone-btn-secondary-01", null, "rx-s12-btn-secondary");
                P("rsph/ask/no/icon", "v2-icon-cross#phone-icon-cross-01", null, "rx-s12-icon-cross");
                RxText("rsph/ask/no/t", "phone", "decline", v.QuestionNo, f, new Rect(722, 185, 98, 21));
                coastalUi.HitArea("rsph/ask/no/hit", new Rect(665, 178, 161, 34), () => v.QuestionTitle = null, f);
            }

            // Bottom: one card per person (Mo 10-26), four at a time as in the mockup; Mira hosts from her card.
            var crew = v.Crew.FindAll(s => s.Portrait != "mira");
            float[] cardX = { 15, 183, 349, 512 }, cardW = { 166, 164, 160, 158 };
            int first = crew.Count > 4 ? Mathf.Clamp(v.RailFirst, 0, crew.Count - 4) : 0;
            for (int n = 0; n < 4 && first + n < crew.Count; n++)
            {
                var s = crew[first + n]; float x = cardX[n];
                P($"rsph/staff/{n}", "v2-staff-card-phone#phone-staff-card-phone-01", new Rect(x, 323, cardW[n], 55));
                Rx($"rsph/staff/{n}/bust", "phone", "", f, new Rect(x + 7, 324, 52, 50), ServiceBust(s.Portrait));
                Rx($"rsph/staff/{n}/icon", "phone", "", f, new Rect(x + 64, 330, 22, 22), RoleIcon(s.Icon));
                RxText($"rsph/staff/{n}/job", "phone", "staff-role-1", s.Job, f, new Rect(x + 91, 331, 66, 16), TextAnchor.MiddleLeft);
                P($"rsph/staff/{n}/track", "v2-meter-track#phone-meter-track-02", new Rect(x + 66, 356, 88, 11));
                P($"rsph/staff/{n}/fill", s.Busy >= .7f ? "v2-meter-fill#cook-progress" : "v2-meter-fill-yellow#phone-meter-fill-yellow-01", new Rect(x + 66, 356, Mathf.Max(10, 88 * Mathf.Clamp01(s.Busy)), 11));
            }
            if (crew.Count > 4) coastalUi.HitArea("rsph/staff/more", new Rect(15, 323, 655, 55), () => v.RailFirst = first + 4 >= crew.Count ? 0 : first + 4, f);

            // A phone-sheet piece by its measured "asset#use" key; the sprite is the asset's own unless named.
            RectTransform P(string id, string key, Rect? at = null, string sprite = null) =>
                Rx(id, "phone", key, f, at ?? RestaurantExact.Pieces["phone:" + key].rect, sprite ?? "rx-" + key.Split('#')[0].Substring(3));
        }

        // At night the crew wear their restaurant clothes (Codex 1's CLOTHES-1 busts); anyone without one keeps the sea portrait.
        // Codex 1's S2 call sheet: the Close door button in the top bar (until the door is closed) and Mira's call strip
        // under it while she has something to say (non-blocking, no tap).
        void ServiceDoorAndCall(string screen, string id, Transform f)
        {
            Rect At(string key) => RestaurantExact.Pieces[$"{screen}:{key}"].rect;
            if (night != null && !night.DoorClosed)
            {
                var b = At("v2-s2-close-door-button#top-bar-close-door");
                coastalUi.Piece(id + "/door", b, "rx-s2-close-door-button", f, new Vector4(24, 24, 24, 24), 3);
                Rx(id + "/door/icon", screen, "v2-s2-close-door-icon#door-icon", f, null, "rx-s2-close-door-icon");
                RxText(id + "/door/t", screen, "close-door", "Close door", f);
                coastalUi.HitArea(id + "/door/hit", b, CloseServiceDoor, f);
            }
            if (miraCall != null && SimTime < miraCallUntil)
            {
                coastalUi.Piece(id + "/call", At("v2-s2-call-bubble#reusable-call-bubble"), "rx-s2-call-bubble", f, new Vector4(48, 36, 114, 36), 3);
                ArrangeArt(Rx(id + "/call/mira", screen, "v2-s2-call-mira#accepted-host-bust", f, null, MiraSprite(miraCall, "call")));
                RxText(id + "/call/t", screen, "mira-call", miraCall, f, null, TextAnchor.MiddleLeft);
            }
        }

        // Codex's frame strips (purchase sparkle, confetti, steam): one frame of the atlas per draw, its pivot on the anchor
        // (frame coordinates), t seconds since it started; false once a one-shot strip has played.
        readonly Dictionary<string, Sprite> stripFrames = new();
        readonly Dictionary<string, (int frame, float start)> stripClock = new();
        float StripTime(string key) // restarts when the strip wasn't drawn last frame
        {
            if (!stripClock.TryGetValue(key, out var c) || Time.frameCount - c.frame > 2) c.start = SimTime;
            stripClock[key] = (Time.frameCount, c.start);
            return SimTime - c.start;
        }
        bool Strip(string id, string name, Vector2 at, float t, Transform parent, float scale = 1, bool loop = false)
        {
            string sprite = "rx-" + name.Substring(3);
            if (!RestaurantExact.Strips.TryGetValue(name, out var fr) || !HasUi(sprite)) return false;
            float total = fr.Sum(x => x.seconds);
            if (captureFreeze) t = loop ? total * .3f : total * .45f; // captures show the burst at its fullest
            if (loop) t %= total; else if (t < 0 || t >= total) return false;
            int i = 0; while (i < fr.Length - 1 && t >= fr[i].seconds) { t -= fr[i].seconds; i++; }
            var (r, pv, size, _) = fr[i];
            var e = coastalUi.Piece(id, new Rect(at.x - size.x * pv.x * scale, at.y - size.y * pv.y * scale, size.x * scale, size.y * scale), sprite, parent, Vector4.zero, 3);
            var img = e.GetComponent<UnityEngine.UI.Image>();
            if (img == null || img.sprite == null) return true;
            if (!stripFrames.TryGetValue(name + i, out var sp))
            {
                var tex = img.sprite.texture; float k = tex.width / fr.Max(x => x.rect.xMax); // the atlas may load smaller than its 3x source
                stripFrames[name + i] = sp = Sprite.Create(tex, new Rect(r.x * k, tex.height - (r.y + r.height) * k, r.width * k, r.height * k), new Vector2(.5f, .5f), 100);
            }
            img.type = UnityEngine.UI.Image.Type.Simple; img.sprite = sp; img.color = Color.white;
            return true;
        }

        // Breaks a line into rows of at most width characters at spaces (the shared styled text doesn't wrap).
        static string Lines(string s, int width)
        {
            var sb = new System.Text.StringBuilder(); int row = 0;
            foreach (var w in s.Split(' '))
            {
                if (row > 0 && row + 1 + w.Length > width) { sb.Append('\n'); row = 0; }
                else if (row > 0) { sb.Append(' '); row++; }
                sb.Append(w); row += w.Length;
            }
            return sb.ToString();
        }

        // Codex 1's pause panel (exact/s2/pause) while the player holds the service: resume, Mira's speed tips, or the
        // upgrades (whose Back returns to the night).
        void ServicePause(string screen, string id, Transform f)
        {
            var v = RestaurantService;
            if (!v.Paused || coachLine != null || !HasUi("rx-s2-pause-panel")) return;
            Rect At(string key) => RestaurantExact.Pieces[$"{screen}:{key}"].rect;
            coastalUi.HitArea(id + "/hold/block", new Rect(-4000, -4000, 9000, 9000), () => { }, f);
            coastalUi.Piece(id + "/hold", At("v2-s2-pause-panel#pause-paper"), "rx-s2-pause-panel", f, RestaurantExact.Pieces[$"{screen}:v2-s2-pause-panel#pause-paper"].border, 3);
            RxText(id + "/hold/title", screen, "pause-title", "Service paused", f);
            void Button(string use, string piece, string words, System.Action act)
            {
                var r = At($"{piece}#{use}");
                coastalUi.Piece($"{id}/hold/{use}", r, "rx-" + piece.Substring(3), f, RestaurantExact.Pieces[$"{screen}:{piece}#{use}"].border, 3);
                RxText($"{id}/hold/{use}/t", screen, use, words, f);
                coastalUi.HitArea($"{id}/hold/{use}/hit", r, () => { act(); audio?.Play(VoyageAudio.Cue.Select, .4f); }, f);
            }
            Button("resume", "v2-s2-pause-primary", "Resume", () => v.Paused = false);
            Button("speed-tips", "v2-s2-pause-secondary", "Speed tips", () =>
            {
                coachLine = "At ×2 the evening flies and the crew keeps up. Slow down when a station breaks or the queue grows.";
                coachPaused = false; miraMood[coachLine] = "happy";
            });
            Button("back-harbour", "v2-s2-pause-secondary", "Upgrades", () => { v.Paused = false; OpenRestaurantUpgrades(); });
        }

        // Codex 1's coach card: Mira's first-night lines over the paused service, Got it and a quiet Skip.
        void ServiceCoach(string screen, string id, Transform f)
        {
            if (coachLine == null) return;
            Rect At(string key) => RestaurantExact.Pieces[$"{screen}:{key}"].rect;
            coastalUi.HitArea(id + "/coach/block", new Rect(-4000, -4000, 9000, 9000), () => { }, f); // the room waits under the card
            coastalUi.Piece(id + "/coach", At("v2-coach-panel#coach-speech"), "rx-coach-panel", f, new Vector4(48, 48, 114, 48), 3);
            ArrangeArt(Rx(id + "/coach/mira", screen, "v2-coach-mira#host-portrait", f, null, MiraSprite(coachLine, "coach")));
            RxText(id + "/coach/t", screen, "coaching-line", Lines(coachLine, 44), f, null, TextAnchor.MiddleLeft); // Codex measured 3 lines of ~44
            coastalUi.Piece(id + "/coach/ok", At("v2-coach-got-it#acknowledge"), "rx-coach-got-it", f, new Vector4(48, 30, 48, 30), 3);
            RxText(id + "/coach/ok/t", screen, "got-it", "Got it", f);
            RxText(id + "/coach/skip", screen, "skip", "Skip", f);
            var k = RestaurantExact.Texts[$"{screen}:skip"].Rect;
            coastalUi.HitArea(id + "/coach/ok/hit", At("v2-coach-got-it#acknowledge"), () => CoachNext(false), f);
            coastalUi.HitArea(id + "/coach/skip/hit", new Rect(k.x, k.y - 10, k.width, k.height + 20), () => CoachNext(true), f);
        }

        // S15: markers over the 3D room (Codex 1's ui-15-markers set): what each table waits for and how patient it still
        // is, a question when a dish ran out, a coin pop at the till, a warning on a broken station and each worker's task.
        void ServiceMarkers()
        {
            if (!HasUi("rx-s15-order-bubble")) return;
            // Sized like the mockup over a room that spans the screen's width.
            float s = compactInterface ? Mathf.Min(iw / 844f, ih / 390f) : iw / 844f * .62f;
            Vector2 G(Vector3 vp) => new(vp.x * iw, (1 - vp.y) * ih);
            void P(string id, string piece, Rect r) => Rx(id, "15", piece, null, r, "rx-" + piece.Substring(3));
            // Codex 1's Closed board hangs over the entrance once the door is shut (label live, like the mockup's).
            if (night.DoorClosed && HasUi("rx-closed-sign-board"))
            {
                var d = G(restaurantWorld.ViewportOf(new Vector2(night.Layout.Door.x, night.Layout.Door.y - .9f), 1.1f)); // just outside, over the way in
                var board = new Rect(d.x - 56 * s, d.y - 27 * s, 112 * s, 27 * s);
                Rx("rmark/closed", "phone", "v2-closed-sign-board#entrance-closed", null, board, "rx-closed-sign-board");
                var cl = RestaurantExact.Texts["phone:closed-label"];
                coastalUi.StyledText("rmark/closed/t", new Rect(board.x + 13 * s, board.y + 10 * s, 86 * s, 12 * s), "Closed", cl.Size * s, cl.Fill, cl.StrokeColour, cl.Stroke, cl.ShadowY, cl.Shadow, cl.Bold, TextAnchor.MiddleCenter, null, 1);
            }
            foreach (var g in night.Groups)
            {
                if (g.TableUid == 0 || g.Phase == GroupPhase.Gone || !restaurantWorld.ItemTop(g.TableUid, out var vp)) continue;
                var at = G(vp); string id = $"rmark/g{g.Id}";
                var choice = g.Tickets.FirstOrDefault(t => t.Phase == TicketPhase.Choice);
                var wait = g.Tickets.FirstOrDefault(t => t.Phase != TicketPhase.Delivered && t.Phase != TicketPhase.Abandoned);
                float patience = Mathf.Clamp01(1 - (night.Seconds - g.SeatedAt) / (RestaurantTuning.TablePatience + g.LastPatienceBoost));
                // Codex 1's moods: hearts at a table served fast and hot, a puff when a plate came cold or the wait runs long,
                // the walking-out arrow just before they give up.
                string mood = null;
                if (g.Phase == GroupPhase.Eating && g.Tickets.Count > 0)
                {
                    // Steam rises off plates for the first half minute after they land (Codex 1's 4-frame puff, looping).
                    if (night.Seconds - g.Tickets.Max(t => t.DeliveredAt) < 30)
                        if (Strip(id + "/steam", "v2-s15-steam-strip", new Vector2(at.x + 10 * s, at.y + 6 * s), StripTime(id + "/steam"), null, s * .5f, true))
                            Fade(coastalUi.ElementRect(id + "/steam"), .6f); // light heat off the plate, not a marker (R3-04)
                    float served = g.Tickets.Max(t => t.DeliveredAt) - g.SeatedAt;
                    mood = g.Tickets.Any(t => t.Cold) ? "v2-s15-mood-annoyed" : served < RestaurantTuning.TablePatience * .5f ? "v2-s15-mood-happy" : null;
                }
                else if (wait != null && patience < .08f) mood = "v2-s15-mood-leaving";
                else if (wait != null && patience < .25f) mood = "v2-s15-mood-annoyed";
                if (mood != null && HasUi("rx-" + mood.Substring(3)))
                {
                    var m = mood.EndsWith("happy") ? new Vector2(32, 25) : mood.EndsWith("annoyed") ? new Vector2(31, 32) : new Vector2(34, 18);
                    bool beside = wait != null; // left of the order bubble, else right above the table
                    P(id + "/mood", mood, new Rect(at.x + (beside ? -33 - 4 - m.x : -m.x / 2) * s, at.y - (beside ? 44 : 30) * s - m.y * s / 2, m.x * s, m.y * s));
                }
                if (choice != null) P(id + "/ask", "v2-s15-question-bubble", new Rect(at.x - 18 * s, at.y - 50 * s, 36 * s, 37 * s));
                else if (g.Phase == GroupPhase.Payment) P(id + "/tip", "v2-s15-tip-pop", new Rect(at.x - 15 * s, at.y - 34 * s, 30 * s, 20 * s));
                else if (wait != null && (g.Phase == GroupPhase.Kitchen || g.Phase == GroupPhase.Order))
                {
                    // The order bubble with the dish inset (measured slot 15,5 38x27 in the 66x43 bubble), patience ring beside it.
                    // Drawn at .72 of the cut: the mockup's compact bubble is about 44x38 over the table (RESTAURANT-REVIEW-2).
                    float so = s * .72f;
                    var b = new Rect(at.x - 33 * so, at.y - 78 * so, 66 * so, 43 * so); // in clear air above the party's heads (R3-03)
                    P(id + "/order", "v2-s15-order-bubble", b);
                    if (g.Phase == GroupPhase.Kitchen)
                        ArrangeArt(Rx(id + "/dish", "15", "", null, new Rect(b.x + 15 * so, b.y + 5 * so, 38 * so, 27 * so), Look(wait.Dish).art));
                    else P(id + "/dish", "v2-s15-task-take-order", new Rect(b.x + 21 * so, b.y + 6 * so, 23 * so, 24 * so));
                    var ring = new Rect(b.xMax - 4 * so, b.y + 16 * so, 26 * so, 26 * so);
                    P(id + "/ring", "v2-s15-patience-track", ring);
                    var fill = Rx(id + "/fill", "15", "v2-s15-patience-fill", null, ring, "rx-s15-patience-fill").GetComponent<UnityEngine.UI.Image>();
                    if (fill != null)
                    {
                        fill.type = UnityEngine.UI.Image.Type.Filled; fill.fillMethod = UnityEngine.UI.Image.FillMethod.Radial360;
                        fill.fillOrigin = 2; fill.fillClockwise = true; fill.fillAmount = patience;
                        fill.color = patience > .5f ? Color.white : patience > .25f ? new Color(1, .78f, .35f) : new Color(1, .42f, .35f);
                    }
                }
            }
            // Tonight's events sit on their tables: birthday, regular, tour group, and the table the captain works first.
            foreach (var g in night.Groups)
            {
                if (g.TableUid == 0 || g.Phase == GroupPhase.Gone || !restaurantWorld.ItemTop(g.TableUid, out var vp)) continue;
                string ev = g.Birthday ? "v2-s15-event-birthday" : g.Regular ? "v2-s15-event-regular" : g.Count >= 6 ? "v2-s15-event-tour" : null;
                if (ev != null) { var at = G(vp); P($"rmark/g{g.Id}/event", ev, new Rect(at.x - 52 * s, at.y - 34 * s, 30 * s, 32 * s)); }
            }
            if (captainTable != 0 && restaurantWorld.ItemTop(captainTable, out var cv))
            { var at = G(cv); P("rmark/captain", "v2-s15-event-captain", new Rect(at.x + 24 * s, at.y - 30 * s, 30 * s, 33 * s)); }
            foreach (var uid in night.Broken)
                if (restaurantWorld.ItemTop(uid, out var vp)) { var at = G(vp); P($"rmark/broken{uid}", "v2-s15-broken-warning", new Rect(at.x - 14 * s, at.y - 26 * s, 28 * s, 21 * s)); }
            foreach (var st in night.Staff)
            {
                string icon = TaskIcon(st.Action);
                if (icon == null || !restaurantWorld.StaffHead(st.Id, out var vp)) continue;
                var at = G(vp); P($"rmark/staff/{st.Id}", icon, new Rect(at.x - 12 * s, at.y - 22 * s, 24 * s, 19 * s));
            }
        }

        static string TaskIcon(string action) =>
            action.StartsWith("Cook") ? "v2-s15-task-cook" : action.StartsWith("Repair") ? "v2-s15-task-repair" : action.StartsWith("Take order") ? "v2-s15-task-take-order"
            : action.StartsWith("Seat") || action.StartsWith("Take payment") ? "v2-s15-task-greet" : action.StartsWith("Clear") ? "v2-s15-task-wipe"
            : action.StartsWith("Serve") ? "v2-s15-task-carry-plate" : action.Contains("Wash") ? "v2-s15-task-wash" : action.Contains("Drink") || action.Contains("Coffee") || action.Contains("Pour") ? "v2-s15-task-pour"
            : action.Contains("Prep") || action.Contains("Chop") ? "v2-s15-task-chop" : null;

        static string ServiceBust(string portrait)
        {
            // Codex 1's restaurant job busts (outfit per job, Mira as host) first, then the earlier crew busts.
            if (ArtLibrary.Get()?.UiTex("v2-rbust-" + portrait) != null) return "v2-rbust-" + portrait;
            string id = portrait == "mira" ? "mira-d" : portrait;
            if (ArtLibrary.Get()?.UiTex("rc-bust-" + id) != null) return "rc-bust-" + id;
            return portrait == "captain" ? "v2-portrait-captain" : $"v2-bust-{portrait}";
        }

        static string RoleIcon(string icon) => icon switch
        {
            "v2-icon-cloche" => "rx-s12-icon-cloche",
            "v2-icon-crew" => "rx-s12x-icon-group",
            _ => "rx-" + icon.Substring(3),
        };


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
                        coastalUi.Icon($"{cid}/bust", new Rect(4, h - bust, bw, bust), ServiceBust(s.Portrait), c, null, s.Portrait == "captain" ? "v2-portrait-captain" : $"v2-portrait-{s.Portrait}-deck");
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


        public sealed class RestaurantShopItem { public string Name, Art, Fallback, Footprint; public int Price; public ItemId Id; public int StoredUid; public string Lock; public int LockStage; }
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
            // Live over the room: the item on the floor (new from the drawer, or lifted with its uid), whether it fits there.
            public ItemId? PlaceId; public Vector2Int Tile; public bool Rotated, Fits, FromStore; public int LiftUid; public string Reason;
            public float Scroll; public readonly List<(string items, int nextUid, int coins)> Undo = new();
        }
        public RestaurantArrangeView RestaurantArrange = new();

        // S1: arrange mode over the room (ui-1-arrange.png), every piece and text at its measured place.
        void InterfaceRestaurantArrange(RestaurantArrangeView v)
        {
            var f = RestaurantFrame("rarr/frame");
            float ox = (iw - 844 * frameScale) / 2 / frameScale;
            // On a taller screen the top bar keeps to the top edge and the drawer to the bottom; the room fills between.
            Transform Band(string id, float y) { var b = coastalUi.Sliced(id, new Rect((iw - 844 * frameScale) / 2, y, 844, 390), ""); b.localScale = new Vector3(frameScale, frameScale, 1); return b; }
            var top = Band("rarr/top", 0); var bottom = Band("rarr/bottom", ih - 390 * frameScale);
            Transform P(Rect r) => r.y < 60 ? top : r.y >= 299 ? bottom : f;
            RectTransform A(string id, string key, Rect? at = null, string sprite = null)
            {
                var r = at ?? RestaurantExact.Pieces["arrange:" + key].rect;
                return Rx(id, "arrange", key, P(r), r, sprite ?? "rx-" + key.Split('#')[0].Substring(3));
            }
            void T(string id, string style, string text, Rect? at = null, TextAnchor align = TextAnchor.MiddleLeft, Color? fill = null) =>
                RxText(id, "arrange", style, text, P(at ?? RestaurantExact.Texts["arrange:" + style].Rect), at, align, fill);
            var cream = new Color(1, .973f, .92f);

            A("rarr/bar", "v2-bar-arrange#arrange-bar-arrange-01", new Rect(-ox, 0, iw / frameScale, 43));
            A("rarr/back", "v2-btn-back#arrange-btn-back-01", null, "rx-s12-btn-back");
            coastalUi.HitArea("rarr/back/hit", new Rect(23, 5, 51, 33), CloseRestaurantArrange, top);
            A("rarr/icon", "v2-icon-chair#arrange-icon-chair-02");
            T("rarr/title", "title", "Arrange", new Rect(127, 7, 160, 29));
            A("rarr/coins", "v2-wallet-arrange#arrange-wallet-arrange-01");
            A("rarr/coins/icon", "v2-icon-coin-arrange#arrange-icon-coin-arrange-01");
            T("rarr/coins/n", "wallet", v.Coins.ToString("N0"), new Rect(641, 12, 58, 20), TextAnchor.MiddleCenter);
            A("rarr/undo", "v2-btn-undo#arrange-btn-undo-01");
            T("rarr/undo/t", "undo", "Undo", new Rect(772, 13, 46, 16));
            coastalUi.HitArea("rarr/undo/hit", new Rect(735, 5, 88, 33), () => UndoArrange(v), top);

            // Live: the room under the bars takes taps (move the ghost there, or lift a placed item).
            bool live = ArrangeLive;
            if (live)
            {
                v.Coins = State.Coins;
                coastalUi.HitArea("rarr/room", new Rect(-ox, 43 - (ih / frameScale - 390) / 2, iw / frameScale, ih / frameScale - 134), () => ArrangeTap(v), f);
                if (v.PlaceId != null)
                {
                    // The bubble follows the footprint's projected centre (the mockup's spot centre is 587,224).
                    var d0 = RestaurantData.Get(v.PlaceId.Value); int w = v.Rotated ? d0.Height : d0.Width, h = v.Rotated ? d0.Width : d0.Height;
                    var vp = restaurantWorld.ViewportOf(new Vector2(v.Tile.x + w * .5f - .5f, v.Tile.y + h * .5f - .5f));
                    float fx = (vp.x * iw - (iw - 844 * frameScale) / 2) / frameScale, fy = ((1 - vp.y) * ih - (ih - 390 * frameScale) / 2) / frameScale;
                    v.PlacingAt = new Vector2((fx - 587) / 844 + .69f, (fy - 224) / 390 + .44f);
                }
            }

            // The placing bubble: highlight on the floor, rotate / cancel / confirm, and the item's name tag.
            if (live ? v.PlaceId != null : v.Placing != null)
            {
                var d = new Vector2((v.PlacingAt.x - .69f) * 844, (v.PlacingAt.y - .44f) * 390);
                Rect M(string key) { var r = RestaurantExact.Pieces["arrange:" + key].rect; return new Rect(r.x + d.x, r.y + d.y, r.width, r.height); }
                if (!live) A("rarr/spot", "v2-placement-highlight#arrange-placement-highlight-01", M("v2-placement-highlight#arrange-placement-highlight-01"));
                if (!live) // fixed spots in the game (Mo 10-27): nothing turns or moves, so only the mockup shows rotate and confirm
                {
                    A("rarr/rotate", "v2-btn-rotate#arrange-btn-rotate-01", M("v2-btn-rotate#arrange-btn-rotate-01"));
                    coastalUi.HitArea("rarr/rotate/hit", M("v2-btn-rotate#arrange-btn-rotate-01"), () => { v.Rotated = !v.Rotated; RefitArrange(v); }, f);
                }
                A("rarr/cancel", "v2-btn-cancel#arrange-btn-cancel-01", M("v2-btn-cancel#arrange-btn-cancel-01"));
                coastalUi.HitArea("rarr/cancel/hit", M("v2-btn-cancel#arrange-btn-cancel-01"), () => { if (live) CancelArrange(v); else v.Placing = null; }, f);
                // A lifted item can also go to storage or be sold back (Codex 1's S1 extras, left of rotate).
                if (live && v.LiftUid != 0 && !v.FromStore && HasUi("rx-s1x-btn-store"))
                {
                    Rect E(string key) { var r = RestaurantExact.Pieces["arrange-extras:" + key].rect; return new Rect(r.x + d.x, r.y + d.y, r.width, r.height); }
                    string[] what = { "store", "sell" };
                    for (int n = 0; n < 2; n++)
                    {
                        int k = n; var at = E($"v2-s1x-btn-{what[n]}#lifted-item-demo");
                        Rx($"rarr/{what[n]}", "arrange-extras", $"v2-s1x-btn-{what[n]}#lifted-item-demo", f, at, $"rx-s1x-btn-{what[n]}");
                        coastalUi.HitArea($"rarr/{what[n]}/hit", at, () => StoreOrSellArrange(v, k == 1), f);
                        var lr = RestaurantExact.Texts["arrange-extras:" + what[n]].Rect;
                        RxText($"rarr/{what[n]}/t", "arrange-extras", what[n], n == 0 ? "Store" : "Sell", f, new Rect(lr.x + d.x, lr.y + d.y, lr.width, lr.height));
                    }
                }
                else { coastalUi.Sliced("rarr/store", Rect.zero, null, f); coastalUi.Sliced("rarr/sell", Rect.zero, null, f); }
                if (!live)
                {
                    A("rarr/confirm", "v2-btn-confirm#arrange-btn-confirm-01", M("v2-btn-confirm#arrange-btn-confirm-01"));
                    coastalUi.HitArea("rarr/confirm/hit", M("v2-btn-confirm#arrange-btn-confirm-01"), () => v.Placing = null, f);
                }
                // A red reason is longer than the item's name: the tag pill stretches between its round ends to fit it.
                var tagAt = M("v2-name-tag#arrange-name-tag-01");
                string tagText = live && !v.Fits ? v.Reason : v.Placing;
                float grow = Mathf.Max(0, 58 + tagText.Length * 7.6f - tagAt.width);
                tagAt.width += grow; float pull = Mathf.Max(0, tagAt.xMax - (844 + ox - 8));
                tagAt.x -= pull;
                coastalUi.Piece("rarr/tag", tagAt, "rx-name-tag", f, new Vector4(66, 0, 66, 0), 3);
                var thumb = M("v2-item-rest-table2#selected-table-name-tag-thumbnail"); thumb.x -= pull;
                var tagArt = live ? "v2-item-rest-" + ArrangeArtKey(v.PlaceId.Value) : v.Items[v.Selected].Art;
                ArrangeArt(A("rarr/tag/art", "v2-item-rest-table2#selected-table-name-tag-thumbnail", thumb, ArrangeSprite(tagArt)));
                T("rarr/tag/text", "world-tag", tagText, new Rect(thumb.xMax + 6, thumb.y + 5, 120 + grow, 17),
                    TextAnchor.MiddleLeft, live && !v.Fits ? new Color(.78f, .16f, .12f) : null);
            }

            // The shop tray: categories on the left, this category's items on the right.
            A("rarr/tray", "v2-arrange-tray#arrange-arrange-tray-01", new Rect(-ox, 299, iw / frameScale, 91));
            Rect[] tab = { new(16, 310, 58, 64), new(78, 309, 68, 65), new(151, 310, 56, 64), new(211, 310, 56, 64), new(271, 310, 60, 64) };
            string[] icon = { "v2-icon-kitchen-pot#arrange-icon-kitchen-pot-01", "v2-icon-chair#arrange-icon-chair-01", "v2-icon-bar-glass#arrange-icon-bar-glass-01",
                "v2-icon-decor-plant#arrange-icon-decor-plant-01", "v2-icon-expand#arrange-icon-expand-01" };
            for (int i = 0; i < v.Categories.Length && i < 5; i++)
            {
                int c = i; bool on = v.Category == i;
                A($"rarr/cat/{i}", on ? "v2-tab-selected#arrange-tab-selected-01" : "v2-tab-idle#arrange-tab-idle-01", tab[i]);
                var ic = A($"rarr/cat/{i}/icon", icon[i]);
                var img = ic.GetComponent<UnityEngine.UI.Image>(); if (img != null && img.sprite != null) img.color = on ? cream : Color.white;
                T($"rarr/cat/{i}/label", $"tabs-{i + 1}", v.Categories[i], new Rect(tab[i].x, 348, tab[i].width, 15), TextAnchor.MiddleCenter, on ? cream : null);
                coastalUi.HitArea($"rarr/cat/{i}/hit", tab[i], () => { if (live) SetArrangeCategory(v, c); else v.Category = c; }, bottom);
            }
            Rect[] card = { new(350, 306, 149, 71), new(505, 306, 152, 71), new(662, 306, 165, 71) };
            string[] art = { "v2-item-rest-table2#arrange-item-rest-table2-01", "v2-item-rest-table4#arrange-item-rest-table4-01", "v2-item-rest-booth#arrange-item-rest-booth-01" };
            string[] coin = { "v2-icon-coin-arrange#catalog-table2-coin", "v2-icon-coin-arrange#catalog-table4-coin", "v2-icon-coin-arrange#catalog-booth-coin" };
            float[] textX = { 429, 589, 756 };
            // The mockup's three cards are measured; a longer category scrolls sideways on the same 157 px pitch.
            if (live) ArrangeScroll(v, ox);
            for (int i = 0; i < v.Items.Count && (live || i < 3); i++)
            {
                int s = i, slot = Mathf.Min(i, 2); var it = v.Items[i]; bool on = v.Selected == i;
                var shift = live ? new Vector2(350 + i * 157 - v.Scroll - card[slot].x, 0) : Vector2.zero;
                Rect At(Rect r) => new(r.x + shift.x, r.y, r.width, r.height);
                if (At(card[slot]).x < 340) { coastalUi.Sliced($"rarr/item/{i}", Rect.zero, null, bottom); continue; }
                float tx = textX[slot] + shift.x;
                A($"rarr/item/{i}", on ? "v2-item-card#arrange-item-card-01" : "v2-item-card-idle#arrange-item-card-idle-01", At(card[slot]));
                bool poorCard = live && it.Lock == null && it.StoredUid == 0 && it.Price > v.Coins;
                // The mockup's locked card shows a smaller illustration; the not-enough-coins card shows none (name, grey price, reason).
                if (it.Lock != null && HasUi("rx-s1-state-bistro"))
                {
                    var la = RestaurantExact.Pieces["arrange:v2-item-rest-table4#locked-item-illustration"].rect;
                    ArrangeArt(A($"rarr/item/{i}/art", art[slot], new Rect(At(card[slot]).x + la.x - 510, la.y, la.width, la.height), ArrangeSprite(it.Art)));
                }
                else if (!(poorCard && HasUi("rx-s1-state-price-disabled")))
                    ArrangeArt(A($"rarr/item/{i}/art", art[slot], At(RestaurantExact.Pieces["arrange:" + art[slot]].rect), ArrangeSprite(it.Art)));
                // Codex 1's card states (exact/s1-card-states, measured on a card at x 350/510/670): a stored item goes back
                // for free under a ribbon, a next-stage item waits under a lock with the stage's name, a price out of reach is greyed.
                float cx = At(card[slot]).x; bool poor = live && it.Lock == null && it.StoredUid == 0 && it.Price > v.Coins;
                Rect S(string key, float baseX) { var r = RestaurantExact.Pieces["arrange:" + key].rect; return new Rect(cx + r.x - baseX, r.y, r.width, r.height); }
                Rect ST(string key, float baseX) { var r = RestaurantExact.Texts["arrange:" + key].Rect; return new Rect(cx + r.x - baseX, r.y, r.width, r.height); }
                if (it.StoredUid != 0 && HasUi("rx-s1-state-stored"))
                {
                    A($"rarr/item/{i}/state", "v2-s1-state-stored#stored-ribbon", S("v2-s1-state-stored#stored-ribbon", 350), "rx-s1-state-stored");
                    T($"rarr/item/{i}/statet", "stored-label", "Stored", ST("stored-label", 350), TextAnchor.MiddleCenter);
                    T($"rarr/item/{i}/name", "stored-item", it.Name, ST("stored-item", 350));
                    T($"rarr/item/{i}/free", "stored-free", "Place for free", ST("stored-free", 350));
                }
                else if (it.Lock != null && HasUi("rx-s1-state-bistro"))
                {
                    A($"rarr/item/{i}/state", "v2-s1-state-bistro#locked-stage-tag", S("v2-s1-state-bistro#locked-stage-tag", 510), "rx-s1-state-bistro");
                    T($"rarr/item/{i}/statet", "bistro-label", it.Lock, ST("bistro-label", 510));
                    T($"rarr/item/{i}/name", "locked-item", it.Name, ST("locked-item", 510));
                    T($"rarr/item/{i}/free", "locked-hint", $"Stage {it.LockStage}", ST("locked-hint", 510));
                }
                else if (poor && HasUi("rx-s1-state-price-disabled"))
                {
                    // The drawer card is shorter than the mockup's: the grey pill rides 5 px higher and 4 px slimmer so the
                    // reason clears the card's lower stroke (RESTAURANT-REVIEW-2).
                    var mp = S("v2-s1-state-price-disabled#muted-price", 670); var pp = ST("poor-price", 670);
                    A($"rarr/item/{i}/state", "v2-s1-state-price-disabled#muted-price", new Rect(mp.x + 4, mp.y - 5, mp.width - 8, mp.height - 4), "rx-s1-state-price-disabled");
                    T($"rarr/item/{i}/statet", "poor-price", it.Price.ToString(), new Rect(pp.x, pp.y - 7, pp.width, pp.height));
                    T($"rarr/item/{i}/name", "poor-item", it.Name, ST("poor-item", 670), TextAnchor.MiddleCenter);
                    var pr = ST("poor-reason", 670);
                    T($"rarr/item/{i}/free", "poor-reason", "Not enough coins", new Rect(pr.x, mp.yMax - 8, pr.width, pr.height), TextAnchor.MiddleCenter);
                }
                else
                {
                    A($"rarr/item/{i}/coin", coin[slot], At(RestaurantExact.Pieces["arrange:" + coin[slot]].rect));
                    T($"rarr/item/{i}/price", $"catalog-price-{slot + 1}", it.Price.ToString(), new Rect(tx + 26, 333, 50, 17));
                    T($"rarr/item/{i}/name", $"catalog-name-{slot + 1}", it.Name, new Rect(tx, 315, 80, 14));
                }
                bool one = it.Footprint == "1×1";
                if (it.StoredUid == 0 && it.Lock == null && !poor)
                {
                    A($"rarr/item/{i}/tile", one ? "v2-s12x-icon-tile1#arrange-s12x-icon-tile1-01" : "v2-s12x-icon-tile2#arrange-s12x-icon-tile2-01",
                        one ? new Rect(tx + 4, 355, 13, 12) : new Rect(tx + 4, 355, 23, 12));
                    T($"rarr/item/{i}/size", $"catalog-size-{slot + 1}", it.Footprint, new Rect(tx + 32, 354, 34, 13));
                }
                coastalUi.HitArea($"rarr/item/{i}/hit", At(card[slot]), () =>
                {
                    if (live) { if (arrangeDrag < 12) PickArrangeItem(v, s); }
                    else { v.Selected = s; v.Placing = $"{v.Items[s].Name} · {v.Items[s].Footprint}"; }
                }, bottom);
            }
        }

        // The cut 1:1 piece when Codex made one (rx-), the v2 item art otherwise; never stretched out of shape.
        string ArrangeSprite(string art) => HasUi("rx-" + art.Substring(3)) ? "rx-" + art.Substring(3) : art;
        static void ArrangeArt(RectTransform r) { var img = r != null ? r.GetComponent<UnityEngine.UI.Image>() : null; if (img != null) img.preserveAspect = true; }

        // A drag across the drawer's cards scrolls them; the tap that ends a drag doesn't pick a card.
        float arrangeDrag; Vector2 arrangeLast;
        void ArrangeScroll(RestaurantArrangeView v, float ox)
        {
            var p = UnityEngine.InputSystem.Pointer.current; if (p == null) return;
            var gui = ToGui(p.position.ReadValue());
            var at = new Vector2((gui.x - (iw - 844 * frameScale) / 2) / frameScale, (gui.y - (ih - 390 * frameScale)) / frameScale); // the drawer band
            if (p.press.wasPressedThisFrame) { arrangeDrag = 0; arrangeLast = at; }
            else if (p.press.isPressed && at.y > 299 && at.x > 340)
            {
                float dx = at.x - arrangeLast.x; arrangeDrag += Mathf.Abs(dx); arrangeLast = at;
                v.Scroll = Mathf.Clamp(v.Scroll - dx, 0, Mathf.Max(0, 350 + v.Items.Count * 157 - (844 + ox)));
            }
        }

        // Returns true when a restaurant screen took the frame.
        Font restaurantDisplay, restaurantBody;

        // Codex 1's hand-off cards (exact/transition): Evening falls as service begins, Good morning after sleep; a tap or a
        // few seconds clears them.
        string transitionCard; float transitionUntil;
        void Transition(string card) { transitionCard = card; transitionUntil = SimTime + 2.6f; }

        void InterfaceTransition()
        {
            bool phone = compactInterface; string sc = $"{transitionCard}-{(phone ? "phone" : "desktop")}";
            float W = phone ? 844 : 1440, H = phone ? 390 : 900, k = Mathf.Min(iw / W, ih / H);
            var f = coastalUi.Sliced("rtrans/frame", new Rect((iw - W * k) / 2, (ih - H * k) / 2, W, H), "");
            f.localScale = new Vector3(k, k, 1); frameScale = k;
            // The painting covers the whole screen (cropped, never stretched); band and words keep the mockup frame.
            float c = Mathf.Max(iw / (W * k), ih / (H * k));
            coastalUi.Piece("rtrans/bg", new Rect(W / 2 - W * c / 2, H / 2 - H * c / 2, W * c, H * c), $"rx-transition-{sc}", f, Vector4.zero, 3);
            coastalUi.Piece("rtrans/band", RestaurantExact.Pieces[$"{sc}:v2-transition-title-band#separate-title-band"].rect, "rx-transition-title-band", f, new Vector4(90, 75, 90, 75), 3);
            RxText("rtrans/title", sc, $"{transitionCard}-title", transitionCard == "evening" ? "Evening falls" : "Good morning", f);
            RxText("rtrans/sub", sc, $"{transitionCard}-subtitle", transitionCard == "evening"
                ? (State.RestaurantNights.Count == 0 ? "The lanterns are lit. Time to welcome your first guests." : "The lanterns are lit. Time to welcome your guests.")
                : "A fresh day at the harbour. Mira has your plan.", f);
            coastalUi.HitArea("rtrans/hit", new Rect(-4000, -4000, 9000, 9000), () => transitionUntil = 0, f);
        }

        bool InterfaceRestaurant()
        {
            if (transitionCard != null && SimTime >= transitionUntil && !captureFreeze) transitionCard = null;
            if (RestaurantPreview == RestaurantScreen.None && transitionCard == null) return false;
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
                    case RestaurantScreen.Sleep: InterfaceRestaurantSleep(RestaurantSleepCard); break;
                    case RestaurantScreen.Market: InterfaceRestaurantMarket(RestaurantMarket); break;
                    case RestaurantScreen.Dashboard: InterfaceRestaurantDashboard(RestaurantDashboard); break;
                    case RestaurantScreen.Upgrades: InterfaceRestaurantUpgrades(RestaurantShopStage); break;
                    case RestaurantScreen.StageUp: InterfaceRestaurantStageUp(RestaurantStageUp); break;
                    case RestaurantScreen.FirstNight: InterfaceRestaurantFirstNight(); break;
                    case RestaurantScreen.Crew: InterfaceRestaurantCrew(); break;
                    case RestaurantScreen.Week: InterfaceRestaurantWeek(RestaurantWeek); break;
                }
                if (transitionCard != null) InterfaceTransition();
            }
            finally { coastalUi.Kit = null; coastalUi.DisplayOverride = coastalUi.BodyOverride = null; }
            // Toasts (Mira's calls in service, why an item can't go there) ride just under the screens' top bars.
            if (toast != null && SimTime < toastUntil && coachLine == null && transitionCard == null) coastalUi.Toast("toast", toast, null, ih * (RestaurantPreview == RestaurantScreen.Service ? .26f : .14f)); // clear of Mira's call strip, not over her coach card
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
        RectTransform Rx(string id, int screen, string piece, Transform parent, Rect? at = null, string sprite = null) => Rx(id, screen.ToString(), piece, parent, at, sprite);

        RectTransform Rx(string id, string screen, string piece, Transform parent, Rect? at = null, string sprite = null)
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
        void RxText(string id, int screen, string style, string text, Transform parent, Rect? at = null, TextAnchor align = TextAnchor.MiddleCenter, Color? fill = null) =>
            RxText(id, screen.ToString(), style, text, parent, at, align, fill);

        void RxText(string id, string screen, string style, string text, Transform parent, Rect? at = null, TextAnchor align = TextAnchor.MiddleCenter, Color? fill = null)
        {
            var s = RestaurantExact.Texts[$"{screen}:{style}"];
            coastalUi.StyledText(id, at ?? s.Rect, text, s.Size, fill ?? s.Fill, s.StrokeColour, s.Stroke, s.ShadowY, s.Shadow, s.Bold, align, parent, frameScale);
        }

        // S6+ screens: every measured piece in paint order, then every measured text with the mockup's words unless the
        // screen supplies its own (text returns null to keep the mockup's, "" to hide). skip drops pieces by key; under
        // draws the screen's own stateful pieces after the art and before the words.
        // sprite renames a piece's sprite (a variant sheet over the same layout); texts reads the words from another
        // sheet's measured styles (S11's later stages).
        void RxScreen(string id, int screen, Transform f, System.Func<string, string> text = null, System.Func<string, bool> skip = null, System.Action under = null,
            System.Func<string, string> sprite = null, string texts = null)
        {
            foreach (var key in RestaurantExact.Layout[screen])
            {
                if (skip != null && skip(key)) continue;
                string name = "rx-" + key.Split('#')[0].Substring(3);
                Rx($"{id}/{key}", screen, key, f, null, sprite?.Invoke(name) ?? name);
            }
            under?.Invoke();
            string textScreen = texts ?? screen.ToString(), prefix = textScreen + ":";
            foreach (var kv in RestaurantExact.Texts)
            {
                if (!kv.Key.StartsWith(prefix)) continue;
                string style = kv.Key.Substring(prefix.Length), words = text?.Invoke(style) ?? kv.Value.Text;
                if (string.IsNullOrEmpty(words)) continue;
                RxText($"{id}/t/{style}", textScreen, style, words, f, null, kv.Value.Align);
            }
        }

        // S12: rest well (ui-12-sleep.png), between the closing card and the morning.
        void InterfaceRestaurantSleep(RestaurantSleepView v)
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rsleep/planks", false);
            var f = RestaurantFrame("rsleep/frame");
            RxScreen("rsleep", 12, f, style => style switch
            {
                "net-value" => (v.Net >= 0 ? "+" : "") + v.Net.ToString("N0"),
                "popularity" => $"Popularity  {(v.Popularity >= 0 ? "+" : "")}{v.Popularity}",
                "tomorrow" => v.Tomorrow,
                "booking" => v.Booking,
                _ => null,
            }, null, null, name => name == "rx-s12-forecast" ? (Weather)v.TomorrowWeather switch
            {
                // Codex 1's weather set shares the sun's rect: fair is the cloud, rain its own.
                Weather.Rain when HasUi("rx-s12-weather-rain") => "rx-s12-weather-rain",
                Weather.Fair when HasUi("rx-s12-weather-cloud") => "rx-s12-weather-cloud",
                _ => null,
            } : null);
            var go = RestaurantExact.Pieces["12:v2-s12-primary#primary"].rect;
            coastalUi.HitArea("rsleep/go", go, () => { if (RestaurantPhase == DayPhase.Closing) RestaurantSleep(); else RestaurantPreview = RestaurantScreen.None; }, f);
        }

        // S7: the morning market (ui-7-market.png). Three measured rows; the buyer takes whatever is not kept.
        void InterfaceRestaurantMarket(RestaurantMarketView v)
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rmarket/planks", false);
            var f = RestaurantFrame("rmarket/frame");
            string[] rowUse = { "primary", "pollock", "plaice" }, rowText = { "mackerel", "pollock", "plaice" };
            int n = Mathf.Min(3, v.Rows.Count);
            var selling = v.Rows.Where(r => !r.Keep).ToList();
            RxScreen("rmarket", 7, f, style =>
            {
                for (int i = 0; i < 3; i++)
                {
                    if (!style.StartsWith(rowText[i] + "-")) continue;
                    if (i >= n) return "";
                    var r = v.Rows[i];
                    return style.Substring(rowText[i].Length + 1) switch
                    {
                        "name" => r.Name, "weight" => $"{r.Kg:0.0} kg", "price" => $"{Mathf.RoundToInt(r.Value / Mathf.Max(.1f, r.Kg))} / kg",
                        "value" => $"{r.Value} coins", _ => null,
                    };
                }
                return style switch
                {
                    "wallet-value" => v.Wallet.ToString("N0"),
                    "buyer-mood" => $"Buyer mood: {v.Mood}", "buyer-demand" => v.Demand,
                    "selling-weight" => $"{selling.Sum(r => r.Kg):0.0} kg", "total-value" => $"{selling.Sum(r => r.Value)} coins",
                    "open-button" => selling.Count > 0 ? "Sell & open" : "Open",
                    _ => null,
                };
            }, key =>
            {
                if (key.StartsWith("v2-s7-fish-") && !key.StartsWith("v2-s7-fish-row") && !key.StartsWith("v2-s7-fish-panel")) return true; // painted per species below
                if (key.StartsWith("v2-s7-button-sell") || key.StartsWith("v2-s7-button-keep")) return true; // drawn with their state below
                if (key.StartsWith("v2-s7-mood-") && v.Mood != "keen") return true;
                for (int i = n; i < 3; i++)
                    if (key == "v2-s7-fish-row#" + rowUse[i] || key.StartsWith($"v2-s7-divider#{rowText[i]}-")) return true;
                return false;
            }, () =>
            {
                string[] fishPieces = { "v2-s7-fish-mackerel#primary", "v2-s7-fish-pollock#primary", "v2-s7-fish-plaice#primary" };
                for (int i = 0; i < n; i++)
                {
                    var r = v.Rows[i]; int k = i;
                    coastalUi.Icon($"rmarket/fish/{i}", RestaurantExact.Pieces["7:" + fishPieces[i]].rect, FishPicture(r.Art), f, null, r.Art);
                    var sell = Rx($"rmarket/sell/{i}", 7, "v2-s7-button-sell#" + rowUse[i], f, null, "rx-s7-button-sell");
                    var keep = Rx($"rmarket/keep/{i}", 7, "v2-s7-button-keep#" + rowUse[i], f, null, "rx-s7-button-keep");
                    // The choice not taken fades back, so each row reads as one decision.
                    Fade(sell, r.Keep ? .45f : 1); Fade(keep, r.Keep ? 1 : .45f);
                    coastalUi.HitArea($"rmarket/sell/{i}/hit", RestaurantExact.Pieces["7:v2-s7-button-sell#" + rowUse[i]].rect, () => v.Rows[k].Keep = false, f);
                    coastalUi.HitArea($"rmarket/keep/{i}/hit", RestaurantExact.Pieces["7:v2-s7-button-keep#" + rowUse[i]].rect, () => v.Rows[k].Keep = true, f);
                }
            });
            coastalUi.HitArea("rmarket/open", RestaurantExact.Pieces["7:v2-s7-button-open#primary"].rect, () => { if (RestaurantPhase == DayPhase.Market) RestaurantMarketOpen(); else RestaurantPreview = RestaurantScreen.None; }, f);
            coastalUi.HitArea("rmarket/back", RestaurantExact.Pieces["7:v2-s7-button-back#primary"].rect, () => { if (RestaurantPhase != DayPhase.Market) RestaurantPreview = RestaurantScreen.None; }, f); // the portions are cut by now
        }

        static string StageWord(string name) => name == "Cafe" ? "Café" : name;
        static string Num(int n) => n.ToString("N0");

        // S6: the restaurant dashboard (ui-6-dashboard.png): the week's income by day, popularity, best sellers, next stage.
        void InterfaceRestaurantDashboard(RestaurantDashboardView v)
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rdash/planks", false);
            var f = RestaurantFrame("rdash/frame");
            string[] menuKey = { "fish", "soup", "coffee" };
            var st = v.Stage;
            bool byDay = RestaurantPhase != DayPhase.Service && HasUi("rx-s6-btn-arrange");
            RxScreen("rdash", 6, f, style =>
            {
                for (int i = 0; i < 3; i++)
                    if (style.StartsWith($"menu-{menuKey[i]}-"))
                        return i >= v.Menu.Count ? "" : style.EndsWith("-label") ? Look(v.Menu[i].dish).name : style.EndsWith("-sold") ? v.Menu[i].sold.ToString() : null;
                return style switch
                {
                    "week-number" => $"Week {v.Week}",
                    "income-value" => Num(v.Income), "income-change" => v.IncomeChange,
                    "income-dishes-value" => Num(v.Dishes), "income-drinks-value" => Num(v.Drinks), "income-tips-value" => Num(v.Tips),
                    "popularity-value" => v.Popularity.ToString(),
                    "popularity-change" => v.PopularityChange == 0 ? "Steady this week" : $"{(v.PopularityChange > 0 ? "+" : "")}{v.PopularityChange} this week",
                    "popularity-caption" => v.PopularityChange > 0 ? "A warmer welcome" : v.PopularityChange < 0 ? "Guests left unhappy" : "Word is getting around",
                    "upgrade-heading" => st.Name == null ? "Top of the harbour" : $"Next: {StageWord(st.Name)}",
                    "upgrade-subtitle" => st.Name == null ? "Every stage is open" : st.Pitch,
                    "upgrade-stars" => st.Name == null ? "" : $"{st.Stars} stars",
                    "upgrade-progress" => st.Name == null ? "" : $"{Num(st.Have)} / {Num(st.Cost)}",
                    "tab-service" => byDay ? "" : null,
                    _ => null,
                };
            }, key =>
                key.StartsWith("v2-s6-bar-") || key.StartsWith("v2-s6-star-full#rating") || key.StartsWith("v2-s6-star-full#primary") || key.StartsWith("v2-s6-star-empty")
                || key.StartsWith("v2-s6-trend") // the painted curve is a fixed shape; the real week is drawn below
                || key.StartsWith("v2-s6-dish-") || key == "v2-s6-progress-fill#primary" || key == "v2-s6-chevron-left#next-week"
                || byDay && key == "v2-s6-tab-idle#primary" // by day the live-service slot is Codex 1's Arrange entry
                || v.Menu.Count < 3 && key == "v2-s6-menu-row#coffee" || v.Menu.Count < 2 && key == "v2-s6-menu-row#soup" || v.Menu.Count < 1 && key == "v2-s6-menu-row#primary",
            () =>
            {
                // Day bars on the measured baseline, the best day in gold, scaled to the week's best night.
                float[] barX = { 38, 71, 105, 140, 174, 209, 244 };
                int best = Mathf.Max(1, v.DayIncome.Max());
                for (int d = 0; d < 7; d++)
                {
                    // A closed night is a faint empty bar, never a small positive one.
                    if (v.DayIncome[d] <= 0) { Fade(Rx($"rdash/bar/{d}", 6, "v2-s6-bar-empty", f, new Rect(barX[d], 246 - 36, 24, 36), "rx-s6-bar-empty"), .28f); continue; }
                    float h = Mathf.Max(6, 55f * v.DayIncome[d] / best);
                    bool gold = v.DayIncome[d] == best;
                    Rx($"rdash/bar/{d}", 6, gold ? "v2-s6-bar-gold#primary" : "v2-s6-bar-teal#primary", f, new Rect(barX[d], 246 - h, gold ? 26 : 24, h), gold ? "rx-s6-bar-gold" : "rx-s6-bar-teal");
                }
                DashboardTrend(v.DayPopularity, f);
                if (byDay)
                {
                    Rx("rdash/arrange", 6, "v2-s6-btn-arrange", f, null, "rx-s6-btn-arrange");
                    Rx("rdash/arrange/chair", 6, "v2-s6-arrange-chair", f, null, "rx-s6-arrange-chair");
                    RxText("rdash/arrange/label", "6", "arrange-entry", "Arrange", f);
                    // Codex 1's count badge on the Arrange tab corner: bought pieces waiting in the store (hidden at zero).
                    int stored = Kitchen.State.Items.Count(i => i.Stored);
                    if (stored > 0 && HasUi("rx-hud-count-badge")) HudBadge("rdash/stored", "dashboard-count", "v2-hud-count-badge", stored > 99 ? "99" : stored.ToString(), stored > 9 ? 30 : 22, f);
                }
                // and the New flag on Upgrades while an upgrade the player can buy now hasn't been looked at yet.
                if (UpgradesNew() && HasUi("rx-hud-new-flag")) HudBadge("rdash/upgrades-new", "upgrades-new", "v2-hud-new-flag", "New", 45, f);
                // The mockup's right chevron is the left one mirrored.
                var next = RestaurantExact.Pieces["6:v2-s6-chevron-left#next-week"].rect;
                var chevron = Rx("rdash/next-week", 6, "v2-s6-chevron-left#next-week", f, new Rect(next.xMax, next.y, next.width, next.height), "rx-s6-chevron-left");
                chevron.localScale = new Vector3(-1, 1, 1);
                float[] starX = { 349, 379, 408, 438, 467 };
                for (int i = 0; i < 5; i++)
                    Rx($"rdash/star/{i}", 6, i < v.Popularity ? "v2-s6-star-full#primary" : "v2-s6-star-empty#primary", f, new Rect(starX[i], 135, 29, 29), i < v.Popularity ? "rx-s6-star-full" : "rx-s6-star-empty");
                string[] dishPiece = { "v2-s6-dish-fish#primary", "v2-s6-dish-soup#primary", "v2-s6-dish-coffee#primary" };
                for (int i = 0; i < v.Menu.Count && i < 3; i++)
                    coastalUi.Icon($"rdash/dish/{i}", RestaurantExact.Pieces["6:" + dishPiece[i]].rect, ArrangeSprite(Look(v.Menu[i].dish).art), f, null, Look(v.Menu[i].dish).fallback);
                if (st.Name != null && st.Cost > 0)
                {
                    var track = RestaurantExact.Pieces["6:v2-s6-progress-fill#primary"].rect;
                    float k = Mathf.Clamp01(st.Have / (float)st.Cost);
                    if (k > 0) Rx("rdash/progress", 6, "v2-s6-progress-fill#primary", f, new Rect(track.x, track.y, Mathf.Max(track.height, RestaurantExact.Pieces["6:v2-s6-progress-track#primary"].rect.width * k - 4), track.height), "rx-s6-progress-fill");
                }
            });
            System.Action close = () => RestaurantPreview = RestaurantScreen.None;
            coastalUi.HitArea("rdash/back", RestaurantExact.Pieces["6:v2-s6-button-back#primary"].rect, close, f);
            coastalUi.HitArea("rdash/close", RestaurantExact.Pieces["6:v2-s6-button-close#primary"].rect, close, f);
            coastalUi.HitArea("rdash/upgrades", RestaurantExact.Pieces["6:v2-s6-button-upgrades#primary"].rect, OpenRestaurantUpgrades, f);
            coastalUi.HitArea("rdash/tab-crew", RestaurantExact.Pieces["6:v2-s6-tab-idle#crew-priorities"].rect, OpenRestaurantCrew, f);
            coastalUi.HitArea("rdash/tab-service", RestaurantExact.Pieces["6:v2-s6-tab-idle#primary"].rect, () => { if (RestaurantPhase == DayPhase.Service) RestaurantPreview = RestaurantScreen.Service; else OpenRestaurantArrange(); }, f);
        }

        // S8: the upgrades shop (ui-8-upgrades.png): the stage path, the next stage, and the kitchen & room cards.
        void InterfaceRestaurantUpgrades(RestaurantStageCard st)
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rshop/planks", false);
            var f = RestaurantFrame("rshop/frame");
            bool top = st.Name == null, canBuy = !top && st.StarsMet && st.Have >= st.Cost;
            string[] cardKey = { "fridge", "stove", "lighting" }, cardUse = { "primary", "stove", "lighting" };
            bool states = HasUi("rx-s8-state-owned-card");
            bool Locked(int i) => Kitchen.State.Stage < RestaurantUpgrades[i].stage;
            RxScreen("rshop", 8, f, style =>
            {
                for (int i = 0; i < 3; i++)
                    if (style == $"{cardKey[i]}-cost")
                        return HasRestaurantUpgrade(RestaurantUpgrades[i].id) ? (states ? "" : "Owned") : Locked(i) ? (states ? "" : $"Needs {StageWord(RestaurantData.Stage(RestaurantUpgrades[i].stage).Name)}")
                            : Num(RestaurantUpgrades[i].cost);
                return style switch
                {
                    "wallet-value" => Num(State.Coins),
                    "next-heading" => top ? "Top of the harbour" : $"Next: {StageWord(st.Name)}",
                    "next-effect" => top ? "Every stage is open" : st.Pitch,
                    "star-requirement" => top ? "" : $"{st.Stars} stars",
                    "stage-cost" => top ? "" : Num(st.Cost),
                    "shortfall" => top ? "" : !st.StarsMet ? $"{restaurantPopularity}/{st.Stars} stars" : canBuy ? "Open it" : $"Need {Num(st.Cost - st.Have)}",
                    "saving-value" => top ? "" : $"{Num(Mathf.Min(st.Have, st.Cost))} / {Num(st.Cost)}",
                    _ => null,
                };
            }, key =>
                key == "v2-s8-progress-fill#primary" || key == "v2-s8-check#stars-met" && !st.StarsMet
                || key == "v2-s8-lock#purchase" && canBuy || key.StartsWith("v2-s8-button-buy") || key is "v2-s8-coin#fridge" or "v2-s8-coin#stove" or "v2-s8-coin#lighting",
            () =>
            {
                if (!top && st.Cost > 0)
                {
                    var fill = RestaurantExact.Pieces["8:v2-s8-progress-fill#primary"].rect;
                    var track = RestaurantExact.Pieces["8:v2-s8-progress-track#primary"].rect;
                    float k = Mathf.Clamp01(st.Have / (float)st.Cost);
                    if (k > 0) Rx("rshop/progress", 8, "v2-s8-progress-fill#primary", f, new Rect(fill.x, fill.y, Mathf.Max(fill.height, (track.width - 2 * (fill.x - track.x)) * k), fill.height), "rx-s8-progress-fill");
                }
                for (int i = 0; i < 3; i++)
                {
                    // Codex 1's S8 states, measured on the fridge card (x 16) and the stove card (x 291): an owned upgrade is a muted
                    // card with a green check, a later-stage one carries the lock tag with the stage's name.
                    var card = RestaurantExact.Pieces[$"8:v2-s8-upgrade-card#{cardUse[i]}"].rect;
                    Rect At(string key, float baseX) { var r = RestaurantExact.Pieces["phone:" + key].rect; return new Rect(card.x + r.x - baseX, r.y, r.width, r.height); }
                    Rect AtT(string key, float baseX) { var r = RestaurantExact.Texts["phone:" + key].Rect; return new Rect(card.x + r.x - baseX, r.y, r.width, r.height); }
                    if (states && HasRestaurantUpgrade(RestaurantUpgrades[i].id))
                    {
                        coastalUi.Piece($"rshop/owned/{i}", card, "rx-s8-state-owned-card", f, RestaurantExact.Pieces["phone:v2-s8-state-owned-card#owned-fridge-card"].border, 3);
                        Rx($"rshop/owned/{i}/art", 8, $"v2-s8-{cardKey[i]}#primary", f, null, $"rx-s8-{cardKey[i]}");
                        Rx($"rshop/owned/{i}/check", "phone", "v2-s8-state-owned-check#owned-check", f, At("v2-s8-state-owned-check#owned-check", 16), "rx-s8-state-owned-check");
                        RxText($"rshop/owned/{i}/t", "phone", "owned-label", "Owned", f, AtT("owned-label", 16), TextAnchor.MiddleLeft);
                        if (upgradeBought == RestaurantUpgrades[i].id) // over the illustration (demo: x +31, y 312 on the card at 558)
                        {
                            var art = RestaurantExact.Pieces[$"8:v2-s8-{cardKey[i]}#primary"].rect;
                            if (!Strip($"rshop/sparkle/{i}", "v2-s8-purchase-strip", art.center, SimTime - upgradeBoughtAt, f, 2.4f)) upgradeBought = null;
                        }
                        continue;
                    }
                    if (states && Locked(i))
                    {
                        Rx($"rshop/needs/{i}", "phone", "v2-s8-state-needs-stage#stage-gate-tag", f, At("v2-s8-state-needs-stage#stage-gate-tag", 291), "rx-s8-state-needs-stage");
                        RxText($"rshop/needs/{i}/t", "phone", "needs-stage-label", $"Needs {StageWord(RestaurantData.Stage(RestaurantUpgrades[i].stage).Name)}", f, AtT("needs-stage-label", 291));
                        continue;
                    }
                    bool can = !HasRestaurantUpgrade(RestaurantUpgrades[i].id) && State.Coins >= RestaurantUpgrades[i].cost;
                    Fade(Rx($"rshop/buy-btn/{i}", 8, $"v2-s8-button-buy#{cardUse[i]}", f, null, "rx-s8-button-buy"), can ? 1 : .5f);
                    Fade(Rx($"rshop/buy-coin/{i}", 8, $"v2-s8-coin#{cardKey[i]}", f, null, "rx-s8-coin"), can ? 1 : .5f);
                }
            });
            coastalUi.HitArea("rshop/back", RestaurantExact.Pieces["8:v2-s8-button-back#primary"].rect, () => RestaurantPreview = RestaurantPhase == DayPhase.Service ? RestaurantScreen.Service : RestaurantScreen.Dashboard, f);
            coastalUi.HitArea("rshop/stage", RestaurantExact.Pieces["8:v2-s8-button-locked#primary"].rect, () => { if (canBuy) BuyRestaurantStage(); }, f);
            for (int i = 0; i < 3; i++)
            {
                string id = RestaurantUpgrades[i].id;
                coastalUi.HitArea($"rshop/buy/{i}", RestaurantExact.Pieces[$"8:v2-s8-button-buy#{cardUse[i]}"].rect, () => { if (BuyRestaurantUpgrade(id)) FillStageCard(RestaurantShopStage); }, f);
            }
        }

        // S11: a new stage (ui-11-stage-up.png); stages 3 and 4 paint their own sheet over the Bistro's layout.
        void InterfaceRestaurantStageUp(RestaurantStageUpView v)
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rstage/planks", false);
            var f = RestaurantFrame("rstage/frame");
            string variant = v.Stage >= 3 && HasUi($"rx-s11-stage{v.Stage}-background") ? $"stage{v.Stage}" : null;
            RxScreen("rstage", 11, f, style => style switch
            {
                "title" => $"Welcome to the {StageWord(v.To)}!",
                "stage" => $"{StageWord(v.From)}  >  {StageWord(v.To)}",
                "reward" => v.Reward,
                "unlock-0" => v.Unlocks[0], "unlock-1" => v.Unlocks[1], "unlock-2" => v.Unlocks[2],
                "building-sign" => StageWord(v.To),
                _ => null,
            }, null, () =>
            {
                // Codex 1's celebration (exact/s11/celebrate): soft rays behind the new facade at the demo's .55, the facade
                // again on top of them, and the New stage ribbon across its foot.
                if (!HasUi("rx-s11-celebrate-rays")) return;
                Fade(Rx("rstage/rays", "phone", "v2-s11-celebrate-rays#behind-new-facade", f, null, "rx-s11-celebrate-rays"), .55f);
                string ill = "rx-s11-illustration", alt = variant == null ? null : ill.Replace("rx-s11-", $"rx-s11-{variant}-");
                Rx("rstage/facade", 11, "v2-s11-illustration#primary", f, null, alt != null && HasUi(alt) ? alt : ill);
                Rx("rstage/ribbon", "phone", "v2-s11-new-stage-ribbon#new-stage-banner", f, null, "rx-s11-new-stage-ribbon");
                RxText("rstage/ribbon/t", "phone", "new-stage-label", "New stage!", f);
                float t = StripTime("stageup");
                Strip("rstage/confetti/0", "v2-s11-confetti-strip", new Vector2(163, 174), t, f, 2.2f);
                Strip("rstage/confetti/1", "v2-s11-confetti-strip", new Vector2(268, 150), t - .25f, f, 2f);
                Strip("rstage/confetti/2", "v2-s11-confetti-strip", new Vector2(95, 210), t - .5f, f, 1.8f);
            }, variant == null ? null : name => HasUi(name.Replace("rx-s11-", $"rx-s11-{variant}-")) ? name.Replace("rx-s11-", $"rx-s11-{variant}-") : name,
            variant == null ? null : "11-" + variant);
            coastalUi.HitArea("rstage/go", RestaurantExact.Pieces["11:v2-s11-primary#primary"].rect, () => RestaurantPreview = RestaurantScreen.Dashboard, f);
        }

        // S13: Mira walks the player through the first service (ui-13-first-night.png) before the doors open; the night
        // waits, paused, until it is read.
        void InterfaceRestaurantFirstNight()
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rfirst/planks", false);
            var f = RestaurantFrame("rfirst/frame");
            RxScreen("rfirst", 13, f);
            coastalUi.HitArea("rfirst/go", new Rect(0, 0, 844, 390), () =>
            {
                RestaurantPreview = RestaurantPhase == DayPhase.Service ? RestaurantScreen.Service : RestaurantScreen.None;
                RestaurantService.Paused = false;
            }, f);
        }

        // S14: Mira's on the harbour HUD (ui-14-harbour-entry.png), under the savings goal; it opens the restaurant's
        // week. The pieces are cut at 3x a 1920x1080 HUD, so the group is laid out in that space and scaled to the column.
        void HarbourRestaurantEntry(float y, float w)
        {
            if (!RestaurantOpen || !HasUi("rx-s14-button")) return;
            float k = w / 440f;
            var g = coastalUi.Sliced("port/mira", new Rect(Edge, y, 440, 146), "");
            g.localScale = new Vector3(k, k, 1);
            Block(new Rect(Edge, y, w, 146 * k));
            Rect At(string piece) { var p = RestaurantExact.Pieces[$"14:{piece}#restaurant-entry"].rect; return new Rect(p.x - 36, p.y - 276, p.width, p.height); }
            coastalUi.Piece("port/mira/button", At("v2-s14-button"), "rx-s14-button", g, new Vector4(140, 100, 140, 100), 3);
            coastalUi.Piece("port/mira/icon", At("v2-s14-restaurant-icon"), "rx-s14-restaurant-icon", g, Vector4.zero, 3);
            bool tonight = RestaurantPhase == DayPhase.Off;
            if (tonight) coastalUi.Piece("port/mira/badge", At("v2-s14-badge"), "rx-s14-badge", g, new Vector4(65, 45, 65, 45), 3);
            coastalUi.DisplayOverride = restaurantDisplay ??= Resources.Load<Font>("Fonts/Fredoka-Bold");
            coastalUi.BodyOverride = restaurantBody ??= Resources.Load<Font>("Fonts/Fredoka-SemiBold");
            try
            {
                foreach (var (style, words) in new[] { ("restaurant-name", "Mira's"), ("service-tonight", tonight ? "Service tonight" : "") })
                {
                    if (words == "") continue;
                    var s = RestaurantExact.Texts["harbour:" + style];
                    coastalUi.StyledText("port/mira/" + style, new Rect(s.Rect.x - 36, s.Rect.y - 276, s.Rect.width, s.Rect.height), words, s.Size, s.Fill, s.StrokeColour, s.Stroke,
                        s.ShadowY, s.Shadow, s.Bold, TextAnchor.MiddleCenter, g, k);
                }
            }
            finally { coastalUi.DisplayOverride = coastalUi.BodyOverride = null; }
            coastalUi.HitArea("port/mira/hit", new Rect(0, 0, 440, 146), () => { OpenRestaurantDashboard(); audio?.Play(VoyageAudio.Cue.Select, .45f); }, g);
        }

        // S6's popularity line over the week from Codex's live-chart pieces: the soft fill under the polyline, the
        // stretched segments, a jewel on each night. Closed nights are skipped.
        void DashboardTrend(int[] pop, Transform f)
        {
            var area = RestaurantExact.Pieces["6:v2-s6-trend#primary"].rect;
            var nights = Enumerable.Range(0, 7).Where(d => pop[d] >= 0).ToList();
            if (nights.Count == 0) return;
            float lo = nights.Min(d => pop[d]), hi = Mathf.Max(lo + 4, nights.Max(d => pop[d]));
            Vector2 P(int d) => new(area.x + 6 + d * (area.width - 12) / 6f, area.yMax - 8 - (pop[d] - lo) / (hi - lo) * (area.height - 16));
            float Y(float x)
            {
                for (int i = 1; i < nights.Count; i++)
                {
                    Vector2 a = P(nights[i - 1]), b = P(nights[i]);
                    if (x <= b.x) return Mathf.Lerp(a.y, b.y, Mathf.InverseLerp(a.x, b.x, x));
                }
                return P(nights[^1]).y;
            }
            const float column = 4;
            for (float x = P(nights[0]).x; x < P(nights[^1]).x; x += column)
            {
                float top = Y(x + column / 2);
                Rx($"rdash/trend/fill/{x:0}", 6, "v2-s6-trend-fill", f, new Rect(x, top, column + .5f, area.yMax - top), "rx-s6-trend-fill");
            }
            for (int i = 1; i < nights.Count; i++)
            {
                Vector2 a = P(nights[i - 1]), b = P(nights[i]), d = b - a;
                var seg = Rx($"rdash/trend/seg/{i}", 6, "v2-s6-trend-segment", f, new Rect(a.x, a.y, d.magnitude, 6), "rx-s6-trend-segment");
                seg.pivot = new Vector2(0, .5f); seg.anchoredPosition = new Vector2(a.x, -a.y);
                seg.localRotation = Quaternion.Euler(0, 0, -Mathf.Atan2(d.y, d.x) * Mathf.Rad2Deg);
            }
            foreach (int d in nights) { var p = P(d); Rx($"rdash/trend/dot/{d}", 6, "v2-s6-trend-dot", f, new Rect(p.x - 6, p.y - 6, 12, 12), "rx-s6-trend-dot"); }
        }

        // S9: crew priorities (ui-9-crew-priorities.png). Jobs are fixed per card; the three tasks reorder. Tap a task to
        // lift it, tap another in the same row to swap them; Save writes the order the next night uses.
        List<(string id, Job job, Work[] order)> crewOrders;
        (int row, int task)? crewLifted;
        float crewTooltipUntil; int crewTooltipRow;
        static readonly string[] CrewRowName = { "mira", "dirk", "ana", "sam", "ines", "olaf" };

        void OpenRestaurantCrew()
        {
            crewOrders = TonightsCrew().Take(6).Select(c => (c.id, c.job, (Work[])PriorityOf(c.id, c.job).Clone())).ToList();
            crewLifted = null;
            RestaurantPreview = RestaurantScreen.Crew;
        }

        static string ChipKey(int row, int task) => row == 0 && task == 0 ? "primary" : $"row-{row}-task-{task}";
        static int CrewRowOf(string key)
        {
            var m = System.Text.RegularExpressions.Regex.Match(key, @"row-(\d)");
            if (m.Success) return int.Parse(m.Groups[1].Value);
            if (key.StartsWith("v2-s9-row#")) return key.EndsWith("#primary") ? 1 : int.Parse(key.Substring(10)) + 1;
            if (key.StartsWith("v2-s9-bust-")) return System.Array.IndexOf(CrewRowName, key.Substring(11).Split('#')[0]);
            return key.EndsWith("#primary") ? 0 : -1;
        }

        void InterfaceRestaurantCrew()
        {
            if (crewOrders == null) OpenRestaurantCrew();
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rcrew/planks", false);
            var f = RestaurantFrame("rcrew/frame");
            int n = crewOrders.Count;
            bool RowPiece(string key) => key.StartsWith("v2-s9-row") || key.StartsWith("v2-s9-task-chip") || key.StartsWith("v2-s9-number-badge")
                || key.StartsWith("v2-s9-grab-handle") || key.StartsWith("v2-s9-job-") || key.StartsWith("v2-s9-bust-");
            // The rows' words are drawn with the rows below: the sheet's measured sizes for them vary 11-28 for the same
            // role, so they use the mockup's steady sizes instead (Codex 1 queue to re-measure).
            RxScreen("rcrew", 9, f, style => System.Array.Exists(CrewRowName, p => style.StartsWith(p + "-")) ? "" : style == "instructions" ? "Jobs belong to each card. Tap two tasks to swap them." : null, key => RowPiece(key) && (CrewRowOf(key) >= n || key.StartsWith("v2-s9-bust-")), () =>
            {
                for (int r = 0; r < n; r++)
                {
                    string p = CrewRowName[r];
                    var (id, job, order) = crewOrders[r];
                    CrewText($"rcrew/name/{r}", p + "-name", Cap(id), 18, f);
                    CrewText($"rcrew/job/{r}/label", p + "-job", job switch { Job.Reception => "Host", _ => job.ToString() }, 14, f);
                    for (int t = 0; t < 3; t++)
                    {
                        if (crewLifted is { } up && up.row == r && up.task == t) continue; // it floats above, see below
                        CrewText($"rcrew/rank/{r}/{t}", $"{p}-rank-{t + 1}", (t + 1).ToString(), 14, f, TextAnchor.MiddleCenter, "mira-rank-1");
                        CrewText($"rcrew/task/{r}/{t}", $"{p}-task-{t + 1}", SimStaff.Label(order[t]), 14, f);
                    }
                    var bust = RestaurantExact.Pieces[$"9:v2-s9-bust-{CrewRowName[r]}"].rect;
                    // The sheet's own head crops where S9 painted that crew member, the rail bust otherwise.
                    // Restaurant clothes first (Codex 1 OUTFITS-2D-1: tight cuts, aspect-fit in the old frame), then the sheet's heads.
                    if (HasUi($"rx-s9-bust-{id}-rest")) ArrangeArt(Rx($"rcrew/bust/{r}", 9, $"v2-s9-bust-{id}", f, bust, $"rx-s9-bust-{id}-rest"));
                    else if (HasUi("rx-s9-bust-" + id)) Rx($"rcrew/bust/{r}", 9, $"v2-s9-bust-{id}", f, new Rect(bust.x, bust.y, bust.width, bust.height));
                    else coastalUi.Icon($"rcrew/bust/{r}", bust, ServiceBust(id), f, null, $"v2-portrait-{id}-deck");
                    for (int t = 0; t < 3; t++)
                    {
                        int row = r, task = t;
                        var chip = RestaurantExact.Pieces[$"9:v2-s9-task-chip#{ChipKey(r, t)}"].rect;
                        if (crewLifted is { } l && l.row == r && l.task != t) Rx($"rcrew/target/{r}/{t}", 9, "v2-s9-slot-target", f, chip);
                        coastalUi.HitArea($"rcrew/chip/{r}/{t}", chip, () => TapCrewChip(row, task), f);
                    }
                    int jobRow = r;
                    coastalUi.HitArea($"rcrew/job/{r}", RestaurantExact.Pieces[$"9:v2-s9-job-field#{(r == 0 ? "primary" : "row-" + r)}"].rect, () => { crewTooltipUntil = Time.unscaledTime + 3; crewTooltipRow = jobRow; }, f);
                }
            });
            if (crewLifted is { } lift)
            {
                // The lifted task floats over its slot with its number, label and handle, as in the drag state.
                var chip = RestaurantExact.Pieces[$"9:v2-s9-task-chip#{ChipKey(lift.row, lift.task)}"].rect;
                var drag = RestaurantExact.Pieces["9:v2-s9-chip-drag"].rect; var home = RestaurantExact.Pieces["9:v2-s9-task-chip"].rect;
                var at = new Rect(chip.x + drag.x - home.x, chip.y + drag.y - home.y, drag.width, drag.height);
                Rx("rcrew/lifted", 9, "v2-s9-chip-drag", f, at);
                var badge = RestaurantExact.Pieces["9:v2-s9-number-badge#primary"].rect;
                Rx("rcrew/lifted/badge", 9, "v2-s9-number-badge", f, new Rect(at.x + 10, at.y + (at.height - badge.height) / 2 - 2, badge.width, badge.height));
                var rank = RestaurantExact.Texts["9:mira-rank-1"]; var label = RestaurantExact.Texts["9:mira-task-1"];
                CrewText("rcrew/lifted/rank", "mira-rank-1", (lift.task + 1).ToString(), 14, f, TextAnchor.MiddleCenter, null, new Rect(at.x + 10, at.y + (at.height - badge.height) / 2 - 2, badge.width, badge.height));
                CrewText("rcrew/lifted/label", "mira-task-1", SimStaff.Label(crewOrders[lift.row].order[lift.task]), 14, f, TextAnchor.MiddleLeft, null, new Rect(at.x + 40, at.y + 4, label.Rect.width, at.height - 12));
                coastalUi.HitArea("rcrew/lifted/hit", at, () => crewLifted = null, f);
            }
            if (Time.unscaledTime < crewTooltipUntil)
            {
                // The measured bubble sits above the third row's job and points down at it; it follows the tapped row.
                float dy = RestaurantExact.Pieces[$"9:v2-s9-job-field#{(crewTooltipRow == 0 ? "primary" : "row-" + crewTooltipRow)}"].rect.y - RestaurantExact.Pieces["9:v2-s9-job-field#row-2"].rect.y;
                var tip = RestaurantExact.Pieces["9:v2-s9-tooltip"].rect; tip.y += dy;
                Rx("rcrew/tip", 9, "v2-s9-tooltip", f, tip);
                CrewText("rcrew/tip/main", "mira-name", "Jobs belong to each card.", 15, f, TextAnchor.MiddleLeft, null, new Rect(199, 108 + dy, 232, 22));
                CrewText("rcrew/tip/hint", "mira-job", "Tap two tasks to swap them.", 14, f, TextAnchor.MiddleLeft, null, new Rect(199, 133 + dy, 232, 20));
            }
            coastalUi.HitArea("rcrew/back", RestaurantExact.Pieces["9:v2-s9-button-back#primary"].rect, () => { crewOrders = null; OpenRestaurantDashboard(); }, f);
            coastalUi.HitArea("rcrew/save", RestaurantExact.Pieces["9:v2-s9-button-save#primary"].rect, () =>
            {
                foreach (var c in crewOrders) SavePriority(c.id, c.order);
                SaveGame(); Toast("Priorities saved for tonight.");
                crewOrders = null; OpenRestaurantDashboard();
            }, f);
        }

        // A row's word at its measured place in S9's own colours (colour from look, or the style itself) at a steady size.
        void CrewText(string id, string style, string words, float size, Transform f, TextAnchor align = TextAnchor.MiddleLeft, string look = null, Rect? at = null)
        {
            var s = RestaurantExact.Texts["9:" + style]; var c = RestaurantExact.Texts["9:" + (look ?? style)];
            coastalUi.StyledText(id, at ?? s.Rect, words, size, c.Fill, c.StrokeColour, c.Stroke, c.ShadowY, c.Shadow, true, align, f, frameScale);
        }

        void TapCrewChip(int row, int task)
        {
            if (crewLifted is { } l && l.row == row && l.task != task)
            {
                var o = crewOrders[row].order;
                (o[l.task], o[task]) = (o[task], o[l.task]);
                crewLifted = null;
                audio?.Play(VoyageAudio.Cue.Select, .4f);
                return;
            }
            crewLifted = crewLifted is { } same && same.row == row && same.task == task ? null : (row, task);
        }

        void OpenRestaurantUpgrades() { FillStageCard(RestaurantShopStage); RestaurantPreview = RestaurantScreen.Upgrades; upgradesSeen = BuyableUpgrades(); }

        // The New flag shows when more upgrades are buyable than when the player last opened the upgrades.
        int upgradesSeen;
        int BuyableUpgrades() => RestaurantUpgrades.Count(u => !HasRestaurantUpgrade(u.id) && Kitchen.State.Stage >= u.stage && State.Coins >= u.cost);
        bool UpgradesNew() => BuyableUpgrades() > upgradesSeen;

        // A HUD badge (blank cut + live cream word) at its measured place, growing to the right from its left edge.
        void HudBadge(string id, string use, string piece, string word, float width, Transform f)
        {
            var at = RestaurantExact.Pieces[$"phone:{piece}#{use}"].rect;
            var border = piece == "v2-hud-count-badge" ? new Vector4(27, 27, 27, 27) : new Vector4(24, 21, 42, 21); // export px, Codex 1's slices
            coastalUi.Piece(id, new Rect(at.x, at.y, width, at.height), "rx-" + piece.Substring(3), f, border, 3);
            var s = RestaurantExact.Texts["phone:" + use].Rect;
            RxText(id + "/word", "phone", use, word, f, piece == "v2-hud-count-badge" ? new Rect(at.x, s.y, width, s.height) : new Rect(s.x, s.y, width - (at.width - s.width), s.height));
        }
        public void OpenRestaurantDashboard() { FillDashboard(); RestaurantPreview = RestaurantScreen.Dashboard; }
        bool HasRestaurantUpgrade(string id) => Kitchen.HasUpgrade(id);

        static void Fade(RectTransform piece, float alpha)
        {
            foreach (var g in piece.GetComponentsInChildren<UnityEngine.UI.Graphic>()) { var c = g.color; c.a = alpha; g.color = c; }
        }

        static string FishPicture(string art) => art != null && art.StartsWith("fish-") ? "rx-fishart-" + art.Substring(5) : art;

        // S3: Mira's plan card on the way out (ui-3-mira-plan.png), every piece and text at its measured place.
        void InterfaceRestaurantPlan(RestaurantPlanView v)
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rplan/planks", false);
            var f = RestaurantFrame("rplan/frame");
            Rx("rplan/bg", 3, "v2-bg-plan", f);
            // As in the mockup: a torso crop, face around (150,140) and the hat ~170 wide, cut at the waist by the frame's edge.
            var miraClip = coastalUi.Clip("rplan/mira/clip", new Rect(0, 0, 300, 390), f);
            Rx("rplan/mira", 3, "v2-mira-plan", miraClip, new Rect(-138, 14 + Mathf.Sin(SimTime * 1.6f) * 1.5f, 564, 705));

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
                coastalUi.Icon($"rplan/dish/{i}/art", new Rect(x + 6, 166, 110, 75), ArrangeSprite(d.Art), f, null, d.Fallback);
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

            if (v.SpecialReward != null && HasUi("rx-s3-reservation-card")) { PlanReservation(v, f); goto go; }
            Rx("rplan/special", 3, "v2-ticket", f);
            Rx("rplan/special/icon", 3, "v2-icon-special", f);
            RxText("rplan/special/head", 3, "special-heading", "Special request", f, null, TextAnchor.MiddleLeft);
            RxText("rplan/special/body", 3, "special-copy", TwoLines(v.SpecialTitle), f); // two lines, as in the mockup
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

            go:
            Rx("rplan/go", 3, "v2-btn-primary", f);
            Rx("rplan/go/icon", 3, "v2-icon-tick", f);
            RxText("rplan/go/label", 3, "got-it", "Got it", f);
            coastalUi.HitArea("rplan/go/hit", new Rect(668, 297, 165, 70), () => { if (RestaurantPhase == DayPhase.Plan) RestaurantPlanAccepted(); else RestaurantPreview = RestaurantScreen.None; }, f);
            miraClip.SetAsLastSibling(); // her welcoming hand reaches over the paper's left edge, as in the mockup (R3-06)
        }

        // S3 with a booking (exact/s3/reservation): the reservation card replaces the special-request ticket.
        void PlanReservation(RestaurantPlanView v, Transform f)
        {
            RectTransform P(string id, string key, string sprite = null) => Rx(id, "plan", key, f, null, sprite ?? "rx-" + key.Split('#')[0].Substring(3));
            void T(string id, string style, string text, TextAnchor a = TextAnchor.MiddleLeft) => RxText(id, "plan", style, text, f, null, a);
            P("rplan/res/patch", "v2-s3-reservation-wall-patch#context-remove-old-ticket");
            P("rplan/res", "v2-s3-reservation-card#special-reservation");
            P("rplan/res/face-slot", "v2-s3-reservation-face-slot#guest-face-slot");
            ArrangeArt(P("rplan/res/face", "v2-guest-ada#example-guest-ada", v.ReservationFace));
            P("rplan/res/dish-slot", "v2-s3-reservation-dish-slot#wished-dish-slot");
            ArrangeArt(P("rplan/res/dish", "v2-dish-grilled-fish#example-wished-dish", ArrangeSprite(v.ReservationDishArt)));
            T("rplan/res/head", "reservation-heading", "Reservation", TextAnchor.MiddleCenter);
            T("rplan/res/name", "guest-name", v.ReservationName);
            T("rplan/res/party", "party-size-time", $"{v.ReservationParty} guests · {v.SpecialReward} coins", TextAnchor.MiddleCenter);
            T("rplan/res/wish", "wished-dish", v.ReservationDish);
            if (v.SpecialAccepted == null)
            {
                P("rplan/res/yes", "v2-s3-reservation-accept#accept-reservation"); T("rplan/res/yes/t", "accept", "Accept", TextAnchor.MiddleCenter);
                P("rplan/res/no", "v2-s3-reservation-decline#decline-reservation"); T("rplan/res/no/t", "decline", "Decline", TextAnchor.MiddleCenter);
                coastalUi.HitArea("rplan/res/yes/hit", RestaurantExact.Pieces["plan:v2-s3-reservation-accept#accept-reservation"].rect, () => v.SpecialAccepted = true, f);
                coastalUi.HitArea("rplan/res/no/hit", RestaurantExact.Pieces["plan:v2-s3-reservation-decline#decline-reservation"].rect, () => v.SpecialAccepted = false, f);
            }
            else RxText("rplan/res/state", "plan", "wished-dish", v.SpecialAccepted == true ? "Booked for tonight" : "Not tonight", f,
                new Rect(680, 200, 144, 60), TextAnchor.MiddleCenter);
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
            // The forecast row sits 14 px higher than measured so it clears the paper's lower outline (RESTAURANT-REVIEW-1).
            Rect Up(Rect r) => new Rect(r.x, r.y - 14, r.width, r.height);
            Rx("rprep/margin/icon", 4, "v2-icon-forecast", f, Up(RestaurantExact.Pieces["4:v2-icon-forecast"].rect));
            RxText("rprep/margin/label", 4, "forecast-label", "Forecast", f, Up(RestaurantExact.Texts["4:forecast-label"].Rect), TextAnchor.MiddleLeft);
            string[] margins = { "Tight", "+10%", "+20%" };
            float[] marginX = { 529, 611, 692 };
            var pill = RestaurantExact.Texts["4:forecast-pill"];
            for (int i = 0; i < 3; i++)
            {
                int m = i; bool on = v.Margin == i; var r = new Rect(marginX[i], 271, 80, 30);
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
            Rx("rclose/bg", 5, "v2-bg-closing", f);
            Rx("rclose/board", 5, "v2-closing-board", f);
            Rx("rclose/head", 5, "v2-closing-header", f);
            RxText("rclose/title", 5, "closing-title", v.Title, f);
            Rx("rclose/moon", 5, "v2-icon-moon", f);
            if (v.BestNight && HasUi("rx-s5-best-night-ribbon"))
            {
                Rx("rclose/best", "phone", "v2-s5-best-night-ribbon#v2-s5-best-night-ribbon", f, null, "rx-s5-best-night-ribbon");
                RxText("rclose/best/t", "phone", "best-night-label", "Best night yet!", f);
            }
            if (v.FullHouse && HasUi("rx-s5-full-house-stamp"))
            {
                Rx("rclose/full", "phone", "v2-s5-full-house-stamp#v2-s5-full-house-stamp", f, null, "rx-s5-full-house-stamp");
                RxText("rclose/full/t", "phone", "full-house-label", "Full house", f);
            }

            // Column 1: the till.
            Rx("rclose/served", 5, "v2-metric-row#served count row", f, null, "rx-metric-row");
            Rx("rclose/served/icon", 5, "v2-icon-guests#served guests", f, null, "rx-icon-guests");
            RxText("rclose/served/text", 5, "served", $"{v.Served} served · {v.Left} left", f, new Rect(188, 69, 128, 22), TextAnchor.MiddleLeft);
            void Line(string id, string row, string icon, string label, int value)
            {
                Rx(id, 5, row, f, null, "rx-metric-row");
                var at = RestaurantExact.Pieces[$"5:{row}"].rect;
                Rx(id + "/icon", 5, icon, f);
                RxText(id + "/label", 5, "metric-label", label, f, new Rect(208, at.y + 3, 100, 17), TextAnchor.MiddleLeft);
                RxText(id + "/n", 5, "metric-number", value.ToString(), f, new Rect(207, at.y + 17, 100, 25), TextAnchor.MiddleLeft);
            }
            Line("rclose/dishes", "v2-metric-row", "v2-dish-closing-fish", "Dishes", v.Dishes);
            Line("rclose/drinks", "v2-metric-row#drinks row", "v2-dish-lemonade", "Drinks", v.Drinks);
            Line("rclose/tips", "v2-metric-row#tips row", "v2-icon-coins", "Tips", v.Tips);
            Rx("rclose/total", 5, "v2-tonight-row", f);
            Rx("rclose/total/icon", 5, "v2-icon-coin-service", f);
            RxText("rclose/total/label", 5, "metric-label", "Tonight", f, new Rect(219, 231, 90, 17), TextAnchor.MiddleLeft);
            RxText("rclose/total/n", 5, "tonight-number", $"+{v.Total}", f, new Rect(219, 246, 100, 30), TextAnchor.MiddleLeft);
            Rx("rclose/cats", 5, "v2-metric-row#cats row", f, null, "rx-metric-row");
            Rx("rclose/cats/art", 5, "v2-illus-cats", f);
            RxText("rclose/cats/text", 5, "cats", $"{v.CatPortions} portions for\nthe alley cats", f, new Rect(236, 295, 90, 34));
            var cs = RestaurantExact.Texts["5:metric-label"];
            coastalUi.StyledText("rclose/cats/vl", new Rect(246, 330, 30, 18), "Value", 11, cs.Fill, cs.StrokeColour, 0, 0, Color.clear, false, TextAnchor.MiddleLeft, f, frameScale);
            Rx("rclose/cats/coin", 5, "v2-icon-coin-service#cat food value coin", f, null, "rx-icon-coin-service");
            RxText("rclose/cats/value", 5, "served", v.CatValue.ToString(), f, new Rect(300, 328, 24, 22), TextAnchor.MiddleLeft);

            // Column 2: reviews and the crew of the night.
            string[] cards = { "v2-review-card", "v2-review-card#review row 2", "v2-review-card#review row 3" };
            for (int i = 0; i < v.Reviews.Count && i < 3; i++)
            {
                var r = v.Reviews[i]; float y = RestaurantExact.Pieces[$"5:{cards[i]}"].rect.y;
                Rx($"rclose/review/{i}", 5, cards[i], f, null, "rx-review-card");
                Rx($"rclose/review/{i}/face", 5, $"v2-review-portrait-0{i + 1}", f, null,
                    r.Portrait.StartsWith("guest-") && HasUi("v2-" + r.Portrait) ? "v2-" + r.Portrait : $"rx-review-portrait-0{ReviewFace(r.Portrait, i)}");
                for (int s = 0; s < 5; s++)
                    Rx($"rclose/review/{i}/star/{s}", 5, "v2-star-full", f, new Rect(396 + s * 19.5f, y + 9, 18, 18), s < r.Stars ? "rx-star-full" : "rx-star-empty");
                RxText($"rclose/review/{i}/quote", 5, "review-quote", $"“{r.Quote}”", f, new Rect(397, y + 28, 146, 30), TextAnchor.MiddleLeft);
            }
            Rx("rclose/crew", 5, "v2-review-card#crew of the night row", f, null, "rx-review-card");
            if (v.CrewOfTheNight == "Jo") Rx("rclose/crew/face", 5, "v2-portrait-crew-jo", f);
            else coastalUi.Portrait("rclose/crew/face", new Rect(331, 292, 62, 62), v.CrewPortrait, f);
            RxText("rclose/crew/label", 5, "crew-of-night-label", "Crew of the night", f, null, TextAnchor.MiddleLeft);
            RxText("rclose/crew/name", 5, "crew-of-night-name", v.CrewOfTheNight, f, new Rect(400, 315, 140, 25), TextAnchor.MiddleLeft);

            // Column 3: popularity; Mira and Sleep stand over the board's corner.
            Rx("rclose/pop", 5, "v2-popularity-card", f);
            RxText("rclose/pop/title", 5, "popularity-title", "Popularity", f, null, TextAnchor.MiddleLeft);
            Rx("rclose/pop/star", 5, "v2-star-full", f);
            RxText("rclose/pop/from", 5, "popularity-before", $"{v.PopularityFrom} →", f, new Rect(607, 112, 60, 29), TextAnchor.MiddleLeft);
            RxText("rclose/pop/to", 5, "popularity-after", v.PopularityTo.ToString(), f, new Rect(664, 109, 50, 34), TextAnchor.MiddleLeft,
                v.PopularityTo >= v.PopularityFrom ? null : Skin.BadInk);
            Rx("rclose/pop/track", 5, "v2-progress-track", f);
            Rx("rclose/pop/fill", 5, "v2-progress-fill", f, new Rect(560, 156, Mathf.Max(18, 130 * Mathf.Clamp01(v.Popularity)), 17));
            Rx("rclose/pop/barstar", 5, "v2-star-full#progress endpoint star", f, null, "rx-star-full");
            RxText("rclose/pop/rep", 5, "reputation", "Harbour reputation", f, new Rect(566, 175, 140, 15));
            RxText("rclose/pop/delta", 5, "reputation", v.Popularity >= v.PopularityBefore ? "A warmer welcome" : "A quieter night", f, new Rect(566, 190, 140, 15), TextAnchor.MiddleCenter, Skin.InkSoft);

            // As in the mockup: big, cut at the waist by the frame's bottom edge.
            var miraClip = coastalUi.Clip("rclose/mira/clip", new Rect(520, 0, 324, 390), f);
            // Mira waves goodnight as the host (Codex 1's v2-s5-mira-host at the mockup's 580,209 148x167), else the captain cut.
            if (HasUi("rx-s5-mira-host")) ArrangeArt(Rx("rclose/mira", 5, "v2-mira-wave", miraClip, new Rect(60, 209 + Mathf.Sin(SimTime * 1.6f) * 1.5f, 148, 167), "rx-s5-mira-host"));
            else Rx("rclose/mira", 5, "v2-mira-wave", miraClip, new Rect(23, 198 + Mathf.Sin(SimTime * 1.6f) * 1.5f, 222, 278));
            Rx("rclose/rays", 5, "v2-accent-rays", f);
            // 12 px right of the measured spot so it clears the end of "Crew of the night" (R3-07).
            Rx("rclose/say", 5, "v2-bubble-mira", f, new Rect(498, 259, 108, 52));
            RxText("rclose/say/text", 5, "mira-bubble", TwoLines(v.MiraLine), f, new Rect(506, 264, 96, 38));
            Rx("rclose/sleep", 5, "v2-btn-primary#Sleep button; nine-slice", f, null, "rx-btn-primary");
            Rx("rclose/sleep/icon", 5, "v2-icon-bed", f);
            RxText("rclose/sleep/label", 5, "sleep", "Sleep", f, new Rect(607, 331, 100, 31), TextAnchor.MiddleLeft);
            coastalUi.HitArea("rclose/sleep/hit", new Rect(531, 317, 190, 57), () => RestaurantPreview = WeekDone() ? RestaurantScreen.Week : RestaurantScreen.Sleep, f);
        }

        // S16 (Codex 1's ui-16-week): seven nights' takings as bars on the measured baseline, the best night gold, the
        // week's best dish and crew member, popularity across the week and the total.
        void InterfaceRestaurantWeek(RestaurantWeekView v)
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("rweek/planks", false);
            var f = RestaurantFrame("rweek/frame");
            int best = System.Array.IndexOf(v.Nights, v.Nights.Max()), top = Mathf.Max(1, v.Nights.Max());
            float tallest = Enumerable.Range(1, 7).Max(i => RestaurantExact.Pieces[$"16:{(i == 6 ? "v2-s16-bar-gold" : "v2-s16-bar-teal")}#night-{i}"].rect.height);
            RxScreen("rweek", 16, f, style =>
            {
                for (int i = 0; i < 7; i++)
                {
                    if (style == $"night-{i + 1}-day") return v.Days[i].ToString();
                    if (style == $"night-{i + 1}-coins") return ""; // drawn over each live bar below
                }
                return style switch
                {
                    "title" => $"A week at Mira's", "income-title" => "Seven nights",
                    "dish-name" => v.Dish, "dish-count" => $"{v.DishCount} served",
                    "crew-name" => v.Crew, "crew-quote" => v.Quote,
                    "popularity-start" => v.PopularityFrom.ToString(), "popularity-end" => v.PopularityTo.ToString(),
                    "popularity-delta" => $"{(v.PopularityTo >= v.PopularityFrom ? "+" : "")}{v.PopularityTo - v.PopularityFrom} this week",
                    "total-coins" => Num(v.Nights.Sum()), "next-week" => "Next week",
                    _ => null,
                };
            }, key => key.StartsWith("v2-s16-bar-") || key.StartsWith("v2-dish-") || key.StartsWith("v2-rbust-"), () =>
            {
                ArrangeArt(Rx("rweek/dish", 16, "v2-dish-grilled-fish#example-best-dish", f, null, ArrangeSprite(v.DishArt)));
                string bust = HasUi("v2-rbust-" + v.CrewId) ? "v2-rbust-" + v.CrewId : "v2-rbust-jo";
                ArrangeArt(Rx("rweek/crew", 16, "v2-rbust-jo#example-crew-jo", f, null, bust));
                for (int i = 0; i < 7; i++)
                {
                    var slot = RestaurantExact.Pieces[$"16:{(i == 5 ? "v2-s16-bar-gold" : "v2-s16-bar-teal")}#night-{i + 1}"].rect;
                    float h = v.Nights[i] <= 0 ? 0 : Mathf.Max(14, tallest * v.Nights[i] / top); // keeps the caps on a small night
                    if (h > 0) Rx($"rweek/bar/{i}", 16, $"{(i == 5 ? "v2-s16-bar-gold" : "v2-s16-bar-teal")}#night-{i + 1}", f,
                        new Rect(slot.x, slot.yMax - h, slot.width, h), i == best ? "rx-s16-bar-gold" : "rx-s16-bar-teal");
                    var t = RestaurantExact.Texts[$"16:night-{i + 1}-coins"].Rect;
                    RxText($"rweek/coins/{i}", 16, $"night-{i + 1}-coins", v.Nights[i].ToString(), f, new Rect(t.x, slot.yMax - h - 23, t.width, t.height));
                }
            });
            coastalUi.HitArea("rweek/next", RestaurantExact.Pieces["16:v2-s16-primary#next-week"].rect, () => RestaurantPreview = RestaurantScreen.Sleep, f);
        }

        // A speech-bubble line broken at the space nearest its middle, as the mockup sets it.
        static string TwoLines(string t)
        {
            if (string.IsNullOrEmpty(t) || t.Length < 12 || t.Contains("\n")) return t;
            int best = -1;
            for (int i = 0; i < t.Length; i++)
                if (t[i] == ' ' && (best < 0 || Mathf.Abs(i - t.Length / 2) < Mathf.Abs(best - t.Length / 2))) best = i;
            return best < 0 ? t : t.Substring(0, best) + "\n" + t.Substring(best + 1);
        }

        // The six painted reviewer faces; the regulars keep theirs, other guests get one by name.
        static int ReviewFace(string portrait, int i) => portrait switch
        {
            "fisher" => 1, "deckhand" => 2, "captain" => 3,
            _ => 4 + (Mathf.Abs((portrait ?? "").GetHashCode()) + i) % 3,
        };
    }
}

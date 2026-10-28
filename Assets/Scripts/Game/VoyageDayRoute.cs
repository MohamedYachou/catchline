using System.Collections.Generic;
using System.Linq;
using Catchline.Game.Sea;
using UnityEngine;

namespace Catchline.Game
{
    // Design 14.1, 14.2 and 14.6 (Mo 10-27): Mira offers the day as cards (easy one stop, medium two, hard two or three with
    // bigger fish), fuels the boat at port and orders the stops by route fuel. A day is one trip: Next stop sails ground to
    // ground (across the sea, or over the chart to the next sea), and Head home ends it. On a route day the engine is off at
    // anchor, so fuel is spent only by the legs, each paid when it starts.
    public partial class VoyageGame
    {
        public sealed class DayStop { public int Spot; public string Ground, Name; }
        public sealed class DayCard
        {
            public string Kind, Title, Line, Art; public readonly List<DayStop> Stops = new();
            public float Fuel, Saved; public int ExtraGuests; public bool Possible = true;
        }
        public readonly List<DayCard> DayCards = new();
        public readonly List<DayStop> DayRoute = new();
        public int DayStopAt { get; private set; }
        public bool DayCardsOpen { get; private set; }
        string routeGround;
        int hopSpot = -1, hopFrom = -1; Vector2 hopExit; bool chartHop;
        public bool RouteDay => DayRoute.Count > 0 && (RestaurantPhase == DayPhase.Out || RestaurantPhase == DayPhase.Home);
        public bool HasNextStop => RestaurantPhase == DayPhase.Out && DayStopAt + 1 < DayRoute.Count;
        public DayStop NextDayStop => HasNextStop ? DayRoute[DayStopAt + 1] : null;
        bool UsesFuel => State.Tier > 0;

        // ---- fuel by route ----------------------------------------------------------------------------------------
        // null is the harbour. Legs between seas on one coast follow the chart; across coasts the boat goes via home.
        static float LegFuel(DayStop a, DayStop b)
        {
            if (a == null && b == null) return 0;
            if (a == null || b == null) return GameData.TripFuel((a ?? b).Spot);
            if (a.Spot == b.Spot) return a.Ground == b.Ground ? 0 : .5f;
            if (Coasts.Of(a.Spot) != Coasts.Of(b.Spot)) return GameData.TripFuel(a.Spot) + GameData.TripFuel(b.Spot);
            return Mathf.Max(1, Mathf.Round(Vector2.Distance(NauticalChartPoint(a.Spot), NauticalChartPoint(b.Spot)) * 9f) / 2f);
        }
        static float RouteFuel(IList<DayStop> stops)
        {
            float f = LegFuel(null, stops[0]);
            for (int i = 1; i < stops.Count; i++) f += LegFuel(stops[i - 1], stops[i]);
            return f + LegFuel(stops[stops.Count - 1], null);
        }
        static IEnumerable<List<DayStop>> Orders(List<DayStop> s)
        {
            if (s.Count <= 1) { yield return s; yield break; }
            for (int i = 0; i < s.Count; i++)
                foreach (var rest in Orders(s.Where((_, k) => k != i).ToList())) yield return new List<DayStop> { s[i] }.Concat(rest).ToList();
        }
        // Mira's tank at departure: full if the till can pay for the top-up, else what is in it.
        float DayTank => !UsesFuel ? float.PositiveInfinity : State.Coins >= State.FuelFillCost ? State.FuelCapacity : State.Fuel;
        bool PayLeg(DayStop a, DayStop b)
        {
            if (!UsesFuel) return true;
            float cost = LegFuel(a, b);
            if (State.Fuel + .001f < cost) return false;
            State.Fuel = Mathf.Max(0, State.Fuel - cost);
            return true;
        }

        // ---- Mira's day cards -------------------------------------------------------------------------------------
        static float BigFish(GroundDef g)
        {
            double w = g.Day.Sum(e => (double)e.weight);
            return w <= 0 ? 0 : (float)(g.Day.Sum(e => e.weight * (double)(GameData.Get(e.species).MaxKg)) / w);
        }
        DayStop Stop(int spot, GroundDef g) => new() { Spot = spot, Ground = g.Id, Name = Grounds.ForMap(spot).Length > 1 ? $"{GameData.Spots[spot].Name} · {g.Name}" : GameData.Spots[spot].Name };

        void BuildDayCards()
        {
            DayCards.Clear();
            int home = Mathf.Clamp(SelectedSpot, 0, GameData.Spots.Length - 1);
            var open = Enumerable.Range(0, Mathf.Min(GameData.Spots.Length, SeaNav.Maps.Length))
                .Where(s => State.Known(s) && Coasts.Open(s, State.Hull) && Coasts.Of(s) == Coasts.Of(home) && Grounds.ForMap(s).Length > 0).ToList();
            if (!open.Contains(home)) open.Add(home);
            var all = open.SelectMany(s => Grounds.ForMap(s).Select(g => (stop: Stop(s, g), big: BigFish(g)))).ToList();
            var first = Grounds.ForMap(home).Length > 0 ? Stop(home, Grounds.ForMap(home)[0]) : new DayStop { Spot = home, Name = GameData.Spots[home].Name };
            DayCard Make(string kind, string title, string art, int extra, List<DayStop> stops)
            {
                var orders = Orders(stops).ToList();
                var best = orders.OrderBy(RouteFuel).First(); float worst = orders.Max(RouteFuel);
                var c = new DayCard { Kind = kind, Title = title, Art = art, ExtraGuests = extra, Fuel = RouteFuel(best), Saved = worst - RouteFuel(best) };
                c.Stops.AddRange(best);
                c.Possible = c.Fuel <= DayTank + .001f;
                // "Harbour mouth · Quay shallows" on every stop reads long; one sea is named once: "Harbour mouth: Quay shallows › Mouth flats".
                var names = c.Stops.Select(s => s.Name).ToList();
                string sea = names[0].Contains(" · ") ? names[0][..names[0].IndexOf(" · ")] : null;
                string route = sea != null && names.All(n => n.StartsWith(sea + " · "))
                    ? sea + ": " + string.Join(" › ", names.Select(n => n[(sea.Length + 3)..])) : string.Join(" › ", names);
                c.Line = !c.Possible ? $"Too far on one tank: {c.Fuel:0.#} fuel. A bigger tank would do it."
                    : c.Saved >= .5f ? $"{route}. Saves {c.Saved:0.#} fuel." : route;
                return c;
            }
            DayCards.Add(Make("easy", "Easy", "v3-daycard-easy", 0, new List<DayStop> { first }));
            // Bigger fish first: the heaviest grounds the boat can reach, never the same ground twice.
            var bigger = all.Where(a => !(a.stop.Spot == first.Spot && a.stop.Ground == first.Ground)).OrderByDescending(a => a.big).Select(a => a.stop).ToList();
            if (bigger.Count > 0)
            {
                var medium = Make("medium", "Medium", "v3-daycard-medium", 0, new List<DayStop> { first, bigger[0] });
                // If the biggest ground is out of range, Mira picks the biggest one that fits.
                if (!medium.Possible) foreach (var b in bigger.Skip(1)) { var m = Make("medium", "Medium", "v3-daycard-medium", 0, new List<DayStop> { first, b }); if (m.Possible) { medium = m; break; } }
                DayCards.Add(medium);
                DayCard hard = null;
                var far = bigger.Where(b => medium.Stops.All(m => m.Spot != b.Spot || m.Ground != b.Ground)).ToList();
                foreach (var b in far) { var h = Make("hard", "Hard", "v3-daycard-hard", 0, medium.Stops.Concat(new[] { b }).ToList()); if (h.Possible) { hard = h; break; } hard ??= h; }
                if (hard == null || !hard.Possible)
                    foreach (var pair in bigger.Take(4).SelectMany((a, i) => bigger.Take(4).Skip(i + 1).Select(b => new List<DayStop> { a, b })))
                    { var h = Make("hard", "Hard", "v3-daycard-hard", 0, pair); if (h.Possible && h.Stops.Any(s => s.Spot != first.Spot || s.Ground != first.Ground)) { hard = h; break; } }
                if (hard != null) DayCards.Add(hard);
            }
        }

        // The forecast pool for a route: every stop's ground, so tonight's guests order what the day can bring back.
        (Species species, float weight)[] RoutePool(IEnumerable<DayStop> stops) => stops
            .SelectMany(s => Grounds.ForMap(s.Spot).Where(g => s.Ground == null || g.Id == s.Ground).SelectMany(g => g.Day))
            .GroupBy(e => e.species).Select(g => (g.Key, g.Sum(e => e.weight))).ToArray();

        // Restaurant days with a choice open the cards; the first night, autoplay and a one-card day go straight to Easy.
        bool OpenDayCards()
        {
            BuildDayCards();
            DayRoute.Clear(); DayStopAt = 0;
            if (State.RestaurantNights.Count == 0 || AutoPlay || RadioAuto || DayCards.Count(c => c.Possible) <= 1) return ChooseDay(DayCards[0]);
            DayCardsOpen = true; RestaurantPhase = DayPhase.Plan; dayCardIndex = Mathf.Clamp(dayCardIndex, 0, DayCards.Count - 1);
            return true;
        }
        int dayCardIndex;

        public bool ChooseDay(DayCard card)
        {
            if (card == null || !card.Possible) return false;
            DayCardsOpen = false;
            DayRoute.Clear(); DayRoute.AddRange(card.Stops); DayStopAt = 0;
            dayExtraGuests = card.Kind == "hard" ? .6f : card.Kind == "medium" ? .3f : 0;
            dayCardKind = card.Kind;
            return RestaurantPlanForRoute();
        }
        float dayExtraGuests; string dayCardKind;

        public void CloseDayCards() { DayCardsOpen = false; DayRoute.Clear(); if (RestaurantPhase == DayPhase.Plan) RestaurantPhase = DayPhase.Off; }

        // Got it on the plan: Mira tops the tank up at the pump, then the first leg is paid as the boat leaves.
        // Returns the notebook line for the pump; RadioBeginDay clears the notebook, so RouteFirstLeg writes it after.
        string RouteDepart()
        {
            if (DayRoute.Count == 0) return null;
            string line = null;
            if (UsesFuel && State.FuelFillCost > 0 && State.Coins >= State.FuelFillCost)
            {
                int cost = State.FuelFillCost;
                if (State.BuyFuel()) line = $"Fuelled up: -{cost} coins";
            }
            SelectedSpot = DayRoute[0].Spot; routeGround = DayRoute[0].Ground;
            return line;
        }
        void RouteFirstLeg(string fuelNote)
        {
            if (DayRoute.Count == 0) return;
            if (fuelNote != null) Note(fuelNote);
            if (DayRoute.Count > 1) Note($"{DayRoute.Count} stops: " + string.Join(", ", DayRoute.Select(s => s.Name)));
            PayLeg(null, DayRoute[0]);
        }
        // The trip chart draws a hop from the last stop's pin, not from the harbour.
        int ChartTarget => hopSpot >= 0 ? hopSpot : ActiveSpot;
        int ChartFrom => hopFrom;
        void RouteHomeLeg() { if (DayRoute.Count > 0 && RestaurantPhase == DayPhase.Out) PayLeg(DayRoute[Mathf.Min(DayStopAt, DayRoute.Count - 1)], null); }
        void ClearRoute() { DayRoute.Clear(); DayStopAt = 0; routeGround = null; hopSpot = hopFrom = -1; chartHop = false; DayCardsOpen = false; }

        // ---- Next stop --------------------------------------------------------------------------------------------
        public string NextStopBlocker()
        {
            if (!HasNextStop) return "No more stops today.";
            if (CurrentMode != Mode.Fishing) return "Finish the current journey first.";
            var from = DayRoute[DayStopAt]; var to = DayRoute[DayStopAt + 1];
            if (UsesFuel && State.Fuel + .001f < LegFuel(from, to) + LegFuel(to, null)) return "Not enough fuel to get there and home, skipper.";
            return RelocateBlocker();
        }

        public bool NextStop()
        {
            var blocker = NextStopBlocker();
            if (blocker != null) { Toast(blocker); return false; }
            var from = DayRoute[DayStopAt]; var to = DayRoute[DayStopAt + 1];
            bool ok = to.Spot == ActiveSpot ? Relocate(to.Ground) : BeginHop(to.Spot);
            if (!ok) return false;
            PayLeg(from, to);
            DayStopAt++; routeGround = to.Ground;
            RadioNextLeg(to);
            audio?.Play(VoyageAudio.Cue.Select, .45f);
            return true;
        }

        // Out of this sea toward the next: sail to the edge facing it, then the chart carries the boat over.
        bool BeginHop(int spot)
        {
            if (Navigation == null || spot < 0 || spot >= SeaNav.Maps.Length) return false;
            var nav = SeaNav.Load(SeaNav.Maps[spot], State.HullDef);
            if (nav == null) return false;
            nav.SetHarbour(SeaLanes.Entry(nav, SeaLanes.HomeDirection(NauticalChartPoint(spot), ChartHarbour), out _));
            var entry = SeaLanes.Entry(nav, SeaLanes.HomeDirection(NauticalChartPoint(spot), NauticalChartPoint(ActiveSpot)), out float heading);
            hopExit = SeaLanes.Entry(Navigation, SeaLanes.HomeDirection(NauticalChartPoint(ActiveSpot), NauticalChartPoint(spot)), out _);
            if (!SailLane(hopExit)) { Toast("No clear sailing route, skipper."); return false; }
            pendingNav = nav; pendingSailor = new BoatSailor(nav, State.HullDef, entry, heading);
            hopSpot = spot; hopFrom = ActiveSpot;
            StowSeaGear(); seaRelocating = false; CurrentMode = Mode.SailingOut; Leg = TripLeg.SeaHop;
            modeTimer = 0; modeDuration = Mathf.Max(.1f, SeaNav.Length(Sailor.Route) / State.HullDef.SailSpeed);
            Captain.Rowing = State.Hull == 0; SetRowing(true);
            return true;
        }

        // Called from TickSeaTravel while the boat leaves this sea.
        bool TickHop()
        {
            if (Leg != TripLeg.SeaHop) return false;
            if (Sailor.Arrived || Vector2.Distance(Sailor.Position, hopExit) < 9f) { BeginChart(false); chartHop = true; }
            return true;
        }

        // At the chart's swap: the next sea replaces this one.
        void SwapHop()
        {
            chartHop = false;
            ActiveSpot = hopSpot; hopSpot = -1;
            laneNavs.Clear();
            foreach (float r in SeaLanes.Clearances) laneNavs.Add(SeaNav.Load(SeaNav.Maps[ActiveSpot], r));
            SwapToSea();
        }

        // ---- the cards --------------------------------------------------------------------------------------------
        void InterfaceDayCards()
        {
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Planks("day/planks", false);
            float pad = compactInterface ? 12 : 24, head = compactInterface ? 64 : 84;
            var top = coastalUi.TitledSlabV3("day/head", new Rect(pad, pad, iw - pad * 2, head));
            coastalUi.Icon("day/head/mira", new Rect(10, 6, head - 12, head - 12), MiraFace("happy"), top, null, "rx-coach-mira");
            coastalUi.Text("day/head/title", new Rect(head + 4, 2, iw - pad * 2 - head - 180, Skin.HeaderBand), "Mira's plans for today", Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, top);
            coastalUi.Text("day/head/line", new Rect(head + 4, Skin.HeaderBand + 2, iw - pad * 2 - head - 20, head - Skin.HeaderBand - 6),
                UsesFuel ? $"I'll fuel us up at the pump. The tank takes {State.FuelCapacity:0} fuel, so here's what we can do." : "Pick a day and I'll sort the rest.", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, top);
            coastalUi.Secondary("day/back", new Rect(iw - pad - 150, pad + 8, 140, Skin.HeaderBand - 14), "Back", () => { CloseDayCards(); RestaurantPreview = RestaurantScreen.None; }, "v2-icon-back");

            int n = DayCards.Count; float gap = compactInterface ? 10 : 18, y = pad + head + gap, h = ih - y - pad;
            float w = Mathf.Min(compactInterface ? 250 : 330, (iw - pad * 2 - gap * (n - 1)) / n), x0 = (iw - (w * n + gap * (n - 1))) / 2;
            for (int i = 0; i < n; i++)
            {
                var c = DayCards[i]; int index = i; bool on = i == dayCardIndex;
                var r = new Rect(x0 + i * (w + gap), y - (on ? 6 : 0), w, h);
                var card = coastalUi.Sliced($"day/card/{i}", r, c.Art, null, c.Possible ? (Color?)null : new Color(1, 1, 1, .6f));
                // The card art (kit 2) has fixed places: the coloured band at 21-31% for the title, the stop dots at 42%,
                // the fish (bigger on harder days) at 50-66%, and the ruled body below it for the details.
                float hh = r.height;
                coastalUi.Text($"day/card/{i}/kind", new Rect(w * .1f, hh * .206f, w * .8f, hh * .106f), c.Title, Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleCenter, card);
                string guests = c.Kind == "hard" ? "+60% guests" : c.Kind == "medium" ? "+30% guests" : "normal night";
                coastalUi.Text($"day/card/{i}/stops", new Rect(10, hh * .325f, w - 20, hh * .07f), (c.Stops.Count == 1 ? "1 stop" : $"{c.Stops.Count} stops") + " · " + guests,
                    Skin.Type.Small, Skin.Ink, TextAnchor.MiddleCenter, card);
                var go = new Rect(12, hh - (compactInterface ? 46 : 58), w - 24, compactInterface ? 38 : 48);
                float by = hh * .675f;
                if (UsesFuel)
                {
                    float ch = compactInterface ? 28 : 36;
                    var chip = new Rect((w - ch * 3.4f) / 2, by, ch * 3.4f, ch);
                    coastalUi.Sliced($"day/card/{i}/fuel", chip, "v3-fuel-chip", card);
                    coastalUi.Text($"day/card/{i}/fuel/t", new Rect(chip.x + chip.height, chip.y, chip.width - chip.height - 8, chip.height), $"{c.Fuel:0.#} fuel", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleCenter, card);
                    by = chip.yMax + 4;
                }
                coastalUi.Text($"day/card/{i}/line", new Rect(12, by, w - 24, Mathf.Max(0, go.y - by - 4)), c.Line, Skin.Type.Caption, c.Possible ? Skin.Ink : Skin.BadInk, TextAnchor.UpperCenter, card);
                if (c.Possible) coastalUi.Primary($"day/card/{i}/go", go, "Let's do it", () => { dayCardIndex = index; ChooseDay(c); audio?.Play(VoyageAudio.Cue.Select, .5f); }, "v2-icon-tick", true, card);
                else coastalUi.Secondary($"day/card/{i}/go", go, "Can't reach", null, "v2-icon-lock", false, card);
                if (on) coastalUi.Pose($"day/card/{i}", 0, 1 + .015f * Mathf.Sin(SimTime * 2f));
            }
        }
    }
}

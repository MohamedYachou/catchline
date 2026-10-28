using System.Collections.Generic;
using Catchline.Game.Sea;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    // The trip out and home in three legs (docs/plans/HARBOUR-PLAN.md section 2): the harbour lane past the
    // lighthouse, the chart fly-over, the sea lane on the map. No cuts: the chart fades over the 3D world and the
    // world is swapped while the chart covers it. Home is the same in reverse, ending with crates to the market.
    public partial class VoyageGame
    {
        public enum TripLeg { None, HarbourOut, ChartOut, SeaOut, SeaHome, ChartHome, HarbourIn, SeaHop } // SeaHop: leaving one sea for the day's next stop
        public TripLeg Leg { get; private set; }
        public bool TripFast;
        float TripRate => (TripFast ? 3f : 1f) * AbilityTravel * RadioPace; // RadioPace: home lasts as long as the prep (design 14.4)
        SeaNav pendingNav;
        BoatSailor pendingSailor;
        readonly List<SeaNav> laneNavs = new();

        // ---- harbour lane: dense samples; bow-in berths back out first ----
        readonly List<Vector2> lanePts = new();
        readonly List<float> laneS = new();
        float laneReverseEnd, laneMouthS, laneChartS, laneAt, laneSpeed, laneHeading;
        bool laneOutbound;
        public bool HarbourLaneActive => Leg == TripLeg.HarbourOut || Leg == TripLeg.HarbourIn || Leg == TripLeg.ChartOut && !chartSwapped;
        float LaneU => laneS.Count > 0 ? Mathf.Clamp01(laneAt / Mathf.Max(.1f, laneS[laneS.Count - 1])) : 0;
        float LaneInside => State.Hull == 0 ? 1.8f : 2.6f;
        float LaneOpen => State.Hull == 0 ? 3.6f : 6f;

        Vector2 HarbourBearing()
        {
            float dx = NauticalChartPoint(ActiveSpot).x - ChartHarbour.x;
            var right = new Vector2(Mathf.Cos(35f * Mathf.Deg2Rad), -Mathf.Sin(35f * Mathf.Deg2Rad));
            return (Vector2.down + right * (dx * 2.5f)).normalized;
        }
        static Vector2[] BerthWaypoints(Berth berth) => berth switch
        {
            Berth.Slipway => new[] { new Vector2(-18f, -11f), HarbourMouth, HarbourOutside },
            Berth.Pontoon => new[] { HarbourMouth, HarbourOutside },
            _ => new[] { HarbourBasin, HarbourMouth, HarbourOutside },
        };

        void BuildHarbourLane(bool outbound)
        {
            laneOutbound = outbound;
            var berth = BerthFor(State.Hull);
            var slot = HarbourSlot;
            var away = BerthAway(berth);
            var exit = HarbourOutside + HarbourBearing() * 14f;
            var ctrl = new List<Vector2>();
            var reverse = new List<Vector2>();
            var mid = BerthWaypoints(berth);
            if (outbound)
            {
                var bow = DockBow;
                if (BowIn(berth)) { reverse.Add(slot); reverse.Add(slot - bow * 4.5f); ctrl.Add(slot - bow * 4.5f); }
                else
                {
                    var pull = slot + bow * 3f + away * 2.5f;
                    ctrl.Add(slot); ctrl.Add(pull);
                    if (Vector2.Dot(bow, HarbourBasin - slot) < 0) ctrl.Add(pull + away * 3f);
                }
                ctrl.AddRange(mid); ctrl.Add(exit);
            }
            else
            {
                ctrl.Add(exit);
                for (int i = mid.Length - 1; i >= 0; i--) ctrl.Add(mid[i]);
                if (BowIn(berth)) ctrl.Add(slot - Vector2.up * 4.5f);
                else ctrl.Add(slot + Vector2.left * 4f + away * 2.5f);
                ctrl.Add(slot);
            }
            lanePts.Clear(); laneS.Clear();
            void Add(Vector2 p) { laneS.Add(lanePts.Count == 0 ? 0 : laneS[laneS.Count - 1] + Vector2.Distance(lanePts[lanePts.Count - 1], p)); lanePts.Add(p); }
            for (int i = 0; i < reverse.Count - 1; i++)
                for (int k = 0; k < 8; k++) Add(Vector2.Lerp(reverse[i], reverse[i + 1], k / 8f));
            laneReverseEnd = reverse.Count > 0 ? (lanePts.Count > 0 ? laneS[laneS.Count - 1] + Vector2.Distance(lanePts[lanePts.Count - 1], reverse[reverse.Count - 1]) : 0) : 0;
            laneMouthS = laneChartS = -1;
            for (int i = 0; i < ctrl.Count - 1; i++)
            {
                var p0 = ctrl[Mathf.Max(0, i - 1)]; var p1 = ctrl[i]; var p2 = ctrl[i + 1]; var p3 = ctrl[Mathf.Min(ctrl.Count - 1, i + 2)];
                int steps = Mathf.Max(4, Mathf.CeilToInt(Vector2.Distance(p1, p2) / .5f));
                for (int k = 0; k < steps; k++)
                {
                    float t = k / (float)steps, t2 = t * t, t3 = t2 * t;
                    Add(.5f * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (3 * p1 - p0 - 3 * p2 + p3) * t3));
                }
                if (ctrl[i + 1] == HarbourMouth && laneMouthS < 0) laneMouthS = laneS[laneS.Count - 1] + Vector2.Distance(lanePts[lanePts.Count - 1], p2);
                if (ctrl[i + 1] == HarbourOutside) laneChartS = laneS[laneS.Count - 1] + Vector2.Distance(lanePts[lanePts.Count - 1], p2) + 3f;
            }
            Add(ctrl[ctrl.Count - 1]);
            laneAt = 0;
            laneSpeed = outbound ? 0 : LaneOpen;
            var first = outbound ? DockBow : (lanePts[1] - lanePts[0]).normalized;
            laneHeading = Mathf.Atan2(first.y, first.x) * Mathf.Rad2Deg;
            PoseOnLane();
        }

        (Vector2 p, Vector2 tangent) LaneSample(float s)
        {
            int i = laneS.BinarySearch(s);
            if (i < 0) i = ~i;
            i = Mathf.Clamp(i, 1, lanePts.Count - 1);
            var a = lanePts[i - 1]; var b = lanePts[i];
            float u = Mathf.InverseLerp(laneS[i - 1], laneS[i], s);
            return (Vector2.Lerp(a, b, u), (b - a).normalized);
        }

        void TickHarbourLane(float dt)
        {
            float rate = TripRate, total = laneS[laneS.Count - 1];
            bool reversing = laneAt < laneReverseEnd;
            bool inside = laneOutbound ? laneAt < laneMouthS : laneAt > laneMouthS;
            float target = reversing ? .9f : inside ? LaneInside : LaneOpen;
            if (!laneOutbound) target = Mathf.Min(target, Mathf.Sqrt(2.4f * Mathf.Max(0, total - laneAt)) + .25f);
            laneSpeed = Mathf.MoveTowards(laneSpeed, target, (target > laneSpeed ? 1.6f : 2.4f) * dt * rate);
            laneAt = Mathf.Min(total, laneAt + laneSpeed * dt * rate);
            var (_, tangent) = LaneSample(laneAt);
            var want = reversing ? -tangent : tangent;
            float remaining = total - laneAt;
            if (!laneOutbound && remaining < 3f)
            {
                var dock = BowIn(BerthFor(State.Hull)) ? Vector2.up : Vector2.right;
                want = Vector2.Lerp(want, dock, 1 - remaining / 3f).normalized;
            }
            if (want.sqrMagnitude > .001f)
                laneHeading = Mathf.MoveTowardsAngle(laneHeading, Mathf.Atan2(want.y, want.x) * Mathf.Rad2Deg, 75f * dt * rate);
            PoseOnLane();
        }

        void PoseOnLane()
        {
            var (p, _) = LaneSample(laneAt);
            var c = State.HullDef.Center;
            travelOffset = new Vector3(p.x - c.x, 0, p.y - c.z);
            float h = laneHeading * Mathf.Deg2Rad;
            travelYaw = YawFor(new Vector2(Mathf.Cos(h), Mathf.Sin(h)));
            travelWake = Mathf.Clamp01(laneSpeed / LaneOpen);
        }

        // ---- the chart fly-over: fade in over the world, sail the token, fade out over the new world ----
        const float ChartFade = .9f;
        bool chartActive, chartSwapped, chartHome;
        float chartAt;
        float ChartSail => Mathf.Clamp(GameData.Spots[ActiveSpot].RowSeconds * .45f, 3f, 7f);
        public float ChartAlpha { get; private set; }
        public float ChartRoute { get; private set; }
        public float ChartZoom { get; private set; } = 1f;
        public bool ChartHomeward => chartHome;

        void BeginChart(bool home)
        {
            chartActive = true; chartSwapped = false; chartHome = home; chartAt = 0;
            ChartAlpha = 0; ChartRoute = 0; ChartZoom = 2.2f;
            Leg = home ? TripLeg.ChartHome : TripLeg.ChartOut;
            audio?.Play(VoyageAudio.Cue.Select, .35f);
        }

        void TickChart(float dt)
        {
            if (!chartActive) return;
            chartAt += dt * TripRate;
            float sailEnd = ChartFade + ChartSail, end = sailEnd + ChartFade;
            float fadeIn = Mathf.SmoothStep(0, 1, chartAt / ChartFade), fadeOut = Mathf.SmoothStep(0, 1, (chartAt - sailEnd) / ChartFade);
            ChartAlpha = chartAt < sailEnd ? fadeIn : 1 - fadeOut;
            ChartZoom = chartAt < ChartFade ? Mathf.Lerp(2.2f, 1f, fadeIn) : chartAt < sailEnd ? 1f : Mathf.Lerp(1f, 2.4f, fadeOut);
            ChartRoute = Mathf.SmoothStep(0, 1, (chartAt - ChartFade) / ChartSail);
            if (!chartSwapped && chartAt >= ChartFade)
            {
                chartSwapped = true;
                if (chartHome) SwapToHarbour(); else if (chartHop) SwapHop(); else SwapToSea();
            }
            if (chartAt >= sailEnd && (Leg == TripLeg.ChartOut || Leg == TripLeg.ChartHome))
            {
                Leg = chartHome ? TripLeg.HarbourIn : TripLeg.SeaOut;
                audio?.Play(VoyageAudio.Cue.Moor, .4f);
            }
            if (chartAt >= end) { chartActive = false; ChartAlpha = 0; ChartZoom = 1; hopFrom = -1; }
        }

        // Extra camera height while the chart covers the world: reads as lifting up to the map and diving back.
        float TripCameraLift => chartActive ? ChartAlpha * 10f : 0f;

        // ---- legs ----
        bool BeginTrip()
        {
            if (!BeginSeaVoyage()) return false;
            var home = SeaLanes.HomeDirection(NauticalChartPoint(ActiveSpot), ChartHarbour);
            var entry = SeaLanes.Entry(Navigation, home, out float heading);
            Navigation.SetHarbour(entry);
            Sailor = new BoatSailor(Navigation, State.HullDef, entry, heading);
            laneNavs.Clear();
            foreach (float r in SeaLanes.Clearances) laneNavs.Add(SeaNav.Load(SeaNav.Maps[ActiveSpot], r));
            pendingNav = Navigation; pendingSailor = Sailor;
            Navigation = null; Sailor = null;
            CurrentMode = Mode.SailingOut; seaRelocating = false; SailMode = seaHaulModal = false;
            ClearUnload();
            Captain.Stop(); Captain.Place(SeatTile);
            Hand?.Stop(); Hand?.Place(HandRest);
            foreach (var p in ExtraPeople) { p.Stop(); p.Place(RestFor(p)); }
            // After the rest places: the deck graph snaps everyone onto tiles its scheduler can route from.
            SetupDeckGraph();
            StowSeaGear();
            Captain.Rowing = State.Hull == 0; SetRowing(true);
            seaFrom = seaMat.color; seaTo = GameData.Spots[ActiveSpot].Water;
            modeTimer = 0; modeDuration = 1;
            BuildHarbourLane(true);
            Leg = TripLeg.HarbourOut;
            audio?.Play(VoyageAudio.Cue.Moor, .55f);
            return true;
        }

        void SwapToSea()
        {
            Navigation = pendingNav; Sailor = pendingSailor; pendingNav = null; pendingSailor = null;
            if (oldScenery != null) Visuals.Kill(oldScenery.gameObject);
            if (scenery != null) Visuals.Kill(scenery.gameObject);
            oldScenery = null; scenery = BuildScenery(ActiveSpot);
            BeginSeaRoute(Mode.SailingOut, false);
            snapCamera = true;
        }

        void SwapToHarbour()
        {
            FlushDeckGraph();
            if (scenery != null) Visuals.Kill(scenery.gameObject);
            scenery = BuildScenery(-1); Navigation = null; Sailor = null;
            seaMat.SetFloat("_BoatAttack_Water_DistanceBlend", 256);
            SetWaterBiome(-1);
            seaFrom = seaTo = Palette.Sea;
            BuildHarbourLane(false);
            snapCamera = true;
        }

        // Sail a lane on the sea map: the widest clearance that finds a way (docs/plans/HARBOUR-PLAN.md rule 2).
        bool SailLane(Vector2 target)
        {
            if (laneNavs.Count == 0 && Navigation != null)
                foreach (float r in SeaLanes.Clearances) laneNavs.Add(SeaNav.Load(Navigation.Map, r));
            var lane = SeaLanes.Lane(Navigation, laneNavs, Sailor.Position, Navigation.Snap(target), out _);
            return lane != null && lane.Count >= 2 ? Sailor.Follow(lane) : Sailor.SailTo(target);
        }

        void TickTrip(float dt)
        {
            TickDeckGraph(); TickDeckFish(dt);
            switch (Leg)
            {
                case TripLeg.HarbourOut:
                    TickHarbourLane(dt);
                    if (laneAt >= laneChartS) BeginChart(false);
                    break;
                case TripLeg.ChartOut:
                    if (!chartSwapped && chartHop) { if (Sailor != null && !Sailor.Arrived) { Sailor.Tick(dt); UpdateSeaTravel(); } }
                    else if (!chartSwapped) TickHarbourLane(dt);
                    break;
                case TripLeg.ChartHome:
                    if (!chartSwapped && Sailor != null && !Sailor.Arrived) { Sailor.Tick(dt); UpdateSeaTravel(); }
                    break;
                case TripLeg.HarbourIn:
                    TickHarbourLane(dt);
                    if (laneAt >= laneS[laneS.Count - 1] - .01f && !chartActive && !PrepHolds) ArriveAtBerth();
                    break;
            }
        }

        void ArriveAtBerth()
        {
            Leg = TripLeg.None;
            dockBow = BowIn(BerthFor(State.Hull)) ? Vector2.up : Vector2.right;
            Captain.Rowing = false; SetRowing(false); travelWake = 0;
            audio?.Play(VoyageAudio.Cue.Moor, .7f);
            EnterHarbour(true);
            StartUnload();
        }

        void ResetTrip()
        {
            Leg = TripLeg.None; chartActive = false; ChartAlpha = 0; ChartZoom = 1;
            pendingNav = null; pendingSailor = null; laneNavs.Clear(); TripFast = false;
        }

        public string TripStage => Leg switch
        {
            TripLeg.HarbourOut => laneAt < laneReverseEnd ? "Casting off" : laneAt < laneMouthS ? "Dead slow through the harbour" : "Past the lighthouse",
            TripLeg.ChartOut or TripLeg.ChartHome => ChartLandmark(ChartRoute, chartHome) ?? "On the chart",
            TripLeg.HarbourIn => laneAt < laneMouthS ? "Past the lighthouse" : LaneU < .9f ? "Dead slow into the harbour" : "Coming alongside",
            _ => null,
        };

        // ---- arrival: crates of the catch carried up to the market, one after another ----
        readonly List<(Transform t, Vector3 from, Vector3 to, float start)> crates = new();

        void StartUnload()
        {
            ClearUnload();
            float kg = 0; foreach (var f in State.UnsoldCatch) kg += f.Kg;
            if (kg <= 0 || scenery == null) return;
            int count = Mathf.Clamp(Mathf.CeilToInt(kg / 6f), 1, 6);
            var market = Shops.Find(s => s.tab == HudTab.Market).anchor;
            if (market == null) return;
            var lib = ArtLibrary.Get();
            var stack = market.localPosition; stack.y = HarbourQuayTop; stack += new Vector3(1.4f, 0, -1.1f);
            var from = Boat.TransformPoint(State.HullDef.Center) + Vector3.up * .5f;
            for (int i = 0; i < count; i++)
            {
                var to = scenery.TransformPoint(stack + new Vector3((i % 2) * .62f, (i / 2) * .335f, 0));
                var crate = lib?.M("FishCrate") != null ? ArtLibrary.Spawn(lib.M("FishCrate"), scenery, Vector3.zero, Quaternion.identity).transform
                    : Visuals.Box("Crate", scenery, Vector3.zero, new Vector3(.6f, .32f, .4f), Palette.DeckWoodDark).transform;
                crate.position = from;
                crate.gameObject.SetActive(false);
                crates.Add((crate, from, to, SimTime + .4f + i * .45f));
            }
        }

        void TickUnload()
        {
            for (int i = 0; i < crates.Count; i++)
            {
                var (t, from, to, start) = crates[i];
                if (t == null) continue;
                float u = Mathf.Clamp01((SimTime - start) / .8f);
                t.gameObject.SetActive(SimTime >= start);
                var p = Vector3.Lerp(from, to, Mathf.SmoothStep(0, 1, u));
                p.y += Mathf.Sin(u * Mathf.PI) * 1.2f;
                t.position = p;
                t.rotation = Quaternion.Euler(0, 180f + Mathf.Sin(u * Mathf.PI) * 25f, Mathf.Sin(u * Mathf.PI * 2) * 8f);
            }
        }

        void ClearUnload()
        {
            foreach (var c in crates) if (c.t != null) Visuals.Kill(c.t.gameObject);
            crates.Clear();
        }
    }
}

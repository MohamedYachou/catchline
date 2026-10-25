using System.Collections.Generic;
using System.Linq;
using Catchline.Game.Deck;
using Catchline.Game.Sea;
using Visuals = Catchline.Prototype.Visuals;
using UnityEngine;
using UnityEngine.EventSystems;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public SeaNav Navigation { get; private set; }
        public BoatSailor Sailor { get; private set; }
        public string ActiveGroundId { get; private set; }
        public bool AtFishingGround => Navigation == null || !SailMode && Navigation.Grounds.Any(g => g.Id == ActiveGroundId && g.Contains(Sailor.Position)) && !Navigation.InShallows(Sailor.Position);
        Transform seaSurface;
        bool seaRelocating;
        SeaNav.Ground destinationGround;

        bool BeginSeaVoyage()
        {
            Navigation = SeaNav.Load(SeaNav.Maps[ActiveSpot], State.HullDef);
            Sailor = Navigation != null ? new BoatSailor(Navigation, State.HullDef, Navigation.Harbour, Mathf.PI) : null;
            ActiveGroundId = null; seaRelocating = false; SailMode = seaHaulModal = false;
            return Navigation != null;
        }
        bool BeginSeaRoute(Mode mode, bool fresh = true)
        {
            if (Navigation == null || Sailor == null) return false;
            destinationGround = mode == Mode.SailingOut ? Navigation.Grounds.FirstOrDefault() : null;
            var target = destinationGround != null ? destinationGround.Centre : Navigation.Harbour;
            if (!SailLane(target)) { Toast("No clear sailing route, skipper."); return false; }
            if (mode == Mode.SailingOut && fresh)
            {
                if (oldScenery != null) Visuals.Kill(oldScenery.gameObject);
                if (scenery != null) Visuals.Kill(scenery.gameObject);
                oldScenery = null; scenery = BuildScenery(ActiveSpot);
                SetupDeckGraph();
            }
            CurrentMode = mode; seaRelocating = false; SailMode = seaHaulModal = false;
            modeTimer = 0; modeDuration = Mathf.Max(.1f, SeaNav.Length(Sailor.Route) / State.HullDef.SailSpeed);
            seaFrom = seaMat.color; seaTo = mode == Mode.SailingHome ? Palette.Sea : GameData.Spots[ActiveSpot].Water;
            Leg = mode == Mode.SailingHome ? TripLeg.SeaHome : fresh ? TripLeg.None : TripLeg.ChartOut;
            StowSeaGear();
            Captain.Rowing = State.Hull == 0; SetRowing(true);
            UpdateSeaTravel(); return true;
        }
        public string RelocateBlocker()
        {
            if (Navigation == null) return "Navigation chart is not ready for this sea.";
            if (CurrentMode != Mode.Fishing && CurrentMode != Mode.SailingOut) return "Finish the current journey first.";
            if (Net != NetState.Stowed || SecondNetActive && SecondNet != NetState.Stowed) return "Haul the net first, skipper.";
            if (Enumerable.Range(0, FittedDeepLineCount).Any(i => DeepLineStatus(i) != DeepLinePhase.Empty)) return "Haul the deep lines first, skipper.";
            if (NetGameActive || Captain.Carrying != null || Manning != null) return "Finish the captain's current job first.";
            return null;
        }
        public bool Relocate(string groundId)
        {
            var ground = Navigation?.Grounds.FirstOrDefault(g => g.Id == groundId);
            return ground != null && SailTo(ground.Centre, ground);
        }
        public bool SailTo(Vector2 target) => SailTo(target, null);
        bool SailTo(Vector2 target, SeaNav.Ground ground)
        {
            var blocker = RelocateBlocker();
            if (blocker != null) { Toast(blocker); return false; }
            var snapped = Navigation.Resolve(Navigation.Snap(target));
            bool beyond = !Navigation.InsideBorder(target);
            if (!SailMode && Navigation.InShallows(snapped)) { Toast("Too shallow to anchor here, skipper."); return false; }
            if (!Sailor.SailTo(snapped)) { Toast("No clear sailing route, skipper."); return false; }
            destinationGround = ground ?? Navigation.Grounds.FirstOrDefault(g => g.Contains(snapped));
            StowSeaGear(); seaRelocating = true; CurrentMode = Mode.SailingOut;
            modeTimer = 0; modeDuration = Mathf.Max(.1f, SeaNav.Length(Sailor.Route) / State.HullDef.SailSpeed);
            Captain.Rowing = State.Hull == 0; SetRowing(true);
            if (beyond) Toast("Fog's thick past the buoys, skipper.");
            return true;
        }
        void StowSeaGear()
        {
            foreach (var person in People)
                if (!workers.TryGetValue(person, out var worker) || worker.Current == null) person.Stop();
            Manning = null; AwaitingCast = false;
            foreach (var rod in Rods) rod.ResetForTrip();
            // Cancel a processing act before enabling transit policy; existing sort/haul jobs keep their claims.
            if (Scheduler != null)
            {
                foreach (var worker in workers.Values)
                    if (worker.Current?.Kind == JobKind.TableWork) Scheduler.Cancel(worker.Current);
                Scheduler.Sailing = true;
            }
        }
        void UpdateSeaTravel()
        {
            var p = Sailor.Position;
            travelOffset = new Vector3(p.x, 0, p.y) - State.HullDef.Center;
            travelYaw = 180f - Sailor.Heading * Mathf.Rad2Deg;
            travelWake = Sailor.Speed / State.HullDef.SailSpeed;
            seaMat.color = Color.Lerp(seaFrom, seaTo, SeaU);
        }
        void TickSeaTravel(float dt)
        {
            Sailor.Tick(dt); modeTimer += dt;
            UpdateSeaTravel(); TickDeckGraph(); TickDeckFish(dt);
            // Home: the chart rises over the last stretch to the map edge, then the harbour lane takes over.
            if (CurrentMode == Mode.SailingHome && (Sailor.Arrived || Vector2.Distance(Sailor.Position, Navigation.Harbour) < 9f)) { BeginChart(true); return; }
            if (!Sailor.Arrived) return;
            Captain.Rowing = false; SetRowing(false); travelWake = 0;
            if (Leg == TripLeg.SeaOut) Leg = TripLeg.None;
            SetWaterBiome(ActiveSpot);
            ActiveGroundId = destinationGround != null && destinationGround.Contains(Sailor.Position) ? destinationGround.Id : null;
            CurrentMode = Mode.Fishing; seaRelocating = false;
            if (Scheduler != null) Scheduler.Sailing = SailMode;
            if (SailMode) { Toast("Stopped. Choose Fish here inside a ground, or tap to sail on."); return; }
            AnchorSeaBoat();
            Toast(ActiveGroundId != null ? "Anchored at " + destinationGround.Name + "." : "Stopped in open water. Choose Sail to find a ground.");
        }
        void InterfaceSeaGrounds() => InterfaceSeaNavigation();

        bool HandleSeaTap(Vector2 screen)
        {
            if (!SailMode || seaHaulModal || Navigation == null || MinigameRod != null || ManagementOpen || OverHud(ToGui(screen))) return false;
            if (EventSystem.current != null)
            {
                var hits = new List<RaycastResult>();
                EventSystem.current.RaycastAll(new PointerEventData(EventSystem.current) { position = screen }, hits);
                if (hits.Count > 0) return false;
            }
            var ray = Cam.ScreenPointToRay(screen);
            if (Physics.Raycast(ray, out var hit) && hit.transform.IsChildOf(Boat)) { StopSeaBoat(); return true; }
            // Also accept the visible hull footprint where no deck collider was hit.
            if (!new Plane(Vector3.up, new Vector3(0, WaterY, 0)).Raycast(ray, out float distance)) return false;
            var p = ray.GetPoint(distance); var target = new Vector2(p.x, p.z);
            if (Vector2.Distance(target, Sailor.Position) < State.HullDef.NavigationRadius) { StopSeaBoat(); return true; }
            return SailTo(target);
        }
    }
}

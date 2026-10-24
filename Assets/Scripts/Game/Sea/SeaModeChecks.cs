#if UNITY_EDITOR
using System;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Isolated acceptance fixture; no save reads/writes and no main-project scene mutations.
        public void CheckSeaModes()
        {
            void Check(bool ok, string why) { if (!ok) throw new Exception("Sea mode: " + why); }
            void Arrive()
            {
                for (float t = 0; CurrentMode != Mode.Fishing && t < 120; t += .05f) Tick(.05f);
                Check(CurrentMode == Mode.Fishing && Sailor.Arrived, "arrives safely");
            }
            Check(SessionOnly, "fixture must be save-isolated");
            showTitle = paused = false; SetSail(); Arrive();
            Check(!SailMode && AtFishingGround, "default arrival is Fishing");
            for (int i = 0; i < 80; i++) Visual(.05f);
            Check(Mathf.Abs(Cam.orthographicSize - 3.2f) < .05f, "normal anchored framing preserved");
            var before = Sailor.Position;
            Check(!HandleSeaTap(new Vector2(720, 450)) && Sailor.Position == before, "water taps ignored in Fishing");
            Check(RequestSailMode() && SailMode && !AtFishingGround && Scheduler.Sailing, "Sail mode stows gear and disables fishing");
            PrepareInterface(1440, 900);
            Check(FishHere(), "stopped inside zone can drop anchor");
            Check(!SailMode && AtFishingGround, "Fish here returns to Fishing");
            RequestSailMode();
            Check(SailTo(Navigation.Grounds[1].Centre), "Sail mode starts real route");
            for (int i = 0; i < 20; i++) Tick(.05f);
            Check(!FishHere(), "cannot fish during motion");
            Check(SailTo(Navigation.Grounds[2].Centre), "can reroute while moving");
            StopSeaBoat(); Check(SailMode && Sailor.Arrived && Sailor.Route == null && Sailor.Speed == 0, "tap boat stops and clears route");
            Check(SailTo(Navigation.Grounds[1].Centre), "can resume after stop"); Arrive();
            Check(SailMode && !AtFishingGround && FishHere() && AtFishingGround, "arrival stays in Sail until Fish here");
            Net = NetState.Soaking;
            Check(!RequestSailMode() && seaHaulModal && !SailMode, "deployed net opens modal before moving");
            PrepareInterface(844, 390);
            Check(InvokeInterface("sea/haul/secondary") && !seaHaulModal && Net == NetState.Soaking, "haul option preserves deployed gear");
            RequestSailMode(); PrepareInterface(844, 390);
            Check(InvokeInterface("sea/haul/primary") && SailMode && Net == NetState.Stowed, "forfeit option stows gear and enters Sail");
            Check(SailTo(new Vector2(10000, 10000)) && Navigation.InsideBorder(Sailor.Route.Last()), "outside tap snaps inside");
            Arrive(); StopSeaBoat(); Check(!FishHere(), "open-water Fish here disabled");
            for (int i = 0; i < 80; i++) Visual(.05f);
            var view = Cam.WorldToViewportPoint(Boat.TransformPoint(State.HullDef.Center));
            Check(view.x > .2f && view.x < .8f && view.y > .2f && view.y < .8f, "camera clamp keeps border hull in frame");
            Debug.Log("[Catchline] SEA MODE CHECKS PASSED: Fishing tap guard, Sail/Fish controls, reroute/stop, arrival, modal choices, border snapping; native gestures pending");
        }
    }
}
namespace Catchline.EditorTools
{
    public static partial class SeaModeChecks
    {
        public static void Run()
        {
            UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.EmptyScene);
            var g = new GameObject("Save-isolated sea modes").AddComponent<Catchline.Game.VoyageGame>();
            g.SessionOnly = true; g.Build();
            try { g.CheckSeaModes(); }
            finally { UnityEngine.Object.DestroyImmediate(g.gameObject); }
        }
    }
}
#endif

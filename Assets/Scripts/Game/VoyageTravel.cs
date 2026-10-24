using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Boat stays in the camera's small stage; scenery travels along the chart bearing.
        public static Vector3 RouteDirection(int spot) => (spot switch
        {
            1 => new Vector3(-.72f, 0, -.70f),
            2 => new Vector3(.72f, 0, -.70f),
            3 => new Vector3(-.98f, 0, -.20f),
            4 => new Vector3(.20f, 0, -.98f),
            _ => new Vector3(-.25f, 0, -.97f)
        }).normalized;

        public float TravelProgress => Mathf.Clamp01(modeTimer / Mathf.Max(.1f, modeDuration));
        public string TravelStage => Navigation != null
            ? CurrentMode == Mode.SailingHome ? "Following the route home" : seaRelocating ? "Sailing to the marked water" : "Following the route to the ground"
            : CurrentMode == Mode.SailingOut
            ? TravelProgress < .18f ? "Casting off · clearing the quay" : TravelProgress < .34f ? "Turning toward the channel" : TravelProgress < .82f ? "Following the coast" : "Settling at the fishing ground"
            : TravelProgress < .15f ? "Turning for Gull Harbour" : TravelProgress < .72f ? "Following the channel home" : TravelProgress < .86f ? "Lining up alongside" : "Sliding gently into the berth";

        Vector3 travelOffset;
        float travelYaw, travelWake;
        static float Segment(float u, float start, float end) => Mathf.SmoothStep(0, 1, Mathf.InverseLerp(start, end, u));

        void UpdateTravel()
        {
            float u = TravelProgress;
            bool home = CurrentMode == Mode.SailingHome;
            var direction = RouteDirection(ActiveSpot) * (home ? -1f : 1f);
            float heading = Mathf.Atan2(direction.z, -direction.x) * Mathf.Rad2Deg;
            float cruise = home ? Segment(u, .15f, .72f) : Segment(u, .34f, .82f);
            // Both sets flow past the stern. A fixed camera-up arrival vector
            // made the world move toward the bow and read as travelling backwards.
            if (oldScenery != null) oldScenery.localPosition = -direction * (30f * cruise);
            scenery.localPosition = direction * (30f * (1f - cruise));
            float clear = home ? 1f - Segment(u, .86f, 1f) : Segment(u, 0, .18f) * (1f - Segment(u, .62f, .82f));
            travelOffset = Vector3.back * (1.35f * clear);
            float turn = home ? Segment(u, 0, .15f) * (1f - Segment(u, .72f, .86f))
                              : Segment(u, .18f, .34f) * (1f - Segment(u, .82f, 1f));
            travelYaw = Mathf.LerpAngle(0, heading, turn);
            travelWake = Mathf.Sin(cruise * Mathf.PI);
            seaMat.color = Color.Lerp(seaFrom, seaTo, cruise);
        }
    }
}

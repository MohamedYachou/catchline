using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // Boats coming and going (harbour plan to-do): now and then a visiting skiff motors in through the mouth, swings
    // round the open basin clear of every berth and the captain's lane, and heads back out to sea. Scenery only: it
    // has no collision and only runs while the captain is in harbour.
    public partial class VoyageGame
    {
        static readonly Vector2[] TrafficRoute =
        {
            new(-6.5f, -30f), HarbourMouth, new(-4.5f, -9f), new(-.5f, -6f), new(3f, -7.5f), new(1.5f, -10.2f),
            new(-3f, -11f), HarbourMouth + new Vector2(1.2f, 0), new(-5.3f, -30f),
        };
        const float TrafficSpeed = 2.4f;
        readonly List<Vector3> trafficPath = new();
        Transform trafficBoat;
        Quaternion trafficTurn;
        float trafficWait = 6, trafficDistance = -1, trafficLength;

        void UpdateHarbourTraffic(float dt)
        {
            bool harbour = CurrentMode == Mode.Harbour && scenery != null;
            if (!harbour) { if (trafficBoat != null) trafficBoat.gameObject.SetActive(false); trafficDistance = -1; return; }
            if (trafficDistance < 0)
            {
                if ((trafficWait -= dt) > 0) return;
                trafficDistance = 0;
            }
            if (!EnsureTrafficBoat()) { trafficDistance = -1; trafficWait = 30; return; }
            trafficDistance += dt * TrafficSpeed;
            if (trafficDistance >= trafficLength)
            {
                trafficBoat.gameObject.SetActive(false); trafficDistance = -1; trafficYaw = float.NaN; trafficWait = Random.Range(25f, 55f);
                return;
            }
            PlaceTraffic(trafficDistance);
        }

        // For renders and checks: put the visitor at a fraction of its round trip.
        public void ShowHarbourTraffic(float u)
        {
            if (!EnsureTrafficBoat()) return;
            trafficDistance = Mathf.Clamp01(u) * trafficLength; trafficYaw = float.NaN; PlaceTraffic(trafficDistance);
        }

        bool EnsureTrafficBoat()
        {
            if (trafficBoat != null && trafficBoat.parent == scenery) return true;
            var prefab = ArtLibrary.Get()?.M("Skiff_VariantYellow");
            if (prefab == null || scenery == null) return false;
            var go = ArtLibrary.Spawn(prefab, scenery, Vector3.zero, prefab.transform.localRotation);
            go.name = "Visiting skiff";
            // Bow axis as MoorBoats reads it: hull-kit boats point down -X, the older harbour variants lie along Z.
            var b = new Bounds(); bool any = false;
            foreach (var r in go.GetComponentsInChildren<Renderer>()) { if (any) b.Encapsulate(r.bounds); else { b = r.bounds; any = true; } }
            var bow = b.size.z > b.size.x ? Vector3.forward : Vector3.left;
            trafficTurn = Quaternion.Inverse(Quaternion.LookRotation(bow)) * prefab.transform.localRotation;
            // A seated helmsman at the stern by the outboard, facing forward.
            var helm = ArtLibrary.Get().M("NPC_Sitting");
            if (helm != null)
            {
                var stern = b.center - bow * (Vector3.Scale(b.extents, bow).magnitude * .5f);
                var man = ArtLibrary.Spawn(helm, null, Vector3.zero, Quaternion.identity);
                man.transform.SetPositionAndRotation(new Vector3(stern.x, b.min.y + .5f, stern.z), Quaternion.LookRotation(bow) * helm.transform.localRotation);
                man.transform.SetParent(go.transform, true);
            }
            trafficBoat = go.transform;

            trafficPath.Clear();
            for (int i = 0; i < TrafficRoute.Length - 1; i++)
                for (int k = 0; k < 8; k++)
                {
                    Vector2 P(int j) => TrafficRoute[Mathf.Clamp(j, 0, TrafficRoute.Length - 1)];
                    float t = k / 8f, t2 = t * t, t3 = t2 * t;
                    var p = .5f * (2 * P(i) + (-P(i - 1) + P(i + 1)) * t + (2 * P(i - 1) - 5 * P(i) + 4 * P(i + 1) - P(i + 2)) * t2
                        + (-P(i - 1) + 3 * P(i) - 3 * P(i + 1) + P(i + 2)) * t3);
                    trafficPath.Add(new Vector3(p.x, 0, p.y));
                }
            var last = TrafficRoute[TrafficRoute.Length - 1]; trafficPath.Add(new Vector3(last.x, 0, last.y));
            trafficLength = 0;
            for (int i = 1; i < trafficPath.Count; i++) trafficLength += Vector3.Distance(trafficPath[i - 1], trafficPath[i]);
            return true;
        }

        Vector3 TrafficPoint(float distance)
        {
            distance = Mathf.Clamp(distance, 0, trafficLength);
            for (int i = 1; i < trafficPath.Count; i++)
            {
                float step = Vector3.Distance(trafficPath[i - 1], trafficPath[i]);
                if (distance <= step || i == trafficPath.Count - 1) return Vector3.Lerp(trafficPath[i - 1], trafficPath[i], step > 0 ? distance / step : 0);
                distance -= step;
            }
            return trafficPath[trafficPath.Count - 1];
        }

        float trafficYaw = float.NaN, trafficLean;

        void PlaceTraffic(float distance)
        {
            trafficBoat.gameObject.SetActive(true);
            var at = TrafficPoint(distance);
            // Heading from the curve's tangent over a boat length, not the 1 m polyline segments (those snapped the bow
            // round the basin turn in 20-30 degree steps), then eased so the hull swings round like a real boat.
            var dir = TrafficPoint(distance + .9f) - TrafficPoint(distance - .9f);
            float time = Time.time, dt = Mathf.Max(Time.deltaTime, 1e-4f);
            if (dir.sqrMagnitude > 1e-6f)
            {
                float target = Mathf.Atan2(dir.x, dir.z) * Mathf.Rad2Deg;
                float prev = trafficYaw;
                trafficYaw = float.IsNaN(trafficYaw) || distance < .05f ? target : Mathf.LerpAngle(trafficYaw, target, 1 - Mathf.Exp(-dt * 6f));
                // Lean a little into the turn (outboard skiff heel), eased the same way.
                float turnRate = float.IsNaN(prev) ? 0 : Mathf.DeltaAngle(prev, trafficYaw) / dt;
                trafficLean = Mathf.Lerp(trafficLean, Mathf.Clamp(-turnRate * .12f, -7f, 7f), 1 - Mathf.Exp(-dt * 3f));
            }
            trafficBoat.localPosition = at + Vector3.up * (.04f * Mathf.Sin(time * 1.7f));
            if (!float.IsNaN(trafficYaw))
                trafficBoat.localRotation = Quaternion.Euler(0, trafficYaw, 0) * Quaternion.Euler(0, 0, trafficLean + 2f * Mathf.Sin(time * 1.3f)) * trafficTurn;
        }
    }
}

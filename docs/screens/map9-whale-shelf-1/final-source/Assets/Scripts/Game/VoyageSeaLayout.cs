using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Permanent open water along the entire fore/aft axis. Reserve for future
        // boats as well as today's hull; never decorate the centre or either end.
        public const float FishingWaterHalfWidth = 4.8f;

        void OrientFishingCoast(GameObject environment, Transform parent)
        {
            var t = environment.transform;
            var pivot = State.HullDef.Center;
            var turn = Quaternion.Euler(0, 90, 0);
            t.localPosition = pivot + turn * (t.localPosition - pivot);
            t.localRotation = turn * t.localRotation;
        }

        void ReserveFishingWater(Transform root)
        {
            // Include piers, piles, props, rocks and shallow obstructions. The old
            // terrain-name filter missed the pier projecting into the boat.
            float nearest = float.PositiveInfinity;
            float surface = WaterY - .2f;
            foreach (var mf in root.GetComponentsInChildren<MeshFilter>())
            {
                if (mf.sharedMesh == null) continue;
                if (!mf.sharedMesh.isReadable)
                {
                    // Future art must still fail safe in a standalone player.
                    // Bounds are conservative; delivered maps retain readable meshes
                    // for the more precise clipped-surface check below.
                    var bounds = mf.sharedMesh.bounds;
                    float low = float.PositiveInfinity, high = float.NegativeInfinity;
                    var transform = root.worldToLocalMatrix * mf.transform.localToWorldMatrix;
                    for (int corner = 0; corner < 8; corner++)
                    {
                        var point = transform.MultiplyPoint3x4(bounds.center + Vector3.Scale(bounds.extents,
                            new Vector3((corner & 1) == 0 ? -1 : 1, (corner & 2) == 0 ? -1 : 1, (corner & 4) == 0 ? -1 : 1)));
                        low = Mathf.Min(low, point.z); high = Mathf.Max(high, point.y);
                    }
                    if (high >= surface) nearest = Mathf.Min(nearest, low);
                    continue;
                }
                var vertices = mf.sharedMesh.vertices;
                var points = new Vector3[vertices.Length];
                var matrix = root.worldToLocalMatrix * mf.transform.localToWorldMatrix;
                for (int i = 0; i < vertices.Length; i++)
                {
                    points[i] = matrix.MultiplyPoint3x4(vertices[i]);
                    if (points[i].y >= surface) nearest = Mathf.Min(nearest, points[i].z);
                }
                // A shore/pile triangle can cross the surface between vertices.
                // Clip its edges too, so submerged vertices cannot hide an intrusion.
                var triangles = mf.sharedMesh.triangles;
                for (int i = 0; i < triangles.Length; i += 3)
                    for (int edge = 0; edge < 3; edge++)
                    {
                        var a = points[triangles[i + edge]];
                        var b = points[triangles[i + (edge + 1) % 3]];
                        if ((a.y < surface) == (b.y < surface)) continue;
                        float z = Mathf.Lerp(a.z, b.z, (surface - a.y) / (b.y - a.y));
                        nearest = Mathf.Min(nearest, z);
                    }
            }
            if (float.IsInfinity(nearest)) return;
            float halfWidth = Mathf.Max(FishingWaterHalfWidth, State.HullDef.Height * State.HullDef.CellSize * .5f + 2f);
            float shift = Mathf.Max(0, State.HullDef.Center.z + halfWidth - nearest);
            // Move the complete diorama together: dock furniture stays on its pier.
            foreach (Transform child in root) child.localPosition += Vector3.forward * shift;
        }
    }
}

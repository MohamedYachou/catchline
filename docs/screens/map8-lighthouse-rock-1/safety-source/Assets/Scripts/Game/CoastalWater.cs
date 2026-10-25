using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.Game
{
    // Bounded surface: moving normals, depth/refraction, small geometric waves.
    public sealed class CoastalWater : MonoBehaviour
    {
        Mesh surface;
        public static GameObject Build(Transform parent, Material material)
        {
            var go = new GameObject("Sea");
            go.transform.SetParent(parent, false);
            go.transform.localPosition = new Vector3(0f, -.32f, 0f);
            var owner = go.AddComponent<CoastalWater>();
            const int cells = 224;
            const float size = 64f;
            var vertices = new Vector3[(cells + 1) * (cells + 1)];
            var triangles = new int[cells * cells * 6];
            for (int z = 0; z <= cells; z++)
                for (int x = 0; x <= cells; x++)
                    vertices[z * (cells + 1) + x] = new Vector3(Coordinate(x), 0, Coordinate(z));
            float Coordinate(int i) => size * .5f * (float)(System.Math.Sinh((2.0 * i / cells - 1) * 2) / System.Math.Sinh(2));
            int t = 0;
            for (int z = 0; z < cells; z++)
                for (int x = 0; x < cells; x++)
                {
                    int a = z * (cells + 1) + x;
                    triangles[t++] = a; triangles[t++] = a + cells + 1; triangles[t++] = a + 1;
                    triangles[t++] = a + 1; triangles[t++] = a + cells + 1; triangles[t++] = a + cells + 2;
                }
            owner.surface = new Mesh { name = "Coastal sea surface", vertices = vertices, triangles = triangles };
            owner.surface.bounds = new Bounds(Vector3.zero, new Vector3(size, 1f, size));
            go.AddComponent<MeshFilter>().sharedMesh = owner.surface;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            return go;
        }

        void OnDestroy() { if (surface != null) Prototype.Visuals.Kill(surface); }
    }
}

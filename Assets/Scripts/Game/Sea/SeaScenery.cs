using System.Collections.Generic;
using Catchline.Game.Sea;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        SeaEnvironment seaEnvironment;

        void BuildNavigableSea(Transform root, ArtLibrary library)
        {
            var model = library?.M(Navigation.ModelId);
            if (model == null) Debug.LogError("[Catchline] Missing sea model: " + Navigation.ModelId);
            else Put(root, model, new Vector3(0, WaterY, 0));
            seaEnvironment = root.gameObject.AddComponent<SeaEnvironment>();
            seaEnvironment.Build(Navigation, seaSurface, seaMat);
            SetWaterBiome(ActiveSpot);
        }

        void UpdateNavigableSeaVisual(float dt)
        {
            if (Navigation == null || Sailor == null) return;
            Cam.farClipPlane = 1600;
            seaEnvironment?.Follow(Sailor.Position);
        }
    }

    // The authored map already contains the marker buoys and unreachable horizon scenery.
    // Extend the detailed 64m surface without stacking transparent water over it.
    public sealed class SeaEnvironment : MonoBehaviour
    {
        readonly List<Mesh> meshes = new();
        Material overlay;
        GameObject ocean;
        SeaNav nav;
        bool previousFog;
        FogMode previousMode;
        Color previousColor;
        float previousDensity;

        public void Build(SeaNav navigation, Transform surface, Material water)
        {
            nav = navigation;
            previousFog = RenderSettings.fog; previousMode = RenderSettings.fogMode;
            previousColor = RenderSettings.fogColor; previousDensity = RenderSettings.fogDensity;
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = new Color(.67f, .77f, .78f);
            ocean = new GameObject("Water to horizon"); ocean.transform.SetParent(surface, false);
            var vertices = new List<Vector3>(); var triangles = new List<int>();
            const int side = 224, perimeter = side * 4;
            float Coordinate(int i) => 32f * (float)(System.Math.Sinh((2.0 * i / side - 1) * 2) / System.Math.Sinh(2));
            float[] rings = { 32, 64, 128, 256, 512, 2048 };
            foreach (float radius in rings)
                for (int edge = 0; edge < 4; edge++)
                    for (int i = 0; i < side; i++)
                    {
                        float p = Coordinate(i) * radius / 32;
                        vertices.Add(edge == 0 ? new Vector3(p, 0, -radius) : edge == 1 ? new Vector3(radius, 0, p)
                            : edge == 2 ? new Vector3(-p, 0, radius) : new Vector3(-radius, 0, -p));
                    }
            for (int r = 0; r < rings.Length - 1; r++)
                for (int i = 0; i < perimeter; i++)
                {
                    int a = r * perimeter + i, b = r * perimeter + (i + 1) % perimeter;
                    triangles.AddRange(new[] { a, b + perimeter, b, a, a + perimeter, b + perimeter });
                }
            AddMesh(ocean, "Ocean annulus", vertices.ToArray(), triangles.ToArray(), null, water);

            overlay = new Material(Resources.Load<Shader>("SeaOverlay"));
            var bounds = nav.CameraBounds;
            float xMin = bounds.xMin - 60, zMin = bounds.yMin - 60;
            int nx = Mathf.CeilToInt((bounds.width + 120) / 4), nz = Mathf.CeilToInt((bounds.height + 120) / 4);
            var points = new Vector3[(nx + 1) * (nz + 1)]; var colors = new Color[points.Length];
            var indices = new List<int>();
            for (int z = 0; z <= nz; z++)
                for (int x = 0; x <= nx; x++)
                {
                    int i = z * (nx + 1) + x;
                    var p = new Vector2(xMin + 4 * x, zMin + 4 * z);
                    points[i] = new Vector3(p.x, -.23f, p.y);
                    float t = nav.InsideBorder(p) ? Mathf.SmoothStep(0, 1, 1 - nav.BorderDistance(p) / 30) : 1;
                    colors[i] = new Color(.06f, .20f, .25f, .58f * t);
                    if (x == nx || z == nz) continue;
                    indices.AddRange(new[] { i, i + nx + 1, i + 1, i + 1, i + nx + 1, i + nx + 2 });
                }
            var shade = new GameObject("Outer water darkening"); shade.transform.SetParent(transform, false);
            AddMesh(shade, "Thirty metre border gradient", points, indices.ToArray(), colors, overlay);
        }

        void AddMesh(GameObject go, string label, Vector3[] points, int[] triangles, Color[] colors, Material material)
        {
            var mesh = new Mesh { name = label, vertices = points, triangles = triangles };
            if (colors != null) mesh.colors = colors;
            mesh.RecalculateBounds(); meshes.Add(mesh);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var renderer = go.AddComponent<MeshRenderer>(); renderer.sharedMaterial = material;
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
        }

        public void Follow(Vector2 boat)
        {
            float border = Mathf.Clamp01(1 - nav.BorderDistance(boat) / 30);
            RenderSettings.fogDensity = Mathf.Lerp(.0012f, .022f, border * border);
        }

        void OnDestroy()
        {
            if (ocean != null) Prototype.Visuals.Kill(ocean);
            foreach (var mesh in meshes) if (mesh != null) Prototype.Visuals.Kill(mesh);
            if (overlay != null) Prototype.Visuals.Kill(overlay);
            RenderSettings.fog = previousFog; RenderSettings.fogMode = previousMode;
            RenderSettings.fogColor = previousColor; RenderSettings.fogDensity = previousDensity;
        }
    }
}

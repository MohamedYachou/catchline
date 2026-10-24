using System.Collections.Generic;
using Catchline.Game.Sea;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        SeaEnvironment seaEnvironment;
        SeaSailingEffects seaEffects;

        void BuildNavigableSea(Transform root, ArtLibrary library)
        {
            var model = library?.M(Navigation.ModelId);
            if (model == null) Debug.LogError("[Catchline] Missing sea model: " + Navigation.ModelId);
            else Put(root, model, new Vector3(0, WaterY, 0));
            seaEnvironment = root.gameObject.AddComponent<SeaEnvironment>();
            seaEnvironment.Build(Navigation, seaSurface, seaMat);
            var effects = new GameObject("Sailing route and wake"); effects.transform.SetParent(root, false);
            seaEffects = effects.AddComponent<SeaSailingEffects>(); seaEffects.Build();
            SetWaterBiome(ActiveSpot);
        }

        void UpdateNavigableSeaVisual(float dt)
        {
            if (Navigation == null || Sailor == null) return;
            Cam.farClipPlane = 1600;
            seaEnvironment?.Follow(Sailor.Position);
            if (seaEffects != null && seaEffects.Draw(Sailor, SailMode || !Sailor.Arrived, dt, Cues == null))
                Toast("Shallows · half speed. Mind the hull, skipper.");
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
        static SeaEnvironment active;
        bool previousFog;
        FogMode previousMode;
        Color previousColor;
        float previousDensity;

        public void Build(SeaNav navigation, Transform surface, Material water)
        {
            nav = navigation;
            // Scene replacement destroys the previous root at frame end. Carry
            // its baseline forward so deferred destruction cannot undo the new fog.
            if (active != null)
            {
                previousFog = active.previousFog; previousMode = active.previousMode;
                previousColor = active.previousColor; previousDensity = active.previousDensity;
            }
            else
            {
                previousFog = RenderSettings.fog; previousMode = RenderSettings.fogMode;
                previousColor = RenderSettings.fogColor; previousDensity = RenderSettings.fogDensity;
            }
            active = this;
            water.SetFloat("_BoatAttack_Water_DistanceBlend", 4096);
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = new Color(.67f, .77f, .78f);
            ocean = new GameObject("Water to horizon"); ocean.transform.SetParent(surface, false);
            var vertices = new List<Vector3>(); var triangles = new List<int>();
            const int side = 224, perimeter = side * 4;
            float Coordinate(int i) => 32f * (float)(System.Math.Sinh((2.0 * i / side - 1) * 2) / System.Math.Sinh(2));
            // Closely spaced inner rings keep vertex fog/waves smooth at wide zoom.
            var rings = new List<float>();
            for (float r = 32; r < 2048; r *= 1.18f) rings.Add(r);
            rings.Add(2048);
            foreach (float radius in rings)
                for (int edge = 0; edge < 4; edge++)
                    for (int i = 0; i < side; i++)
                    {
                        float p = Coordinate(i) * radius / 32;
                        vertices.Add(edge == 0 ? new Vector3(p, 0, -radius) : edge == 1 ? new Vector3(radius, 0, p)
                            : edge == 2 ? new Vector3(-p, 0, radius) : new Vector3(-radius, 0, -p));
                    }
            for (int r = 0; r < rings.Count - 1; r++)
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
            // Continue the edge tint beyond the sampled gradient. A finite tinted
            // rectangle would otherwise be visible as a hard seam at wide zoom.
            float xMax = xMin + nx * 4, zMax = zMin + nz * 4;
            var outside = new List<Vector3>(); var outsideIndices = new List<int>();
            void Strip(float left, float bottom, float right, float top)
            {
                int start = outside.Count;
                outside.AddRange(new[] { new Vector3(left, -.23f, bottom), new Vector3(right, -.23f, bottom),
                    new Vector3(right, -.23f, top), new Vector3(left, -.23f, top) });
                outsideIndices.AddRange(new[] { start, start + 1, start + 2, start, start + 2, start + 3 });
            }
            Strip(-4096, -4096, xMin, 4096); Strip(xMax, -4096, 4096, 4096);
            Strip(xMin, -4096, xMax, zMin); Strip(xMin, zMax, xMax, 4096);
            var beyond = new GameObject("Dark water beyond buoys"); beyond.transform.SetParent(transform, false);
            var outsideColors = new Color[outside.Count];
            for (int i = 0; i < outsideColors.Length; i++) outsideColors[i] = new Color(.06f, .20f, .25f, .58f);
            AddMesh(beyond, "Continuous outer sea tint", outside.ToArray(), outsideIndices.ToArray(), outsideColors, overlay);
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
            if (active == this)
            {
                active = null;
                RenderSettings.fog = previousFog; RenderSettings.fogMode = previousMode;
                RenderSettings.fogColor = previousColor; RenderSettings.fogDensity = previousDensity;
            }
        }
    }
}

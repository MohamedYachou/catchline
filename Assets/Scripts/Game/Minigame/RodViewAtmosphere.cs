using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
using Visuals = Catchline.Prototype.Visuals;

namespace Catchline.Game
{
    // Scoped to one captain cast. Never changes the sea model or navigation data.
    sealed class RodViewAtmosphere
    {
        readonly Transform sky, wake;
        readonly Material skyMaterial, cueMaterial;
        readonly List<(Renderer renderer, bool hidden)> overlays = new();
        readonly HashSet<Renderer> recorded = new();
        readonly Transform scene;
        readonly bool fog;
        readonly Color fogColor;
        readonly float fogDensity;
        readonly FogMode fogMode;
        readonly MaterialPropertyBlock cueBlock = new();
        readonly List<Renderer> discovered = new();
        readonly List<Renderer> cueRenderers = new();
        float nextScan = float.NegativeInfinity;

        public RodViewAtmosphere(Transform parent, Transform scene, Vector3 seaward)
        {
            this.scene = scene;
            fog = RenderSettings.fog; fogColor = RenderSettings.fogColor;
            fogDensity = RenderSettings.fogDensity; fogMode = RenderSettings.fogMode;
            skyMaterial = new Material(Resources.Load<Shader>("RodViewSky"));
            skyMaterial.SetFloat("_CloudHeading", Mathf.Atan2(seaward.z, seaward.x));
            cueMaterial = new Material(Resources.Load<Shader>("RodViewCue"));
            var dome = GameObject.CreatePrimitive(PrimitiveType.Quad);
            dome.name = "Rod view sky and soft clouds"; sky = dome.transform;
            sky.SetParent(parent, false);
            Visuals.Kill(dome.GetComponent<Collider>());
            var renderer = dome.GetComponent<Renderer>(); renderer.sharedMaterial = skyMaterial;
            renderer.shadowCastingMode = ShadowCastingMode.Off; renderer.receiveShadows = false;
            wake = Ring(parent, "Bobber drift wake", .022f);
        }

        public Transform BuildBobber(Transform parent)
        {
            var root = new GameObject("Bobber reading").transform; root.SetParent(parent, false);
            // A broad orange cap stays legible on a landscape phone. All dimensions are metres.
            Visuals.Prim(PrimitiveType.Sphere, "Orange float cap", root,
                Vector3.up * .105f, new Vector3(.16f, .19f, .16f), Palette.Hex("FF681F"));
            Visuals.Prim(PrimitiveType.Sphere, "Ivory float waist", root,
                Vector3.up * .015f, new Vector3(.145f, .12f, .145f), Palette.Hex("FFF0CD"));
            Visuals.Prim(PrimitiveType.Cylinder, "Navy float stem", root,
                Vector3.down * .07f, new Vector3(.035f, .085f, .035f), Palette.HullNavy);
            return root;
        }

        public void Update(Camera camera, Vector3 bob, float waterY, bool floating, float clock)
        {
            // Discover any cues created after the cast began, keeping each renderer's prior state.
            if (clock >= nextScan)
            {
                nextScan = clock + .2f;
                scene.GetComponentsInChildren(true, discovered);
                foreach (var renderer in discovered)
                    if ((renderer.name == "Ground ring" || renderer.GetComponent<SeaSailingEffects>() != null) && recorded.Add(renderer))
                        overlays.Add((renderer, renderer.forceRenderingOff));
            }
            foreach (var item in overlays) if (item.renderer != null) item.renderer.forceRenderingOff = true;
            // A camera-facing backdrop stays within the clip range throughout the cast.
            float distance = camera.farClipPlane * .9f;
            float height = camera.orthographic ? camera.orthographicSize * 2 :
                2 * distance * Mathf.Tan(camera.fieldOfView * .5f * Mathf.Deg2Rad);
            sky.SetPositionAndRotation(camera.transform.position + camera.transform.forward * distance, camera.transform.rotation);
            sky.localScale = new Vector3(height * Mathf.Max(camera.aspect, 2.4f) * 1.01f, height * 1.01f, 1); // wide enough for any screen, even before the aspect settles
            skyMaterial.SetFloat("_Clock", clock);
            RenderSettings.fog = true; RenderSettings.fogMode = FogMode.ExponentialSquared;
            RenderSettings.fogColor = Palette.Hex("B9DAD8");
            RenderSettings.fogDensity = Mathf.Max(.0045f, fogDensity);
            wake.gameObject.SetActive(floating);
            wake.position = new Vector3(bob.x, waterY + .045f, bob.z);
            wake.localScale = Vector3.one * (.19f + Mathf.Sin(clock * 2) * .025f);
        }

        public Transform Ring(Transform parent, string name, float width)
        {
            var go = new GameObject(name); go.transform.SetParent(parent, false);
            var ring = go.AddComponent<LineRenderer>(); ring.useWorldSpace = false;
            ring.positionCount = 49; ring.widthMultiplier = width; ring.sharedMaterial = cueMaterial;
            ring.shadowCastingMode = ShadowCastingMode.Off; ring.receiveShadows = false;
            for (int i = 0; i <= 48; i++)
            { float a = i * Mathf.PI * 2 / 48; ring.SetPosition(i, new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a))); }
            return go.transform;
        }

        public void StyleCue(Transform effect, float alpha)
        {
            cueBlock.SetColor("_Tint", new Color(.67f, .94f, .91f, alpha));
            effect.GetComponentsInChildren(false, cueRenderers);
            foreach (var renderer in cueRenderers)
            { if (renderer.sharedMaterial != cueMaterial) renderer.sharedMaterial = cueMaterial; renderer.SetPropertyBlock(cueBlock); }
        }

        public void Dispose()
        {
            foreach (var item in overlays)
                if (item.renderer != null) item.renderer.forceRenderingOff = item.hidden;
            RenderSettings.fog = fog; RenderSettings.fogMode = fogMode;
            RenderSettings.fogColor = fogColor; RenderSettings.fogDensity = fogDensity;
            Visuals.Kill(skyMaterial); Visuals.Kill(cueMaterial);
        }
    }
}

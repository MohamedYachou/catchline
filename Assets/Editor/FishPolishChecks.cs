using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class FishPolishChecks
    {
        static void Check(bool ok, string why) { if (!ok) throw new Exception("FISH POLISH: " + why); }
        static void Visual(VoyageGame g) => typeof(VoyageGame).GetMethod("Visual", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { 0f });
        public static void Run()
        {
            Check(new DirectoryInfo(Path.GetFullPath(".")).Name == "Catchline-lead-sim", "assigned scratch only");
            FishRodImport.Prepare(); ArtImport.BuildLibrary();
            foreach (var name in new[] { "RodViewSky", "RodViewCue" })
            { var shader = Resources.Load<Shader>(name); Check(shader != null && !ShaderUtil.ShaderHasError(shader), name + " compiles"); }
            var g = FishViewChecks.Fixture();
            g.ReelInRodView();
            for (int n = 0; n < 1000 && g.RodViewActive; n++) g.Tick(.025f);
            var fog = RenderSettings.fog; var fogMode = RenderSettings.fogMode;
            var fogColor = RenderSettings.fogColor; var fogDensity = RenderSettings.fogDensity;
            Check(g.StageFishViewCapture(), "production no-save cod cast");
            g.Tick(1.3f); Visual(g);
            var rings = g.GetComponentsInChildren<Renderer>(true).Where(r => r.name == "Ground ring").ToArray();
            Check(rings.Length >= 3 && rings.All(r => r.forceRenderingOff), "actual ground rings hidden");
            Check(g.GetComponentsInChildren<SeaSailingEffects>(true).All(e => e.GetComponent<Renderer>().forceRenderingOff), "route overlays hidden");
            // New overlays created during a cast must be caught too; a previously hidden one stays hidden on exit.
            var hidden = new GameObject("Ground ring").AddComponent<MeshRenderer>(); hidden.transform.SetParent(g.transform); hidden.forceRenderingOff = true;
            var late = new GameObject("Ground ring").AddComponent<MeshRenderer>(); late.transform.SetParent(g.transform);
            g.Tick(.3f); Visual(g); Check(late.forceRenderingOff, "late-created overlay hidden");
            var cap = g.GetComponentsInChildren<Renderer>(true).First(r => r.name == "Orange float cap");
            g.Cam.aspect = 844f / 390;
            var low = g.Cam.WorldToViewportPoint(cap.bounds.center - Vector3.up * cap.bounds.extents.y);
            var high = g.Cam.WorldToViewportPoint(cap.bounds.center + Vector3.up * cap.bounds.extents.y);
            float pixels = Mathf.Abs(high.y - low.y) * 390;
            Check(pixels >= 5, "orange cap reads at phone size: " + pixels);
            var wake = g.GetComponentsInChildren<Transform>(true).First(t => t.name == "Bobber drift wake");
            Check(wake.gameObject.activeSelf, "waiting bobber has wake");
            var wakeMaterial = wake.GetComponent<Renderer>().sharedMaterial;
            var skyMaterial = g.GetComponentsInChildren<Renderer>(true).First(r => r.name == "Rod view sky and soft clouds").sharedMaterial;
            g.ReelInRodView();
            for (int n = 0; n < 1000 && g.RodViewActive; n++) g.Tick(.025f);
            Check(!g.RodViewActive && rings.All(r => !r.forceRenderingOff) && !late.forceRenderingOff && hidden.forceRenderingOff,
                "cancel restores actual overlays and preserves pre-hidden state");
            Check(!g.GetComponentsInChildren<Transform>(true).Any(t => t.name == "Rod view sky and soft clouds"), "sky removed after cast");
            Check(RenderSettings.fog == fog && RenderSettings.fogMode == fogMode && RenderSettings.fogColor == fogColor &&
                Mathf.Approximately(RenderSettings.fogDensity, fogDensity), "exact fog restoration");
            Check(wakeMaterial == null && skyMaterial == null, "owned cue/sky materials destroyed");
            Debug.Log($"[Catchline] FISH POLISH CHECKS PASS: cast/cancel overlay lifecycle + late/pre-hidden renderers, sky/material cleanup + fog restoration, shaders, orange cap {pixels:F2}px at844");
        }
        public static void VerifyAndBuild() { Run(); GameBuild.BuildBoth(); }
        public static void QuickSky()
        {
            var g = FishViewChecks.Fixture(); Check(g.StageFishViewCapture(), "sky fixture");
            g.Tick(1.3f); g.Cam.aspect = 844f / 390; g.PrepareInterface(844, 390); Visual(g);
            var renderer = g.GetComponentsInChildren<Renderer>(true).First(r => r.name == "Rod view sky and soft clouds");
            var folder = Path.GetFullPath("../Catchline/docs/screens/fish-polish-1/sky-probe"); Directory.CreateDirectory(folder);
            Debug.Log($"[Catchline] SKY PROBE {renderer.bounds} queue={renderer.sharedMaterial.renderQueue} shader={renderer.sharedMaterial.shader.name} active={renderer.gameObject.activeInHierarchy} enabled={renderer.enabled} far={g.Cam.farClipPlane} forward={g.Cam.transform.forward}");
            Shot("visible"); renderer.forceRenderingOff = true; Shot("hidden");
            void Shot(string name) => Drain((System.Collections.IEnumerator)typeof(VoyageGame).GetMethod("CompositeFrame", BindingFlags.Instance | BindingFlags.NonPublic)
                .Invoke(g, new object[] { folder, name, new Vector2Int(844, 390) }));
        }
        public static void Preview()
        {
            if (Directory.Exists("Assets/Art/Models/GullHarbourV2")) HarbourImportChecks.Run();
            Run();
            var g = FishViewChecks.Fixture(); Check(g.StageFishViewCapture(), "preview fixture");
            g.Tick(1.3f);
            var capture = (System.Collections.IEnumerator)typeof(VoyageGame).GetMethod("CaptureFishPolish", BindingFlags.Instance | BindingFlags.NonPublic)
                .Invoke(g, new object[] { Path.GetFullPath("../Catchline/docs/screens/fish-polish-1/preview") });
            // Composite preview frames are synchronous; native frame capture is checked separately.
            Drain(capture);
        }
        static void Drain(System.Collections.IEnumerator routine)
        { while (routine.MoveNext()) if (routine.Current is System.Collections.IEnumerator nested) Drain(nested); }
    }
}

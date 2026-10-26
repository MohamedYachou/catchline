using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class CliffsLifeChecks
    {
        static void Check(bool ok, string label) { if (!ok) throw new Exception("Cliffs life: " + label); }
        public static void Run()
        {
            Check(Application.dataPath.Replace('\\', '/').EndsWith("Catchline-sim/Assets"), "scratch only");
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Cliffs life session-only fixture").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            var lib = ArtLibrary.Get();
            foreach (string name in new[] { "SealColony", "Seal", "Seagull", "DiveSplash" }) Check(lib.M(name) != null, name + " existing asset");
            var model = UnityEngine.Object.Instantiate(lib.M("GullSealCliffsSeaV2"));
            try
            {
                typeof(VoyageGame).GetMethod("DressSkerries", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { model, lib });
                var anchors = model.GetComponentsInChildren<Transform>();
                foreach (string name in new[] { "SealHaulout_1", "SealHaulout_2", "SealHaulout_3" })
                {
                    var at = anchors.Single(t => t.name == name);
                    Check(at.GetComponentsInChildren<SealLife>().Length == 1, name + " animated seal");
                    Check(at.GetComponentsInChildren<Animation>().Length > 0, name + " legacy clips");
                }
                foreach (string name in new[] { "CliffGulls_1", "CliffGulls_2" })
                    Check(anchors.Single(t => t.name == name).GetComponentsInChildren<Gull>().Length == 2, name + " gull pair");
                var spray = model.GetComponentInChildren<CliffSpray>();
                Check(spray != null && Mathf.Abs(spray.transform.position.y - model.transform.position.y) < .001f, "spray at water level");
                Check(model.GetComponentsInChildren<SealLife>().Length == 9, "three haulouts and six foreground seals");
                Check(anchors.Count(t => t.name == "Cliffs foreground perch") == 6, "six existing rock surfaces");
            // Verify the shared dispatch does not add this map's life to older maps.
            var older = UnityEngine.Object.Instantiate(lib.M("GullLighthouseRockSeaV2"));
            try { typeof(VoyageGame).GetMethod("DressSkerries", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { older, lib }); Check(older.GetComponentsInChildren<CliffSpray>().Length == 0 && older.GetComponentsInChildren<SealLife>().Length == 0, "older map unchanged"); }
            finally { UnityEngine.Object.DestroyImmediate(older); }

            }
            finally { UnityEngine.Object.DestroyImmediate(model); UnityEngine.Object.DestroyImmediate(g.gameObject); }
            Debug.Log("[Catchline] CLIFFS LIFE CHECKS PASSED. Snapshot written to Logs/check-cliffs-life.log");
        }
        public static void RunAndBuild()
        {
            Run(); CrewCardsAbilityChecks.Regression(); SealCliffsMapChecks.BuildNative();
            Debug.Log("[Catchline] CLIFFS LIFE REGRESSION AND BUILD PASSED. Snapshot written to Builds/Map10Capture/Catchline.exe");
        }
    }
}

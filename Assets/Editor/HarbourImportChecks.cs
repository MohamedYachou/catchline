using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using UnityEditor;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Read-only geometry audit of the unchanged HarbourV2 imports, in the assigned scratch only.
    public static class HarbourImportChecks
    {
        [Serializable] public class Row
        {
            public string name, asset, sha256, notes;
            public long triangles;
            public Vector3 min, max, size, pivot, rootRotation, rootScale;
            public string[] materials;
            public bool resolves, looseMaterials;
        }
        [Serializable] class Receipt { public Row[] models; }
        public static void Run()
        {
            if (new DirectoryInfo(Path.GetFullPath(".")).Name != "Catchline-lead-sim")
                throw new InvalidOperationException("Harbour audit requires Catchline-lead-sim");
            ArtImport.BuildLibrary();
            var library = AssetDatabase.LoadAssetAtPath<ArtLibrary>("Assets/Resources/ArtLibrary.asset");
            var rows = Directory.GetFiles("Assets/Art/Models/GullHarbourV2", "*.fbx").OrderBy(p => p).Select(path =>
            {
                path = path.Replace('\\', '/');
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if (prefab == null || library.M(prefab.name) != prefab) throw new Exception("Harbour lookup failed: " + path);
                var instance = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
                try
                {
                    var renderers = instance.GetComponentsInChildren<Renderer>(true);
                    if (renderers.Length == 0) throw new Exception("Empty model: " + path);
                    var bounds = renderers[0].bounds;
                    foreach (var r in renderers.Skip(1)) bounds.Encapsulate(r.bounds);
                    var mats = renderers.SelectMany(r => r.sharedMaterials).ToArray();
                    bool loose = mats.Any(m => m == null || AssetDatabase.GetAssetPath(m) != path);
                    long tris = instance.GetComponentsInChildren<MeshFilter>(true).Sum(f =>
                        Triangles(f.sharedMesh)) + instance.GetComponentsInChildren<SkinnedMeshRenderer>(true).Sum(r => Triangles(r.sharedMesh));
                    using var hash = System.Security.Cryptography.SHA256.Create();
                    var row = new Row { name = prefab.name, asset = path,
                        sha256 = BitConverter.ToString(hash.ComputeHash(File.ReadAllBytes(path))).Replace("-", ""),
                        triangles = tris, min = bounds.min, max = bounds.max, size = bounds.size,
                        pivot = instance.transform.position, rootRotation = instance.transform.eulerAngles,
                        rootScale = instance.transform.localScale, resolves = true, looseMaterials = loose,
                        materials = mats.Select(m => m == null ? "NULL" : m.name).Distinct().ToArray(),
                        notes = loose ? "QUESTION: null or external material" : "Embedded materials; geometry unchanged" };
                    Debug.Log($"[Catchline] HARBOUR IMPORT {row.name}: {tris} tris, {bounds.size:F3}m, pivot {row.pivot:F3}, root rotation {row.rootRotation:F3}, scale {row.rootScale:F3}, M(name) PASS, loose={loose}");
                    return row;
                }
                finally { UnityEngine.Object.DestroyImmediate(instance); }
            }).ToArray();
            var output = Path.GetFullPath("../Catchline/docs/screens/harbour-1");
            Directory.CreateDirectory(output);
            File.WriteAllText(Path.Combine(output, "import-receipt.json"), JsonUtility.ToJson(new Receipt { models = rows }, true));
            Debug.Log($"[Catchline] HARBOUR IMPORT PASS {rows.Length} models");
        }
        static long Triangles(Mesh mesh) => mesh == null ? 0 :
            Enumerable.Range(0, mesh.subMeshCount).Sum(i => (long)mesh.GetIndexCount(i) / 3);

        public static void VerifyCaptureStages()
        {
            Run();
            FishPolishChecks.Run();
            var game = UnityEngine.Object.FindFirstObjectByType<VoyageGame>();
            VerifyStages(game, new[] { "harbour-h0", "harbour-h1", "harbour-h2", "harbour-h3", "harbour-h4",
                "depart-lane", "chart-leg", "sea-entry", "return-sea", "return-chart", "return-lane", "arrival-crates",
                "intro-open", "intro-basin", "intro-berth", "cage-pull", "cage-snag", "cage-board", "net-setting", "net-haul", "net-bunt" });
        }
        public static void VerifyRemainingStages()
        {
            if (new DirectoryInfo(Path.GetFullPath(".")).Name != "Catchline-lead-sim")
                throw new InvalidOperationException("Harbour evidence requires Catchline-lead-sim");
            var game = FishViewChecks.Fixture();
            VerifyStages(game, new[] { "cage-snag", "cage-board", "net-setting", "net-haul", "net-bunt" });
        }
        public static void VerifyBoardStage()
        {
            if (new DirectoryInfo(Path.GetFullPath(".")).Name != "Catchline-lead-sim")
                throw new InvalidOperationException("Harbour evidence requires Catchline-lead-sim");
            var game = FishViewChecks.Fixture();
            VerifyStages(game, new[] { "cage-board" });
            const System.Reflection.BindingFlags flags = System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic;
            var view = typeof(VoyageGame).GetField("cageView", flags).GetValue(game);
            var crab = view.GetType().GetField("onBoard", flags).GetValue(view) as Transform;
            if (crab == null) throw new Exception("Sorting-board evidence captured before the crab arrived");
            Debug.Log("[Catchline] POPULATED SORTING BOARD PASS");
        }
        static void VerifyStages(VoyageGame game, string[] screens)
        {
            var stage = typeof(VoyageGame).GetMethod("StageUiV2", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
            foreach (var screen in screens)
            {
                if (!(bool)stage.Invoke(game, new object[] { screen })) throw new Exception("Evidence stage failed: " + screen);
                Debug.Log("[Catchline] EVIDENCE STAGE PASS " + screen);
            }
            Debug.Log("[Catchline] EVIDENCE STAGES COMPLETE");
        }
    }
}

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
                        Enumerable.Range(0, f.sharedMesh.subMeshCount).Sum(i => (long)f.sharedMesh.GetIndexCount(i) / 3));
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
    }
}

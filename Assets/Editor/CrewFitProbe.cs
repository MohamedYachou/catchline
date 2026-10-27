using System.Linq;
using UnityEditor;
using UnityEngine;

namespace Catchline.EditorTools
{
    // One-off: print the imported world-space height of the old blob crew rig vs the new Quaternius
    // puppets so we can match their scale to the boat. Safe to delete after crew fit is dialled in.
    public static class CrewFitProbe
    {
        [MenuItem("Catchline/Probe Crew Fit")]
        public static void Run()
        {
            Report("Assets/Art/Models/Crew/CrewRig.fbx");
            foreach (var n in new[] { "mira", "sam", "kofi" })
                Report($"Assets/Art/Models/Crew/Quaternius/{n}.fbx");
            Debug.Log("[Catchline] CREW FIT PROBE DONE");
        }

        static void Report(string path)
        {
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab == null) { Debug.Log($"[Catchline] probe {path}: MISSING"); return; }
            var go = Object.Instantiate(prefab);
            var rs = go.GetComponentsInChildren<Renderer>();
            if (rs.Length == 0) { Debug.Log($"[Catchline] probe {path}: no renderers"); Object.DestroyImmediate(go); return; }
            var b = rs[0].bounds;
            foreach (var r in rs) b.Encapsulate(r.bounds);
            Debug.Log($"[Catchline] probe {path}: size={b.size} (H={b.size.y:0.000}) center={b.center} importScale={((ModelImporter)AssetImporter.GetAtPath(path))?.globalScale}");
            Object.DestroyImmediate(go);
        }
    }
}

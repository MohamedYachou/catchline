using System;
using System.Linq;
using Catchline.Game;
using UnityEditor;
using UnityEngine;
namespace Catchline.EditorTools
{
    // Run only in Windows-owned scratch after water checks release it. No scene/player capture.
    public static class FishArtChecks
    {
        static void Check(bool ok, string message)
        { if (!ok) throw new Exception("[Catchline] Fish art check failed: " + message); }
        public static void Run()
        {
            ArtImport.BuildLibrary();
            var parent = new GameObject("Isolated fish art check");
            try
            {
                foreach (var fish in GameData.Fish)
                {
                    string model = fish.Species == Species.Conger ? "CongerEel" : fish.Species.ToString();
                    var asset = AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Art/Models/Fish/" + model + ".fbx");
                    Check(asset != null, model + " imported FBX");
                    int tris = asset.GetComponentsInChildren<MeshFilter>(true).Sum(m => m.sharedMesh.triangles.Length / 3);
                    Check(tris > 1000 && tris < 4000, model + " bounded triangle count");
                    string portrait = "fish-" + fish.Species.ToString().ToLowerInvariant();
                    var texture = ArtLibrary.Get().UiTex(portrait);
                    Check(texture != null && texture.width >= 256 && texture.width == texture.height * 2, portrait + " library/landscape import");
                    var instance = DeckFish.BuildModel(fish.Species, (fish.MinKg + fish.MaxKg) * .5f, parent.transform);
                    var renderers = instance.GetComponentsInChildren<Renderer>();
                    Check(renderers.Length > 0 && renderers.Length <= 2, model + " resolves authored mesh, not fallback");
                    var bounds = renderers[0].bounds;
                    foreach (var r in renderers) { bounds.Encapsulate(r.bounds); Check(r.sharedMaterials.All(m => m != null && m.shader != null), model + " material slots"); }
                    Check(Mathf.Max(bounds.size.x, bounds.size.z) > bounds.size.y * 1.7f, model + " lies on deck, not vertical");
                    Check(bounds.size.magnitude < 2f, model + " metre-scale bounds");
                    UnityEngine.Object.DestroyImmediate(instance.gameObject);
                }
            }
            finally { UnityEngine.Object.DestroyImmediate(parent); }
            Debug.Log("[Catchline] FISH ART IMPORT CHECKS PASSED; native HUD screenshots/listening/Mo acceptance still pending");
        }
    }
}

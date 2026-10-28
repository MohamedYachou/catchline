using System.IO;
using UnityEditor;
using UnityEngine;

namespace Catchline.EditorTools
{
    // HIFI art (Art/HIFI.md; Mo 10-28: "not low poly in mind"). Codex ships each model under Assets/Art/Models/Hifi/ with
    // baked BaseColor/Normal/Mask sets and an <Asset>.hifi.json naming its MH_ materials. This builds one URP Lit material
    // per set (Mask: R metallic, G occlusion, A smoothness) in a Materials folder beside the model and remaps the FBX onto
    // them, so the textures render as authored instead of being flattened to a palette colour.
    sealed class HifiImport : AssetPostprocessor
    {
        public const string Root = "Assets/Art/Models/Hifi";

        [System.Serializable] class Manifest { public string asset; public Entry[] materials; }
        [System.Serializable] class Entry { public string name, set; public float[] tiling; public bool tiles; }

        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(Root + "/") || !assetPath.Contains("/Textures/")) return;
            var t = (TextureImporter)assetImporter;
            string n = Path.GetFileNameWithoutExtension(assetPath);
            t.mipmapEnabled = true; t.maxTextureSize = 2048; t.anisoLevel = 4;
            t.wrapMode = TextureWrapMode.Repeat; // tiling sets (planks, stone) and atlases alike
            if (n.EndsWith("_Normal")) t.textureType = TextureImporterType.NormalMap;
            else { t.textureType = TextureImporterType.Default; t.sRGBTexture = !n.EndsWith("_Mask"); t.alphaIsTransparency = false; }
        }

        static bool queued;
        static void OnPostprocessAllAssets(string[] imported, string[] deleted, string[] moved, string[] movedFrom)
        {
            if (queued) return;
            foreach (var p in imported)
            {
                if (!p.StartsWith(Root + "/") || p.Contains("/Materials/")) continue;
                queued = true;
                EditorApplication.delayCall += () => { queued = false; Sync(); };
                return;
            }
        }

        [MenuItem("Catchline/Art/Rebuild HIFI materials")]
        public static void Sync()
        {
            if (!AssetDatabase.IsValidFolder(Root)) return;
            foreach (var guid in AssetDatabase.FindAssets("t:TextAsset", new[] { Root }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!path.EndsWith(".hifi.json")) continue;
                try { Apply(path); }
                catch (System.Exception e) { Debug.LogWarning($"[Catchline] HIFI {path}: {e.Message}"); }
            }
        }

        static void Apply(string manifestPath)
        {
            var m = JsonUtility.FromJson<Manifest>(File.ReadAllText(manifestPath));
            string dir = Path.GetDirectoryName(manifestPath).Replace('\\', '/');
            string asset = string.IsNullOrEmpty(m.asset) ? Path.GetFileName(manifestPath).Replace(".hifi.json", "") : m.asset;
            var importer = AssetImporter.GetAtPath($"{dir}/{asset}.fbx") as ModelImporter;
            if (m.materials == null || m.materials.Length == 0) return;
            if (!AssetDatabase.IsValidFolder($"{dir}/Materials")) AssetDatabase.CreateFolder(dir, "Materials");
            var shader = Shader.Find("Universal Render Pipeline/Lit");
            var map = importer != null ? importer.GetExternalObjectMap() : null;
            bool remap = false;
            foreach (var e in m.materials)
            {
                if (string.IsNullOrEmpty(e.name)) continue;
                string set = string.IsNullOrEmpty(e.set) ? e.name.Replace("MH_", "") : e.set;
                string matPath = $"{dir}/Materials/{e.name}.mat";
                var mat = AssetDatabase.LoadAssetAtPath<Material>(matPath);
                bool created = mat == null;
                if (created) mat = new Material(shader) { name = e.name };
                Fill(mat, shader, Tex(dir, set, "BaseColor"), Tex(dir, set, "Normal"), Tex(dir, set, "Mask"),
                    e.tiling != null && e.tiling.Length == 2 ? new Vector2(e.tiling[0], e.tiling[1]) : Vector2.one);
                if (created) AssetDatabase.CreateAsset(mat, matPath); else EditorUtility.SetDirty(mat);
                if (importer == null) continue;
                var id = new AssetImporter.SourceAssetIdentifier(typeof(Material), e.name);
                if (map.TryGetValue(id, out var current) && current == mat) continue;
                importer.AddRemap(id, mat); remap = true;
            }
            AssetDatabase.SaveAssets();
            if (remap) importer.SaveAndReimport();
        }

        static Texture2D Tex(string dir, string set, string kind) => AssetDatabase.LoadAssetAtPath<Texture2D>($"{dir}/Textures/{set}_{kind}.png");

        static void Fill(Material mat, Shader shader, Texture2D baseMap, Texture2D normal, Texture2D mask, Vector2 tiling)
        {
            if (mat.shader != shader) mat.shader = shader;
            mat.SetTexture("_BaseMap", baseMap); mat.SetTexture("_MainTex", baseMap);
            mat.SetColor("_BaseColor", Color.white); mat.SetColor("_Color", Color.white);
            mat.SetTextureScale("_BaseMap", tiling); mat.SetTextureScale("_MainTex", tiling);
            mat.SetTexture("_BumpMap", normal); mat.SetFloat("_BumpScale", 1);
            Keyword(mat, "_NORMALMAP", normal != null);
            // Metallic workflow; URP reads metallic from R and smoothness from A of _MetallicGlossMap, occlusion from G of _OcclusionMap.
            mat.SetFloat("_WorkflowMode", 1); mat.SetFloat("_SmoothnessTextureChannel", 0);
            mat.SetTexture("_MetallicGlossMap", mask); mat.SetFloat("_Metallic", 0); mat.SetFloat("_Smoothness", mask != null ? 1 : .3f);
            Keyword(mat, "_METALLICSPECGLOSSMAP", mask != null);
            mat.SetTexture("_OcclusionMap", mask); mat.SetFloat("_OcclusionStrength", 1);
            Keyword(mat, "_OCCLUSIONMAP", mask != null);
        }

        static void Keyword(Material mat, string k, bool on) { if (on) mat.EnableKeyword(k); else mat.DisableKeyword(k); }
    }
}

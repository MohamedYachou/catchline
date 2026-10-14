using System.IO;
using System.Linq;
using Catchline.Game;
using UnityEditor;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Import rules for Codex's art, and the ArtLibrary asset the game loads at runtime.
    public class ArtImport : AssetPostprocessor
    {
        const string UiFolder = "Assets/Art/UI/";

        // UI sprites are exported at 2x. Import them as IMGUI textures at 1x so 9-slice borders match the HUD sizes.
        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(UiFolder)) return;
            var ti = (TextureImporter)assetImporter;
            ti.textureType = TextureImporterType.GUI;
            ti.textureShape = TextureImporterShape.Texture2D;
            ti.mipmapEnabled = false;
            ti.wrapMode = TextureWrapMode.Clamp;
            ti.filterMode = FilterMode.Bilinear;
            ti.alphaIsTransparency = true;
            ti.npotScale = TextureImporterNPOTScale.None;
            ti.textureCompression = TextureImporterCompression.Uncompressed;
            string name = Path.GetFileNameWithoutExtension(assetPath);
            ti.maxTextureSize = name.StartsWith("bar-") ? 64 : name == "strike-water" ? 1024 : name.EndsWith("-tail") ? 32 : 128;
        }

        // Models keep their materials inside the FBX (no loose Materials folders); the game remaps them
        // to its own URP materials by palette name at spawn time anyway.
        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith("Assets/Art/Models/")) return;
            var mi = (ModelImporter)assetImporter;
            mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
            mi.materialLocation = ModelImporterMaterialLocation.InPrefab;
            mi.importAnimation = false;
            mi.importCameras = false;
            mi.importLights = false;
        }

        const string LibraryPath = "Assets/Resources/ArtLibrary.asset";

        static GameObject Model(string path) => AssetDatabase.LoadAssetAtPath<GameObject>("Assets/Art/Models/" + path + ".fbx");

        [MenuItem("Catchline/Rebuild Art Library")]
        public static void BuildLibrary()
        {
            Directory.CreateDirectory("Assets/Resources");
            var lib = AssetDatabase.LoadAssetAtPath<ArtLibrary>(LibraryPath);
            if (lib == null)
            {
                lib = ScriptableObject.CreateInstance<ArtLibrary>();
                AssetDatabase.CreateAsset(lib, LibraryPath);
            }
            lib.Rowboat = Model("Boats/Rowboat");
            lib.FishingRod = Model("Fishing/FishingRod");
            lib.Bobber = Model("Fishing/Bobber");
            lib.Cooler = Model("DeckProps/Cooler");
            lib.IceBox = Model("DeckProps/IceBox");
            lib.BaitBucket = Model("DeckProps/BaitBucket");
            lib.LunchTin = Model("DeckProps/LunchTin");
            lib.Quay = Model("Harbour/Quay4m");
            lib.QuayLadder = Model("Harbour/Quay4mLadder");
            lib.Bollard = Model("Harbour/Bollard");
            lib.LampPost = Model("Harbour/LampPost");
            lib.HouseA = Model("Harbour/HouseA");
            lib.HouseB = Model("Harbour/HouseB");
            lib.Lighthouse = Model("Harbour/Lighthouse");
            lib.RockA = Model("Harbour/BreakwaterRockA");
            lib.RockB = Model("Harbour/BreakwaterRockB");
            lib.RockC = Model("Harbour/BreakwaterRockC");
            lib.Kelp = Model("Harbour/KelpPatch");
            lib.Fish = new[] { Model("Fish/Herring"), Model("Fish/Mackerel"), Model("Fish/Pollock"), Model("Fish/SeaBass"), Model("Fish/CongerEel"), null, null };
            var pngs = Directory.GetFiles(Path.GetFullPath(UiFolder), "*.png");
            lib.Ui = pngs
                .Select(p => UiFolder + Path.GetFileName(p))
                .Select(p => AssetDatabase.LoadMainAssetAtPath(p) as Texture2D)
                .Where(t => t != null)
                .ToArray();
            if (lib.Ui.Length == 0 && pngs.Length > 0)
                Debug.LogWarning($"[Catchline] {pngs.Length} UI pngs on disk but none loaded; first: {UiFolder + Path.GetFileName(pngs[0])} -> {AssetDatabase.LoadMainAssetAtPath(UiFolder + Path.GetFileName(pngs[0]))?.GetType().Name ?? "null"}");
            lib.UiFont = AssetDatabase.LoadAssetAtPath<Font>(UiFolder + "Fonts/Fredoka-Medium.ttf");
            EditorUtility.SetDirty(lib);
            AssetDatabase.SaveAssets();
            var mats = lib.Rowboat != null ? lib.Rowboat.GetComponentsInChildren<Renderer>().SelectMany(r => r.sharedMaterials).Select(m => m != null ? m.name : "null").Distinct() : Enumerable.Empty<string>();
            Debug.Log($"[Catchline] Art library: rowboat {(lib.Rowboat != null)} [{string.Join(", ", mats)}], {lib.Ui.Length} UI textures, font {(lib.UiFont != null)}");
        }
    }
}

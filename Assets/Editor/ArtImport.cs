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
        static bool rebuildQueued;

        static void OnPostprocessAllAssets(string[] imported, string[] deleted, string[] moved, string[] movedFrom)
        {
            if (rebuildQueued || !imported.Any(p => p.StartsWith("Assets/Art/Models/") && p.EndsWith(".fbx")
                || p.StartsWith("Assets/Art/Water/") && (p.EndsWith(".png") || p.EndsWith(".tif")) || p.StartsWith("Assets/gemini/") && (p.EndsWith(".png") || p.EndsWith(".fbx")) || p.EndsWith("/CoastalWater.shader") || p.EndsWith("/PtsWater.shader"))) return;
            rebuildQueued = true;
            EditorApplication.delayCall += () =>
            {
                rebuildQueued = false;
                BuildLibrary();
            };
        }

        // UI sprites are exported at 2x. Import them as IMGUI textures at 1x so 9-slice borders match the HUD sizes.
        void OnPreprocessTexture()
        {
            if (assetPath.StartsWith("Assets/Art/Water/PTS/"))
            {
                var water = (TextureImporter)assetImporter;
                water.textureType = TextureImporterType.Default;
                water.sRGBTexture = false;
                water.mipmapEnabled = true;
                water.wrapMode = TextureWrapMode.Repeat;
                water.filterMode = FilterMode.Trilinear;
                water.maxTextureSize = 2048;
                return;
            }
            if (assetPath.StartsWith("Assets/Art/Textures/"))
            {
                var water = (TextureImporter)assetImporter;
                water.textureType = TextureImporterType.Default;
                water.textureShape = TextureImporterShape.Texture2D;
                water.wrapMode = Path.GetFileName(assetPath).StartsWith("water-tile") || assetPath.Contains("deck-planks") ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
                water.mipmapEnabled = true;
                water.alphaIsTransparency = true;
                water.filterMode = FilterMode.Bilinear;
                water.maxTextureSize = 1024;
                return;
            }
            if (!assetPath.StartsWith(UiFolder) && !assetPath.StartsWith("Assets/gemini/")) return;
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
            if (name.StartsWith("v2-"))
            {
                // UI v2 kit: 2x authored, never downscaled; planks and rope tile.
                ti.maxTextureSize = 2048;
                if (name.StartsWith("v2-plank") || name.StartsWith("v2-rope")) ti.wrapMode = TextureWrapMode.Repeat;
                return;
            }
            ti.maxTextureSize = assetPath.StartsWith("Assets/gemini/") ? 1024 : name == "title-backdrop" || name.StartsWith("header-") || name == "sea-chart" ? 2048
                : name == "logo-catchline" || name == "strike-water" ? 1024
                : name == "daily-gift" ? 512
                : name.StartsWith("fish-") && name != "fish-shadow" || name.StartsWith("portrait-") ? 256
                : name.StartsWith("bar-") ? 64 : name.EndsWith("-tail") ? 32 : 128;
        }

        // Models keep their materials inside the FBX (no loose Materials folders); the game remaps them
        // to its own URP materials by palette name at spawn time anyway.
        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith("Assets/Art/Models/") && !assetPath.StartsWith("Assets/gemini/Models/")) return;
            var mi = (ModelImporter)assetImporter;
            mi.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
            mi.materialLocation = ModelImporterMaterialLocation.InPrefab;
            mi.importAnimation = assetPath.EndsWith("/CrewRig.fbx") || assetPath.EndsWith("/WreckLife/Gannet.fbx") || assetPath.EndsWith("/Crew/Townsfolk.fbx") || assetPath.EndsWith("/LighthouseLife/Puffin.fbx") || assetPath.EndsWith("/HarbourLife/Dog.fbx") || assetPath.EndsWith("/HarbourLife/Cat.fbx") || assetPath.EndsWith("/GullCoastLife/Cormorant.fbx") || assetPath.EndsWith("/GullCoastLife/Oystercatcher.fbx");
            if (mi.importAnimation) mi.animationType = ModelImporterAnimationType.Legacy;
            if (assetPath.EndsWith("/PrepFisherV1.fbx") || assetPath.EndsWith("/Tier5FisherV1.fbx") || assetPath.EndsWith("/Tier5DeepLines103.fbx")) mi.isReadable = true; // Physical deck slices also run in the player.
            if (assetPath.StartsWith("Assets/gemini/Models/")) mi.isReadable = true;
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
            lib.Fish = GameData.Fish.Select(f => AssetDatabase.LoadAssetAtPath<GameObject>("Assets/gemini/Models/"+f.Species+".fbx")
                ?? Model(f.Species == Species.Crab ? "Props/Crab" : "Fish/"+(f.Species == Species.Conger ? "CongerEel" : f.Species.ToString()))).ToArray();
            lib.Models = Directory.GetFiles(Path.GetFullPath("Assets/Art/Models"), "*.fbx", SearchOption.AllDirectories)
                .Select(p => "Assets/Art/Models/" + Path.GetRelativePath(Path.GetFullPath("Assets/Art/Models"), p).Replace('\\', '/'))
                .Select(p => AssetDatabase.LoadAssetAtPath<GameObject>(p))
                .Where(g => g != null)
                .ToArray();
            if (Directory.Exists("Assets/gemini/Models")) lib.Models=lib.Models.Concat(Directory.GetFiles("Assets/gemini/Models","*.fbx")
                .Select(p=>AssetDatabase.LoadAssetAtPath<GameObject>(p.Replace('\\','/'))).Where(g=>g!=null)).ToArray();
            lib.CrewClips = AssetDatabase.LoadAllAssetsAtPath("Assets/Art/Models/Crew/CrewRig.fbx")
                .OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__")).ToArray();
            Debug.Log($"[Catchline] Art library: {lib.Models.Length} models");
            var pngs = Directory.GetFiles(Path.GetFullPath(UiFolder), "*.png");
            // Crew cards v2: frames, portraits, chests, tools and icons live in subfolders.
            var cardFolders = new[] { "Cards", "Portraits", "Crew", "Tutorial" };
            lib.Ui = pngs
                .Select(p => UiFolder + Path.GetFileName(p))
                .Concat(cardFolders.Where(f => Directory.Exists(UiFolder + f))
                    .SelectMany(f => Directory.GetFiles(UiFolder + f, "*.png").Select(p => UiFolder + f + "/" + Path.GetFileName(p))))
                .Select(p => AssetDatabase.LoadMainAssetAtPath(p) as Texture2D)
                .Where(t => t != null)
                .ToArray();
            if (lib.Ui.Length == 0 && pngs.Length > 0)
                Debug.LogWarning($"[Catchline] {pngs.Length} UI pngs on disk but none loaded; first: {UiFolder + Path.GetFileName(pngs[0])} -> {AssetDatabase.LoadMainAssetAtPath(UiFolder + Path.GetFileName(pngs[0]))?.GetType().Name ?? "null"}");
            if (Directory.Exists("Assets/gemini"))
                lib.Ui = lib.Ui.Concat(Directory.GetFiles("Assets/gemini", "*.png", SearchOption.AllDirectories)
                    .Select(p => AssetDatabase.LoadAssetAtPath<Texture2D>(p.Replace('\\', '/'))).Where(t => t != null)).ToArray();
            lib.UiFont = AssetDatabase.LoadAssetAtPath<Font>(UiFolder + "Fonts/Fredoka-Medium.ttf");
            lib.DisplayFont = AssetDatabase.LoadAssetAtPath<Font>(UiFolder + "Fonts/LilitaOne-Regular.ttf");
            lib.StationFiles = Directory.GetFiles("Assets/Art/Models/Boats", "*.stations.json")
                .Select(p => AssetDatabase.LoadAssetAtPath<TextAsset>(p.Replace('\\', '/'))).Where(t => t != null).ToArray();
            lib.NavigationFiles = Directory.GetFiles("Assets/Art/Models/Environment", "navigation*.json", SearchOption.AllDirectories)
                .Select(p => AssetDatabase.LoadAssetAtPath<TextAsset>(p.Replace('\\', '/'))).Where(t => t != null).ToArray();
            lib.WaterShader = AssetDatabase.LoadAssetAtPath<Shader>("Assets/Art/Shaders/PtsWater.shader")
                ?? AssetDatabase.LoadAssetAtPath<Shader>("Assets/Art/Shaders/CoastalWater.shader");
            lib.PtsWaterNormals = AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Art/Water/PTS/WaterNormals.tif");
            lib.PtsWaterDither = AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Art/Water/PTS/normalNoise.png");
            lib.WaterRipples = AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Art/Water/normal-ripples.png");
            lib.WaterCrossing = AssetDatabase.LoadAssetAtPath<Texture2D>("Assets/Art/Water/normal-crossing.png");
            var waterPaths = Directory.GetFiles(Path.GetFullPath("Assets/Art/Textures"), "*.png")
                .Select(p => "Assets/Art/Textures/" + Path.GetFileName(p)).ToArray();
            foreach (var path in waterPaths)
                if (AssetDatabase.LoadAssetAtPath<Texture2D>(path) == null)
                    AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate | ImportAssetOptions.ForceSynchronousImport);
            lib.WaterTextures = waterPaths.Select(p => AssetDatabase.LoadAssetAtPath<Texture2D>(p)).Where(t => t != null).ToArray();
            if (lib.WaterTextures.Length != waterPaths.Length)
                throw new System.InvalidOperationException("[Catchline] Water texture import incomplete: " + lib.WaterTextures.Length + "/" + waterPaths.Length);
            EditorUtility.SetDirty(lib);
            AssetDatabase.SaveAssets();
            var mats = lib.Rowboat != null ? lib.Rowboat.GetComponentsInChildren<Renderer>().SelectMany(r => r.sharedMaterials).Select(m => m != null ? m.name : "null").Distinct() : Enumerable.Empty<string>();
            Debug.Log($"[Catchline] Art library: rowboat {(lib.Rowboat != null)} [{string.Join(", ", mats)}], {lib.Ui.Length} UI textures, font {(lib.UiFont != null)}");
        }
    }
}

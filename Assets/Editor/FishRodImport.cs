using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using UnityEditor;
using UnityEngine;

namespace Catchline.EditorTools
{
    public sealed class FishRodImport : AssetPostprocessor
    {
        const string Folder = "Assets/Art/Models/FishRodFP/";
        const string Model = Folder + "FishRodFP.fbx";
        const string Resource = "Assets/Scripts/Game/Minigame/Resources/RodViewArt.asset";
        public override int GetPostprocessOrder() => 100;
        void OnPreprocessModel()
        {
            if (assetPath != Model) return;
            var m = (ModelImporter)assetImporter;
            // These are transform-only clips. Legacy permits explicit SampleAnimation in players
            // without an enabled Animator/controller also advancing the pose on Unity's clock.
            m.importAnimation = true; m.animationType = ModelImporterAnimationType.Legacy;
            m.animationCompression = ModelImporterAnimationCompression.Off;
            m.optimizeGameObjects = false; m.importCameras = m.importLights = false;
            m.materialImportMode = ModelImporterMaterialImportMode.None;
        }
        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(Folder)) return;
            var t = (TextureImporter)assetImporter;
            t.sRGBTexture = true; t.wrapMode = TextureWrapMode.Clamp; t.mipmapEnabled = true;
            t.textureCompression = TextureImporterCompression.Uncompressed; t.maxTextureSize = 256;
        }
        static void OnPostprocessAllAssets(string[] imported, string[] deleted, string[] moved, string[] from)
        {
            if (imported.Any(p => p.StartsWith(Folder))) EditorApplication.delayCall += Prepare;
        }
        public static void Prepare()
        {
            var importer = AssetImporter.GetAtPath(Model) as ModelImporter;
            if (importer != null && importer.animationType != ModelImporterAnimationType.Legacy)
            {
                importer.animationType = ModelImporterAnimationType.Legacy;
                importer.SaveAndReimport();
            }
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(Model);
            if (model == null) return;
            var clips = AssetDatabase.LoadAllAssetsAtPath(Model).OfType<AnimationClip>()
                .Where(c => !c.name.StartsWith("__preview__")).ToArray();
            if (clips.Length != 7) throw new Exception("FishRodFP must import all seven authored clips: " + string.Join(",", clips.Select(c => c.name)));
            if (clips.Any(c => !c.legacy)) throw new Exception("FishRodFP runtime sampling requires Legacy clips");
            var data = AssetDatabase.LoadAssetAtPath<RodViewArt>(Resource);
            if (data == null) { data = ScriptableObject.CreateInstance<RodViewArt>(); AssetDatabase.CreateAsset(data, Resource); }
            data.Model = model; data.Atlas = AssetDatabase.LoadAssetAtPath<Texture2D>(Folder + "FishRodFP_Atlas.png"); data.Clips = clips;
            EditorUtility.SetDirty(data); AssetDatabase.SaveAssets();
            var instance = UnityEngine.Object.Instantiate(model);
            foreach (var animator in instance.GetComponentsInChildren<Animator>()) animator.enabled = false;
            foreach (var clip in clips)
            {
                clip.SampleAnimation(instance, clip.length * .5f);
                var tip = ArtLibrary.Find(instance, "LineTip"); var root = ArtLibrary.Find(instance, "RodRoot");
                Debug.Log($"[Catchline] FP clip {clip.name} {clip.length:F3}s root={root.localRotation.eulerAngles} tip={tip.position:F4}");
            }
            foreach (var n in new[] { "RodRoot", "Rod_01", "Rod_08", "LineTip", "GripHand.L", "ReelHandle", "ReelHand.R" })
            {
                var t = ArtLibrary.Find(instance, n);
                Debug.Log($"[Catchline] FP bone {n} position={t.position:F4} localRotation={t.localRotation.eulerAngles:F4}");
            }
            UnityEngine.Object.DestroyImmediate(instance);
        }
    }
}

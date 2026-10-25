using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Catchline.Game;
using UnityEditor;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Narrow additive import rule; runs after the general ArtImport settings.
    public sealed class SkerriesLifeImport : AssetPostprocessor
    {
        const string Folder = "Assets/Art/Models/Environment/Skerries/";
        public override int GetPostprocessOrder() => 100;
        void OnPreprocessModel()
        {
            if (!assetPath.StartsWith(Folder, StringComparison.Ordinal)) return;
            var importer = (ModelImporter)assetImporter;
            importer.importAnimation = assetPath == Folder + "Seal.fbx";
            if (importer.importAnimation) importer.animationType = ModelImporterAnimationType.Legacy;
        }
        static void Check(bool value, string label)
        { if (!value) throw new Exception("[Catchline] Skerries life import failed: " + label); }
        static string Tail(string value) => value.Split('|').Last();

        public static void CheckAndBuild()
        {
            Check(Application.dataPath.Replace('\\', '/').EndsWith("Catchline-sim/Assets", StringComparison.OrdinalIgnoreCase), "scratch only");
            const string sealPath = Folder + "Seal.fbx";
            var importer = (ModelImporter)AssetImporter.GetAtPath(sealPath);
            Check(importer != null && importer.importAnimation && importer.animationType == ModelImporterAnimationType.Legacy, "Legacy seal importer");
            var takes = importer.defaultClipAnimations;
            Check(takes.Length == 3, "three exported action takes");
            foreach (var take in takes)
            {
                take.name = Tail(take.name);
                take.loopTime = take.name != "Slide";
                take.wrapMode = take.loopTime ? WrapMode.Loop : WrapMode.Once;
            }
            importer.clipAnimations = takes;
            importer.SaveAndReimport();
            ArtImport.BuildLibrary();
            var expected = new Dictionary<string, int> {
                { "Seal", 636 }, { "SealColony", 1964 }, { "SealSwimHead", 510 },
                { "ReefBreak_A", 112 }, { "ReefBreak_B", 112 }, { "CrabBuoySet", 216 }, { "PotStack", 2001 }
            };
            var results = new List<string> { DateTime.UtcNow.ToString("O"), "Imported assets only; runtime placement and action transitions remain Claude-owned." };
            foreach (var pair in expected)
            {
                string path = Folder + pair.Key + ".fbx";
                Check(ArtLibrary.Get().M(pair.Key) != null, pair.Key + " ArtLibrary lookup");
                var meshes = AssetDatabase.LoadAllAssetsAtPath(path).OfType<Mesh>().ToArray();
                long triangles = meshes.Sum(m => Enumerable.Range(0, m.subMeshCount).Sum(s => (long)m.GetIndexCount(s) / 3));
                Check(triangles == pair.Value, pair.Key + " Unity triangle count " + triangles);
                results.Add(pair.Key + " lookup/triangles PASS " + triangles);
            }
            var clips = AssetDatabase.LoadAllAssetsAtPath(sealPath).OfType<AnimationClip>().Where(c => !c.name.StartsWith("__preview__")).ToArray();
            Check(clips.Length == 3 && clips.Select(c => c.name).OrderBy(n => n).SequenceEqual(new[] { "Bask", "Look", "Slide" }), "three stable clip names");
            foreach (var clip in clips)
            {
                Check(clip.legacy, clip.name + " legacy flag");
                float duration = clip.name == "Bask" ? 4 : clip.name == "Look" ? 3 : 1.2f;
                Check(Mathf.Abs(clip.length - duration) < .04f, clip.name + " duration");
                Check(clip.wrapMode == (clip.name == "Slide" ? WrapMode.Once : WrapMode.Loop), clip.name + " wrap mode");
                var seal = UnityEngine.Object.Instantiate(AssetDatabase.LoadAssetAtPath<GameObject>(sealPath));
                var baked = new Mesh();
                try
                {
                    var skin = seal.GetComponentInChildren<SkinnedMeshRenderer>();
                    Check(skin != null && skin.bones.Length == 6, "six-bone skin");
                    clip.SampleAnimation(seal, 0); skin.BakeMesh(baked); var first = baked.vertices;
                    float moved = 0, loopError = 0;
                    for (int sample = 1; sample <= 4; sample++)
                    {
                        clip.SampleAnimation(seal, clip.length * sample / 4f); skin.BakeMesh(baked); var current = baked.vertices;
                        float delta = first.Select((v, i) => Vector3.Distance(v, current[i])).Max();
                        if (sample < 4) moved = Mathf.Max(moved, delta); else loopError = delta;
                    }
                    Check(moved > .00001f, clip.name + " deforms imported skin");
                    if (clip.name != "Slide") Check(loopError < .001f, clip.name + " seamless loop");
                    results.Add(clip.name + " Legacy " + clip.length.ToString("F2") + "s " + clip.wrapMode + " sampled skin motion=" + moved.ToString("F6") + "m end delta=" + loopError.ToString("F6") + "m PASS");
                }
                finally { UnityEngine.Object.DestroyImmediate(baked); UnityEngine.Object.DestroyImmediate(seal); }
            }
            Directory.CreateDirectory("Logs");
            File.WriteAllLines("Logs/map6-life-import.txt", results);
            Debug.Log("[Catchline] SKERRIES LIFE IMPORT PASSED. Snapshot written to Logs/map6-life-import.txt");
            SkerriesMapChecks.BuildNative();
        }
    }
}

using System;
using System.IO;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class ChartPresentationChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("Chart presentation check failed: " + why); }
        static Bounds BoundsIn(Transform source, Transform frame)
        {
            Bounds result = new(); bool first = true;
            foreach (var mf in source.GetComponentsInChildren<MeshFilter>())
            {
                var bounds = mf.sharedMesh.bounds;
                for (int corner = 0; corner < 8; corner++)
                {
                    var p = frame.InverseTransformPoint(mf.transform.TransformPoint(bounds.center + Vector3.Scale(bounds.extents,
                        new Vector3((corner & 1) == 0 ? -1 : 1, (corner & 2) == 0 ? -1 : 1, (corner & 4) == 0 ? -1 : 1))));
                    if (first) { result = new Bounds(p, Vector3.zero); first = false; } else result.Encapsulate(p);
                }
            }
            return result;
        }
        public static void Capture()
        {
            var texture = (TextureImporter)AssetImporter.GetAtPath("Assets/Resources/Charts/gull-coast.png");
            texture.mipmapEnabled = false; texture.maxTextureSize = 4096; texture.textureCompression = TextureImporterCompression.Uncompressed;
            texture.sRGBTexture = true; texture.alphaIsTransparency = false; texture.SaveAndReimport();
            texture.npotScale = TextureImporterNPOTScale.None; texture.SaveAndReimport();
            ChartChecks.Capture();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Stern trailing net fixture").AddComponent<VoyageGame>(); game.SessionOnly = true; game.Build(); game.StartNetBoatTrial();
            Check(game.SetNet(), "begin net deployment"); NetHaulChecks.FinishCaptainSet(game);
            var floats = (Transform)typeof(VoyageGame).GetField("netFloats", Hidden).GetValue(game);
            var model = (Transform)typeof(VoyageGame).GetField("netModelRoot", Hidden).GetValue(game);
            var stern = BoundsIn(model, game.Boat).max.x;
            for (int frame = 0; frame < 100; frame++)
            {
                game.Tick(.05f); var gear = BoundsIn(floats, game.Boat);
                Check(gear.min.x > stern + .5f, "all net panels stay behind physical stern while water bobs");
                Check(Mathf.Abs(gear.center.z - game.State.HullDef.Center.z) < .2f, "net centred behind boat, not alongside");
                var ropes = floats.GetComponentsInChildren<LineRenderer>(); Check(ropes.Length == 2, "two stern ropes visible");
                foreach (var rope in ropes) Check(rope.positionCount == 2 && Vector3.Distance(rope.GetPosition(0), rope.GetPosition(1)) < 3.5f, "ropes connect stern to nearby floating gear");
            }
            var shot = typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic);
            shot.Invoke(null, new object[] { game, "../chart017/net-behind-stern", 1440, 900, 1f });
            shot.Invoke(null, new object[] { game, "../chart017/net-behind-stern-phone", 844, 390, 1f });
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] CHART PRESENTATION CHECKS PASSED: illustrated map, stern clearance/centre/ropes through moving water");
            Debug.Log("[Catchline] Snapshot written to Logs/chart017");
        }
        public static void ValidateAndBuildPreview()
        {
            Capture(); NetHaulChecks.Run(); CrewPolishChecks.Run(); BuildPreview();
        }
        public static void ReviewAndBuildPreview() { Capture(); BuildPreview(); }
        public static void BuildPreview()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Illustrated chart preview").AddComponent<VoyageGame>(); game.SessionOnly = true;
            const string scene = "Assets/Scenes/Chart017Preview.unity";
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scene);
            string output = Path.GetFullPath("Builds/Chart017/Catchline.exe");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { scene }, locationPathName = output,
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None });
            Check(report.summary.result == BuildResult.Succeeded, "separate illustrated chart preview built");
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: " + output);
        }
    }
}

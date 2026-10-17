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
    public static class SeaClearanceChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        const float Surface = -.52f;
        static void Check(bool ok, string reason) { if (!ok) throw new Exception("Sea clearance check failed: " + reason); }
        public static void Verify(VoyageGame game, int spot)
        {
            var scene = (Transform)typeof(VoyageGame).GetField("scenery", Hidden).GetValue(game);
            float edge = game.State.HullDef.Center.z + Mathf.Max(VoyageGame.FishingWaterHalfWidth,
                game.State.HullDef.Height * game.State.HullDef.CellSize * .5f + 2f);
            int tested = 0, meshes = 0;
            foreach (var mesh in scene.GetComponentsInChildren<MeshFilter>())
            {
                if (!mesh.sharedMesh) continue;
                meshes++;
                var vertices = mesh.sharedMesh.vertices;
                for (int i = 0; i < vertices.Length; i++) vertices[i] = scene.InverseTransformPoint(mesh.transform.TransformPoint(vertices[i]));
                var triangles = mesh.sharedMesh.triangles;
                for (int i = 0; i < triangles.Length; i += 3)
                    for (int e = 0; e < 3; e++)
                    {
                        Vector3 a = vertices[triangles[i + e]], b = vertices[triangles[i + (e + 1) % 3]];
                        if (a.y >= Surface)
                        {
                            Check(a.z >= edge - .002f, $"map{spot} hull{game.State.Hull} exposed {mesh.name} inside reserve ({a.z:F3} < {edge:F3})");
                            tested++;
                        }
                        if ((a.y < Surface) == (b.y < Surface)) continue;
                        float z = a.z + (b.z - a.z) * (Surface - a.y) / (b.y - a.y);
                        Check(z >= edge - .002f, $"map{spot} {mesh.name} surface-crossing edge intrudes");
                    }
            }
            Check(meshes > 0, "actual scene meshes checked (deep channel may be entirely submerged)");
            Debug.Log($"[Catchline] CLEAR WATER map{spot} hull{game.State.Hull}: {tested} exposed vertices/edges; minimum bank edge {edge:F2}m; fore/aft corridor unbounded");
        }
        public static void Run()
        {
            ArtImport.BuildLibrary();
            foreach (string name in new[] { "GullHarbourMouth", "GullKelpBank", "GullSandbar", "GullRockyPoint", "GullDeepChannel" })
                Check(((ModelImporter)AssetImporter.GetAtPath("Assets/Art/Models/Environment/" + name + ".fbx")).isReadable,
                    name + " retains clearance geometry in built player");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Whole-scenery clearance fixture").AddComponent<VoyageGame>();
            game.SessionOnly = true; game.Build(); game.StartNetBoatTrial();
            Directory.CreateDirectory(Path.GetFullPath("Logs/sea014"));
            for (int hull = 0; hull < GameData.Hulls.Length; hull++)
            {
                game.State.Hull = hull;
                for (int spot = 0; spot < GameData.Spots.Length; spot++) { game.Showcase(spot, 0); Verify(game, spot); }
            }
            // Future growth test: much wider and longer than any delivered hull.
            var future = GameData.Hulls[2]; int width = future.Width, height = future.Height;
            try
            {
                future.Width = 141; future.Height = 81; game.State.Hull = 2;
                for (int spot = 0; spot < GameData.Spots.Length; spot++) { game.Showcase(spot, 0); Verify(game, spot); }
            }
            finally { future.Width = width; future.Height = height; }
            game.State.Hull = 2;
            for (int spot = 0; spot < GameData.Spots.Length; spot++)
            {
                game.Showcase(spot, 0); game.Tick(.01f); Verify(game, spot);
                typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic)
                    .Invoke(null, new object[] { game, "../sea014/map-" + spot, 1440, 900, 1f });
            }
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] SEA CLEARANCE CHECKS PASSED: all exposed meshes including docks/props;5maps x3hulls +14m future hull/8m beam");
            Debug.Log("[Catchline] Snapshot written to Logs/sea014");
        }
        public static void ValidateAndBuildPreview()
        {
            Run();
            PreviewSetupChecks.Run();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Clear fishing water preview").AddComponent<VoyageGame>(); game.SessionOnly = true;
            const string scene = "Assets/Scenes/Sea014Preview.unity";
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scene);
            string output = Path.GetFullPath("Builds/Sea014/Catchline.exe");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { scene }, locationPathName = output,
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None });
            Check(report.summary.result == BuildResult.Succeeded, "separate preview built");
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: " + output);
        }
    }
}

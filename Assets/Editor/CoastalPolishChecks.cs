using System;
using System.IO;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class CoastalPolishChecks
    {
        static void Check(bool pass, string label) { if (!pass) throw new Exception("Coastal polish check failed: " + label); }
        public static void Run()
        {
            ArtImport.BuildLibrary();
            for (int spot = 0; spot < GameData.Spots.Length; spot++)
            {
                var root = new GameObject("Coastal route check");
                var game = root.AddComponent<VoyageGame>();
                game.SessionOnly = true;
                game.Build();
                for (int i = 0; i < GameData.Spots.Length; i++) game.State.Charts.Add(i);
                game.State.FoodMinutes = 100;
                game.SelectedSpot = spot;
                var start = game.Boat.TransformPoint(game.State.HullDef.Center);
                game.SetSail();
                float duration = GameData.Spots[spot].RowSeconds / WorkSpeed.Rate(game.Captain);
                game.Tick(duration * .17f);
                Check(game.Boat.TransformPoint(game.State.HullDef.Center).z < start.z - 1.25f, "clears quay sideways before turn " + spot);
                Check(Mathf.Abs(Mathf.DeltaAngle(game.Boat.eulerAngles.y, 0)) < 1, "parallel to quay during clearance");
                game.Tick(duration * .27f);
                var bow = game.Boat.TransformDirection(Vector3.left); bow.y = 0;
                Check(Vector3.Dot(bow.normalized, VoyageGame.RouteDirection(spot)) > .99f, "bow follows chart bearing " + spot);
                game.Tick(duration);
                Check(game.CurrentMode == VoyageGame.Mode.Fishing, "outbound arrives " + spot);
                var arrived = game.Boat.TransformPoint(game.State.HullDef.Center);
                Check(Mathf.Abs(arrived.x - game.State.HullDef.Center.x) < .0001f && Mathf.Abs(arrived.z - game.State.HullDef.Center.z) < .0001f, "fishing stage restored about hull centre");
                game.HeadHome();
                game.Tick(duration * .84f);
                Check(game.Boat.TransformPoint(game.State.HullDef.Center).z < game.State.HullDef.Center.z - 1.20f, "approaches clear of quay " + spot);
                game.Tick(duration);
                Check(game.CurrentMode == VoyageGame.Mode.Harbour, "home arrives " + spot);
                Check(Mathf.Abs(Mathf.DeltaAngle(game.Boat.eulerAngles.y, 0)) < 1
                    && Mathf.Abs(game.Boat.TransformPoint(game.State.HullDef.Center).z - game.State.HullDef.Center.z) < .0001f, "parked alongside " + spot);
                UnityEngine.Object.DestroyImmediate(root);
            }
            var environment = ArtLibrary.Get().M("GullHarbourMouth");
            if (environment != null)
            {
                bool beacon = false, quay = false;
                foreach (var mesh in environment.GetComponentsInChildren<MeshFilter>())
                {
                    var center = mesh.transform.TransformPoint(mesh.sharedMesh.bounds.center);
                    if (mesh.name.Contains("Beacon")) { Check(center.x > 0, "beacon correct handedness"); beacon = true; }
                    if (mesh.name.Contains("WorkingQuay") || mesh.name.Contains("Working_Quay")) { Check(center.x > 0, "quay correct handedness"); quay = true; }
                }
                Check(beacon && quay, "authored landmarks imported");
            }
            foreach (string name in new[] { "GullKelpBank", "GullSandbar", "GullRockyPoint", "GullDeepChannel" })
            {
                var prefab = ArtLibrary.Get().M(name);
                if (prefab == null) continue; // Artist deliveries can arrive separately.
                bool terrain = false;
                foreach (var mesh in prefab.GetComponentsInChildren<MeshFilter>())
                {
                    if (mesh.name != "Terrain_ConnectedShoalsAndSeabed") continue;
                    var center = mesh.transform.TransformPoint(mesh.sharedMesh.bounds.center);
                    // All four use the same exact-camera terrain rectangle; this catches
                    // the X reflection that previously passed Blender-only round trips.
                    Check(Mathf.Abs(center.x - 1.533545f) < .002f && Mathf.Abs(center.z - .462129f) < .002f, name + " Unity terrain handedness");
                    terrain = true;
                }
                Check(terrain, name + " connected opaque depth support");
                int triangles = 0;
                foreach (var mesh in prefab.GetComponentsInChildren<MeshFilter>()) triangles += mesh.sharedMesh.triangles.Length / 3;
                Check(triangles <= 24000, name + " bounded triangle budget");
                Debug.Log($"[Catchline] ENVIRONMENT IMPORT PASSED: {name}, {triangles} triangles; terrain bounds match source axes");
            }
            Check(!ShaderUtil.ShaderHasError(ArtLibrary.Get().WaterShader), "coastal shader compiles");
            Debug.Log("[Catchline] COASTAL POLISH CHECKS PASSED");
        }

        public static void RenderMaps()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Camera-only background review").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.Build();
            string directory = Path.GetFullPath("Logs/polish004-maps");
            for (int spot = 0; spot < GameData.Spots.Length; spot++)
            {
                game.Showcase(spot, 0);
                game.Tick(.4f);
                PrototypeTools.Render(game.Cam, Path.Combine(directory, $"map-{spot}-desktop.png"), 1440, 900);
                PrototypeTools.Render(game.Cam, Path.Combine(directory, $"map-{spot}-phone.png"), 844, 390);
            }
            game.Showcase(0, 0);
            for (int frame = 0; frame < 12; frame++)
            {
                game.Tick(.12f);
                PrototypeTools.Render(game.Cam, Path.Combine(directory, $"water-{frame:00}.png"), 1440, 900);
            }
            Debug.Log("[Catchline] Snapshot written to " + directory + " (camera-only; IMGUI absent)");
        }
    }
}

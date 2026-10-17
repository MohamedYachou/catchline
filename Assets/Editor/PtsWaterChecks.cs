using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class PtsWaterChecks
    {
        static void Check(bool pass, string label)
        { if (!pass) throw new Exception("PTS water check failed: " + label); }

        public static void Run()
        {
            ArtImport.BuildLibrary();
            var lib = ArtLibrary.Get();
            Check(lib.WaterShader != null && lib.WaterShader.name == "Catchline/PTS Water" && !ShaderUtil.ShaderHasError(lib.WaterShader), "real PTS shading adapter imports");
            Check(lib.PtsWaterNormals != null && lib.PtsWaterDither != null, "original PTS surface/shadow textures referenced");
            Check(lib.PtsWaterNormals.mipmapCount > 1, "surface normals have mipmaps to avoid fine shimmer");
            var root = new GameObject("PTS water integration check");
            var game = root.AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.Build();
            var sea = root.GetComponentsInChildren<CoastalWater>().Single();
            var material = sea.GetComponent<Renderer>().sharedMaterial;
            Check(material.shader == lib.WaterShader && material.GetTexture("_SurfaceNormals") == lib.PtsWaterNormals, "live stage uses PTS material and packed normals");
            Check(material.GetFloat("_BoatAttack_water_FoamIntensity") == 0, "foam disabled");
            Check(sea.GetComponent<MeshFilter>().sharedMesh.vertexCount <= 65535, "dense water stays within mobile 16-bit index range");
            game.Showcase(0, 0);
            game.Tick(.5f);
            Check(Mathf.Abs(material.GetFloat("_Clock") - PtsWater.Clock(game.SimTime)) < .001f, "waves follow slowed voyage simulation clock");
            Vector3 center = game.Boat.TransformPoint(game.State.HullDef.Center);
            Quaternion rotation = game.Boat.localRotation;
            game.Tick(0);
            Check(Vector3.Distance(center, game.Boat.TransformPoint(game.State.HullDef.Center)) < .00001f
                && Quaternion.Angle(rotation, game.Boat.localRotation) < .001f, "paused water and hull pose stay still");
            float minHeight = center.y, maxHeight = center.y;
            for (int frame = 0; frame < 80; frame++)
            {
                game.Tick(.1f);
                Vector3 moved = game.Boat.TransformPoint(game.State.HullDef.Center);
                Check(Vector2.Distance(new Vector2(center.x, center.z), new Vector2(moved.x, moved.z)) < .0001f,
                    "rocking stays centred on hull without horizontal deck drift");
                Check(Mathf.Abs(moved.y - game.State.HullDef.Center.y) < .055f, "heave stays subtle");
                minHeight = Mathf.Min(minHeight, moved.y); maxHeight = Mathf.Max(maxHeight, moved.y);
            }
            Check(maxHeight - minHeight > .001f, "boat follows changing surface height");
            float harbourVisibility = material.GetFloat("_MaxDepth");
            game.Showcase(4, 0);
            Check(material.GetFloat("_MaxDepth") < harbourVisibility, "deep channel obscures finite seabed edge");
            game.Showcase(2, 0);
            foreach (var terrain in root.GetComponentsInChildren<Renderer>().Where(r => r.name == "Terrain_ConnectedShoalsAndSeabed"))
                Check(!terrain.sharedMaterials.Any(m => m.color == Palette.Hex("BEA77D")), "sand wetness comes from water depth rather than square material bands");
            var camera = game.Cam;
            UnityEngine.Object.DestroyImmediate(root);
            Check(sea == null && camera == null, "disposing a voyage removes its water and camera");
            Debug.Log("[Catchline] PTS WATER INTEGRATION CHECKS PASSED");
        }

        public static void RestoreAndBuild()
        {
            ArtImport.BuildLibrary();
            Directory.CreateDirectory("Logs/water025");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Restored water025 native view").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build(); g.StartNetBoatTrial(); g.Tick(.5f);
            var material = g.GetComponentInChildren<CoastalWater>().GetComponent<Renderer>().sharedMaterial;
            Check(material.shader.name == "Catchline/PTS Water", "restored actual runtime shader before capture");
            var shot = typeof(ReferenceHudChecks).GetMethod("Shot", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic);
            shot.Invoke(null, new object[] { g, "../water025/restored-desktop", 1440, 900, 1f });
            shot.Invoke(null, new object[] { g, "../water025/restored-phone", 844, 390, 1f });
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            ProgressionLaunchChecks.BuildBoth();
            Debug.Log("[Catchline] WATER025 RESTORE AND BUILDS PASSED");
        }

        public static void Capture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Run();
            var game = new GameObject("PTS background map capture").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.Build();
            string folder = Path.GetFullPath("Logs/pts-water-integrated");
            for (int map = 0; map < 5; map++)
            {
                game.Showcase(map, 0);
                game.Tick(.1f);
                PrototypeTools.Render(game.Cam, Path.Combine(folder, $"map-{map}-desktop.png"), 1440, 900);
                PrototypeTools.Render(game.Cam, Path.Combine(folder, $"map-{map}-phone.png"), 844, 390);
            }
            game.Showcase(0, 0);
            game.Tick(.1f);
            var material = game.GetComponentInChildren<CoastalWater>().GetComponent<Renderer>().sharedMaterial;
            // Freeze every scene object; only the water's simulation clock changes.
            for (int frame = 0; frame < 20; frame++)
            {
                material.SetFloat("_Clock", PtsWater.Clock(frame * .16f));
                PrototypeTools.Render(game.Cam, Path.Combine(folder, $"water-{frame:00}.png"), 1080, 675);
            }
            material.SetFloat("_Clock", PtsWater.Clock(.64f));
            float detailScale = material.GetFloat("_DetailScale");
            foreach (float scale in new[] { .8f, 1.6f, 3.2f })
            {
                material.SetFloat("_DetailScale", scale);
                PrototypeTools.Render(game.Cam, Path.Combine(folder, $"ripple-scale-{scale:F1}.png"), 1440, 900);
            }
            material.SetFloat("_DetailScale", detailScale);
            PrototypeTools.Render(game.Cam, Path.Combine(folder, "sun-reflection-on.png"), 1080, 675);
            float specularStrength = material.GetFloat("_SpecularStrength");
            material.SetFloat("_SpecularStrength", 0);
            PrototypeTools.Render(game.Cam, Path.Combine(folder, "sun-reflection-off.png"), 1080, 675);
            material.SetFloat("_SpecularStrength", specularStrength);
            Debug.Log("[Catchline] Snapshot written to " + folder + " (scene-only; runtime HUD not captured)");
        }

        public static void CaptureBuoyancy()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            Run();
            var game = new GameObject("Coupled boat/water background capture").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.Build();
            game.Showcase(0, 0);
            game.Tick(.1f);
            Vector3 cameraPosition = game.Cam.transform.position;
            float cameraSize = game.Cam.orthographicSize;
            string folder = Path.GetFullPath("Logs/water007-coupled");
            for (int frame = 0; frame < 40; frame++)
            {
                game.Tick(.16f);
                // Hold the camera steady so the actual hull bob/rock is visible.
                game.Cam.transform.position = cameraPosition;
                game.Cam.orthographicSize = cameraSize;
                PrototypeTools.Render(game.Cam, Path.Combine(folder, $"motion-{frame:00}.png"), 1080, 675);
            }
            PrototypeTools.Render(game.Cam, Path.Combine(folder, "phone.png"), 844, 390);
            Debug.Log("[Catchline] Snapshot written to " + folder + " (coupled boat/water, fixed camera; no HUD)");
        }
    }
}

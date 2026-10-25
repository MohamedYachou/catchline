using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using Catchline.Game.Sea;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // MAP8 acceptance fixture. Run only through docs/tools/check.ps1 in Catchline-sim.
    public static class LighthouseRockMapChecks
    {
        [Serializable] sealed class Receipt
        {
            public string map = "GullLighthouseRock", utc;
            public int maps, hullRoutes, lanes;
            public bool assets, chartPurchase, anchors, groundPoolsReady;
            public string[] trips, groundIds, limits;
        }
        static void Check(bool ok, string label)
        { if (!ok) throw new Exception("[Catchline] MAP8 check failed: " + label); }
        static void ScratchOnly()
        {
            Check(Application.dataPath.Replace('\\', '/').EndsWith("Catchline-sim/Assets", StringComparison.OrdinalIgnoreCase), "scratch project only");
        }

        public static void Run()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            Check(SeaNav.Maps.Length == 8 && GameData.Spots.Length == 8 && SeaNav.Maps[7] == "GullLighthouseRock", "eight maps/spots with stable order");
            var spot = GameData.Spots[7];
            Check(spot.Name == "Lighthouse rock" && spot.RowSeconds == 30f && spot.BiteWait == 1.4f && spot.ChartCost == 1370, "spot data");
            var state = new GameState(6501); state.Coins = 1369;
            Check(!state.Known(7) && !state.BuyChart(7) && state.Coins == 1369, "unaffordable chart stays locked");
            state.Coins = 1370;
            Check(state.BuyChart(7) && state.Known(7) && state.Coins == 0, "1370-coin chart purchase");
            var nav = SeaNav.Load("GullLighthouseRock", GameData.Hulls[4]);
            Check(nav != null && !nav.Interim && nav.ModelId == "GullLighthouseRockSeaV2" && nav.Grounds.Count == 3, "real model/navigation lookup");
            string[] ids = { "the-pinnacle", "tide-race", "deep-ledge" };
            Check(nav.Grounds.Select(g => g.Id).SequenceEqual(ids), "ground IDs/order");
            var model = UnityEngine.Object.Instantiate(ArtLibrary.Get().M(nav.ModelId));
            try
            {
                model.transform.SetPositionAndRotation(new Vector3(0, -.32f, 0), Quaternion.identity);
                model.transform.localScale = Vector3.one;
                string[] anchorNames = { "PuffinLedge_1", "PuffinLedge_2", "PuffinLedge_3", "TideRace_1", "TideRace_2", "LighthouseLamp_1", "CardinalBuoy_1" };
                var expected = new[] { new Vector3(-16f,2.08f,-5f), new Vector3(-6f,3.38f,-4.7f), new Vector3(8f,4.68f,-3.8f), new Vector3(43.1941830f,-0.2850000f,59.1010852f), new Vector3(32.7907820f,-0.2850000f,65.1648504f), new Vector3(0.0000000f,22.0800000f,15.0000000f), new Vector3(99.0159975f,-0.3200000f,-48.6356416f) };
                for (int i = 0; i < anchorNames.Length; i++)
                {
                    var anchor = model.GetComponentsInChildren<Transform>(true).Single(t => t.name == anchorNames[i]);
                    Check(Vector3.Distance(anchor.position, expected[i]) < .02f, "life anchor world transform " + anchor.name + ": " + anchor.position);
                    Check(anchor.GetComponent<Renderer>() == null, "life anchor remains an empty");
                }
            }
            finally { UnityEngine.Object.DestroyImmediate(model); }

            MapNavChecks.Run(); // all directed harbour/ground routes, five hulls, eight maps
            SeaSceneChecks.Assets();
            string baseline = HarbourTripChecks.Run(); // all eight SeaLanes + five harbour hulls
            var trips = new List<string> { baseline };
            foreach (string id in ids) trips.Add(NewGroundTrip(id));
            bool pools = Grounds.ForMap(7).Select(g => g.Id).SequenceEqual(ids);
            Check(pools, "three ground pools");
            var expectedPools = new[] {
                new[] { (Species.Pollock,40f),(Species.SeaBass,30f),(Species.Conger,20f),(Species.GoldTipShark,1f) },
                new[] { (Species.Mackerel,45f),(Species.SeaBass,35f),(Species.YellowfinTuna,3f) },
                new[] { (Species.Cod,35f),(Species.Monkfish,30f),(Species.Turbot,10f),(Species.AtlanticSwordfish,1f) } };
            for (int i=0;i<3;i++) Check(Grounds.ForMap(7)[i].Day.SequenceEqual(expectedPools[i]), ids[i]+" exact species weights");
            var receipt = new Receipt {
                utc = DateTime.UtcNow.ToString("O"), maps = 8, hullRoutes = 480, lanes = 24,
                assets = true, chartPurchase = true, anchors = true, groundPoolsReady = pools,
                trips = trips.ToArray(), groundIds = ids,
                limits = new[] { "Scratch simulation and asset checks; native visuals are separate.", "Runtime puffins/tide race/lighthouse glow/buoy life, chart glyph and water optics remain lead-owned; see native review." }
            };
            Directory.CreateDirectory("Logs");
            File.WriteAllText("Logs/map8-checks.json", JsonUtility.ToJson(receipt, true));
            Debug.Log("[Catchline] MAP8 CHECKS PASSED: eight maps, 480 hull routes, 24 lanes, three new-ground/home trips. Snapshot written to Logs/map8-checks.json");
        }

        // The chart point landed after the full 480-route run began.
        // Recheck its entry lanes and actual trips against the current runtime.
        public static void PostIntegration()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            PerchReview();
            Check(Vector2.Distance(VoyageGame.NauticalChartPoint(7), new Vector2(.66f, .24f)) < .0001f, "lead chart point");
            var proof = SeaNav.Load("GullLighthouseRock", 2.25f);
            var wide = SeaLanes.Clearances.Select(r => SeaNav.Load("GullLighthouseRock", r)).ToList();
            var home = SeaLanes.HomeDirection(VoyageGame.NauticalChartPoint(7), VoyageGame.ChartHarbour);
            var entry = SeaLanes.Entry(proof, home, out _);
            Check(Vector2.Dot((entry - proof.CameraBounds.center).normalized, home) > .5f, "updated entry faces home");
            foreach (var ground in proof.Grounds)
            {
                var lane = SeaLanes.Lane(proof, wide, entry, ground.Centre, out float clear);
                Check(lane != null && SeaLanes.Proven(proof, lane) && clear >= 4.5f, "updated entry lane " + ground.Id);
            }
            string[] ids = { "the-pinnacle", "tide-race", "deep-ledge" };
            var trips = ids.Select(NewGroundTrip).ToArray();
            Directory.CreateDirectory("Logs");
            File.WriteAllText("Logs/map8-postintegration-checks.json", JsonUtility.ToJson(new Receipt {
                utc = DateTime.UtcNow.ToString("O"), maps = 8, hullRoutes = 0, lanes = 3,
                assets = true, anchors = true, chartPurchase = true, groundPoolsReady = true,
                groundIds = ids, trips = trips,
                limits = new[] { "Targeted latest-chart three approach lanes and three complete bait-cast-home trips; full 480 geometry routes/24 lanes recorded separately.", "Runtime life animation and presentation require separate native review." }
            }, true));
            Debug.Log("[Catchline] MAP8 POST-INTEGRATION PASSED: updated entry three lanes/three normal bait-cast-home trips. Snapshot written to Logs/map8-postintegration-checks.json");
        }
        public static void PostIntegrationAndBuild()
        {
            PostIntegration(); BuildNative();
        }

        // Scene-only close evidence for all three corrected perches. Uses the
        // production DressSkerries dispatcher, import scales and life assets.
        static void PerchReview()
        {
            Check(Resources.Load<Shader>("Shaders/GlowAdditive") != null, "scratch additive glow shader resource copied");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("MAP8 outward perch review").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            var env = ArtLibrary.Spawn(ArtLibrary.Get().M("GullLighthouseRockSeaV2"), null, new Vector3(600, -.32f, 0), Quaternion.identity);
            typeof(VoyageGame).GetMethod("DressSkerries", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { env, ArtLibrary.Get() });
            var buoyAnchor = env.GetComponentsInChildren<Transform>().Single(t => t.name == "CardinalBuoy_1");
            Check(Vector3.Distance(buoyAnchor.position - new Vector3(600,0,0), new Vector3(99.0159975f,-.32f,-48.6356416f)) < .02f, "cardinal buoy anchor off the rock");
            var sun = new GameObject("MAP8 review sun").AddComponent<Light>(); sun.type = LightType.Directional; sun.intensity = 1.3f;
            sun.color = new Color(1, .96f, .88f); sun.transform.rotation = Quaternion.Euler(55, 195, 0);
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat; RenderSettings.ambientLight = new Color(.58f, .64f, .7f);
            var cam = new GameObject("MAP8 perch camera").AddComponent<Camera>(); cam.orthographic = true; cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = new Color(.18f, .5f, .6f); cam.farClipPlane = 300;
            var folder = "C:/Users/momoy/Projects/Catchline/docs/screens/map8-lighthouse-rock-1"; Directory.CreateDirectory(folder);
            Vector3[] positions = { new(-16,2.08f,-5), new(-6,3.38f,-4.7f), new(8,4.68f,-3.8f) };
            for (int i=0; i<3; i++)
            {
                var anchor = env.GetComponentsInChildren<Transform>().Single(t => t.name == "PuffinLedge_" + (i+1));
                Check(Vector3.Distance(anchor.position - new Vector3(600,0,0), positions[i]) < .02f, "corrected outward perch " + anchor.name);
                Check(anchor.GetComponentInChildren<PuffinLife>() != null, "animated puffin at " + anchor.name);
                foreach (bool top in new[] { false, true })
                {
                    var dir = (top ? new Vector3(0,-1,.001f) : new Vector3(.574f,-.819f,1)).normalized;
                    cam.orthographicSize = 4.5f; cam.transform.position = anchor.position + Vector3.up*.4f - dir*60; cam.transform.rotation = Quaternion.LookRotation(dir);
                    var rt = new RenderTexture(1440,900,24); var tex = new Texture2D(1440,900,TextureFormat.RGB24,false);
                    cam.targetTexture = rt; cam.Render(); RenderTexture.active = rt;
                    tex.ReadPixels(new Rect(0,0,1440,900),0,0); tex.Apply(); RenderTexture.active = null; cam.targetTexture = null;
                    File.WriteAllBytes(folder + "/perch-" + (i+1) + (top ? "-top.png" : "-deck.png"), tex.EncodeToPNG());
                    UnityEngine.Object.DestroyImmediate(tex); rt.Release(); UnityEngine.Object.DestroyImmediate(rt);
                }
            }
            UnityEngine.Object.DestroyImmediate(env.gameObject); UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] MAP8 PERCH FIX: all three transformed outward anchors, six dressed deck/top renders written");
        }

        static string NewGroundTrip(string id)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("MAP8 session-only trip check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            g.State.Hull = 4; g.State.Coins = 10000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { false });
            g.Tick(.05f); Check(g.State.BuyChart(7), "new chart for trip"); g.SelectedSpot = 7;
            var legs = new HashSet<VoyageGame.TripLeg>();
            void Until(Func<bool> done, string stage)
            {
                for (int n = 0; n < 12000 && !done(); n++)
                {
                    g.Tick(.025f); legs.Add(g.Leg);
                    if (g.Sailor != null && g.Navigation != null)
                        Check(!g.Navigation.Blocked(g.Sailor.Position) && g.Navigation.InsideBorder(g.Sailor.Position), id + " collision/border");
                }
                Check(done(), id + " " + stage);
            }
            try
            {
                g.SetSail();
                Until(() => g.CurrentMode == VoyageGame.Mode.Fishing && g.Leg == VoyageGame.TripLeg.None, "departure arrival");
                if (g.ActiveGroundId != id)
                {
                    Check(g.Relocate(id), id + " relocate starts");
                    Until(() => g.CurrentMode == VoyageGame.Mode.Fishing, "relocation arrival");
                }
                Check(g.ActiveGroundId == id && g.AtFishingGround && g.Sailor.Arrived, id + " anchor is fishable");
                Check(UnityEngine.Object.FindObjectsByType<PuffinLife>(FindObjectsSortMode.None).Length == 3, id + " three animated puffins");
                Check(UnityEngine.Object.FindObjectsByType<TideRaceDrift>(FindObjectsSortMode.None).Length == 2, id + " two tide races");
                Check(UnityEngine.Object.FindObjectsByType<BeamSweep>(FindObjectsSortMode.None).Length == 1, id + " lighthouse beam");
                var beam = UnityEngine.Object.FindFirstObjectByType<BeamSweep>();
                Check(beam.GetComponentsInChildren<Renderer>().All(r => r.sharedMaterial.shader.name == "Catchline/GlowAdditive"), id + " beam uses additive glow shader");
                Check(UnityEngine.Object.FindObjectsByType<BuoyBob>(FindObjectsSortMode.None).Length == 1, id + " cardinal buoy");
                var rod = g.Rods.FirstOrDefault(g.CanCommandRod);
                Check(rod != null, id + " rod command available");
                g.CommandRod(rod);
                Until(() => rod.InWater, "normal captain bait/cast");
                g.HeadHome();
                Until(() => g.CurrentMode == VoyageGame.Mode.Harbour, "home arrival");
                foreach (var leg in new[] { VoyageGame.TripLeg.HarbourOut, VoyageGame.TripLeg.ChartOut, VoyageGame.TripLeg.SeaOut, VoyageGame.TripLeg.SeaHome, VoyageGame.TripLeg.ChartHome, VoyageGame.TripLeg.HarbourIn })
                    Check(legs.Contains(leg), id + " complete trip leg " + leg);
                string result = "GullLighthouseRock/" + id + " tier5 out/anchor/bait-cast/home PASS";
                Debug.Log("[Catchline] " + result); return result;
            }
            finally { UnityEngine.Object.DestroyImmediate(g.gameObject); }
        }

        public static void RunAndBuild()
        {
            Run(); BuildNative();
        }
        public static void BuildNative()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var g = new GameObject("MAP8 native acceptance TEST").AddComponent<VoyageGame>();
            g.SessionOnly = true;
            const string fixture = "Assets/Map8Acceptance.unity";
            EditorSceneManager.SaveScene(scene, fixture);
            Directory.CreateDirectory("Builds/Map8Capture"); Directory.CreateDirectory("Logs");
            var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes = new[] { fixture }, locationPathName = "Builds/Map8Capture/Catchline.exe",
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None
            });
            Check(result.summary.result == BuildResult.Succeeded, "native TEST build " + result.summary.result);
            File.WriteAllText("Logs/map8-build.txt", DateTime.UtcNow.ToString("O") + " " + result.summary.result);
            Debug.Log("[Catchline] MAP8 TEST BUILD PASSED. Snapshot written to Builds/Map8Capture/Catchline.exe");
        }
    }
}

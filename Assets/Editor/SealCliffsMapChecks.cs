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
    // MAP10 acceptance fixture. Run only through docs/tools/check.ps1 in Catchline-sim.
    public static class SealCliffsMapChecks
    {
        [Serializable] sealed class Receipt
        {
            public string map = "GullSealCliffs", utc;
            public int maps, hullRoutes, lanes;
            public bool assets, chartPurchase, anchors, groundPoolsReady;
            public string[] trips, groundIds, limits;
        }
        static void Check(bool ok, string label)
        { if (!ok) throw new Exception("[Catchline] MAP10 check failed: " + label); }
        static void ScratchOnly()
        {
            Check(Application.dataPath.Replace('\\', '/').EndsWith("Catchline-sim/Assets", StringComparison.OrdinalIgnoreCase), "scratch project only");
        }

        public static void Run()
        { RunChecks(true); }
        static void RunChecks(bool allMaps)
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            Check(SeaNav.Maps.Length == 10 && GameData.Spots.Length == 10 && SeaNav.Maps[9] == "GullSealCliffs", "ten maps/spots with stable order");
            var spot = GameData.Spots[9];
            Check(spot.Name == "Seal cliffs" && spot.RowSeconds == 36f && spot.BiteWait == 1.5f && spot.ChartCost == 32000, "spot data");
            var state = new GameState(6501); state.Coins = 32000;
            Check(!state.BuyChart(9) && state.Coins == 32000, "Outer coast chart needs a tier 4 boat");
            state.Hull = 3; state.Coins = 31999;
            Check(!state.Known(9) && !state.BuyChart(9) && state.Coins == 31999, "unaffordable chart stays locked");
            state.Coins = 32000;
            Check(state.BuyChart(9) && state.Known(9) && state.Coins == 0, "32000-coin chart purchase");
            var nav = SeaNav.Load("GullSealCliffs", GameData.Hulls[4]);
            Check(nav != null && !nav.Interim && nav.ModelId == "GullSealCliffsSeaV2" && nav.Grounds.Count == 3, "real model/navigation lookup");
            string[] ids = { "arch-pool", "seal-cove", "stack-race" };
            Check(nav.Grounds.Select(g => g.Id).SequenceEqual(ids), "ground IDs/order");
            var model = UnityEngine.Object.Instantiate(ArtLibrary.Get().M(nav.ModelId));
            try
            {
                model.transform.SetPositionAndRotation(new Vector3(0, -.32f, 0), Quaternion.identity);
                model.transform.localScale = Vector3.one;
                string[] anchorNames = { "SealHaulout_1", "SealHaulout_2", "SealHaulout_3", "CliffGulls_1", "CliffGulls_2", "ArchSpray_1" };
                var expected = new[] { new Vector3(-5.0000000f,0.5800000f,68.0000000f), new Vector3(2.0000000f,0.7800000f,68.0000000f), new Vector3(9.0000000f,0.6800000f,68.0000000f), new Vector3(-37.0000000f,5.6800000f,76.0000000f), new Vector3(67.0000000f,6.8800000f,77.0000000f), new Vector3(-74.0000000f,-0.3200000f,52.0000000f) };
                for (int i = 0; i < anchorNames.Length; i++)
                {
                    var anchor = model.GetComponentsInChildren<Transform>(true).Single(t => t.name == anchorNames[i]);
                    Check(Vector3.Distance(anchor.position, expected[i]) < .02f, "life anchor world transform " + anchor.name + ": " + anchor.position);
                    Check(anchor.GetComponent<Renderer>() == null, "life anchor remains an empty");
                }
            }
            finally { UnityEngine.Object.DestroyImmediate(model); }

            if (allMaps) MapNavChecks.Run();
            else FinalMapRoutes();
            ShelfSceneAssets();
            string baseline = HarbourTripChecks.Run(); // all ten SeaLanes + five harbour hulls
            var trips = new List<string> { baseline };
            foreach (string id in ids) trips.Add(NewGroundTrip(id));
            bool pools = Grounds.ForMap(9).Select(g => g.Id).SequenceEqual(ids);
            Check(pools, "three ground pools");
            var expectedPools = new[] {
                new[] { (Species.Pollock,40f),(Species.RedMullet,30f),(Species.Conger,15f),(Species.Crab,2f) },
                new[] { (Species.Mackerel,40f),(Species.Herring,30f),(Species.SeaBass,20f),(Species.RedMullet,3f) },
                new[] { (Species.Cod,35f),(Species.Pollock,30f),(Species.Conger,15f),(Species.Turbot,1f) } };
            for (int i=0;i<3;i++) Check(Grounds.ForMap(9)[i].Day.SequenceEqual(expectedPools[i]), ids[i]+" exact species weights");
            var receipt = new Receipt {
                utc = DateTime.UtcNow.ToString("O"), maps = 10, hullRoutes = allMaps ? 600 : 60, lanes = 30,
                assets = true, chartPurchase = true, anchors = true, groundPoolsReady = pools,
                trips = trips.ToArray(), groundIds = ids,
                limits = new[] { "Scratch simulation and asset checks; native visuals are separate.", "Runtime seals/gulls/spray life, chart glyph and water optics remain lead-owned; see native review." }
            };
            Directory.CreateDirectory("Logs");
            string output = allMaps ? "Logs/map10-checks.json" : "Logs/map10-final-checks.json";
            File.WriteAllText(output, JsonUtility.ToJson(receipt, true));
            Debug.Log("[Catchline] MAP10 CHECKS PASSED: ten maps, " + receipt.hullRoutes + " hull routes, 30 lanes, three new-ground/home trips. Snapshot written to " + output);
        }

        // Keep the shared scene checks, with MAP10's explicitly open-water art contract.
        // No horizon islands are added to the one-seamount shelf for an older-map assertion.
        static void ShelfSceneAssets()
        {
            Check(Resources.Load<Shader>("SeaOverlay") != null, "overlay included in player resources");
            foreach (string map in SeaNav.Maps)
            {
                var nav = SeaNav.Load(map, GameData.Hulls[0]);
                Check(nav != null && !nav.Interim, map + " real navigation");
                var model = ArtLibrary.Get().M(nav.ModelId);
                Check(model != null, map + " authored model");
                if (map != "GullWhaleShelf")
                    Check(model.GetComponentsInChildren<Transform>(true).Any(t => t.name.StartsWith("Horizon")), map + " horizon silhouettes");
                else
                    Check(model.GetComponentsInChildren<Transform>(true).Count(t => t.name == "WreckGulls_1") == 1, "MAP10 single sea-mount crown anchor");
                var root = new GameObject("Shelf sea environment check");
                var water = new Material(ArtLibrary.Get().WaterShader);
                try
                {
                    var surface = CoastalWater.Build(root.transform, water);
                    var env = root.AddComponent<SeaEnvironment>(); env.Build(nav, surface.transform, water);
                    var ocean = surface.transform.Find("Water to horizon").GetComponent<MeshFilter>().sharedMesh;
                    Check(ocean.bounds.size.x >= 4096 && ocean.vertexCount < 25000, map + " bounded-cost horizon water");
                    env.Follow(nav.Harbour); float harbourFog = RenderSettings.fogDensity;
                    env.Follow(nav.Snap(nav.Border[0]));
                    Check(RenderSettings.fogDensity > harbourFog, map + " fog increases near border");
                }
                finally { UnityEngine.Object.DestroyImmediate(root); UnityEngine.Object.DestroyImmediate(water); }
            }
            Debug.Log("[Catchline] MAP10 SEA SCENE ASSETS PASSED: ten real maps, older horizon models, open shelf, ocean extension and border fog");
        }

        // Only MAP10 terrain changed after the full nine-map run. Recheck all 60
        // affected directed routes, plus every sea lane and the three live trips.
        static void FinalMapRoutes()
        {
            int routes = 0;
            foreach (var hull in GameData.Hulls)
            {
                var nav = SeaNav.Load("GullSealCliffs", hull);
                var destinations = nav.Grounds.Select(g => g.Centre).Prepend(nav.Harbour).ToArray();
                for (int a=0;a<destinations.Length;a++) for (int b=0;b<destinations.Length;b++)
                {
                    if (a==b) continue;
                    var route=nav.Plan(destinations[a],destinations[b]);
                    Check(route!=null,"final route exists");
                    foreach (var p in route) Check(!nav.Blocked(p)&&nav.InsideBorder(p),"final clear waypoint");
                    for(int k=1;k<route.Count;k++) Check(nav.Visible(route[k-1],route[k]),"final clear segment");
                    var sailor=new BoatSailor(nav,hull,destinations[a]);
                    Check(sailor.SailTo(destinations[b]),"final sailor starts");
                    float elapsed=0;
                    while(!sailor.Arrived&&elapsed<120)
                    {
                        sailor.Tick(.05f);elapsed+=.05f;
                        Check(!nav.Blocked(sailor.Position)&&nav.InsideBorder(sailor.Position),"final collision-free sailing");
                    }
                    Check(sailor.Arrived&&Vector2.Distance(sailor.Position,destinations[b])<.4f,"final sailor arrives");routes++;
                }
            }
            Check(routes==60,"all affected hull routes");
            Debug.Log("[Catchline] MAP10 FINAL TERRAIN ROUTES PASSED: 60 directed hull routes");
        }

        static string NewGroundTrip(string id)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("MAP10 session-only trip check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            g.State.Hull = 4; g.State.Coins = 40000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { false });
            g.Tick(.05f); Check(g.State.BuyChart(9), "new chart for trip"); g.SelectedSpot = 9;
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
                var rod = g.Rods.FirstOrDefault(g.CanCommandRod);
                Check(rod != null, id + " rod command available");
                g.CommandRod(rod);
                Until(() => rod.InWater, "normal captain bait/cast");
                g.HeadHome();
                Until(() => g.CurrentMode == VoyageGame.Mode.Harbour, "home arrival");
                foreach (var leg in new[] { VoyageGame.TripLeg.HarbourOut, VoyageGame.TripLeg.ChartOut, VoyageGame.TripLeg.SeaOut, VoyageGame.TripLeg.SeaHome, VoyageGame.TripLeg.ChartHome, VoyageGame.TripLeg.HarbourIn })
                    Check(legs.Contains(leg), id + " complete trip leg " + leg);
                string result = "GullSealCliffs/" + id + " tier5 out/anchor/bait-cast/home PASS";
                Debug.Log("[Catchline] " + result); return result;
            }
            finally { UnityEngine.Object.DestroyImmediate(g.gameObject); }
        }

        public static void RunAndBuild()
        {
            Run(); BuildNative();
        }
        public static void FinalTerrainAndBuild()
        { RunChecks(false); BuildNative(); }
        public static void BuildNative()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var g = new GameObject("MAP10 native acceptance TEST").AddComponent<VoyageGame>();
            g.SessionOnly = true;
            const string fixture = "Assets/Map10Acceptance.unity";
            EditorSceneManager.SaveScene(scene, fixture);
            Directory.CreateDirectory("Builds/Map10Capture"); Directory.CreateDirectory("Logs");
            var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes = new[] { fixture }, locationPathName = "Builds/Map10Capture/Catchline.exe",
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None
            });
            Check(result.summary.result == BuildResult.Succeeded, "native TEST build " + result.summary.result);
            File.WriteAllText("Logs/map10-build.txt", DateTime.UtcNow.ToString("O") + " " + result.summary.result);
            Debug.Log("[Catchline] MAP10 TEST BUILD PASSED. Snapshot written to Builds/Map10Capture/Catchline.exe");
        }
    }
}


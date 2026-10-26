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
    // MAP9 acceptance fixture. Run only through docs/tools/check.ps1 in Catchline-sim.
    public static class WhaleShelfMapChecks
    {
        [Serializable] sealed class Receipt
        {
            public string map = "GullWhaleShelf", utc;
            public int maps, hullRoutes, lanes;
            public bool assets, chartPurchase, anchors, groundPoolsReady;
            public string[] trips, groundIds, limits;
        }
        static void Check(bool ok, string label)
        { if (!ok) throw new Exception("[Catchline] MAP9 check failed: " + label); }
        static void ScratchOnly()
        {
            Check(Application.dataPath.Replace('\\', '/').EndsWith("Catchline-sim/Assets", StringComparison.OrdinalIgnoreCase), "scratch project only");
        }

        public static void Run()
        { RunChecks(true); }
        static void RunChecks(bool allMaps)
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            Check(SeaNav.Maps.Length >= 9 && GameData.Spots.Length == SeaNav.Maps.Length && SeaNav.Maps[8] == "GullWhaleShelf", "Whale shelf stays map/spot 8 as later maps are added");
            var spot = GameData.Spots[8];
            Check(spot.Name == "Whale shelf" && spot.RowSeconds == 34f && spot.BiteWait == 1.5f && spot.ChartCost == 8500, "spot data");
            var state = new GameState(6501); state.Coins = 8500;
            Check(!state.BuyChart(8) && state.Coins == 8500, "Outer coast chart needs a tier 3 boat");
            state.Hull = 2; state.Coins = 8499;
            Check(!state.Known(8) && !state.BuyChart(8) && state.Coins == 8499, "unaffordable chart stays locked");
            state.Coins = 8500;
            Check(state.BuyChart(8) && state.Known(8) && state.Coins == 0, "8500-coin chart purchase");
            var nav = SeaNav.Load("GullWhaleShelf", GameData.Hulls[4]);
            Check(nav != null && !nav.Interim && nav.ModelId == "GullWhaleShelfSeaV2" && nav.Grounds.Count == 3, "real model/navigation lookup");
            string[] ids = { "herring-shoals", "shelf-edge", "whale-road" };
            Check(nav.Grounds.Select(g => g.Id).SequenceEqual(ids), "ground IDs/order");
            var model = UnityEngine.Object.Instantiate(ArtLibrary.Get().M(nav.ModelId));
            try
            {
                model.transform.SetPositionAndRotation(new Vector3(0, -.32f, 0), Quaternion.identity);
                model.transform.localScale = Vector3.one;
                string[] anchorNames = { "GannetDive_1", "GannetDive_2", "WhaleSpout_1", "WhaleSpout_2", "CardinalBuoy_1", "WreckGulls_1" };
                var expected = new[] { new Vector3(-89.0000000f,-0.3200000f,-41.0000000f), new Vector3(-79.0000000f,-0.3200000f,-38.0000000f), new Vector3(107.0000000f,-0.3200000f,-48.0000000f), new Vector3(118.0000000f,-0.3200000f,-44.0000000f), new Vector3(9.0159975f,-0.3200000f,63.3643584f), new Vector3(-23.0000000f,1.0800000f,15.0000000f) };
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
            string baseline = HarbourTripChecks.Run(); // all nine SeaLanes + five harbour hulls
            var trips = new List<string> { baseline };
            foreach (string id in ids) trips.Add(NewGroundTrip(id));
            bool pools = Grounds.ForMap(8).Select(g => g.Id).SequenceEqual(ids);
            Check(pools, "three ground pools");
            var expectedPools = new[] {
                new[] { (Species.Herring,50f),(Species.Mackerel,35f),(Species.Whiting,12f),(Species.FlyingFish,2f) },
                new[] { (Species.Cod,30f),(Species.Pollock,30f),(Species.Conger,20f),(Species.Turbot,10f),(Species.AbyssalGreatWhite,1f) },
                new[] { (Species.Mackerel,35f),(Species.SeaBass,25f),(Species.Pollock,20f),(Species.SpottedEagleRay,3f) } };
            for (int i=0;i<3;i++) Check(Grounds.ForMap(8)[i].Day.SequenceEqual(expectedPools[i]), ids[i]+" exact species weights");
            var receipt = new Receipt {
                utc = DateTime.UtcNow.ToString("O"), maps = 9, hullRoutes = allMaps ? 540 : 60, lanes = 27,
                assets = true, chartPurchase = true, anchors = true, groundPoolsReady = pools,
                trips = trips.ToArray(), groundIds = ids,
                limits = new[] { "Scratch simulation and asset checks; native visuals are separate.", "Runtime gannets/whale spouts/gulls/buoy life, chart glyph and water optics remain lead-owned; see native review." }
            };
            Directory.CreateDirectory("Logs");
            string output = allMaps ? "Logs/map9-checks.json" : "Logs/map9-final-checks.json";
            File.WriteAllText(output, JsonUtility.ToJson(receipt, true));
            Debug.Log("[Catchline] MAP9 CHECKS PASSED: nine maps, " + receipt.hullRoutes + " hull routes, 27 lanes, three new-ground/home trips. Snapshot written to " + output);
        }

        // Keep the shared scene checks, with MAP9's explicitly open-water art contract.
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
                    Check(model.GetComponentsInChildren<Transform>(true).Count(t => t.name == "WreckGulls_1") == 1, "MAP9 single sea-mount crown anchor");
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
            Debug.Log("[Catchline] MAP9 SEA SCENE ASSETS PASSED: nine real maps, older horizon models, open shelf, ocean extension and border fog");
        }

        // Only MAP9 terrain changed after the full nine-map run. Recheck all 60
        // affected directed routes, plus every sea lane and the three live trips.
        static void FinalMapRoutes()
        {
            int routes = 0;
            foreach (var hull in GameData.Hulls)
            {
                var nav = SeaNav.Load("GullWhaleShelf", hull);
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
            Debug.Log("[Catchline] MAP9 FINAL TERRAIN ROUTES PASSED: 60 directed hull routes");
        }

        static string NewGroundTrip(string id)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("MAP9 session-only trip check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            g.State.Hull = 4; g.State.Coins = 20000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { false });
            g.Tick(.05f); Check(g.State.BuyChart(8), "new chart for trip"); g.SelectedSpot = 8;
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
                string result = "GullWhaleShelf/" + id + " tier5 out/anchor/bait-cast/home PASS";
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
        public static void ChartHandoffAndBuild()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            var trips = new[] { "herring-shoals", "shelf-edge", "whale-road" }
                .Select(NewGroundTrip).ToArray();
            Directory.CreateDirectory("Logs");
            File.WriteAllLines("Logs/map9-chart-handoff-trips.txt", trips);
            Debug.Log("[Catchline] MAP9 CHART HANDOFF TRIPS PASSED: three affected grounds and home");
            BuildNative();
        }
        public static void BuildNative()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var g = new GameObject("MAP9 native acceptance TEST").AddComponent<VoyageGame>();
            g.SessionOnly = true;
            const string fixture = "Assets/Map9Acceptance.unity";
            EditorSceneManager.SaveScene(scene, fixture);
            Directory.CreateDirectory("Builds/Map9Capture"); Directory.CreateDirectory("Logs");
            var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes = new[] { fixture }, locationPathName = "Builds/Map9Capture/Catchline.exe",
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None
            });
            Check(result.summary.result == BuildResult.Succeeded, "native TEST build " + result.summary.result);
            File.WriteAllText("Logs/map9-build.txt", DateTime.UtcNow.ToString("O") + " " + result.summary.result);
            Debug.Log("[Catchline] MAP9 TEST BUILD PASSED. Snapshot written to Builds/Map9Capture/Catchline.exe");
        }
    }
}


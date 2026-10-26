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
    // MAP11 acceptance fixture. Run only through docs/tools/check.ps1 in Catchline-sim.
    public static class KelpForestMapChecks
    {
        [Serializable] sealed class Receipt
        {
            public string map = "GullKelpForest", utc;
            public int maps, hullRoutes, lanes;
            public bool assets, chartPurchase, anchors, groundPoolsReady;
            public string[] trips, groundIds, limits;
        }
        static void Check(bool ok, string label)
        { if (!ok) throw new Exception("[Catchline] MAP11 check failed: " + label); }
        static void ScratchOnly()
        {
            Check(Application.dataPath.Replace('\\', '/').EndsWith("Catchline-sim/Assets", StringComparison.OrdinalIgnoreCase), "scratch project only");
        }

        public static void Run()
        { RunChecks(true); }
        static void RunChecks(bool allMaps)
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            Check(SeaNav.Maps.Length == 11 && GameData.Spots.Length == 11 && SeaNav.Maps[10] == "GullKelpForest", "eleven maps/spots with stable order");
            var spot = GameData.Spots[10];
            Check(spot.Name == "Kelp forest" && spot.RowSeconds == 28f && spot.BiteWait == 1.4f && spot.ChartCost == 36000, "spot data");
            var state = new GameState(6501); state.Coins = 36000;
            Check(!state.BuyChart(10) && state.Coins == 36000, "Outer coast chart needs a tier 4 boat");
            state.Hull = 3; state.Coins = 35999;
            Check(!state.Known(10) && !state.BuyChart(10) && state.Coins == 35999, "unaffordable chart stays locked");
            state.Coins = 36000;
            Check(state.BuyChart(10) && state.Known(10) && state.Coins == 0, "36000-coin chart purchase");
            var nav = SeaNav.Load("GullKelpForest", GameData.Hulls[4]);
            Check(nav != null && !nav.Interim && nav.ModelId == "GullKelpForestSeaV2" && nav.Grounds.Count == 3, "real model/navigation lookup");
            string[] ids = { "kelp-edge", "sand-clearing", "post-line" };
            Check(nav.Grounds.Select(g => g.Id).SequenceEqual(ids), "ground IDs/order");
            LifeAndAnchors();

            if (allMaps) MapNavChecks.Run();
            else FinalMapRoutes();
            ShelfSceneAssets();
            string baseline = HarbourTripChecks.Run(); // all eleven SeaLanes + five harbour hulls
            var trips = new List<string> { baseline };
            foreach (string id in ids) trips.Add(NewGroundTrip(id));
            bool pools = Grounds.ForMap(10).Select(g => g.Id).SequenceEqual(ids);
            Check(pools, "three ground pools");
            var expectedPools = new[] {
                new[] { (Species.RedMullet,40f),(Species.Pollock,30f),(Species.SeaBass,20f),(Species.Crab,2f) },
                new[] { (Species.Plaice,40f),(Species.Whiting,30f),(Species.RedMullet,20f),(Species.Turbot,3f) },
                new[] { (Species.Mackerel,45f),(Species.Herring,30f),(Species.Conger,15f),(Species.Turbot,2f) } };
            for (int i=0;i<3;i++) Check(Grounds.ForMap(10)[i].Day.SequenceEqual(expectedPools[i]), ids[i]+" exact species weights");
            var receipt = new Receipt {
                utc = DateTime.UtcNow.ToString("O"), maps = 11, hullRoutes = allMaps ? 660 : 60, lanes = 33,
                assets = true, chartPurchase = true, anchors = true, groundPoolsReady = pools,
                trips = trips.ToArray(), groundIds = ids,
                limits = new[] { "Scratch simulation and asset checks; native visuals are separate.", "Delivered static OtterRaft model with bob; individual otter clips not requested. Foreground post broad-circle exception accepted by Claude 2, 2026-10-26 08:45." }
            };
            Directory.CreateDirectory("Logs");
            string output = allMaps ? "Logs/map11-checks.json" : "Logs/map11-final-checks.json";
            File.WriteAllText(output, JsonUtility.ToJson(receipt, true));
            Debug.Log("[Catchline] MAP11 CHECKS PASSED: eleven maps, " + receipt.hullRoutes + " hull routes, 33 lanes, three new-ground/home trips. Snapshot written to " + output);
        }

        static void LifeAndAnchors()
        {
            var nav = SeaNav.Load("GullKelpForest", GameData.Hulls[4]);
            var model = UnityEngine.Object.Instantiate(ArtLibrary.Get().M(nav.ModelId));
            try
            {
                model.transform.SetPositionAndRotation(new Vector3(0, -.32f, 0), Quaternion.identity);
                model.transform.localScale = Vector3.one;
                string[] anchorNames = { "KelpSway_1", "KelpSway_2", "KelpSway_3", "KelpSway_4", "OtterRaft_1", "PostGulls_1", "PostGulls_2" };
                var expected = new[] { new Vector3(-90.8164895f,-0.3200000f,-27.5895740f), new Vector3(-82.6249691f,-0.3200000f,-33.3253383f), new Vector3(3.1941830f,-0.3200000f,29.1010852f), new Vector3(78.3643584f,-0.3200000f,-24.0159975f), new Vector3(-92.0000000f,-0.3200000f,-22.0000000f), new Vector3(79.6013290f,1.2800000f,-24.5159013f), new Vector3(87.3013582f,1.2800000f,-29.9075198f) };
                for (int i = 0; i < anchorNames.Length; i++)
                {
                    var anchor = model.GetComponentsInChildren<Transform>(true).Single(t => t.name == anchorNames[i]);
                    Check(Vector3.Distance(anchor.position, expected[i]) < .02f, "life anchor world transform " + anchor.name + ": " + anchor.position);
                    Check(anchor.GetComponent<Renderer>() == null, "life anchor remains an empty");
                }
                var owner = new GameObject("MAP11 life fixture").AddComponent<VoyageGame>();
                var water = new Material(ArtLibrary.Get().WaterShader);
                try
                {
                    typeof(VoyageGame).GetField("seaMat", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(owner, water);
                    typeof(VoyageGame).GetMethod("DressSkerries", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(owner, new object[] { model, ArtLibrary.Get() });
                    var sways = model.GetComponentsInChildren<KelpRootSway>();
                    Check(sways.Length == 4, "four independently rooted kelp clusters sway");
                    foreach (var sway in sways)
                    {
                        Check(sway.Period >= 4 && sway.Period <= 7, "slow 4-7 second sway");
                        Check(sway.GetComponentsInChildren<MeshFilter>().Length == 1, "exactly one localized authored cluster per sway");
                        Check(Mathf.Abs(Quaternion.Dot(sway.Pose(0), sway.Pose(sway.Period))) > .999999f, "continuous periodic sway");
                        Check(Quaternion.Angle(sway.Pose(0), sway.Pose(sway.Period * .25f)) > .1f, "sway actually moves");
                        for (int n = 0; n < 24; n++) Check(Quaternion.Angle(Quaternion.identity, sway.Pose(n * sway.Period / 24)) < 2, "gentle sway below two degrees");
                    }
                    var raft = ArtLibrary.Find(model, "Otter raft");
                    Check(raft != null && raft.GetComponent<Floater>() != null, "delivered otter raft with gentle bob");
                    Check(raft.GetComponentsInChildren<MeshFilter>().Length == 4, "raft kelp, two adults and pup imported");
                    Check(raft.GetComponentsInChildren<Renderer>().All(r => r.sharedMaterials.All(m => m != null && m.shader.isSupported && m.GetFloat("_Cull") == 0)), "raft palette bound to supported two-sided materials");
                    Check(model.GetComponentsInChildren<Gull>().Length == 4, "four existing post gulls");
                    Check(model.GetComponentsInChildren<KelpBayOptics>().Length == 1, "one map-local optics owner");
                    var transmission = water.GetVector("_AbsorptionColor");
                    Check(transmission.x > transmission.z && transmission.y > transmission.z && transmission.x < .9f && transmission.y < .9f,
                        "MAP11 warm shallow transmission with depth absorption retained; native sand read reviewed separately");
                    Debug.Log("[Catchline] MAP11 LIFE CHECKS PASSED: four localized 4-7s sways, bounded periodic motion, delivered otter raft, four post gulls, map-local optics");
                }
                finally { UnityEngine.Object.DestroyImmediate(owner.gameObject); UnityEngine.Object.DestroyImmediate(water); }
            }
            finally { UnityEngine.Object.DestroyImmediate(model); }

        }

        public static void LifeAndBuild()
        { ScratchOnly(); ArtImport.BuildLibrary(); LifeAndAnchors(); BuildNative(); }

        // Retain the accepted MAP9 open shelf exception; do not add horizon islands.
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
                    Check(model.GetComponentsInChildren<Transform>(true).Count(t => t.name == "WreckGulls_1") == 1, "MAP11 single sea-mount crown anchor");
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
            Debug.Log("[Catchline] MAP11 SEA SCENE ASSETS PASSED: eleven real maps, older horizon models, open shelf, ocean extension and border fog");
        }

        // COASTS-2 changed economy/chart after the full eleven-map run. Recheck all 60
        // affected directed routes, plus every sea lane and the three live trips.
        static void FinalMapRoutes()
        {
            int routes = 0;
            foreach (var hull in GameData.Hulls)
            {
                var nav = SeaNav.Load("GullKelpForest", hull);
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
            Debug.Log("[Catchline] MAP11 FINAL TERRAIN ROUTES PASSED: 60 directed hull routes");
        }

        static string NewGroundTrip(string id)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("MAP11 session-only trip check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            g.State.Hull = 4; g.State.Coins = 40000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { false });
            g.Tick(.05f); Check(g.State.BuyChart(10), "new chart for trip"); g.SelectedSpot = 10;
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
                string result = "GullKelpForest/" + id + " tier5 out/anchor/bait-cast/home PASS";
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
            var g = new GameObject("MAP11 native acceptance TEST").AddComponent<VoyageGame>();
            g.SessionOnly = true;
            const string fixture = "Assets/Map11Acceptance.unity";
            EditorSceneManager.SaveScene(scene, fixture);
            Directory.CreateDirectory("Builds/Map11Capture"); Directory.CreateDirectory("Logs");
            var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes = new[] { fixture }, locationPathName = "Builds/Map11Capture/Catchline.exe",
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None
            });
            Check(result.summary.result == BuildResult.Succeeded, "native TEST build " + result.summary.result);
            File.WriteAllText("Logs/map11-build.txt", DateTime.UtcNow.ToString("O") + " " + result.summary.result);
            Debug.Log("[Catchline] MAP11 TEST BUILD PASSED. Snapshot written to Builds/Map11Capture/Catchline.exe");
        }
    }
}


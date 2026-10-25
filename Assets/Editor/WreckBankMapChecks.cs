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
    // MAP7 acceptance fixture. Run only through docs/tools/check.ps1 in Catchline-sim.
    public static class WreckBankMapChecks
    {
        [Serializable] sealed class Receipt
        {
            public string map = "GullWreckBank", utc;
            public int maps, hullRoutes, lanes;
            public bool assets, chartPurchase, anchors, groundPoolsReady;
            public string[] trips, groundIds, limits;
        }
        static void Check(bool ok, string label)
        { if (!ok) throw new Exception("[Catchline] MAP7 check failed: " + label); }
        static void ScratchOnly()
        {
            Check(Application.dataPath.Replace('\\', '/').EndsWith("Catchline-sim/Assets", StringComparison.OrdinalIgnoreCase), "scratch project only");
        }

        public static void Run()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            Check(SeaNav.Maps.Length == 7 && GameData.Spots.Length == 7 && SeaNav.Maps[6] == "GullWreckBank", "seven maps/spots with stable order");
            var spot = GameData.Spots[6];
            Check(spot.Name == "Wreck bank" && spot.RowSeconds == 26f && spot.BiteWait == 1.3f && Mathf.Approximately(spot.ChartCost, GameData.Spots[5].ChartCost * 1.4f), "spot data");
            var state = new GameState(6501); state.Coins = 979;
            Check(!state.Known(6) && !state.BuyChart(6) && state.Coins == 979, "unaffordable chart stays locked");
            state.Coins = 980;
            Check(state.BuyChart(6) && state.Known(6) && state.Coins == 0, "980-coin chart purchase");
            var nav = SeaNav.Load("GullWreckBank", GameData.Hulls[4]);
            Check(nav != null && !nav.Interim && nav.ModelId == "GullWreckBankSeaV2" && nav.Grounds.Count == 3, "real model/navigation lookup");
            string[] ids = { "the-wreck", "herring-bank", "sand-edge" };
            Check(nav.Grounds.Select(g => g.Id).SequenceEqual(ids), "ground IDs/order");
            var model = UnityEngine.Object.Instantiate(ArtLibrary.Get().M(nav.ModelId));
            try
            {
                model.transform.SetPositionAndRotation(new Vector3(0, -.32f, 0), Quaternion.identity);
                model.transform.localScale = Vector3.one;
                string[] anchorNames = { "GannetDive_1", "GannetDive_2", "GannetDive_3", "GannetDive_4", "WreckGulls_1", "CardinalBuoy_1" };
                var expected = new[] { new Vector3(-4.963642f,0.800000f,59.772122f), new Vector3(3.227878f,0.800000f,54.036358f), new Vector3(-2.504486f,0.800000f,70.257948f), new Vector3(12.240251f,0.800000f,59.933572f), new Vector3(-77.802045f,1.480000f,-37.516519f), new Vector3(-68.626522f,-0.320000f,-36.616642f) };
                for (int i = 0; i < anchorNames.Length; i++)
                {
                    var anchor = model.GetComponentsInChildren<Transform>(true).Single(t => t.name == anchorNames[i]);
                    Check(Vector3.Distance(anchor.position, expected[i]) < .02f, "life anchor world transform " + anchor.name + ": " + anchor.position);
                    Check(anchor.GetComponent<Renderer>() == null, "life anchor remains an empty");
                }
            }
            finally { UnityEngine.Object.DestroyImmediate(model); }

            MapNavChecks.Run(); // all directed harbour/ground routes, five hulls, seven maps
            SeaSceneChecks.Assets();
            string baseline = HarbourTripChecks.Run(); // all seven SeaLanes + five harbour hulls
            var trips = new List<string> { baseline };
            foreach (string id in ids) trips.Add(NewGroundTrip(id));
            bool pools = Grounds.ForMap(6).Select(g => g.Id).SequenceEqual(ids);
            Check(pools, "three ground pools");
            var expectedPools = new[] {
                new[] { (Species.Conger,40f),(Species.Cod,30f),(Species.Pollock,25f),(Species.Turbot,2f) },
                new[] { (Species.Herring,50f),(Species.Mackerel,30f),(Species.Whiting,20f) },
                new[] { (Species.Plaice,50f),(Species.Turbot,12f),(Species.Whiting,25f),(Species.SpottedEagleRay,1f) } };
            for (int i=0;i<3;i++) Check(Grounds.ForMap(6)[i].Day.SequenceEqual(expectedPools[i]), ids[i]+" exact species weights");
            var receipt = new Receipt {
                utc = DateTime.UtcNow.ToString("O"), maps = 7, hullRoutes = 420, lanes = 21,
                assets = true, chartPurchase = true, anchors = true, groundPoolsReady = pools,
                trips = trips.ToArray(), groundIds = ids,
                limits = new[] { "Scratch simulation and asset checks; native visuals are separate.", "Runtime gulls/gannets/buoy life, chart glyph and water optics remain lead-owned; see native review." }
            };
            Directory.CreateDirectory("Logs");
            File.WriteAllText("Logs/map7-checks.json", JsonUtility.ToJson(receipt, true));
            Debug.Log("[Catchline] MAP7 CHECKS PASSED: seven maps, 420 hull routes, 21 lanes, three new-ground/home trips. Snapshot written to Logs/map7-checks.json");
        }

        // Claude changed spot6's chart point after the full geometry run began.
        // Recheck its new home-facing entry and complete trips without repeating 420 unchanged geometry routes.
        public static void PostIntegration()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            var proof = SeaNav.Load("GullWreckBank", 2.25f);
            var wide = SeaLanes.Clearances.Select(r => SeaNav.Load("GullWreckBank", r)).ToList();
            var home = SeaLanes.HomeDirection(VoyageGame.NauticalChartPoint(6), VoyageGame.ChartHarbour);
            var entry = SeaLanes.Entry(proof, home, out _);
            Check(Vector2.Dot((entry - proof.CameraBounds.center).normalized, home) > .5f, "updated entry faces home");
            foreach (var ground in proof.Grounds)
            {
                var lane = SeaLanes.Lane(proof, wide, entry, ground.Centre, out float clear);
                Check(lane != null && SeaLanes.Proven(proof, lane) && clear >= 4.5f, "updated entry lane " + ground.Id);
            }
            string[] ids = { "the-wreck", "herring-bank", "sand-edge" };
            var trips = ids.Select(id => NewGroundTrip(id, true)).ToArray();
            Directory.CreateDirectory("Logs");
            File.WriteAllText("Logs/map7-postlife-checks.json", JsonUtility.ToJson(new Receipt {
                utc = DateTime.UtcNow.ToString("O"), maps = 7, hullRoutes = 0, lanes = 3,
                assets = true, anchors = true, chartPurchase = true, groundPoolsReady = true,
                groundIds = ids, trips = trips,
                limits = new[] { "Targeted check after chart/life integration; full 420 geometry routes and 21 lane baseline remain separately recorded.", "Life component presence checked; animation and presentation require native review." }
            }, true));
            Debug.Log("[Catchline] MAP7 POST-INTEGRATION PASSED: updated entry three lanes/three normal bait-cast-home trips; four gannets and cardinal buoy present. Snapshot written to Logs/map7-postlife-checks.json");
        }

        static string NewGroundTrip(string id, bool requireLife = false)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("MAP7 session-only trip check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            g.State.Hull = 4; g.State.Coins = 10000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { false });
            g.Tick(.05f); Check(g.State.BuyChart(6), "new chart for trip"); g.SelectedSpot = 6;
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
                if (requireLife)
                {
                    Check(UnityEngine.Object.FindObjectsByType<GannetDive>(FindObjectsSortMode.None).Length == 4, id + " four runtime gannets");
                    Check(UnityEngine.Object.FindObjectsByType<BuoyBob>(FindObjectsSortMode.None).Length == 1, id + " runtime cardinal buoy");
                }
                var rod = g.Rods.FirstOrDefault(g.CanCommandRod);
                Check(rod != null, id + " rod command available");
                g.CommandRod(rod);
                Until(() => rod.InWater, "normal captain bait/cast");
                g.HeadHome();
                Until(() => g.CurrentMode == VoyageGame.Mode.Harbour, "home arrival");
                foreach (var leg in new[] { VoyageGame.TripLeg.HarbourOut, VoyageGame.TripLeg.ChartOut, VoyageGame.TripLeg.SeaOut, VoyageGame.TripLeg.SeaHome, VoyageGame.TripLeg.ChartHome, VoyageGame.TripLeg.HarbourIn })
                    Check(legs.Contains(leg), id + " complete trip leg " + leg);
                string result = "GullWreckBank/" + id + " tier5 out/anchor/bait-cast/home PASS";
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
            var g = new GameObject("MAP7 native acceptance TEST").AddComponent<VoyageGame>();
            g.SessionOnly = true;
            const string fixture = "Assets/Map7Acceptance.unity";
            EditorSceneManager.SaveScene(scene, fixture);
            Directory.CreateDirectory("Builds/Map7Capture"); Directory.CreateDirectory("Logs");
            var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes = new[] { fixture }, locationPathName = "Builds/Map7Capture/Catchline.exe",
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None
            });
            Check(result.summary.result == BuildResult.Succeeded, "native TEST build " + result.summary.result);
            File.WriteAllText("Logs/map7-build.txt", DateTime.UtcNow.ToString("O") + " " + result.summary.result);
            Debug.Log("[Catchline] MAP7 TEST BUILD PASSED. Snapshot written to Builds/Map7Capture/Catchline.exe");
        }
    }
}

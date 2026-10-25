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
    // MAP6 acceptance fixture. Run only through docs/tools/check.ps1 in Catchline-sim.
    public static class SkerriesMapChecks
    {
        [Serializable] sealed class Receipt
        {
            public string map = "GullSkerries", utc;
            public int maps, hullRoutes, lanes;
            public bool assets, chartPurchase, anchors, groundPoolsReady;
            public string[] trips, groundIds, limits;
        }
        static void Check(bool ok, string label)
        { if (!ok) throw new Exception("[Catchline] MAP6 check failed: " + label); }
        static void ScratchOnly()
        {
            Check(Application.dataPath.Replace('\\', '/').EndsWith("Catchline-sim/Assets", StringComparison.OrdinalIgnoreCase), "scratch project only");
        }

        public static void Run()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            Check(SeaNav.Maps.Length == 6 && GameData.Spots.Length == 6 && SeaNav.Maps[5] == "GullSkerries", "six maps/spots with stable order");
            var spot = GameData.Spots[5];
            Check(spot.Name == "Seal skerries" && spot.RowSeconds == 24f && spot.BiteWait == 1.35f && Mathf.Approximately(spot.ChartCost, GameData.Spots[4].ChartCost * 1.4f), "spot data");
            var state = new GameState(6501); state.Coins = 699;
            Check(!state.Known(5) && !state.BuyChart(5) && state.Coins == 699, "unaffordable chart stays locked");
            state.Coins = 700;
            Check(state.BuyChart(5) && state.Known(5) && state.Coins == 0, "700-coin chart purchase");
            var nav = SeaNav.Load("GullSkerries", GameData.Hulls[4]);
            Check(nav != null && !nav.Interim && nav.ModelId == "GullSkerriesSeaV2" && nav.Grounds.Count == 3, "real model/navigation lookup");
            string[] ids = { "seal-rocks", "kelp-gully", "outer-reef" };
            Check(nav.Grounds.Select(g => g.Id).SequenceEqual(ids), "ground IDs/order");
            var model = UnityEngine.Object.Instantiate(ArtLibrary.Get().M(nav.ModelId));
            try
            {
                model.transform.SetPositionAndRotation(new Vector3(0, -.32f, 0), Quaternion.identity);
                model.transform.localScale = Vector3.one;
                var expected = new[] { new Vector3(-62, 1.88f, 13), new Vector3(-13, 2.58f, 8) };
                for (int i = 0; i < 2; i++)
                {
                    var anchor = model.GetComponentsInChildren<Transform>(true).Single(t => t.name == "SealColony_" + (i + 1));
                    Check(Vector3.Distance(anchor.position, expected[i]) < .02f, "seal anchor world transform " + (i + 1) + ": " + anchor.position);
                    Check(anchor.GetComponent<Renderer>() == null, "seal anchor remains an empty");
                }
            }
            finally { UnityEngine.Object.DestroyImmediate(model); }

            MapNavChecks.Run(); // all directed harbour/ground routes, five hulls, six maps
            SeaSceneChecks.Assets();
            string baseline = HarbourTripChecks.Run(); // all six SeaLanes + five harbour hulls
            var trips = new List<string> { baseline };
            foreach (string id in ids) trips.Add(NewGroundTrip(id));
            bool pools = Grounds.ForMap(5).Select(g => g.Id).SequenceEqual(ids);
            if (!pools) Debug.LogWarning("[Catchline] MAP6 EXTERNAL PENDING: Claude-owned Grounds.ByMap row missing; trips use spot fallback fish pool.");
            var receipt = new Receipt {
                utc = DateTime.UtcNow.ToString("O"), maps = 6, hullRoutes = 360, lanes = 18,
                assets = true, chartPurchase = true, anchors = true, groundPoolsReady = pools,
                trips = trips.ToArray(), groundIds = ids,
                limits = new[] { "Scratch simulation and asset checks; native visuals are separate.", "Species-specific ground pools and seal/reef life integration remain lead-owned if marked pending." }
            };
            Directory.CreateDirectory("Logs");
            File.WriteAllText("Logs/map6-checks.json", JsonUtility.ToJson(receipt, true));
            Debug.Log("[Catchline] MAP6 CHECKS PASSED: six maps, 360 hull routes, 18 lanes, three new-ground/home trips. Snapshot written to Logs/map6-checks.json");
        }

        static string NewGroundTrip(string id)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("MAP6 session-only trip check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            g.State.Hull = 4; g.State.Coins = 10000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { false });
            g.Tick(.05f); Check(g.State.BuyChart(5), "new chart for trip"); g.SelectedSpot = 5;
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
                g.HeadHome();
                Until(() => g.CurrentMode == VoyageGame.Mode.Harbour, "home arrival");
                foreach (var leg in new[] { VoyageGame.TripLeg.HarbourOut, VoyageGame.TripLeg.ChartOut, VoyageGame.TripLeg.SeaOut, VoyageGame.TripLeg.SeaHome, VoyageGame.TripLeg.ChartHome, VoyageGame.TripLeg.HarbourIn })
                    Check(legs.Contains(leg), id + " complete trip leg " + leg);
                string result = "GullSkerries/" + id + " tier5 out/anchor/home PASS";
                Debug.Log("[Catchline] " + result); return result;
            }
            finally { UnityEngine.Object.DestroyImmediate(g.gameObject); }
        }

        public static void RunAndBuild()
        {
            Run(); BuildNative();
        }
        // A chart-point-only correction changes the home-facing entry, not static
        // map geometry. Recheck the affected lanes/trips without repeating 360
        // unchanged static routes and the five unchanged harbour baselines.
        public static void RecheckChartAndBuild()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            var nav = SeaNav.Load("GullSkerries", 2.25f);
            var wide = SeaLanes.Clearances.Select(r => SeaNav.Load("GullSkerries", r)).ToList();
            var home = SeaLanes.HomeDirection(VoyageGame.NauticalChartPoint(5), VoyageGame.ChartHarbour);
            var entry = SeaLanes.Entry(nav, home, out _);
            Check(Vector2.Dot((entry - nav.CameraBounds.center).normalized, home) > .5f, "corrected chart entry faces home");
            var results = new List<string> { DateTime.UtcNow.ToString("O"), "chart point=" + VoyageGame.NauticalChartPoint(5) };
            foreach (var ground in nav.Grounds)
            {
                var lane = SeaLanes.Lane(nav, wide, entry, ground.Centre, out float clearance);
                Check(lane != null && SeaLanes.Proven(nav, lane) && clearance >= 4.5f, "corrected chart lane " + ground.Id);
                results.Add(ground.Id + " lane clearance=" + clearance.ToString("F2") + "m");
            }
            foreach (var ground in nav.Grounds) results.Add(NewGroundTrip(ground.Id));
            Directory.CreateDirectory("Logs");
            File.WriteAllLines("Logs/map6-chart-recheck.txt", results);
            Debug.Log("[Catchline] MAP6 CHART ENTRY RECHECK PASSED. Snapshot written to Logs/map6-chart-recheck.txt");
            BuildNative();
        }
        public static void BuildNative()
        {
            ScratchOnly(); ArtImport.BuildLibrary();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene);
            var g = new GameObject("MAP6 native acceptance TEST").AddComponent<VoyageGame>();
            g.SessionOnly = true;
            const string fixture = "Assets/Map6Acceptance.unity";
            EditorSceneManager.SaveScene(scene, fixture);
            Directory.CreateDirectory("Builds/Map6Capture"); Directory.CreateDirectory("Logs");
            var result = BuildPipeline.BuildPlayer(new BuildPlayerOptions {
                scenes = new[] { fixture }, locationPathName = "Builds/Map6Capture/Catchline.exe",
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None
            });
            Check(result.summary.result == BuildResult.Succeeded, "native TEST build " + result.summary.result);
            File.WriteAllText("Logs/map6-build.txt", DateTime.UtcNow.ToString("O") + " " + result.summary.result);
            Debug.Log("[Catchline] MAP6 TEST BUILD PASSED. Snapshot written to Builds/Map6Capture/Catchline.exe");
        }
    }
}

using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class FuelDepartureChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string reason) { if (!ok) throw new Exception("Fuel/departure: " + reason); }
        static void Field(VoyageGame g, string n, object v) => typeof(VoyageGame).GetField(n, H).SetValue(g, v);
        static object Call(VoyageGame g, string n, params object[] args) => typeof(VoyageGame).GetMethod(n, H).Invoke(g, args);
        static VoyageGame Fixture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Fuel021 isolated fixture").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build(); g.StartNetBoatTrial(); return g;
        }
        public static void Run()
        {
            Directory.CreateDirectory("Logs/fuel021");
            var s = new GameState(12) { Hull = 2, Fuel = 0, Coins = 10 };
            Check(s.FuelCapacity == 10 && s.FuelFillCost == 10 && s.BuyFuel() && s.Fuel == 10 && s.Coins == 0, "ten minutes at former1coin/min provision cost");
            Check(!s.BuyFuel(), "full tank never charges");
            s.Owned.Add(UpgradeId.LunchTin); s.Coins = 10;
            Check(s.FuelCapacity == 20 && s.BuyFuel() && s.Fuel == 20 && s.Coins == 0, "owned old tin doubles tank without refilling for free");
            s.Fuel = 12.345f; s.Save("Logs/fuel021/save.json"); var loaded = GameState.Load("Logs/fuel021/save.json");
            Check(loaded.Fuel == s.Fuel && loaded.FuelCapacity == 20, "fractional fuel and tank persist exactly");
            s.Fuel = 0; s.Save("Logs/fuel021/save.json"); Check(GameState.Load("Logs/fuel021/save.json").Fuel == 0, "empty saved fuel stays empty");
            s.Fuel = 19; s.Coins = 0; Check(!s.BuyFuel() && s.Fuel == 19, "unaffordable fill atomic");
            var g = Fixture(); g.State.FoodMinutes = 0; Check(WorkSpeed.Rate(g.Captain) == 1f, "empty food standard crew pace");
            g.State.FoodMinutes = 100; Check(WorkSpeed.Rate(g.Captain) == 1f, "legacy food grants no speed bonus");
            g.State.Fuel = 10; g.Tick(60); Check(Mathf.Abs(g.State.Fuel - 9) < .003f, "one minute elapsed burns one minute independent of crew");
            g.State.Fuel = 1.001f; g.Tick(.2f); Check(g.CurrentMode == VoyageGame.Mode.SailingHome, "base tank automatically returns at10percent");
            for (int i = 0; i < 1000 && g.CurrentMode != VoyageGame.Mode.Harbour; i++) g.Tick(.05f);
            Check(g.CurrentMode == VoyageGame.Mode.Harbour && g.State.Fuel > 0 && g.State.Fuel < 1, "reserve completes home leg and dock never refills");
            Check(g.SailBlocker() != null, "reserve cannot relaunch");
            g.State.UnsoldCatch.Clear(); g.RequestDeparture(); g.PrepareInterface(1440, 900);
            Check(!g.InvokeInterface("depart/go") && g.CurrentMode == VoyageGame.Mode.Harbour, "go disabled until fuel restored");
            int coins = g.State.Coins, cost = g.State.FuelFillCost;
            Check(g.InvokeInterface("depart/refuel") && g.State.Coins == coins - cost && g.State.Fuel == 10, "manifest refill exact inventory and cost");
            g.PrepareInterface(1440, 900); int bait = g.State.Bait;
            Check(g.InvokeInterface("depart/worms/buy") && g.State.Bait == bait + GameData.BaitPackSize, "quick bait purchase real inventory");
            g.PrepareInterface(844, 390);
            Check(!g.InvokeInterface("supplies/deep-net/buy") && !g.InvokeInterface("port/sail"), "manifest excludes real shop/stale departure controls");
            Check(g.InvokeInterface("depart/go") && g.CurrentMode == VoyageGame.Mode.SailingOut, "explicit go launches once");
            g.State.Owned.Add(UpgradeId.LunchTin); g.Tick(30); g.State.Fuel = 2.001f; g.Tick(.2f);
            Check(g.CurrentMode == VoyageGame.Mode.SailingHome, "upgraded return threshold is10percent/two minutes");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] FUEL DEPARTURE CHECKS PASSED");
        }
        static void Capture()
        {
            var g = Fixture(); g.Showcase(-1, 0); g.State.DeepNetUses.AddRange(new[] { 2, 3 }); g.State.SelectedNet = NetKind.Deep;
            g.State.Fuel = 4.6f; g.State.Squid = 18; g.RequestDeparture();
            var shot = typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic);
            void Shot(string n, int w, int h, float scale = 1) => shot.Invoke(null, new object[] { g, "../fuel021/" + n, w, h, scale });
            Shot("departure-desktop", 1440, 900); Shot("departure-phone", 844, 390); Shot("departure-phone-larger", 844, 390, 1.15f);
            g.State.Fuel = .8f; g.State.Coins = 0; Shot("departure-shortfall", 1440, 900);
            Field(g, "departureReady", false); g.StartNetBoatTrial(); Shot("fishing-fuel", 1440, 900);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
        public static void ValidateAndBuildPreview()
        {
            ArtImport.BuildLibrary(); Run(); Capture(); WeightNetChecks.Regression(); BuildPreview();
            Debug.Log("[Catchline] FUEL021 COMBINED UPDATE VERIFIED");
        }
        public static void ReviewAndBuildPreview() { ArtImport.BuildLibrary(); Run(); WeightNetChecks.Review(); Capture(); BuildPreview(); }
        public static void BuildPreview()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Catchline combined Fuel021 preview").AddComponent<VoyageGame>(); g.SessionOnly = true;
            const string scene = "Assets/Scenes/Fuel021Preview.unity";
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scene);
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { scene }, locationPathName = Path.GetFullPath("Builds/Fuel021/Catchline.exe"), target = BuildTarget.StandaloneWindows64 });
            Check(report.summary.result == BuildResult.Succeeded, "combined Windows build");
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: " + Path.GetFullPath("Builds/Fuel021/Catchline.exe"));
        }
    }
}

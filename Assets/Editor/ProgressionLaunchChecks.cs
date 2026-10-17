using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Collections.Generic;
using Catchline.Game;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class ProgressionLaunchChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("NET023: " + why); }
        static void Field(VoyageGame g, string n, object v) => typeof(VoyageGame).GetField(n, H).SetValue(g, v);
        static void State(VoyageGame g, GameState s) => typeof(VoyageGame).GetProperty("State").GetSetMethod(true).Invoke(g, new object[] { s });
        static VoyageGame Fixture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("NET023 isolated fixture").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build(); g.StartNetBoatTrial(); return g;
        }
        public static void Run()
        {
            Directory.CreateDirectory("Logs/crew026");
            var s = new GameState(9) { Hull = 2, Coins = 4999 };
            Check(s.CoolerCapacity == 100 && s.NetCapacityKg == 10, "base tier3 hold100/net10");
            Check(!s.TryBuy(UpgradeId.NetSystem) && s.Coins == 4999 && s.NetCapacityKg == 10, "net upgrade shortfall atomic");
            s.Coins = 5000; Check(s.TryBuy(UpgradeId.NetSystem) && s.Coins == 0 && s.NetCapacityKg == 15, "exact5000 upgrade changes both net capacities");
            Check(!s.TryBuy(UpgradeId.NetSystem), "upgrade cannot charge twice");
            s.Owned.Add(UpgradeId.BigCooler); s.Save("Logs/crew026/state.json"); var loaded = GameState.Load("Logs/crew026/state.json");
            Check(loaded.CoolerCapacity == 150 && loaded.NetCapacityKg == 15 && loaded.Coins == 0, "owned upgrades persist without repurchase");
            Check(s.UpgradeCost(UpgradeId.BigCooler) == 3000 && s.UpgradeCost(UpgradeId.RodCarbon) == 3500 && s.UpgradeCost(UpgradeId.LunchTin) == 1500, "tier3 authoritative upgrade prices");
            var early = new GameState(9) { Coins = 10000 }; Check(early.UpgradeCost(UpgradeId.BigCooler) == 60 && !early.TryBuy(UpgradeId.NetSystem), "starter economy preserved and net system unavailable early");
            var refit = new GameState(2) { Hull = 1, Coins = 3999 };
            Check(!refit.RefitCompact() && refit.Coins == 3999, "real tier3 refit shortfall atomic");
            refit.Coins = 4000; refit.Owned.Add(UpgradeId.BigCooler); refit.UnsoldCatch.Add(new CaughtFish { Kg = 3 });
            Check(refit.RefitCompact() && refit.Coins == 0 && refit.Hull == 2 && refit.CoolerCapacity == 150 && refit.UnsoldCatch.Count == 1 && refit.Fuel == refit.FuelCapacity, "real progression to tier3 preserves owned upgrades/cargo");
            var a = new GameState(1) { Hull = 2 }; var b = new GameState(1) { Hull = 2 };
            for (int i = 0; i < 100; i++) a.OnCatch(0, .1f); b.OnCatch(0, 10);
            Check(Mathf.Abs(a.Richness[0] - b.Richness[0]) < .0001f, "equal mass depletes equally regardless fish count");
            var g = Fixture();
            var report = new System.Text.StringBuilder("ground,capacity,method,meanFish,meanKg,meanFreshQuote\n");
            foreach (int spot in Enumerable.Range(0, GameData.Spots.Length))
            foreach (bool upgraded in new[] { false, true })
            {
                double[] values = new double[2], counts = new double[2];
                foreach (bool deep in new[] { false, true })
                {
                    double kg = 0, val = 0, count = 0;
                    for (int seed = 0; seed < 200; seed++)
                    {
                        var run = new GameState(seed) { Hull = 2, SelectedNet = deep ? NetKind.Deep : NetKind.Shallow };
                        if (upgraded) run.Owned.Add(UpgradeId.NetSystem); State(g, run);
                        typeof(VoyageGame).GetProperty("ActiveSpot").GetSetMethod(true).Invoke(g, new object[] { spot });
                        typeof(VoyageGame).GetMethod("RollCompactCatch", H).Invoke(g, null);
                        var batch = (List<(Species species, float kg)>)typeof(VoyageGame).GetField("netFish", H).GetValue(g);
                        Check(g.NetCatchKg <= run.NetCapacityKg + .0001f && g.NetCatchKg >= run.NetCapacityKg * .8f, "hard shared kg budget on every ground");
                        Check(batch.All(f => GameData.Spots[spot].Table.Any(e => e.species == f.species) && f.kg >= GameData.Get(f.species).MinKg && f.kg <= GameData.Get(f.species).MaxKg), "only honest local specimens");
                        var cargo = batch.Select(f => new CaughtFish { Species = f.species, Kg = f.kg }).ToList();
                        int quote = run.QuoteSale(cargo, 0).Coins; int sale = run.Sell(cargo, 0).Coins; Check(quote == sale, "hull-specific quote equals actual payout");
                        count += batch.Count; kg += g.NetCatchKg; val += quote;
                        if (spot == 0 && !deep) Check(batch.Count > 5, "school net genuinely exceeds old five-fish impression");
                    }
                    int index = deep ? 1 : 0; values[index] = val / 200; counts[index] = count / 200;
                    report.AppendLine($"{GameData.Spots[spot].Name},{(upgraded ? 15 : 10)},{(deep ? "deep" : "shallow")},{count/200:0.00},{kg/200:0.00},{val/200:0.00}");
                }
                Check(values[1] > values[0] && counts[0] > counts[1], "same net mass: deep earns more, shallow has more fish");
            }
            File.WriteAllText("Logs/crew026/net-balance.csv", report.ToString()); Debug.Log("[Catchline] CREW026 ACTUAL NET BALANCE:\n" + report);
            TripEconomy(); UnityEngine.Object.DestroyImmediate(g.gameObject);
            Ui(); Debug.Log("[Catchline] NET023 PROGRESSION CHECKS PASSED");
        }
        static void TripEconomy()
        {
            var report = new System.Text.StringBuilder("composition,freshGross,agedGross,netAfterExampleCosts\n");
            foreach (bool mixed in new[] { false, true })
            {
                var cargo = new List<CaughtFish>();
                for (int i = 0; i < (mixed ? 125 : 250); i++) cargo.Add(new CaughtFish { Species = Species.Herring, Kg = .2f });
                for (int i = 0; i < (mixed ? 50 : 100); i++) cargo.Add(new CaughtFish { Species = Species.Mackerel, Kg = .5f });
                if (mixed) { for (int i = 0; i < 6; i++) cargo.Add(new CaughtFish { Species = Species.Cod, Kg = 6 }); for (int i = 0; i < 2; i++) cargo.Add(new CaughtFish { Species = Species.Conger, Kg = 7 }); }
                var s = new GameState(1) { Hull = 2 }; int fresh = s.QuoteSale(cargo, 0).Coins;
                int aged = s.QuoteSale(cargo, 180).Coins;
                // Illustrative expenses: fuel/crew/bait and10shallow or5shallow+5deep net cycles.
                report.AppendLine($"{(mixed ? "50/50 by kg" : "small")},{fresh},{aged},{aged-(mixed ? 332 : 245)}");
            }
            File.WriteAllText("Logs/crew026/trip-economy.csv", report.ToString()); Debug.Log("[Catchline] CREW026 ILLUSTRATIVE100KG TRIP ECONOMY (not measured play):\n" + report);
        }
        static void Ui()
        {
            var g = Fixture(); g.Showcase(-1, 0); g.State.Coins = 4999;
            Field(g, "hudTab", VoyageGame.HudTab.Chandlery); Field(g, "panelOpen", true); Field(g, "toastUntil", 0f);
            g.PrepareInterface(844, 390);
            Check(!g.InvokeInterface("upgrade/NetSystem/buy") && g.State.Coins == 4999, "real shop refuses4999");
            g.State.Coins = 5000; g.PrepareInterface(844, 390);
            Check(g.InvokeInterface("upgrade/NetSystem/buy") && g.State.Coins == 0 && g.State.NetCapacityKg == 15, "real shop charges5000 and upgrades both nets");
            g.State.Owned.Remove(UpgradeId.NetSystem); g.State.Coins = 6000; Field(g, "toastUntil", 0f);
            var shot = typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic);
            void Shot(string n, int w, int h) => shot.Invoke(null, new object[] { g, "../crew026/" + n, w, h, 1f });
            foreach (var size in new[] { new Vector2Int(1440,900), new Vector2Int(844,390) })
            {
                g.PrepareInterface(size.x, size.y); var scroll = g.GetComponentsInChildren<UnityEngine.UI.ScrollRect>().Single(); Canvas.ForceUpdateCanvases();
                var card = g.GetComponentsInChildren<RectTransform>().Single(t => t.name == "upgrade/NetSystem");
                scroll.verticalNormalizedPosition = 1 - Mathf.Clamp01((-card.anchoredPosition.y - 6) / (scroll.content.rect.height - scroll.viewport.rect.height));
                Shot("net-upgrade-" + size.x, size.x, size.y);
            }
            g.State.Coins = 200; g.RequestDeparture(); Shot("departure-100kg", 1440, 900);
            Field(g, "departureReady", false); g.StartNetBoatTrial();
            g.State.Deckhand = null; g.State.ExtraCrew.Clear(); g.SyncCrew(); foreach (var rod in g.Rods) rod.State = RodState.Ready;
            g.State.SelectedNet = NetKind.Shallow; g.State.Rng = new System.Random(12);
            Check(g.SetNet(), "manyfish real capture starts net"); NetHaulChecks.FinishCaptainSet(g);
            typeof(VoyageGame).GetMethod("TickNet", H).Invoke(g, new object[] { 20f });
            Check(g.HaulNet(), "manyfish real capture hauls"); NetHaulChecks.FinishCaptainHaul(g);
            for (int i = 0; i < 600 && g.LastNetReceipt == null; i++) g.Tick(.05f);
            Check(g.LastNetReceipt != null && g.LastNetReceipt.Count > 5 && g.HoldKg <= 10.001f, "manyfish actual storage/capture");
            Shot("school-net-stowed", 1440, 900); Shot("school-net-stowed-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
        public static void ValidateAndBuild()
        {
            ArtImport.BuildLibrary(); Run(); FuelDepartureChecks.Run(); WeightNetChecks.Regression(); BuildBoth();
            Debug.Log("[Catchline] CREW026 COMBINED REGRESSION PASSED");
        }
        public static void BuildBoth()
        {
            // Every release, including stat-only rebuilds, resolves and validates live water.
            PtsWaterChecks.Run();
            foreach (bool test in new[] { false, true })
            {
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var g = new GameObject(test ? "Tier3 isolated test" : "Persistent Catchline").AddComponent<VoyageGame>(); g.SessionOnly = test;
                string scene = test ? "Assets/Scenes/Crew026Test.unity" : "Assets/Scenes/Crew026Real.unity";
                EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scene);
                string output = Path.GetFullPath("Builds/Crew026/" + (test ? "Test" : "Real") + "/Catchline.exe");
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { scene }, locationPathName = output, target = BuildTarget.StandaloneWindows64 });
                Check(report.summary.result == BuildResult.Succeeded, "build " + (test ? "test" : "real"));
                Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: " + output);
            }
        }
    }
}

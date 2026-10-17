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
    public static class WeightNetChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("Weight/net check failed: " + why); }
        static object Call(VoyageGame g, string n, params object[] a) => typeof(VoyageGame).GetMethod(n, H).Invoke(g, a);
        static void Set(VoyageGame g, string n, object v) => typeof(VoyageGame).GetProperty(n).GetSetMethod(true).Invoke(g, new[] { v });
        static void Field(VoyageGame g, string n, object v) => typeof(VoyageGame).GetField(n, H).SetValue(g, v);
        static VoyageGame Fixture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Weight020 isolated fixture").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build(); g.StartNetBoatTrial();
            foreach (var p in g.ExtraPeople.Concat(new[] { g.Captain, g.Hand })) if (p != null) p.Stop();
            g.State.Deckhand = null; g.State.ExtraCrew.Clear(); g.SyncCrew();
            return g;
        }
        static void SaveChecks()
        {
            string path = Path.GetFullPath("Logs/weight020/save-test.json");
            var s = new GameState(17) { Coins = 400, Hull = 2, SelectedNet = NetKind.Deep };
            s.Owned.Add(UpgradeId.BigCooler); s.DeepNetUses.AddRange(new[] { 1, 3 });
            s.UnsoldCatch.Add(new CaughtFish { Species = Species.Conger, Kg = 15.17f });
            s.Save(path); var loaded = GameState.Load(path);
            Check(loaded != null && loaded.SelectedNet == NetKind.Deep && loaded.DeepNetUses.SequenceEqual(new[] { 1, 3 }), "deep remaining uses persist exactly");
            Check(loaded.CoolerCapacity == 150 && loaded.UnsoldCatch.Single().Kg == 15.17f && loaded.Coins == 400, "upgrades/cargo/coins preserved");
            s.DeepNetUses.Clear(); s.Save(path); Check(GameState.Load(path).DeepNetUses.Count == 0, "exhausted stock never refills");
            File.WriteAllText(path, "{\"Version\":1,\"Coins\":123,\"Hull\":0,\"Owned\":[0],\"Charts\":[],\"Board\":[],\"Offers\":[],\"Active\":[],\"UnsoldCatch\":[{\"Species\":0,\"Kg\":0.25}]}");
            loaded = GameState.Load(path);
            Check(loaded != null && loaded.CoolerCapacity == 35 && loaded.DeepNetUses.Count == 0 && loaded.UnsoldCatch.Single().Kg == .25f && loaded.Coins == 123, "legacy save keeps actual fish and upgrade without granting deep nets");
            s = new GameState(18) { Coins = 99 }; Check(!s.BuyDeepNet() && s.Coins == 99, "deep insufficient funds atomic");
            s.Coins = 300; Check(s.BuyDeepNet() && s.BuyDeepNet() && s.BuyDeepNet() && !s.BuyDeepNet() && s.Coins == 0, "rack and purchase cost exact");
            s.SpendDeepNetUse(); Check(s.DeepNetUses.SequenceEqual(new[] { 2, 3, 3 }), "one failed/success use preserves reserve");
            s.SpendDeepNetUse(); s.SpendDeepNetUse(); Check(s.DeepNetUses.SequenceEqual(new[] { 3, 3 }), "exhausted fitted net rotates reserve");
        }
        static void StorageChecks(VoyageGame g)
        {
            g.Cooler.Clear(); Check(g.TryStore(new CaughtFish { Kg = g.State.CoolerCapacity - .01f }), "fill just below capacity");
            Check(!g.HoldFull && g.TryStore(new CaughtFish { Kg = 150f }) && g.HoldFull, "unlimited whole final trophy accepted");
            Check(!g.TryStore(new CaughtFish { Kg = .1f }) && g.Cooler.Count == 2, "next concurrent insert rejected");
            g.Cooler.Clear(); Check(!g.TryStore(new CaughtFish { Kg = 0 }) && !g.TryStore(new CaughtFish { Kg = float.NaN }), "invalid fish cannot occupy storage");
            for (int i = 0; i < 80; i++) Check(g.TryStore(new CaughtFish { Kg = .1f }), "no hidden fish-count cap");
            Check(Mathf.Abs(g.HoldKg - 8) < .001f, "mass sum correct"); g.Cooler.Clear();
            for (int i = 0; i < 3; i++)
            {
                g.State.Hull = i; float basic = g.State.CoolerCapacity; g.State.Owned.Add(UpgradeId.BigCooler);
                Check(g.State.CoolerCapacity == (i == 0 ? 35f : basic * 1.5f), "upgrade adds kg on every hull"); g.State.Owned.Clear();
            }
            g.State.Hull = 2;
        }
        static void PriceChecks()
        {
            var s = new GameState(19);
            foreach (var d in GameData.Fish)
            {
                Check(Mathf.Abs(s.SpecimenPricePerKg(d.Species, d.MaxKg) / s.SpecimenPricePerKg(d.Species, d.MinKg) - 1.5f) < .001f, "large specimen earns50%more per kg " + d.Name);
                Check(s.SpecimenPricePerKg(d.Species, d.MaxKg * 10) == s.SpecimenPricePerKg(d.Species, d.MaxKg), "premium capped for saved oversized fish");
            }
            var fish = new System.Collections.Generic.List<CaughtFish> { new() { Species = Species.Cod, Kg = 6 }, new() { Species = Species.Herring, Kg = .2f } };
            int coins = s.Coins; var quote = s.QuoteSale(fish, 0); var sale = s.Sell(fish, 0);
            Check(quote.Coins == sale.Coins && s.Coins == coins + sale.Coins, "sale quote and actual payout agree");
        }
        static void NetChecks(VoyageGame g)
        {
            g.State.Coins = 100; Check(g.State.BuyDeepNet(), "buy deep net for real captain trial");
            g.State.SelectedNet = NetKind.Deep;
            Check(!g.SelectNetLoadout(NetKind.Shallow), "cannot switch underway");
            Check(g.SetNet(), "set deep net"); NetHaulChecks.ReachCaptainWinch(g); g.CancelNetHaulGame();
            Check(g.State.DeepNetUses[0] == 3 && g.Net == VoyageGame.NetState.Stowed, "cancel set spends no use");
            Check(g.SetNet(), "retry deep net"); NetHaulChecks.FinishCaptainSet(g);
            Check(g.NetRemaining >= 29.9f, "deep30second soak"); Call(g, "TickNet", 30f);
            float kg = g.NetCatchKg; int count = g.NetCatch; Check(kg > 0 && count > 0, "deep kg batch exists");
            g.Cooler.Add(new CaughtFish { Kg = g.State.CoolerCapacity - .01f });
            Check(g.HaulNet(), "haul deep with one final fish space"); NetHaulChecks.FinishCaptainHaul(g);
            Check(g.State.DeepNetUses[0] == 2 && g.NetBasketCount == count, "one successful use spent before unloading");
            for (int i = 0; i < 600 && g.NetUnloadActive; i++) g.Tick(.05f);
            Check(g.Cooler.Count == 2 && g.HoldFull && g.NetBasketCount == count - 1, "batch inserts only one final fish and retains overflow");
            Check(g.LastNetReceipt != null && g.LastNetReceipt.Count == 1, "manifest counts only actual stored fish");
            g.Cooler.Clear(); foreach (var f in g.OnDeck.ToArray()) { UnityEngine.Object.DestroyImmediate(f.Root.gameObject); } g.OnDeck.Clear();
            // Real setting mistakes invoke production failure callback; repeat cancel must not spend twice.
            Check(g.SetNet(), "set next deep cycle"); NetHaulChecks.ReachCaptainWinch(g);
            for (int i = 0; i < 400 && g.NetGameActive; i++) { if (g.NetGamePhase < .1f) g.TapNetGame(); Call(g, "TickNet", .05f); }
            Check(g.State.DeepNetUses[0] == 1 && !g.NetGameActive && g.NetCatch == 0, "failed setting loses one use, retains remaining net");
            g.CancelNetHaulGame(); Check(g.State.DeepNetUses[0] == 1, "cancel after failure cannot double debit");
        }
        sealed class FixedRoll : System.Random
        {
            readonly double roll; public FixedRoll(double roll) { this.roll = roll; }
            public override double NextDouble() => roll;
        }
        static void WorkerChecks(VoyageGame g)
        {
            g.State.Deckhand = new CrewMember { Name = "Net hand", Role = CrewRole.Deckhand, VoyagesLeft = 3 };
            g.SyncCrew();
            foreach (double roll in new[] { .79999, .8, .99 })
            {
                Call(g, "ResetNet"); g.Cooler.Clear();
                foreach (var f in g.OnDeck) UnityEngine.Object.DestroyImmediate(f.Root.gameObject);
                g.OnDeck.Clear(); g.State.DeepNetUses.Clear(); g.State.DeepNetUses.AddRange(new[] { 3, 3 });
                g.State.SelectedNet = NetKind.Deep; g.State.Rng = new System.Random(9);
                Call(g, "RollCompactCatch"); Set(g, "Net", VoyageGame.NetState.Ready);
                g.State.Rng = new FixedRoll(roll); g.Hand.Stop();
                Check(g.TryNetWork(g.Hand), "worker claims deep haul");
                for (int i = 0; i < 1200 && g.Net == VoyageGame.NetState.Hauling; i++) g.Hand.Tick(.05f, 1, Quaternion.identity);
                Check(g.State.DeepNetUses.SequenceEqual(new[] { 2, 3 }), "worker spends one use and keeps reserves on either outcome");
                Check((g.NetBasketCount > 0) == (roll < .8), "worker exact80percent success boundary");
                Check(g.State.NetInventory == 3, "deep outcomes never consume shallow reserve");
            }
            g.State.DeepNetUses.Clear(); g.State.DeepNetUses.Add(1); g.State.Rng = new FixedRoll(.79);
            Call(g, "RollCompactCatch"); Set(g, "Net", VoyageGame.NetState.Ready);
            Check(g.TryNetWork(g.Hand), "recover last deep use");
            for (int i = 0; i < 1200 && g.Net == VoyageGame.NetState.Hauling; i++) g.Hand.Tick(.05f, 1, Quaternion.identity);
            Call(g, "ClearNetUnload"); g.Hand.Stop();
            Check(g.State.DeepNetUses.Count == 0 && g.CanCaptainNet && g.CaptainNetAction(), "exhausted rack never blocks retrying basket unloading");
            Call(g, "ClearNetUnload"); g.Captain.Stop();
            foreach (var f in g.OnDeck) UnityEngine.Object.DestroyImmediate(f.Root.gameObject);
            g.OnDeck.Clear(); g.Cooler.Clear(); g.Cooler.Add(new CaughtFish { Kg = g.State.CoolerCapacity - .01f });
            foreach (var person in new[] { g.Captain, g.Hand })
            {
                person.Place(g.State.HullDef.HoldAccess);
                person.Carrying = new DeckFish { Kg = 10, Root = new GameObject("Concurrent final fish").transform };
                Call(g, "Stow", person); person.Tick(.01f, 1, Quaternion.identity);
            }
            Check(g.Captain.Busy && g.Hand.Busy && g.DepartureOverflow() == 1, "both stow concurrently and departure predicts single overflow");
            g.Captain.Tick(10, 1, Quaternion.identity); g.Hand.Tick(10, 1, Quaternion.identity);
            Check(g.Cooler.Count == 2 && g.Hand.Carrying != null && g.HoldFull, "same-frame deliveries accept only one final whole fish");
            g.Cooler.Clear(); g.Cooler.Add(new CaughtFish { Kg = 50f }); g.Cooler.Add(new CaughtFish { Kg = 49.999996f });
            Check(!g.HoldFull && g.DepartureOverflow() == 0, "departure uses exact sum even when displayed float rounds to capacity");
        }
        static void Balance(VoyageGame g)
        {
            var report = new System.Text.StringBuilder("ground,method,meanFish,meanKg,meanFreshQuote,workerExpectedAfterNetCostPerHaul\n");
            for (int spot = 0; spot < GameData.Spots.Length; spot++)
            foreach (bool deep in new[] { false, true })
            {
                double kg = 0, value = 0, count = 0;
                for (int seed = 0; seed < 500; seed++)
                {
                    Set(g, "State", new GameState(seed) { Hull = 2, SelectedNet = deep ? NetKind.Deep : NetKind.Shallow });
                    Set(g, "ActiveSpot", spot); Call(g, "RollCompactCatch");
                    var batch = (System.Collections.Generic.List<(Species species, float kg)>)typeof(VoyageGame).GetField("netFish", H).GetValue(g);
                    Check(batch.All(f => GameData.Spots[spot].Table.Any(e => e.species == f.species)), "every net specimen belongs to selected ground");
                    Check(batch.All(f => f.kg >= GameData.Get(f.species).MinKg && f.kg <= GameData.Get(f.species).MaxKg), "net never fabricates out-of-range specimens");
                    var fish = batch.Select(f => new CaughtFish { Species = f.species, Kg = f.kg }).ToList();
                    count += fish.Count; kg += g.NetCatchKg; value += g.State.QuoteSale(fish, 0).Coins;
                }
                double gross = value / 500;
                double netCost = deep ? GameData.DeepNetCost / (double)GameData.DeepNetUses : .2 * GameData.NetReplacementCost;
                report.AppendLine(FormattableString.Invariant($"{GameData.Spots[spot].Name},{(deep ? "deep" : "shallow")},{count / 500:0.00},{kg / 500:0.00},{gross:0.00},{gross * .8 - netCost:0.00}"));
                Check(gross * .8 > netCost, "fresh worker net economics positive before voyage expenses");
            }
            File.WriteAllText("Logs/weight020/balance.csv", report.ToString());
            Debug.Log("[Catchline] WEIGHT020 BALANCE (fresh unsaturated market;500seeds/ground/method;before voyage expenses):\n" + report);
        }
        static void Capture()
        {
            var g = Fixture(); g.StartNetBoatTrial(); g.State.DeepNetUses.AddRange(new[] { 2, 3 });
            g.State.SelectedNet = NetKind.Deep;
            g.TryStore(new CaughtFish { Species = Species.SeaBass, Kg = 2.8f });
            var shot = typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic);
            void Shot(string name, int w, int h) => shot.Invoke(null, new object[] { g, "../weight020/" + name, w, h, 1f });
            Shot("fishing-desktop", 1440, 900); Shot("fishing-phone", 844, 390);
            g.HeadHome(); for (int i = 0; i < 1000 && g.CurrentMode != VoyageGame.Mode.Harbour; i++) g.Tick(.05f);
            Field(g, "hudTab", VoyageGame.HudTab.Supplies); Field(g, "panelOpen", true);
            Field(g, "toastUntil", 0f);
            Shot("supplies-desktop", 1440, 900); Shot("supplies-phone", 844, 390);
            foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            {
                g.PrepareInterface(size.x, size.y);
                var scroll = g.GetComponentsInChildren<UnityEngine.UI.ScrollRect>().Single();
                Canvas.ForceUpdateCanvases(); scroll.verticalNormalizedPosition = 0;
                Shot("net-purchase-" + size.x, size.x, size.y);
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
        static void UiChecks()
        {
            var g = Fixture(); Set(g, "CurrentMode", VoyageGame.Mode.Harbour);
            Field(g, "hudTab", VoyageGame.HudTab.Supplies); Field(g, "panelOpen", true); Field(g, "toastUntil", 0f);
            g.State.Coins = 99; g.PrepareInterface(844, 390);
            Check(!g.InvokeInterface("supplies/deep-net/buy") && g.State.DeepNetUses.Count == 0, "deep purchase disabled on shortfall");
            g.State.Coins = 100; g.PrepareInterface(844, 390);
            Check(g.InvokeInterface("supplies/deep-net/buy") && g.State.Coins == 0 && g.State.DeepNetUses.SequenceEqual(new[] { 3 }), "real shop buys one3use net");
            g.PrepareInterface(844, 390); Check(g.InvokeInterface("supplies/loadout/deep") && g.DeepNetSelected, "harbour selects deep loadout");
            g.State.DeepNetUses.AddRange(new[] { 3, 3 }); g.State.Coins = 1000; g.PrepareInterface(844, 390);
            Check(!g.InvokeInterface("supplies/deep-net/buy") && g.State.Coins == 1000, "full deep rack cannot charge");
            var scroll = g.GetComponentsInChildren<UnityEngine.UI.ScrollRect>().Single();
            Canvas.ForceUpdateCanvases(); scroll.verticalNormalizedPosition = 0; g.PrepareInterface(844, 390); Canvas.ForceUpdateCanvases();
            var button = g.GetComponentsInChildren<RectTransform>().Single(t => t.name == "supplies/deep-net/buy");
            var corners = new Vector3[4]; button.GetWorldCorners(corners);
            Check(corners.All(c => RectTransformUtility.RectangleContainsScreenPoint(scroll.viewport, RectTransformUtility.WorldToScreenPoint(null, c))), "deep purchase button fully reachable at bottom on phone");
            Set(g, "CurrentMode", VoyageGame.Mode.Fishing); g.PrepareInterface(844, 390);
            Check(!g.InvokeInterface("supplies/deep-net/buy"), "sea cannot buy deep nets through stale shop control");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
        public static void Run()
        {
            Directory.CreateDirectory("Logs/weight020"); ArtImport.BuildLibrary(); SaveChecks(); PriceChecks();
            var g = Fixture(); StorageChecks(g); NetChecks(g); WorkerChecks(g); Balance(g); UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] WEIGHT NET CHECKS PASSED"); Debug.Log("[Catchline] Snapshot written to Logs/weight020");
        }
        public static void Regression()
        {
            Run(); UiChecks(); FirstVoyageChecks.Regression(); NetHaulChecks.Run(); NetEconomyChecks.Run();
            CrewPolishChecks.Run(); CatchRewardChecks.Run(); ChartChecks.Run(); SeaClearanceChecks.Run();
            Capture(); Debug.Log("[Catchline] WEIGHT020 REGRESSION PASSED");
            Debug.Log("[Catchline] Snapshot written to Logs/weight020");
        }
        public static void Review() { Run(); UiChecks(); Capture(); }
        public static void ReviewAndBuildPreview() { Review(); BuildPreview(); }
        public static void BuildPreview()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Weight020 preview").AddComponent<VoyageGame>(); g.SessionOnly = true;
            const string scene = "Assets/Scenes/Weight020Preview.unity";
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scene);
            string output = Path.GetFullPath("Builds/Weight020/Catchline.exe");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { scene }, locationPathName = output, target = BuildTarget.StandaloneWindows64 });
            Check(report.summary.result == BuildResult.Succeeded, "isolated preview build");
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: " + output);
        }
    }
}

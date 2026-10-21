using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

namespace Catchline.EditorTools
{
    public static class CatchRewardChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static object Call(VoyageGame g, string name, params object[] args) => typeof(VoyageGame).GetMethod(name, Hidden).Invoke(g, args);
        static void Check(bool ok, string why) { if (!ok) throw new Exception("Catch reward check failed: " + why); }
        static void Until(VoyageGame g, Func<bool> done, string why, float seconds = 30)
        {
            for (float t = 0; t < seconds && !done(); t += .05f) g.Tick(.05f);
            Check(done(), why);
        }
        static VoyageGame Fixture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Isolated catch reward fixture").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build(); g.State.Hull = 2; g.State.Fuel = g.State.FuelCapacity;
            Call(g, "RebuildBoat", false);
            typeof(VoyageGame).GetField("showTitle", Hidden).SetValue(g, false);
            g.State.FoodMinutes = g.State.FoodCapacity; g.Showcase(0, 0);
            foreach (var rod in g.Rods) rod.State = RodState.Ready;
            return g;
        }
        static void Basket(VoyageGame g, int count)
        {
            for (int i = 0; i < count; i++)
            {
                var f = new DeckFish { Species = i % 2 == 0 ? Species.Herring : Species.Mackerel,
                    Kg = i % 2 == 0 ? .2f : .4f, Age = 1, CaughtAt = g.SimTime, FromNetBasket = true, Tile = g.State.HullDef.NetAccess };
                f.RestPos = new Vector3(4.2f, .07f, 1.15f);
                f.Root = DeckFish.BuildModel(f.Species, f.Kg, g.Boat); f.Root.localPosition = f.RestPos;
                g.OnDeck.Add(f);
            }
            Call(g, "BeginNetUnload", g.Captain);
        }
        static Rect UiRect(VoyageGame g, string name)
        {
            var r = g.GetComponentsInChildren<RectTransform>().Single(t => t.name == name);
            return new Rect(r.anchoredPosition.x, -r.anchoredPosition.y, r.rect.width, r.rect.height);
        }
        static void Shot(VoyageGame g, string name, int w = 1440, int h = 900, float type = 1)
            => typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic)
                .Invoke(null, new object[] { g, "../catch018/" + name, w, h, type });
        public static void Run()
        {
            Check(CatchPresentation.Tier(Species.Herring, .2f) == CatchTier.Common, "white common");
            Check(CatchPresentation.Tier(Species.Herring, .29f) == CatchTier.BigCommon, "green big common relative to species");
            Check(CatchPresentation.Tier(Species.Turbot, 2) == CatchTier.Rare, "blue rare");
            Check(CatchPresentation.Tier(Species.Turbot, 4.9f) == CatchTier.BigRare, "purple big rare");
            foreach (var fish in GameData.Fish)
            {
                float cutoff = fish.MaxKg * .75f;
                Check(!CatchPresentation.IsBig(fish.Species, cutoff - .0001f) && CatchPresentation.IsBig(fish.Species, cutoff), "size boundary " + fish.Name);
                if ((int)fish.Species < 10) Check((int)CatchPresentation.Tier(fish.Species, fish.MaxKg) < (int)CatchTier.Legendary, "legacy fish never promoted by value " + fish.Name);
            }
            Check(Enum.GetValues(typeof(CatchTier)).Cast<CatchTier>().Select(CatchPresentation.Accent).Distinct().Count() == 6, "six distinct future-ready styles");
            var g = Fixture();
            Check(g.SetNet(), "actual captain sets net"); NetHaulChecks.FinishCaptainSet(g);
            Call(g, "TickNet", GameData.ShallowNetSoakSeconds); Check(g.HaulNet(), "actual captain hauls"); NetHaulChecks.FinishCaptainHaul(g);
            var actual = g.OnDeck.Where(f => f.FromNetBasket).ToArray();
            Check(actual.Length > 0 && g.LastNetReceipt == null && g.Cooler.Count == 0, "no storage receipt at landing");
            Until(g, () => g.Captain.BusyLabel == "Gathering net catch" && g.Captain.Busy, "real gathering");
            Check(g.LastNetReceipt == null, "no receipt during gathering");
            Until(g, () => g.Captain.BusyLabel == "Stowing net catch" && g.Captain.Busy, "real stowing");
            Check(g.LastNetReceipt == null, "no receipt before stow completes");
            Until(g, () => g.LastNetReceipt != null, "receipt follows actual successful storage");
            var receipt = g.LastNetReceipt;
            Check(receipt.Count == actual.Length && g.Cooler.Count == actual.Length, "net list exact inserted count");
            Check(Mathf.Abs(receipt.Kg - actual.Sum(f => f.Kg)) < .0001f, "net list exact total weight");
            Check(receipt.Value == g.Cooler.Sum(f => g.State.ValueOf(f, g.SimTime)), "receipt value uses actual current market and freshness");
            Check(receipt.Items.Select(f => f.Species).OrderBy(x => x).SequenceEqual(actual.Select(f => f.Species).OrderBy(x => x)), "net list exact species multiset");
            int coins = g.State.Coins;
            g.Tick(.4f);
            foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390), new Vector2Int(2560, 1440) })
            {
                g.PrepareInterface(size.x, size.y, 1);
                var panel = UiRect(g, "catch/net"); var ui = g.GetComponentInChildren<CoastalCanvas>();
                Check(panel.xMin >= 0 && panel.yMin >= 0 && panel.xMax <= ui.Width && panel.yMax <= ui.Height, "receipt fits native viewport");
                Check(!panel.Overlaps(UiRect(g, "hold/freshness")), "receipt clear of hold status");
                Check(g.GetComponentsInChildren<Text>().Single(t => t.name == "catch/net/total").text.StartsWith(receipt.Count + " fish"), "visible count honest");
            }
            g.Tick(12); g.PrepareInterface(1440, 900);
            Check(g.InvokeInterface("catch/net/review"), "last haul can be reopened"); g.PrepareInterface(1440, 900);
            Check(ReferenceEquals(g.LastNetReceipt, receipt) && g.State.Coins == coins && g.Cooler.Count == actual.Length, "review never pays or duplicates fish");
            g.State.Rng = new System.Random(92);
            for (int i = 0; i < 20; i++) g.PrepareInterface(1440, 900);
            Check(g.State.Rng.Next() == new System.Random(92).Next(), "presentation consumes no catch RNG");
            g.Cooler[0].Kg = 100;
            Check(receipt.Kg < 100, "receipt snapshot independent of later live mutation");
            Call(g, "ResetFeedback"); Check(g.LastNetReceipt == null, "new voyage clears review snapshot");
            UnityEngine.Object.DestroyImmediate(g.gameObject);

            g = Fixture(); Basket(g, 3); g.Tick(.2f); g.Captain.Stop();
            Check(g.Cooler.Count == 0 && g.LastNetReceipt == null && !g.NetUnloadActive && g.OnDeck.All(f => f.ClaimedBy == null), "cancel gather releases claims with no false reward");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            g = Fixture();
            g.Cooler.Add(new CaughtFish { Species = Species.Herring, Kg = g.State.CoolerCapacity - .01f });
            Basket(g, 3); Until(g, () => g.LastNetReceipt != null, "partial hold stores available fish");
            Check(g.LastNetReceipt.Count == 1 && g.OnDeck.Count(f => f.FromNetBasket) == 2, "partial receipt excludes unstored backlog");
            int count = g.Cooler.Count;
            g.Tick(10); Check(g.Cooler.Count == count && g.LastNetReceipt.Count == 1, "full hold never adds ghost receipt entries");
            Call(g, "ResetCatchReceipts");
            var carried = g.OnDeck.First(); g.OnDeck.Remove(carried); carried.Root.SetParent(g.Captain.Root, false); g.Captain.Carrying = carried;
            Check(!(bool)Call(g, "TryStow", g.Captain) && g.LastNetReceipt == null, "full manual storage creates no reward");
            g.Cooler.RemoveAt(0);
            Check((bool)Call(g, "TryStow", g.Captain) && g.LastNetReceipt.Count == 1, "manual leftover net fish gets actual storage receipt");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] CATCH REWARD CHECKS PASSED: tiers/size boundaries, no current legendary, actual net-storage species/count/kg/value, cancellation/full/partial/manual safety, review no mutation, viewport/status clearance, snapshot/RNG isolation");
        }
        public static void Capture()
        {
            Directory.CreateDirectory(Path.GetFullPath("Logs/catch018"));
            var g = Fixture(); g.StartNetBoatTrial();
            var examples = new[] { (Species.Mackerel, .42f, "white"), (Species.Mackerel, .68f, "green"), (Species.Turbot, 2.4f, "blue"), (Species.Turbot, 4.9f, "purple") };
            foreach (var example in examples)
            {
                g.LandFish(g.Rods[0], example.Item1, example.Item2); g.Tick(.45f);
                Shot(g, example.Item3 + "-desktop"); Shot(g, example.Item3 + "-phone", 844, 390);
                g.PrepareInterface(844, 390);
                var panel = UiRect(g, "catch");
                Check(!panel.Overlaps(UiRect(g, "net/orders")) && !panel.Overlaps(UiRect(g, "home")), "reward does not cover crew or home controls");
            }
            // Art fixture only: real supported species/weights, passed through the exact
            // production storage-snapshot/UI methods. Actual net distribution tested in Run.
            var sample = new[] {
                new CaughtFish { Species = Species.Herring, Kg = .2f, StowedAt = g.SimTime },
                new CaughtFish { Species = Species.Herring, Kg = .24f, StowedAt = g.SimTime },
                new CaughtFish { Species = Species.Mackerel, Kg = .4f, StowedAt = g.SimTime },
                new CaughtFish { Species = Species.Whiting, Kg = .7f, StowedAt = g.SimTime },
                new CaughtFish { Species = Species.Pollock, Kg = 1.3f, StowedAt = g.SimTime } };
            g.Cooler.AddRange(sample); Call(g, "RecordStoredNet", new object[] { sample }); g.Tick(.45f);
            Shot(g, "net-list-desktop"); Shot(g, "net-list-phone", 844, 390); Shot(g, "net-list-laptop", 2560, 1440);
            Shot(g, "large-type-phone", 844, 390, 1.15f);
            g.Tick(12); Shot(g, "review-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] Snapshot written to Logs/catch018 (native world+Canvas, four active tiers and net receipt)");
        }
        public static void ValidateAndBuildPreview()
        {
            ArtImport.BuildLibrary(); FirstVoyageChecks.Regression(); NetHaulChecks.Run(); NetEconomyChecks.Run(); CrewPolishChecks.Run(); Run(); Capture(); BuildPreview();
        }
        public static void ReviewAndBuildPreview() { ArtImport.BuildLibrary(); Run(); Capture(); BuildPreview(); }
        public static void BuildPreview()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Catchline catch presentation preview").AddComponent<VoyageGame>(); game.SessionOnly = true;
            const string scene = "Assets/Scenes/Catch018Preview.unity";
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scene);
            var output = Path.GetFullPath("Builds/Catch018/Catchline.exe");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { scene }, locationPathName = output,
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None });
            Check(report.summary.result == BuildResult.Succeeded, "separate reward preview built");
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: " + output);
        }
    }
}

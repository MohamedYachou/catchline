using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class FirstVoyageChecks
    {
        static void Check(bool condition, string message)
        {
            if (!condition) throw new Exception("[Catchline] First voyage check failed: " + message);
        }

        static void Until(VoyageGame game, Func<bool> done, string label, float timeout = 45f)
        {
            for (float t = 0f; t < timeout && !done(); t += .05f) game.Tick(.05f);
            Check(done(), label);
        }

        public static void Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("First voyage check").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.Build();
            bool hadAutoCarry = PlayerPrefs.HasKey("catchline.autoCarry");
            int autoCarry = PlayerPrefs.GetInt("catchline.autoCarry", 1);
            try
            {
                PlayerPrefs.SetInt("catchline.autoCarry", 0);
                Check(game.FirstVoyage && game.LearningFishing && game.StrikeWindow == 1.5f, "gentle first catches");
                game.SetSail();
                Until(game, () => game.CurrentMode == VoyageGame.Mode.Fishing, "arrives at sea", 240f);
                Check(game.VoyageHint().Contains("Tap Fish"), "first cast prompt");
                var rod = game.Rods[0];
                Check(game.UsesDeckGraph, "first voyage uses the rowboat deck graph");
                var basket = game.GearStation(StationKind.Rod, rod.Index).Out;
                var sort = game.DeckGraph.OfKind(StationKind.SortTable).First();
                // The reading minigame holds the failed result until the line has returned.
                game.CommandRod(rod);
                Until(game, () => rod.State == RodState.Waiting, "first cast");
                Check(game.VoyageHint().Contains("bobber"), "waiting never says tap Fish");
                game.StrikeTap();
                Check(game.Stats.Spooked == 1 && rod.ReadingResult == StrikeResult.TooEarly && rod.State == RodState.Waiting,
                    "early strike records one failed reading before returning the line");
                game.StrikeTap();
                Check(game.Stats.Spooked == 1 && rod.ReadingResult == StrikeResult.TooEarly, "duplicate strike cannot repeat a failed result");
                Until(game, () => rod.Reading == null && rod.State == RodState.Unbaited, "failed cast returns unbaited");

                for (int n = 0; n < 100 && !game.HoldFull; n++)
                {
                    // Each completed reading needs the real Fish command to recast.
                    if (game.CanCommandRod(rod)) game.CommandRod(rod);
                    Until(game, () => rod.State == RodState.Bite, "bite");
                    Check(game.VoyageHint().Contains("now"), "strike instruction at bite");
                    game.StrikeTap();
                    Until(game, () => basket.Count == 1, "catch lands in rod basket");
                    Check(game.OnDeck.Count == 0, "graph catch does not use legacy loose deck list");
                    bool undersize = FishRules.Undersize(basket.Fish[0]);
                    int stored = game.Cooler.Count, thrown = game.ThrownBack;
                    Check(game.CaptainHaulFrom(basket), "Carry starts the captain haul");
                    Until(game, () => sort.In.Count == 1, "catch reaches sorting table");
                    game.CommandKeep(true);
                    Until(game, () => undersize ? game.ThrownBack == thrown + 1 : game.Cooler.Count == stored + 1,
                        "Keep returns undersize or stows keeper");
                    Check(game.Scheduler.Balanced, "catch conserved through carry, sort and stow");
                    if (game.Stats.Landed >= 3) Check(!game.LearningFishing && Mathf.Approximately(game.StrikeWindow, game.State.BiteWindow), "normal timing after third landed fish");
                }
                Debug.Log($"[Catchline] First voyage catch totals: {game.Stats.Landed} landed, {game.Cooler.Count} stored, {game.ThrownBack} returned, {game.HoldKg:0.000}/{game.State.CoolerCapacity}kg, {game.State.Bait} bait; hint {game.VoyageHint()}");
                Check(game.VoyageHint().Contains("Cooler full"), "return prompt");
                int securedCount = game.Cooler.Count;
                game.HeadHome();
                Until(game, () => game.CurrentMode == VoyageGame.Mode.Harbour, "sale at harbour", 240f);
                Check(game.State.UnsoldCatch.Count == securedCount && game.State.LastSale == null, "arrival keeps the haul unsold");
                Check(game.SellHaul(), "captain explicitly sells haul");
                Check(game.State.LogCount.Sum() == securedCount && game.State.LastSale.Coins > 0, "sale and fish log");
                Debug.Log($"[Catchline] First trip: {game.State.LastSale.Minutes:0.00} min, {game.State.LastSale.Coins} earned, {game.State.Coins} total; cooler costs {GameData.Upgrade(UpgradeId.BigCooler).Cost}");
                Check(!game.FirstVoyage && !game.LearningFishing, "tutorial stays completed after sale");
                int coins = game.State.Coins;
                Check(coins >= GameData.Upgrade(UpgradeId.BigCooler).Cost + GameData.BaitPackCost, "first full trip funds cooler plus replacement bait");
                Check(game.State.TryBuy(UpgradeId.BigCooler) && Mathf.Approximately(game.State.CoolerCapacity, GameData.RowboatBigCoolerKg), "first upgrade uses current rowboat cooler capacity");
                Check(!game.State.TryBuy(UpgradeId.BigCooler), "upgrade spends once");
                string save = Path.GetFullPath("Logs/first-voyage-test-save.json");
                try
                {
                    game.State.Save(save);
                    var loaded = GameState.Load(save);
                    Check(loaded != null && loaded.LogCount.Sum() == securedCount, "learning progress survives save");
                    Check(ArtLibrary.Get().UiTex("fish-herring") != null && ArtLibrary.Get().UiTex("fish-mackerel") != null, "catch portraits available");
                }
                finally { if (File.Exists(save)) File.Delete(save); }
            }
            finally
            {
                if (hadAutoCarry) PlayerPrefs.SetInt("catchline.autoCarry", autoCarry);
                else PlayerPrefs.DeleteKey("catchline.autoCarry");
                UnityEngine.Object.DestroyImmediate(game.gameObject);
            }
            Debug.Log("[Catchline] FIRST VOYAGE CHECKS PASSED");
        }

        public static void Regression()
        {
            Run();
            SkiffChecks.Run();
            SkiffChecks.Automation();
            UrgentCrewChecks.Run();
            SalePayoutChecks.Run();
            FisherFeedbackChecks.Run();
            CoastalPolishChecks.Run();
            PtsWaterChecks.Run();
            MenuSystemChecks.Run();
            InterfaceChecks.Run();
            CompactFisherChecks.Run();
            NetChoiceChecks.Run();
            ReferenceHudChecks.Run();
            Check(ArtLibrary.Get().WaterShader != null && !ShaderUtil.ShaderHasError(ArtLibrary.Get().WaterShader), "water shader imports and compiles");
            Check(ArtLibrary.Get().WaterTextures.Length == 7 && ArtLibrary.Get().WaterTex("water-tile").wrapMode == TextureWrapMode.Repeat, "seven water/effect textures import with repeating sea tile");
            Debug.Log("[Catchline] FIRST VOYAGE REGRESSION PASSED");
        }

        // Call on Catchline-sim only. This preview has a separate scene and never loads/saves real progress.
        public static void ValidateAndBuildPreview()
        {
            Regression();
            BuildPreview();
        }

        public static void BuildPreview()
        {
            ArtImport.BuildLibrary();
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Catchline preview").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            const string scenePath = "Assets/Scenes/FirstVoyagePreview.unity";
            EditorSceneManager.SaveScene(scene, scenePath);
            string output = Path.GetFullPath("Builds/FirstVoyage/Catchline.exe");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { scenePath }, locationPathName = output,
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None,
            });
            if (report.summary.result != BuildResult.Succeeded) throw new Exception("Preview build failed: " + report.summary.result);
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: " + output);
        }
    }
}

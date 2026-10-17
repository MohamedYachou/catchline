using System;
using System.IO;
using Catchline.Game;
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
            Check(game.FirstVoyage && game.LearningFishing && game.StrikeWindow == 1.5f, "gentle first catches");
            game.SetSail();
            Until(game, () => game.CurrentMode == VoyageGame.Mode.Fishing, "arrives at sea");
            Check(game.VoyageHint().Contains("Tap Fish"), "first cast prompt");
            var rod = game.Rods[0];
            // Fail once on purpose: the normal early-strike cost and recovery still work.
            game.CommandRod(rod);
            Until(game, () => rod.State == RodState.Waiting, "first cast");
            Check(game.VoyageHint().Contains("bobber"), "waiting never says tap Fish");
            game.StrikeTap();
            Check(game.Stats.Spooked == 1 && rod.State == RodState.Unbaited, "early strike still costs bait");

            for (int n = 0; n < 100 && !game.HoldFull; n++)
            {
                // Manning recasts after an early strike; following catches need the real Fish command.
                if (game.CanCommandRod(rod)) game.CommandRod(rod);
                Until(game, () => rod.State == RodState.Bite, "bite");
                Check(game.VoyageHint().Contains("now"), "strike instruction at bite");
                game.StrikeTap();
                Until(game, () => game.OnDeck.Count > 0 && game.CanCarry(game.OnDeck[0]), "catch lands and can be carried");
                Check(game.VoyageHint().Contains("Carry"), "carry prompt");
                game.CommandCarry(game.OnDeck[0]);
                int target = n + 1;
                Until(game, () => game.Cooler.Count == target, "real pickup and stow path");
                if (n == 2) Check(!game.LearningFishing && Mathf.Approximately(game.StrikeWindow, game.State.BiteWindow), "normal timing after third landed fish");
            }
            Check(game.VoyageHint().Contains("Cooler full"), "return prompt");
            int securedCount = game.Cooler.Count;
            game.HeadHome();
            Until(game, () => game.CurrentMode == VoyageGame.Mode.Harbour, "sale at harbour");
            Check(game.State.UnsoldCatch.Count == securedCount && game.State.LastSale == null, "arrival keeps the haul unsold");
            Check(game.SellHaul(), "captain explicitly sells haul");
            Check(game.State.LogCount[0] + game.State.LogCount[1] == securedCount && game.State.LastSale.Coins > 0, "sale and fish log");
            Debug.Log($"[Catchline] First trip: {game.State.LastSale.Minutes:0.00} min, {game.State.LastSale.Coins} earned, {game.State.Coins} total; cooler costs {GameData.Upgrade(UpgradeId.BigCooler).Cost}");
            Check(!game.FirstVoyage && !game.LearningFishing, "tutorial stays completed after sale");
            int coins = game.State.Coins;
            Check(coins >= GameData.Upgrade(UpgradeId.BigCooler).Cost + GameData.BaitPackCost, "first full trip funds cooler plus replacement bait");
            Check(game.State.TryBuy(UpgradeId.BigCooler) && game.State.CoolerCapacity == 6, "first upgrade unlocks6kg");
            Check(!game.State.TryBuy(UpgradeId.BigCooler), "upgrade spends once");
            string save = Path.GetFullPath("Logs/first-voyage-test-save.json");
            try
            {
                game.State.Save(save);
                var loaded = GameState.Load(save);
                Check(loaded != null && loaded.LogCount[0] + loaded.LogCount[1] == securedCount, "learning progress survives save");
                Check(ArtLibrary.Get().UiTex("fish-herring") != null && ArtLibrary.Get().UiTex("fish-mackerel") != null, "catch portraits available");
            }
            finally { if (File.Exists(save)) File.Delete(save); }
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

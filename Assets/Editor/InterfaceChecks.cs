using System;
using System.IO;
using System.Reflection;
using System.Linq;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;

namespace Catchline.EditorTools
{
    public static class InterfaceChecks
    {
        static readonly BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Set(VoyageGame game, string field, object value) => typeof(VoyageGame).GetField(field, Private).SetValue(game, value);
        static void Check(bool pass, string message) { if (!pass) throw new Exception("Coastal interface check failed: " + message); }
        static VoyageGame Fixture()
        {
            var game = new GameObject("Isolated coastal UI fixture").AddComponent<VoyageGame>();
            game.SessionOnly = true; game.Build(); Set(game, "showTitle", false);
            game.Tick(.01f);
            return game;
        }
        static void Shot(VoyageGame game, string path, int width, int height, float textScale = 0)
        {
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            game.Cam.targetTexture = rt;
            game.Cam.aspect = (float)width / height;
            game.PrepareInterface(width, height, textScale);
            Canvas.ForceUpdateCanvases();
            var request = new RenderPipeline.StandardRequest { destination = rt };
            if (RenderPipeline.SupportsRenderRequest(game.Cam, request)) RenderPipeline.SubmitRenderRequest(game.Cam, request);
            else game.Cam.Render();
            var uiTarget = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            game.GetComponentInChildren<CoastalCanvas>().RenderCapture(uiTarget);
            var composite = new Material(Shader.Find("Hidden/Catchline/Coastal UI Composite"));
            Graphics.Blit(uiTarget, rt, composite);
            var previous = RenderTexture.active; RenderTexture.active = rt;
            var texture = new Texture2D(width, height, TextureFormat.RGB24, false);
            texture.ReadPixels(new Rect(0, 0, width, height), 0, 0); texture.Apply();
            Directory.CreateDirectory(Path.GetDirectoryName(path)); File.WriteAllBytes(path, texture.EncodeToPNG());
            // A completed scene-only render must never be reported as HUD proof.
            int bright = 0;
            for (int y = 0; y < 16; y++) for (int x = 0; x < 16; x++)
            {
                float px = game.CurrentMode == VoyageGame.Mode.Harbour ? .35f + x * .035f : .04f + x * .009f;
                float py = game.CurrentMode == VoyageGame.Mode.Harbour ? .12f + y * .045f : .77f + y * .010f;
                Color sample = texture.GetPixel(Mathf.RoundToInt(width * px), Mathf.RoundToInt(height * py));
                if (sample.r > .8f && sample.g > .75f && sample.b > .6f) bright++;
            }
            Check(bright > 85, "native interface surface is present in capture");
            RenderTexture.active = previous; game.Cam.targetTexture = null;
            UnityEngine.Object.DestroyImmediate(texture); UnityEngine.Object.DestroyImmediate(rt);
            UnityEngine.Object.DestroyImmediate(uiTarget); UnityEngine.Object.DestroyImmediate(composite);
        }
        public static void Run()
        {
            var game = Fixture();
            game.State.Coins = 100;
            game.PrepareInterface(1440, 900);
            Check(game.InvokeInterface("shop/tab/Supplies"), "supplies tab is a real retained button"); game.Tick(0);
            int bait = game.State.Bait, coins = game.State.Coins;
            Check(game.InvokeInterface("supplies/worms/buy"), "worm purchase is reachable");
            Check(game.State.Bait == bait + GameData.BaitPackSize && game.State.Coins == coins - GameData.BaitPackCost, "UI purchase charges exactly once");
            game.State.Coins = 0; game.Tick(0);
            Check(!game.InvokeInterface("supplies/squid/buy") && game.State.Coins == 0, "unaffordable control disabled");
            game.State.Coins = 100; game.InvokeInterface("shop/tab/Chandlery"); game.Tick(0);
            Check(game.InvokeInterface("upgrade/BigCooler/buy"), "upgrade button bound"); game.Tick(0);
            Check(game.State.Has(UpgradeId.BigCooler) && !game.InvokeInterface("upgrade/BigCooler/buy"), "owned upgrade cannot be bought twice");
            Check(!game.InvokeInterface("refit/buy"), "locked refit disabled");
            game.InvokeInterface("shop/tab/Market"); game.State.UnsoldCatch.Add(new CaughtFish { Species = Species.Herring, Kg = .3f, StowedAt = 0 }); game.Tick(0);
            coins = game.State.Coins;
            Check(game.InvokeInterface("market/sell") && game.State.Coins > coins, "sell control pays the saved haul"); game.Tick(0);
            Check(!game.InvokeInterface("market/sell"), "sold haul cannot be sold twice");
            game.Showcase(0, 0); game.Tick(.01f);
            Check(game.InvokeInterface("rod/0"), "world fishing control bound");
            game.Tick(.1f);
            Check(game.Manning != null, "rod command reaches gameplay");
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] COASTAL INTERFACE CHECKS PASSED (native Canvas controls/state; no physical pointer claim)");
        }
        public static void Capture()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            FishArtChecks.Run();
            Run();
            var game = Fixture();
            game.State.Coins = 380;
            string folder = Path.GetFullPath("Logs/hud008");
            foreach (VoyageGame.HudTab tab in Enum.GetValues(typeof(VoyageGame.HudTab)))
            {
                Set(game, "hudTab", tab); game.Tick(0);
                Shot(game, Path.Combine(folder, "shop-" + tab + "-desktop.png"), 1440, 900);
                Shot(game, Path.Combine(folder, "shop-" + tab + "-phone.png"), 844, 390);
            }
            for (int i = 0; i < 6; i++) game.State.UnsoldCatch.Add(new CaughtFish { Species = Species.Mackerel, Kg = .4f, StowedAt = 0 });
            Set(game, "hudTab", VoyageGame.HudTab.Market); game.Tick(0);
            Shot(game, Path.Combine(folder, "market-haul-desktop.png"), 1440, 900);
            game.Showcase(0, 0); game.Tick(.1f);
            Shot(game, Path.Combine(folder, "fishing-idle-desktop.png"), 1440, 900);
            Shot(game, Path.Combine(folder, "fishing-idle-phone.png"), 844, 390);
            game.CommandRod(game.Rods[0]);
            for (int i = 0; i < 500 && game.MinigameRod?.State != RodState.Bite; i++) game.Tick(.05f);
            Check(game.MinigameRod?.State == RodState.Bite, "capture reaches actual bite");
            Shot(game, Path.Combine(folder, "fishing-bite-desktop.png"), 1440, 900);
            Shot(game, Path.Combine(folder, "fishing-bite-phone.png"), 844, 390);
            game.StrikeTap();
            for (int i = 0; i < 300 && game.Stats.Landed == 0; i++) game.Tick(.05f);
            game.Tick(.5f);
            Shot(game, Path.Combine(folder, "fishing-catch-desktop.png"), 1440, 900);
            Shot(game, Path.Combine(folder, "fishing-catch-phone.png"), 844, 390);
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            game = Fixture(); game.State.Coins = 5000; game.State.BestVoyageFish = GameData.SkiffFishGoal;
            Check(game.RefitSkiff(), "crew capture refit"); game.Tick(2);
            for (int i = 0; i < 3 && game.State.Board.Count > 0; i++) game.State.Hire(game.State.Board[0]);
            game.SyncCrew(); game.Showcase(1, 0); game.Tick(.1f);
            Shot(game, Path.Combine(folder, "skiff-crew-phone.png"), 844, 390);
            Shot(game, Path.Combine(folder, "skiff-crew-large-phone.png"), 844, 390, 1.15f);
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] Snapshot written to " + folder + " (actual native Canvas and world, isolated fixtures)");
        }
        public static void CaptureSingle()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = Fixture();
            Shot(game, Path.GetFullPath("Logs/hud008/render-diagnostic.png"), 1440, 900);
            Debug.Log("[Catchline] Snapshot written to render-diagnostic");
        }
    }
}

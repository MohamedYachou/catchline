using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEditor;
using UnityEditor.Build.Reporting;

namespace Catchline.EditorTools
{
    public static class NetPlayChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static object Call(VoyageGame g, string name, params object[] args) => typeof(VoyageGame).GetMethod(name, Hidden).Invoke(g, args);
        static void Check(bool ok, string why) { if (!ok) throw new Exception("Net play check failed: " + why); }
        static void Work(Person p) { for (int i = 0; i < 1000 && !p.Idle; i++) p.Tick(.05f, Quaternion.identity); }
        static void Shot(VoyageGame g, string name, int w = 1440, int h = 900) => typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic)
            .Invoke(null, new object[] { g, "../net015/" + name, w, h, 1f });
        public static void ValidateAndBuildPreview()
        {
            FirstVoyageChecks.Regression();
            NetEconomyChecks.Run();
            SeaClearanceChecks.Run();
            ChartChecks.Capture();
            Capture();
            BuildPreview();
        }
        public static void ReviewAndBuildPreview()
        {
            Capture();
            BuildPreview();
        }
        public static void BuildPreview()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Catchline feedback preview").AddComponent<VoyageGame>();
            g.SessionOnly = true;
            const string scene = "Assets/Scenes/Net015Preview.unity";
            EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scene);
            string output = Path.GetFullPath("Builds/Net015/Catchline.exe");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { scene }, locationPathName = output,
                target = BuildTarget.StandaloneWindows64, options = BuildOptions.None });
            Check(report.summary.result == BuildResult.Succeeded, "separate feedback preview built");
            Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: " + output);
        }
        public static void Capture()
        {
            PreviewSetupChecks.Run();
            NetHaulChecks.Run();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Player feedback net/scene fixture").AddComponent<VoyageGame>();
            game.SessionOnly = true; game.Build(); game.StartNetBoatTrial();
            Directory.CreateDirectory(Path.GetFullPath("Logs/net015"));
            for (int spot = 0; spot < GameData.Spots.Length; spot++)
            {
                game.Showcase(spot, 0); game.Tick(.01f);
                SeaClearanceChecks.Verify(game, spot);
                Shot(game, "map-" + spot);
            }
            game.Showcase(0, 0);
            Shot(game, "stern-icon-laptop", 2560, 1440); Shot(game, "stern-icon-phone", 844, 390);
            Check(game.InvokeInterface("net"), "stern net icon uses real set action"); Work(game.Captain);
            Shot(game, "setting-taps"); Shot(game, "setting-phone", 844, 390);
            NetHaulChecks.FinishCaptainSet(game);
            Check(game.Net == VoyageGame.NetState.Soaking && game.NetRemaining == GameData.ShallowNetSoakSeconds, "short40second soak");
            Call(game, "TickNet", GameData.ShallowNetSoakSeconds); game.PrepareInterface(1440, 900);
            Check(game.InvokeInterface("net"), "stern icon starts ready haul");
            NetHaulChecks.ReachCaptainWinch(game);
            Shot(game, "winch-start"); Shot(game, "winch-phone", 844, 390);
            for (int i = 0; i < 500 && game.NetGameActive; i++)
            {
                if (game.NetGameTension < .64f) game.TapNetGame();
                game.Tick(.05f);
                if (i == 40) Shot(game, "winch-mid");
            }
            Check(!game.NetGameActive && game.NetUnloadActive && game.NetBasketCount >= 2, "haul starts automatic batch unloading");
            int netCount = game.NetBasketCount, before = game.Cooler.Count;
            for (int i = 0; i < 400 && game.NetUnloadActive; i++)
            {
                game.Tick(.05f);
                if (i == 32) Shot(game, "automatic-unloading");
            }
            Check(!game.NetUnloadActive && game.NetBasketCount == 0 && game.Cooler.Count >= before + netCount, "whole net batch automatically enters storage without a single Carry command");
            Shot(game, "unloaded");
            // Two simultaneous deliveries deliberately share the same hold-access tile.
            game.Captain.Stop(); game.Hand.Stop();
            foreach (var p in new[] { game.Captain, game.Hand })
            {
                p.Place(game.State.HullDef.HoldAccess);
                p.Carrying = new DeckFish { Species = Species.Herring, Kg = .3f, CaughtAt = game.SimTime, Root = new GameObject("Concurrent delivery").transform };
                p.Carrying.Root.SetParent(p.Root, false);
                Call(game, "Stow", p); p.Tick(.01f, Quaternion.identity);
            }
            Check(game.Captain.Busy && game.Hand.Busy && game.Captain.BusyLabel == "Stowing" && game.Hand.BusyLabel == "Stowing", "both actors stow at once without a hold lock");
            before = game.Cooler.Count; Work(game.Captain); Work(game.Hand);
            Check(game.Cooler.Count == before + 2, "concurrent deliveries each count exactly once");
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] NET PLAY CHECKS PASSED: clear hull-growth corridor, stern icon,40s soak,actual winch,automatic batch storage,concurrent deliveries");
            Debug.Log("[Catchline] Snapshot written to Logs/net015");
        }
    }
}

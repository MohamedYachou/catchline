using System;
using System.IO;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.EditorTools
{
    // Camera renders of the lead's new views for review in the scratch editor (no UI: IMGUI and the overlay canvas are
    // not in a camera render). Batch: -executeMethod Catchline.EditorTools.LeadShots.Run ; CATCHLINE_SHOTS filters
    // the sets (harbour, intro, cage, trip). Images go to docs/screens/overnight/ in the main checkout.
    public static class LeadShots
    {
        const string Out = @"C:\Users\momoy\Projects\Catchline\docs\screens\overnight\";
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;

        public static void Run()
        {
            Directory.CreateDirectory(Out);
            ArtImport.BuildLibrary();
            var only = Environment.GetEnvironmentVariable("CATCHLINE_SHOTS");
            bool Want(string set) => string.IsNullOrEmpty(only) || only.Contains(set);
            if (Want("harbour")) Harbour();
            if (Want("intro")) Intro();
            if (Want("cage")) Cage();
            if (Want("trip")) Trip();
            if (Want("net")) Net();
            if (Want("gut")) Gut();
            if (Want("traffic")) Traffic();
            Debug.Log("LEADSHOTS DONE " + Out);
        }

        static VoyageGame Game(string name)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject(name).AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
            typeof(VoyageGame).GetField("showTitle", H).SetValue(g, false);
            return g;
        }

        static void Shot(VoyageGame g, string file, int width = 1440, int height = 900)
        {
            var rt = RenderTexture.GetTemporary(width, height, 24, RenderTextureFormat.ARGB32);
            var target = g.Cam.targetTexture; var active = RenderTexture.active;
            var texture = new Texture2D(width, height, TextureFormat.RGBA32, false);
            try
            {
                g.Cam.targetTexture = rt; g.Cam.aspect = width / (float)height;
                RenderPipeline.SubmitRenderRequest(g.Cam, new RenderPipeline.StandardRequest { destination = rt });
                RenderTexture.active = rt; texture.ReadPixels(new Rect(0, 0, width, height), 0, 0); texture.Apply();
                File.WriteAllBytes(Out + file + ".png", texture.EncodeToPNG());
            }
            finally { g.Cam.targetTexture = target; RenderTexture.active = active; RenderTexture.ReleaseTemporary(rt); UnityEngine.Object.DestroyImmediate(texture); }
        }

        static void Rebuild(VoyageGame g, int hull)
        {
            g.State.Hull = hull; g.State.Coins = 10000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", H).Invoke(g, new object[] { false });
            for (int i = 0; i < 60; i++) g.Tick(.05f);
        }

        static void Harbour()
        {
            for (int hull = 0; hull <= 4; hull++)
            {
                var g = Game("Harbour shot"); Rebuild(g, hull);
                Shot(g, $"harbour-h{hull}");
                Shot(g, $"harbour-h{hull}-phone", 844, 390);
                UnityEngine.Object.DestroyImmediate(g.gameObject);
            }
        }

        static void Traffic()
        {
            var g = Game("Traffic shot"); Rebuild(g, 2);
            g.ShowHarbourTraffic(.42f); Shot(g, "traffic-h2-basin");
            g.BeginIntro();
            for (float t = 0; t < 3f; t += .05f) g.Tick(.05f);
            g.ShowHarbourTraffic(.3f); Shot(g, "traffic-intro-mouth");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Intro()
        {
            var g = Game("Intro shot");
            for (int i = 0; i < 40; i++) g.Tick(.05f);
            g.BeginIntro();
            float t = 0;
            foreach (float at in new[] { .5f, 3f, 5.5f, 8f, 10f })
            {
                while (t < at) { g.Tick(.05f); t += .05f; }
                Shot(g, $"intro-{at:0.0}s");
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Cage()
        {
            var g = Game("Cage shot");
            g.StartTier5Trial();
            var timers = (float[])typeof(VoyageGame).GetField("buoyTimers", H).GetValue(g);
            timers[0] = timers[1] = g.BuoySoakSeconds;
            g.TryBuoyWork(g.Captain);
            for (int i = 0; i < 400 && !g.CageViewActive; i++) g.Tick(.05f);
            for (int i = 0; i < 12; i++) g.Tick(.05f);
            Shot(g, "cage-0-start"); Shot(g, "cage-0-start-phone", 844, 390);
            var cage = g.Cage;
            for (int i = 0; i < 6; i++) { g.TapCage(); g.Tick(.05f); g.Tick(.05f); }
            Shot(g, "cage-1-hauling");
            for (int i = 0; i < 200 && cage.Phase == CagePhase.Pull; i++) { g.TapCage(); g.Tick(.08f); }
            if (cage.Phase == CagePhase.Snag) { g.Tick(.3f); Shot(g, "cage-2-snag"); g.DragCage(cage.SnagDirection); }
            for (int i = 0; i < 200 && cage.Phase == CagePhase.Pull; i++) { g.TapCage(); g.Tick(.08f); }
            for (int i = 0; i < 20; i++) g.Tick(.05f);
            Shot(g, "cage-3-board"); Shot(g, "cage-3-board-phone", 844, 390);
            if (cage.Current is { } crab) { g.FlickCage(!crab.Keeper); g.Tick(.05f); g.Tick(.15f); Shot(g, "cage-4-flick"); }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Net()
        {
            var g = NetViewChecks.Fixture();
            g.SetNet();
            for (int i = 0; i < 600 && !g.NetViewActive; i++) g.Tick(.05f);
            for (int i = 0; i < 14; i++) g.Tick(.05f);
            Shot(g, "net-0-setting"); Shot(g, "net-0-setting-phone", 844, 390);
            int shots = 0;
            for (int i = 0; i < 800 && g.NetGameActive; i++)
            {
                if (g.NetGamePhase >= .43f && g.NetGamePhase <= .55f && g.TapNetGame() && shots++ == 1) { g.Tick(.025f); g.Tick(.3f); Shot(g, "net-1-cast"); }
                g.Tick(.025f);
            }
            typeof(VoyageGame).GetMethod("TickNet", H).Invoke(g, new object[] { GameData.ShallowNetSoakSeconds + 1f });
            g.HaulNet();
            for (int i = 0; i < 600 && !g.NetViewActive; i++) g.Tick(.05f);
            for (int i = 0; i < 14; i++) g.Tick(.05f);
            bool mid = false, bunt = false;
            for (int i = 0; i < 1200 && g.NetGameActive; i++)
            {
                if (g.NetGameTension < .64f) g.TapNetGame();
                g.Tick(.025f);
                if (!mid && g.NetGameProgress > .3f) { mid = true; Shot(g, "net-2-haul"); }
                if (!bunt && g.NetGameProgress > .85f) { bunt = true; Shot(g, "net-3-bunt"); Shot(g, "net-3-bunt-phone", 844, 390); }
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Gut()
        {
            var (g, table) = GutViewChecks.Fixture(2);
            g.CaptainGutAt(table);
            for (int i = 0; i < 400 && !g.GutWaiting; i++) g.Tick(.05f);
            for (int i = 0; i < 14; i++) g.Tick(.05f);
            Shot(g, "gut-0-board"); Shot(g, "gut-0-board-phone", 844, 390);
            g.CutGut(GutViewChecks.CleanCut); g.Tick(.2f);
            Shot(g, "gut-1-clean"); Shot(g, "gut-1-clean-phone", 844, 390);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void Trip()
        {
            var g = Game("Trip shot"); Rebuild(g, 2);
            for (int i = 0; i < 5; i++) if (!g.State.Known(0)) g.State.BuyChart(0);
            g.SelectedSpot = 0; g.SetSail();
            float t = 0;
            foreach (float at in new[] { 3f, 9f, 16f, 22f })
            {
                while (t < at) { g.Tick(.05f); t += .05f; }
                Shot(g, $"trip-{at:00}s-{g.Leg}");
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
    }
}

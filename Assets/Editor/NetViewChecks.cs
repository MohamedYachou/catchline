using System;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // The captain's net work opens the full-screen net view, plays through setting and hauling under the unchanged
    // VoyageNetGame rules, and hands back to the orthographic deck camera with the captain visible again.
    // Batch: -executeMethod Catchline.EditorTools.NetViewChecks.Run
    public static class NetViewChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string what) { if (!ok) throw new Exception("NETVIEW: " + what); }
        static void Set(VoyageGame g, string key, object value) => typeof(VoyageGame).GetProperty(key).GetSetMethod(true).Invoke(g, new[] { value });

        public static VoyageGame Fixture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Net view check").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
            typeof(VoyageGame).GetField("showTitle", H).SetValue(g, false);
            Check(g.StartNetBoatTrial(), "compact net boat trial");
            for (int i = 0; i < 20; i++) g.Tick(.05f);
            Check(g.CurrentMode == VoyageGame.Mode.Fishing, "fishing at the spot");
            return g;
        }

        public static string Run()
        {
            ArtImport.BuildLibrary();
            var g = Fixture();
            Check(g.SetNet(), "the captain takes the net");
            for (int i = 0; i < 600 && !g.NetViewActive; i++) g.Tick(.05f);
            Check(g.NetViewActive && g.NetGameSetting, "setting opens the net view");
            for (int i = 0; i < 12; i++) g.Tick(.05f);
            Check(!g.Cam.orthographic, "on a perspective camera");
            Check(!g.Captain.Root.GetComponentInChildren<Renderer>().enabled, "with the captain hidden");
            float setting = 0;
            for (int i = 0; i < 800 && g.NetGameActive; i++)
            {
                if (g.NetGamePhase >= .43f && g.NetGamePhase <= .55f) g.TapNetGame();
                g.Tick(.025f); setting += .025f;
            }
            Check(g.Net == VoyageGame.NetState.Soaking, "three clean casts set the net");
            for (int i = 0; i < 60; i++) g.Tick(.05f);
            Check(!g.NetViewActive && g.Cam.orthographic, "the view hands back while the net soaks");
            Check(g.Captain.Root.GetComponentInChildren<Renderer>().enabled, "and the captain is visible again");

            typeof(VoyageGame).GetMethod("TickNet", H).Invoke(g, new object[] { GameData.ShallowNetSoakSeconds + 1f });
            Check(g.HaulNet(), "the captain hauls");
            for (int i = 0; i < 600 && !g.NetViewActive; i++) g.Tick(.05f);
            Check(g.NetViewActive && !g.NetGameSetting, "hauling opens the net view");
            float haul = 0;
            for (int i = 0; i < 1200 && g.NetGameActive; i++)
            {
                if (g.NetGameTension < .64f) g.TapNetGame();
                g.Tick(.025f); haul += .025f;
            }
            Check(g.Net == VoyageGame.NetState.Stowed, "a balanced rhythm brings the net aboard");
            for (int i = 0; i < 60; i++) g.Tick(.05f);
            Check(!g.NetViewActive && g.Cam.orthographic, "and the view hands back");

            UnityEngine.Object.DestroyImmediate(g.gameObject);
            string text = $"NETVIEW PASS · set {setting:0.0}s · haul {haul:0.0}s";
            Debug.Log(text);
            return text;
        }

        [MenuItem("Catchline/Checks/Net view")]
        static void Menu() => Debug.Log(Run());
    }
}

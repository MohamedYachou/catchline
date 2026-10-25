using System;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // The new-game intro flies in on a perspective camera and hands back to the exact orthographic harbour camera, on
    // its own or when skipped, and leaves no sky or fog behind. Batch: -executeMethod Catchline.EditorTools.IntroChecks.Run
    public static class IntroChecks
    {
        static void Check(bool ok, string what) { if (!ok) throw new Exception("INTRO: " + what); }

        public static string Run()
        {
            ArtImport.BuildLibrary();
            string report = "";
            foreach (bool skip in new[] { false, true })
            {
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var g = new GameObject("Intro check").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
                typeof(VoyageGame).GetField("showTitle", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic).SetValue(g, false);
                for (int i = 0; i < 40; i++) g.Tick(.05f);
                var deckRotation = g.Cam.transform.rotation; var deckPosition = g.Cam.transform.position;
                bool fog = RenderSettings.fog;
                g.BeginIntro();
                g.Tick(.05f);
                Check(g.IntroActive && !g.Cam.orthographic, "the intro flies a perspective camera");
                Check(Vector3.Distance(g.Cam.transform.position, deckPosition) > 10, "it starts out at sea");
                float seconds = 0;
                if (skip) { g.Tick(1f); g.SkipIntro(); }
                for (int i = 0; i < 400 && g.IntroActive; i++) { g.Tick(.05f); seconds += .05f; }
                Check(!g.IntroActive && g.Cam.orthographic, "it hands back to the orthographic camera");
                Check(Quaternion.Angle(g.Cam.transform.rotation, deckRotation) < .01f, "with the harbour camera's angle");
                Check(Vector3.Distance(g.Cam.transform.position, deckPosition) < .5f, $"and position ({Vector3.Distance(g.Cam.transform.position, deckPosition):0.00} m off)");
                Check(RenderSettings.fog == fog && GameObject.Find("Intro sky") == null, "no sky or fog left behind");
                Check(g.CurrentMode == VoyageGame.Mode.Harbour, "still in harbour");
                report += skip ? $" · skipped, done in {seconds + 1:0.0}s" : $" · full {seconds:0.0}s";
                UnityEngine.Object.DestroyImmediate(g.gameObject);
            }
            string text = "INTRO PASS" + report;
            Debug.Log(text);
            return text;
        }

        [MenuItem("Catchline/Checks/Intro")]
        static void Menu() => Debug.Log(Run());
    }
}

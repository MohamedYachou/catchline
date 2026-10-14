using System;
using System.IO;
using Catchline.Prototype;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.EditorTools
{
    public static class PrototypeTools
    {
        const string ScenePath = "Assets/Scenes/DeckPrototype.unity";

        // Creates the prototype scene (one GameObject with DeckPrototype) and makes it the first build scene.
        [MenuItem("Catchline/Create Deck Prototype Scene")]
        public static void CreateScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            new GameObject("DeckPrototype").AddComponent<DeckPrototype>();
            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Debug.Log($"[Catchline] Created {ScenePath}");
        }

        // Opens the prototype scene and enters Play mode. Also usable as a launch argument:
        //   Unity -projectPath . -executeMethod Catchline.EditorTools.PrototypeTools.OpenAndPlay
        [MenuItem("Catchline/Play Deck Prototype %#p")]
        public static void OpenAndPlay()
        {
            if (!File.Exists(ScenePath)) CreateScene();
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            EditorSceneManager.OpenScene(ScenePath);
            EditorApplication.delayCall += () => EditorApplication.isPlaying = true;
        }

        // Batchmode check: builds the deck, runs the simulation headless, logs a report
        // and renders a PNG.
        //   Unity -batchmode -quit -projectPath . -executeMethod Catchline.EditorTools.PrototypeTools.Snapshot
        //         -snapshotPath out.png -simSeconds 90 [-fullCrew yes]
        public static void Snapshot()
        {
            string path = Arg("-snapshotPath", Path.GetFullPath("Logs/deck-snapshot.png"));
            float seconds = float.Parse(Arg("-simSeconds", "90"), System.Globalization.CultureInfo.InvariantCulture);

            if (!File.Exists(ScenePath)) CreateScene();
            EditorSceneManager.OpenScene(ScenePath);
            var deck = UnityEngine.Object.FindFirstObjectByType<DeckPrototype>();
            deck.Build();
            if (Arg("-fullCrew", "no") == "yes") deck.StaffFully();

            float reportEvery = 30f, nextReport = reportEvery;
            for (float t = 0f; t < seconds; t += 0.05f)
            {
                deck.Tick(0.05f);
                if (deck.SimTime >= nextReport)
                {
                    Debug.Log("[Catchline] " + deck.Report());
                    nextReport += reportEvery;
                }
            }

            Render(deck.Cam, path, 1600, 900);
            Debug.Log($"[Catchline] Snapshot written to {path}");
        }

        static void Render(Camera cam, string path, int width, int height)
        {
            var rt = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
            cam.aspect = (float)width / height;
            var request = new RenderPipeline.StandardRequest { destination = rt };
            if (RenderPipeline.SupportsRenderRequest(cam, request)) RenderPipeline.SubmitRenderRequest(cam, request);
            else
            {
                cam.targetTexture = rt;
                cam.Render();
                cam.targetTexture = null;
            }

            var prev = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(width, height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, width, height), 0, 0);
            tex.Apply();
            RenderTexture.active = prev;
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            File.WriteAllBytes(path, tex.EncodeToPNG());
        }

        static string Arg(string name, string fallback)
        {
            var args = Environment.GetCommandLineArgs();
            int i = Array.IndexOf(args, name);
            return i >= 0 && i + 1 < args.Length ? args[i + 1] : fallback;
        }
    }
}

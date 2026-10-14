using System;
using System.IO;
using System.Linq;
using Catchline.Game;
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
            AssetDatabase.SaveAssets();
            Debug.Log($"[Catchline] Created {ScenePath}");
        }

        // Opens the prototype scene and enters Play mode. Also usable as a launch argument:
        //   Unity -projectPath . -executeMethod Catchline.EditorTools.PrototypeTools.OpenAndPlay
        [MenuItem("Catchline/Play Deck Prototype (old)")]
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

        const string VoyagePath = "Assets/Scenes/Voyage.unity";

        // Build 1 scene: one GameObject with VoyageGame. It becomes the first build scene.
        [MenuItem("Catchline/Create Voyage Scene")]
        public static void CreateVoyageScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            new GameObject("VoyageGame").AddComponent<VoyageGame>();
            EditorSceneManager.SaveScene(scene, VoyagePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(VoyagePath, true), new EditorBuildSettingsScene(ScenePath, true) };
            AssetDatabase.SaveAssets();
            Debug.Log($"[Catchline] Created {VoyagePath}");
        }

        [MenuItem("Catchline/Play Voyage %#p")]
        public static void PlayVoyage()
        {
            ArtImport.BuildLibrary();
            if (!File.Exists(VoyagePath)) CreateVoyageScene();
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            EditorSceneManager.OpenScene(VoyagePath);
            EditorApplication.delayCall += () => EditorApplication.isPlaying = true;
        }

        // Balance check: a bot plays N voyages headless, logs each voyage and renders a PNG mid-fishing.
        //   Unity -batchmode -quit -projectPath . -executeMethod Catchline.EditorTools.PrototypeTools.VoyageSim
        //         -voyages 15 [-seed 7] [-snapshotPath out.png]
        public static void VoyageSim()
        {
            int voyages = int.Parse(Arg("-voyages", "15"));
            string path = Arg("-snapshotPath", Path.GetFullPath("Logs/voyage-snapshot.png"));
            ArtImport.BuildLibrary();
            if (!File.Exists(VoyagePath)) CreateVoyageScene();
            EditorSceneManager.OpenScene(VoyagePath);
            var game = UnityEngine.Object.FindFirstObjectByType<VoyageGame>();
            game.Seed = int.Parse(Arg("-seed", "7"));
            game.AutoPlay = true;
            game.Build();
            var shaders = UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None)
                .SelectMany(r => r.sharedMaterials.Select(m => m == null ? $"{r.name}:null" : $"{m.name}:{m.shader.name}"))
                .Distinct().Take(25);
            Debug.Log("[Catchline] Materials: " + string.Join(" | ", shaders));
            // A shot of the harbour before the bot sails.
            game.Tick(0.2f);
            Render(game.Cam, path.Replace(".png", "-harbour.png"), 1600, 900);
            if (Arg("-showcase", "0") == "1")
            {
                // One shot per sea at the fishing camera, then the harbour wide and the deck close.
                for (int k = 0; k < GameData.Spots.Length; k++)
                {
                    game.Showcase(k, 0f);
                    Render(game.Cam, path.Replace(".png", $"-sea{k}.png"), 1600, 900);
                }
                game.Showcase(-1, 3f);
                Render(game.Cam, path.Replace(".png", "-harbour-wide.png"), 1600, 900);
                game.Showcase(-2, -1.4f);
                Render(game.Cam, path.Replace(".png", "-deck.png"), 1600, 900);
                game.Showcase(-1, 0f);
            }
            game.Tick(0.3f);

            int logged = 0;
            while (game.State.Voyage <= voyages && game.SimTime < voyages * 900f)
            {
                game.Tick(0.05f);
                while (logged < game.Log.Count) Debug.Log("[Catchline] " + game.Log[logged++]);
            }
            float until = game.SimTime + 600f;
            while (game.CurrentMode != VoyageGame.Mode.Fishing && game.SimTime < until) game.Tick(0.05f);
            float shotAt = game.SimTime + 35f;
            while (game.SimTime < shotAt) game.Tick(0.05f);
            Debug.Log($"[Catchline] Sim done at {game.SimTime / 60f:0.0} min, coins {game.State.Coins}");
            Render(game.Cam, path, 1600, 900);
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

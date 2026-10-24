using System.IO;
using Catchline.Game;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // The one player build: Real keeps the save, Test never reads or writes it.
    public static class GameBuild
    {
        [MenuItem("Catchline/Build Game (Real + Test)")]
        public static void BuildBoth()
        {
            // The v2 sprites live in the art library; a stale library silently falls back to old art.
            ArtImport.BuildLibrary();
            foreach (bool test in new[] { false, true })
            {
                string mode = test ? "Test" : "Real";
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                var game = new GameObject(test ? "Catchline (test, no save)" : "Catchline").AddComponent<VoyageGame>();
                game.SessionOnly = test;
                string scene = $"Assets/Scenes/Catchline{mode}.unity";
                EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(), scene);
                string output = Path.GetFullPath($"Builds/Catchline/{mode}/Catchline.exe");
                var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { scene }, locationPathName = output, target = BuildTarget.StandaloneWindows64 });
                if (report.summary.result != BuildResult.Succeeded) throw new System.Exception($"[Catchline] {mode} build {report.summary.result}");
                Debug.Log($"[Catchline] GAME BUILT: {output}");
            }
        }
    }
}

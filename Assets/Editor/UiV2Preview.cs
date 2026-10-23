using System.IO;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Save-isolated UI v2 preview: a SessionOnly VoyageGame scene, played in the editor, writes
    // composite frames to Logs/uiv2. Iteration aid only; acceptance frames come from native builds.
    public static class UiV2Preview
    {
        const string ScenePath = "Assets/Scenes/UiV2Preview.unity";

        static void EnsureScene()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("UI v2 save-isolated preview").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            EditorSceneManager.SaveScene(scene, ScenePath);
        }

        [MenuItem("Catchline/UI v2 Preview Capture")]
        public static void Capture() => Capture(null);

        public static void Capture(string screens)
        {
            ArtImport.BuildLibrary();
            EnsureScene();
            Directory.CreateDirectory("Temp");
            File.WriteAllLines("Temp/uiv2-request.txt", screens == null ? new[] { Path.GetFullPath("Logs/uiv2") } : new[] { Path.GetFullPath("Logs/uiv2"), screens });
            EditorSceneManager.OpenScene(ScenePath);
            EditorApplication.delayCall += () => EditorApplication.isPlaying = true;
        }

        // Native acceptance build of the same save-isolated scene.
        [MenuItem("Catchline/UI v2 Build Preview")]
        public static void BuildPreview()
        {
            ArtImport.BuildLibrary();
            EnsureScene();
            var output = Path.GetFullPath("Builds/UiV2/Catchline.exe");
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions { scenes = new[] { ScenePath }, locationPathName = output, target = BuildTarget.StandaloneWindows64, options = BuildOptions.None });
            // The capture script waits for this marker; the player stub keeps its template timestamp.
            File.WriteAllText("Logs/uiv2-build.txt", report.summary.result.ToString());
            if (report.summary.result != UnityEditor.Build.Reporting.BuildResult.Succeeded) throw new System.Exception("[Catchline] UIV2 build " + report.summary.result);
            Debug.Log("[Catchline] UIV2 PREVIEW BUILT: " + output);
        }
    }
}

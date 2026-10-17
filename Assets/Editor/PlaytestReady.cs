using UnityEditor;
using UnityEditor.SceneManagement;

namespace Catchline.EditorTools
{
    public static class PlaytestReady
    {
        public static void Open()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.OpenScene("Assets/Scenes/Voyage.unity");
            EditorApplication.isPlaying = false;
            UnityEngine.Debug.Log("[Catchline] Playtest ready: press Play, then Continue or New voyage. Imported models refresh the library automatically; stop and Play again after a new delivery.");
        }
    }
}

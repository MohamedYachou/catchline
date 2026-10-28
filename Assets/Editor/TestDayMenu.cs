using UnityEditor;
using Catchline.Game;

namespace Catchline.EditorTools
{
    // Mo's test day: Play on a throwaway save at the morning of a regular restaurant day (VoyageTestDay.cs).
    // Pressed while playing, it stops and starts again on the test save.
    static class TestDayMenu
    {
        [MenuItem("Catchline/Test the restaurant day")]
        static void TestDay()
        {
            SessionState.SetBool(VoyageGame.TestDayKey, true);
            if (!EditorApplication.isPlaying) { EditorApplication.isPlaying = true; return; }
            EditorApplication.playModeStateChanged += Again;
            EditorApplication.isPlaying = false;
        }

        static void Again(PlayModeStateChange change)
        {
            if (change != PlayModeStateChange.EnteredEditMode) return;
            EditorApplication.playModeStateChanged -= Again;
            EditorApplication.isPlaying = true;
        }
    }
}

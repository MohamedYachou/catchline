using UnityEngine;

namespace Catchline.Game
{
    // A resource keeps the imported clips/atlas referenced in both player builds.
    public sealed class RodViewArt : ScriptableObject
    {
        public GameObject Model;
        public Texture2D Atlas;
        public AnimationClip[] Clips;
        public AnimationClip Clip(string name)
        {
            if (Clips != null)
                foreach (var clip in Clips)
                    if (clip != null && (clip.name == name || clip.name.EndsWith("|" + name))) return clip;
            return null;
        }
    }
}

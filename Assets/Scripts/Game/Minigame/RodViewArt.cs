using UnityEngine;

namespace Catchline.Game
{
    // A resource keeps the imported clips/atlas referenced in both player builds.
    public sealed class RodViewArt : ScriptableObject
    {
        public GameObject Model;
        // The same rig with the sleeve and glove islands removed (Codex 2, FISH-ARMS-2 step 0); null in old imports.
        public GameObject RodOnly;
        public Texture2D Atlas;
        public AnimationClip[] Clips;
        // FISH-POLISH-1 item 1: the view ships rod-only (the reel turns by itself) until the remade arms pass review.
        public bool UseArms;
        static readonly string[] ArmBones = { "GripHand.L", "ReelHand.R" };

        // A copy of the skinned mesh without the triangles that ride on the hand bones (gloves and sleeves).
        public static Mesh WithoutArms(SkinnedMeshRenderer skin)
        {
            var source = skin.sharedMesh;
            if (source == null || !source.isReadable) return null;
            var arm = new System.Collections.Generic.HashSet<int>();
            for (int b = 0; b < skin.bones.Length; b++)
                if (skin.bones[b] != null && System.Array.IndexOf(ArmBones, skin.bones[b].name) >= 0) arm.Add(b);
            if (arm.Count == 0) return null;
            var weights = source.boneWeights;
            bool OnArm(int v)
            {
                var w = weights[v]; float a = 0;
                if (arm.Contains(w.boneIndex0)) a += w.weight0; if (arm.Contains(w.boneIndex1)) a += w.weight1;
                if (arm.Contains(w.boneIndex2)) a += w.weight2; if (arm.Contains(w.boneIndex3)) a += w.weight3;
                return a > .5f;
            }
            var mesh = Instantiate(source); mesh.name = source.name + " (rod only)";
            for (int s = 0; s < mesh.subMeshCount; s++)
            {
                var tris = mesh.GetTriangles(s); var keep = new System.Collections.Generic.List<int>(tris.Length);
                for (int i = 0; i < tris.Length; i += 3)
                    if (!OnArm(tris[i]) && !OnArm(tris[i + 1]) && !OnArm(tris[i + 2])) { keep.Add(tris[i]); keep.Add(tris[i + 1]); keep.Add(tris[i + 2]); }
                mesh.SetTriangles(keep, s);
            }
            return mesh;
        }
        public AnimationClip Clip(string name)
        {
            if (Clips != null)
                foreach (var clip in Clips)
                    if (clip != null && (clip.name == name || clip.name.EndsWith("|" + name))) return clip;
            return null;
        }
    }
}

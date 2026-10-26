using UnityEngine;

namespace Catchline.Game
{
    // Life on the Seal skerries (MAP6-SKERRIES-1, art SKERRIES-LIFE-1): the map's anchor empties get a seal colony with
    // one basking seal that now and then looks round, surf patches that breathe on the reefs and the crab buoy set.
    // Anchors the map does not have are simply skipped.
    public partial class VoyageGame
    {
        void DressSkerries(GameObject environment, ArtLibrary lib)
        {
            if (DressGullCoastLife(environment, lib)) return;
            int reef = 0;
            foreach (var t in environment.GetComponentsInChildren<Transform>())
            {
                if (t.name.StartsWith("SealColony_"))
                {
                    Spawn(lib.M("SealColony"), t, Vector3.zero);
                    var seal = Spawn(lib.M("Seal"), t, new Vector3(1.4f, 0, -.6f));
                    if (seal != null) seal.AddComponent<SealLife>().Bark = () => audio?.Play(VoyageAudio.Cue.SealBark, .16f);
                }
                else if (t.name.StartsWith("ReefBreak_"))
                {
                    var surf = Spawn(lib.M(reef++ % 2 == 0 ? "ReefBreak_A" : "ReefBreak_B"), t, Vector3.zero);
                    if (surf != null) surf.AddComponent<SurfPulse>().Phase = reef * 1.7f;
                }
                else if (t.name.StartsWith("CrabBuoy_")) Spawn(lib.M("CrabBuoySet"), t, Vector3.zero);
                else DressWreck(t, environment.transform.position.y, lib);
            }
        }

        static GameObject Spawn(GameObject prefab, Transform at, Vector3 offset) =>
            prefab == null ? null : ArtLibrary.Spawn(prefab, at, offset, Quaternion.identity);
    }

    // Basks on a loop and looks round every so often (the Seal's legacy clips Bask and Look), sometimes with a bark.
    public sealed class SealLife : MonoBehaviour
    {
        public System.Action Bark;
        Animation clips; float nextLook;
        void Start()
        {
            clips = GetComponentInChildren<Animation>();
            if (clips == null) { enabled = false; return; }
            foreach (AnimationState s in clips) s.wrapMode = WrapMode.Loop;
            Play("Bask");
            nextLook = Time.time + Random.Range(5f, 12f);
        }
        void Update()
        {
            if (Time.time < nextLook) return;
            nextLook = Time.time + Random.Range(8f, 16f);
            if (Play("Look")) clips.CrossFadeQueued(Name("Bask"), .4f);
            if (Random.value < .4f) Bark?.Invoke();
        }
        string Name(string part) { foreach (AnimationState s in clips) if (s.name.Contains(part)) return s.name; return null; }
        bool Play(string part) { var n = Name(part); if (n == null) return false; clips.CrossFade(n, .4f); return true; }
    }

    // Broken water over a reef: swells and settles as the waves pass.
    public sealed class SurfPulse : MonoBehaviour
    {
        public float Phase;
        Vector3 rest;
        void Start() => rest = transform.localScale;
        void Update()
        {
            float w = Mathf.Sin(Time.time * 1.3f + Phase);
            transform.localScale = new Vector3(rest.x * (1 + .08f * w), rest.y, rest.z * (1 + .12f * Mathf.Max(0, w)));
        }
    }
}

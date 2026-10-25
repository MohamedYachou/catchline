using UnityEngine;

namespace Catchline.Game
{
    // Life at Lighthouse rock (MAP8, art LIGHTHOUSE-LIFE-1): puffins on the ledges (one of them alive, bobbing and now
    // and then flapping), standing waves in the tide race and the lamp's beam sweeping round. The cardinal buoy is
    // the wreck bank's (DressWreck). Anchors the map does not have are simply skipped.
    public partial class VoyageGame
    {
        const float PuffinScale = 2.2f;
        static Material glowMaterial;

        void DressLighthouse(Transform anchor, float waterY, ArtLibrary lib)
        {
            var water = new Vector3(anchor.position.x, waterY, anchor.position.z);
            if (anchor.name.StartsWith("PuffinLedge_"))
            {
                int n = anchor.GetSiblingIndex();
                // Drawn larger than life (as the gulls are) so they read from the boat.
                var group = Spawn(lib.M("PuffinGroup"), anchor, Vector3.zero);
                if (group != null) { group.transform.localScale *= PuffinScale; group.transform.Rotate(0, n * 70, 0); }
                var puffin = Spawn(lib.M("Puffin"), anchor, new Vector3(.75f, 0, -.35f) * PuffinScale);
                if (puffin != null) { puffin.transform.localScale *= PuffinScale; puffin.transform.Rotate(0, 200 + n * 40, 0); puffin.AddComponent<PuffinLife>(); }
            }
            else if (anchor.name.StartsWith("TideRace_"))
            {
                var race = Spawn(lib.M("TideRace"), anchor, Vector3.zero);
                if (race == null) return;
                race.transform.position = water + Vector3.up * .02f;
                race.AddComponent<TideRaceDrift>().Phase = anchor.GetSiblingIndex() * 1.9f;
            }
            else if (anchor.name.StartsWith("LighthouseLamp_"))
            {
                var glow = Spawn(lib.M("LighthouseGlow"), anchor, Vector3.zero);
                if (glow == null) return;
                if (glowMaterial == null)
                {
                    var shader = Resources.Load<Shader>("Shaders/GlowAdditive");
                    if (shader != null) glowMaterial = new Material(shader) { name = "LampGlow" };
                }
                foreach (var r in glow.GetComponentsInChildren<Renderer>())
                {
                    r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; r.receiveShadows = false;
                    if (glowMaterial != null) r.sharedMaterial = glowMaterial;
                }
                glow.AddComponent<BeamSweep>();
            }
        }
    }

    // Stands on the ledge bobbing (Idle) and every so often flaps its wings for a moment (Flap).
    public sealed class PuffinLife : MonoBehaviour
    {
        Animation clips; float nextFlap, flapUntil;
        void Start()
        {
            clips = GetComponentInChildren<Animation>();
            if (clips == null) { enabled = false; return; }
            foreach (AnimationState s in clips) s.wrapMode = WrapMode.Loop;
            Play("Idle", 0); foreach (AnimationState s in clips) s.time = Random.Range(0, s.length);
            nextFlap = Time.time + Random.Range(4f, 10f);
        }
        void Update()
        {
            if (flapUntil > 0 && Time.time > flapUntil) { flapUntil = 0; Play("Idle", .25f); }
            if (Time.time < nextFlap) return;
            nextFlap = Time.time + Random.Range(7f, 15f);
            if (Play("Flap", .15f)) flapUntil = Time.time + Random.Range(.8f, 1.6f);
        }
        bool Play(string part, float fade)
        {
            foreach (AnimationState s in clips) if (s.name.EndsWith(part)) { clips.CrossFade(s.name, fade); return true; }
            return false;
        }
    }

    // Standing waves hold their place against the stream: the crests shuffle a little and breathe.
    public sealed class TideRaceDrift : MonoBehaviour
    {
        public float Phase;
        Vector3 rest, restScale;
        void Start() { rest = transform.localPosition; restScale = transform.localScale; }
        void Update()
        {
            float t = Time.time + Phase;
            transform.localPosition = rest + transform.localRotation * new Vector3(.25f * Mathf.Sin(t * .9f), .03f * Mathf.Sin(t * 2.1f), 0);
            float w = Mathf.Sin(t * 1.6f);
            transform.localScale = new Vector3(restScale.x, restScale.y * (1 + .25f * w), restScale.z * (1 + .05f * w));
        }
    }

    // The lighthouse beam turns once every twelve seconds.
    public sealed class BeamSweep : MonoBehaviour
    {
        void Update() => transform.Rotate(0, 30f * Time.deltaTime, 0, Space.World);
    }
}

using UnityEngine;

namespace Catchline.Game
{
    // Life on the Wreck bank (MAP7-WRECK-BANK-1, art WRECK-LIFE-1): gannets circle over the herring boils and now and
    // then fold up and dive, gulls sit on the wreck and a cardinal buoy rides beside it. Called for every anchor the
    // environment has; anchors a map does not have are simply skipped.
    public partial class VoyageGame
    {
        void DressWreck(Transform anchor, float waterY, ArtLibrary lib)
        {
            var water = new Vector3(anchor.position.x, waterY, anchor.position.z);
            if (anchor.name.StartsWith("GannetDive_"))
            {
                var boil = Spawn(lib.M("HerringBoil"), anchor, Vector3.zero);
                if (boil != null) { boil.transform.position = water + Vector3.up * .01f; boil.AddComponent<SurfPulse>().Phase = anchor.GetSiblingIndex() * 2.3f; }
                var bird = Spawn(lib.M("Gannet"), anchor, Vector3.zero);
                if (bird == null) return;
                var dive = bird.AddComponent<GannetDive>();
                dive.Water = water; dive.Splash = Spawn(lib.M("DiveSplash"), anchor, Vector3.zero);
                dive.Plunge = () => audio?.Play(VoyageAudio.Cue.Splash, .1f);
            }
            else if (anchor.name.StartsWith("WreckGulls_"))
            {
                var gull = lib.M("Seagull");
                if (gull == null) return;
                // Three on the rusted rail, facing about the same way.
                for (int i = 0; i < 3; i++)
                    Spawn(gull, anchor, new Vector3((i - 1) * .55f, 0, i == 1 ? .15f : 0))?.transform.Rotate(0, 170 + i * 25, 0);
                foreach (Transform t in anchor) if (t.name == gull.name) t.gameObject.AddComponent<Gull>();
            }
            else if (anchor.name.StartsWith("CardinalBuoy_"))
            {
                var buoy = Spawn(lib.M("CardinalBuoy"), anchor, Vector3.zero);
                if (buoy != null) { buoy.transform.position = water; buoy.AddComponent<BuoyBob>(); }
            }
        }
    }

    // A gannet circling high over a herring boil (the Gannet's legacy clips Glide and Dive). Every so often it folds
    // and drops onto the boil; a splash bursts where it goes in, and a while later it is back up circling.
    public sealed class GannetDive : MonoBehaviour
    {
        public Vector3 Water;
        public GameObject Splash;
        public System.Action Plunge;
        const float Height = 7, Radius = 3.2f, DropSeconds = 1.1f;
        Animation clips; Renderer[] skin;
        float angle, nextDive, diveAge = -1, splashAge = -1, awayUntil = -1;
        Vector3 diveFrom;

        void Start()
        {
            clips = GetComponentInChildren<Animation>();
            skin = GetComponentsInChildren<Renderer>();
            if (clips != null) foreach (AnimationState s in clips) s.wrapMode = s.name.Contains("Dive") ? WrapMode.ClampForever : WrapMode.Loop;
            angle = Random.Range(0, 360f);
            nextDive = Time.time + Random.Range(5f, 14f);
            if (Splash != null) Splash.SetActive(false);
            Play("Glide");
        }

        void Update()
        {
            float dt = Time.deltaTime;
            UpdateSplash(dt);
            if (awayUntil > 0)
            {
                if (Time.time < awayUntil) return;
                awayUntil = -1; Show(true); Play("Glide");
                nextDive = Time.time + Random.Range(7f, 16f);
            }
            if (diveAge >= 0)
            {
                // Falls with gravity's ease-in onto the boil, the clip folding the wings meanwhile.
                diveAge += dt;
                float t = Mathf.Clamp01(diveAge / DropSeconds);
                transform.position = Vector3.Lerp(diveFrom, Water, t * t);
                if (t >= 1)
                {
                    diveAge = -1; Show(false); awayUntil = Time.time + Random.Range(2.5f, 5f);
                    splashAge = 0; Plunge?.Invoke();
                }
                return;
            }
            // Circling: the clip holds the wings set; the turn and a slight bank come from here.
            angle += dt * 26;
            var round = Quaternion.Euler(0, angle, 0);
            transform.position = Water + round * new Vector3(Radius, Height, 0);
            transform.rotation = round * Quaternion.Euler(0, 0, 12); // flying the +Z tangent, banked into the turn
            if (Time.time > nextDive) { diveAge = 0; diveFrom = transform.position; Play("Dive"); }
        }

        void UpdateSplash(float dt)
        {
            if (Splash == null || splashAge < 0) return;
            splashAge += dt;
            Splash.SetActive(splashAge < .9f);
            Splash.transform.position = Water;
            float up = Mathf.Clamp01(splashAge / .12f), down = Mathf.Clamp01((splashAge - .25f) / .65f);
            Splash.transform.localScale = new Vector3(1 + down * .4f, Mathf.Max(.01f, up * (1 - down)), 1 + down * .4f);
            if (splashAge >= .9f) splashAge = -1;
        }

        void Show(bool on) { foreach (var r in skin) if (r != null) r.enabled = on; }
        void Play(string part)
        {
            if (clips == null) return;
            foreach (AnimationState s in clips) if (s.name.Contains(part)) { clips.Stop(); clips.Play(s.name); return; }
        }
    }

    // A buoy riding the swell: a gentle rise and fall with a slow lean.
    public sealed class BuoyBob : MonoBehaviour
    {
        Vector3 rest; Quaternion restRotation; float phase;
        void Start() { rest = transform.localPosition; restRotation = transform.localRotation; phase = Random.Range(0, 6f); }
        void Update()
        {
            float t = Time.time + phase;
            transform.localPosition = rest + Vector3.up * (.06f * Mathf.Sin(t * 1.4f));
            transform.localRotation = restRotation * Quaternion.Euler(3.5f * Mathf.Sin(t * 1.1f), 0, 2.5f * Mathf.Sin(t * .8f + 1));
        }
    }
}

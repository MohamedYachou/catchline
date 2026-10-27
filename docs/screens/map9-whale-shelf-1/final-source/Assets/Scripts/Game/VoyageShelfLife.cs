using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    // Life on the Whale shelf (MAP9): whales passing along the whale road blow a spout and then show their tail. The
    // shelf's gannets, buoy and gulls use the wreck bank's dispatch. Anchors the map does not have are simply skipped.
    public partial class VoyageGame
    {
        void DressShelf(Transform anchor, float waterY, ArtLibrary lib)
        {
            if (!anchor.name.StartsWith("WhaleSpout_")) return;
            var water = new Vector3(anchor.position.x, waterY, anchor.position.z);
            var tail = Spawn(lib.M("WhaleTail"), anchor, Vector3.zero);
            if (tail != null) { tail.transform.position = water; tail.transform.Rotate(0, anchor.GetSiblingIndex() * 55, 0); tail.AddComponent<WhaleTail>(); }
            var spout = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            Visuals.Kill(spout.GetComponent<Collider>());
            spout.name = "Whale spout"; spout.transform.SetParent(anchor, false); spout.transform.position = water + new Vector3(1.2f, 0, 0);
            var r = spout.GetComponent<Renderer>(); r.sharedMaterial = Visuals.Mat(Palette.Hex("EEF3F2")); r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
            spout.AddComponent<WhaleSpout>().Phase = anchor.GetSiblingIndex() * 7f;
        }
    }

    // A whale's blow: a white column shoots up, spreads at the top and falls back over about two seconds.
    public sealed class WhaleSpout : MonoBehaviour
    {
        public float Phase;
        float next, t = -1;
        Vector3 water;
        void Start() { water = transform.localPosition; next = Time.time + 3 + Phase; transform.localScale = Vector3.zero; }
        void Update()
        {
            if (t < 0) { if (Time.time < next) return; t = 0; }
            t += Time.deltaTime;
            float rise = Mathf.Clamp01(t / .35f), fall = Mathf.Clamp01((t - .9f) / 1.1f);
            float height = 2.6f * rise * (1 - fall * fall), width = Mathf.Lerp(.25f, .9f, Mathf.Clamp01(t / 1.2f)) * (1 - fall);
            transform.localScale = new Vector3(width, height, width);
            transform.localPosition = water + Vector3.up * height * .5f;
            if (t > 2) { t = -1; transform.localScale = Vector3.zero; next = Time.time + Random.Range(14f, 30f); }
        }
    }
}

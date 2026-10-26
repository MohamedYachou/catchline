using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        void DressCliffs(Transform anchor, float waterY, ArtLibrary lib)
        {
            var map = anchor;
            while (map != null && !map.name.Contains("GullSealCliffs")) map = map.parent;
            if (map == null) { DressKelp(anchor, waterY, lib); return; }
            if (anchor.name.StartsWith("SealHaulout_")) CliffsSeals(anchor, lib);
            else if (anchor.name.StartsWith("CliffGulls_")) CliffsGulls(anchor, lib);
            else if (anchor.name.StartsWith("ArchSpray_"))
            {
                var spray = Spawn(lib.M("DiveSplash"), anchor, Vector3.zero);
                if (spray != null)
                {
                    spray.transform.position = new Vector3(anchor.position.x, waterY, anchor.position.z);
                    spray.AddComponent<CliffSpray>();
                }
            }
            // These existing low ledges are the cliffs' foreground at each ground.
            // Their tops, rather than floating offsets, support the close-camera life.
            else if (anchor.name.StartsWith("Terrain_CornerRock_"))
            {
                var mesh = anchor.GetComponent<MeshFilter>();
                if (mesh == null || mesh.sharedMesh == null) return;
                var bounds = anchor.GetComponent<Renderer>().bounds;
                // MAP10 authoring: crown centre .52 + .18*.6 above the map root.
                // Bounds stay available in a player without enabling CPU mesh copies.
                var surface = new Vector3(bounds.center.x, waterY + .628f, bounds.center.z);
                var perch = new GameObject("Cliffs foreground perch").transform;
                perch.SetParent(anchor, false); perch.position = surface;
                // A single seal and two gulls keep the narrow ledge readable.
                var seal = Spawn(lib.M("Seal"), perch, Vector3.zero);
                if (seal != null) seal.AddComponent<SealLife>().Bark = RareCliffsBark;
                CliffsGulls(perch, lib);
            }
        }

        void RareCliffsBark() { if (Random.value < .15f) audio?.Play(VoyageAudio.Cue.SealBark, .1f); }
        void CliffsSeals(Transform anchor, ArtLibrary lib)
        {
            Spawn(lib.M("SealColony"), anchor, Vector3.zero);
            var seal = Spawn(lib.M("Seal"), anchor, new Vector3(1.4f, 0, -.6f));
            if (seal != null) seal.AddComponent<SealLife>().Bark = RareCliffsBark;
        }
        static void CliffsGulls(Transform anchor, ArtLibrary lib)
        {
            for (int i = 0; i < 2; i++)
            {
                var gull = Spawn(lib.M("Seagull"), anchor, new Vector3((i == 0 ? -1 : 1) * .65f, 0, .25f));
                if (gull != null) { gull.transform.Rotate(0, 160 + i * 35, 0); gull.AddComponent<Gull>(); }
            }
        }


    }

    // Reuses the existing white gannet splash; a short burst between long quiet gaps.
    public sealed class CliffSpray : MonoBehaviour
    {
        Vector3 restScale; Renderer[] skin; float age = -1, next;
        void Start()
        {
            restScale = transform.localScale; skin = GetComponentsInChildren<Renderer>();
            Show(false); next = Time.time + Random.Range(2f, 5f);
        }
        void Update()
        {
            if (age < 0) { if (Time.time < next) return; age = 0; Show(true); }
            age += Time.deltaTime;
            float rise = Mathf.Clamp01(age / .14f), fall = Mathf.Clamp01((age - .25f) / .8f);
            transform.localScale = Vector3.Scale(restScale, new Vector3(1 + fall * .5f, Mathf.Max(.01f, rise * (1 - fall)), 1 + fall * .5f));
            if (age < 1.05f) return;
            age = -1; Show(false); next = Time.time + Random.Range(7f, 14f);
        }
        void Show(bool visible) { foreach (var r in skin) if (r != null) r.enabled = visible; }
    }
}

using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        void DressKelp(Transform anchor, float waterY, ArtLibrary lib)
        {
            var map = anchor;
            while (map != null && !map.name.Contains("GullKelpForest")) map = map.parent;
            if (map == null) return;
            if (anchor.name.StartsWith("KelpSway_"))
            {
                // Only this bay's material instance: shared PTS shader and other
                // maps retain their optics. Green-teal shallows show the warm bed.
                if (anchor.name == "KelpSway_1" && seaMat != null)
                {
                    var optics = map.gameObject.AddComponent<KelpBayOptics>();
                    optics.Game = this; optics.Water = seaMat; optics.Apply();
                }
                var patch = ArtLibrary.Find(map.gameObject, "RootedForestPatch_" + anchor.name);
                if (patch == null) return;
                var pivot = new GameObject("Kelp root sway " + anchor.name).transform;
                pivot.SetParent(map, false);
                pivot.position = anchor.position - map.up * 1.15f;
                pivot.rotation = map.rotation;
                patch.SetParent(pivot, true);
                var sway = pivot.gameObject.AddComponent<KelpRootSway>();
                sway.Period = 4f + (anchor.name[anchor.name.Length - 1] - '1');
                sway.Phase = (anchor.name[anchor.name.Length - 1] - '1') * 1.7f;
            }
            else if (anchor.name.StartsWith("PostGulls_")) CliffsGulls(anchor, lib);
            else if (anchor.name == "OtterRaft_1")
            {
                // Static raft delivered by Codex 2; retain the supplied fallback
                // for builds whose art library predates that optional model.
                var otters = Spawn(lib.M("OtterRaft"), anchor, Vector3.zero);
                if (otters != null)
                {
                    otters.name = "Otter raft";
                    otters.transform.position = new Vector3(anchor.position.x, waterY, anchor.position.z);
                    otters.AddComponent<KelpRaftSkin>().Bind();
                    otters.AddComponent<Floater>().Amp = .025f;
                    return;
                }
                var raft = new GameObject("Kelp raft (gull fallback)").transform;
                raft.SetParent(anchor, false);
                raft.position = new Vector3(anchor.position.x, waterY + .025f, anchor.position.z);
                Spawn(lib.M("KelpForest") ?? lib.Kelp, raft, Vector3.zero);
                CliffsGulls(raft, lib);
                raft.gameObject.AddComponent<Floater>().Amp = .025f;
            }
        }
    }

    // The new palette stays local to this model. Thin raft ribbons render from
    // both sides; dispose these bounded, spawn-time material instances with it.
    public sealed class KelpRaftSkin : MonoBehaviour
    {
        readonly System.Collections.Generic.List<Material> owned = new();
        public void Bind()
        {
            foreach (var renderer in GetComponentsInChildren<Renderer>())
            {
                var materials = renderer.sharedMaterials;
                for (int i = 0; i < materials.Length; i++)
                {
                    var source = materials[i];
                    if (source == null) continue;
                    string name = source.name;
                    string hex = name.Contains("M_OtterBrown") ? "705040"
                        : name.Contains("M_OtterCream") ? "C8C3AF"
                        : name.Contains("M_OtterPaw") ? "50392E"
                        : name.Contains("M_KelpGreen") ? "3D573B"
                        : name.Contains("M_KelpGold") ? "536D3D"
                        : name.Contains("M_KelpBulb") ? "8C7949" : null;
                    var material = new Material(Shader.Find("Universal Render Pipeline/Lit")) {
                        name = "Kelp raft " + name,
                        color = hex != null ? Palette.Hex(hex) : source.color
                    };
                    material.SetFloat("_Smoothness", .2f);
                    material.SetFloat("_Cull", 0);
                    owned.Add(material); materials[i] = material;
                }
                renderer.sharedMaterials = materials;
            }
        }
        void OnDestroy()
        {
            foreach (var material in owned)
                if (Application.isPlaying) Destroy(material); else DestroyImmediate(material);
        }
    }

    // A map-local material override. Arrival/relocation reset the generic biome;
    // reapply only while this map is the active navigation environment.
    public sealed class KelpBayOptics : MonoBehaviour
    {
        public VoyageGame Game;
        public Material Water;
        // Preserve warm sand at shallow depth; green scattering supplies the
        // water tint as depth increases. A green-biased transmission made the
        // pale bed uniformly sage instead of exposing the warm source palette.
        static readonly Vector4 Transmission = new Vector4(.86f, .84f, .74f, 1);
        static readonly Color Shallows = Palette.Hex("3A8F86").linear;
        public void Apply()
        {
            if (Water == null || !Water.HasProperty("_AbsorptionColor")) return;
            Water.SetVector("_AbsorptionColor", Transmission);
            Water.SetColor("_ScatteringColor", Shallows);
        }
        void LateUpdate()
        {
            if (Game == null || Game.Navigation == null || Game.Navigation.ModelId != "GullKelpForestSeaV2") return;
            if (Water != null && Water.HasProperty("_AbsorptionColor") && Water.GetVector("_AbsorptionColor") != Transmission) Apply();
        }
    }

    // Cached rest pose; quaternion/value math only, with no per-frame allocation.
    public sealed class KelpRootSway : MonoBehaviour
    {
        public float Period = 5f, Phase;
        Quaternion rest = Quaternion.identity;
        void Awake() { rest = transform.localRotation; }
        public Quaternion Pose(float time) => rest * Quaternion.Euler(
            Mathf.Sin(time * (2f * Mathf.PI / Period) + Phase) * 1.2f, 0,
            Mathf.Sin(time * (2f * Mathf.PI / Period) + Phase + .8f) * .8f);
        void Update() { transform.localRotation = Pose(Time.time); }
    }
}

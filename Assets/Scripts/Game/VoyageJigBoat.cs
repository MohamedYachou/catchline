using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public bool IsJigBoat => State != null && State.Hull == 5;
        Transform jigGlow;
        Transform jigPool;
        Material jigBulb;
        public bool JigLampsLit { get; private set; }

        public bool RefitJig()
        {
            if (CurrentMode != Mode.Harbour || !State.RefitJig()) return false;
            RebuildBoat(); BeginRefitFx(); audio?.Play(VoyageAudio.Cue.RefitFanfare, .35f);
            Toast("Jig boat ready: 130 kg hold, five crew berths and three jig reels. First tank included.");
            SaveGame(); return true;
        }

        void ConfigureJigBoat(GameObject model)
        {
            jigGlow = jigPool = null; jigBulb = null;
            // The delivered panel has an origin at the boat root, not a hinge.
            // Give the existing lid animation a measured edge pivot without changing the imported mesh.
            var panel = ArtLibrary.Find(model, "HoldHatchLid");
            var hatchMesh = panel != null ? panel.GetComponent<MeshFilter>() : null;
            if (hatchMesh != null && hatchMesh.sharedMesh != null)
            {
                var bounds = hatchMesh.sharedMesh.bounds;
                var matrix = Boat.worldToLocalMatrix * panel.localToWorldMatrix;
                var deckBounds = new Bounds(matrix.MultiplyPoint3x4(bounds.min), Vector3.zero);
                foreach (float x in new[] { bounds.min.x, bounds.max.x })
                    foreach (float y in new[] { bounds.min.y, bounds.max.y })
                        foreach (float z in new[] { bounds.min.z, bounds.max.z })
                            deckBounds.Encapsulate(matrix.MultiplyPoint3x4(new Vector3(x,y,z)));
                var hinge = new GameObject("HoldHatchLid").transform;
                hinge.SetParent(panel.parent, false);
                hinge.position = Boat.TransformPoint(new Vector3(deckBounds.center.x, deckBounds.min.y, deckBounds.min.z));
                hinge.rotation = Boat.rotation;
                panel.name = "Jig hatch panel"; panel.SetParent(hinge, true);
                compactLidRest = hinge.localRotation;
            }
            var owned = model.AddComponent<JigRuntimeMaterials>();
            foreach (var r in model.GetComponentsInChildren<Renderer>())
            {
                var mats = r.sharedMaterials;
                for (int i = 0; i < mats.Length; i++)
                    if (mats[i] != null && mats[i].name.Contains("M_JigBulb"))
                    {
                        jigBulb ??= owned.Own(new Material(mats[i]));
                        jigBulb.EnableKeyword("_EMISSION"); mats[i] = jigBulb;
                    }
                r.sharedMaterials = mats;
            }
            var prefab = ArtLibrary.Get()?.M("JigLampGlow");
            if (prefab != null)
            {
                var fx = Instantiate(prefab, model.transform.parent);
                fx.name = "Jig lamp glow";
                fx.transform.localPosition = model.transform.localPosition;
                fx.transform.localRotation = Quaternion.Euler(0,-90,0) * prefab.transform.localRotation;
                fx.transform.localScale = prefab.transform.localScale;
                jigGlow = fx.transform;
                var shader = Resources.Load<Shader>("Shaders/GlowAdditive");
                foreach (var r in fx.GetComponentsInChildren<Renderer>())
                {
                    bool pool = r.name == "WaterLightPool";
                    var m = owned.Own(new Material(shader));
                    m.SetColor("_Color", Palette.Hex(pool ? "CFEFC0" : "FFE7A3"));
                    m.SetFloat("_Strength", pool ? .24f : .6f);
                    r.sharedMaterial = m; r.shadowCastingMode = ShadowCastingMode.Off; r.receiveShadows = false;
                    if (pool) jigPool = r.transform;
                }
            }
            UpdateJigLamps();
        }

        void UpdateJigLamps()
        {
            JigLampsLit = IsJigBoat && (duskBlend > .1f || State.NightVoyage || CurrentMode == Mode.Fishing && AtFishingGround);
            if (jigGlow != null) jigGlow.gameObject.SetActive(JigLampsLit);
            if (jigBulb != null) jigBulb.SetColor("_EmissionColor", JigLampsLit ? Palette.Hex("FFE7A3") * 1.3f : Color.black);
            // The effect's authored pool is horizontal; follow the actual sea plane rather than boat bobbing.
            if (jigPool != null)
            {
                var p = jigPool.position; p.y = WaterY + .01f; jigPool.position = p;
            }
        }
    }

    sealed class JigRuntimeMaterials : MonoBehaviour
    {
        readonly List<Material> materials = new();
        public Material Own(Material material) { materials.Add(material); return material; }
        void OnDestroy()
        {
            foreach (var material in materials)
                if (material != null)
                    if (Application.isPlaying) Destroy(material); else DestroyImmediate(material);
        }
    }
}

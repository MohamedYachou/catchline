using System;
using UnityEngine;
using UnityEngine.Rendering;

namespace Catchline.Game
{
    /// <summary>
    /// Authored fish silhouette, independent of fishing rules and saves. Place the root at
    /// the water surface; +Z is the nose. Depth moves only the visual below that root.
    /// The URP camera must supply its opaque depth texture (Copy Depth: After Opaques).
    /// </summary>
    [ExecuteAlways]
    public sealed class FishShadow : MonoBehaviour
    {
        [SerializeField, Range(0, 1)] float depth = .2f;
        [SerializeField, Range(0, 1)] float visibility = 1;
        [SerializeField] Shader silhouetteShader;
        public float Depth { get => depth; set { depth = Unit(value); ApplyVisual(); } }
        public float Visibility { get => visibility; set { visibility = Unit(value); ApplyVisual(); } }
        public Species Species { get; private set; }
        public float Kg { get; private set; }
        public float Length { get; private set; }
        public bool IsSwimming => hasTarget || dartRemaining > 0;
        public bool AutomaticAdvance { get; set; } = true;
        public GameObject Model { get; private set; }

        Transform visual;
        Renderer[] renderers;
        Material material;
        MaterialPropertyBlock properties;
        Bounds modelBounds;
        Vector3 target, dartDirection;
        float speed, dartRemaining, phase;
        bool hasTarget;
        static float Unit(float n) => float.IsFinite(n) ? Mathf.Clamp01(n) : 0;
        static bool Finite(Vector3 v) => float.IsFinite(v.x) && float.IsFinite(v.y) && float.IsFinite(v.z);

        /// <summary>GameData.Length is the midpoint specimen length, in game-world metres.
        /// Similar shapes scale with the cube root of mass; outliers clamp to the species range.</summary>
        public static float LengthFor(Species species, float kg)
        {
            var d = GameData.Get(species);
            if (!float.IsFinite(kg) || kg <= 0) throw new ArgumentOutOfRangeException(nameof(kg));
            return d.Length * Mathf.Pow(Mathf.Clamp(kg, d.MinKg, d.MaxKg) / ((d.MinKg + d.MaxKg) * .5f), 1f / 3f);
        }

        public void Initialize(Species species, float kg, ArtLibrary library = null)
        {
            float length = LengthFor(species, kg);
            library = library != null ? library : ArtLibrary.Get();
            var prefab = library != null ? library.FishFor(species) ?? library.M(species.ToString()) : null;
            if (prefab == null) throw new InvalidOperationException("FishShadow: missing ArtLibrary model for " + species);
            var shader = silhouetteShader != null ? silhouetteShader : Resources.Load<Shader>("FishShadow");
            if (shader == null || !shader.isSupported) throw new InvalidOperationException("FishShadow: supported silhouette shader required");
            ClearVisual();
            Species = species; Kg = kg; Length = length;
            phase = 0; hasTarget = false; dartRemaining = 0;
            visual = new GameObject("Submerged visual").transform;
            visual.SetParent(transform, false);
            Model = Instantiate(prefab, visual, false);
            Model.name = prefab.name;
            // Retain original mesh topology and all fins. No generated fish proxy or mesh mutation.
            foreach (var c in Model.GetComponentsInChildren<Collider>(true)) Dispose(c);
            foreach (var a in Model.GetComponentsInChildren<Animator>(true)) a.enabled = false;
            foreach (var a in Model.GetComponentsInChildren<Animation>(true)) a.enabled = false;
            Model.transform.localPosition = Vector3.zero;
            Model.transform.localRotation = Quaternion.identity;
            Model.transform.localScale = Vector3.one;
            var nose = ArtLibrary.Find(Model, "Nose");
            var tail = ArtLibrary.Find(Model, "TailEnd");
            if (nose != null && tail != null)
            {
                var heading = Model.transform.InverseTransformVector(nose.position - tail.position);
                Model.transform.localRotation = Quaternion.FromToRotation(heading, Vector3.forward);
            }
            else ArtLibrary.AimAlong(Model, Vector3.forward, 1);
            renderers = Model.GetComponentsInChildren<Renderer>(true);
            Bounds b = BoundsInVisual();
            if (renderers.Length == 0 || b.size.z < .00001f)
            {
                ClearVisual();
                throw new InvalidOperationException("FishShadow: empty model " + species);
            }
            float scale = Length / b.size.z;
            Model.transform.localScale *= scale;
            Model.transform.localPosition = -b.center * scale;
            modelBounds = BoundsInVisual();
            material = new Material(shader) { name = "FishShadow (owned instance)", hideFlags = HideFlags.DontSave };
            properties = new MaterialPropertyBlock();
            foreach (var r in renderers)
            {
                var mats = new Material[r.sharedMaterials.Length];
                Array.Fill(mats, material); r.sharedMaterials = mats;
                r.shadowCastingMode = ShadowCastingMode.Off; r.receiveShadows = false;
                r.lightProbeUsage = LightProbeUsage.Off; r.reflectionProbeUsage = ReflectionProbeUsage.Off;
                // CPU culling must include the GPU tail wave.
                var bounds = r.localBounds;
                bounds.Expand(bounds.size.magnitude * .3f); r.localBounds = bounds;
            }
            ApplyVisual();
        }

        Bounds BoundsInVisual()
        {
            Bounds result = default; bool any = false;
            foreach (var r in renderers)
            {
                var matrix = visual.worldToLocalMatrix * r.transform.localToWorldMatrix;
                var b = r.localBounds;
                for (int i = 0; i < 8; i++)
                {
                    var p = matrix.MultiplyPoint3x4(b.center + Vector3.Scale(b.extents,
                        new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1)));
                    if (!any) { result = new Bounds(p, Vector3.zero); any = true; } else result.Encapsulate(p);
                }
            }
            return result;
        }

        public void SwimTo(Vector3 worldPos, float metresPerSecond)
        {
            if (!Finite(worldPos) || !float.IsFinite(metresPerSecond) || metresPerSecond < 0)
                throw new ArgumentOutOfRangeException(nameof(worldPos));
            target = worldPos; speed = metresPerSecond;
            hasTarget = speed > 0 && (target - transform.position).sqrMagnitude > .000001f;
        }

        /// <summary>Short horizontal burst, then resume the previous SwimTo destination.</summary>
        public void Dart(Vector3 direction)
        {
            if (!Finite(direction)) throw new ArgumentOutOfRangeException(nameof(direction));
            direction.y = 0;
            if (direction.sqrMagnitude < .000001f) return;
            dartDirection = direction.normalized; dartRemaining = .32f;
        }

        void Update() { if (AutomaticAdvance && Application.IsPlaying(gameObject)) Advance(Time.deltaTime); }

        // Explicit clock for deterministic previews; caller need not run or alter voyage simulation.
        public void Advance(float dt)
        {
            if (!float.IsFinite(dt) || dt < 0) throw new ArgumentOutOfRangeException(nameof(dt));
            if (visual == null) return;
            Vector3 before = transform.position;
            if (dartRemaining > 0)
            {
                float step = Mathf.Min(dt, dartRemaining);
                transform.position += dartDirection * (Mathf.Max(Length * 4, 1.2f) * step);
                dartRemaining = Mathf.Max(0, dartRemaining - step);
                dt -= step;
            }
            if (hasTarget && dt > 0)
            {
                transform.position = Vector3.MoveTowards(transform.position, target, speed * dt);
                if ((transform.position - target).sqrMagnitude < .000001f) hasTarget = false;
            }
            var move = transform.position - before; move.y = 0;
            if (move.sqrMagnitude > .0000001f)
                transform.rotation = Quaternion.LookRotation(move.normalized, Vector3.up);
            float travel = Vector3.Distance(before, transform.position);
            phase += dt * 2.3f + travel / Mathf.Max(Length, .01f) * 11;
            ApplyVisual();
        }

        void LateUpdate() => ApplyVisual(); // property matrices follow a moving parent too
        void OnValidate() { depth = Unit(depth); visibility = Unit(visibility); ApplyVisual(); }
        void OnEnable() => ApplyVisual();
        void OnDisable() { if (renderers != null) foreach (var r in renderers) if (r != null) r.enabled = false; }

        void ApplyVisual()
        {
            if (visual == null || properties == null) return;
            // Clearance keeps the dorsal fin under calm water even for the largest model.
            visual.localPosition = Vector3.down * (.08f + modelBounds.extents.y + depth * 1.25f);
            properties.SetMatrix("_WorldToFish", visual.worldToLocalMatrix);
            properties.SetMatrix("_FishToWorld", visual.localToWorldMatrix);
            properties.SetFloat("_Length", Length);
            properties.SetFloat("_Phase", phase);
            properties.SetFloat("_Depth", depth);
            properties.SetFloat("_Visibility", visibility);
            foreach (var r in renderers)
                if (r != null) { r.enabled = isActiveAndEnabled && visibility > 0; r.SetPropertyBlock(properties); }
        }

        void OnDestroy() => ClearVisual();
        void ClearVisual()
        {
            // Remove old geometry immediately from rendering even with deferred Destroy.
            if (visual != null) { visual.gameObject.SetActive(false); Dispose(visual.gameObject); }
            if (material != null) Dispose(material);
            visual = null; Model = null; material = null; renderers = null; properties = null;
        }
        static void Dispose(UnityEngine.Object obj)
        { if (Application.isPlaying) Destroy(obj); else DestroyImmediate(obj); }
    }
}

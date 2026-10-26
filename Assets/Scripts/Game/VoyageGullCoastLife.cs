using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // SeaV2 positions are authored world X/Z metres. Never apply the small
        // fallback diorama's rotation or reserve-water displacement to these.
        bool DressGullCoastLife(GameObject environment, ArtLibrary lib)
        {
            int map = System.Array.FindIndex(Sea.SeaNav.Maps, n => environment.name.StartsWith(n + "SeaV2"));
            if (map < 0 || map > 4) return false;
            var root = new GameObject("Gull coast life").transform;
            root.SetParent(environment.transform, false);
            GameObject Place(string model, float x, float y, float z, float yaw = 0)
            {
                var go = Put(root, lib.M(model), new Vector3(x, y, z), yaw);
                if (go != null) go.AddComponent<GullCoastSkin>().Bind();
                return go;
            }
            if (map == 0 || map == 1)
            {
                var line = map == 0 ? Place("PotBuoyLine", -70, 0, 34, 15)
                    : Place("PotBuoyLine", -73, 0, -26, -25);
                if (line != null) line.AddComponent<GullCoastBob>();
            }
            else if (map == 2)
            {
                // Height measured on the native long-bar surface; the shallow
                // patch skirt joins the sand, while the four feet stay dry.
                var group = Place("OystercatcherGroup", -14, 0, 5, 90);
                // Existing terrain supplies the sand; its measured slope is fitted per bird below.
                var patch = group == null ? null : ArtLibrary.Find(group, "WetSandBar");
                if (patch != null) patch.gameObject.SetActive(false);
                float[] sandOffsets = { .2234428f, .186594f, .234589f, .1689253f };
                if (group != null)
                    foreach (var r in group.GetComponentsInChildren<Renderer>())
                        if (r.name.StartsWith("Forager_") && int.TryParse(r.name.Substring(8), out int i) && i >= 1 && i <= 4)
                            r.transform.localPosition += Vector3.up * sandOffsets[i - 1];
                ReplaceBird(group, "Forager_1", "Oystercatcher", lib, false, 1);
            }
            else if (map == 3)
            {
                var group = Place("CormorantRock", -77, 0, -30, 150);
                ReplaceBird(group, "PerchedCormorant_1", "Cormorant", lib, true, .78f);
            }
            else
            {
                var pair = Place("ChannelMarkers", 0, 0, 0);
                if (pair != null)
                {
                    // Independent waterline pivots, with a 22m passage rather
                    // than the source assembly's 2.3m display spacing.
                    foreach (var (name, x, z) in new[] { ("RedCan", -112f, -40f), ("GreenCone", -91f, -33f) })
                    {
                        var marker = pair.GetComponentsInChildren<Transform>().FirstOrDefault(t => t.name == name);
                        if (marker == null) continue;
                        marker.SetParent(root, true);
                        marker.position = new Vector3(x, environment.transform.position.y, z);
                        marker.gameObject.AddComponent<GullCoastBob>();
                    }
                }
            }
            return true;
        }

        static void ReplaceBird(GameObject group, string staticName, string rigName, ArtLibrary lib, bool cormorant, float scale)
        {
            if (group == null || lib.M(rigName) == null) return;
            var original = group.GetComponentsInChildren<Renderer>().FirstOrDefault(r => r.name == staticName);
            if (original == null) return;
            // Static group vertices are baked in metres, not necessarily about
            // each child's origin. Bounds locate the actual feet, not (0,0,0).
            var foot = original.bounds.center; foot.y = original.bounds.min.y;
            var bird = Put(group.transform, lib.M(rigName), group.transform.InverseTransformPoint(foot), 0, scale);
            if (bird == null) return;
            original.enabled = false;
            bird.AddComponent<GullCoastSkin>().Bind();
            bird.AddComponent<GullCoastBird>().Cormorant = cormorant;
        }
    }

    // Whole-assembly bob retains the delivered rope and marker waterline pivots.
    public sealed class GullCoastBob : MonoBehaviour
    {
        Vector3 rest;
        void Start() => rest = transform.localPosition;
        void Update() => transform.localPosition = rest + Vector3.up * (.022f * Mathf.Sin(Time.time * 1.1f + rest.x));
    }

    public sealed class GullCoastBird : MonoBehaviour
    {
        public bool Cormorant;
        Animation clips; float next; bool alternate;
        void Start()
        {
            clips = GetComponentInChildren<Animation>();
            if (clips == null) { enabled = false; return; }
            clips.cullingType = AnimationCullingType.AlwaysAnimate;
            // Importer take prefixes vary. Expose the short contract names and
            // set wrap per state; Dive is once, never a looping sinking bird.
            var names = new[] { "Idle", "DryWings", "Dive", "Walk", "Probe" };
            var source = new List<(string name, AnimationClip clip)>();
            foreach (AnimationState s in clips)
                foreach (var name in names) if (s.name.Contains(name)) source.Add((name, s.clip));
            foreach (var item in source)
            {
                clips.AddClip(item.clip, item.name);
                clips[item.name].wrapMode = item.name == "Dive" ? WrapMode.Once : WrapMode.Loop;
            }
            Play(Cormorant ? "Idle" : "Probe");
            next = Time.time + 4;
        }
        void Play(string name) { if (clips[name] == null) return; if (Application.isPlaying) clips.CrossFade(name, .25f); else clips[name].clip.SampleAnimation(clips.gameObject, 0); }
        void Update()
        {
            if (Time.time < next) return;
            alternate = !alternate;
            Play(Cormorant ? alternate ? "DryWings" : "Idle" : alternate ? "Walk" : "Probe");
            // Both birds stay over their real support; Walk is delivered in place.
            // Perched birds do not dive through their rock.
            next = Time.time + (alternate ? 3 : 6);
        }
    }

    // Local URP bindings preserve the delivered palette without changing other
    // scenery's shared material slots. Flat geometry and opaque backface culling.
    public sealed class GullCoastSkin : MonoBehaviour
    {
        readonly List<Material> owned = new();
        public void Bind()
        {
            var palette = new Dictionary<string,string> {
                {"M_FeatherDark","25383C"},{"M_FeatherGloss","344D4A"},
                {"M_Ivory","F3F0DC"},{"M_BillOrange","E36A35"},{"M_LegPink","C9857F"},
                {"M_RockShade","6F6A61"},{"M_Rock","8E8A80"},{"M_WetSand","A69775"},
                {"M_Red","BF4F3D"},{"M_Green","477A56"},{"M_Rope","D1AF76"},
                {"M_LampGlow","FFE7A3"},{"M_BillHorn","B7A179"},{"M_EyeTeal","70B4A0"},{"M_Eye","14262A"}
            };
            var cache = new Dictionary<string,Material>();
            foreach (var renderer in GetComponentsInChildren<Renderer>())
            {
                var materials = renderer.sharedMaterials;
                for (int i = 0; i < materials.Length; i++)
                {
                    var source = materials[i]; if (source == null) continue;
                    var slot = palette.Keys.FirstOrDefault(n => source.name.Contains(n));
                    if (slot == null) continue;
                    if (!cache.TryGetValue(slot, out var material))
                    {
                        material = new Material(Shader.Find("Universal Render Pipeline/Lit")) { name = "Gull coast " + slot, color = Palette.Hex(palette[slot]) };
                        material.SetFloat("_Smoothness", slot == "M_FeatherGloss" ? .32f : .12f);
                        if (slot == "M_LampGlow") { material.EnableKeyword("_EMISSION"); material.SetColor("_EmissionColor", material.color * 1.4f); }
                        owned.Add(material); cache[slot] = material;
                    }
                    materials[i] = material;
                }
                renderer.sharedMaterials = materials;
            }
        }
        void OnDestroy() { foreach (var material in owned) if (material != null) Prototype.Visuals.Kill(material); }
    }
}

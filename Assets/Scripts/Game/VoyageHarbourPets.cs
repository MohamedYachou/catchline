using System.Collections.Generic;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        void DressHarbourPets(Transform root, ArtLibrary lib, float quayTop)
        {
            var dog = lib.M("Dog"); var cat = lib.M("Cat");
            if (dog != null)
            {
                var holder = new GameObject("Harbour dog").transform; holder.SetParent(root, false);
                var rig = ArtLibrary.Spawn(dog, holder, Vector3.zero, Quaternion.identity);
                HarbourPetPose.Materials(rig);
                holder.gameObject.AddComponent<HarbourDog>().Setup(rig, quayTop, 61);
            }
            if (cat != null && lib.M("CrateStack") != null)
            {
                // Behind the walkers, on the back paving (.02m below the quay edge).
                var perch = new GameObject("Cat's crate").transform; perch.SetParent(root, false);
                perch.localPosition = new Vector3(-14f, quayTop - .02f, 4.65f);
                ArtLibrary.Spawn(lib.M("CrateStack"), perch, Vector3.zero, Quaternion.identity);
                // The supplied top crate is open. Three thin boards support the curled cat,
                // rather than putting its feet at the empty crate's bounding-box height.
                for (int i = 0; i < 3; i++)
                    Visuals.Box("Crate lid plank", perch, new Vector3((i - 1) * .161f, .6925f, .01f),
                        new Vector3(.158f, .025f, .35f), i == 1 ? Palette.Hex("DFB77A") : Palette.DeckWood);
                var holder = new GameObject("Harbour cat").transform; holder.SetParent(perch, false);
                holder.localPosition = new Vector3(0, .705f, .01f);
                holder.localRotation = Quaternion.Euler(0, 150, 0);
                var rig = ArtLibrary.Spawn(cat, holder, Vector3.zero, Quaternion.identity);
                HarbourPetPose.Materials(rig);
                holder.gameObject.AddComponent<HarbourCat>().Setup(rig, 131);
            }
        }
    }

    // A holder owns movement; imported root/bone tracks remain intact beneath it.
    // Runtime uses Legacy crossfades; edit-mode evidence samples the same imported clips.
    sealed class HarbourPetPose
    {
        readonly GameObject rig;
        readonly Animation animation;
        readonly Dictionary<string, AnimationClip> clips = new();
        readonly Dictionary<string, string> names = new();
        float time;
        public string Action { get; private set; }
        public bool Ready => animation != null;
        public HarbourPetPose(GameObject model)
        {
            rig = model; animation = model.GetComponentInChildren<Animation>();
            if (animation == null) return;
            animation.playAutomatically = false; animation.Stop();
            foreach (AnimationState state in animation)
            {
                var part = state.name.Split('|'); string name = part[part.Length - 1];
                clips[name] = state.clip; names[name] = state.name; state.wrapMode = WrapMode.Loop;
            }
            animation.enabled = Application.isPlaying;
        }
        public bool Has(string action) => clips.ContainsKey(action);
        public void Play(string action)
        {
            if (!Has(action) || Action == action) return;
            bool first = Action == null; Action = action; time = 0;
            if (Application.isPlaying)
            {
                if (first) animation.Play(names[action]);
                else animation.CrossFade(names[action], .3f);
            }
            else clips[action].SampleAnimation(rig, 0);
        }
        public void Tick(float dt)
        {
            time += dt;
            if (!Application.isPlaying && Action != null)
                clips[Action].SampleAnimation(rig, Mathf.Repeat(time, clips[Action].length));
        }
        public static void Materials(GameObject rig)
        {
            var colors = new Dictionary<string, string> {
                ["M_Rubber"]="28343B", ["M_GullWhite"]="F1F0EA", ["M_HairChestnut"]="50392E",
                ["M_Ginger"]="C58B50", ["M_GingerShade"]="9C6036", ["M_WoodHighlight"]="DFB77A", ["M_NoseRose"]="B97566"
            };
            foreach (var renderer in rig.GetComponentsInChildren<Renderer>())
            {
                var materials = renderer.sharedMaterials;
                for (int i = 0; i < materials.Length; i++)
                {
                    string n = materials[i] == null ? "" : materials[i].name.Replace(" (Instance)", "");
                    int prefix = n.IndexOf("M_", System.StringComparison.Ordinal); if (prefix > 0) n = n.Substring(prefix);
                    int suffix = n.IndexOf('.'); if (suffix > 0) n = n.Substring(0, suffix);
                    if (colors.TryGetValue(n, out var hex)) materials[i] = Visuals.Mat(Palette.Hex(hex));
                }
                renderer.sharedMaterials = materials;
            }
        }
    }

    public sealed class HarbourDog : MonoBehaviour
    {
        public const float West = -14.5f, East = -6.5f, Lane = 3.95f;
        HarbourPetPose pose;
        System.Random rng;
        float y, x, target, pause;
        public string Action => pose?.Action;
        public float LastStopDuration { get; private set; }
        public float PauseRemaining => pause;
        float R(float a, float b) => a + (float)rng.NextDouble() * (b-a);
        public void Setup(GameObject rig, float quayTop, int seed)
        {
            pose = new HarbourPetPose(rig); rng = new System.Random(seed); y = quayTop;
            if (!pose.Ready || !pose.Has("Trot") || !pose.Has("Sniff") || !pose.Has("Sit")) { enabled = false; return; }
            x = R(West+1, East-1); target = East;
            transform.localPosition = new Vector3(x,y,Lane); transform.localRotation = Quaternion.Euler(0,90,0);
            pose.Play("Trot"); Tick(0);
        }
        void Update() => Tick(Mathf.Min(Time.deltaTime,.1f));
        public void Tick(float dt)
        {
            if (pose == null || !enabled) return;
            if (pause > 0)
            {
                pause = Mathf.Max(0,pause-dt);
                if (pause == 0) pose.Play("Trot");
            }
            else
            {
                var want = Quaternion.Euler(0,target > x ? 90 : -90,0);
                transform.localRotation = Quaternion.RotateTowards(transform.localRotation,want,180*dt);
                // Turn on the spot before proceeding, rather than sliding sideways.
                if (Quaternion.Angle(transform.localRotation,want) < 12)
                {
                    x = Mathf.MoveTowards(x,target,.75f*dt);
                    bool end = Mathf.Abs(x-target) < .001f;
                    if (end) target = target == East ? West : East;
                    if (end || rng.NextDouble() < dt/11f)
                    {
                        pause = LastStopDuration = R(3,8);
                        pose.Play(rng.NextDouble() < .5 ? "Sniff" : "Sit");
                    }
                }
            }
            transform.localPosition = new Vector3(x,y,Lane); pose.Tick(dt);
        }
    }

    public sealed class HarbourCat : MonoBehaviour
    {
        HarbourPetPose pose;
        System.Random rng;
        float remaining;
        public string Action => pose?.Action;
        public float LastLookInterval { get; private set; }
        float Rest() => 20f + (float)rng.NextDouble()*20f - 3f;
        public void Setup(GameObject rig, int seed)
        {
            pose = new HarbourPetPose(rig); rng = new System.Random(seed);
            if (!pose.Ready || !pose.Has("Sleep") || !pose.Has("Look")) { enabled = false; return; }
            pose.Play("Sleep"); remaining = LastLookInterval = 20+(float)rng.NextDouble()*20; pose.Tick(0);
        }
        void Update() => Tick(Mathf.Min(Time.deltaTime,.1f));
        public void Tick(float dt)
        {
            if (pose == null || !enabled) return;
            remaining -= dt;
            if (remaining <= 0)
            {
                float overshoot = -remaining;
                if (pose.Action == "Sleep") { pose.Play("Look"); remaining = 3-overshoot; }
                else { pose.Play("Sleep"); remaining = Rest()-overshoot; LastLookInterval = remaining+3+overshoot; }
            }
            pose.Tick(dt);
        }
    }
}

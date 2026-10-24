using System;
using System.Collections.Generic;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    // Tells a tap what it hit.
    public class Tappable : MonoBehaviour
    {
        public Rod Rod;
        public DeckFish Fish;
        public bool Cooler;
        public bool Deck;
    }

    // A fish flopping on the deck, waiting to be picked up and carried to the cooler.
    public class DeckFish
    {
        public Species Species;
        public float Kg;
        public Transform Root;
        public Vector2Int Tile;
        public Person ClaimedBy;
        public float Age;
        public float CaughtAt;
        public bool CaughtByCrew; // Automatic catches stay out of captain reward/toast feedback.
        public bool FromNetBasket;
        public int DeepLineRig = -1; // Normal deck collection, but retain this rig's catch until collected.
        public Vector3 RestPos, SpawnFrom;
        public Transform Tail;

        public static Transform BuildModel(Species s, float kg, Transform parent)
        {
            var def = GameData.Get(s);
            float k = Mathf.Lerp(0.85f, 1.25f, Mathf.InverseLerp(def.MinKg, def.MaxKg, kg));
            var library = ArtLibrary.Get();
            // New species also resolve by model name, without replacing the existing indexed library.
            var prefab = library?.FishFor(s) ?? library?.M(s.ToString());
            if (prefab != null)
            {
                // Modelled fish: nose +Z, upright. Lay it on its side inside an unrotated holder.
                var h = new GameObject(def.Name + " (holder)").transform;
                h.SetParent(parent, false);
                var model = ArtLibrary.Spawn(prefab, h, Vector3.zero, Quaternion.identity);
                // FBX exporter unit/root transforms vary. Fit the existing species
                // length, rather than treating centimetre mesh coordinates as metres.
                if (s == Species.Crab) ArtLibrary.AimAlong(model, Vector3.forward, def.Length*k*1.3f);
                else if ((int)s >= 10) GeminiFishModels.Fit(model, def.Length * k * 1.3f, s);
                else
                {
                    ArtLibrary.AimAlong(model, Vector3.forward, def.Length * k * 1.3f);
                    model.transform.localRotation = Quaternion.Euler(0, 0, 90) * model.transform.localRotation;
                }
                return h;
            }
            float len = def.Length * k;
            bool eel = s == Species.Conger;
            var root = new GameObject(def.Name).transform;
            root.SetParent(parent, false);
            var body = Visuals.Prim(PrimitiveType.Sphere, "Body", root, Vector3.zero,
                new Vector3(eel ? 0.07f : len * 0.32f, eel ? 0.07f : len * 0.3f, len), def.Color);
            body.transform.localPosition = new Vector3(0f, 0f, 0f);
            var tail = Visuals.Box("Tail", root, new Vector3(0f, 0f, -len * 0.55f), new Vector3(0.02f, len * 0.28f, len * 0.18f), def.Color * 0.85f);
            tail.transform.localRotation = Quaternion.Euler(0f, 0f, 0f);
            if (s == Species.Mackerel)
                for (int i = 0; i < 3; i++)
                    Visuals.Box("Stripe", root, new Vector3(0f, len * 0.11f, (i - 1) * len * 0.22f), new Vector3(len * 0.2f, 0.01f, 0.025f), Palette.Hex("1F4E50"));
            Visuals.Prim(PrimitiveType.Sphere, "Eye", root, new Vector3(0f, len * 0.05f, len * 0.36f), Vector3.one * 0.035f, Palette.Rubber);
            // Lie on its side inside an unrotated holder, so the holder can flop and be carried.
            root.localRotation = Quaternion.Euler(0f, 0f, 90f);
            var holder = new GameObject(def.Name + " (holder)").transform;
            holder.SetParent(parent, false);
            root.SetParent(holder, false);
            return holder;
        }
    }

    // A person on deck: walks the tile grid, does timed actions and carries one fish.
    public class Person
    {
        public readonly string Name;
        public readonly bool IsCaptain;
        // One work-speed model: skill 100 and level 1 for the captain and (until cards arrive) every hand. See WorkSpeed.
        public float Skill = WorkSpeed.SpecialitySkill, LevelMult = WorkSpeed.BaseLevelMult;
        public float Speed => WorkSpeed.Rate(Skill, LevelMult);
        public CrewMember Contract;
        public Transform Root { get; private set; }
        public DeckFish Carrying;
        public bool Rowing;

        Vector3 pos;
        public DeckGrid Grid;
        readonly Vector3 offset;
        readonly List<Vector2Int> path = new();
        Action arrive, walkCancel;
        float busyLeft, busyTotal;
        Action busyDone, busyCancel;
        public string BusyLabel { get; private set; }
        Transform body;
        Quaternion facing = Quaternion.identity;
        public bool Loitering { get; private set; }
        public bool CarryingBatch;
        public int PatrolLeg { get; private set; }
        float lookoutLeft, lookoutDuration;
        Transform rig, lookoutHead;
        readonly Dictionary<string, AnimationClip> clips = new();
        public string Pose;
        string lastPose;
        float poseTime;
        string oneShot;
        float oneShotLeft;

        public void PlayOnce(string pose)
        {
            oneShot = pose;
            oneShotLeft = clips.TryGetValue(pose, out var clip) ? clip.length : 0f;
        }
        float anim;
        bool moving;

        public Person(string name, bool captain, Vector3 offset)
        {
            Name = name;
            IsCaptain = captain;
            this.offset = offset;
        }

        public Vector2Int Tile => Grid != null ? Grid.GetTile(pos - offset) : DeckGrid.ToTile(pos);
        public bool Walking => path.Count > 0 || arrive != null;
        public bool Busy => busyTotal > 0f;
        public float BusyProgress => busyTotal > 0f ? Mathf.Clamp01(1f - busyLeft / busyTotal) : 0f; // read-only, for the crew rail
        public bool Idle => !Walking && !Busy;
        public string State => Busy ? BusyLabel : Walking ? Loitering ? "strolling" : "walking" : Carrying != null ? "carrying a fish" : Loitering ? "looking overboard" : "ready";

        public void Build(Transform boat, Vector2Int tile, Color suit, Color hat)
        {
            Root = new GameObject(Name).transform;
            Root.SetParent(boat, false);
            Place(tile);

            body = new GameObject("Body").transform;
            body.SetParent(Root, false);
            var lib = ArtLibrary.Get();
            var prefab = lib?.M("CrewRig");
            if (prefab != null)
            {
                rig = ArtLibrary.Spawn(prefab, body, Vector3.zero, Quaternion.identity).transform;
                // Playback is sampled by the same clock as gameplay, including the balance bot.
                var automatic = rig.GetComponent<Animation>();
                if (automatic != null) automatic.enabled = false;
                string outfit = IsCaptain ? "Outfit_Captain" : Contract?.Grade == Grade.Veteran ? "Outfit_Veteran" : Contract?.Role == CrewRole.Fisherman ? "Outfit_Fisherman" : "Outfit_Deckhand";
                string roleHat = IsCaptain ? "Hat_CaptainCap" : Contract?.Role == CrewRole.Fisherman ? "Hat_Hood" : "Hat_Beanie";
                foreach (var child in rig.GetComponentsInChildren<Transform>(true))
                {
                    if (child.name == "Head") lookoutHead = child;
                    if (child.name.StartsWith("Outfit_")) child.gameObject.SetActive(child.name == outfit);
                    if (child.name.StartsWith("Hat_")) child.gameObject.SetActive(child.name == roleHat);
                }
                if (Contract?.Role == CrewRole.Engineer)
                {
                    foreach(var t in rig.GetComponentsInChildren<Transform>(true))
                        if(t.name.StartsWith("Hat_"))t.gameObject.SetActive(false);
                    Visuals.Prim(PrimitiveType.Sphere,"Engineer hardhat",body,new Vector3(0,.9f,0),new Vector3(.32f,.16f,.30f),Palette.Hex("E6AD38"));
                    Visuals.Prim(PrimitiveType.Cylinder,"Engineer hardhat brim",body,new Vector3(0,.87f,0),new Vector3(.36f,.025f,.34f),Palette.Hex("E6AD38"));
                }
                if (lib.CrewClips != null)
                    foreach (var clip in lib.CrewClips)
                    {
                        var parts = clip.name.Split('|');
                        clips[parts[parts.Length - 1]] = clip;
                    }
            }
            else
            {
            Visuals.Prim(PrimitiveType.Capsule, "Torso", body, new Vector3(0f, 0.3f, 0f), new Vector3(0.34f, 0.3f, 0.28f), suit);
            Visuals.Prim(PrimitiveType.Sphere, "Head", body, new Vector3(0f, 0.74f, 0f), Vector3.one * 0.28f, Palette.Skin);
            Visuals.Box("Nose", body, new Vector3(0f, 0.74f, 0.14f), new Vector3(0.05f, 0.05f, 0.04f), Palette.Skin * 0.92f);
            if (IsCaptain)
            {
                Visuals.Prim(PrimitiveType.Cylinder, "Cap", body, new Vector3(0f, 0.87f, 0f), new Vector3(0.28f, 0.045f, 0.28f), hat);
                Visuals.Box("Brim", body, new Vector3(0f, 0.85f, 0.14f), new Vector3(0.2f, 0.02f, 0.11f), Palette.Rubber);
            }
            else
            {
                Visuals.Prim(PrimitiveType.Sphere, "Beanie", body, new Vector3(0f, 0.83f, 0f), new Vector3(0.29f, 0.19f, 0.29f), hat);
            }
            }
        }

        public void Place(Vector2Int tile)
        {
            EndLoiter();
            path.Clear();
            arrive = walkCancel = null;
            pos = (Grid != null ? Grid.GetLocal(tile) : DeckGrid.ToLocal(tile)) + offset;
            if (Root != null) Root.localPosition = pos;
        }

        public void Stop()
        {
            EndLoiter();
            path.Clear();
            var wc = walkCancel;
            arrive = walkCancel = null;
            wc?.Invoke();
            if (Busy)
            {
                var bc = busyCancel;
                busyTotal = 0f;
                busyDone = busyCancel = null;
                bc?.Invoke();
            }
        }

        public bool WalkTo(DeckGrid grid, Vector2Int tile, Action onArrive, Action onCancel = null)
        {
            Stop();
            Grid = grid;
            var p = grid.FindPath(Tile, tile);
            if (p == null) return false;
            path.AddRange(p);
            arrive = onArrive ?? (() => { });
            walkCancel = onCancel;
            return true;
        }

        public void Do(string label, float seconds, Action done, Action cancel = null)
        {
            EndLoiter();
            BusyLabel = label;
            busyLeft = busyTotal = seconds;
            busyDone = done;
            busyCancel = cancel;
        }

        public void Face(Vector3 dir)
        {
            dir.y = 0f;
            if (dir.sqrMagnitude > 0.0001f) facing = Quaternion.LookRotation(dir);
        }

        public void FacePoint(Vector3 boatLocal) => Face(boatLocal - pos);

        void EndLoiter()
        {
            if (Loitering) Pose = null;
            Loitering = false;
            lookoutLeft = 0;
        }

        public bool PatrolReady => !Walking && lookoutLeft <= 0;

        public void Stroll(DeckGrid grid, Vector2Int tile, Vector3 outward)
        {
            int leg = ++PatrolLeg;
            if (!WalkTo(grid, tile, () =>
            {
                Face(outward);
                // Relaxed hands at the rail; the idle clip supplies subtle breathing.
                Pose = "Idle";
                lookoutLeft = lookoutDuration = 3.8f + leg % 3 * .9f;
            })) return;
            Loitering = true;
        }

        public void Tick(float dt, Quaternion camRot)
        {
            moving = false;
            float budget = WorkSpeed.Walk(Skill, LevelMult) * dt * (Loitering ? .55f : 1f);
            while (path.Count > 0 && budget > 0f)
            {
                var goal = (Grid != null ? Grid.GetLocal(path[0]) : DeckGrid.ToLocal(path[0])) + offset;
                var d = goal - pos;
                float dist = d.magnitude;
                if (dist > 0.001f) Face(d);
                moving = true;
                if (dist <= budget)
                {
                    pos = goal;
                    budget -= dist;
                    path.RemoveAt(0);
                }
                else
                {
                    pos += d / dist * budget;
                    budget = 0f;
                }
            }
            if (path.Count == 0 && arrive != null)
            {
                var a = arrive;
                arrive = walkCancel = null;
                a();
            }

            if (Busy)
            {
                busyLeft -= dt * Speed;
                if (busyLeft <= 0f)
                {
                    var done = busyDone;
                    busyTotal = 0f;
                    busyDone = busyCancel = null;
                    done?.Invoke();
                }
            }

            if (Loitering && !Walking) lookoutLeft = Mathf.Max(0, lookoutLeft - dt);
            Root.localRotation = Quaternion.RotateTowards(Root.localRotation, facing, 420f * dt);
            // The authored rig already moves its hips. A second whole-body work bob
            // made resting and working sailors vibrate against the deck.
            anim += dt;
            float bob = rig == null && moving ? Mathf.Abs(Mathf.Sin(anim * 10f)) * 0.025f : 0f;
            Root.localPosition = pos + Vector3.up * bob;
            body.localRotation = Rowing ? Quaternion.Euler(Mathf.Sin(anim * 3.2f) * 18f, 0f, 0f) : Quaternion.identity;
            if (rig != null)
            {
                body.localRotation = Quaternion.identity;
                oneShotLeft = Mathf.Max(0f, oneShotLeft - dt * Speed);
                string pose = moving ? Carrying != null || CarryingBatch ? "Carry" : "Walk"
                    : Busy ? BusyLabel switch { "Baiting" or "Setting net" => "Bait", "Casting" => "Cast", "Winching net" or "Hauling net" or "Recovering buoy catch" => "Reel", "Taking fish" or "Putting fish away" or "Making chum" or "Sorting fish" or "Stowing" or "Picking up" or "Gathering net catch" or "Stowing net catch" => "Stow", _ => "Idle" }
                    : oneShotLeft > 0f ? oneShot : Rowing ? "Row" : Pose ?? "Idle";
                if (pose != lastPose) { poseTime = 0f; lastPose = pose; }
                poseTime += dt * Speed * (moving && Loitering ? .55f : 1f);
                if (clips.TryGetValue(pose, out var clip) && clip.length > 0f)
                {
                    bool loop = pose is "Idle" or "Walk" or "Carry" or "Bait" or "Wait" or "Reel" or "Row";
                    clip.SampleAnimation(rig.gameObject, loop ? Mathf.Repeat(poseTime, clip.length) : Mathf.Min(poseTime, clip.length));
                    if (Loitering && !moving && lookoutHead != null)
                    {
                        float elapsed = lookoutDuration - lookoutLeft;
                        float settle = Mathf.SmoothStep(0, 1, Mathf.Min(elapsed, lookoutLeft) * 2f);
                        // Look down past the rail, with a slow glance along the water.
                        var down = Quaternion.AngleAxis(14f * settle, Root.right);
                        var glance = Quaternion.AngleAxis(Mathf.Sin(elapsed * 1.1f) * 9f * settle, Root.up);
                        lookoutHead.rotation = glance * down * lookoutHead.rotation;
                    }
                }
            }

            if (Carrying != null)
            {
                Carrying.Root.localPosition = new Vector3(0f, 0.55f, 0.24f);
                Carrying.Root.localRotation = Quaternion.Euler(0f, 90f, Mathf.Sin(anim * 14f) * 12f);
            }
        }
    }

    public enum RodState { Unbaited, Ready, Flying, Waiting, Bite, Reeling }

    // One fishing rod on the gunwale: bait, cast, wait through nibbles, strike, reel.
    // A fish shadow circles the bobber while you wait, darts in on nibbles and sits on it when it bites.
    public class Rod
    {
        public readonly int Index;
        public readonly Vector2Int Tile;
        public RodState State = RodState.Unbaited;
        public float Power;
        public Person BaitingBy;
        public Person Fisher;
        public bool FisherAttempted;
        public bool Unlocked = true;
        public Species HookedSpecies;
        public float HookedKg;
        public bool Chum;
        public bool Squid; // baited with squid: bigger fish
        public bool Scraps; // Unlimited poor bait: small species/specimens only.

        public Transform Root { get; private set; }
        public Vector3 TipLocal => tipLocal;
        Transform bobber, splash, shadow;
        TextMesh alert;
        LineRenderer line;
        Vector3 tipLocal;
        public Vector3 Outward { get; private set; } = Vector3.back;
        Vector3 castFrom, castTo;
        float t, waitTotal, waitTimer, nibbleTimer, reelTotal, swimAngle, biteWindow = GameData.BiteWindow;
        readonly List<float> nibbles = new();
        int nextNibble;
        bool selfHook;
        float anim;

        public const float WaterY = -0.3f;

        public Rod(int index, Vector2Int tile)
        {
            Index = index;
            Tile = tile;
        }

        public bool InWater => State is RodState.Waiting or RodState.Bite or RodState.Flying or RodState.Reeling;
        public float WaitRemaining => State == RodState.Waiting ? waitTotal - waitTimer : 999f;
        public float WaitProgress => State == RodState.Waiting ? Mathf.Clamp01(waitTimer / waitTotal) : State == RodState.Bite ? 1f : 0f;
        public bool Nibbling => nibbleTimer > 0f;
        public float BiteProgress => State == RodState.Bite ? Mathf.Clamp01(t / biteWindow) : 0f;
        public float ReelProgress => State == RodState.Reeling ? Mathf.Clamp01(t) : 0f;
        public float SwimAngle => swimAngle;

        public string StateText => State switch
        {
            RodState.Unbaited => "needs bait",
            RodState.Ready => "baited",
            RodState.Flying => "casting",
            RodState.Waiting => "waiting for a bite",
            RodState.Bite => "BITE!",
            RodState.Reeling => "reeling in",
            _ => "",
        };

        public void Build(Transform boat, Transform world, Vector3? socket = null, GameObject upgradedRod = null, Vector3? outward = null)
        {
            Root = new GameObject($"Rod {Index + 1}").transform;
            Root.SetParent(boat, false);
            var lib = ArtLibrary.Get();
            var rodPrefab = upgradedRod ?? lib?.FishingRod;
            bool model = rodPrefab != null;
            // With the rowboat model the rod sits in its gunwale socket.
            var baseLocal = socket ?? DeckGrid.ToLocal(Tile) + (model ? new Vector3(0f, 0.44f, -0.615f) : new Vector3(0f, 0.32f, -0.42f));
            Outward = outward ?? Vector3.back;
            var dir = new Vector3(0.05f, 1.6f, Outward.z * .6f).normalized; // lean over the rod's actual gunwale
            tipLocal = baseLocal + dir * (model ? 1.6f : 1.52f);
            if (model)
            {
                var rod = ArtLibrary.Spawn(rodPrefab, Root, baseLocal, Quaternion.identity);
                ArtLibrary.AimAlong(rod, dir, 2f);
                tipLocal = baseLocal + dir * 2f;
            }
            else
            {
                var pole = Visuals.Prim(PrimitiveType.Cylinder, "Pole", Root, (baseLocal + tipLocal) / 2f, new Vector3(0.035f, (tipLocal - baseLocal).magnitude / 2f, 0.035f), Palette.Rubber);
                pole.transform.localRotation = Quaternion.FromToRotation(Vector3.up, dir);
                Visuals.Box("Holder", Root, baseLocal + new Vector3(0f, -0.12f, 0f), new Vector3(0.12f, 0.3f, 0.12f), Palette.Steel);
                Visuals.Prim(PrimitiveType.Cylinder, "Reel", Root, baseLocal + dir * 0.25f + new Vector3(0f, -0.06f, 0f), new Vector3(0.1f, 0.03f, 0.1f), Palette.Steel);
            }

            bobber = new GameObject("Bobber").transform;
            bobber.SetParent(world, false);
            if (lib != null && lib.Bobber != null) ArtLibrary.Spawn(lib.Bobber, bobber, Vector3.zero, Quaternion.identity, 1.8f);
            else
            {
                Visuals.Prim(PrimitiveType.Sphere, "Top", bobber, new Vector3(0f, 0.04f, 0f), new Vector3(0.12f, 0.08f, 0.12f), Palette.Bad);
                Visuals.Prim(PrimitiveType.Sphere, "Bottom", bobber, new Vector3(0f, -0.01f, 0f), new Vector3(0.12f, 0.08f, 0.12f), Palette.Rail);
            }

            splash = Visuals.Prim(PrimitiveType.Cylinder, "Splash", world, Vector3.zero, new Vector3(0.3f, 0.005f, 0.3f), new Color(0.9f, 0.97f, 1f)).transform;
            splash.gameObject.SetActive(false);
            shadow = Visuals.Prim(PrimitiveType.Sphere, "FishShadow", world, Vector3.zero, new Vector3(0.16f, 0.01f, 0.42f), VoyageGame.ShadowColor).transform;
            shadow.gameObject.SetActive(false);

            var lineGo = new GameObject("Line");
            lineGo.transform.SetParent(world, false);
            line = lineGo.AddComponent<LineRenderer>();
            line.useWorldSpace = true;
            line.positionCount = 2;
            line.widthMultiplier = 0.012f;
            line.sharedMaterial = Visuals.Mat(new Color(0.95f, 0.95f, 0.95f));
            line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;

            alert = Visuals.Label("Alert", Root, tipLocal + new Vector3(0f, 0.35f, 0f), 0.06f);
            alert.text = "!";
            alert.color = Palette.Oilskin;
            alert.fontStyle = FontStyle.Bold;
        }

        public void SetUnlocked(bool on)
        {
            Unlocked = on;
            Root.gameObject.SetActive(on);
            bobber.gameObject.SetActive(on);
            line.gameObject.SetActive(on);
            if (!on) shadow.gameObject.SetActive(false);
        }

        public void Destroy()
        {
            Visuals.Kill(Root.gameObject);
            Visuals.Kill(bobber.gameObject);
            Visuals.Kill(shadow.gameObject);
            Visuals.Kill(splash.gameObject);
            Visuals.Kill(line.gameObject);
        }

        public void ResetForTrip()
        {
            if (State != RodState.Ready || Chum) State = RodState.Unbaited;
            Chum = false;
            BaitingBy = null;
            FisherAttempted = false;
            nibbleTimer = 0f;
            splash.gameObject.SetActive(false);
            shadow.gameObject.SetActive(false);
        }

        Vector3 LandingPoint(Transform boat, float power)
        {
            var tip = boat.TransformPoint(tipLocal);
            var outward = boat.TransformDirection(new Vector3(0.12f, 0f, Outward.z)).normalized;
            var p = tip + outward * (0.5f + power * 2.3f);
            return new Vector3(p.x, WaterY, p.z);
        }

        public void Cast(VoyageGame g, float power)
        {
            if (State != RodState.Ready) return;
            Power = Mathf.Clamp01(power);
            castFrom = g.Boat.TransformPoint(tipLocal);
            castTo = LandingPoint(g.Boat, Power);
            t = 0f;
            State = RodState.Flying;
            FisherAttempted = false;
        }

        // Player (or bot) strikes. Returns a message for the toast.
        public string Strike(VoyageGame g)
        {
            if (State == RodState.Waiting)
            {
                bool nibble = Nibbling;
                State = RodState.Unbaited;
                nibbleTimer = 0f;
                g.Stats.Spooked++;
                return nibble ? "Too early! That was only a nibble, and the fish took the bait." : "Too early! You spooked it and lost the bait.";
            }
            if (State == RodState.Bite)
            {
                StartReel();
                return $"Hooked a {GameData.Get(HookedSpecies).Name.ToLower()}!";
            }
            return null;
        }

        void StartReel()
        {
            State = RodState.Reeling;
            t = 0f;
            reelTotal = Mathf.Clamp(0.8f + HookedKg * 0.3f, 0.8f, 2.5f);
            castFrom = bobber.position;
            splash.gameObject.SetActive(false);
        }

        void StartWait(VoyageGame g, float scale)
        {
            State = RodState.Waiting;
            waitTotal = g.State.RollBiteWait(g.ActiveSpot, Power) * scale;
            if (g.LearningFishing) waitTotal = Mathf.Clamp(waitTotal, 4f, 6f);
            waitTimer = 0f;
            nibbles.Clear();
            nextNibble = 0;
            int n = 1 + g.State.Rng.Next(3);
            for (int i = 0; i < n; i++) nibbles.Add(1f + (float)g.State.Rng.NextDouble() * Mathf.Max(0.5f, waitTotal - 2f));
            nibbles.Sort();
        }

        public void Tick(VoyageGame g, float dt, bool attended)
        {
            anim += dt;
            var tipWorld = g.Boat.TransformPoint(tipLocal);
            var bobPos = tipWorld + Vector3.down * 0.35f;
            bool showShadow = false;
            Vector3 shadowPos = castTo;

            switch (State)
            {
                case RodState.Flying:
                    t += dt / GameData.FlightTime;
                    bobPos = Vector3.Lerp(castFrom, castTo, t) + Vector3.up * Mathf.Sin(Mathf.Clamp01(t) * Mathf.PI) * 1.2f;
                    if (t >= 1f)
                    {
                        StartWait(g, 1f);
                        swimAngle = (float)g.State.Rng.NextDouble() * 360f;
                        bobPos = castTo;
                        g.Splash(castTo, 0.25f, Fisher == null);
                    }
                    break;

                case RodState.Waiting:
                    waitTimer += dt;
                    if (nextNibble < nibbles.Count && waitTimer >= nibbles[nextNibble])
                    {
                        nextNibble++;
                        nibbleTimer = 0.4f;
                        g.OnNibble(this);
                    }
                    nibbleTimer = Mathf.Max(0f, nibbleTimer - dt);
                    bobPos = castTo + Vector3.up * (Mathf.Sin(anim * 2.2f + Index) * 0.015f - (nibbleTimer > 0f ? 0.05f : 0f));
                    // The fish circles closer as the bite nears, and darts in for a nibble.
                    swimAngle += dt * 70f;
                    float radius = Mathf.Lerp(1.0f, 0.35f, WaitProgress) * (nibbleTimer > 0f ? 0.3f : 1f);
                    showShadow = true;
                    shadowPos = castTo + Quaternion.Euler(0f, swimAngle, 0f) * Vector3.forward * radius;
                    if (waitTimer >= waitTotal)
                    {
                        State = RodState.Bite;
                        t = 0f;
                        (HookedSpecies, HookedKg) = g.State.RollFish(g.ActiveSpot, Power + (Squid ? GameData.SquidPowerBonus : 0f), Scraps, Squid, Chum);
                        biteWindow = g.StrikeWindow;
                        selfHook = (float)g.State.Rng.NextDouble() < g.State.SelfHookChance;
                        splash.gameObject.SetActive(true);
                        g.OnBite(this);
                    }
                    break;

                case RodState.Bite:
                    t += dt;
                    bobPos = castTo + Vector3.down * 0.14f;
                    float s = 0.3f + Mathf.Repeat(anim * 1.5f, 1f) * 0.4f;
                    splash.position = castTo + Vector3.up * 0.01f;
                    splash.localScale = new Vector3(s, 0.005f, s);
                    showShadow = true;
                    shadowPos = castTo + new Vector3(Mathf.Sin(anim * 30f) * 0.05f, 0f, 0f);
                    if (t >= biteWindow)
                    {
                        splash.gameObject.SetActive(false);
                        if (!attended && selfHook)
                        {
                            StartReel();
                            if (Fisher == null) g.Toast($"Rod {Index + 1} hooked a {GameData.Get(HookedSpecies).Name.ToLower()} by itself.");
                        }
                        else if (!attended && g.State.Rng.NextDouble() < 0.6)
                        {
                            // Nobody struck: the fish keeps picking at the bait. Slower, not wasted.
                            StartWait(g, 0.6f);
                        }
                        else
                        {
                            State = RodState.Unbaited;
                            g.Stats.Missed++;
                            if (Fisher == null) g.Toast(attended ? "Too late! It got away with the bait." : $"A fish stole the bait on rod {Index + 1}.");
                        }
                    }
                    break;

                case RodState.Reeling:
                    t += dt * g.State.ReelSpeed * (Fisher?.Speed ?? 1f) / reelTotal;
                    var under = new Vector3(tipWorld.x, WaterY, tipWorld.z);
                    bobPos = Vector3.Lerp(castFrom, under, t) + Vector3.up * Mathf.Abs(Mathf.Sin(anim * 18f)) * 0.04f;
                    showShadow = true;
                    shadowPos = bobPos;
                    if (t >= 1f)
                    {
                        State = RodState.Unbaited;
                        showShadow = false;
                        g.LandFish(this, HookedSpecies, HookedKg);
                    }
                    break;
            }

            shadow.gameObject.SetActive(showShadow && Unlocked);
            if (showShadow)
            {
                var prev = shadow.position;
                shadow.position = new Vector3(shadowPos.x, WaterY - .42f, shadowPos.z);
                var move = shadow.position - prev;
                if (move.sqrMagnitude > 0.00001f) shadow.rotation = Quaternion.LookRotation(move.normalized);
            }
            bobber.position = bobPos;
            line.SetPosition(0, tipWorld);
            line.SetPosition(1, bobPos + Vector3.up * 0.05f);
            alert.gameObject.SetActive(State == RodState.Bite && Fisher == null && g.MinigameRod != this && Mathf.Repeat(anim * 6f, 1f) < 0.7f);
            alert.transform.rotation = g.Cam.transform.rotation;
        }
    }
}

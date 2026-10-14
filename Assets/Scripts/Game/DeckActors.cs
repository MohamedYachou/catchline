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
        public Vector3 RestPos, SpawnFrom;

        public static Transform BuildModel(Species s, float kg, Transform parent)
        {
            var def = GameData.Get(s);
            float k = Mathf.Lerp(0.85f, 1.25f, Mathf.InverseLerp(def.MinKg, def.MaxKg, kg));
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
        public float Speed = 1f;
        public CrewMember Contract;
        public Transform Root { get; private set; }
        public DeckFish Carrying;
        public bool Rowing;

        Vector3 pos;
        readonly Vector3 offset;
        readonly List<Vector2Int> path = new();
        Action arrive, walkCancel;
        float busyLeft, busyTotal;
        Action busyDone, busyCancel;
        public string BusyLabel { get; private set; }
        Transform barFill, barRoot, body;
        float anim;
        bool moving;

        public Person(string name, bool captain, Vector3 offset)
        {
            Name = name;
            IsCaptain = captain;
            this.offset = offset;
        }

        public Vector2Int Tile => DeckGrid.ToTile(pos);
        public bool Walking => path.Count > 0 || arrive != null;
        public bool Busy => busyTotal > 0f;
        public bool Idle => !Walking && !Busy;
        public string State => Busy ? BusyLabel : Walking ? "walking" : Carrying != null ? "carrying a fish" : "ready";

        public void Build(Transform boat, Vector2Int tile, Color suit, Color hat)
        {
            Root = new GameObject(Name).transform;
            Root.SetParent(boat, false);
            Place(tile);

            body = new GameObject("Body").transform;
            body.SetParent(Root, false);
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

            barRoot = new GameObject("Progress").transform;
            barRoot.SetParent(Root, false);
            barRoot.localPosition = new Vector3(0f, 1.15f, 0f);
            Visuals.Box("Back", barRoot, Vector3.zero, new Vector3(0.5f, 0.06f, 0.02f), Palette.Rubber);
            barFill = Visuals.Box("Fill", barRoot, new Vector3(0f, 0f, -0.012f), new Vector3(0.48f, 0.045f, 0.02f), Palette.Oilskin).transform;
            barRoot.gameObject.SetActive(false);
        }

        public void Place(Vector2Int tile)
        {
            path.Clear();
            arrive = walkCancel = null;
            pos = DeckGrid.ToLocal(tile) + offset;
            if (Root != null) Root.localPosition = pos;
        }

        public void Stop()
        {
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
            var p = grid.FindPath(Tile, tile);
            if (p == null) return false;
            path.AddRange(p);
            arrive = onArrive ?? (() => { });
            walkCancel = onCancel;
            return true;
        }

        public void Do(string label, float seconds, Action done, Action cancel = null)
        {
            BusyLabel = label;
            busyLeft = busyTotal = seconds;
            busyDone = done;
            busyCancel = cancel;
        }

        public void Face(Vector3 dir)
        {
            dir.y = 0f;
            if (dir.sqrMagnitude > 0.0001f) Root.localRotation = Quaternion.LookRotation(dir);
        }

        public void Tick(float dt, float mult, Quaternion camRot)
        {
            moving = false;
            float budget = GameData.WalkSpeed * Speed * mult * dt;
            while (path.Count > 0 && budget > 0f)
            {
                var goal = DeckGrid.ToLocal(path[0]) + offset;
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
                busyLeft -= dt * Speed * mult;
                if (busyLeft <= 0f)
                {
                    var done = busyDone;
                    busyTotal = 0f;
                    busyDone = busyCancel = null;
                    done?.Invoke();
                }
            }

            // Animation: bob while walking, nod while working, sway while rowing.
            anim += dt;
            float bob = moving ? Mathf.Abs(Mathf.Sin(anim * 13f)) * 0.06f : 0f;
            if (Busy) bob = Mathf.Abs(Mathf.Sin(anim * 9f)) * 0.03f;
            Root.localPosition = pos + Vector3.up * bob;
            body.localRotation = Rowing ? Quaternion.Euler(Mathf.Sin(anim * 3.2f) * 18f, 0f, 0f) : Quaternion.identity;

            barRoot.gameObject.SetActive(Busy);
            if (Busy)
            {
                float t = 1f - Mathf.Clamp01(busyLeft / busyTotal);
                barFill.localScale = new Vector3(0.48f * t, 0.045f, 0.02f);
                barFill.localPosition = new Vector3(-0.24f + 0.24f * t, 0f, -0.012f);
                barRoot.rotation = camRot;
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
        public bool Unlocked = true;
        public Species HookedSpecies;
        public float HookedKg;

        public Transform Root { get; private set; }
        public Vector3 TipLocal => tipLocal;
        Transform bobber, splash, shadow;
        TextMesh alert;
        LineRenderer line;
        Vector3 tipLocal;
        Vector3 castFrom, castTo;
        float t, waitTotal, waitTimer, nibbleTimer, reelTotal, swimAngle;
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
        public float BiteProgress => State == RodState.Bite ? Mathf.Clamp01(t / GameData.BiteWindow) : 0f;
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

        public void Build(Transform boat, Transform world)
        {
            Root = new GameObject($"Rod {Index + 1}").transform;
            Root.SetParent(boat, false);
            var baseLocal = DeckGrid.ToLocal(Tile) + new Vector3(0f, 0.32f, -0.42f);
            tipLocal = baseLocal + new Vector3(0.15f, 0.85f, -1.25f);
            var dir = tipLocal - baseLocal;
            var pole = Visuals.Prim(PrimitiveType.Cylinder, "Pole", Root, (baseLocal + tipLocal) / 2f, new Vector3(0.035f, dir.magnitude / 2f, 0.035f), Palette.Rubber);
            pole.transform.localRotation = Quaternion.FromToRotation(Vector3.up, dir);
            Visuals.Box("Holder", Root, baseLocal + new Vector3(0f, -0.12f, 0f), new Vector3(0.12f, 0.3f, 0.12f), Palette.Steel);
            Visuals.Prim(PrimitiveType.Cylinder, "Reel", Root, baseLocal + dir.normalized * 0.25f + new Vector3(0f, -0.06f, 0f), new Vector3(0.1f, 0.03f, 0.1f), Palette.Steel);

            bobber = new GameObject("Bobber").transform;
            bobber.SetParent(world, false);
            Visuals.Prim(PrimitiveType.Sphere, "Top", bobber, new Vector3(0f, 0.04f, 0f), new Vector3(0.12f, 0.08f, 0.12f), Palette.Bad);
            Visuals.Prim(PrimitiveType.Sphere, "Bottom", bobber, new Vector3(0f, -0.01f, 0f), new Vector3(0.12f, 0.08f, 0.12f), Palette.Rail);

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

        public void ResetForTrip()
        {
            if (State != RodState.Ready) State = RodState.Unbaited;
            BaitingBy = null;
            nibbleTimer = 0f;
            splash.gameObject.SetActive(false);
            shadow.gameObject.SetActive(false);
        }

        Vector3 LandingPoint(Transform boat, float power)
        {
            var tip = boat.TransformPoint(tipLocal);
            var outward = boat.TransformDirection(new Vector3(0.12f, 0f, -1f)).normalized;
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
            waitTimer = 0f;
            nibbles.Clear();
            nextNibble = 0;
            int n = 1 + g.State.Rng.Next(3);
            for (int i = 0; i < n; i++) nibbles.Add(1f + (float)g.State.Rng.NextDouble() * Mathf.Max(0.5f, waitTotal - 2f));
            nibbles.Sort();
        }

        public void Tick(VoyageGame g, float dt, float mult, bool attended)
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
                        g.Splash(castTo, 0.25f);
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
                        (HookedSpecies, HookedKg) = g.State.RollFish(g.ActiveSpot, Power);
                        selfHook = (float)g.State.Rng.NextDouble() < GameData.SelfHookChance;
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
                    if (t >= GameData.BiteWindow)
                    {
                        splash.gameObject.SetActive(false);
                        if (!attended && selfHook)
                        {
                            StartReel();
                            g.Toast($"Rod {Index + 1} hooked a {GameData.Get(HookedSpecies).Name.ToLower()} by itself.");
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
                            g.Toast(attended ? "Too late! It got away with the bait." : $"A fish stole the bait on rod {Index + 1}.");
                        }
                    }
                    break;

                case RodState.Reeling:
                    t += dt * mult / reelTotal;
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
                shadow.position = new Vector3(shadowPos.x, -0.312f, shadowPos.z);
                var move = shadow.position - prev;
                if (move.sqrMagnitude > 0.00001f) shadow.rotation = Quaternion.LookRotation(move.normalized);
            }
            bobber.position = bobPos;
            line.SetPosition(0, tipWorld);
            line.SetPosition(1, bobPos + Vector3.up * 0.05f);
            alert.gameObject.SetActive(State == RodState.Bite && Mathf.Repeat(anim * 6f, 1f) < 0.7f);
            alert.transform.rotation = g.Cam.transform.rotation;
        }
    }
}

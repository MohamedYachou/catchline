using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Prototype
{
    public enum JobKind { None, Work, Carry, Idle }

    // A person on deck. The deck hands out jobs; the worker walks the grid and does them.
    public class Worker
    {
        public readonly string Name;
        public readonly bool IsCaptain;
        public Station Assigned;
        public float WalkSpeed = 2.6f;
        public float WorkSpeed = 1f;

        public Transform Root { get; private set; }
        Vector3 pos; // boat-local, on the deck surface
        readonly Vector3 standOffset;
        GameObject ring, carried;

        JobKind job;
        Station target, dest;
        ItemType item;
        int phase;
        float thinkDelay;
        float animTime;
        bool moving;
        readonly List<Vector2Int> path = new();

        public Worker(string name, bool isCaptain, int index)
        {
            Name = name;
            IsCaptain = isCaptain;
            // Small per-worker offset so two people at the same spot don't merge into one.
            standOffset = new Vector3(((index % 3) - 1) * 0.16f, 0f, ((index / 3) % 2) * 0.16f - 0.08f);
        }

        public Vector2Int Tile => DeckGrid.ToTile(pos);
        public bool IsWorkingAt(Station s) => job == JobKind.Work && phase == 1 && target == s;

        public string StateText => job switch
        {
            JobKind.Work => phase == 0 ? $"walking to {target.Name}" : $"working at {target.Name}",
            JobKind.Carry => phase == 0 ? $"fetching {item} from {target.Name}" : $"carrying {item} to {dest.Name}",
            JobKind.Idle => "moving",
            _ => "waiting",
        };

        public void BuildVisual(Transform boat, Vector2Int startTile, Color suit, Color hat)
        {
            Root = new GameObject(Name).transform;
            Root.SetParent(boat, false);
            pos = DeckGrid.ToLocal(startTile) + standOffset;
            Root.localPosition = pos;

            var col = Root.gameObject.AddComponent<CapsuleCollider>();
            col.center = new Vector3(0f, 0.5f, 0f);
            col.radius = 0.32f;
            col.height = 1.1f;
            Root.gameObject.AddComponent<Clickable>().Worker = this;

            var skin = new Color(0.96f, 0.78f, 0.62f);
            Visuals.Prim(PrimitiveType.Capsule, "Body", Root, new Vector3(0f, 0.32f, 0f), new Vector3(0.36f, 0.32f, 0.3f), suit);
            Visuals.Prim(PrimitiveType.Sphere, "Head", Root, new Vector3(0f, 0.78f, 0f), Vector3.one * 0.3f, skin);
            if (IsCaptain)
            {
                Visuals.Prim(PrimitiveType.Cylinder, "Cap", Root, new Vector3(0f, 0.92f, 0f), new Vector3(0.3f, 0.05f, 0.3f), hat);
                Visuals.Box("Brim", Root, new Vector3(0f, 0.89f, 0.15f), new Vector3(0.22f, 0.02f, 0.12f), new Color(0.1f, 0.12f, 0.2f));
            }
            else
            {
                Visuals.Prim(PrimitiveType.Sphere, "Beanie", Root, new Vector3(0f, 0.88f, 0f), new Vector3(0.31f, 0.2f, 0.31f), hat);
            }
            // Facing marker so you can read which way they're walking.
            Visuals.Box("Nose", Root, new Vector3(0f, 0.78f, 0.15f), new Vector3(0.05f, 0.05f, 0.04f), skin * 0.9f);

            ring = Visuals.Prim(PrimitiveType.Cylinder, "Selected", Root, new Vector3(0f, 0.01f, 0f), new Vector3(0.75f, 0.005f, 0.75f), new Color(1f, 0.85f, 0.2f));
            ring.SetActive(false);
        }

        public void SetSelected(bool on) => ring.SetActive(on);

        // ---- jobs (started by the deck) --------------------------------------

        public void StartWork(DeckPrototype deck, Station s)
        {
            job = JobKind.Work;
            target = s;
            phase = 0;
            s.Operator = this;
            s.ReserveWork(deck);
            SetPath(deck, s.Access);
        }

        public void StartCarry(DeckPrototype deck, Station from, Station to, ItemType t)
        {
            job = JobKind.Carry;
            target = from;
            dest = to;
            item = t;
            phase = 0;
            from.Outputs[t].Reserved++;
            to.Inputs[t].Incoming++;
            SetPath(deck, from.Access);
        }

        public void StartIdle(DeckPrototype deck, Vector2Int tile)
        {
            job = JobKind.Idle;
            SetPath(deck, tile);
        }

        public void Wait(float seconds)
        {
            job = JobKind.None;
            thinkDelay = seconds;
        }

        void SetPath(DeckPrototype deck, Vector2Int goal)
        {
            path.Clear();
            var p = deck.Grid.FindPath(Tile, goal);
            if (p != null) path.AddRange(p);
        }

        // ---- per-frame --------------------------------------------------------

        public void Tick(DeckPrototype deck, float dt)
        {
            moving = false;
            switch (job)
            {
                case JobKind.None:
                    thinkDelay -= dt;
                    if (thinkDelay <= 0f) deck.AssignJob(this);
                    break;

                case JobKind.Work:
                    if (phase == 0)
                    {
                        if (Walk(dt)) phase = 1;
                    }
                    else
                    {
                        Face(target.Center);
                        target.Progress += dt * WorkSpeed / target.WorkTime;
                        if (target.Progress >= 1f)
                        {
                            target.CompleteWork(deck);
                            Wait(0.1f);
                        }
                    }
                    break;

                case JobKind.Carry:
                    if (phase == 0)
                    {
                        if (Walk(dt))
                        {
                            target.Outputs[item].Take();
                            ShowCarried(item);
                            phase = 1;
                            SetPath(deck, dest.Access);
                        }
                    }
                    else if (Walk(dt))
                    {
                        dest.Inputs[item].Deliver();
                        deck.OnDelivered(dest, item);
                        HideCarried();
                        Wait(0.1f);
                    }
                    break;

                case JobKind.Idle:
                    if (Walk(dt)) Wait(0.5f);
                    break;
            }
            Animate(dt);
        }

        // Moves along the path; true once the last tile is reached.
        bool Walk(float dt)
        {
            float budget = WalkSpeed * dt;
            while (path.Count > 0 && budget > 0f)
            {
                var goal = DeckGrid.ToLocal(path[0]) + standOffset;
                var delta = goal - pos;
                float dist = delta.magnitude;
                if (dist > 0.001f) Face(goal);
                moving = true;
                if (dist <= budget)
                {
                    pos = goal;
                    budget -= dist;
                    path.RemoveAt(0);
                }
                else
                {
                    pos += delta / dist * budget;
                    budget = 0f;
                }
            }
            return path.Count == 0;
        }

        void Face(Vector3 localTarget)
        {
            var d = localTarget - pos;
            d.y = 0f;
            if (d.sqrMagnitude > 0.0001f) Root.localRotation = Quaternion.LookRotation(d);
        }

        void Animate(float dt)
        {
            animTime += dt;
            float bob = 0f;
            if (moving) bob = Mathf.Abs(Mathf.Sin(animTime * 13f)) * 0.07f;
            else if (job == JobKind.Work && phase == 1) bob = Mathf.Abs(Mathf.Sin(animTime * 8f)) * 0.04f;
            Root.localPosition = pos + Vector3.up * bob;
        }

        void ShowCarried(ItemType t)
        {
            HideCarried();
            carried = Visuals.Box("Carried", Root, new Vector3(0f, 1.12f, 0f), Items.SizeOf(t) * 1.1f, Items.ColorOf(t));
        }

        void HideCarried()
        {
            if (carried != null) Visuals.Kill(carried);
            carried = null;
        }
    }
}

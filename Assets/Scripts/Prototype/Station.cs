using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Prototype
{
    public enum StationKind { Hauler, SortTable, BandingBench, LiveTank, PotRack }

    // A machine or work spot on deck. One worker at a time can run it; items arrive in
    // input piles and leave from output piles, carried by crew along Routes.
    public class Station
    {
        public readonly string Name;
        public readonly StationKind Kind;
        public readonly RectInt Footprint;
        public readonly Vector2Int Access;
        public readonly float WorkTime;
        public readonly float Height;

        public readonly Dictionary<ItemType, ItemBuffer> Inputs = new();
        public readonly Dictionary<ItemType, ItemBuffer> Outputs = new();
        public readonly Dictionary<ItemType, Station> Routes = new();

        public Worker Operator;
        public float Progress;
        public float BusyTime, BlockedTime, StarvedTime;

        public Transform Root { get; private set; }
        TextMesh label;
        Renderer statusLight;
        Transform progressFill;

        // The sorting table reserves room for the biggest possible catch from one pot.
        const int MaxKeepersPerPot = 3;

        public Station(string name, StationKind kind, RectInt footprint, Vector2Int access, float workTime, float height)
        {
            Name = name;
            Kind = kind;
            Footprint = footprint;
            Access = access;
            WorkTime = workTime;
            Height = height;
        }

        public Vector3 Center => new(Footprint.x + (Footprint.width - 1) / 2f, 0f, Footprint.y + (Footprint.height - 1) / 2f);

        public void BuildVisual(Transform boat, Color color)
        {
            Root = new GameObject(Name).transform;
            Root.SetParent(boat, false);
            Root.localPosition = Center;

            var size = new Vector3(Footprint.width - 0.12f, Height, Footprint.height - 0.12f);
            var body = Visuals.Box("Body", Root, new Vector3(0f, Height / 2f, 0f), size, color, keepCollider: true);
            body.AddComponent<Clickable>().Station = this;

            statusLight = Visuals.Prim(PrimitiveType.Sphere, "Status", Root,
                new Vector3(size.x / 2f - 0.08f, Height + 0.06f, -size.z / 2f + 0.08f), Vector3.one * 0.12f, Color.gray).GetComponent<Renderer>();

            if (Kind != StationKind.LiveTank)
            {
                Visuals.Box("ProgressBack", Root, new Vector3(0f, Height + 0.55f, -0.45f), new Vector3(0.8f, 0.06f, 0.06f), new Color(0.15f, 0.15f, 0.18f));
                progressFill = Visuals.Box("ProgressFill", Root, new Vector3(-0.4f, Height + 0.55f, -0.47f), new Vector3(0f, 0.07f, 0.07f), new Color(0.3f, 0.9f, 0.4f)).transform;
            }

            label = Visuals.Label("Label", Root, new Vector3(0f, Height + 0.7f, 0f), 0.034f);
        }

        public Transform AddAnchor(Vector3 offset)
        {
            var a = new GameObject("Pile").transform;
            a.SetParent(Root, false);
            a.localPosition = new Vector3(offset.x, Height, offset.z);
            return a;
        }

        public void AddInput(ItemType t, int capacity, Vector3? pileOffset)
            => Inputs[t] = new ItemBuffer(t, capacity, pileOffset.HasValue ? AddAnchor(pileOffset.Value) : null);

        public void AddOutput(ItemType t, int capacity, Vector3 pileOffset)
            => Outputs[t] = new ItemBuffer(t, capacity, AddAnchor(pileOffset));

        // ---- work rules -------------------------------------------------------

        public bool HasWork => Kind != StationKind.LiveTank;

        public bool CanStartWork(DeckPrototype deck) => Kind switch
        {
            StationKind.Hauler => deck.PotsInWater - deck.PotsBeingHauled > 0 && Outputs[ItemType.FullPot].Space >= 1,
            StationKind.SortTable => Inputs[ItemType.FullPot].Available >= 1
                                     && Outputs[ItemType.Crab].Space >= MaxKeepersPerPot
                                     && Outputs[ItemType.EmptyPot].Space >= 1,
            StationKind.BandingBench => Inputs[ItemType.Crab].Available >= 1 && Outputs[ItemType.BandedCrab].Space >= 1,
            StationKind.PotRack => Inputs[ItemType.EmptyPot].Available >= 1,
            _ => false,
        };

        public void ReserveWork(DeckPrototype deck)
        {
            switch (Kind)
            {
                case StationKind.Hauler:
                    deck.PotsBeingHauled++;
                    Outputs[ItemType.FullPot].Incoming++;
                    break;
                case StationKind.SortTable:
                    Inputs[ItemType.FullPot].Reserved++;
                    Outputs[ItemType.Crab].Incoming += MaxKeepersPerPot;
                    Outputs[ItemType.EmptyPot].Incoming++;
                    break;
                case StationKind.BandingBench:
                    Inputs[ItemType.Crab].Reserved++;
                    Outputs[ItemType.BandedCrab].Incoming++;
                    break;
                case StationKind.PotRack:
                    Inputs[ItemType.EmptyPot].Reserved++;
                    break;
            }
        }

        public void CompleteWork(DeckPrototype deck)
        {
            switch (Kind)
            {
                case StationKind.Hauler:
                    deck.PotsBeingHauled--;
                    deck.PotsInWater--;
                    Outputs[ItemType.FullPot].Produce(1, 1);
                    break;
                case StationKind.SortTable:
                    Inputs[ItemType.FullPot].Consume();
                    Outputs[ItemType.Crab].Produce(deck.RollKeepers(), MaxKeepersPerPot);
                    Outputs[ItemType.EmptyPot].Produce(1, 1);
                    break;
                case StationKind.BandingBench:
                    Inputs[ItemType.Crab].Consume();
                    Outputs[ItemType.BandedCrab].Produce(1, 1);
                    break;
                case StationKind.PotRack:
                    // Restacked pots are rebaited and go straight back over the side.
                    Inputs[ItemType.EmptyPot].Consume();
                    deck.PotsInWater++;
                    break;
            }
            Progress = 0f;
            Operator = null;
        }

        // Base priority for a free worker choosing between stations.
        public float WorkScore(DeckPrototype deck)
        {
            if (Kind == StationKind.Hauler) return 0.35f + 0.3f * deck.PotsInWater / DeckPrototype.TotalPots;
            float fill = 0f;
            foreach (var b in Inputs.Values) fill = Mathf.Max(fill, b.Fill);
            return 0.3f + fill;
        }

        // Free room in an output pile, ignoring space a worker has already promised.
        int Room(ItemType t) => Outputs[t].Capacity - Outputs[t].Count;

        bool OutputBlocked()
        {
            return Kind switch
            {
                StationKind.Hauler => Room(ItemType.FullPot) < 1,
                StationKind.SortTable => Room(ItemType.Crab) < MaxKeepersPerPot || Room(ItemType.EmptyPot) < 1,
                StationKind.BandingBench => Room(ItemType.BandedCrab) < 1,
                StationKind.LiveTank => Inputs[ItemType.BandedCrab].Count >= Inputs[ItemType.BandedCrab].Capacity,
                _ => false,
            };
        }

        // ---- per-frame state, stats and visuals -------------------------------

        public void Tick(DeckPrototype deck, float dt, Quaternion faceCamera)
        {
            bool working = Operator != null && Operator.IsWorkingAt(this);
            bool blocked = OutputBlocked();

            if (working) BusyTime += dt;
            else if (blocked) BlockedTime += dt;
            else StarvedTime += dt;

            string state;
            Color light, text;
            if (Kind == StationKind.LiveTank)
            {
                var tank = Inputs[ItemType.BandedCrab];
                state = blocked ? "FULL - sell catch" : $"{tank.Count}/{tank.Capacity} crabs";
                light = blocked ? new Color(0.95f, 0.25f, 0.2f) : new Color(0.3f, 0.75f, 0.95f);
                text = blocked ? new Color(1f, 0.45f, 0.4f) : Color.white;
            }
            else if (working)
            {
                state = "working";
                light = new Color(0.3f, 0.95f, 0.4f);
                text = Color.white;
            }
            else if (Operator != null)
            {
                state = "crew on the way";
                light = new Color(0.95f, 0.85f, 0.3f);
                text = Color.white;
            }
            else if (blocked)
            {
                state = "OUTPUT FULL";
                light = new Color(0.95f, 0.25f, 0.2f);
                text = new Color(1f, 0.45f, 0.4f);
            }
            else if (Kind == StationKind.Hauler && deck.PotsInWater == 0)
            {
                state = "no pots in the water";
                light = Color.gray;
                text = new Color(0.8f, 0.8f, 0.8f);
            }
            else if (CanStartWork(deck))
            {
                state = "needs a worker";
                light = new Color(0.95f, 0.65f, 0.2f);
                text = new Color(1f, 0.8f, 0.4f);
            }
            else
            {
                state = "waiting for input";
                light = Color.gray;
                text = new Color(0.8f, 0.8f, 0.8f);
            }

            int queue = 0;
            if (Kind != StationKind.LiveTank)
                foreach (var b in Inputs.Values) queue += b.Count;
            string queueText = queue >= 2 ? $"  queue {queue}" : "";

            label.text = $"{Name}\n{state}{queueText}";
            label.color = text;
            label.transform.rotation = faceCamera;
            statusLight.sharedMaterial = Visuals.Mat(light);

            if (progressFill != null)
            {
                float p = Mathf.Clamp01(Progress);
                progressFill.localScale = new Vector3(0.8f * p, 0.07f, 0.07f);
                progressFill.localPosition = new Vector3(-0.4f + 0.4f * p, Height + 0.55f, -0.47f);
            }
        }

        public string Report(float simTime)
        {
            float t = Mathf.Max(0.001f, simTime);
            string piles = "";
            foreach (var b in Inputs.Values) piles += $" in:{b.Type}={b.Count}/{b.Capacity}";
            foreach (var b in Outputs.Values) piles += $" out:{b.Type}={b.Count}/{b.Capacity}";
            return $"{Name,-14} busy {BusyTime / t:P0}  blocked {BlockedTime / t:P0}  idle {StarvedTime / t:P0} |{piles}";
        }
    }
}

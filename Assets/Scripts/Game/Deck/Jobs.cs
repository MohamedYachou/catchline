using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game.Deck
{
    // One job system for every hull (docs/MASTER-PLAN.md B3).
    public enum JobKind { Haul, Sort, TableWork, RodCycle, NetCycle, CageCycle, LineCycle, JigCycle, Relocate, EventResponse }
    public enum Duty { Haul, Sort, Table }

    // What the scheduler needs from a body on deck. Person implements it through an adapter in the game;
    // checks use a simulated actor.
    public interface IDeckActor
    {
        Vector2Int Tile { get; }
        bool WalkTo(Vector2Int tile, Action arrive, Action cancel);
        void Act(string label, float seconds, Action done, Action cancel);
        void Stop();
    }

    public sealed class Worker
    {
        public string Name;
        public bool Captain;
        public CrewRole Role;
        public IDeckActor Actor;
        public Duty Primary = Duty.Haul, Secondary = Duty.Sort;
        Duty? pendingPrimary, pendingSecondary;
        public Job Current;
        public readonly List<CaughtFish> Hands = new();
        // Hand capacity (B3): at most three fish or 6 kg.
        public int HandCount = 3;
        public float HandKg = 6f;
        public Station Operating; // fishers: the gear station they run

        // Duties switch after the current job (M1 acceptance).
        public void SetDuties(Duty primary, Duty secondary)
        {
            if (Current == null) { Primary = primary; Secondary = secondary; pendingPrimary = pendingSecondary = null; }
            else { pendingPrimary = primary; pendingSecondary = secondary; }
        }
        internal void ApplyPending()
        {
            if (pendingPrimary.HasValue) Primary = pendingPrimary.Value;
            if (pendingSecondary.HasValue) Secondary = pendingSecondary.Value;
            pendingPrimary = pendingSecondary = null;
        }
        public bool Idle => Current == null;
    }

    // Where carried fish go. The hold and overboard are sinks; baskets take a reserved slot.
    public sealed class Drop
    {
        public Basket Basket;
        public Station Station;      // access point (basket owner or the hold hatch)
        public bool Hold, Overboard;
        public static Drop To(Basket b) => new() { Basket = b, Station = b.Owner };
    }

    public sealed class Job
    {
        public JobKind Kind;
        public Worker Worker;
        public Basket Source;
        public readonly List<CaughtFish> Fish = new();
        public Drop Target;
        public Station At;
        public string Label;
        public bool Started, Finished, Cancelled;
        internal int reserved;
        public override string ToString() => $"{Kind} {Fish.Count} fish {Source?.Id}→{(Target?.Hold == true ? "hold" : Target?.Overboard == true ? "overboard" : Target?.Basket?.Id)}";
    }

    // Sort decision for one fish (B2 routing): undersize and thrown classes go back; the rest go to SortOut,
    // flagged for the table when the table wants them.
    public enum SortOutcome { Throw, Keep, Table }
}

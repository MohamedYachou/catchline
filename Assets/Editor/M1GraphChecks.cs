using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEngine;

namespace Catchline.EditorTools
{
    // M1 core (docs/MASTER-PLAN.md M1): station files load for all five hulls, every station is reachable,
    // and the scheduler moves fish rod → RodOut → SortIn → SortOut → hold with one claim at a time,
    // throwing undersize back and losing nothing when a carry is cancelled.
    public static class M1GraphChecks
    {
        static void Check(bool ok, string what) { if (!ok) throw new Exception("[Catchline] M1 check failed: " + what); }

        // Simulated body: walks at 1.2 m/s along the cached path; acts take their seconds.
        sealed class SimActor : IDeckActor
        {
            public Vector2Int Tile { get; set; }
            readonly DeckGraph deck; public readonly SimClock Clock;
            public SimActor(DeckGraph d, SimClock c, Vector2Int t) { deck = d; Clock = c; Tile = t; }
            public bool WalkTo(Vector2Int tile, Action arrive, Action cancel)
            {
                if (!deck.Reachable(Tile, tile)) return false;
                float seconds = deck.Distance(Tile, tile) / 1.2f; var to = tile;
                Clock.After(seconds, this, () => { Tile = to; arrive(); });
                return true;
            }
            public void Act(string label, float seconds, Action done, Action cancel) => Clock.After(seconds, this, done);
            public void Stop() => Clock.Drop(this);
        }
        sealed class SimClock
        {
            public float Now;
            readonly List<(float at, object owner, Action act)> queue = new();
            public void After(float s, object owner, Action a) => queue.Add((Now + s, owner, a));
            public void Drop(object owner) => queue.RemoveAll(q => q.owner == owner);
            public void Advance(float dt)
            {
                float end = Now + dt;
                for (;;)
                {
                    var due = queue.Where(q => q.at <= end).OrderBy(q => q.at).FirstOrDefault();
                    if (due.act == null) break;
                    queue.Remove(due); Now = due.at; due.act();
                }
                Now = end;
            }
        }

        static CaughtFish Fish(Species s, float t) { var d = GameData.Get(s); return new CaughtFish { Species = s, Kg = Mathf.Lerp(d.MinKg, d.MaxKg, t) }; }

        public static void Run()
        {
            for (int h = 0; h < GameData.Hulls.Length; h++)
            {
                var hull = GameData.Hulls[h];
                var deck = DeckGraph.Load(hull);
                Check(deck != null, hull.Model + " station file in ArtLibrary");
                Check(deck.Hold != null && deck.OfKind(StationKind.SortTable).Any(), hull.Model + " has hold and sort table");
                var from = deck.Access(deck.Hold);
                foreach (var s in deck.Stations)
                    Check(deck.Reachable(from, deck.Access(s)), $"{hull.Model} {s.Id} reachable from the hold");
                foreach (var g in deck.Stations.Where(s => s.IsGear))
                    Check(g.Out != null, $"{hull.Model} {g.Id} has an output basket");
                Flow(hull, deck);
                Debug.Log($"[Catchline] M1 {hull.Model}: {deck.Stations.Count} stations, {deck.Baskets.Count} baskets reachable; flow ok");
            }
            Debug.Log("[Catchline] M1 GRAPH CHECKS PASSED");
        }

        static void Flow(HullDef hull, DeckGraph deck)
        {
            var clock = new SimClock();
            var sched = new DeckScheduler(deck);
            var stowed = new List<CaughtFish>(); var thrown = new List<CaughtFish>();
            sched.OnStowed = stowed.Add; sched.OnThrown = thrown.Add;
            var hold = deck.Access(deck.Hold);
            var hauler = new Worker { Name = "Hauler", Role = CrewRole.Deckhand, Primary = Duty.Haul, Secondary = Duty.Sort, Actor = new SimActor(deck, clock, hold) };
            var sorter = new Worker { Name = "Sorter", Role = CrewRole.Deckhand, Primary = Duty.Sort, Secondary = Duty.Haul, Actor = new SimActor(deck, clock, hold) };
            sched.Workers.Add(hauler); sched.Workers.Add(sorter);
            var rod = deck.OfKind(StationKind.Rod).First();
            var keep = Fish(Species.Mackerel, .9f); var small = Fish(Species.Mackerel, .05f);
            sched.Land(rod, keep); sched.Land(rod, small);
            var claimed = new HashSet<CaughtFish>();
            for (int t = 0; t < 1200 && stowed.Count + thrown.Count < 2; t++)
            {
                sched.Tick(); clock.Advance(.1f);
                Check(sched.Balanced, hull.Model + " no fish lost or duplicated");
                foreach (var w in sched.Workers) if (w.Current != null) foreach (var f in w.Current.Fish) Check(!sched.Workers.Any(o => o != w && o.Current != null && o.Current.Fish.Contains(f)), "one claim per fish");
            }
            Check(stowed.Contains(keep), hull.Model + " keeper reaches the hold through the sort table");
            Check(thrown.Contains(small) && !stowed.Contains(small), hull.Model + " undersize never reaches the hold");

            // Cancelling mid-carry loses no fish.
            var a = Fish(Species.Herring, .8f); var b = Fish(Species.Herring, .9f);
            sched.Land(rod, a); sched.Land(rod, b);
            for (int t = 0; t < 400 && !sched.Workers.Any(w => w.Hands.Count > 0); t++) { sched.Tick(); clock.Advance(.05f); }
            var carrier = sched.Workers.FirstOrDefault(w => w.Hands.Count > 0);
            Check(carrier != null, hull.Model + " a carry starts");
            sched.Cancel(carrier.Current);
            Check(sched.Balanced && carrier.Hands.Count == 0, hull.Model + " cancel mid-carry keeps every fish");

            // Duties switch after the current job, not during it.
            sched.Tick(); clock.Advance(.05f);
            var busy = sched.Workers.FirstOrDefault(w => w.Current != null);
            if (busy != null)
            {
                var before = busy.Primary; busy.SetDuties(Duty.Table, Duty.Haul);
                Check(busy.Primary == before, hull.Model + " duty change waits for the current job");
            }
            for (int t = 0; t < 1200 && sched.OnDeck > 0; t++) { sched.Tick(); clock.Advance(.1f); Check(sched.Balanced, hull.Model + " balanced while clearing"); }
            Check(sched.OnDeck == 0, hull.Model + " deck clears (" + sched.OnDeck + " left)");
        }
    }
}

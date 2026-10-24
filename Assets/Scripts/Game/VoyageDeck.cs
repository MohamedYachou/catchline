using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game.Deck;
using Catchline.Prototype;
using UnityEngine;
using Station = Catchline.Game.Deck.Station;
using StationKind = Catchline.Game.Deck.StationKind;
using Worker = Catchline.Game.Deck.Worker;

namespace Catchline.Game
{
    // M1 bridge: the deck graph and job scheduler drive the existing crew bodies.
    // Hulls migrate one at a time (rowboat → skiff → compact → prep → buoy); a hull not yet
    // migrated keeps its legacy worker code untouched.
    public partial class VoyageGame
    {
        // Hull models already running on the deck graph. Grows as each hull migrates.
        static readonly HashSet<string> DeckGraphHulls = new();
        public DeckGraph DeckGraph { get; private set; }
        public DeckScheduler Scheduler { get; private set; }
        public bool UsesDeckGraph => Scheduler != null;
        public int ThrownBack { get; private set; } // undersize and keep-rule throwbacks this voyage (log only, exempt from quota)
        readonly Dictionary<Person, Worker> workers = new();
        readonly Dictionary<CaughtFish, Transform> basketFish = new();

        // Person as a scheduler body: walks on the station-file grid, acts with the existing Do().
        sealed class PersonActor : IDeckActor
        {
            readonly Person person; readonly DeckGrid grid;
            public PersonActor(Person p, DeckGrid g) { person = p; grid = g; }
            public Vector2Int Tile => person.Tile;
            public bool WalkTo(Vector2Int tile, Action arrive, Action cancel) => person.WalkTo(grid, tile, arrive, cancel);
            public void Act(string label, float seconds, Action done, Action cancel) => person.Do(label, seconds, done, cancel);
            public void Stop() => person.Stop();
        }

        // Called after the boat and crew are built for a voyage.
        void SetupDeckGraph()
        {
            DeckGraph = null; Scheduler = null; workers.Clear(); ThrownBack = 0;
            foreach (var t in basketFish.Values) if (t != null) Visuals.Kill(t.gameObject);
            basketFish.Clear();
            if (!DeckGraphHulls.Contains(State.HullDef.Model)) return;
            DeckGraph = DeckGraph.Load(State.HullDef);
            if (DeckGraph == null) { Debug.LogWarning("[Catchline] No station file for " + State.HullDef.Model + "; legacy deck code stays active."); return; }
            Scheduler = new DeckScheduler(DeckGraph)
            {
                HoldRemainingKg = () => State.CoolerCapacity - HoldKg,
                OnStowed = f => { HideBasketFish(f); DeliverCatch(f); lidPop = 1f; },
                OnThrown = f => { HideBasketFish(f); ThrownBack++; },
            };
            SyncDeckWorkers();
        }

        void SyncDeckWorkers()
        {
            if (Scheduler == null) return;
            foreach (var p in People)
            {
                if (workers.ContainsKey(p)) continue;
                var w = new Worker
                {
                    Name = p.Name, Captain = p == Captain, Role = p == Captain ? CrewRole.Deckhand : p.Contract.Role, Actor = new PersonActor(p, DeckGraph.Grid),
                    Primary = p.Contract?.WorkPreference == DeckhandWork.Prep ? Duty.Table : Duty.Haul, Secondary = Duty.Sort,
                };
                workers[p] = w; Scheduler.Workers.Add(w);
            }
            foreach (var gone in workers.Keys.Where(p => !People.Contains(p)).ToList())
            {
                var w = workers[gone]; if (w.Current != null) Scheduler.Cancel(w.Current);
                Scheduler.Workers.Remove(w); workers.Remove(gone);
            }
        }

        void TickDeckGraph()
        {
            if (Scheduler == null || CurrentMode != Mode.Fishing) return;
            Scheduler.Tick();
            PlaceBasketFish();
        }

        // Gear lands into its station's basket (or loose beside it when big). Returns false when nothing could land.
        bool LandOnDeck(Station gear, Species s, float kg)
        {
            var fish = new CaughtFish { Species = s, Kg = kg, StowedAt = SimTime };
            Scheduler.Land(gear, fish);
            var model = DeckFish.BuildModel(s, kg, Boat);
            basketFish[fish] = model;
            return true;
        }
        public Station GearStation(StationKind kind, int index) => DeckGraph?.OfKind(kind).ElementAtOrDefault(index);

        // Fish models sit in their basket (stacked), loose beside the station, or in a worker's hands.
        void PlaceBasketFish()
        {
            foreach (var b in DeckGraph.Baskets)
                for (int i = 0; i < b.Fish.Count; i++)
                    if (basketFish.TryGetValue(b.Fish[i], out var t) && t != null)
                    {
                        if (t.parent != Boat) t.SetParent(Boat, false);
                        t.localPosition = b.Position + new Vector3((i % 3 - 1) * .07f, .06f + i / 3 * .05f, (i % 2) * .05f);
                    }
            foreach (var lf in Scheduler.Loose)
                if (basketFish.TryGetValue(lf.Fish, out var t) && t != null)
                {
                    if (t.parent != Boat) t.SetParent(Boat, false);
                    t.localPosition = DeckGraph.Grid.GetLocal(lf.Tile) + new Vector3(0, .07f, 0);
                }
            foreach (var kv in workers)
                for (int i = 0; i < kv.Value.Hands.Count; i++)
                    if (basketFish.TryGetValue(kv.Value.Hands[i], out var t) && t != null && t.parent != kv.Key.Root)
                    {
                        t.SetParent(kv.Key.Root, false);
                        t.localPosition = new Vector3(0, .55f + i * .06f, .22f);
                    }
        }

        void HideBasketFish(CaughtFish f)
        {
            if (basketFish.TryGetValue(f, out var t)) { if (t != null) Visuals.Kill(t.gameObject); basketFish.Remove(f); }
        }

        // ---- captain commands (player taps) ---------------------------------------------------

        public bool CaptainKeepAtSort(bool keep)
        {
            if (Scheduler == null || !workers.TryGetValue(Captain, out var w)) return false;
            var sort = DeckGraph.OfKind(StationKind.SortTable).FirstOrDefault(s => s.In.UnclaimedCount > 0);
            return sort != null && Scheduler.CaptainSort(w, sort, keep);
        }
        public bool CaptainHaulFrom(Basket b) => Scheduler != null && workers.TryGetValue(Captain, out var w) && Scheduler.CaptainHaul(w, b);
    }
}

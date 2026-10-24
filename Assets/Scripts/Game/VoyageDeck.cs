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
    // Hulls migrate one at a time (rowboat â†’ skiff â†’ compact â†’ prep â†’ buoy); a hull not yet
    // migrated keeps its legacy worker code untouched.
    public partial class VoyageGame
    {
        // Hull models already running on the deck graph. Grows as each hull migrates.
        static readonly HashSet<string> DeckGraphHulls = new() { "Rowboat", "Skiff", "CompactFisherV1", "PrepFisherV1", "Tier5DeepLines103" };
        public DeckGraph DeckGraph { get; private set; }
        public DeckScheduler Scheduler { get; private set; }
        public bool UsesDeckGraph => Scheduler != null;
        public int ThrownBack { get; private set; } // undersize and keep-rule throwbacks this voyage (log only, exempt from quota)
        readonly Dictionary<Person, Worker> workers = new();
        readonly Dictionary<CaughtFish, Transform> basketFish = new();

        // Person as a scheduler body: walks on the station-file grid, acts with the existing Do().
        sealed class PersonActor : IDeckActor
        {
            readonly Person person; readonly DeckGrid grid; readonly CardState card;
            public PersonActor(Person p, DeckGrid g, CardState c) { person = p; grid = g; card = c; }
            void Skill(Speciality job)
            {
                person.Skill = card == null ? 100 : CardProgression.Skill(card.Def,card.Rarity,job);
                person.LevelMult = card == null ? 1 : CardProgression.LevelMult(card.Level);
                if (card != null && ((job == Catchline.Game.Speciality.Sort && (card.Id == "noor" || card.Id == "tove")) || (job == Catchline.Game.Speciality.Table && card.Id == "mats") || (job == Catchline.Game.Speciality.Haul && card.Id == "ana"))) person.Skill *= 1.1f;
            }
            public Vector2Int Tile => person.Tile;
            public bool WalkTo(Vector2Int tile, Action arrive, Action cancel) { Skill(Catchline.Game.Speciality.Haul); return person.WalkTo(grid, tile, arrive, cancel); }
            public void Act(string label, float seconds, Action done, Action cancel) { Skill(label == "Sorting" ? Catchline.Game.Speciality.Sort : label == "Processing" ? Catchline.Game.Speciality.Table : Catchline.Game.Speciality.Haul); person.Do(label, seconds, done, cancel); }
            public void Stop() => person.Stop();
        }

        // Called after the boat and crew are built for a voyage.
        void SetupDeckGraph()
        {
            DeckGraph = null; Scheduler = null; workers.Clear(); ThrownBack = 0;
            foreach (var t in basketFish.Values) if (t != null) Visuals.Kill(t.gameObject);
            basketFish.Clear();
            foreach (var t in stationProps) if (t != null) Visuals.Kill(t.gameObject);
            stationProps.Clear();
            if (!DeckGraphHulls.Contains(State.HullDef.Model)) return;
            DeckGraph = DeckGraph.Load(State.HullDef);
            if (DeckGraph == null) { Debug.LogWarning("[Catchline] No station file for " + State.HullDef.Model + "; legacy deck code stays active."); return; }
            // Idle movement and gear operators must use the same walkability as hauling jobs.
            Grid = DeckGraph.Grid;
            foreach (var p in People) { p.Stop(); p.Grid = Grid; p.Place(DeckGraph.Nearest(p.Tile)); }
            Scheduler = new DeckScheduler(DeckGraph)
            {
                HoldRemainingKg = () => State.CoolerCapacity - HoldKg,
                OnStowed = f => { HideBasketFish(f); TryStore(f); lidPop = 1f; },
                OnThrown = f => { HideBasketFish(f); ThrownBack++; },
            };
            SyncDeckWorkers();
            SpawnStationProps();
        }

        // Station props from Codex's StationsV1 kit (sort board, bait bin, hatch ring, navigator bracket, baskets).
        readonly List<Transform> stationProps = new();
        readonly Dictionary<Basket, (Transform t, int fill)> basketProps = new();
        void SpawnStationProps()
        {
            basketProps.Clear();
            var lib = ArtLibrary.Get();
            foreach (var s in DeckGraph.Stations)
            {
                var prefab = s.ModelId != null ? lib?.M(s.ModelId) : null;
                if (prefab == null) continue;
                var go = ArtLibrary.Spawn(prefab, Boat, s.Position, Quaternion.Euler(0, s.Yaw, 0));
                if (go != null) stationProps.Add(go.transform);
            }
            foreach (var b in DeckGraph.Baskets) SetBasketProp(b);
        }
        // Baskets show 0-3 fill states (empty, a few, half, full).
        void SetBasketProp(Basket b)
        {
            if (b.Kind is BasketKind.SortIn or BasketKind.SortOut or BasketKind.TableIn or BasketKind.TableOut && b.Owner.ModelId != null) return; // the bench model carries its trays
            int fill = b.Count == 0 ? 0 : b.Fill < .34f ? 1 : b.Fill < .99f ? 2 : 3;
            if (basketProps.TryGetValue(b, out var cur) && cur.fill == fill) return;
            if (cur.t != null) Visuals.Kill(cur.t.gameObject);
            string prefix = b.Owner.BasketPrefix ?? (b.CapacityCount > 8 ? "Art108_BasketLarge" : "Art108_BasketSmall");
            var prefab = ArtLibrary.Get()?.M(prefix + "_" + fill);
            var go = prefab != null ? ArtLibrary.Spawn(prefab, Boat, b.Position, Quaternion.identity) : null;
            basketProps[b] = (go != null ? go.transform : null, fill);
            if (go != null) stationProps.Add(go.transform);
        }

        // Heading home: keepers still on deck go to the hold if there is room; undersize goes back.
        void FlushDeckGraph()
        {
            if (Scheduler == null) return;
            Scheduler.CancelAll();
            var all = DeckGraph.Baskets.SelectMany(b => b.Fish).Concat(Scheduler.Loose.Select(l => l.Fish)).ToList();
            foreach (var f in all) if (!FishRules.Undersize(f)) TryStore(f);
            foreach (var t in basketFish.Values) if (t != null) Visuals.Kill(t.gameObject);
            foreach (var t in stationProps) if (t != null) Visuals.Kill(t.gameObject);
            basketFish.Clear(); stationProps.Clear(); basketProps.Clear();
            DeckGraph = null; Scheduler = null; workers.Clear();
        }

        void SyncDeckWorkers()
        {
            if (Scheduler == null) return;
            foreach (var p in People)
            {
                if (workers.ContainsKey(p)) continue;
                var w = new Worker
                {
                    Name = p.Name, Captain = p == Captain, Role = p == Captain ? CrewRole.Deckhand : p.Contract.Role, Card = CardFor(p.Contract), Actor = new PersonActor(p, DeckGraph.Grid, CardFor(p.Contract)),
                    HandCount = CardFor(p.Contract)?.Id == "sam" ? 4 : 3,
                    Available = () => p.Idle || p.Loitering,
                    Primary = p.Contract?.WorkPreference == DeckhandWork.Prep ? Duty.Table : p.Contract?.WorkPreference == DeckhandWork.Nets ? Duty.Sort : Duty.Haul, Secondary = Duty.Sort,
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
            if (Scheduler == null || CurrentMode == Mode.Harbour) return;
            SyncDeckWorkers();
            Scheduler.Tick();
            CaptainFollowUp();
            PlaceBasketFish();
            foreach (var b in DeckGraph.Baskets) SetBasketProp(b);
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
            if (sort == null || !Scheduler.CaptainSort(w, sort, keep)) return false;
            Manning = null; AwaitingCast = false;
            return true;
        }
        // Keep finishes by stowing. An idle captain can also bring rod catches to the sort table.
        void CaptainFollowUp()
        {
            if (Scheduler == null || !workers.TryGetValue(Captain, out var w) || !w.Idle) return;
            if (keepThenStow)
            {
                var outBasket = DeckGraph.OfKind(StationKind.SortTable).Select(s => s.Out).FirstOrDefault(b => b != null && b.UnclaimedCount > 0);
                keepThenStow = false;
                if (outBasket != null && Scheduler.CaptainHaul(w, outBasket)) return;
            }
            if (!AutoCarryCatch || CurrentMode != Mode.Fishing || !Captain.Idle || Captain.Carrying != null
                || MinigameRod != null || Manning != null && Manning.State is RodState.Bite or RodState.Reeling) return;
            foreach (var basket in DeckGraph.OfKind(StationKind.Rod).Select(s => s.Out).Where(b => b != null && b.UnclaimedCount > 0))
                if (CaptainHaulFrom(basket))
                {
                    Manning = null; AwaitingCast = false;
                    return;
                }
        }
        bool keepThenStow;
        public void CommandKeep(bool keep)
        {
            if (!CaptainKeepAtSort(keep)) return;
            keepThenStow = keep;
        }
        // Tap bubbles on migrated hulls: Carry at a basket, Stow from the sorted tray. Keep / Throw are screen buttons.
        void InterfaceDeckBubbles()
        {
            if (Scheduler == null || !workers.TryGetValue(Captain, out var cap) || !cap.Idle) return;
            foreach (var b in DeckGraph.Baskets.Where(b => b.Owner.IsGear && b.Owner.Out == b && b.UnclaimedCount > 0))
                InterfaceBubble("deck/carry/" + b.Id, Boat.TransformPoint(b.Position + Vector3.up * .35f), b.UnclaimedCount > 1 ? $"Carry {b.UnclaimedCount}" : "Carry", "icon-fish",
                    () => { Manning = null; AwaitingCast = false; CaptainHaulFrom(b); });
            foreach (var s in DeckGraph.OfKind(StationKind.SortTable))
                if ((s.In == null || s.In.UnclaimedCount == 0) && s.Out != null && s.Out.UnclaimedCount > 0 && !HasDeckhand)
                    InterfaceBubble("deck/stow/" + s.Id, Boat.TransformPoint(s.Position + Vector3.up * .45f), "Stow", "icon-fish", () => CaptainHaulFrom(s.Out));
        }
        // A fish on the sort table: Throw and Keep as big buttons at the left and right of the open water,
        // drawn after the catch card so it never covers them, and level with the middle of the screen, clear of it.
        void InterfaceSortDecision()
        {
            if (CurrentMode != Mode.Fishing || Scheduler == null || !workers.TryGetValue(Captain, out var cap) || !cap.Idle) return;
            if (!DeckGraph.OfKind(StationKind.SortTable).Any(s => s.In != null && s.In.UnclaimedCount > 0)) return;
            float w = compactInterface ? 100 : 150, h = compactInterface ? 72 : 96, y = ih / 2 - h / 2;
            var left = new Rect(HudGapLeft, y, w, h); var right = new Rect(HudGapRight - w, y, w, h);
            coastalUi.Primary("deck/throw", left, "Throw", () => { CommandKeep(false); MenuSound(); }); Block(left);
            coastalUi.Secondary("deck/keep", right, "Keep", () => { CommandKeep(true); MenuSound(); }); Block(right);
        }

        public bool CaptainHaulFrom(Basket b) => Scheduler != null && workers.TryGetValue(Captain, out var w) && Scheduler.CaptainHaul(w, b);
    }
}


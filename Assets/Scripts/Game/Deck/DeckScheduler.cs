using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game.Deck
{
    // Scheduler (docs/MASTER-PLAN.md B3): idle deckhands take the highest-pressure job of their primary
    // duty (fullest basket, then nearest), else their secondary. Fishers run their station's cycle elsewhere;
    // the captain only does what the player taps. Fish keep their identity; every move is claim-checked.
    public sealed class DeckScheduler
    {
        public readonly DeckGraph Deck;
        public bool Sailing; // Transit permits sorting and stowing, never processing.
        public readonly List<Worker> Workers = new();
        public sealed class LooseFish { public CaughtFish Fish; public Vector2Int Tile; public object Claim; }
        public readonly List<LooseFish> Loose = new();
        readonly HashSet<CaughtFish> forTable = new();

        // Keep rule and table orders live outside; default is undersize back, purple+ to a table when fitted.
        public Func<CaughtFish, SortOutcome> Decide;
        public Func<float> HoldRemainingKg = () => float.MaxValue;
        public Action<CaughtFish> OnStowed, OnThrown;
        public Action<Job, CaughtFish> OnTableDone; // M3 product chain; default passes the fish on to TableOut
        // Seconds for one act; the game wires these to the one work-speed model (CARDS-AND-SPEEDS §1, §4).
        public Func<Worker, JobKind, float> ActSeconds = (w, k) => k switch { JobKind.Sort => 1.2f, JobKind.TableWork => 3f, _ => .5f };
        public Func<Worker, float> StowSeconds = w => .6f;

        // Integrity: every landed fish is somewhere; nothing is duplicated or lost.
        public int Landed, Stowed, Thrown;
        public int OnDeck => Deck.Baskets.Sum(b => b.Count) + Loose.Count + Workers.Sum(w => w.Hands.Count);
        public bool Balanced => Landed == Stowed + Thrown + OnDeck;

        public DeckScheduler(DeckGraph deck)
        {
            Deck = deck;
            Decide = f => FishRules.Undersize(f) ? SortOutcome.Throw
                : FishRules.Class(f) >= FishClass.Purple && Deck.OfKind(StationKind.ProcessTable).Any() ? SortOutcome.Table : SortOutcome.Keep;
        }

        // ---- landing ------------------------------------------------------------------------

        // Gear lands a fish into its basket, or loose beside the station when it is too big or the basket is full.
        public bool Land(Station gear, CaughtFish f)
        {
            Landed++;
            if (gear.Out != null && FishRules.FitsBasket(f) && gear.Out.Put(f, false)) return true;
            Loose.Add(new LooseFish { Fish = f, Tile = Deck.Access(gear) });
            return gear.Out != null && FishRules.FitsBasket(f); // false: oversize fish, deck tile now blocked by it
        }
        public bool GearCanLand(Station gear) => gear.Out == null || !gear.Out.Full;

        // ---- scheduling ---------------------------------------------------------------------

        public void Tick()
        {
            foreach (var w in Workers)
            {
                if (!w.Idle || w.Captain || w.Role == CrewRole.Fisherman || w.Role == CrewRole.Navigator || !w.Available()) continue;
                w.ApplyPending();
                var job = Pick(w);
                if (job != null) Start(job);
            }
        }

        IEnumerable<Duty> Duties(Worker w) => w.Role == CrewRole.Engineer ? new[] { Duty.Haul } : new[] { w.Primary, w.Secondary };

        public Job Pick(Worker w)
        {
            foreach (var duty in Duties(w).Distinct())
            {
                var job = duty switch { Duty.Sort => PickSort(w), Duty.Table => PickTable(w), _ => PickHaul(w) };
                if (job != null) return job;
            }
            return null;
        }

        float Dist(Worker w, Station s) => Deck.Distance(w.Actor.Tile, Deck.Access(s));

        Job PickSort(Worker w)
        {
            var s = Deck.OfKind(StationKind.SortTable).Where(t => t.Worker == null && t.In != null && t.Out != null && t.In.UnclaimedCount > 0 && t.Out.Free > 0)
                .OrderByDescending(t => t.In.Fill).ThenBy(t => Dist(w, t)).FirstOrDefault();
            if (s == null) return null;
            var job = new Job { Kind = JobKind.Sort, Worker = w, Source = s.In, At = s, Label = "Sorting", Target = Drop.To(s.Out) };
            var batch = s.In.Unclaimed.Take(w.WholeBasket ? s.Out.Free : 1).ToList();
            foreach (var f in batch)
            {
                if (!s.In.Claim(f,job)) continue;
                job.Fish.Add(f);
            }
            if (job.Fish.Count == 0 || !s.Out.Reserve(job.Fish.Count))
            { foreach (var f in job.Fish) s.In.Release(f,job); return null; }
            job.reserved = job.Fish.Count; s.Worker = w;
            return job;
        }

        Job PickTable(Worker w)
        {
            if (Sailing) return null;
            var s = Deck.OfKind(StationKind.ProcessTable).Where(t => t.In != null && t.Out != null && t.In.UnclaimedCount > 0 && t.Out.Free > 0
                    && Workers.Count(o => o.Current?.At == t && o.Current.Kind == JobKind.TableWork) < t.Places)
                .OrderByDescending(t => t.In.Fill).ThenBy(t => Dist(w, t)).FirstOrDefault();
            if (s == null) return null;
            var job = new Job { Kind = JobKind.TableWork, Worker = w, Source = s.In, At = s, Label = "Processing", Target = Drop.To(s.Out) };
            var f = s.In.Unclaimed.First();
            if (!s.In.Claim(f, job) || !s.Out.Reserve(1)) { s.In.Release(f, job); return null; }
            job.Fish.Add(f); job.reserved = 1;
            return job;
        }

        // Where fish from a basket go next.
        Drop NextFor(Basket from, CaughtFish f)
        {
            switch (from.Kind)
            {
                case BasketKind.SortOut:
                    if (forTable.Contains(f))
                    {
                        if (Sailing) return null;
                        var table = Deck.OfKind(StationKind.ProcessTable).Where(t => t.In != null && t.In.Free > 0).OrderBy(t => (t.Position - from.Position).sqrMagnitude).FirstOrDefault();
                        if (table != null) return Drop.To(table.In);
                    }
                    return HoldDrop();
                case BasketKind.TableOut: return HoldDrop();
                default:
                    var sort = Deck.OfKind(StationKind.SortTable).Where(t => t.In != null && t.In.Free > 0).OrderBy(t => (t.Position - from.Position).sqrMagnitude).FirstOrDefault();
                    return sort != null ? Drop.To(sort.In) : Deck.OfKind(StationKind.SortTable).Any() ? null : HoldDrop();
            }
        }
        Drop HoldDrop() => Deck.Hold != null ? new Drop { Hold = true, Station = Deck.Hold } : null;

        Job PickHaul(Worker w)
        {
            // Loose fish block a deck tile and come first.
            foreach (var lf in Loose.Where(l => l.Claim == null).OrderBy(l => Deck.Distance(w.Actor.Tile, l.Tile)))
            {
                if (FishRules.NeedsTwo(lf.Fish) && !w.PowerLifter && w.HandKg < lf.Fish.Kg) continue; // two-carrier fish wait for a strong lifter or a pair (M2 ability)
                var drop = Decide(lf.Fish) == SortOutcome.Throw ? new Drop { Overboard = true, Station = null } : HoldDrop();
                if (drop == null || drop.Hold && HoldRemainingKg() < lf.Fish.Kg) continue;
                var job = new Job { Kind = JobKind.Haul, Worker = w, Target = drop, Label = "Hauling" };
                lf.Claim = job; job.Fish.Add(lf.Fish);
                return job;
            }
            var sources = Deck.Baskets.Where(b => b.UnclaimedCount > 0 && b.Kind is not (BasketKind.SortIn or BasketKind.TableIn))
                .OrderByDescending(b => b.Fill).ThenBy(b => Dist(w, b.Owner));
            foreach (var b in sources)
            {
                var job = BuildHaul(w, b);
                if (job != null) return job;
            }
            return null;
        }

        // One load from a basket: up to the hand limits, all bound for the same place.
        Job BuildHaul(Worker w, Basket b)
        {
            if (b.UnclaimedCount == 0) return null;
            var drop = NextFor(b, b.Unclaimed.First());
            if (drop == null) return null;
            var job = new Job { Kind = JobKind.Haul, Worker = w, Source = b, Target = drop, Label = "Hauling" };
            float kg = 0;
            foreach (var f in b.Unclaimed.ToList())
            {
                if (job.Fish.Count >= w.HandCount || kg + f.Kg > w.HandKg && job.Fish.Count > 0) break;
                var d = NextFor(b, f);
                if (d == null || d.Hold != drop.Hold || d.Basket != drop.Basket) continue;
                if (drop.Basket != null && drop.Basket.Free < job.Fish.Count + 1) break;
                if (drop.Hold && HoldRemainingKg() < kg + f.Kg) break;
                b.Claim(f, job); job.Fish.Add(f); kg += f.Kg;
            }
            if (job.Fish.Count == 0) return null;
            if (drop.Basket != null) { drop.Basket.Reserve(job.Fish.Count); job.reserved = job.Fish.Count; }
            return job;
        }

        public float HaulWalkMultiplier(Worker worker)
        {
            var job = worker.Current;
            if (job?.Kind != JobKind.Haul) return 1;
            bool same(Job other) => other?.Kind == JobKind.Haul && other.Source == job.Source && other.Source != null && other.Target?.Basket == job.Target?.Basket && other.Target?.Hold == job.Target?.Hold;
            bool sam(Worker w) => w.Card?.Id == "sam" && w.Card.Rarity >= CardRarity.Purple;
            return Workers.Any(w => w != worker && same(w.Current) && (sam(w) || sam(worker))) ? 1.3f : 1;
        }

        // ---- running ------------------------------------------------------------------------

        void Start(Job job)
        {
            var w = job.Worker; w.Current = job; job.Started = true;
            switch (job.Kind)
            {
                case JobKind.Sort: case JobKind.TableWork: RunBench(job); break;
                default: RunHaul(job); break;
            }
        }

        Vector2Int SourceTile(Job job)
        {
            if (job.Source != null) return Deck.Access(job.Source.Owner);
            var lf = Loose.FirstOrDefault(l => l.Claim == job);
            return lf != null ? lf.Tile : job.Worker.Actor.Tile;
        }

        void RunHaul(Job job)
        {
            var w = job.Worker;
            Walk(job, SourceTile(job), () => w.Actor.Act("Picking up", ActSeconds(w, JobKind.Haul), () =>
            {
                foreach (var f in job.Fish)
                {
                    if (job.Source != null) job.Source.Take(f, job);
                    else Loose.RemoveAll(l => l.Claim == job && l.Fish == f);
                    w.Hands.Add(f);
                }
                if (job.Target.Overboard) { w.Actor.Act("Throwing back", StowSeconds(w), () => Deliver(job), () => Cancel(job)); return; }
                Walk(job, Deck.Access(job.Target.Station), () => w.Actor.Act("Stowing", StowSeconds(w), () => Deliver(job), () => Cancel(job)));
            }, () => Cancel(job)));
        }

        void RunBench(Job job)
        {
            var w = job.Worker;
            Walk(job, Deck.Access(job.At), () => w.Actor.Act(job.Label, ActSeconds(w, job.Kind), () =>
            {
                foreach (var f in job.Fish)
                {
                job.Source.Take(f, job);
                if (job.Kind == JobKind.Sort)
                {
                    var outcome = Decide(f);
                    if (outcome == SortOutcome.Throw) { job.Target.Basket.Unreserve(1); Thrown++; OnThrown?.Invoke(f); }
                    else { if (outcome == SortOutcome.Table) forTable.Add(f); job.Target.Basket.Put(f, true); }
                }
                else
                {
                    forTable.Remove(f);
                    if (OnTableDone != null) { job.Target.Basket.Unreserve(1); OnTableDone(job, f); }
                    else job.Target.Basket.Put(f, true);
                }
                }
                job.reserved = 0; Finish(job);
            }, () => Cancel(job)));
        }

        void Walk(Job job, Vector2Int tile, Action arrive)
        {
            if (job.Worker.Actor.Tile == tile) { arrive(); return; }
            if (!job.Worker.Actor.WalkTo(tile, arrive, () => Cancel(job))) Cancel(job);
        }

        void Deliver(Job job)
        {
            var w = job.Worker;
            foreach (var f in w.Hands.ToList())
            {
                w.Hands.Remove(f);
                if (job.Target.Overboard) { Thrown++; OnThrown?.Invoke(f); }
                else if (job.Target.Hold) { Stowed++; forTable.Remove(f); OnStowed?.Invoke(f); }
                else job.Target.Basket.Put(f, true);
            }
            job.reserved = 0; Finish(job);
        }

        void Finish(Job job)
        {
            job.Finished = true;
            if (job.At != null && job.At.Worker == job.Worker) job.At.Worker = null;
            job.Worker.Current = null;
        }

        // Cancelling never loses or duplicates fish: claims are released, reservations returned, and
        // anything in hand goes back to its basket or lands loose where the worker stands.
        public void Cancel(Job job)
        {
            if (job.Finished || job.Cancelled) return;
            job.Cancelled = true;
            var w = job.Worker;
            foreach (var f in job.Fish) job.Source?.Release(f, job);
            foreach (var lf in Loose.Where(l => l.Claim == job)) lf.Claim = null;
            if (job.Target?.Basket != null && job.reserved > 0) job.Target.Basket.Unreserve(job.reserved);
            foreach (var f in w.Hands.ToList())
            {
                w.Hands.Remove(f);
                if (job.Source == null || !FishRules.FitsBasket(f) || !job.Source.Put(f, false)) Loose.Add(new LooseFish { Fish = f, Tile = w.Actor.Tile });
            }
            if (job.At != null && job.At.Worker == w) job.At.Worker = null;
            w.Current = null;
            w.Actor.Stop();
        }

        public void CancelAll() { foreach (var w in Workers.Where(x => x.Current != null).ToList()) Cancel(w.Current); }

        // ---- captain commands (the player taps) ---------------------------------------------

        // Tier 0: the captain keeps or throws the fish at the sort table himself (two-button bubble).
        public bool CaptainSort(Worker captain, Station sort, bool keep)
        {
            if (!captain.Idle || sort.In == null || sort.Out == null || sort.In.UnclaimedCount == 0 || keep && sort.Out.Free == 0) return false;
            var job = new Job { Kind = JobKind.Sort, Worker = captain, Source = sort.In, At = sort, Label = "Sorting", Target = Drop.To(sort.Out) };
            var f = sort.In.Unclaimed.First(); sort.In.Claim(f, job); job.Fish.Add(f);
            if (keep) { sort.Out.Reserve(1); job.reserved = 1; }
            var prior = Decide;
            Decide = x => x == f ? keep && !FishRules.Undersize(x) ? SortOutcome.Keep : SortOutcome.Throw : prior(x);
            captain.Current = job; job.Started = true;
            Walk(job, Deck.Access(sort), () => captain.Actor.Act("Sorting", ActSeconds(captain, JobKind.Sort), () =>
            {
                sort.In.Take(f, job);
                if (Decide(f) == SortOutcome.Throw) { if (job.reserved > 0) sort.Out.Unreserve(1); Thrown++; OnThrown?.Invoke(f); }
                else sort.Out.Put(f, true);
                Decide = prior; job.reserved = 0; Finish(job);
            }, () => { Decide = prior; Cancel(job); }));
            return true;
        }

        // The captain hauls one load from a basket the player tapped.
        public bool CaptainHaul(Worker captain, Basket from)
        {
            if (!captain.Idle) return false;
            var job = BuildHaul(captain, from);
            if (job == null) return false;
            Start(job); return true;
        }
    }
}

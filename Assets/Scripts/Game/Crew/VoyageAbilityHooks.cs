using System.Collections.Generic;
using System.Linq;
using Catchline.Game.Deck;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        readonly HashSet<CaughtFish> instantNetSort = new();
        readonly DeliverySortBonus handOff = new();
        readonly string[] netSetter = new string[2];
        readonly string[] lineSetter = new string[3];

        void WireAbilityJobs()
        {
            instantNetSort.Clear(); handOff.Clear();
            Scheduler.BenchRate = job =>
            {
                if (job.Kind != JobKind.Sort || job.Fish.Count == 0) return 1;
                if (job.Worker.Card?.Id == "noor" && instantNetSort.Contains(job.Fish[0])) return float.PositiveInfinity;
                return (Abilities?.SortRate(job.Worker.Card?.Id, job.Fish[0]) ?? 1) * handOff.Begin(job);
            };
            Scheduler.OnSorted = (job, fish) =>
            {
                if (instantNetSort.Remove(fish) && job.Worker.Card?.Id == "noor") Abilities?.InstantSorted();
                handOff.Complete(job);
                Abilities?.Sorted(job.Worker.Card?.Id, fish);
            };
            Scheduler.OnCancelled = handOff.Cancel;
            Scheduler.ProductBatch = w => Abilities?.ProductBatch(w.Card?.Id) ?? 1;
            Scheduler.OnProductDone = job => Abilities?.ProductDone(job.Worker.Card?.Id, job.Fish.Count);
            Scheduler.WholeLoad = (w, basket) => w.Card?.Id == "sam" && basket.Kind == BasketKind.NetOut && Abilities?.Armed("sam", 2) == true;
            Scheduler.SweepReady = w => w.Card?.Id == "ana" && Abilities?.Armed("ana", 2) == true;
            Scheduler.OnSweepDelivered = w => Abilities?.SweepDelivered();
            Scheduler.OnDelivered = job =>
            {
                if (job.Worker.Card?.Id == "ana" && Abilities?.Has("ana", 1) == true && job.Target.Basket?.Kind == BasketKind.SortIn)
                { handOff.Offer(job.Target.Station); Abilities.HandedOff(); }
                if (job.Worker.Card?.Id == "sam" && job.WholeLoad) Abilities?.Consume("sam", 2);
            };
        }

        void PrepareNetSet(Person person, int rig)
        {
            netSetter[rig] = AbilityOwner(person);
            Abilities?.NetSet(netSetter[rig]);
        }
        float NetSoakAbility(int rig) => Abilities?.NextSoak(rig) ?? 1;
        float NetSetSeconds(Person person, float seconds) => Abilities?.InstantNetSet(AbilityOwner(person)) == true ? .001f : seconds;

        // Apply batch perks once, before emission. A bonus specimen always fits the source's normal kg budget.
        void PrepareNetHaul(Person person, int rig, List<(Species species, float kg)> fish)
        {
            string hauler = AbilityOwner(person);
            float capacity = NetWeightRange(ActiveSpot, DeepNetSelected).y;
            float original = fish.Sum(f => f.kg);
            Abilities?.NetHauled(netSetter[rig], hauler, original / Mathf.Max(.01f, capacity), rig);
            if (hauler != "rosa" || Abilities?.Consume("rosa", 1) != true) return;
            float budget = Mathf.Min(capacity, original * 1.3f) - original;
            // Use the same net catch pool, but never force an oversize/illegal specimen into the budget.
            var extras = CatchExpectation.RollNet(State.Hull, ActiveSpot, DeepNetSelected, capacity, State.Rng, State.FishTable(ActiveSpot), Abilities.DoubleWeight);
            foreach (var extra in extras)
            {
                if (extra.kg > budget) continue;
                fish.Add(extra); budget -= extra.kg;
                AbilityCatch(ActiveSpot, extra.kg, extra.species, true);
            }
        }
        bool LandAbilityNet(Station station, Species species, float kg, Person hauler, int ordinal)
        {
            var fish = new CaughtFish { Species = species, Kg = kg, StowedAt = SimTime };
            if (AbilityOwner(hauler) == "rosa" && Abilities?.Has("rosa", 2) == true && ordinal < 6 && !FishRules.Undersize(fish)
                && HoldKg + kg <= State.CoolerCapacity && TryStore(fish, false))
            {
                Scheduler.Landed++; Scheduler.Stowed++;
                return true;
            }
            if (Abilities?.Has("noor", 2) == true && ordinal < 5) instantNetSort.Add(fish);
            Scheduler.Land(station, fish);
            basketFish[fish] = DeckFish.BuildModel(species, kg, Boat);
            return true;
        }
    }
}

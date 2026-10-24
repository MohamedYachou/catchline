using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Exercise the live Person adapter and voyage bridge, rather than a second scheduler simulation.
    public static class M1HullChecks
    {
        static void Check(bool ok, string text) { if (!ok) throw new Exception("[Catchline] M1 hull: " + text); }
        static void Advance(VoyageGame g, float seconds)
        {
            for (float t = 0; t < seconds; t += .05f)
            {
                g.Tick(.05f);
                Check(g.Scheduler.Balanced, "fish conservation");
                var claimed = new HashSet<CaughtFish>();
                foreach (var w in g.Scheduler.Workers.Where(w => w.Current != null))
                    foreach (var f in w.Current.Fish) Check(claimed.Add(f), "single job claim per fish");
            }
        }
        static void Until(VoyageGame g, Func<bool> done, string text, float seconds = 60)
        {
            for (float t = 0; t < seconds && !done(); t += .05f) Advance(g, .05f);
            Check(done(), text);
        }
        public static void Run(int hull)
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("M1 live hull").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build(); g.State.Hull = hull; g.State.Coins = 10000; g.State.Fuel = g.State.FuelCapacity;
            for (int i = 0; i < 2; i++)
            {
                g.State.EnsureCrewRoleOffers();
                Check(g.State.Hire(g.State.Board.First(c => c.Role == CrewRole.Deckhand)), "hire two deckhands");
            }
            typeof(VoyageGame).GetMethod("RebuildBoat", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic).Invoke(g, new object[] { false });
            g.SyncCrew(); g.SetSail();
            for (float t = 0; t < 120 && g.CurrentMode != VoyageGame.Mode.Fishing; t += .05f) g.Tick(.05f);
            Check(g.CurrentMode == VoyageGame.Mode.Fishing && g.UsesDeckGraph, "live hull uses graph");
            var deck = g.DeckGraph; var sched = g.Scheduler;
            foreach (var s in deck.Stations) Check(deck.Reachable(deck.Access(deck.Hold), deck.Access(s)), s.Id + " reachable");
            var hands = sched.Workers.Where(w => !w.Captain).ToArray();
            hands[0].SetDuties(Duty.Haul, Duty.Haul); hands[1].SetDuties(Duty.Sort, Duty.Sort);
            float kg = GameData.Get(Species.Mackerel).MaxKg * .9f;
            var rod = g.Rods[0]; var basket = g.GearStation(StationKind.Rod, 0).Out;
            g.LandFish(rod, Species.Mackerel, kg);
            Check(basket.Count == 1 && g.OnDeck.Count == 0, "rod lands in basket");
            Until(g, () => hands[0].Hands.Count > 0, "hauler picks up catch");
            var active = hands[0].Current;
            hands[0].SetDuties(Duty.Sort, Duty.Haul);
            Check(hands[0].Current == active && hands[0].Primary == Duty.Haul, "duty change deferred during job");
            sched.Cancel(active);
            Check(sched.Balanced, "cancel is lossless");
            Until(g, () => sched.Stowed == 1, "rod to sort to hold after cancellation");
            g.LandFish(rod, Species.Herring, GameData.Get(Species.Herring).MinKg);
            Until(g, () => sched.Thrown == 1, "undersize thrown back");
            Check(g.Cooler.Count == 1, "undersize never in hold");
            // Sustained live trace: sparse arrivals allow every hull to clear without overflowing the hold.
            for (int i = 0; i < 6; i++) { g.LandFish(rod, Species.Mackerel, kg); Advance(g, 20); }
            Check(sched.Stowed == 7 && sched.OnDeck == 0 && hands.All(w => w.Idle), "120 second trace drained with no stuck worker");
            if (hull == 2)
            {
                hands[0].SetDuties(Duty.Haul, Duty.Haul); hands[1].SetDuties(Duty.Sort, Duty.Sort);
                var field = typeof(VoyageGame).GetField("netFish", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
                var pile = (List<(Species, float)>)field.GetValue(g);
                for (int i = 0; i < 14; i++) pile.Add((Species.Mackerel, kg));
                typeof(VoyageGame).GetMethod("FinishHaul", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic).Invoke(g, null);
                Check(g.GearStation(StationKind.Net, 0).Out.Count == 14 && g.OnDeck.Count == 0, "net unload enters graph");
                Until(g, () => sched.Stowed == 21, "14 fish net pile sorted and stowed by sorter and hauler under 60 seconds", 59.9f);
            }
            Debug.Log("[Catchline] M1 " + g.State.HullDef.Model.ToUpperInvariant() + " CHECKS PASSED");
        }
    }
    public static class M1SkiffChecks { public static void Run() => M1HullChecks.Run(1); }
    public static class M1CompactChecks { public static void Run() => M1HullChecks.Run(2); }
    public static class M1PrepChecks { public static void Run() => M1HullChecks.Run(3); }
}

using System;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // M1 live: the rowboat runs on the deck graph. A real voyage lands a rod catch in the rod basket; the
    // captain carries it to the sort table (tap), keeps it (tap) and it reaches the hold; an undersize fish is
    // thrown back even when kept; heading home keeps every keeper.
    public static class M1RowboatChecks
    {
        static void Check(bool ok, string what) { if (!ok) throw new Exception("[Catchline] M1 rowboat check failed: " + what); }
        static void Until(VoyageGame g, Func<bool> done, string what, float seconds = 60)
        {
            for (float t = 0; t < seconds && !done(); t += .05f) g.Tick(.05f);
            Check(done(), what);
        }

        public static void Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("M1 rowboat check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            Check(g.State.Hull == 0, "starts on the rowboat");
            g.SetSail();
            Until(g, () => g.CurrentMode == VoyageGame.Mode.Fishing, "arrives at sea", 120);
            Check(g.UsesDeckGraph && g.DeckGraph.Hull == "Rowboat", "rowboat runs on the deck graph");
            var rod = g.Rods[0];
            var rodBasket = g.GearStation(StationKind.Rod, rod.Index).Out;
            var sort = g.DeckGraph.OfKind(StationKind.SortTable).First();

            g.LandFish(rod, Species.Mackerel, GameData.Get(Species.Mackerel).MaxKg * .9f);
            Check(rodBasket.Count == 1 && g.OnDeck.Count == 0, "catch lands in the rod basket, not loose on deck");
            int cooler = g.Cooler.Count;
            Check(g.CaptainHaulFrom(rodBasket), "Carry tap starts a haul");
            Until(g, () => sort.In.Count == 1, "captain carries it to the sort table");
            g.CommandKeep(true);
            Until(g, () => g.Cooler.Count == cooler + 1, "Keep sorts and stows it in the hold");
            Check(g.Scheduler.Balanced, "no fish lost after the keep");

            var tiny = GameData.Get(Species.Herring);
            g.LandFish(rod, Species.Herring, tiny.MinKg);
            g.CaptainHaulFrom(rodBasket);
            Until(g, () => sort.In.Count == 1, "undersize carried to the sort table");
            g.CommandKeep(true);
            Until(g, () => g.ThrownBack == 1, "undersize thrown back even when kept");
            Check(g.Cooler.Count == cooler + 1, "undersize never reaches the hold");

            g.LandFish(rod, Species.Mackerel, GameData.Get(Species.Mackerel).MaxKg * .8f);
            int before = g.Cooler.Count;
            // The real map puts the nearest ground a few metres from the quay; sail home from the far ground so the trip lasts.
            if (g.Navigation != null) g.Sailor.Push(g.Navigation.Grounds[g.Navigation.Grounds.Count - 1].Centre);
            g.HeadHome();
            Check(g.UsesDeckGraph && g.Scheduler.Sailing, "heading home keeps the deck graph ticking in transit");
            Check(g.CaptainHaulFrom(rodBasket), "captain can sort the remaining keeper while sailing");
            Until(g, () => sort.In.Count == 1, "return trip carries keeper to sort table");
            g.CommandKeep(true);
            Until(g, () => g.Cooler.Count == before + 1, "return trip sorts and stows the keeper");
            Until(g, () => g.CurrentMode == VoyageGame.Mode.Harbour, "returns to harbour", 120);
            Check(!g.UsesDeckGraph, "arrival releases deck graph");
            Debug.Log("[Catchline] M1 ROWBOAT CHECKS PASSED");
        }
    }
}

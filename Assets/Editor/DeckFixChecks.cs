using System;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Live bridge regressions for DECK-FIX-1, always save-isolated.
    public static class DeckFixChecks
    {
        const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
        static object Call(VoyageGame g, string name, params object[] args) => typeof(VoyageGame).GetMethod(name, Private).Invoke(g, args);
        static void Check(bool ok, string why) { if (!ok) throw new Exception("[Catchline] DECK-FIX-1 failed: " + why); }
        static void Until(VoyageGame g, Func<bool> done, string why, float seconds = 60)
        {
            for (float t = 0; t < seconds && !done(); t += .05f) g.Tick(.05f);
            Check(done(), why);
        }
        static bool Visible(VoyageGame g, string id) => g.GetComponentsInChildren<Transform>(false).Any(t => t.name == id);

        public static void Run()
        {
            bool hadPref = PlayerPrefs.HasKey("catchline.autoCarry");
            int oldPref = PlayerPrefs.GetInt("catchline.autoCarry");
            try
            {
                ArtImport.BuildLibrary();
                for (int tier = 0; tier < 2; tier++) Carry(tier);
                Decisions();
                Debug.Log("[Catchline] DECK-FIX-1 CHECKS PASSED: Rowboat/Skiff default On, Off/manual, On, busy/rod/claim guards, Keep/Throw retirement, settings");
            }
            finally
            {
                if (hadPref) PlayerPrefs.SetInt("catchline.autoCarry", oldPref); else PlayerPrefs.DeleteKey("catchline.autoCarry");
                PlayerPrefs.Save();
            }
        }

        static VoyageGame Game(int tier)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("DECK-FIX-1 no-save check");
            root.SetActive(false);
            var g = root.AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build(); root.SetActive(true);
            Call(g, "StartTestTier", tier);
            g.SetSail();
            Until(g, () => g.CurrentMode == VoyageGame.Mode.Fishing, "arrive at ground", 180);
            return g;
        }

        static void Carry(int tier)
        {
            PlayerPrefs.DeleteKey("catchline.autoCarry");
            var g = Game(tier);
            var rod = g.Rods[0];
            var basket = g.GearStation(StationKind.Rod, rod.Index).Out;
            var sort = g.DeckGraph.OfKind(StationKind.SortTable).First();
            var captain = g.Scheduler.Workers.Single(w => w.Captain);
            g.LandFish(rod, Species.Mackerel, .62f);
            Until(g, () => sort.In.Count == 1 && captain.Idle, "default On delivers rod catch to sort, tier " + tier);
            Check(g.Manning == null && !g.AwaitingCast && g.Scheduler.Balanced, "auto-carry clears rod intent and conserves fish");
            g.CommandKeep(false);
            Until(g, () => sort.In.Count == 0 && captain.Idle, "throw clears first fish");

            PlayerPrefs.SetInt("catchline.autoCarry", 0);
            g.LandFish(rod, Species.Mackerel, .62f);
            g.Tick(4);
            Check(basket.UnclaimedCount == 1 && sort.In.Count == 0 && captain.Idle, "Off leaves catch for manual Carry");
            g.PrepareInterface(844, 390);
            Check(g.InvokeInterface("deck/carry/" + basket.Id), "Off retains working Carry bubble");
            Until(g, () => sort.In.Count == 1 && captain.Idle, "manual Carry still delivers");
            g.CommandKeep(false);
            Until(g, () => sort.In.Count == 0 && captain.Idle, "manual catch thrown");

            PlayerPrefs.SetInt("catchline.autoCarry", 1);
            g.LandFish(rod, Species.Mackerel, .62f);
            g.Captain.Do("Test busy", 2, () => { });
            g.Tick(.25f);
            Check(basket.UnclaimedCount == 1 && captain.Idle, "auto-carry does not interrupt captain action");
            g.Captain.Stop();
            // Exercise the same follow-up called by TickDeckGraph without ticking synthetic rod timers.
            typeof(VoyageGame).GetProperty("Manning").SetValue(g, rod);
            g.Captain.Place(rod.Tile);
            foreach (var state in new[] { RodState.Flying, RodState.Waiting, RodState.Bite, RodState.Reeling })
            {
                rod.State = state;
                Call(g, "CaptainFollowUp");
                Check(basket.UnclaimedCount == 1 && captain.Idle && g.Manning == rod, "active rod protected: " + state);
            }
            rod.State = RodState.Unbaited;
            typeof(VoyageGame).GetProperty("Manning").SetValue(g, null);
            var fish = basket.Fish.Single();
            var otherClaim = new object();
            basket.Claim(fish, otherClaim);
            Call(g, "CaptainFollowUp");
            Check(captain.Idle && sort.In.Count == 0, "claimed catch not stolen");
            basket.Release(fish, otherClaim);
            Until(g, () => sort.In.Count == 1 && captain.Idle, "On resumes once idle with an unclaimed catch");
            Check(g.Scheduler.Balanced, "all fish accounted for");
            Debug.Log("[Catchline] DECK-FIX-1 auto-carry tier " + tier + " PASSED");
        }

        static void Decisions()
        {
            var g = Game(0);
            Check((bool)Call(g, "StageUiV2", "sort"), "stage sort");
            foreach (var size in new[] { new Vector2Int(1440, 900), new Vector2Int(844, 390) })
            {
                g.PrepareInterface(size.x, size.y);
                Check(Visible(g, "deck/keep") && Visible(g, "deck/throw"), "waiting fish has both controls");
            }
            Check(g.InvokeInterface("deck/keep"), "Keep starts sorting");
            g.PrepareInterface(844, 390);
            Check(!Visible(g, "deck/keep") && !Visible(g, "deck/throw"), "claimed fish immediately retires buttons");
            Until(g, () => g.Scheduler.OnDeck == 0 && g.Captain.Idle, "Keep sorts then stows");
            g.PrepareInterface(844, 390);
            Check(!Visible(g, "deck/keep") && !g.InvokeInterface("deck/throw"), "empty table leaves no active/stale action");
            Check((bool)Call(g, "StageUiV2", "sort-home"), "same Canvas survives Keep then Head home with another waiting fish");
            Check(!Visible(g, "deck/keep") && !Visible(g, "deck/throw"), "homebound controls retired");
            Until(g, () => g.CurrentMode == VoyageGame.Mode.Harbour, "return to harbour", 180);
            g.PrepareInterface(844, 390);
            Check(!Visible(g, "deck/keep") && !Visible(g, "deck/throw"), "harbour controls retired");
            g.SetSail(); g.PrepareInterface(844, 390);
            Check(!Visible(g, "deck/keep") && !Visible(g, "deck/throw"), "outbound controls retired");
            Check((bool)Call(g, "StageUiV2", "settings"), "settings stage");
            g.PrepareInterface(844, 390);
            Check(g.InvokeInterface("settings/auto-carry/0") && PlayerPrefs.GetInt("catchline.autoCarry") == 0, "settings Off persists");
            g.PrepareInterface(844, 390);
            Check(g.InvokeInterface("settings/auto-carry/1") && PlayerPrefs.GetInt("catchline.autoCarry") == 1, "settings On persists");
        }
    }
}

using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Save-isolated regression for Mo's urgent rowboat automation / recovery request.
    public static class UrgentCrewChecks
    {
        static void Check(bool ok, string message)
        {
            if (!ok) throw new Exception("[Catchline] First voyage check failed: urgent " + message);
        }
        static void Until(VoyageGame game, Func<bool> done, string message, float timeout = 90f)
        {
            for (float t = 0; t < timeout && !done(); t += .05f) game.Tick(.05f);
            Check(done(), message);
        }
        static int Offers(GameState state, CrewRole role) => state.Board.Count(c => c.Role == role);
        static int Hired(GameState state, CrewRole role) => state.Crew.Count(c => c.Role == role);
        static void CheckComposition(CrewRole[] roles, int seed, bool saveReload)
        {
            var state = new GameState(seed) { Hull = 2, Coins = 10000 };
            state.EnsureCrewRoleOffers();
            Check(Offers(state, CrewRole.Deckhand) >= 3 && Offers(state, CrewRole.Fisherman) >= 3, "tier3 always offers three candidates of each role");
            foreach (var role in roles)
            {
                var offer = state.Board.FirstOrDefault(c => c.Role == role);
                Check(offer != null && state.Hire(offer), "hire contract " + role);
                Check(Offers(state, CrewRole.Deckhand) >= 3 && Offers(state, CrewRole.Fisherman) >= 3, "both role offers replenish after each hire");
            }
            Check(state.CrewCount == 3, "fill all three berths");
            foreach (CrewRole role in new[] { CrewRole.Deckhand, CrewRole.Fisherman })
                Check(Hired(state, role) == roles.Count(r => r == role), "requested composition remains aboard: " + role);
            Check(state.Crew.All(c => c.VoyagesLeft == GameData.ContractVoyages(c.Grade)), "new hires retain grade-based contract duration");
            if (saveReload)
            {
                string path = Path.GetFullPath("Logs/crew026/crew-mix-save.json");
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                try
                {
                    state.Save(path);
                    var loaded = GameState.Load(path);
                    Check(loaded.CrewCount == 3 && loaded.Crew.All(c => c.VoyagesLeft == GameData.ContractVoyages(c.Grade)), "contract timers survive save reload");
                    Check(Offers(loaded, CrewRole.Deckhand) >= 3 && Offers(loaded, CrewRole.Fisherman) >= 3, "both offers survive save reload");
                    state = loaded;
                    loaded.Board.Clear(); loaded.Save(path); loaded = GameState.Load(path);
                    Check(Offers(loaded, CrewRole.Deckhand) >= 3 && Offers(loaded, CrewRole.Fisherman) >= 3, "older empty board saves restore all role choices");
                    state = loaded;
                }
                finally { if (File.Exists(path)) File.Delete(path); }
            }

            var hiredCrew = state.Crew.ToArray();
            var contractLengths = hiredCrew.ToDictionary(c => c.Name, c => c.VoyagesLeft);
            for (int voyage = 1; voyage <= contractLengths.Values.Max(); voyage++)
            {
                state.EndVoyage(new SaleReport());
                foreach (var crew in hiredCrew)
                {
                    int remaining = contractLengths[crew.Name] - voyage;
                    Check(state.Crew.Contains(crew) == (remaining > 0), "crew contract expires on its stated voyage");
                    if (remaining > 0) Check(crew.VoyagesLeft == remaining, "crew contract countdown advances by one voyage");
                }
                Check(Offers(state, CrewRole.Deckhand) >= 3 && Offers(state, CrewRole.Fisherman) >= 3, "both roles remain available after contract expiry and board roll");
            }
            Check(state.CrewCount == 0, "all hired contracts expire on schedule");
        }
        static void CheckCrewMixes()
        {
            foreach (int hull in Enumerable.Range(0, GameData.Hulls.Length))
                for (int seed = 0; seed < 30; seed++)
                {
                    var state = new GameState(seed) { Hull = hull };
                    state.EnsureCrewRoleOffers();
                    Check(Offers(state, CrewRole.Deckhand) >= state.HullDef.CrewCap && Offers(state, CrewRole.Fisherman) >= state.HullDef.CrewCap,
                        $"both roles fill all {state.HullDef.CrewCap} berths on hull {hull}, seed {seed}");
                }
            CheckComposition(new[] { CrewRole.Fisherman, CrewRole.Fisherman, CrewRole.Fisherman }, 9101, true);
            CheckComposition(new[] { CrewRole.Deckhand, CrewRole.Deckhand, CrewRole.Deckhand }, 9102, false);
            CheckComposition(new[] { CrewRole.Fisherman, CrewRole.Deckhand, CrewRole.Fisherman }, 9103, false);
        }
        static void CheckCrewMixTrial()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var trial = new GameObject("Save-isolated crew mix test").AddComponent<VoyageGame>();
            trial.SessionOnly = true; trial.Build();
            Check(trial.StartCrewMixTrial(), "isolated crew trial starts");
            Check(trial.State.Hull == 2 && trial.State.CrewCount == 0 && trial.State.Coins == 1000, "test starts at tier3 harbour with empty berths and hiring funds");
            Check(Offers(trial.State, CrewRole.Deckhand) >= 3 && Offers(trial.State, CrewRole.Fisherman) >= 3, "test offers all role choices");
            Check(trial.State.Board[0].Role != trial.State.Board[1].Role, "first Crew Office row exposes both worker roles");
            trial.PrepareInterface(1440, 900);
            var controls = trial.GetComponentsInChildren<RectTransform>().Select(t => t.name).ToHashSet();
            Check(Enumerable.Range(0, 6).All(i => controls.Contains("hire/" + i + "/buy")), "Crew Office exposes six candidate purchase controls");
            Directory.CreateDirectory("Logs/crew026");
            var shot = typeof(ReferenceHudChecks).GetMethod("Shot", BindingFlags.Static | BindingFlags.NonPublic);
            shot.Invoke(null, new object[] { trial, "../crew026/crew-office-desktop", 1440, 900, 1f });
            shot.Invoke(null, new object[] { trial, "../crew026/crew-office-phone", 844, 390, 1f });
            foreach (var role in new[] { CrewRole.Fisherman, CrewRole.Deckhand, CrewRole.Fisherman })
            {
                int index = trial.State.Board.FindIndex(c => c.Role == role);
                trial.PrepareInterface(1440, 900);
                Check(index >= 0 && trial.InvokeInterface("hire/" + index + "/buy"), "Crew Office buys selected " + role + " through its real control");
                Check(trial.State.Crew.Any(c => c.Role == role), "selected role joins the test boat");
            }
            Check(trial.State.CrewCount == 3 && Offers(trial.State, CrewRole.Deckhand) >= 3 && Offers(trial.State, CrewRole.Fisherman) >= 3,
                "test fills three mixed berths while role offers remain available");
            UnityEngine.Object.DestroyImmediate(trial.gameObject);
        }
        public static void Run()
        {
            ArtImport.BuildLibrary();
            CheckCrewMixes();
            CheckCrewMixTrial();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Urgent rowboat checks").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.Build();
            var s = game.State;
            Check(s.HullDef.CrewCap == 2, "rowboat supports two employees plus captain");
            for (int seed = 0; seed < 30; seed++)
            {
                var board = new GameState(seed).Board;
                Check(board.Count(c => c.Role == CrewRole.Deckhand) >= 2 && board.Count(c => c.Role == CrewRole.Fisherman) >= 2, "both roles cover every rowboat berth across seeds");
            }
            s.Coins = 1000;
            var hand = s.Board.First(c => c.Role == CrewRole.Deckhand);
            var fisher = s.Board.First(c => c.Role == CrewRole.Fisherman);
            Check(s.Hire(hand) && s.Hire(fisher), "both roles hired on rowboat");
            Check(s.Board.Count(c => c.Role == CrewRole.Deckhand) >= 2 && s.Board.Count(c => c.Role == CrewRole.Fisherman) >= 2, "all role choices replenished after hire");
            Check(!s.Hire(s.Board[0]), "third employee blocked");
            game.SyncCrew(); game.SyncUpgrades();
            Check(game.Hand != null && game.ExtraPeople.Count == 1 && game.Rods[1].Unlocked, "two crew and dedicated second rod built");
            Check(game.Grid.FindPath(new Vector2Int(2,1), game.Rods[1].Tile) != null, "fisherman rests on valid rowboat tile");
            s.Coins = 0; s.Bait = 0; s.Squid = 0; s.FoodMinutes = 20;
            Check(game.SailBlocker() == null && s.TakeBait(out bool squid) && !squid && s.Coins == 0, "broke captain can launch and use free bait");
            for (int n = 0; n < 200; n++)
            {
                var (species, kg) = s.RollFish(4, 1.4f, true);
                var def = GameData.Get(species);
                Check((species == Species.Herring || species == Species.Mackerel) && kg <= def.MinKg + (def.MaxKg-def.MinKg)*.201f, "scraps cannot catch large fish even in deep water");
            }
            game.SetSail();
            Until(game, () => game.CurrentMode == VoyageGame.Mode.Fishing, "arrive at sea");
            Until(game, () => game.Cooler.Count >= 1, "fisherman catches and deckhand stows without captain taps", 240f);
            Check(game.Rods[1].Fisher != null && game.Rods[0].Fisher == null, "fisherman leaves captain's rod free");
            var rod = game.Rods[0];
            game.CommandRod(rod);
            Until(game, () => rod.State == RodState.Bite, "captain bite");
            game.StrikeTap();
            Until(game, () => game.AwaitingCast, "deckhand keeps captain in fishing mode");
            Check(game.Manning == rod && game.CurrentHaul().Count > 0, "haul includes deck and carried fish");
            game.Tick(3f);
            Check(game.AwaitingCast && (rod.State == RodState.Ready || rod.State == RodState.Unbaited), "does not silently recast");
            Check(game.ThrowAgain(), "one big throw action resumes same rod");
            Until(game, () => rod.State == RodState.Bite, "second cast");
            game.StrikeTap();
            Until(game, () => game.AwaitingCast, "second catch retains mode");
            game.LeaveFishing();
            Check(game.Manning == null && !game.AwaitingCast, "leave exits fishing interaction");
            game.HeadHome();
            Until(game, () => game.CurrentMode == VoyageGame.Mode.Harbour, "port arrival");
            Check(s.Coins == 0 && s.UnsoldCatch.Count >= 3 && s.LastSale == null, "arrival preserves fish without auto-sale");
            Check(game.SailBlocker() == "Sell your haul first", "unsold catch cannot be silently lost on departure");
            var quote = s.QuoteSale(s.UnsoldCatch, 0);
            int payout = quote.Coins + quote.ContractCoins;
            Check(payout > 0 && s.Coins == 0 && s.LastSale == null, "quote is valuable and side-effect free");
            string path = Path.GetFullPath("Logs/urgent-crew-save.json");
            try
            {
                s.Save(path);
                var loaded = GameState.Load(path);
                Check(loaded.CrewCount == 2 && loaded.UnsoldCatch.Count == s.UnsoldCatch.Count, "crew and unsold haul survive reload");
                Check(loaded.QuoteSale(loaded.UnsoldCatch, 0).Coins + loaded.QuoteSale(loaded.UnsoldCatch, 0).ContractCoins == payout, "saved catch retains exact value");
                // Simulate an old save with no offers.
                loaded.Board.Clear(); loaded.Save(path); loaded = GameState.Load(path);
                Check(loaded.Board.Count(c => c.Role == CrewRole.Fisherman) >= loaded.HullDef.CrewCap
                    && loaded.Board.Count(c => c.Role == CrewRole.Deckhand) >= loaded.HullDef.CrewCap, "old saves recover full role choices");
            }
            finally { if (File.Exists(path)) File.Delete(path); }
            game.Tick(90f);
            Check(s.QuoteSale(s.UnsoldCatch,0).Coins + s.QuoteSale(s.UnsoldCatch,0).ContractCoins == payout, "harbour browsing does not degrade haul");
            Check(game.SellHaul() && s.Coins == payout && s.UnsoldCatch.Count == 0, "explicit sale pays exact preview and clears once");
            Check(!game.SellHaul() && s.Coins == payout, "double sale blocked");
            Check(s.LogCount.Sum() >= 3 && s.Voyage == 2, "sale advances log and voyage once");
            var fish = new CaughtFish { Species = Species.Herring, Kg = .3f, StowedAt = 0 };
            Check(s.Freshness(fish, 59) == 1f && s.Freshness(fish, 120) < 1f, "freshness grace and degradation match messaging");
            s.Owned.Add(UpgradeId.IceBox);
            Check(s.Freshness(fish, 10000) == 1f, "ice preserves value");
            Debug.Log("[Catchline] URGENT CREW CHECKS PASSED: expiring contracts, flexible offers, crew trial, automation, scraps, persistent cast, sale/save, freshness");
        }
    }
}

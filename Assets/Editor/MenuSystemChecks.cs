using System;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class MenuSystemChecks
    {
        const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool pass, string label) { if (!pass) throw new Exception("Menu/system check failed: " + label); }
        static T Read<T>(VoyageGame game, string field) => (T)typeof(VoyageGame).GetField(field, Private).GetValue(game);
        static object Call(VoyageGame game, string method, params object[] args) => typeof(VoyageGame).GetMethod(method, Private).Invoke(game, args);

        public static void Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Isolated menu/system check").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.Build();
            typeof(VoyageGame).GetField("showTitle", Private).SetValue(game, false);
            var state = game.State;
            state.Coins = 1000;
            Check(state.Hire(state.Board.First(c => c.Role == CrewRole.Deckhand)), "hire fixture deckhand");
            game.SyncCrew();
            state.FoodMinutes = 100;
            game.SetSail();
            for (int i = 0; i < 500 && game.CurrentMode != VoyageGame.Mode.Fishing; i++) game.Tick(.05f);
            Check(game.CurrentMode == VoyageGame.Mode.Fishing, "fixture reaches sea through normal route");
            for (int i = 0; i < 8; i++) game.Cooler.Add(new CaughtFish { Species = Species.Herring, Kg = .45f, StowedAt = game.SimTime });
            for (int i = 0; i < 5; i++) game.LandFish(game.Rods[0], Species.Herring, .25f);
            game.Captain.Carrying = game.OnDeck[0]; game.OnDeck.RemoveAt(0);
            game.Hand.Carrying = game.OnDeck[0]; game.OnDeck.RemoveAt(0);
            Check(game.CurrentHaul().Count == 13 && game.UnstowedHaul().Count == 5 && game.DepartureOverflow() == 3, "carried/deck fish counted once; exact three-fish loss");
            state.Owned.Add(UpgradeId.BigCooler);
            Check(game.DepartureOverflow() == 0 && state.CoolerCapacity == 6, "larger cooler prevents overflow");
            state.Hull = 1;
            Check(game.DepartureOverflow() == 0 && state.CoolerCapacity == 27, "skiff capacity used");
            state.Hull = 0; state.Owned.Remove(UpgradeId.BigCooler);
            for (int i = 0; i < 2; i++) game.Cooler.Add(new CaughtFish { Species = Species.Herring, Kg = .25f, StowedAt = game.SimTime });
            Check(game.DepartureOverflow() == 5, "full cooler exposes all unstowed fish");
            game.Cooler.RemoveRange(8, 2);

            state.Active.Clear();
            state.Active.Add(new Contract { Species = Species.Herring, Count = 9, VoyagesLeft = 3, Reward = 50 });
            int coins = state.Coins;
            var secured = state.QuoteSale(game.Cooler, game.SimTime);
            var total = state.QuoteSale(game.CurrentHaul(), game.SimTime);
            Check(secured.ContractCoins == 0 && total.ContractCoins == 50, "pending contract bonus is separate from secured value");
            Check(state.Coins == coins && state.Active[0].Delivered == 0, "quotation never sells or changes the live market/contracts");
            Call(game, "RequestHeadHome");
            Check(Read<bool>(game, "confirmHeadHome") && Read<bool>(game, "paused") && game.CurrentMode == VoyageGame.Mode.Fishing, "player overflow request waits for explicit choice");
            float clock = game.SimTime, food = state.FoodMinutes;
            for (int i = 0; i < 15; i++) Call(game, "Update");
            Check(game.SimTime == clock && state.FoodMinutes == food && game.CurrentHaul().Count == 13, "real Update respects the modal pause without losing fish");
            Call(game, "CancelHeadHome");
            Check(!Read<bool>(game, "paused") && !Read<bool>(game, "confirmHeadHome") && game.CurrentHaul().Count == 13, "cancel preserves every fish and resumes");
            Call(game, "RequestHeadHome"); Call(game, "ConfirmHeadHome");
            Check(game.CurrentMode == VoyageGame.Mode.SailingHome && game.Cooler.Count == 10 && game.OnDeck.Count == 0 && game.Captain.Carrying == null && game.Hand.Carrying == null && game.ExtraPeople.All(p => p.Carrying == null), "confirmation keeps capacity and normal carried-first disposal");
            for (int i = 0; i < 500 && game.CurrentMode != VoyageGame.Mode.Harbour; i++) game.Tick(.05f);
            Check(game.CurrentMode == VoyageGame.Mode.Harbour && state.UnsoldCatch.Count == 10, "return secures ten fish for explicit sale");
            Check((bool)Call(game, "ShopHasNews", VoyageGame.HudTab.Market), "unsold haul attracts attention to Market");
            Check(game.SellHaul(), "explicit sale succeeds");
            int paid = state.Coins;
            Check(paid > coins && !game.SellHaul() && state.Coins == paid, "sale pays once");

            var fish = new System.Collections.Generic.List<CaughtFish> { new CaughtFish { Species = Species.Herring, Kg = .25f, StowedAt = 0 } };
            Check(game.FreshnessStatus(fish, 59).Contains("1s"), "freshness countdown before grace boundary");
            Check(game.FreshnessStatus(fish, 60).Contains("loses 7%"), "depreciation explanation at grace boundary");
            Check(Mathf.Approximately(state.Freshness(fish[0], 120), .93f) && game.FreshnessStatus(fish, 9999).Contains("minimum"), "freshness rate and minimum preserved");
            state.Owned.Add(UpgradeId.IceBox);
            Check(game.FreshnessStatus(fish, 9999).Contains("Iced"), "ice preserves full value");
            state.Coins = state.Bait = state.Squid = 0;
            Check(!(bool)Call(game, "ShopHasNews", VoyageGame.HudTab.Supplies) && state.TakeBait(out _), "free scraps work without false unaffordable Supplies badge");
            UnityEngine.Object.DestroyImmediate(game.gameObject);
            Debug.Log("[Catchline] MENU AND HARBOUR SYSTEM CHECKS PASSED (native state/input methods; visual controls still need player review)");
        }
    }
}

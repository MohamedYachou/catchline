using System;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Design 14.1, 14.2, 14.6: Mira's day cards, her stop order and fuel by route, and a whole two-stop day played headless
    // (out, Next stop across to the second ground, home) with the fuel paid per leg and none burned at anchor.
    public static class DayRouteChecks
    {
        const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool pass, string label) { if (!pass) throw new Exception("Day route check failed: " + label); }
        static object Call(VoyageGame game, string method, params object[] args) => typeof(VoyageGame).GetMethod(method, Private).Invoke(game, args);
        static bool Until(VoyageGame g, Func<bool> done, float seconds = 600f)
        {
            for (float t = 0; t < seconds && !done(); t += .05f) g.Tick(.05f);
            return done();
        }

        public static void Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Isolated day route check").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.Build();
            typeof(VoyageGame).GetField("showTitle", Private).SetValue(game, false);
            var s = game.State;
            s.Hull = 1; s.Coins = 5000; s.Fuel = s.FuelCapacity; s.FoodMinutes = 100; s.Bait = 40;
            s.Charts.Add(1); s.Charts.Add(2);
            Call(game, "RebuildBoat", true);
            game.RadioAuto = true;

            Call(game, "BuildDayCards");
            var cards = game.DayCards;
            Debug.Log("[Catchline] DAY cards " + string.Join(" | ", cards.Select(c => $"{c.Kind} {c.Fuel:0.#} fuel (saves {c.Saved:0.#}) {c.Possible}: {string.Join(" > ", c.Stops.Select(x => x.Name))}")));
            Check(cards.Count == 3 && cards[0].Kind == "easy" && cards[0].Stops.Count == 1, "easy card is one stop");
            Check(cards[1].Stops.Count == 2 && cards[2].Stops.Count >= 2, "medium two stops, hard two or three");
            Check(cards.All(c => c.Saved >= 0 && c.Fuel > 0), "Mira's order is never worse than another order");
            Check(cards.All(c => c.Stops.Select(x => x.Spot + "/" + x.Ground).Distinct().Count() == c.Stops.Count), "no ground twice on one day");
            float bigMedium = cards[1].Stops.Max(x => Grounds.ForMap(x.Spot).First(g => g.Id == x.Ground).Day.Max(e => GameData.Get(e.species).MaxKg));
            float bigEasy = cards[0].Stops.Max(x => Grounds.ForMap(x.Spot).First(g => g.Id == x.Ground).Day.Max(e => GameData.Get(e.species).MaxKg));
            Check(bigMedium >= bigEasy, "medium reaches bigger fish than easy");

            // A tank too small for the hard route greys that card with her reason.
            float fuel = s.Fuel; s.Coins = 0; s.Fuel = cards[0].Fuel;
            Call(game, "BuildDayCards");
            Check(game.DayCards[0].Possible && game.DayCards.Skip(1).Any(c => !c.Possible && c.Line.Contains("Too far")), "out-of-range cards are greyed with Mira's reason");
            s.Fuel = fuel; s.Coins = 5000;

            Call(game, "BuildDayCards");
            var medium = game.DayCards[1];
            Check(game.ChooseDay(medium) && game.RestaurantPhase == VoyageGame.DayPhase.Plan, "choosing a card opens tonight's plan");
            Check(game.DayRoute.Count == 2, "the route is the card's stops");
            Call(game, "RestaurantPlanAccepted");
            Check(game.RestaurantPhase == VoyageGame.DayPhase.Out, "Got it sails");
            float first = s.FuelCapacity - s.Fuel;
            Check(Mathf.Abs(first - GameData.TripFuel(medium.Stops[0].Spot)) < .01f, $"first leg paid at departure ({first})");
            Check(Until(game, () => game.CurrentMode == VoyageGame.Mode.Fishing && game.Leg == VoyageGame.TripLeg.None && game.RadioOpen == null), "reaches the first stop");
            Check(game.ActiveSpot == medium.Stops[0].Spot && game.ActiveGroundId == medium.Stops[0].Ground, "anchored at the first stop's ground");
            float atAnchor = s.Fuel;
            Until(game, () => false, 30f);
            Check(Mathf.Abs(s.Fuel - atAnchor) < .001f, "no fuel burned at anchor on a route day");

            Check(game.HasNextStop && game.NextStopBlocker() == null, "Next stop is open");
            Check(game.NextStop(), "Next stop sails");
            Check(game.DayStopAt == 1, "the route moves on");
            Check(Until(game, () => game.CurrentMode == VoyageGame.Mode.Fishing && game.Leg == VoyageGame.TripLeg.None && game.RadioOpen == null, 900f),
                $"reaches the second stop (mode {game.CurrentMode}, leg {game.Leg})");
            Check(game.ActiveSpot == medium.Stops[1].Spot && game.ActiveGroundId == medium.Stops[1].Ground, $"anchored at the second stop's ground ({game.ActiveSpot}/{game.ActiveGroundId})");
            Check(!game.HasNextStop, "the last stop has no Next");

            game.HeadHome();
            Check(Until(game, () => game.CurrentMode == VoyageGame.Mode.Harbour, 900f), "sails home");
            float spent = s.FuelCapacity - s.Fuel;
            Check(Mathf.Abs(spent - medium.Fuel) < .01f, $"the day used exactly the route's fuel ({spent} vs {medium.Fuel})");
            Debug.Log($"[Catchline] DAY ROUTE CHECKS PASSED: {medium.Stops.Count} stops, {spent:0.#} fuel, phase {game.RestaurantPhase}");
        }
    }
}

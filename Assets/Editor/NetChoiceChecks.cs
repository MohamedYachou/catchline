using System;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Isolated scratch runner; not executed in the main project or against a player's save.
    public static class NetChoiceChecks
    {
        const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string message)
        { if (!ok) throw new Exception("[Catchline] Net choice check failed: " + message); }
        static object Call(VoyageGame game, string method, params object[] args)
            => typeof(VoyageGame).GetMethod(method, Private).Invoke(game, args);
        static void Set(VoyageGame game, string property, object value)
            => typeof(VoyageGame).GetProperty(property).GetSetMethod(true).Invoke(game, new[] { value });
        static void Work(Person person)
        { for (int i = 0; i < 800 && !person.Idle; i++) person.Tick(.05f, Quaternion.identity); }

        public static void Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Net choice regression").AddComponent<VoyageGame>();
            game.SessionOnly = true;
            game.AutoPlay = true;
            game.Build();
            game.State.Hull = 2;
            Call(game, "RebuildBoat", true);
            Set(game, "CurrentMode", VoyageGame.Mode.Fishing);
            Set(game, "ActiveSpot", 0);
            var a = game.Captain;
            a.Stop();
            Check(game.SetNet(), "captain starts setting");
            Check(!game.SetNet() && !game.HaulNet(), "one actor claims the net");
            var other = new Person("Other hand", false, Vector3.zero) { Contract = new CrewMember { Role = CrewRole.Deckhand } };
            Check(!game.TryNetWork(other), "second hand cannot claim occupied winch");
            a.Stop();
            Check(game.Net == VoyageGame.NetState.Stowed, "cancel walking set rolls back");
            Check(game.SetNet(), "can retry canceled set");
            Work(a);
            NetHaulChecks.FinishCaptainSet(game);
            Check(game.Net == VoyageGame.NetState.Soaking && a.Idle, "soak releases worker");
            float soak = game.NetRemaining;
            Check(soak > GameData.ShallowNetSoakSeconds - .2f && soak <= GameData.ShallowNetSoakSeconds, "compact soak remains about40 seconds after final set tap");
            Call(game, "TickNet", soak - 1f);
            Check(game.Net == VoyageGame.NetState.Soaking && game.NetCatch == 0, "no early yield");
            Call(game, "TickNet", 0f);
            Check(Mathf.Abs(game.NetRemaining - 1f) < .001f, "zero time freezes soak");
            Call(game, "TickNet", 1f);
            int count = game.NetCatch;
            Check(game.Net == VoyageGame.NetState.Ready && count > 0 && game.NetCatchKg >= game.NetWeightRange(game.ActiveSpot, false).x, "bounded yield at 40 seconds");
            Call(game, "TickNet", 600f);
            Check(game.Net == VoyageGame.NetState.Ready && game.NetCatch == count, "ready waits without automatic haul or extra catch");
            for (int i = 0; i < game.State.CoolerCapacity; i++) game.Cooler.Add(new CaughtFish { Kg = 1f });
            Check(game.HaulNet(), "ready net can be recovered with full hold");
            a.Stop();
            Check(game.Net == VoyageGame.NetState.Ready && game.NetCatch == count, "canceled haul retains catch");
            Check(game.HaulNet(), "retry haul");
            Work(a);
            NetHaulChecks.FinishCaptainHaul(game);
            Check(game.Net == VoyageGame.NetState.Stowed && game.NetCatch == 0, "haul consumed once");
            Check(game.NetBasketCount == count && game.OnDeck.All(f => f.FromNetBasket), "haul lands in contained backlog");
            Check(game.HoldFull && !game.SetNet(), "haul does not bypass full hold and basket blocks next set");
            game.Cooler.Clear();
            int landed = game.Stats.Landed;
            Call(game, "TickNet", 1000f);
            Check(game.Stats.Landed == landed && !game.HaulNet(), "completed haul cannot repeat");
            foreach (var fish in game.OnDeck) UnityEngine.Object.DestroyImmediate(fish.Root.gameObject);
            game.OnDeck.Clear();
            Check(game.SetNet(), "empty basket releases next cycle");
            // Exercise cancellation after arrival, while the active setting game owns the winch.
            for (int i = 0; i < 400 && a.Walking; i++) a.Tick(.01f, Quaternion.identity);
            Check(a.Busy && game.NetGameActive && game.NetGameSetting, "active setting game reached");
            a.Stop();
            Check(game.Net == VoyageGame.NetState.Stowed && game.NetCatch == 0, "cancel active set releases ownership");
            // Yield uses the location table, never paid-bait power or nonlocal trophies.
            for (int seed = 0; seed < 100; seed++)
            {
                var state = new GameState(seed) { Hull = 2 };
                Set(game, "State", state);
                for (int spot = 0; spot < GameData.Spots.Length; spot++)
                {
                    Set(game, "ActiveSpot", spot);
                    Call(game, "RollCompactCatch");
                    var fish = (System.Collections.Generic.List<(Species species, float kg)>)typeof(VoyageGame).GetField("netFish", Private).GetValue(game);
                    Check(fish.Count > 0 && fish.Sum(f => f.kg) > 0, "all seeded locations yield 3-5");
                    Check(fish.All(f => GameData.Spots[spot].Table.Any(e => e.species == f.species)), "catch remains local");
                    Check(fish.All(f => f.species == Species.Herring || f.species == Species.Mackerel || f.species == Species.Whiting || f.species == Species.Pollock), "schooling species only");
                }
            }
            Call(game, "ResetNet");
            Debug.Log("[Catchline] NET CHOICE CHECKS PASSED: claim, cancellation, soak, bounded catch, ready waiting and safe basket");
        }
    }
}

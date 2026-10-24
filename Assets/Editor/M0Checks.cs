using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // M0 acceptance (docs/MASTER-PLAN.md): one work-speed model, no market saturation, no prepare premium.
    // Run in a Unity scratch copy: -executeMethod Catchline.EditorTools.M0Checks.Run
    public static class M0Checks
    {
        const BindingFlags Private = BindingFlags.Instance | BindingFlags.NonPublic;
        const BindingFlags AnyMember = BindingFlags.Instance | BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
        const float Dt = .005f, Tolerance = .011f;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("M0: " + why); }
        static object Call(VoyageGame g, string name, params object[] args) => typeof(VoyageGame).GetMethod(name, Private).Invoke(g, args);
        static void Field(VoyageGame g, string name, object value) => typeof(VoyageGame).GetField(name, Private).SetValue(g, value);
        static void Property(VoyageGame g, string name, object value) => typeof(VoyageGame).GetProperty(name).GetSetMethod(true).Invoke(g, new[] { value });

        // Seconds this person spends in each Busy label while the job runs to completion (walking time excluded).
        static Dictionary<string, float> Timed(Person p)
        {
            var seconds = new Dictionary<string, float>();
            for (int i = 0; i < 40000 && !p.Idle; i++)
            {
                if (p.Busy) { seconds.TryGetValue(p.BusyLabel, out float s); seconds[p.BusyLabel] = s + Dt; }
                p.Tick(Dt, Quaternion.identity);
            }
            Check(p.Idle, "job finishes");
            return seconds;
        }

        static int TicksFor(Person p, float baseSeconds)
        {
            p.Stop(); bool done = false; int ticks = 0;
            p.Do("M0 same job", baseSeconds, () => done = true);
            while (!done && ticks < 100000) { p.Tick(Dt, Quaternion.identity); ticks++; }
            Check(done, "timed action completes");
            return ticks;
        }

        static DeckFish Landed(VoyageGame g)
        {
            g.LandFish(g.Rods[0], Species.Herring, .2f);
            return g.OnDeck.Last();
        }

        public static void Run()
        {
            Directory.CreateDirectory("Logs/m0");
            ArtImport.BuildLibrary();
            Formula();
            RemovedSymbols();
            NoMarketSaturation();
            LegacyPreparedSave();
            CompactDeckSpeed();
            Debug.Log("[Catchline] M0 CHECKS PASSED");
            Debug.Log("[Catchline] Snapshot written to Logs/m0");
        }

        static void Formula()
        {
            // duration = base / (skill / 100) / levelMult ; walk = 2.2 m/s * (skill / 100) * levelMult
            Check(Mathf.Approximately(WorkSpeed.Duration(2f, 100f, 1f), 2f), "skill 100 level 1 runs at base duration");
            Check(Mathf.Approximately(WorkSpeed.Duration(2f, 50f, 1f), 4f), "skill 50 takes twice as long");
            Check(Mathf.Approximately(WorkSpeed.Duration(1.5f, 100f, 1.5f), 1f), "level multiplier shortens the base duration");
            Check(Mathf.Approximately(WorkSpeed.Walk(100f, 1f), 2.2f) && Mathf.Approximately(GameData.WalkSpeed, 2.2f), "walk 2.2 m/s at skill 100");
            Check(Mathf.Approximately(WorkSpeed.Walk(65f, 1.03f), 2.2f * .65f * 1.03f), "walk scales with skill and level");
            Check(Mathf.Approximately(GameData.PickupTime, .5f) && Mathf.Approximately(GameData.StowTime, .6f), "pickup 0.5 s and stow 0.6 s base durations");
            Check(Mathf.Approximately(GameData.BaitTime, 1f) && Mathf.Approximately(GameData.CastTime, .5f), "bait 1.0 s and cast 0.5 s base durations");
            Check(Mathf.Approximately(GameData.NetSetTime, 2f) && Mathf.Approximately(GameData.NetHaulTime, 5f), "net set 2 s and haul 5 s base durations");
            var p = new Person("M0 probe", false, Vector3.zero);
            Check(Mathf.Approximately(p.Speed, 1f) && p.Skill == 100f && p.LevelMult == 1f, "a new person is skill 100, level 1");
        }

        static void RemovedSymbols()
        {
            foreach (var name in new[] { "CrewWorkSpeed", "DeckhandHandlingSpeed", "CompactPickupTime", "CompactStowTime", "MarketDropPerFish", "MarketRecovery" })
                Check(typeof(GameData).GetField(name, AnyMember) == null, "GameData." + name + " is gone");
            Check(typeof(GameData).GetMethod("Speed", AnyMember) == null, "GameData.Speed(Grade) is gone");
            foreach (var name in new[] { "Prepared", "PreparedBonus", "PreparedQuality" })
                Check(typeof(CaughtFish).GetField(name, AnyMember) == null, "CaughtFish." + name + " is gone");
            Check(typeof(GameState).GetField("Market", AnyMember) == null, "GameState.Market is gone");
            Check(typeof(GameState).GetField("Tier5Condition", AnyMember) == null && typeof(GameState).GetField("Tier5Broken", AnyMember) == null, "legacy tier-5 condition arrays are gone");
            Check(typeof(VoyageGame).GetProperty("WorkMult", AnyMember) == null, "VoyageGame.WorkMult is gone");
            Check(typeof(VoyageGame).GetMethod("FishHandlingSeconds", AnyMember) == null, "FishHandlingSeconds is gone");
            // Chum stays: M3 builds on it.
            Check(typeof(GameState).GetField("Chum", AnyMember) != null && PrepOrderSettings.ChumYield(Species.Herring, .2f) == 1, "chum code retained");
        }

        static void NoMarketSaturation()
        {
            foreach (int hull in new[] { 0, 1, 2, 3 })
            {
                var state = new GameState(700 + hull) { Hull = hull };
                float price = state.PricePerKg(Species.Herring);
                var one = new CaughtFish { Species = Species.Herring, Kg = .2f, StowedAt = 0f };
                int single = state.ValueOf(one, 0f);
                var fifty = Enumerable.Range(0, 50).Select(_ => new CaughtFish { Species = Species.Herring, Kg = .2f, StowedAt = 0f }).ToList();
                var report = state.Sell(fifty, 0f);
                Check(report.FishSold == 50 && report.Coins == 50 * single, "all 50 herring pay the same price (hull " + hull + ")");
                Check(state.PricePerKg(Species.Herring) == price && state.ValueOf(one, 0f) == single, "selling 50 herring does not change the herring price (hull " + hull + ")");
                var again = state.Sell(fifty.Select(f => new CaughtFish { Species = f.Species, Kg = f.Kg, StowedAt = 0f }).ToList(), 0f);
                Check(again.Coins == report.Coins, "a second sale pays exactly the same (hull " + hull + ")");
                state.EndVoyage(new SaleReport());
                Check(state.PricePerKg(Species.Herring) == price, "ending the voyage leaves the price alone (hull " + hull + ")");
            }
        }

        static void LegacyPreparedSave()
        {
            string path = Path.Combine(Path.GetTempPath(), "catchline-m0-" + Guid.NewGuid() + ".json");
            try
            {
                // An old save: prepared fish with the 25%/150% bonus fields, plus the retired market and tier-5 condition arrays.
                File.WriteAllText(path, "{\"Version\":1,\"Coins\":50,\"Hull\":3,\"Owned\":[],\"Charts\":[],\"Board\":[],\"Offers\":[],\"Active\":[],"
                    + "\"Market\":[0.5,0.5,0.5],\"HasTier5Condition\":true,\"Tier5Condition\":[10,100,100,100,100,100,100,100],\"Tier5Broken\":[true,false,false,false,false,false,false,false],"
                    + "\"UnsoldCatch\":[{\"Species\":0,\"Kg\":0.2,\"StowedAt\":-5,\"Prepared\":true,\"PreparedQuality\":0.7,\"PreparedBonus\":1.5},"
                    + "{\"Species\":6,\"Kg\":4,\"StowedAt\":-5,\"Prepared\":true,\"PreparedQuality\":1,\"PreparedBonus\":1.25},"
                    + "{\"Species\":0,\"Kg\":0.2,\"StowedAt\":-5}],\"LogCount\":[0],\"LogBest\":[0]}");
                var loaded = GameState.Load(path);
                Check(loaded != null && loaded.Coins == 50 && loaded.UnsoldCatch.Count == 3, "a save with prepared fish loads");
                for (int i = 0; i < 3; i++)
                {
                    var f = loaded.UnsoldCatch[i];
                    var d = GameData.Get(f.Species);
                    int raw = Mathf.Max(1, Mathf.RoundToInt(f.Kg * d.PricePerKg * (1f + .5f * Mathf.InverseLerp(d.MinKg, d.MaxKg, f.Kg))));
                    Check(loaded.Freshness(f, 0f) == 1f && loaded.ValueOf(f, 0f) == raw, "formerly prepared fish are worth the raw value (fish " + i + ")");
                }
                Check(loaded.ValueOf(loaded.UnsoldCatch[0], 0f) == loaded.ValueOf(loaded.UnsoldCatch[2], 0f), "a prepared herring equals an unprepared herring");
                var expected = loaded.UnsoldCatch.Sum(f => loaded.ValueOf(f, 0f));
                loaded.Save(path);
                var again = GameState.Load(path);
                Check(again != null && again.UnsoldCatch.Count == 3, "the catch survives a re-save");
                var quote = again.QuoteSale(again.UnsoldCatch, 0f);
                int before = again.Coins;
                var sale = again.Sell(again.UnsoldCatch, 0f);
                Check(sale.Coins == expected && quote.Coins == expected && again.Coins == before + expected, "the old prepared catch sells at raw value");
            }
            finally { if (File.Exists(path)) File.Delete(path); }
        }

        static void CompactDeckSpeed()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("M0 isolated compact fisher").AddComponent<VoyageGame>();
            game.SessionOnly = true; game.Build(); Field(game, "showTitle", false);
            Check(game.TrialCompactFisher() && game.State.Hull == 2, "compact fisher fixture");
            game.State.Deckhand = null; game.State.ExtraCrew.Clear(); game.SyncCrew();
            game.State.Coins = 1000; game.State.EnsureCrewRoleOffers();
            Check(game.State.Hire(game.State.Board.First(c => c.Role == CrewRole.Deckhand)), "hire a deckhand");
            game.State.Deckhand.Grade = Grade.Veteran; // Grades used to change speed; they no longer do.
            game.SyncCrew();
            Property(game, "CurrentMode", VoyageGame.Mode.Fishing);
            Property(game, "ActiveSpot", 0);
            Field(game, "panelOpen", false);
            var captain = game.Captain; var hand = game.Hand;
            Check(hand != null && hand.Contract.Role == CrewRole.Deckhand, "real deckhand aboard");
            Check(captain.Skill == 100f && captain.LevelMult == 1f, "captain is skill 100, level 1");
            Check(Mathf.Approximately(captain.Speed, hand.Speed) && Mathf.Approximately(WorkSpeed.Walk(captain), WorkSpeed.Walk(hand)), "captain and hand share one speed model");

            // Captain: real pickup and stow on the compact boat.
            var fish = Landed(game);
            Call(game, "Fetch", captain, fish);
            var captainJob = Timed(captain);
            Check(captainJob.ContainsKey("Picking up") && captainJob.ContainsKey("Stowing") && game.Cooler.Count == 1, "captain really picked up and stowed");
            float captainPickup = captainJob["Picking up"], captainStow = captainJob["Stowing"];
            Debug.Log($"[Catchline] M0 captain compact pickup={captainPickup:0.000}s stow={captainStow:0.000}s");
            Check(captainPickup < 1f && captainStow < 1f, "captain pickup and stow are under 1 s on the compact boat");
            Check(Mathf.Abs(captainPickup - GameData.PickupTime) <= Tolerance && Mathf.Abs(captainStow - GameData.StowTime) <= Tolerance, "captain pickup 0.5 s and stow 0.6 s");

            // Hand: the same job takes the same time.
            fish = Landed(game);
            Call(game, "Fetch", hand, fish);
            var handPickup = Timed(hand);
            Check(hand.Carrying != null && handPickup.ContainsKey("Picking up"), "hand really picked up");
            Call(game, "Stow", hand);
            var handStow = Timed(hand);
            Check(handStow.ContainsKey("Stowing") && game.Cooler.Count == 2, "hand really stowed");
            Debug.Log($"[Catchline] M0 hand compact pickup={handPickup["Picking up"]:0.000}s stow={handStow["Stowing"]:0.000}s");
            Check(Mathf.Abs(handPickup["Picking up"] - captainPickup) <= Tolerance, "hand and captain pick up in the same time");
            Check(Mathf.Abs(handStow["Stowing"] - captainStow) <= Tolerance, "hand and captain stow in the same time");

            // And any other job: identical ticks for identical base duration.
            foreach (float seconds in new[] { GameData.BaitTime, GameData.CastTime, GameData.NetSetTime, GameData.NetHaulTime })
            {
                int a = TicksFor(captain, seconds), b = TicksFor(hand, seconds);
                Check(a == b && Mathf.Abs(a * Dt - seconds) <= Tolerance, $"captain and hand both take {seconds:0.0} s for a {seconds:0.0} s job");
            }
            UnityEngine.Object.DestroyImmediate(game.gameObject);
        }
    }
}

using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class NetHaulChecks
    {
        const BindingFlags Hidden = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("Net tap check failed: " + why); }
        static object Call(VoyageGame g, string key, params object[] args) => typeof(VoyageGame).GetMethod(key, Hidden).Invoke(g, args);
        static void Set(VoyageGame g, string key, object value) => typeof(VoyageGame).GetProperty(key).GetSetMethod(true).Invoke(g, new[] { value });
        static void Tick(VoyageGame g, float dt) { Call(g, "TickNet", dt); g.Captain.Tick(dt, Quaternion.identity); }
        static VoyageGame Fixture()
        {
            var g = new GameObject("Isolated tap net").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
            Set(g, "State", new GameState(37) { Hull = 2, FoodMinutes = 24 }); Call(g, "RebuildBoat", true);
            Set(g, "CurrentMode", VoyageGame.Mode.Fishing); Set(g, "ActiveSpot", 0);
            typeof(VoyageGame).GetField("showTitle", Hidden).SetValue(g, false);
            return g;
        }
        public static void ReachCaptainWinch(VoyageGame g)
        {
            for (int i = 0; i < 800 && g.Captain.Walking; i++) g.Captain.Tick(.05f, Quaternion.identity);
            Check(g.NetGameActive && g.Captain.Busy, "actual cancellable captain activity reached");
        }
        public static void FinishCaptainSet(VoyageGame g)
        {
            if (!g.NetGameActive) ReachCaptainWinch(g);
            Check(g.NetGameSetting, "setting uses its own timing game");
            for (int i = 0; i < 700 && g.NetGameActive; i++)
            {
                if (g.NetGamePhase >= .43f && g.NetGamePhase <= .55f) g.TapNetGame();
                Tick(g, .025f);
            }
            Check(!g.NetGameActive && g.Net == VoyageGame.NetState.Soaking, "three clean timed casts deploy net");
        }
        public static float FinishCaptainHaul(VoyageGame g)
        {
            if (!g.NetGameActive) ReachCaptainWinch(g);
            Check(!g.NetGameSetting, "haul uses tension game"); float elapsed = 0;
            for (int i = 0; i < 800 && g.NetGameActive; i++)
            {
                if (g.NetGameTension < .64f) g.TapNetGame();
                Tick(g, .025f); elapsed += .025f;
            }
            Check(!g.NetGameActive && g.Net == VoyageGame.NetState.Stowed, "balanced tap rhythm recovers net");
            return elapsed;
        }
        static void Ready(VoyageGame g) { Call(g, "RollCompactCatch"); Set(g, "Net", VoyageGame.NetState.Ready); }
        sealed class FixedRoll : System.Random
        {
            readonly double value; public FixedRoll(double value) { this.value = value; }
            public override double NextDouble() => value;
        }
        public static void Run()
        {
            ArtImport.BuildLibrary(); EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = Fixture(); int nets = g.State.NetInventory;
            Check(g.SetNet(), "captain claims setting"); ReachCaptainWinch(g);
            Tick(g, 3); Check(g.NetGameProgress == 0 && g.NetGameSetting, "setting never completes without taps");
            g.CancelNetHaulGame(); Check(g.Net == VoyageGame.NetState.Stowed && g.State.NetInventory == nets, "cancel preserves reusable net");
            Check(g.SetNet(), "retry setting"); FinishCaptainSet(g);
            Check(g.State.NetInventory == nets && g.NetRemaining >= GameData.ShallowNetSoakSeconds - .1f, "clean setting reuses fitted net and starts40s soak");
            Call(g, "TickNet", GameData.ShallowNetSoakSeconds); int fish = g.NetCatch; Check(fish > 0 && g.NetCatchKg >= g.NetWeightRange(g.ActiveSpot, false).x, "schooling mass yield");
            Check(g.HaulNet(), "claim haul"); ReachCaptainWinch(g); Tick(g, 4);
            Check(g.NetGameProgress == 0 && g.NetCatch == fish, "idle game cannot win");
            Check(g.TapNetGame(), "one tap accepted"); Tick(g, 0);
            Check(g.NetGameProgress == 0, "zero-dt pause does not consume queued input");
            Tick(g, .025f); float one = g.NetGameProgress; Tick(g, 2);
            Check(g.NetGameActive && g.NetGameProgress < one, "one press never repeats; cold progress slips away");
            for (int i = 0; i < 8; i++) { g.TapNetGame(); Tick(g, 2); }
            Check(g.NetGameProgress < .1f && g.NetGameDamage == 0, "lazy isolated taps cannot win without nearing red");
            Set(g, "NetGameProgress", .7f); Set(g, "NetGameTension", .77f); Tick(g, .2f);
            float warmLoss = .7f - g.NetGameProgress;
            Set(g, "NetGameProgress", .7f); Set(g, "NetGameTension", .3f); Tick(g, .2f);
            Check(.7f - g.NetGameProgress > warmLoss * 3, "near-red tension loses far less progress than slack line");
            Set(g, "NetGameProgress", .7f); Set(g, "NetGameTension", .99f); Tick(g, .2f);
            Check(.7f - g.NetGameProgress > warmLoss * 10, "overload rapidly loses progress before tear");
            g.CancelNetHaulGame(); g.CancelNetHaulGame();
            Check(g.Net == VoyageGame.NetState.Ready && g.NetCatch == fish && g.State.NetInventory == nets, "repeat cancel preserves exact catch/inventory");
            g.State.Rng = new System.Random(771); var untouched = new System.Random(771);
            Check(g.HaulNet(), "retry careful haul"); float elapsed = FinishCaptainHaul(g);
            Check(elapsed > 3 && elapsed < 15, "careful active haul takes seconds: " + elapsed);
            Check(g.NetBasketCount == fish && g.State.NetInventory == nets && g.Stats.Landed == fish, "whole batch once, successful net remains reusable");
            Check(g.State.Rng.Next() == untouched.Next(), "captain skill consumes no chance roll");
            Check(!g.TapNetGame(), "stale tap cannot duplicate catch");
            foreach (var f in g.OnDeck) UnityEngine.Object.DestroyImmediate(f.Root.gameObject); g.OnDeck.Clear();
            Call(g, "ResetNet"); Ready(g); Check(g.HaulNet(), "begin tear test"); ReachCaptainWinch(g);
            // Two deliberately overloaded pulls, with enough separation for real input.
            for (int i = 0; i < 2; i++) { Set(g, "NetGameTension", .95f); Check(g.TapNetGame(), "overload press accepted after cooldown"); Tick(g, .25f); }
            Check(!g.NetGameActive && g.State.NetInventory == nets - 1 && g.NetCatch == 0 && g.NetBasketCount == 0, $"two overloaded taps destroy exactly one net and lose batch (active={g.NetGameActive}, stock={g.State.NetInventory}, catch={g.NetCatch}, basket={g.NetBasketCount}, mistakes={g.NetGameDamage})");
            Tick(g, 10); g.CancelNetHaulGame(); Check(g.State.NetInventory == nets - 1, "tear callback cannot consume another reserve");
            Check(g.SetNet(), "spare permits setting"); ReachCaptainWinch(g);
            for (int i = 0; i < 2; i++)
            {
                while (g.NetGamePhase > .15f || g.NetGamePhase < .02f) Tick(g, .025f);
                g.TapNetGame(); Tick(g, .5f);
            }
            Check(!g.NetGameActive && g.State.NetInventory == nets - 2, "two missed setting casts tear one reserve");
            g.State.NetInventory = 0; Check(!g.SetNet(), "no spare cannot deploy phantom net");
            // Exact worker probability boundary, exercised through actual claim/completion.
            foreach (double roll in new[] { .799999, .8 })
            {
                Call(g, "ResetNet"); g.State.NetInventory = 3; Ready(g); fish = g.NetCatch;
                g.State.Rng = new FixedRoll(roll);
                var hand = new Person("Net hand", false, Vector3.zero) { Grid = g.Grid, Contract = new CrewMember { Role = CrewRole.Deckhand } };
                hand.Build(g.Boat, g.State.HullDef.NetAccess, Palette.Oilskin, Palette.Accent);
                Check(g.TryNetWork(hand), "hand claims recovery"); hand.Tick(.01f, Quaternion.identity);
                hand.Tick(5, Quaternion.identity);
                Check(g.State.NetInventory == (roll < .8 ? 3 : 2), "worker80/20 boundary consumes net only on tear");
                Check(g.NetBasketCount == (roll < .8 ? fish : 0), "worker safe batch or lost batch matches risk");
                foreach (var f in g.OnDeck) UnityEngine.Object.DestroyImmediate(f.Root.gameObject); g.OnDeck.Clear();
                hand.Stop(); UnityEngine.Object.DestroyImmediate(hand.Root.gameObject);
            }
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] NET HAUL CHECKS PASSED: tap-only set/haul, skill band, cold/idle/overload decay, tears/reserves, cancellation/exact batch/no captain RNG, worker80/20 boundary");
        }
    }
}

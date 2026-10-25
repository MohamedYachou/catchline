using System;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Crab pots on the smaller boats: a skiff buys one pot (a second is refused), the compact fisher carries two; at a
    // ground the pot soaks, the captain hauls it through the cage view, keepers land and pay the hand-sorted bonus, and
    // the pot soaks again. The save keeps the pots.
    // Batch: -executeMethod Catchline.EditorTools.CrabPotChecks.Run
    public static class CrabPotChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string what) { if (!ok) throw new Exception("CRABPOTS: " + what); }

        // A skiff in harbour with coins, ready to buy pots (renders use it too).
        public static VoyageGame Fixture(int hull)
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Crab pot check").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
            g.NewGame(); g.State.Hull = hull; g.State.Coins = 5000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", H).Invoke(g, new object[] { false });
            foreach (var flag in new[] { "showTitle", "paused", "panelOpen", "captureFreeze" }) typeof(VoyageGame).GetField(flag, H).SetValue(g, false);
            g.Tick(.05f);
            return g;
        }

        public static void Run()
        {
            try
            {
                var g = Fixture(1);
                Check(g.MaxCrabPots == 1 && g.PotsSet == 0, "a skiff carries one pot, none yet");
                Check(g.BuyCrabPot() && g.State.CrabPots == 1 && g.PotsSet == 1, "buy one pot");
                Check(!g.BuyCrabPot() && g.State.CrabPots == 1, "a second pot is refused on a skiff");
                string path = System.IO.Path.Combine(Application.temporaryCachePath, "crabpot-check.json"); g.State.Save(path); var loaded = GameState.Load(path); System.IO.File.Delete(path);
                Check(loaded != null && loaded.CrabPots == 1, "the save keeps the pot");

                g.Showcase(0, 0); g.Tick(.05f);
                Check(g.AtFishingGround && g.PotsSet == 1, "at a ground with the pot set");
                var timers = (float[])typeof(VoyageGame).GetField("buoyTimers", H).GetValue(g);
                for (int i = 0; i < 40; i++) g.Tick(.05f);
                Check(timers[0] > 1 && g.BuoyRemaining(0) > 0, "the pot soaks at the ground");
                Check(!g.TryBuoyWork(g.Captain), "not before it has soaked");
                timers[0] = g.BuoySoakSeconds;
                int coins = g.State.Coins;
                Check(g.TryBuoyWork(g.Captain), "the captain takes the soaked pot");
                for (int i = 0; i < 400 && !g.CageViewActive; i++) g.Tick(.05f);
                Check(g.CageViewActive, "the cage view opens at the stern");
                var cage = g.Cage;
                for (int i = 0; i < 600 && cage.Phase is CagePhase.Pull or CagePhase.Snag; i++)
                {
                    if (cage.Phase == CagePhase.Snag) g.DragCage(cage.SnagDirection); else if (i % 4 == 0) g.TapCage();
                    g.Tick(.05f);
                }
                for (int i = 0; i < 400 && cage.Phase == CagePhase.Sort; i++) { if (cage.Current is { } crab) g.FlickCage(crab.Keeper); g.Tick(.05f); }
                for (int i = 0; i < 200 && g.CageViewActive; i++) g.Tick(.05f);
                Check(cage.Phase == CagePhase.Done && !g.CageViewActive, "hauled, sorted and back on deck");
                Check(g.BuoyHauls == 1 && g.CageResult != null && g.BuoyRemaining(0) > g.BuoySoakSeconds - 15, "one haul, the pot soaks again: " + g.CageResult);
                int kept = cage.Results.FindAll(r => r.Kept && r.Crab.Keeper).Count;
                Check(kept == 0 || g.State.Coins > coins, "hand-sorted bonus paid");
                UnityEngine.Object.DestroyImmediate(g.gameObject);

                var c = Fixture(2);
                Check(c.MaxCrabPots == 2 && c.BuyCrabPot() && c.BuyCrabPot() && c.PotsSet == 2 && !c.BuyCrabPot(), "the compact fisher carries two pots");
                UnityEngine.Object.DestroyImmediate(c.gameObject);
                Debug.Log($"CRABPOTS PASS · skiff 1 pot, compact 2, haul {g.CageResult}");
                EditorApplication.Exit(0);
            }
            catch (Exception e) { Debug.LogError(e); EditorApplication.Exit(1); }
        }
    }
}

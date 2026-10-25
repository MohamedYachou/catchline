using System;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // The captain's crab cage in the real game: the buoy bubble sends the captain to the buoy, the view opens, taps
    // haul, a drag frees a snag, flicks sort, keepers land in the hold with the hand-sorted bonus, and the view returns
    // to the deck with the buoy soaking again. Leaving mid-haul gives the buoy back untouched.
    // Batch: -executeMethod Catchline.EditorTools.CageViewChecks.Run
    public static class CageViewChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string what) { if (!ok) throw new Exception("CAGEVIEW: " + what); }

        public static string Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Cage view check").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
            Check(g.StartTier5Trial(), "tier 5 trial");
            var timers = (float[])typeof(VoyageGame).GetField("buoyTimers", H).GetValue(g);

            // Leaving gives the buoy back.
            timers[0] = timers[1] = g.BuoySoakSeconds;
            Check(g.TryBuoyWork(g.Captain), "captain takes a ready buoy");
            for (int i = 0; i < 400 && !g.CageViewActive; i++) g.Tick(.05f);
            Check(g.CageViewActive, "the cage view opens at the buoy");
            g.LeaveCage(); g.Tick(.05f);
            Check(!g.CageViewActive && g.Captain.Idle && g.BuoyRemaining(0) <= 0, "leaving gives the buoy back");

            // A full haul with a right sort.
            int coins = g.State.Coins;
            Check(g.TryBuoyWork(g.Captain), "captain takes the buoy again");
            for (int i = 0; i < 400 && !g.CageViewActive; i++) g.Tick(.05f);
            Check(g.CageViewActive, "the cage view reopens");
            var cage = g.Cage; bool snagged = false;
            for (int i = 0; i < 400 && cage.Phase is CagePhase.Pull or CagePhase.Snag; i++)
            {
                if (cage.Phase == CagePhase.Snag) { snagged = true; g.DragCage(cage.SnagDirection); }
                else if (i % 4 == 0) g.TapCage();
                g.Tick(.05f);
            }
            Check(cage.Phase == CagePhase.Sort, "taps haul the cage to the rail");
            int hauls = g.BuoyHauls;
            for (int i = 0; i < 400 && cage.Phase == CagePhase.Sort; i++)
            {
                if (cage.Current is { } crab) g.FlickCage(crab.Keeper); // flicks arriving before the crab lands are held
                g.Tick(.05f);
            }
            int keepers = cage.Results.FindAll(r => r.Kept).Count; float keptKg = 0;
            foreach (var r in cage.Results) if (r.Kept) keptKg += r.Crab.Kg;
            Check(cage.Results.Count == cage.Crabs.Count, "every crab got its own flick");
            Check(cage.Phase == CagePhase.Done && cage.Fines == 0, "every crab sorted right");
            for (int i = 0; i < 200 && g.CageViewActive; i++) g.Tick(.05f);
            Check(!g.CageViewActive && g.Cam.orthographic, "the view returns to the deck camera");
            Check(g.BuoyHauls == hauls + 1 && g.CageResult.Contains($"{keepers} kept"), $"one haul recorded, keepers counted: {g.CageResult}");
            Check(keepers == 0 || g.State.Coins > coins, "hand-sorted bonus paid");
            Check(g.BuoyRemaining(0) > g.BuoySoakSeconds - 15 && g.CageResult != null, "the buoy soaks again and the result reads " + g.CageResult);
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            string text = $"CAGEVIEW PASS · {cage.Crabs.Count} crabs, {keepers} kept ({keptKg:0.0} kg), snag {snagged} · {g.CageResult}";
            Debug.Log(text);
            return text;
        }

        [MenuItem("Catchline/Checks/Cage view")]
        static void Menu() => Debug.Log(Run());
    }
}

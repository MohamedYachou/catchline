using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // The captain guts the fish waiting at the prep fisher's process table: the view opens at the board, a clean cut
    // finishes at once and builds the streak, a ragged one takes the crew's time, the next fish follows, and the view
    // hands back to the deck when the table is empty. Leaving mid-fish puts the fish back.
    // Batch: -executeMethod Catchline.EditorTools.GutViewChecks.Run
    public static class GutViewChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string what) { if (!ok) throw new Exception("GUTVIEW: " + what); }
        public static readonly Vector2[] CleanCut = { new(.05f, 0), new(.5f, .03f), new(.95f, 0) };
        public static readonly Vector2[] RaggedCut = { new(.1f, 0), new(.5f, .3f), new(.9f, .02f) };

        public static (VoyageGame g, Station table) Fixture(int fish)
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Gut view check").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
            typeof(VoyageGame).GetField("showTitle", H).SetValue(g, false);
            Check(g.StartPrepBoatTrial(), "prep boat trial");
            typeof(VoyageGame).GetMethod("SetupDeckGraph", H).Invoke(g, null); // arrival builds it; the trial skips the trip
            for (int i = 0; i < 20; i++) g.Tick(.05f);
            Check(g.CurrentMode == VoyageGame.Mode.Fishing && g.Scheduler != null, $"fishing on the deck graph ({g.CurrentMode}, {g.State.HullDef.Model})");
            // Only the captain works the table here.
            g.Scheduler.Workers.RemoveAll(w => !w.Captain);
            var table = g.DeckGraph.OfKind(StationKind.ProcessTable).FirstOrDefault();
            Check(table != null && table.In != null, "the prep fisher has a process table");
            var kinds = new[] { Species.Mackerel, Species.Pollock, Species.Cod };
            for (int i = 0; i < fish; i++) table.In.Put(new CaughtFish { Species = kinds[i % 3], Kg = 1.2f }, false);
            return (g, table);
        }

        public static void Run()
        {
            Check(GutRules.Grade(CleanCut) == GutGrade.Clean && GutRules.Grade(RaggedCut) == GutGrade.Ragged
                && GutRules.Grade(new[] { new Vector2(.4f, 0), new Vector2(.5f, 0) }) == GutGrade.None
                && GutRules.Grade(new[] { new Vector2(.95f, 0), new Vector2(.05f, 0) }) == GutGrade.None, "cut grading");
            var (g, table) = Fixture(3);
            Check(g.CaptainGutAt(table), "the captain takes a fish at the table");
            for (int i = 0; i < 400 && !g.GutViewActive; i++) g.Tick(.05f);
            Check(g.GutViewActive && g.GutWaiting, "the gut view opens with a fish on the board");
            for (int i = 0; i < 12; i++) g.Tick(.05f);
            Check(!g.Cam.orthographic && !g.Captain.Root.GetComponentInChildren<Renderer>().enabled, "close-up camera, captain hidden");
            int before = table.In.Count;

            Check(g.CutGut(CleanCut) == GutGrade.Clean && g.GutStreak == 1, "a clean cut");
            float t = 0; while (t < 1.2f && !(g.GutWaiting && table.In.Count < before)) { g.Tick(.05f); t += .05f; }
            Check(table.In.Count == before - 1 && g.GutWaiting && t < GutRules.CleanSeconds + .2f, $"clean finishes fast and the next fish follows ({t:0.00}s)");

            Check(g.CutGut(RaggedCut) == GutGrade.Ragged && g.GutStreak == 0, "a ragged cut ends the streak");
            t = 0; while (t < 5 && table.In.Count > before - 2) { g.Tick(.05f); t += .05f; }
            Check(t >= GutRules.RaggedSeconds - .1f, $"ragged takes the crew's time ({t:0.00}s)");

            for (int i = 0; i < 10 && !g.GutWaiting; i++) g.Tick(.05f);
            Check(g.CutGut(CleanCut) == GutGrade.Clean, "the last fish");
            for (int i = 0; i < 40 && g.GutViewActive; i++) g.Tick(.05f);
            Check(!g.GutViewActive && g.Cam.orthographic && g.Captain.Root.GetComponentInChildren<Renderer>().enabled, "the empty table hands back to the deck");
            Check(table.In.Count == 0, "all three fish processed");

            table.In.Put(new CaughtFish { Species = Species.Cod, Kg = 3f }, false);
            Check(g.CaptainGutAt(table), "another fish");
            for (int i = 0; i < 400 && !g.GutWaiting; i++) g.Tick(.05f);
            g.LeaveGut();
            for (int i = 0; i < 20; i++) g.Tick(.05f);
            Check(!g.GutViewActive && table.In.UnclaimedCount == 1, "leaving puts the fish back");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("GUTVIEW PASS · clean, ragged, chained three, leave");
        }
    }
}

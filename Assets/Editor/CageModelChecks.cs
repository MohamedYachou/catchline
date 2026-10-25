using System;
using Catchline.Game;

namespace Catchline.EditorTools
{
    // The crab cage minigame (docs/plans/MINIGAMES.md, section 2): fast taps bring the cage up in about three seconds,
    // stopping lets it sink back, a snag frees only the way the arrow says (or by itself after a wait), and the sort
    // pays for keepers and fines kept undersize or berried crabs.
    // Batch: -executeMethod Catchline.EditorTools.CageModelChecks.Run
    public static class CageModelChecks
    {
        static void Check(bool ok, string what) { if (!ok) throw new Exception("CAGE: " + what); }

        public static string Run()
        {
            int snags = 0, total = 200; float slowest = 0;
            for (int seed = 0; seed < total; seed++)
            {
                var cage = new CageModel(new Random(seed));
                Check(cage.Crabs.Count >= 2 && cage.Crabs.Count <= 4, "two to four crabs");
                bool snagged = false;
                // Four taps a second, dragging the right way half a second after a snag.
                for (float t = 0; t < 10 && cage.Phase is CagePhase.Pull or CagePhase.Snag; t += .05f)
                {
                    if (cage.Phase == CagePhase.Snag) { snagged = true; if (cage.Elapsed % 1 > .5f) cage.Drag(cage.SnagDirection); }
                    else if ((int)(t * 20) % 5 == 0) cage.Tap();
                    cage.Tick(.05f);
                }
                Check(cage.Phase == CagePhase.Sort, $"seed {seed} reaches the rail at four taps a second");
                if (snagged) snags++;
                slowest = Math.Max(slowest, cage.Elapsed);
                foreach (var crab in cage.Crabs) cage.Flick(crab.Keeper);
                Check(cage.Phase == CagePhase.Done && cage.Fines == 0 && cage.Results.TrueForAll(r => r.Right), "a right sort has no fines");
            }
            Check(snags > total / 5 && snags < total / 2, $"about one cage in three snags ({snags}/{total})");
            Check(slowest < 6.5f, $"fast tapping lands every cage within 6.5 s ({slowest:0.0})");

            // Not tapping: the cage sinks back.
            var idle = new CageModel(new Random(1));
            for (int i = 0; i < 4; i++) idle.Tap();
            float lifted = idle.Lift;
            for (int i = 0; i < 40; i++) idle.Tick(.05f);
            Check(idle.Lift < lifted - .15f, "the rope slips back between taps");

            // A wrong drag locks the rope for a second; the snag frees itself after the wait.
            var stuck = FindSnagging();
            while (stuck.Phase == CagePhase.Pull) stuck.Tap();
            Check(stuck.Phase == CagePhase.Snag && stuck.Lift == CageModel.SnagAt, "snag holds the cage halfway");
            Check(!stuck.Drag(-stuck.SnagDirection) && !stuck.Drag(stuck.SnagDirection), "wrong drag locks the rope");
            for (int i = 0; i < 21; i++) stuck.Tick(.05f);
            Check(stuck.Drag(stuck.SnagDirection) && stuck.Phase == CagePhase.Pull, "right drag frees it after the lock");
            var waited = FindSnagging();
            while (waited.Phase == CagePhase.Pull) waited.Tap();
            for (int i = 0; i < 70 && waited.Phase == CagePhase.Snag; i++) waited.Tick(.05f);
            Check(waited.Phase == CagePhase.Pull, "an ignored snag frees itself");

            // Keeping everything: every undersize or berried crab is a fine.
            var greedy = new CageModel(new Random(7)); int bad = greedy.Crabs.FindAll(c => !c.Keeper).Count;
            while (greedy.Phase != CagePhase.Sort) { greedy.Tap(); greedy.Tick(.05f); if (greedy.Phase == CagePhase.Snag) greedy.Drag(greedy.SnagDirection); }
            foreach (var _ in greedy.Crabs) greedy.Flick(true);
            Check(greedy.Fines == bad && greedy.Kept == greedy.Crabs.Count, "keeping everything fines each bad crab");
            Check(greedy.PriceMultiplier(new CageModel.Crab { Kg = 1, Undersize = true }) < 0 && greedy.PriceMultiplier(new CageModel.Crab { Kg = 1 }) > 1, "price multipliers");

            string text = $"CAGEMODEL PASS · {total} cages, {snags} snags, slowest {slowest:0.0}s";
            UnityEngine.Debug.Log(text);
            return text;
        }

        static CageModel FindSnagging()
        {
            for (int seed = 0; ; seed++)
            {
                var c = new CageModel(new Random(seed));
                var probe = new CageModel(new Random(seed));
                while (probe.Phase == CagePhase.Pull) probe.Tap();
                if (probe.Phase == CagePhase.Snag) return c;
            }
        }
    }
}

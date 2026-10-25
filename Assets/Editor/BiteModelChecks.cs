using System;
using Catchline.Game;
using UnityEngine;

namespace Catchline.EditorTools
{
    // The rod view's fish: a patient player who strikes only on the take hooks it; a player who strikes on the
    // deepest dip of a fake spooks it; big fish fake more and give less time.
    public static class BiteModelChecks
    {
        // Species variety: every style can still be hooked by a patient player; plaice shows the flat lift bite,
        // mackerel jumps when hooked, a conger fights longer than a herring, darters sometimes come as a shoal.
        static string Variety()
        {
            const float dt = 1 / 60f;
            int jumps = 0, shoals = 0;
            foreach (var (species, kg) in new[] { (Species.Herring, .2f), (Species.Mackerel, .5f), (Species.Plaice, 1.5f), (Species.Conger, 8f), (Species.Cod, 5f) })
                for (int seed = 0; seed < 100; seed++)
                {
                    var m = new BiteModel(species, kg, new System.Random(seed));
                    if (m.Shoal > 1) shoals++;
                    float under = 0, tilt = 0;
                    for (float t = 0; t < 40 && m.Phase != FishPhase.Hooked && !m.Finished; t += dt)
                    {
                        m.Tick(dt);
                        if (m.Phase != FishPhase.Take) continue;
                        under += dt; tilt = Mathf.Max(tilt, m.Tilt);
                        if (species == Species.Plaice) Check(m.Dip < .2f, "plaice lift bite pulled the bobber under");
                        if (under >= Mathf.Min(.3f, m.TakeWindow * .7f)) m.Strike();
                    }
                    Check(m.Phase == FishPhase.Hooked, $"{species} seed {seed} ({m.Style}) never hooked by a patient player");
                    if (species == Species.Plaice) Check(tilt > .9f, "plaice take never lay the bobber flat");
                    bool jumped = false;
                    for (float t = 0; !m.HookedDone && t < 10; t += dt) { m.Tick(dt); jumped |= m.Jump; }
                    Check(m.HookedDone, $"{species} fight never ended");
                    if (species == Species.Mackerel && jumped) jumps++;
                    if (species == Species.Herring) Check(!jumped, "herring jumped");
                }
            float herring = new BiteModel(Species.Herring, .2f, new System.Random(1)).HookedSeconds, conger = new BiteModel(Species.Conger, 8f, new System.Random(1)).HookedSeconds;
            Check(conger > herring * 1.8f, $"fight length conger {conger:0.0}s vs herring {herring:0.0}s");
            Check(jumps > 90, $"mackerel jumped in {jumps}/100 fights");
            Check(shoals > 50 && shoals < 200, $"darter shoals {shoals}/200");
            return $"variety ok (mackerel jumps {jumps}/100, shoals {shoals}/200, fight {herring:0.0}-{conger:0.0}s)";
        }
        static void Check(bool ok, string why) { if (!ok) throw new Exception("[Catchline] BiteModel failed: " + why); }

        public static string Run()
        {
            const float dt = 1 / 60f;
            int smallFakes = 0, bigFakes = 0, earlyHooks = 0;
            for (int seed = 0; seed < 200; seed++)
            {
                foreach (var (species, kg) in new[] { (Species.Herring, .15f), (Species.Cod, 6.8f) })
                {
                    float d = BiteModel.DifficultyFor(species, kg);
                    // Patient: strikes 0.3 s into the take (human reaction), never before.
                    var m = new BiteModel(d, new System.Random(seed)); bool fake = false; float under = 0;
                    for (float t = 0; t < 40 && !m.Finished && m.Phase != FishPhase.Hooked; t += dt)
                    {
                        m.Tick(dt);
                        if (m.Phase == FishPhase.Fake) { fake = true; Check(m.Dip < .95f, "a fake pulled the bobber fully under"); }
                        if (m.Phase == FishPhase.Take) { under += dt; if (under >= Mathf.Min(.3f, m.TakeWindow * .7f)) Check(m.Strike() == StrikeResult.Hooked, "strike during the take missed"); }
                    }
                    Check(m.Phase == FishPhase.Hooked, $"{species} seed {seed} never hooked by a patient player");
                    if (species == Species.Herring && fake) smallFakes++;
                    if (species == Species.Cod && fake) bigFakes++;
                    // Greedy: strikes on the first deep dip.
                    var g = new BiteModel(d, new System.Random(seed));
                    for (float t = 0; t < 40 && !g.Finished && g.Phase is not (FishPhase.Hooked or FishPhase.Spooked); t += dt)
                    {
                        g.Tick(dt);
                        if (g.Dip > .5f) { if (g.Strike() == StrikeResult.Hooked) earlyHooks++; }
                    }
                    // Asleep: never strikes; the fish spits the bait.
                    var s = new BiteModel(d, new System.Random(seed));
                    for (float t = 0; t < 60 && !s.Finished; t += dt) s.Tick(dt);
                    Check(s.Phase == FishPhase.Gone && s.Strike() == StrikeResult.TooLate, "an ignored take did not end the bite");
                }
            }
            float herring = BiteModel.DifficultyFor(Species.Herring, .15f), cod = BiteModel.DifficultyFor(Species.Cod, 6.8f);
            Check(herring < .15f && cod > .8f, $"difficulty herring {herring:0.00} cod {cod:0.00}");
            Check(bigFakes > 180 && smallFakes < 20, $"fakes: cod {bigFakes}/200, herring {smallFakes}/200");
            Check(new BiteModel(cod, new System.Random(1)).TakeWindow < .5f, "big fish take window too long");
            string variety = Variety();
            return $"BITEMODEL PASS · {variety} · cod fakes {bigFakes}/200 · herring fakes {smallFakes}/200 · greedy hooks {earlyHooks}/400";
        }
    }
}

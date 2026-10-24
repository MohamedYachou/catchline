using System;
using Catchline.Game;
using UnityEngine;

namespace Catchline.EditorTools
{
    // The rod view's fish: a patient player who strikes only on the take hooks it; a player who strikes on the
    // deepest dip of a fake spooks it; big fish fake more and give less time.
    public static class BiteModelChecks
    {
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
            return $"BITEMODEL PASS · cod fakes {bigFakes}/200 · herring fakes {smallFakes}/200 · greedy hooks {earlyHooks}/400";
        }
    }
}

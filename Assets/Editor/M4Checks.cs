using System;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Sea;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // MASTER-PLAN M4 + MAP-PLAN 7.2: grounds table, richness, moving schools, visible cues, navigator report, save, and the
    // relocating bot beating the one that never moves. Cue visuals are asserted through the data that drives them.
    public static class M4Checks
    {
        static void Check(bool ok, string what) { if (!ok) throw new Exception("[Catchline] M4 check failed: " + what); }
        static bool Near(float a, float b, float eps = .0005f) => Mathf.Abs(a - b) <= eps;
        static void Until(VoyageGame g, Func<bool> done, string what, float seconds = 120)
        {
            for (float t = 0; t < seconds && !done(); t += .05f) g.Tick(.05f);
            Check(done(), what);
        }

        public static void Run()
        {
            ArtImport.BuildLibrary();
            Table();
            Richness();
            Navigator();
            SchoolMotion();
            SaveRoundTrip();
            LiveVoyage();
            BotComparison();
            Debug.Log("[Catchline] M4 CHECKS PASSED (grounds tables + no species lost; drain/floor/recovery; bands + navigator move suggestion; school bonus 1.3 to 1.0, relocation, bounds; gulls/ring follow bands; no fishing outside a zone; save round trip; relocating bot beats stayer)");
        }

        static void Table()
        {
            for (int map = 0; map < SeaNav.Maps.Length; map++)
            {
                var nav = SeaNav.Load(SeaNav.Maps[map], GameData.Hulls[0]);
                Check(nav != null, SeaNav.Maps[map] + " navigation loads");
                var defs = Grounds.ForMap(map);
                Check(defs.Length == 3 && nav.Grounds.Count == 3, SeaNav.Maps[map] + " has three grounds");
                for (int i = 0; i < 3; i++) Check(defs[i].Id == nav.Grounds[i].Id, SeaNav.Maps[map] + " ground id matches navigation: " + defs[i].Id);
                var union = defs.SelectMany(d => d.Day.Select(e => e.species)).ToHashSet();
                foreach (var e in GameData.Spots[map].Table) Check(union.Contains(e.species), GameData.Spots[map].Name + " keeps " + e.species);
                foreach (var d in defs)
                {
                    Check(d.Night.Length == d.Day.Length && d.Night.Select(e => e.species).SequenceEqual(d.Day.Select(e => e.species)), d.Id + " night pool covers the same species");
                    Check(d.Night.Zip(d.Day, (n, y) => !Near(n.weight, y.weight)).Any(x => x), d.Id + " night pool differs from day");
                    Check(d.Day.All(e => e.weight > 0), d.Id + " weights positive");
                }
            }
        }

        static void Richness()
        {
            var st = new GameState(11) { CurrentGround = 0 };
            Check(st.GroundRich.All(r => r == 1f), "richness starts at 1.0");
            int spot = 1; st.CurrentGround = 0;
            st.OnCatch(spot, .3f, Species.Mackerel, false);
            Check(Near(Grounds.Richness(st.GroundRich, spot, 0, Species.Mackerel), .98f) && Grounds.Richness(st.GroundRich, spot, 0, Species.Herring) == 1f, "a rod catch drains that species by 0.02");
            st.OnCatch(spot, 5f, Species.Herring, true);
            Check(Near(Grounds.Richness(st.GroundRich, spot, 0, Species.Herring), .98f) && Near(Grounds.Richness(st.GroundRich, spot, 1, Species.Mackerel), 1f), "a net drains 0.004 per kg at this ground only");
            for (int i = 0; i < 100; i++) st.OnCatch(spot, 1f, Species.Mackerel, false);
            Check(Near(Grounds.Richness(st.GroundRich, spot, 0, Species.Mackerel), .3f), "floor 0.3");
            st.EndVoyage(new SaleReport());
            Check(Near(Grounds.Richness(st.GroundRich, spot, 0, Species.Mackerel), .65f) && Near(Grounds.Richness(st.GroundRich, spot, 0, Species.Herring), 1f), "a voyage recovers 0.35, capped at 1.0");
            // Rolls and bite waits use the ground: a depleted species is rarer and a depleted ground bites slower.
            var fresh = new GameState(5) { CurrentGround = 0 }; var worn = new GameState(5) { CurrentGround = 0 };
            for (int s = 0; s < worn.GroundRich.Length; s++) worn.GroundRich[s] = .4f;
            double a = 0, b = 0; for (int i = 0; i < 2000; i++) { a += fresh.RollBiteWait(spot, .5f); b += worn.RollBiteWait(spot, .5f); }
            Check(b > a * 1.5, "worn ground bites slower");
            Check(fresh.FishTable(spot).Length == Grounds.Get(spot, 0).Day.Length, "rolls draw from the ground's pool");
            var biased = new GameState(5) { CurrentGround = 0 };
            Grounds.Drain(biased.GroundRich, spot, 0, Species.Mackerel, .7f);
            float fm = biased.FishTable(spot).First(e => e.species == Species.Mackerel).weight / Grounds.Get(spot, 0).Day.First(e => e.species == Species.Mackerel).weight;
            Check(Near(fm, .3f), "species weight scales with its richness");
            var legacy = new GameState(5);
            Check(legacy.FishTable(spot) == GameData.Spots[spot].Table, "no ground anchored keeps the old map table");
        }

        static void Navigator()
        {
            Check(Grounds.BandOf(.8f) == RichnessBand.Rich && Grounds.BandOf(.799f) == RichnessBand.Thinning && Grounds.BandOf(.5f) == RichnessBand.Thinning && Grounds.BandOf(.499f) == RichnessBand.Poor, "bands rich >= .8 / thinning / poor < .5");
            int spot = 1;
            var rich = Grounds.NewRichness();
            var all = Grounds.Report(rich, spot, 0);
            Check(all.Overall == RichnessBand.Rich && !all.ShouldMove && all.Line == "Rich water here.", "fresh ground reports rich, no move");
            foreach (var e in Grounds.Get(spot, 0).Day) Grounds.Drain(rich, spot, 0, e.species, .35f);
            var r = Grounds.Report(rich, spot, 0);
            Check(r.Overall == RichnessBand.Thinning && r.ShouldMove && r.BetterGroundId != "kelp-shallows", "0.65 vs fresh grounds suggests a move: " + r.Line);
            Check(r.Species.All(s => s.band == RichnessBand.Thinning) && r.Line.Contains("thinning here") && r.Line.Contains("richer"), "report line names the species and a richer ground: " + r.Line);
            var near = Grounds.NewRichness();
            foreach (var e in Grounds.Get(spot, 0).Day) Grounds.Drain(near, spot, 0, e.species, .29f);
            Check(!Grounds.Report(near, spot, 0).ShouldMove, "0.29 gap is not enough to suggest moving");
            var exact = Grounds.NewRichness();
            foreach (var e in Grounds.Get(spot, 0).Day) Grounds.Drain(exact, spot, 0, e.species, .3f);
            Check(Grounds.Report(exact, spot, 0).ShouldMove, "0.30 gap suggests moving");
            // Only the player's targeted species count.
            var targetedRich = Grounds.NewRichness();
            Grounds.Drain(targetedRich, spot, 0, Species.Mackerel, .6f);
            Check(Grounds.Report(targetedRich, spot, 0, s => s == Species.Herring).Overall == RichnessBand.Rich, "untargeted species ignored");
            Check(Near(Grounds.EventWarningSeconds(0), 8f) && Near(Grounds.EventWarningSeconds(4), 10f), "event warning 8 s + 0.5 s per level");
            Check(Grounds.GullCount(1f, 0) >= 3 && Enumerable.Range(0, 40).All(i => Grounds.GullCount(.9f, i) is >= 3 and <= 6)
                && Enumerable.Range(0, 40).All(i => Grounds.GullCount(.65f, i) is >= 1 and <= 2) && Enumerable.Range(0, 40).All(i => Grounds.GullCount(.4f, i) == 0), "gull count follows the bands");
            Check(Grounds.RingTint(1f) != Grounds.RingTint(.65f) && Grounds.RingTint(.65f) != Grounds.RingTint(.4f), "ring tint differs by band");
        }

        static void SchoolMotion()
        {
            var nav = SeaNav.Load(SeaNav.Maps[1], GameData.Hulls[0]);
            var schools = new Schools(nav, 31);
            for (int i = 0; i < nav.Grounds.Count; i++)
            {
                var s = schools.ByGround[i]; var zone = nav.Grounds[i];
                Check(s.Radius >= 6f && s.Radius <= 8f, "school radius 6-8 m");
                Check(Near(schools.Bonus(i, s.Position), 1.3f), "bonus 1.3 at the school centre");
                // Sweep boat positions along a ray out of the school to the zone edge.
                var dir = new Vector2(Mathf.Cos(i + 1), Mathf.Sin(i + 1));
                float previous = 1.3f; Vector2 last = s.Position; bool reachedEdge = false;
                for (float d = 0; d < zone.Radius * 2.2f; d += .1f)
                {
                    var p = s.Position + dir * d;
                    if (!zone.Contains(p)) { Check(Near(schools.Bonus(i, p), 1f), "no school bonus outside the zone"); reachedEdge = true; break; }
                    float bonus = schools.Bonus(i, p);
                    Check(bonus <= previous + .0001f && bonus >= 1f - .0001f, "bonus falls monotonically from 1.3 to 1.0");
                    if (d <= s.Radius) Check(Near(bonus, 1.3f), "1.3 inside the school");
                    previous = bonus; last = p;
                }
                Check(reachedEdge && Near(schools.Bonus(i, last), 1f, .02f), "bonus is 1.0 at the zone edge");
                Check(schools.Bonus(i, s.Position + dir * (s.Radius + 1f)) is > 1f and < 1.3f, "bonus is between 1.0 and 1.3 in between");
            }
            // Drift speed and zone bounds over time; jump every 3-5 minutes.
            var tracked = new Schools(nav, 77); var first = tracked.ByGround.Select(s => s.Position).ToArray();
            var jumpsAt = new float[nav.Grounds.Count]; float clock = 0; int maxJumps = 0;
            for (clock = 0; clock < 1500f; clock += .5f)
            {
                var before = tracked.ByGround.Select(s => (s.Position, s.Jumps)).ToArray();
                tracked.Tick(.5f, _ => 1f);
                for (int i = 0; i < nav.Grounds.Count; i++)
                {
                    var s = tracked.ByGround[i]; var zone = nav.Grounds[i];
                    Check((s.Position - zone.Centre).magnitude <= zone.Radius - s.Radius + .01f, "school stays fully inside its zone");
                    if (s.Jumps == before[i].Jumps) Check((s.Position - before[i].Position).magnitude / .5f <= .41f, "drift at most 0.4 m/s");
                    else
                    {
                        Check(s.Velocity.magnitude >= .199f && s.Velocity.magnitude <= .401f, "new drift 0.2-0.4 m/s");
                        if (jumpsAt[i] > 0) Check(clock - jumpsAt[i] >= 179f && clock - jumpsAt[i] <= 301f, "jump interval 3-5 min: " + (clock - jumpsAt[i]));
                        jumpsAt[i] = clock; maxJumps = Mathf.Max(maxJumps, s.Jumps);
                    }
                }
            }
            Check(maxJumps >= 4, "schools relocate over time");
            Check(tracked.ByGround.Select(s => s.Position).Zip(first, (a, b) => a != b).All(x => x), "schools moved");
            // A thin ground makes its school jump early (after the 30 s gap), a rich one does not.
            var thin = new Schools(nav, 5); int jumps0 = thin.ByGround[0].Jumps;
            for (float t = 0; t < 29f; t += .5f) thin.Tick(.5f, i => i == 0 ? .4f : 1f);
            Check(thin.ByGround[0].Jumps == jumps0, "no jump inside the 30 s gap");
            for (float t = 0; t < 3f; t += .5f) thin.Tick(.5f, i => i == 0 ? .4f : 1f);
            Check(thin.ByGround[0].Jumps == jumps0 + 1 && thin.ByGround[1].Jumps == 0, "school jumps when its ground drops below 0.5");
        }


        static void SaveRoundTrip()
        {
            var st = new GameState(3);
            for (int i = 0; i < st.GroundRich.Length; i++) st.GroundRich[i] = Mathf.Lerp(.3f, 1f, (i % 7) / 6f);
            string path = System.IO.Path.Combine(Application.temporaryCachePath, "m4-check-save.json");
            try
            {
                st.Save(path);
                var json = System.IO.File.ReadAllText(path);
                var v2 = SaveV2.FromJson(json);
                Check(v2 != null && v2.GroundRichness.Count == st.GroundRich.Length, "richness stored in the Save v2 payload");
                var back = GameState.Load(path);
                Check(back != null && back.GroundRich.Length == st.GroundRich.Length, "save loads");
                for (int i = 0; i < st.GroundRich.Length; i++) Check(Near(back.GroundRich[i], st.GroundRich[i], .0001f), "richness survives save/load at slot " + i);
            }
            finally { if (System.IO.File.Exists(path)) System.IO.File.Delete(path); }
        }

        static void LiveVoyage()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("M4 check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            g.SetSail();
            Until(g, () => g.CurrentMode == VoyageGame.Mode.Fishing && g.ActiveGroundId != null, "anchors at a ground");
            g.Tick(.1f);
            int spot = g.ActiveSpot;
            Check(g.Navigation.Grounds[0].Id == g.ActiveGroundId && g.State.CurrentGround == 0, "anchored ground drives the roll tables");
            Check(g.GroundSchools != null && g.Cues != null, "schools and cues exist at sea");
            // Cues follow the bands.
            for (int i = 0; i < 3; i++)
            {
                Check(g.Cues.RingBand(i) == RichnessBand.Rich && g.Cues.GullsShown(i) >= 3 && g.Cues.GullsShown(i) <= 6, "rich ground " + i + " shows 3-6 gulls");
                Check(g.Cues.RingColour(i) == Grounds.RingTint(1f), "rich ring is warm");
            }
            foreach (var e in Grounds.Get(spot, 1).Day) Grounds.Drain(g.State.GroundRich, spot, 1, e.species, .35f);
            foreach (var e in Grounds.Get(spot, 2).Day) Grounds.Drain(g.State.GroundRich, spot, 2, e.species, .6f);
            g.Tick(.1f);
            Check(g.Cues.RingBand(1) == RichnessBand.Thinning && g.Cues.GullsShown(1) is >= 1 and <= 2 && g.Cues.RingColour(1) == Grounds.RingTint(.65f), "thinning ground: 1-2 gulls, neutral ring");
            Check(g.Cues.RingBand(2) == RichnessBand.Poor && g.Cues.GullsShown(2) == 0 && g.Cues.RingColour(2) == Grounds.RingTint(.4f), "poor ground: no gulls, grey ring");
            Check(g.Cues.RingBand(0) == RichnessBand.Rich && g.Cues.GullsShown(0) >= 3, "rich ground keeps its gulls");
            // A landed rod catch drains that species at the anchored ground.
            var species = Grounds.Get(spot, 0).Day[0].species;
            float before = Grounds.Richness(g.State.GroundRich, spot, 0, species);
            g.LandFish(g.Rods[0], species, GameData.Get(species).MaxKg * .9f);
            Check(Near(before - Grounds.Richness(g.State.GroundRich, spot, 0, species), .02f), "live catch drains the anchored ground by 0.02");
            // School bonus follows the boat.
            var school = g.GroundSchools.ByGround[0];
            g.Sailor.Push(school.Position); g.Tick(.05f);
            Check(g.AtFishingGround && Near(g.State.SchoolBonus, 1.3f, .001f), "boat inside the school gets 1.3");
            // Rods do nothing outside a zone, and the roll ignores grounds there.
            var open = Enumerable.Range(0, 400).Select(i => g.Navigation.CameraBounds.center + new Vector2((i % 20 - 10) * 8f, (i / 20 - 10) * 8f))
                .First(p => g.Navigation.InsideBorder(p) && !g.Navigation.Blocked(p) && !g.Navigation.InShallows(p) && !g.Navigation.Grounds.Any(z => (z.Centre - p).magnitude < z.Radius + 3f));
            g.Sailor.Push(open); g.Tick(.05f);
            Check(!g.AtFishingGround && g.State.CurrentGround == -1 && g.State.SchoolBonus == 1f, $"outside a zone: no ground, no bonus (at {g.AtFishingGround}, ground {g.State.CurrentGround}, bonus {g.State.SchoolBonus}, pos {g.Sailor.Position}, mode {g.CurrentMode})");
            var states = g.Rods.Select(r => r.State).ToArray();
            for (float t = 0; t < 20f; t += .05f) g.Tick(.05f);
            Check(g.Rods.Select(r => r.State).SequenceEqual(states), "no fishing outside a zone");
            // Relocate to a richer ground when the navigator would suggest it.
            Check(g.Relocate(g.Navigation.Grounds[1].Id), "relocate command works");
            Until(g, () => g.CurrentMode == VoyageGame.Mode.Fishing && g.ActiveGroundId == g.Navigation.Grounds[1].Id, "arrives at the second ground");
            g.Tick(.1f);
            Check(g.State.CurrentGround == 1, "anchoring switches the roll table to the new ground");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }

        static void BotComparison()
        {
            int spot = 1; // Kelp bank
            float Simulate(bool moves, out int hops)
            {
                var st = new GameState(4242); hops = 0; float value = 0; int ground = 0;
                for (int voyage = 0; voyage < 20; voyage++)
                {
                    float t = 0;
                    while (true)
                    {
                        st.CurrentGround = ground; st.SchoolBonus = 1.15f;
                        t += (st.RollBiteWait(spot, .55f) + 3.5f) / 3f; // three rods working the ground
                        if (t > 480f) break;
                        var (species, kg) = st.RollFish(spot, .55f);
                        value += CatchExpectation.NominalValue(species, kg);
                        st.OnCatch(spot, kg, species, false);
                        if (!moves) continue;
                        var report = Grounds.Report(st.GroundRich, spot, ground);
                        if (report.ShouldMove) { ground = Grounds.IndexOf(spot, report.BetterGroundId); t += 15f; hops++; }
                    }
                    st.EndVoyage(new SaleReport());
                }
                return value;
            }
            float mover = Simulate(true, out int hops), stayer = Simulate(false, out _);
            Debug.Log($"[Catchline] M4 bot at Kelp bank over 20 voyages: relocating {mover:0} coins ({hops} moves) vs never moving {stayer:0}");
            Check(hops > 0 && mover > stayer, $"relocating bot earns more than the stayer ({mover:0} vs {stayer:0})");
        }
    }
}

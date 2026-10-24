using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Sea;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class MapNavChecks
    {
        public static string Report { get; private set; }
        static void Check(bool ok, string what) { if (!ok) throw new Exception("[Catchline] MapNav check failed: " + what); }
        public static void Run()
        {
            Report = "";
            ArtImport.BuildLibrary();
            Fixtures();
            int maps = 0, routes = 0;
            foreach (var map in SeaNav.Maps)
            {
                bool found = false;
                foreach (var hull in GameData.Hulls)
                {
                    var nav = SeaNav.Load(map, hull);
                    if (nav == null) continue;
                    found = true;
                    var destinations = nav.Grounds.Select(g => g.Centre).Prepend(nav.Harbour).ToArray();
                    float min = float.PositiveInfinity, max = 0;
                    for (int i = 0; i < destinations.Length; i++)
                        for (int j = 0; j < destinations.Length; j++)
                        {
                            if (i == j) continue;
                            var a = destinations[i]; var b = destinations[j];
                            var route = nav.Plan(a, b);
                            string label = map + "/" + hull.Model + " " + i + "->" + j;
                            Check(route != null, label + " route exists");
                            foreach (var p in route) Check(!nav.Blocked(p) && nav.InsideBorder(p), label + " clear point");
                            for (int k = 1; k < route.Count; k++) Check(nav.Visible(route[k - 1], route[k]), label + " clear segment");
                            if (nav.Visible(a, b)) Check(SeaNav.Length(route) <= Vector2.Distance(a, b) * 1.6f, label + " detour within1.6x");
                            var sailor = new BoatSailor(nav, hull, a);
                            Check(sailor.SailTo(b), label + " sailor starts");
                            float elapsed = 0;
                            while (!sailor.Arrived && elapsed < 120)
                            {
                                sailor.Tick(.05f); elapsed += .05f;
                                Check(!nav.Blocked(sailor.Position) && nav.InsideBorder(sailor.Position), label + " collision-free sailing");
                            }
                            Check(sailor.Arrived && Vector2.Distance(sailor.Position, b) < .4f, label + " sailor arrives at " + sailor.Position + " next route=" + string.Join(";", route));
                            if (i == 0 && j == 1) Check(elapsed >= 10 && elapsed <= 20, label + " representative harbour trip 10-20 seconds: " + elapsed);
                            min = Mathf.Min(min, elapsed); max = Mathf.Max(max, elapsed); routes++;
                        }
                    var snapped = nav.Snap(new Vector2(10000, 10000));
                    Check(nav.InsideBorder(snapped) && nav.Snap(snapped) == snapped, map + " outside target snaps stably inside");
                    foreach (var island in nav.Islands)
                    {
                        var sailor = new BoatSailor(nav, hull, nav.Harbour);
                        sailor.Push(island.Aggregate(Vector2.zero, (s, p) => s + p) / island.Length);
                        Check(!nav.Blocked(sailor.Position) && nav.InsideBorder(sailor.Position), map + " pushed boat resolved out of island");
                    }
                    string result = $"[Catchline] MAPNAV {map}/{hull.Model}: {min:0.00}-{max:0.00}s, {(nav.Interim ? "INTERIM" : "REAL")}";
                    Report += result + "\n"; Debug.Log(result);
                }
                if (found) maps++;
                else Debug.LogWarning("[Catchline] MAPNAV DATA PENDING: " + map);
            }
            Check(maps >= 2, "at least Harbour mouth and Kelp bank data loaded");
            Debug.Log($"[Catchline] MAP NAV CHECKS PASSED: {maps}/5 available maps, {routes} directed hull routes; missing maps await art. Native captures/feel not tested.");
        }
        public static void Gameplay()
        {
            ArtImport.BuildLibrary();
            UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.EmptyScene, UnityEditor.SceneManagement.NewSceneMode.Single);
            var g = new GameObject("Map navigation gameplay check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build(); g.SetSail();
            Check(g.Navigation != null && g.CurrentMode == VoyageGame.Mode.SailingOut && g.UsesDeckGraph, "departure builds real route and live deck");
            void Arrive(VoyageGame.Mode mode)
            {
                for (float t = 0; t < 120 && g.CurrentMode != mode; t += .05f) g.Tick(.05f);
                Check(g.CurrentMode == mode, "physical arrival " + mode);
            }
            Arrive(VoyageGame.Mode.Fishing);
            Check(g.AtFishingGround && g.Navigation.Grounds.First().Contains(g.Sailor.Position), "arrival inside ground zone");
            Check(g.Relocate(g.Navigation.Grounds[1].Id), "relocate command starts route");
            Check(!g.CanCommandRod(g.Rods[0]), "no gear deployed during sailing");
            Arrive(VoyageGame.Mode.Fishing);
            Check(g.ActiveGroundId == g.Navigation.Grounds[1].Id && g.AtFishingGround, "relocation reaches requested ground");
            Check(g.SailTo(new Vector2(10000, 10000)), "outside water tap accepted as snapped route");
            Check(g.Navigation.InsideBorder(g.Sailor.Route.Last()), "outside destination inside border");
            Arrive(VoyageGame.Mode.Fishing);
            Check(!g.AtFishingGround && !g.CanCommandRod(g.Rods[0]), "open water cannot fish");
            g.HeadHome(); Arrive(VoyageGame.Mode.Harbour);
            Check(g.Navigation == null && !g.UsesDeckGraph, "harbour arrival clears voyage graph");
            Debug.Log("[Catchline] MAP NAV GAMEPLAY CHECKS PASSED (session-only; no native visual acceptance)");
        }
        static void Fixtures()
        {
            const string json = "{\"map\":\"fixture\",\"border\":[[-50,-50],[50,-50],[50,50],[-50,50]],\"islands\":[[[-2,-5],[2,-5],[2,5],[-2,5]]],\"shallows\":[[[-5,-8],[5,-8],[5,8],[-5,8]]],\"harbour\":[-20,0],\"grounds\":[]}";
            var nav = SeaNav.Parse(json, 2);
            Check(!nav.Visible(new(-20, 0), new(20, 0)), "island blocks direct segment");
            Check(nav.Plan(new(-20, 0), new(20, 0))?.Count > 2, "A* goes round inflated island");
            Check(nav.Plan(new(-20, 0), Vector2.zero) == null, "land target refused");
            Check(Mathf.Abs(nav.Cost(new(-20, 20), new(20, 20)) - 40) < .01f, "open-water cost");
            Check(nav.Cost(new(-4.5f, -7), new(-4.5f, 7)) > 27.9f, "shallows cost twice");
            Check(!nav.Blocked(nav.Resolve(Vector2.zero)), "centre push recovery");
            var p = nav.Slide(new(-20, 0), new(20, 0));
            Check(!nav.Blocked(p) && p.x < -3.9f, "swept collision prevents tunnelling");
            var h = GameData.Hulls[0];
            var sailor = new BoatSailor(nav, h, new(-20, 0), Mathf.PI);
            sailor.SailTo(new(-20, 20));
            float before = sailor.Heading; sailor.Tick(.05f);
            Check(Mathf.Abs(Mathf.DeltaAngle(before * Mathf.Rad2Deg, sailor.Heading * Mathf.Rad2Deg)) <= h.TurnDegreesPerSecond * .05f + .001f, "turn rate limit");
        }
    }
}

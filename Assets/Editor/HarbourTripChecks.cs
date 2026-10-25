using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Sea;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // The harbour and the three-leg trip (docs/plans/HARBOUR-PLAN.md): every hull leaves its berth and comes back to
    // it through the harbour lane, the chart and the sea lane, never touching a moored boat, and every sea map's
    // lanes keep their clearance. Batch: -executeMethod Catchline.EditorTools.HarbourTripChecks.Run
    public static class HarbourTripChecks
    {
        static void Check(bool ok, string what) { if (!ok) throw new Exception("[Catchline] Harbour trip check failed: " + what); }

        public static string Run()
        {
            ArtImport.BuildLibrary();
            var report = new List<string>();
            report.Add(Lanes());
            foreach (int hull in new[] { 0, 1, 2, 3, 4 }) report.Add(Trip(hull, hull == 4 ? 3 : 0));
            string text = "HARBOURTRIP PASS · " + string.Join(" · ", report);
            Debug.Log(text);
            return text;
        }

        // Rule 2/3: a lane of at least 4.5 m from the home-facing entry to every ground, proven for the biggest hull.
        static string Lanes()
        {
            int lanes = 0;
            for (int spot = 0; spot < SeaNav.Maps.Length; spot++)
            {
                var proof = SeaNav.Load(SeaNav.Maps[spot], 2.25f);
                Check(proof != null, SeaNav.Maps[spot] + " navigation");
                var wide = SeaLanes.Clearances.Select(r => SeaNav.Load(SeaNav.Maps[spot], r)).ToList();
                var home = SeaLanes.HomeDirection(VoyageGame.NauticalChartPoint(spot), VoyageGame.ChartHarbour);
                var entry = SeaLanes.Entry(proof, home, out _);
                Check(Vector2.Dot((entry - proof.CameraBounds.center).normalized, home) > .5f, SeaNav.Maps[spot] + " entry faces home");
                foreach (var g in proof.Grounds)
                {
                    var lane = SeaLanes.Lane(proof, wide, entry, g.Centre, out float clear);
                    Check(lane != null && SeaLanes.Proven(proof, lane) && clear >= 4.5f, $"{SeaNav.Maps[spot]} lane to {g.Id} ({clear:0.0} m)");
                    lanes++;
                }
            }
            return $"{lanes} sea lanes clear";
        }

        static string Trip(int hull, int spot)
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Harbour trip check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            g.State.Hull = hull; g.State.Coins = 10000; g.State.Fuel = g.State.FuelCapacity;
            typeof(VoyageGame).GetMethod("RebuildBoat", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic).Invoke(g, new object[] { false });
            g.Tick(.05f); // the harbour rebuilds for the new berth
            for (int i = 0; i < 5; i++) if (!g.State.Known(spot)) g.State.BuyChart(spot);
            g.SelectedSpot = spot;
            var boatBounds = BoatFootprint(g);
            Check((new Vector2(boatBounds.center.x, boatBounds.center.z) - g.HarbourSlot).magnitude < .6f, $"hull {hull} sits at its berth");
            var moored = Moored(g);
            var legs = new List<VoyageGame.TripLeg>();
            float outSeconds = 0, homeSeconds = 0, clock = 0;
            void Watch(float seconds, Func<bool> done, string what)
            {
                for (float t = 0; t < seconds && !done(); t += .05f)
                {
                    g.Tick(.05f); clock += .05f;
                    if (legs.Count == 0 || legs[legs.Count - 1] != g.Leg) legs.Add(g.Leg);
                    if (g.HarbourLaneActive)
                    {
                        moored ??= Moored(g);
                        var b = BoatFootprint(g);
                        foreach (var m in moored)
                            Check(!Overlap(g, m), $"hull {hull} clear of the moored boat at {m.center:F1} size {m.size:F1}, boat {b.center:F1} size {b.size:F1} ({g.Leg})");
                    }
                }
                Check(done(), $"hull {hull}: {what}");
            }
            g.SetSail();
            Check(g.Leg == VoyageGame.TripLeg.HarbourOut, $"hull {hull} leaves through the harbour lane");
            Watch(240, () => g.CurrentMode == VoyageGame.Mode.Fishing && g.Leg == VoyageGame.TripLeg.None, "arrives at the ground");
            outSeconds = clock; clock = 0;
            g.HeadHome();
            moored = null;
            Watch(240, () => g.CurrentMode == VoyageGame.Mode.Harbour, "comes home");
            homeSeconds = clock;
            moored = Moored(g);
            boatBounds = BoatFootprint(g);
            Check((new Vector2(boatBounds.center.x, boatBounds.center.z) - g.HarbourSlot).magnitude < .6f, $"hull {hull} docks at its berth: boat {boatBounds.center:F2} slot {g.HarbourSlot:F2} leg {g.Leg} mode {g.CurrentMode}");
            string order = string.Join(">", legs.Distinct().Select(l => l.ToString()));
            foreach (var need in new[] { "HarbourOut", "ChartOut", "SeaOut", "SeaHome", "ChartHome", "HarbourIn" })
                Check(order.Contains(need), $"hull {hull} trip has {need}: {order}");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            return $"hull {hull} {GameData.Hulls[hull].Name} ok (out {outSeconds:0}s, home {homeSeconds:0}s)";
        }

        static List<Bounds> Moored(VoyageGame g)
        {
            var list = new List<Bounds>();
            foreach (var f in UnityEngine.Object.FindObjectsByType<Floater>(FindObjectsSortMode.None))
            {
                var r = f.GetComponentsInChildren<Renderer>();
                if (r.Length == 0 || f.transform.IsChildOf(g.Boat)) continue;
                var b = r[0].bounds; foreach (var x in r) b.Encapsulate(x.bounds);
                if (b.size.x > 1.5f && b.size.z > 1.5f) list.Add(b);
            }
            return list;
        }

        static Bounds BoatFootprint(VoyageGame g)
        {
            var def = g.State.HullDef;
            var c = g.Boat.TransformPoint(def.Center);
            float len = def.Width * def.CellSize, beam = def.Height * def.CellSize;
            var along = g.Boat.TransformDirection(Vector3.right);
            float ex = Mathf.Abs(along.x) * len / 2 + Mathf.Abs(along.z) * beam / 2, ez = Mathf.Abs(along.z) * len / 2 + Mathf.Abs(along.x) * beam / 2;
            return new Bounds(c, new Vector3(ex * 2, 1, ez * 2));
        }

        // The hull's turned rectangle against a moored boat's box (separating axes), with a hand's width of slack
        // for fenders and oars on the moored models.
        static bool Overlap(VoyageGame g, Bounds m)
        {
            var def = g.State.HullDef;
            var c = g.Boat.TransformPoint(def.Center);
            var ax = g.Boat.TransformDirection(Vector3.right); var a = new Vector2(ax.x, ax.z).normalized; var n = new Vector2(-a.y, a.x);
            float hl = def.Width * def.CellSize / 2, hb = def.Height * def.CellSize / 2, slack = .25f;
            var centre = new Vector2(c.x, c.z); var mc = new Vector2(m.center.x, m.center.z); var me = new Vector2(m.extents.x, m.extents.z);
            foreach (var axis in new[] { Vector2.right, Vector2.up, a, n })
            {
                float rBoat = hl * Mathf.Abs(Vector2.Dot(a, axis)) + hb * Mathf.Abs(Vector2.Dot(n, axis));
                float rBox = me.x * Mathf.Abs(axis.x) + me.y * Mathf.Abs(axis.y);
                if (Mathf.Abs(Vector2.Dot(centre - mc, axis)) > rBoat + rBox - slack) return false;
            }
            return true;
        }

        [MenuItem("Catchline/Checks/Harbour trip")]
        static void Menu() => Debug.Log(Run());
    }
}

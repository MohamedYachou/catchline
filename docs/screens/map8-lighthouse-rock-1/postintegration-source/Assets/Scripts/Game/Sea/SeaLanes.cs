using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game.Sea
{
    // Sea lanes (docs/plans/HARBOUR-PLAN.md section 3). The boat enters each sea map from the edge that faces Gull
    // Harbour on the chart, and sails to a ground along a lane planned with a wide clearance, then smoothed.
    // Every smoothed piece is re-proven against the real hull clearance, so a lane never crosses land.
    public static class SeaLanes
    {
        // Twice the biggest hull's navigation radius plus 2 m, then narrower fallbacks for tight maps.
        public static readonly float[] Clearances = { 6.5f, 4.5f, 3f };
        const float ScreenYaw = 35f * Mathf.Deg2Rad;

        // Direction (x, z on the sea map) from the map toward Gull Harbour, from the chart illustration, turned into
        // the sea camera's screen frame (yaw 35: screen right = (cos, -sin), screen up = (sin, cos)).
        public static Vector2 HomeDirection(Vector2 chartSpot, Vector2 chartHarbour)
        {
            var d = chartHarbour - chartSpot; // chart y grows downward
            var right = new Vector2(Mathf.Cos(ScreenYaw), -Mathf.Sin(ScreenYaw));
            var up = new Vector2(Mathf.Sin(ScreenYaw), Mathf.Cos(ScreenYaw));
            var w = right * d.x - up * d.y;
            return w.sqrMagnitude < 1e-6f ? -up : w.normalized;
        }

        // Entry point on the home-facing edge: the ray from the map centre toward home meets the border, pulled in by
        // the lane clearance. The bearing is swung up to 60 degrees each way if the edge there is land.
        public static Vector2 Entry(SeaNav nav, Vector2 home, out float inboundHeading)
        {
            var bounds = nav.CameraBounds;
            var centre = bounds.center;
            foreach (float swing in new[] { 0f, 10f, -10f, 20f, -20f, 30f, -30f, 45f, -45f, 60f, -60f })
            {
                var dir = Rotate(home, swing);
                float far = Mathf.Max(bounds.width, bounds.height) * 2;
                float lo = 0, hi = far;
                for (int i = 0; i < 24; i++) { float mid = (lo + hi) / 2; if (nav.InsideBorder(centre + dir * mid)) lo = mid; else hi = mid; }
                foreach (float inset in new[] { Clearances[0] + 2f, Clearances[1] + 2f, nav.Radius + 2f })
                {
                    var p = nav.Snap(centre + dir * Mathf.Max(0, lo - inset));
                    if (nav.Blocked(p) || nav.InShallows(p)) continue;
                    var inward = (centre - p).normalized;
                    inboundHeading = Mathf.Atan2(inward.y, inward.x);
                    return p;
                }
            }
            var fallback = nav.Harbour;
            var toward = (centre - fallback).normalized;
            inboundHeading = Mathf.Atan2(toward.y, toward.x);
            return fallback;
        }

        // A lane from a to b: the widest clearance that still finds a way, smoothed, every sample proven clear.
        public static List<Vector2> Lane(SeaNav nav, IReadOnlyList<SeaNav> wide, Vector2 a, Vector2 b, out float clearance)
        {
            for (int i = 0; i < wide.Count; i++)
            {
                if (wide[i] == null) continue;
                var raw = wide[i].Plan(a, b);
                if (raw == null) continue;
                raw[0] = a; raw[raw.Count - 1] = b;
                if (!Proven(nav, raw)) continue;
                clearance = wide[i].Radius;
                var smooth = Smooth(raw, 3);
                return Proven(nav, smooth) ? smooth : raw;
            }
            clearance = nav.Radius;
            return nav.Plan(a, b);
        }

        public static bool Proven(SeaNav nav, IReadOnlyList<Vector2> route)
        {
            for (int i = 1; i < route.Count; i++) if (!nav.Visible(route[i - 1], route[i])) return false;
            return true;
        }

        // Chaikin corner cutting with the end points kept: long legs keep their line, corners become arcs.
        public static List<Vector2> Smooth(IReadOnlyList<Vector2> route, int passes)
        {
            var p = new List<Vector2>(route);
            for (int pass = 0; pass < passes && p.Count > 2; pass++)
            {
                var q = new List<Vector2> { p[0] };
                for (int i = 0; i < p.Count - 1; i++)
                {
                    var a = p[i]; var b = p[i + 1];
                    if (i > 0) q.Add(Vector2.Lerp(a, b, .25f));
                    if (i < p.Count - 2) q.Add(Vector2.Lerp(a, b, .75f));
                }
                q.Add(p[p.Count - 1]);
                p = q;
            }
            return p;
        }

        static Vector2 Rotate(Vector2 v, float degrees)
        {
            float r = degrees * Mathf.Deg2Rad, c = Mathf.Cos(r), s = Mathf.Sin(r);
            return new Vector2(v.x * c - v.y * s, v.x * s + v.y * c);
        }
    }
}

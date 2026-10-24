using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game.Deck;
using UnityEngine;

namespace Catchline.Game.Sea
{
    // Configuration-space navigation. World X/Z metres; all collision is data, never physics.
    public sealed class SeaNav
    {
        public sealed class Ground
        {
            public string Id, Name, PoolId;
            public Vector2 Centre;
            public float Radius, Depth;
            public bool Contains(Vector2 p) => (p - Centre).sqrMagnitude <= Radius * Radius;
        }
        public static readonly string[] Maps = { "GullHarbourMouth", "GullKelpBank", "GullSandbar", "GullRockyPoint", "GullDeepChannel" };
        public string Map { get; private set; }
        public string ModelId { get; private set; }
        public bool Interim { get; private set; }
        public Vector2 Harbour { get; private set; }
        public Rect CameraBounds { get; private set; }
        public readonly List<Ground> Grounds = new();
        public readonly List<Vector2[]> Islands = new(), Shallows = new();
        public Vector2[] Border { get; private set; }
        public readonly float Radius;
        readonly List<Vector2[]> land = new();
        readonly List<Vector2> vertices = new();
        List<(int to, float cost)>[] edges;
        const float Epsilon = .005f;

        public static SeaNav Load(string map, HullDef hull)
        {
            // Parse the map id inside each asset: every map's asset has the same file name.
            var files = ArtLibrary.Get()?.NavigationFiles;
            if (files == null) return null;
            foreach (bool interim in new[] { false, true })
                foreach (var file in files.Where(f => f != null && f.name.EndsWith(interim ? "navigation.interim" : "navigation", StringComparison.Ordinal)))
                {
                    var root = (Dictionary<string, object>)MiniJson.Parse(file.text);
                    if (Text(root, "map") == map) return new SeaNav(root, hull.NavigationRadius, interim);
                }
            return null;
        }
        public static SeaNav Parse(string json, float radius) => new((Dictionary<string, object>)MiniJson.Parse(json), radius, false);
        SeaNav(Dictionary<string, object> root, float radius, bool interim)
        {
            Radius = Mathf.Max(0, radius); Interim = interim;
            Map = Text(root, "map"); ModelId = Text(root, "runtimeModelId") ?? Map + "SeaV2";
            Border = Polygon(root["border"]);
            if (Border.Length < 3) throw new FormatException("Navigation border needs three vertices: " + Map);
            Harbour = Point(root["harbour"]);
            foreach (var p in Polygons(root, "islands"))
            {
                land.Add(p); Islands.Add(Inflate(p, Radius + .02f));
            }
            foreach (var p in Polygons(root, "shallows")) Shallows.Add(Inflate(p, Radius));
            foreach (Dictionary<string, object> g in (List<object>)root["grounds"])
                Grounds.Add(new Ground { Id = Text(g, "id"), Name = Text(g, "name"), PoolId = Text(g, "poolId"),
                    Centre = Point(g.TryGetValue("centre", out var c) ? c : g.TryGetValue("center", out c) ? c : g["position"]),
                    Radius = Number(g, "radius", 12), Depth = Number(g, "nominalDepth", Number(g, "seabedDepth", 3)) });
            var min = new Vector2(Border.Min(p => p.x), Border.Min(p => p.y));
            var max = new Vector2(Border.Max(p => p.x), Border.Max(p => p.y));
            CameraBounds = Rect.MinMaxRect(min.x, min.y, max.x, max.y);
            if (root.TryGetValue("cameraBounds", out var bounds) && bounds is Dictionary<string, object> b)
            {
                if (b.ContainsKey("min") && b.ContainsKey("max")) { min = Point(b["min"]); max = Point(b["max"]); }
                else { min = new Vector2(Number(b, "minX", Number(b, "xMin", min.x)), Number(b, "minZ", Number(b, "zMin", min.y))); max = new Vector2(Number(b, "maxX", Number(b, "xMax", max.x)), Number(b, "maxZ", Number(b, "zMax", max.y))); }
                CameraBounds = Rect.MinMaxRect(min.x, min.y, max.x, max.y);
            }
            BuildGraph();
        }

        // Round convex joins circumscribe the hull disc. Concave joins intersect the offset edges.
        // Collision below also tests the original shoreline distance, so a difficult concave offset
        // can never admit a path through land, even when its candidate outline folds over itself.
        public static Vector2[] Inflate(Vector2[] polygon, float radius)
        {
            var p = polygon.ToArray();
            if (Area(p) < 0) Array.Reverse(p);
            var result = new List<Vector2>();
            for (int i = 0; i < p.Length; i++)
            {
                var a = (p[i] - p[(i + p.Length - 1) % p.Length]).normalized;
                var b = (p[(i + 1) % p.Length] - p[i]).normalized;
                var na = new Vector2(a.y, -a.x); var nb = new Vector2(b.y, -b.x);
                float angle = Mathf.Atan2(Cross(na, nb), Vector2.Dot(na, nb));
                if (angle > .001f)
                {
                    int steps = Mathf.CeilToInt(angle / (Mathf.PI / 8));
                    float r = radius / Mathf.Cos(angle / steps / 2);
                    for (int s = 0; s <= steps; s++)
                    {
                        float t = Mathf.Atan2(na.y, na.x) + angle * s / steps;
                        result.Add(p[i] + new Vector2(Mathf.Cos(t), Mathf.Sin(t)) * r);
                    }
                }
                else
                {
                    var bisector = na + nb;
                    result.Add(p[i] + bisector * (radius / Mathf.Max(.01f, 1 + Vector2.Dot(na, nb))));
                }
            }
            return result.ToArray();
        }
        void BuildGraph()
        {
            foreach (var poly in Islands.Concat(Shallows))
                foreach (var v in poly) if (InsideBorder(v) && !Blocked(v)) vertices.Add(v);
            // Concave border vertices are necessary for visibility around border indentations.
            foreach (var v in Border) { var q = Snap(v); if (!Blocked(q)) vertices.Add(q); }
            edges = new List<(int, float)>[vertices.Count];
            for (int i = 0; i < edges.Length; i++) edges[i] = new();
            for (int i = 0; i < vertices.Count; i++)
                for (int j = 0; j < i; j++)
                    if (Visible(vertices[i], vertices[j]))
                    {
                        float cost = Cost(vertices[i], vertices[j]);
                        edges[i].Add((j, cost)); edges[j].Add((i, cost));
                    }
        }
        public bool InsideBorder(Vector2 p) => Contains(Border, p, true);
        public float BorderDistance(Vector2 p) => DistanceToEdges(Border, p);
        public bool Blocked(Vector2 p) => land.Any(poly => Contains(poly, p, true) || DistanceToEdges(poly, p) < Radius + .009f);
        public bool InShallows(Vector2 p) => Shallows.Any(poly => Contains(poly, p, true));
        public Vector2 Snap(Vector2 p)
        {
            // Keep the entire hull inside the buoys, including at concave corners.
            for (int pass = 0; pass < 12; pass++)
            {
                bool inside = Contains(Border, p, true);
                var q = Nearest(Border, p, out int edge);
                if (inside && (q - p).magnitude >= Radius + .02f) return p;
                var d = Border[(edge + 1) % Border.Length] - Border[edge];
                var inward = new Vector2(-d.y, d.x).normalized * Mathf.Sign(Area(Border));
                p = q + inward * (Radius + .03f);
            }
            return p;
        }
        public Vector2 Resolve(Vector2 p)
        {
            p = Snap(p);
            for (int pass = 0; pass < 16 && Blocked(p); pass++)
                foreach (var poly in land)
                {
                    var q = Nearest(poly, p, out int edge);
                    bool inside = Contains(poly, p, true);
                    if (!inside && (p - q).magnitude >= Radius + .02f) continue;
                    var d = poly[(edge + 1) % poly.Length] - poly[edge];
                    var outward = new Vector2(d.y, -d.x).normalized * Mathf.Sign(Area(poly));
                    p = q + (inside || (p - q).sqrMagnitude < .000001f ? outward : (p - q).normalized) * (Radius + .04f);
                }
            return Snap(p);
        }
        public bool Visible(Vector2 a, Vector2 b)
        {
            if (Blocked(a) || Blocked(b) || !InsideBorder(a) || !InsideBorder(b)) return false;
            for (int i = 0; i < Border.Length; i++)
                if (SegmentDistance(a, b, Border[i], Border[(i + 1) % Border.Length]) < Radius + .008f) return false;
            var cuts = Cuts(Border, a, b); cuts.Add(0); cuts.Add(1); cuts.Sort();
            for (int i = 1; i < cuts.Count; i++)
                if (!InsideBorder(Vector2.Lerp(a, b, (cuts[i - 1] + cuts[i]) * .5f))) return false;
            foreach (var poly in land)
                for (int i = 0; i < poly.Length; i++)
                    if (SegmentDistance(a, b, poly[i], poly[(i + 1) % poly.Length]) < Radius + .008f) return false;
            return true;
        }
        // Integrate exactly over shallow polygon crossings; overlapping rings cost twice, never four times.
        public float Cost(Vector2 a, Vector2 b)
        {
            var cuts = new List<float> { 0, 1 };
            foreach (var p in Shallows) cuts.AddRange(Cuts(p, a, b));
            cuts.Sort(); float cost = 0;
            for (int i = 1; i < cuts.Count; i++)
                cost += (cuts[i] - cuts[i - 1]) * (InShallows(Vector2.Lerp(a, b, (cuts[i] + cuts[i - 1]) * .5f)) ? 2 : 1);
            return cost * Vector2.Distance(a, b);
        }
        public List<Vector2> Plan(Vector2 from, Vector2 to)
        {
            from = Resolve(from); to = Snap(to);
            if (Blocked(to)) return null;
            if (Vector2.Distance(from, to) < Epsilon) return new() { from, to };
            int n = vertices.Count, end = n + 1;
            var nodes = vertices.Concat(new[] { from, to }).ToArray();
            var g = Enumerable.Repeat(float.PositiveInfinity, n + 2).ToArray();
            var previous = Enumerable.Repeat(-1, n + 2).ToArray();
            var closed = new bool[n + 2]; g[n] = 0;
            while (true)
            {
                int at = -1; float best = float.PositiveInfinity;
                for (int i = 0; i < nodes.Length; i++)
                    if (!closed[i] && g[i] + Vector2.Distance(nodes[i], to) < best) { at = i; best = g[i] + Vector2.Distance(nodes[i], to); }
                if (at < 0) return null;
                if (at == end)
                {
                    var path = new List<Vector2>();
                    for (int i = end; i >= 0; i = previous[i]) path.Add(nodes[i]);
                    path.Reverse(); return path;
                }
                closed[at] = true;
                // Cached static visibility plus dynamic source/target edges.
                var neighbours = at < n ? new List<(int to, float cost)>(edges[at]) : new();
                if (at == n)
                    for (int i = 0; i < n; i++) if (Visible(from, nodes[i])) neighbours.Add((i, Cost(from, nodes[i])));
                if (Visible(nodes[at], to)) neighbours.Add((end, Cost(nodes[at], to)));
                foreach (var edge in neighbours)
                    if (!closed[edge.to] && g[at] + edge.cost < g[edge.to]) { g[edge.to] = g[at] + edge.cost; previous[edge.to] = at; }
            }
        }
        public static float Length(IReadOnlyList<Vector2> route)
        {
            float length = 0;
            for (int i = 1; i < route.Count; i++) length += Vector2.Distance(route[i - 1], route[i]);
            return length;
        }
        public Vector2 Slide(Vector2 from, Vector2 to)
        {
            from = Resolve(from); to = Snap(to);
            if (Visible(from, to)) return to;
            // Sweep first (prevents tunnelling); project remaining displacement onto the contact edge.
            float lo = 0, hi = 1;
            for (int i = 0; i < 16; i++) { float mid = (lo + hi) / 2; if (Visible(from, Vector2.Lerp(from, to, mid))) lo = mid; else hi = mid; }
            var hit = Vector2.Lerp(from, to, Mathf.Max(0, lo - .001f));
            Vector2 tangent = Vector2.zero; float nearest = float.PositiveInfinity;
            foreach (var p in land)
            {
                var q = Nearest(p, hit, out int edge); float d = (q - hit).sqrMagnitude;
                if (d < nearest) { nearest = d; tangent = (p[(edge + 1) % p.Length] - p[edge]).normalized; }
            }
            var slide = Snap(hit + tangent * Vector2.Dot(to - hit, tangent));
            return Visible(hit, slide) ? slide : Resolve(hit);
        }

        static float Cross(Vector2 a, Vector2 b) => a.x * b.y - a.y * b.x;
        static float Area(Vector2[] p) { float a = 0; for (int i = 0; i < p.Length; i++) a += Cross(p[i], p[(i + 1) % p.Length]); return a * .5f; }
        public static bool Contains(Vector2[] poly, Vector2 p, bool boundary = false)
        {
            bool inside = false;
            for (int i = 0, j = poly.Length - 1; i < poly.Length; j = i++)
            {
                var a = poly[j]; var b = poly[i];
                if ((p - Closest(a, b, p)).sqrMagnitude < .000001f) return boundary;
                if ((a.y > p.y) != (b.y > p.y) && p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y) + a.x) inside = !inside;
            }
            return inside;
        }
        static Vector2 Closest(Vector2 a, Vector2 b, Vector2 p) => a + (b - a) * Mathf.Clamp01(Vector2.Dot(p - a, b - a) / Mathf.Max(.0000001f, (b - a).sqrMagnitude));
        static Vector2 Nearest(Vector2[] poly, Vector2 p, out int edge)
        {
            float best = float.PositiveInfinity; Vector2 q = p; edge = 0;
            for (int i = 0; i < poly.Length; i++) { var c = Closest(poly[i], poly[(i + 1) % poly.Length], p); float d = (c - p).sqrMagnitude; if (d < best) { best = d; q = c; edge = i; } }
            return q;
        }
        static float DistanceToEdges(Vector2[] p, Vector2 q) => Vector2.Distance(q, Nearest(p, q, out _));
        static bool Intersection(Vector2 a, Vector2 b, Vector2 c, Vector2 d, out float t)
        {
            float den = Cross(b - a, d - c); t = 0;
            if (Mathf.Abs(den) < .000001f) return false;
            t = Cross(c - a, d - c) / den; float u = Cross(c - a, b - a) / den;
            return t >= 0 && t <= 1 && u >= 0 && u <= 1;
        }
        static List<float> Cuts(Vector2[] p, Vector2 a, Vector2 b)
        {
            var result = new List<float>();
            for (int i = 0; i < p.Length; i++) if (Intersection(a, b, p[i], p[(i + 1) % p.Length], out float t)) result.Add(t);
            return result;
        }
        static float SegmentDistance(Vector2 a, Vector2 b, Vector2 c, Vector2 d) => Intersection(a, b, c, d, out _) ? 0
            : Mathf.Min(Vector2.Distance(a, Closest(c, d, a)), Vector2.Distance(b, Closest(c, d, b)), Vector2.Distance(c, Closest(a, b, c)), Vector2.Distance(d, Closest(a, b, d)));
        static string Text(Dictionary<string, object> d, string key) => d.TryGetValue(key, out var v) ? v as string : null;
        static float Number(Dictionary<string, object> d, string key, float fallback) => d.TryGetValue(key, out var v) ? Convert.ToSingle(v) : fallback;
        static Vector2 Point(object v)
        {
            if (v is List<object> a) return new(Convert.ToSingle(a[0]), Convert.ToSingle(a[a.Count == 3 ? 2 : 1]));
            var d = (Dictionary<string, object>)v;
            foreach (string key in new[] { "position", "centre", "center" }) if (d.TryGetValue(key, out var p)) return Point(p);
            return new(Number(d, "x", 0), Number(d, "z", Number(d, "y", 0)));
        }
        static Vector2[] Polygon(object v)
        {
            if (v is Dictionary<string, object> d) v = d.TryGetValue("vertices", out var p) ? p : d["points"];
            return ((List<object>)v).Select(Point).ToArray();
        }
        static IEnumerable<Vector2[]> Polygons(Dictionary<string, object> root, string key) => root.TryGetValue(key, out var v) ? ((List<object>)v).Select(Polygon) : Enumerable.Empty<Vector2[]>();
    }
}

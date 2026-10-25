using System.Collections.Generic;
using System.Linq;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game.Deck
{
    // A hull's deck as data: grid, blocked tiles, stations and baskets, loaded from the
    // <Model>.stations.json file delivered with the boat model (docs/MASTER-PLAN.md B2).
    public sealed class DeckGraph
    {
        public string Hull;
        public DeckGrid Grid;
        public readonly List<Station> Stations = new();
        public readonly List<Basket> Baskets = new();
        public readonly List<Vector2Int> Blocked = new();

        public Station Hold => Stations.FirstOrDefault(s => s.Kind == StationKind.HoldHatch);
        public IEnumerable<Station> OfKind(StationKind k) => Stations.Where(s => s.Kind == k);
        public Station Get(string id) => Stations.FirstOrDefault(s => s.Id == id);

        // Station file for a hull, from the ArtLibrary (filled by ArtImport from Assets/Art/Models/Boats/*.stations.json).
        public static DeckGraph Load(HullDef hull)
        {
            var file = ArtLibrary.Get()?.StationFile(hull.Model);
            return file != null ? Parse(file.text, hull) : null;
        }

        public static DeckGraph Parse(string json, HullDef hull = null)
        {
            var root = (Dictionary<string, object>)MiniJson.Parse(json);
            var g = new DeckGraph { Hull = (string)root["hull"] };
            var grid = (Dictionary<string, object>)root["grid"];
            int w = Int(grid["width"]), h = Int(grid["height"]);
            float cell = (float)(double)grid["cellSize"];
            if (hull != null && (hull.Width != w || hull.Height != h || !Mathf.Approximately(hull.CellSize, cell)))
                throw new System.InvalidOperationException($"[Catchline] {g.Hull} station grid {w}x{h}@{cell} does not match HullDef {hull.Width}x{hull.Height}@{hull.CellSize}");
            g.Grid = new DeckGrid(w, h, cell);
            if (root.TryGetValue("blocked", out var b) && b is List<object> blocked)
                foreach (List<object> t in blocked)
                {
                    var tile = new Vector2Int(Int(t[0]), Int(t[1]));
                    g.Blocked.Add(tile);
                    if (g.Grid.InBounds(tile)) g.Grid.Block(new RectInt(tile, Vector2Int.one));
                }
            foreach (Dictionary<string, object> s in (List<object>)root["stations"])
            {
                var st = new Station
                {
                    Id = (string)s["id"], Kind = Station.ParseKind((string)s["kind"]), Position = Vec(s["pos"]),
                    Yaw = s.TryGetValue("yaw", out var yaw) ? (float)(double)yaw : 0,
                    Places = s.TryGetValue("places", out var p) ? Int(p) : 1,
                    ModelId = s.TryGetValue("runtimeModelId", out var m) ? (string)m : null,
                    BasketPrefix = s.TryGetValue("runtimeBasketPrefix", out var bp) ? (string)bp : null,
                };
                if (s.TryGetValue("workTile", out var wt)) st.WorkTile = Tile(wt);
                if (s.TryGetValue("workTiles", out var wts)) st.WorkTiles = ((List<object>)wts).Select(Tile).ToList();
                if (st.WorkTiles.Count == 0) st.WorkTiles.Add(st.WorkTile);
                else if (!s.ContainsKey("workTile")) st.WorkTile = st.WorkTiles[0];
                var inKind = Station.InKind(st.Kind); var outKind = Station.OutKind(st.Kind);
                if (inKind.HasValue) { st.In = new Basket(st.Id + "/in", inKind.Value, st, s.TryGetValue("basketIn", out var bi) ? Vec(bi) : st.Position); g.Baskets.Add(st.In); }
                if (outKind.HasValue && s.TryGetValue("basketOut", out var bo)) { st.Out = new Basket(st.Id + "/out", outKind.Value, st, Vec(bo)); g.Baskets.Add(st.Out); }
                g.Stations.Add(st);
            }
            // Gear without its own basket shares the nearest gear basket (Skiff rod3 shares rod2's by design).
            foreach (var st in g.Stations.Where(x => x.IsGear && x.Out == null))
                st.Out = g.Stations.Where(x => x.IsGear && x.Out != null && x.Out.Owner == x)
                    .OrderBy(x => (x.Position - st.Position).sqrMagnitude).Select(x => x.Out).FirstOrDefault();
            return g;
        }

        // The tile a worker stands on to use a station: its declared work tile, or the nearest walkable one.
        public Vector2Int Access(Station s)
        {
            foreach (var t in s.WorkTiles) if (!Grid.IsBlocked(t)) return t;
            return Nearest(s.WorkTile);
        }
        public Vector2Int Nearest(Vector2Int from)
        {
            if (!Grid.IsBlocked(from)) return from;
            for (int r = 1; r < Mathf.Max(Grid.Width, Grid.Height); r++)
                for (int dx = -r; dx <= r; dx++)
                    for (int dy = -r; dy <= r; dy++)
                    {
                        if (Mathf.Abs(dx) != r && Mathf.Abs(dy) != r) continue;
                        var t = from + new Vector2Int(dx, dy);
                        if (!Grid.IsBlocked(t)) return t;
                    }
            return from;
        }

        // Path cache: deck layouts are static per voyage, so pairs are solved once.
        readonly Dictionary<(Vector2Int, Vector2Int), List<Vector2Int>> paths = new();
        public List<Vector2Int> Path(Vector2Int from, Vector2Int to)
        {
            if (paths.TryGetValue((from, to), out var p)) return p;
            p = Grid.FindPath(from, to);
            paths[(from, to)] = p;
            return p;
        }
        public bool Reachable(Vector2Int from, Vector2Int to) => from == to || Path(from, to) != null;
        public float Distance(Vector2Int from, Vector2Int to)
        {
            var p = Path(from, to);
            if (p == null) return float.MaxValue;
            float d = 0; var prev = from;
            foreach (var t in p) { d += Vector2Int.Distance(prev, t) * Grid.CellSize; prev = t; }
            return d;
        }

        static int Int(object o) => (int)System.Math.Round((double)o);
        static Vector2Int Tile(object o) { var a = (List<object>)o; return new Vector2Int(Int(a[0]), Int(a[1])); }
        static Vector3 Vec(object o) { var a = (List<object>)o; return new Vector3((float)(double)a[0], (float)(double)a[1], (float)(double)a[2]); }
    }
}

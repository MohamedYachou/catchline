using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Prototype
{
    // Walkable tile grid of the deck. Tile (x, y) sits at boat-local (x, 0, y).
    public class DeckGrid
    {
        public readonly int Width, Height;
        readonly bool[] blocked;

        static readonly Vector2Int[] Dirs =
        {
            new(1, 0), new(-1, 0), new(0, 1), new(0, -1),
            new(1, 1), new(1, -1), new(-1, 1), new(-1, -1),
        };

        public DeckGrid(int width, int height)
        {
            Width = width;
            Height = height;
            blocked = new bool[width * height];
        }

        public bool InBounds(Vector2Int t) => t.x >= 0 && t.y >= 0 && t.x < Width && t.y < Height;
        public bool IsBlocked(Vector2Int t) => !InBounds(t) || blocked[t.y * Width + t.x];

        public void Block(RectInt r)
        {
            foreach (var t in r.allPositionsWithin) blocked[t.y * Width + t.x] = true;
        }

        public static Vector3 ToLocal(Vector2Int t) => new(t.x, 0f, t.y);
        public static Vector2Int ToTile(Vector3 local) => new(Mathf.RoundToInt(local.x), Mathf.RoundToInt(local.z));

        // Breadth-first search with diagonal moves that never cut a blocked corner.
        // Returns the tiles to walk (excluding the start), or null when unreachable.
        public List<Vector2Int> FindPath(Vector2Int from, Vector2Int to)
        {
            var result = new List<Vector2Int>();
            if (from == to) return result;
            if (IsBlocked(to)) return null;

            var came = new Dictionary<Vector2Int, Vector2Int> { [from] = from };
            var queue = new Queue<Vector2Int>();
            queue.Enqueue(from);
            while (queue.Count > 0)
            {
                var c = queue.Dequeue();
                if (c == to) break;
                foreach (var d in Dirs)
                {
                    var n = c + d;
                    if (IsBlocked(n) || came.ContainsKey(n)) continue;
                    if (d.x != 0 && d.y != 0 && (IsBlocked(new Vector2Int(c.x + d.x, c.y)) || IsBlocked(new Vector2Int(c.x, c.y + d.y)))) continue;
                    came[n] = c;
                    queue.Enqueue(n);
                }
            }
            if (!came.ContainsKey(to)) return null;
            for (var c = to; c != from; c = came[c]) result.Add(c);
            result.Reverse();
            return result;
        }
    }
}

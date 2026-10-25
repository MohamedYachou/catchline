using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Cosmetic routes use no catch/economy RNG and never claim a work station.
        // HandThink runs during these walks, so real jobs interrupt on the next step.
        void IdlePatrol(Person hand)
        {
            if (!hand.PatrolReady) return;
            int phase = (hand.PatrolLeg + (hand == Hand ? 0 : ExtraPeople.IndexOf(hand) + 1)) % 4;
            bool port = phase < 2;
            float targetX = (Grid.Width - 1) * Grid.CellSize * (phase % 2 == 0 ? .25f : .75f);
            float targetZ = port ? 0 : (Grid.Height - 1) * Grid.CellSize;
            var target = new Vector3(targetX, 0, targetZ);
            var candidates = new List<Vector2Int>();
            for (int y = 0; y < Grid.Height; y++)
                for (int x = 0; x < Grid.Width; x++)
                {
                    var tile = new Vector2Int(x, y);
                    if (Grid.IsBlocked(tile) || tile == CoolerAccess || tile == NetAccess
                        || Rods.Any(r => r.Unlocked && r.Tile == tile)) continue;
                    var local = Grid.GetLocal(tile);
                    if (Vector3.Distance(local, Grid.GetLocal(hand.Tile)) < .6f) continue;
                    if (People.Any(p => p != hand && Vector3.Distance(Grid.GetLocal(p.Tile), local) < .5f)) continue;
                    candidates.Add(tile);
                }
            foreach (var tile in candidates.OrderBy(t => (Grid.GetLocal(t) - target).sqrMagnitude))
            {
                if (Grid.FindPath(hand.Tile, tile) == null) continue;
                // The deck graph blocks more than the walk grid (stations, baskets): never stroll into a pocket the
                // scheduler cannot route out of, or every job given to this hand cancels on the spot.
                if (UsesDeckGraph && DeckGraph?.Hold != null && !DeckGraph.Reachable(tile, DeckGraph.Access(DeckGraph.Hold))) continue;
                hand.Stroll(Grid, tile, port ? Vector3.back : Vector3.forward);
                return;
            }
        }

        void FaceHold(Person person) => person.FacePoint(Grid.GetLocal(CoolerTile));
        void FaceNet(Person person) => person.Face(IsNetFisher ? Vector3.right : new Vector3(1, 0, -.5f));
    }
}

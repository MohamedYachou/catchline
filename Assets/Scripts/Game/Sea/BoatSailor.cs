using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game.Sea
{
    public sealed class BoatSailor
    {
        public readonly SeaNav Nav;
        readonly HullDef hull;
        List<Vector2> route;
        int next;
        float arrivalRadius;
        public Vector2 Position { get; private set; }
        public float Heading { get; private set; } // radians in the navigation X/Z plane
        public float Speed { get; private set; }
        public bool Arrived { get; private set; } = true;
        public IReadOnlyList<Vector2> Route => route;
        public BoatSailor(SeaNav nav, HullDef hull, Vector2 position, float heading = 0)
        { Nav = nav; this.hull = hull; Position = nav.Resolve(position); Heading = heading; }
        public bool SailTo(Vector2 target, float radius = .35f)
        {
            if (Nav.InShallows(Nav.Snap(target))) return false;
            var plan = Nav.Plan(Position, target);
            if (plan == null) return false;
            route = plan; next = 1; arrivalRadius = Mathf.Max(.15f, radius); Arrived = false;
            return true;
        }
        public void Push(Vector2 position) => Position = Nav.Resolve(position);
        public void Tick(float dt)
        {
            // Substeps make large test ticks and frame spikes obey the same collision/turn limits.
            while (dt > 0 && !Arrived)
            {
                float step = Mathf.Min(dt, .025f); dt -= step;
                if (route == null || next >= route.Count) { Arrived = true; Speed = 0; break; }
                var target = route[next]; var delta = target - Position;
                bool last = next == route.Count - 1;
                float distance = delta.magnitude;
                if (last && distance <= arrivalRadius && !Nav.InShallows(Position)) { Arrived = true; Speed = 0; break; }
                if (!last && distance <= .01f) { next++; continue; }
                float desired = Mathf.Atan2(delta.y, delta.x) * Mathf.Rad2Deg;
                float degrees = Mathf.MoveTowardsAngle(Heading * Mathf.Rad2Deg, desired, hull.TurnDegreesPerSecond * step);
                Heading = degrees * Mathf.Deg2Rad;
                float error = Mathf.Abs(Mathf.DeltaAngle(degrees, desired));
                // Slow before corners so a finite turning radius never cuts inside a shoreline.
                float speed = hull.SailSpeed * (Nav.InShallows(Position) ? .5f : 1);
                speed *= error <= .001f ? 1f : 0f;
                if (last) speed = Mathf.Min(speed, Mathf.Max(.35f, (distance - arrivalRadius) * 3));
                var forward = new Vector2(Mathf.Cos(Heading), Mathf.Sin(Heading));
                var proposed = Position + forward * Mathf.Min(distance, speed * step);
                var moved = Nav.Slide(Position, proposed);
                Speed = Vector2.Distance(Position, moved) / step; Position = moved;
            }
        }
    }
}

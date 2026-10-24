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
        float arrivalRadius, drive;
        public Vector2 Position { get; private set; }
        public float Heading { get; private set; }
        public float Speed { get; private set; }
        public float TurnRate { get; private set; }
        public bool Arrived { get; private set; } = true;
        public IReadOnlyList<Vector2> Route => route;
        public int NextWaypoint => next;
        public BoatSailor(SeaNav nav, HullDef hull, Vector2 position, float heading = 0)
        { Nav = nav; this.hull = hull; Position = nav.Resolve(position); Heading = heading; }
        public bool SailTo(Vector2 target, float radius = .35f)
        {
            var plan = Nav.Plan(Position, target);
            if (plan == null) return false;
            route = plan; next = 1; arrivalRadius = Mathf.Max(.15f, radius); Arrived = false;
            return true;
        }
        public void Stop() { Arrived = true; Speed = drive = TurnRate = 0; route = null; next = 0; }
        public void Push(Vector2 position) => Position = Nav.Resolve(position);
        public void Tick(float dt)
        {
            while (dt > 0 && !Arrived)
            {
                float step = Mathf.Min(dt, .025f); dt -= step;
                if (route == null || next >= route.Count) { Arrived = true; Speed = drive = TurnRate = 0; break; }
                var delta = route[next] - Position;
                bool last = next == route.Count - 1;
                float distance = delta.magnitude;
                if (last && distance <= arrivalRadius) { Arrived = true; Speed = drive = TurnRate = 0; break; }
                if (!last && distance <= .01f) { next++; continue; }
                float desired = Mathf.Atan2(delta.y, delta.x) * Mathf.Rad2Deg;
                float old = Heading * Mathf.Rad2Deg;
                float turn = hull.TurnDegreesPerSecond * Mathf.Clamp(3f / (hull.Width * hull.CellSize), .55f, 1f);
                float degrees = Mathf.MoveTowardsAngle(old, desired, turn * step);
                TurnRate = Mathf.DeltaAngle(old, degrees) / step; Heading = degrees * Mathf.Deg2Rad;
                float error = Mathf.Abs(Mathf.DeltaAngle(degrees, desired));
                float speed = hull.SailSpeed * (Nav.InShallows(Position) ? .5f : 1);
                float boatLength = Mathf.Max(3, hull.Width * hull.CellSize + 1);
                float brake = hull.SailSpeed * hull.SailSpeed / (2 * boatLength);
                // A graph corner is approached slowly before turning; never round it through land.
                bool corner = !last && Vector2.Angle(delta, route[next + 1] - route[next]) > 20;
                if (last || corner) speed = Mathf.Min(speed, Mathf.Sqrt(2 * brake * Mathf.Max(.005f, distance - (last ? arrivalRadius : 0))));
                if (error > 20) speed = 0;
                drive = Mathf.MoveTowards(drive, speed, step * (drive < speed ? hull.SailSpeed / 1.5f : brake));
                // Keep the clearance-proven segment while the visual heading catches the last few degrees.
                var proposed = Position + delta.normalized * Mathf.Min(distance, error > 20 ? 0 : drive * step);
                var moved = Nav.Slide(Position, proposed);
                Speed = Vector2.Distance(Position, moved) / step; Position = moved;
            }
        }
    }
}

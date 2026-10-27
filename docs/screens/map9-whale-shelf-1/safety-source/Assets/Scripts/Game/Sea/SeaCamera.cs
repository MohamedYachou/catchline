using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        float seaCameraBlend, seaBank;
        Vector3 SeaCameraTarget(Vector3 anchored, float dt)
        {
            float target = Navigation != null && Sailor != null && !Sailor.Arrived ? 1 : 0;
            seaCameraBlend = Mathf.Lerp(seaCameraBlend, target, 1 - Mathf.Exp(-Mathf.Max(0, dt) * 3));
            Cam.transform.rotation = Quaternion.Euler(45 + 9 * seaCameraBlend, 35, 0);
            return anchored + new Vector3(.574f, 0, .819f) * (3 * seaCameraBlend);
        }
        float SeaCameraSize(float anchored)
        {
            float size = anchored + 5 * seaCameraBlend;
            if (Navigation == null || Sailor == null || Navigation.CameraBounds.Contains(Sailor.Position)) return size;
            // Authored camera bounds are inset from the sailing border. Widen at
            // that clamp rather than allowing the hull to leave the visible water.
            var delta = Boat.TransformPoint(State.HullDef.Center) - camCenter;
            float margin = State.HullDef.NavigationRadius + 1;
            float vertical = Mathf.Abs(Vector3.Dot(delta, Cam.transform.up)) + margin;
            float horizontal = (Mathf.Abs(Vector3.Dot(delta, Cam.transform.right)) + margin) / Cam.aspect;
            return Mathf.Max(size, Mathf.Max(vertical, horizontal) * 2);
        }
        float SeaCameraDistance() => Navigation != null ? Mathf.Max(40, Cam.orthographicSize * 2.5f) : 40;
        Quaternion SeaBankRotation(float dt)
        {
            float target = Navigation != null && Sailor != null && !Sailor.Arrived
                ? Mathf.Clamp(-Sailor.TurnRate / 35, -3, 3) * Mathf.Clamp01(Sailor.Speed / 2) : 0;
            seaBank = Mathf.Lerp(seaBank, target, 1 - Mathf.Exp(-Mathf.Max(0, dt) * 7));
            // Boat local X is its fore-aft axis.
            return Quaternion.Euler(seaBank, 0, 0);
        }
    }
}

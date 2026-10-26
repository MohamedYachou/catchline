using UnityEngine;
using UnityEngine.InputSystem;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        float strikeFxBorn = float.NegativeInfinity;
        Vector2 strikeFxPoint;
        const float StrikeFxSeconds = .45f;

        Vector2 StrikeBobberPoint()
        {
            var bobber = transform.Find("Captain rod view/Bobber reading");
            var world = bobber != null ? bobber.position : rodView.Rod.CastTarget;
            // Keep the cue on the water surface while the float dips underneath it.
            world.y = rodView.Rod.CastTarget.y + .02f;
            var v = Cam.WorldToViewportPoint(world);
            return new Vector2(v.x * iw, (1 - v.y) * ih);
        }

        void RecordStrikeFx()
        {
            if (!RodViewActive || !HasUi("fx-tap-ripple")) return;
            var pointer = Pointer.current;
            // Space/programmatic strikes originate at the bobber; touch/mouse use the actual press.
            strikeFxPoint = pointer != null && pointer.press.wasPressedThisFrame
                ? ToGui(pointer.position.ReadValue()) / new Vector2(VW, VH)
                : StrikeBobberPoint() / new Vector2(iw, ih);
            strikeFxBorn = SimTime;
        }

        void InterfaceStrikeFx()
        {
            if (!RodViewActive) return;
            if (rodView.Rod.State == RodState.Bite && !rodView.Rod.ReadingResult.HasValue && HasUi("fx-tap-burst"))
            {
                var bobber = StrikeBobberPoint();
                float size = compactInterface ? 128 : 144;
                float pulse = 1 + .04f * (1 - Mathf.Cos(SimTime * Mathf.PI * 2 / .9f));
                if (HasUi("fx-tap-ripple"))
                    coastalUi.Icon("strikefx/bobber-ring", Centered(bobber.x, bobber.y, 88, 88), "fx-tap-ripple");
                float separation = 44 + size * .54f + 12;
                float x = bobber.x + separation;
                if (x + size * .54f > iw - Edge) x = bobber.x - separation;
                x = Mathf.Clamp(x, Edge + size * .54f, iw - Edge - size * .54f);
                float y = Mathf.Clamp(bobber.y, Edge + size * .54f, ih - Edge - 100);
                coastalUi.Icon("strikefx/burst", Centered(x, y, size, size), "fx-tap-burst");
                var badge = coastalUi.Pose("strikefx/burst", scale: pulse);
                coastalUi.Text("strikefx/label", new Rect(size * .16f, size * .27f, size * .68f, size * .46f),
                    "TAP!", Skin.Type.Display, Skin.Ink, TextAnchor.MiddleCenter, badge);
            }
            float k = (SimTime - strikeFxBorn) / StrikeFxSeconds;
            if (k < 0 || k >= 1 || !HasUi("fx-tap-ripple")) return;
            float diameter = 140 * Mathf.Lerp(.3f, 1.4f, Ease.OutCubic(k));
            var point = strikeFxPoint * new Vector2(iw, ih);
            coastalUi.Icon("strikefx/ripple", Centered(point.x, point.y, diameter, diameter), "fx-tap-ripple", null, Tint(Color.white, 1 - k));
        }
    }
}

using UnityEngine;
using UnityEngine.UI;

namespace Catchline.Game
{
    // Motion helpers for animated screens (crew cards, chests). Elements are retained and repositioned every
    // frame, so a pose is reapplied each frame after the element is drawn.
    public sealed partial class CoastalCanvas
    {
        // Rotates and scales an element drawn this frame about its centre. Identity values reset an old pose.
        public RectTransform Pose(string id, float angle = 0, float scale = 1, float scaleX = 1)
        {
            if (!elements.TryGetValue(id, out var e)) return null;
            var rt = e.Rect; var size = rt.sizeDelta;
            if (rt.pivot != new Vector2(.5f, .5f))
            {
                rt.pivot = new Vector2(.5f, .5f);
                rt.anchoredPosition += new Vector2(size.x * .5f, -size.y * .5f);
            }
            rt.localEulerAngles = new Vector3(0, 0, angle);
            rt.localScale = new Vector3(scale * scaleX, scale, 1);
            return rt;
        }

        // Children of this element are clipped to its rect (shine sweeps, sliding fills).
        public void Clip(string id)
        {
            if (elements.TryGetValue(id, out var e) && e.Rect.GetComponent<RectMask2D>() == null) e.Rect.gameObject.AddComponent<RectMask2D>();
        }

        // Where an element drawn this frame sits, in the root's logical top-left coordinates (through nested parents
        // and scrolls). Coach marks use it to point at a button wherever its screen put it.
        public bool TryFind(string id, out Rect r)
        {
            r = default;
            if (!elements.ContainsKey(id) && aliases.TryGetValue(id, out var target)) id = target;
            if (!elements.TryGetValue(id, out var e) || !e.Used || !e.Rect.gameObject.activeInHierarchy) return false;
            var corners = new Vector3[4]; e.Rect.GetWorldCorners(corners);
            Vector2 topLeft = Root.InverseTransformPoint(corners[1]), bottomRight = Root.InverseTransformPoint(corners[3]);
            var root = Root.rect;
            r = Rect.MinMaxRect(topLeft.x - root.xMin, root.yMax - topLeft.y, bottomRight.x - root.xMin, root.yMax - bottomRight.y);
            return r.width > 0 && r.height > 0;
        }

        // A transparent container for grouping and posing children.
        public RectTransform Group(string id, Rect r, Transform parent = null)
        {
            var e = Get(id, r, parent);
            if (e.Image != null) e.Image.color = Color.clear;
            return e.Rect;
        }
    }

    // Easing curves (t in 0..1).
    public static class Ease
    {
        public static float Clamp(float t) => t < 0 ? 0 : t > 1 ? 1 : t;
        public static float OutCubic(float t) { t = Clamp(t); return 1 - (1 - t) * (1 - t) * (1 - t); }
        public static float InCubic(float t) { t = Clamp(t); return t * t * t; }
        public static float OutBack(float t, float s = 1.70158f) { t = Clamp(t) - 1; return t * t * ((s + 1) * t + s) + 1; }
        public static float OutElastic(float t)
        {
            t = Clamp(t);
            if (t == 0 || t == 1) return t;
            return Mathf.Pow(2, -10 * t) * Mathf.Sin((t * 10 - .75f) * (2 * Mathf.PI / 3)) + 1;
        }
        // 0 -> 1 -> 0 bump.
        public static float Pulse(float t) { t = Clamp(t); return Mathf.Sin(t * Mathf.PI); }
    }
}

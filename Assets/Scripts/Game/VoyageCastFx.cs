using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        const float CastFxSeconds = .7f;
        readonly Dictionary<Rod, (float born, Vector3 point)> castFx = new();

        // Both captain close-up and deck rods pass this boundary. Keep their existing splash audio.
        void TickCastRod(Rod rod, float dt)
        {
            bool flying = rod.State == RodState.Flying;
            rod.Tick(this, dt, Attending(rod) || FisherAt(rod));
            if (flying && rod.State == RodState.Waiting)
                castFx[rod] = (SimTime, rod.CastTarget);
        }

        void InterfaceCastFx()
        {
            if (CurrentMode != Mode.Fishing || MenuOpen) return;
            foreach (var pair in castFx)
            {
                float t = SimTime - pair.Value.born;
                if (t < 0 || t >= CastFxSeconds || !Rods.Contains(pair.Key)) continue;
                var view = Cam.WorldToViewportPoint(pair.Value.point);
                if (view.z <= 0) continue;
                float x = view.x * iw, y = (1 - view.y) * ih;
                // Reproject every frame: the water point stays fixed while the cast camera settles.
                var edge = Cam.WorldToViewportPoint(pair.Value.point + Cam.transform.right);
                float unit = Mathf.Abs(edge.x - view.x) * iw;
                float k = t / CastFxSeconds;
                float size = unit * Mathf.Lerp(.35f, 1.65f, Ease.OutCubic(k));
                string id = "castfx/" + pair.Key.Index;
                bool ring = HasUi("fx-cast-ring");
                coastalUi.Icon(id + "/ring", Centered(x, y, size, size), ring ? "fx-cast-ring" : "fx-glow", null,
                    Tint(ring ? Color.white : new Color(.39f, .78f, .77f), (1 - k) * .85f));
                // Ring art already contains the water-plane oval; keep the square sprite aspect.
                if (t < .32f && HasUi("fx-cast-drops"))
                {
                    float pop = t / .32f, drops = unit * Mathf.Lerp(.5f, 1.1f, Ease.OutCubic(pop));
                    coastalUi.Icon(id + "/drops", Centered(x, y - unit * .12f * Mathf.Sin(pop * Mathf.PI), drops, drops),
                        "fx-cast-drops", null, Tint(Color.white, 1 - pop));
                }
            }
            // CoastalCanvas.End hides every id omitted this frame, including expired drops and rings.
        }
    }
}

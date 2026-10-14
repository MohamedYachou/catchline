using UnityEngine;

namespace Catchline.Game
{
    // Small ambient behaviours on scenery models. Purely visual: they read real time, not the voyage clock.

    // A perched seagull: turns its head about, flaps now and then, and sometimes flies off and comes back later.
    public class Gull : MonoBehaviour
    {
        Transform wingL, wingR;
        Quaternion baseL, baseR;
        Vector3 perch;
        Quaternion perchRot;
        float nextFlap, flapUntil, nextTurn, flightT = -1f, awayUntil;
        Vector3 flightDir;
        System.Random rng;

        float R(float a, float b) => a + (float)rng.NextDouble() * (b - a);

        void Start()
        {
            rng = new System.Random(GetInstanceID());
            wingL = ArtLibrary.Find(gameObject, "Wing_L");
            wingR = ArtLibrary.Find(gameObject, "Wing_R");
            if (wingL != null) baseL = wingL.localRotation;
            if (wingR != null) baseR = wingR.localRotation;
            perch = transform.localPosition;
            perchRot = transform.localRotation;
            nextFlap = Time.time + R(2f, 8f);
            nextTurn = Time.time + R(1f, 4f);
        }

        void Update()
        {
            float t = Time.time;
            if (flightT >= 0f)
            {
                // Flying away: climb and leave, then reappear on the perch after a while.
                flightT += Time.deltaTime;
                transform.localPosition = perch + flightDir * (flightT * 3.5f) + Vector3.up * (flightT * flightT * 0.9f + flightT * 0.8f);
                Flap(t, 14f, 55f);
                if (flightT > 6f)
                {
                    flightT = -1f;
                    awayUntil = t + R(10f, 25f);
                    SetVisible(false);
                }
                return;
            }
            if (awayUntil > 0f)
            {
                if (t < awayUntil) return;
                awayUntil = 0f;
                transform.localPosition = perch;
                transform.localRotation = perchRot;
                SetVisible(true);
                flapUntil = t + 0.8f;
            }
            if (t > nextTurn)
            {
                transform.localRotation = perchRot * Quaternion.Euler(0f, R(-50f, 50f), 0f);
                nextTurn = t + R(1.5f, 5f);
            }
            if (t > nextFlap)
            {
                flapUntil = t + R(0.5f, 1.2f);
                nextFlap = t + R(4f, 12f);
                if (rng.NextDouble() < 0.12) FlyOff();
            }
            if (t < flapUntil) Flap(t, 12f, 45f);
            else Flap(0f, 0f, 0f);
        }

        public void FlyOff()
        {
            if (flightT >= 0f || awayUntil > 0f) return;
            flightT = 0f;
            float a = R(0f, Mathf.PI * 2f);
            flightDir = new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a));
            transform.localRotation = Quaternion.LookRotation(flightDir);
        }

        void Flap(float t, float speed, float amp)
        {
            float a = Mathf.Sin(t * speed) * amp;
            if (wingL != null) wingL.localRotation = baseL * Quaternion.Euler(0f, 0f, a);
            if (wingR != null) wingR.localRotation = baseR * Quaternion.Euler(0f, 0f, -a);
        }

        void SetVisible(bool on)
        {
            foreach (var r in GetComponentsInChildren<Renderer>()) r.enabled = on;
        }
    }

    // Bobs and rocks a floating object (buoys, moored boats).
    public class Floater : MonoBehaviour
    {
        public float Amp = 0.04f, Rock = 3f, Speed = 1f;
        Vector3 basePos;
        Quaternion baseRot;
        float phase;

        void Start()
        {
            basePos = transform.localPosition;
            baseRot = transform.localRotation;
            phase = (GetInstanceID() % 100) * 0.37f;
        }

        void Update()
        {
            float t = Time.time * Speed + phase;
            transform.localPosition = basePos + Vector3.up * (Mathf.Sin(t * 1.3f) * Amp);
            transform.localRotation = baseRot * Quaternion.Euler(Mathf.Sin(t) * Rock, 0f, Mathf.Sin(t * 0.8f + 1f) * Rock);
        }
    }

    // Slowly rises and sinks a part (the whale tail, later), or spins one (propellers, winch drums).
    public class Spinner : MonoBehaviour
    {
        public Vector3 Axis = Vector3.forward;
        public float DegreesPerSecond;
        void Update() => transform.Rotate(Axis, DegreesPerSecond * Time.deltaTime, Space.Self);
    }

    // A whale surfacing now and then far off: the tail rises out of the water, hangs, and slides back down.
    public class WhaleTail : MonoBehaviour
    {
        Vector3 basePos;
        float next, t = -1f;

        void Start()
        {
            basePos = transform.localPosition;
            transform.localPosition = basePos + Vector3.down * 2f;
            next = Time.time + 4f;
        }

        void Update()
        {
            if (t < 0f)
            {
                if (Time.time < next) return;
                t = 0f;
            }
            t += Time.deltaTime;
            // 0-1.5 s rise, 1.5-3.5 s hold, 3.5-5 s sink.
            float up = t < 1.5f ? t / 1.5f : t < 3.5f ? 1f : Mathf.Max(0f, 1f - (t - 3.5f) / 1.5f);
            up = Mathf.SmoothStep(0f, 1f, up);
            transform.localPosition = basePos + Vector3.down * (2f * (1f - up));
            transform.localRotation = Quaternion.Euler(0f, transform.localEulerAngles.y, (1f - up) * 25f);
            if (t > 5f)
            {
                t = -1f;
                next = Time.time + Random.Range(25f, 60f);
            }
        }
    }
}

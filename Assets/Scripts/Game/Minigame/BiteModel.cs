using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    public enum FishPhase { Approach, Inspect, Nibble, Fake, Take, Hooked, Spooked, Gone }
    public enum StrikeResult { Hooked, TooEarly, TooLate }

    // One fish working one bait, as the full-screen rod view shows it. Pure logic: the view only reads the signals.
    // A small fish comes straight in, nibbles once or twice and takes. A big fish circles, nibbles longer, fakes
    // (one deep dip that pops back up while it backs off) and its real take gives a much shorter strike window.
    // The only honest tell of a take: the bobber goes fully under and STAYS under while the line runs sideways.
    public class BiteModel
    {
        // Bobber: 0 floating, 1 pulled fully under. Drift: bobber offset on the water plane (m, x right / y away).
        public float Dip { get; private set; }
        public Vector2 Drift { get; private set; }
        // Rod tip bend 0..1, for the foreground rod and the line tension.
        public float RodPull { get; private set; }
        // Fish relative to the bobber (m), heading (radians, 0 = +x), depth 0 surface .. 1 deep.
        public Vector2 FishPos { get; private set; }
        public float FishHeading { get; private set; }
        public float FishDepth { get; private set; } = 1f;
        public bool Dart { get; private set; } // true on the frame the fish bolts (spook, fake back-off)

        public FishPhase Phase { get; private set; } = FishPhase.Approach;
        public float PhaseTime { get; private set; }
        public readonly float Difficulty, TakeWindow;

        readonly System.Random rng;
        readonly Queue<(FishPhase phase, float seconds, float depth)> beats = new();
        float beatLength, beatDepth, circle, wobble;
        Vector2 from, to;

        public BiteModel(float difficulty, System.Random rng)
        {
            Difficulty = Mathf.Clamp01(difficulty); this.rng = rng;
            TakeWindow = Mathf.Lerp(.9f, .42f, Difficulty);
            beats.Enqueue((FishPhase.Approach, Range(1.6f, 2.6f) + Difficulty * 1.5f, 0));
            if (Difficulty > .25f || Roll(.4f)) beats.Enqueue((FishPhase.Inspect, Range(.8f, 1.6f) + Difficulty * 1.6f, 0));
            int nibbles = 1 + rng.Next(2) + Mathf.RoundToInt(Difficulty * 2), fakes = (int)(Difficulty * 2.6f + (float)rng.NextDouble() * .6f);
            // Interleave: a fake never comes first, and never right before the take on the smallest fish.
            while (nibbles + fakes > 0)
            {
                bool fake = fakes > 0 && (nibbles == 0 || beats.Count > 1 && Roll(.45f));
                if (fake) { fakes--; beats.Enqueue((FishPhase.Fake, Range(.7f, 1f), Mathf.Lerp(.55f, .88f, Difficulty) + Range(-.05f, .05f))); }
                else { nibbles--; beats.Enqueue((FishPhase.Nibble, Range(.5f, .9f), Range(.14f, .3f))); }
                if (Roll(.5f)) beats.Enqueue((FishPhase.Inspect, Range(.5f, 1.2f), 0));
            }
            beats.Enqueue((FishPhase.Take, TakeWindow, 1));
            float a = Range(0, Mathf.PI * 2);
            FishPos = from = new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * Range(2.4f, 3.2f);
            FishHeading = a + Mathf.PI;
            Next();
        }

        float Range(float a, float b) => a + (float)rng.NextDouble() * (b - a);
        bool Roll(float p) => rng.NextDouble() < p;

        void Next()
        {
            if (beats.Count == 0) { Enter(FishPhase.Gone, 0); return; }
            var b = beats.Dequeue();
            Enter(b.phase, b.seconds); beatDepth = b.depth;
        }

        void Enter(FishPhase phase, float seconds)
        {
            Phase = phase; PhaseTime = 0; beatLength = seconds; from = FishPos;
            float a = Range(0, Mathf.PI * 2);
            to = phase switch
            {
                FishPhase.Approach => new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * Range(.6f, .9f),
                FishPhase.Inspect => FishPos.normalized * Range(.45f, .8f),
                FishPhase.Nibble or FishPhase.Fake or FishPhase.Take => FishPos.normalized * .12f,
                FishPhase.Spooked or FishPhase.Gone => FishPos.normalized * 4f + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * .5f,
                _ => FishPos,
            };
            Dart = phase is FishPhase.Spooked or FishPhase.Gone;
            if (phase == FishPhase.Take) circle = FishHeading; // runs off the way it faces
        }

        public void Tick(float dt)
        {
            Dart = false; PhaseTime += dt; wobble += dt;
            float k = beatLength > 0 ? Mathf.Clamp01(PhaseTime / beatLength) : 1, ease = k * k * (3 - 2 * k);
            Vector2 last = FishPos;
            switch (Phase)
            {
                case FishPhase.Approach:
                    FishPos = Vector2.Lerp(from, to, ease); FishDepth = Mathf.Lerp(1, .55f, ease);
                    Dip = 0; RodPull = 0; break;
                case FishPhase.Inspect:
                    circle += dt * Mathf.Lerp(1.6f, .9f, Difficulty);
                    FishPos = Vector2.Lerp(from, new Vector2(Mathf.Cos(circle), Mathf.Sin(circle)) * to.magnitude, ease);
                    FishDepth = Mathf.Lerp(FishDepth, .45f, dt * 2); Dip = 0; RodPull = 0; break;
                case FishPhase.Nibble:
                    FishPos = Vector2.Lerp(from, to, Mathf.Min(1, k * 4)); FishDepth = .35f;
                    // Two or three quick shallow ticks, the rod tip barely twitching.
                    float tick = Mathf.Max(0, Mathf.Sin(k * Mathf.PI * 5));
                    Dip = tick * tick * beatDepth; RodPull = Dip * .4f; break;
                case FishPhase.Fake:
                    // Pulls down hard, holds a moment, lets go: the bobber pops back and bounces, the fish backs off.
                    FishDepth = .3f;
                    if (k < .3f) { FishPos = Vector2.Lerp(from, to, k / .3f); Dip = Mathf.SmoothStep(0, beatDepth, k / .3f); }
                    else if (k < .48f) Dip = beatDepth;
                    else
                    {
                        if (PhaseTime - dt < beatLength * .48f) Dart = true;
                        float r = (k - .48f) / .52f;
                        Dip = Mathf.Max(0, beatDepth * (1 - r * 2.2f)) - Mathf.Sin(r * Mathf.PI * 3) * (1 - r) * .12f;
                        FishPos = Vector2.Lerp(to, to.normalized * .9f, Mathf.SmoothStep(0, 1, r));
                    }
                    RodPull = Mathf.Max(0, Dip) * .55f; break;
                case FishPhase.Take:
                    // Under and going: the bobber stays down and travels with the fish.
                    FishDepth = .25f; Dip = Mathf.Min(1, PhaseTime / .14f);
                    FishPos += new Vector2(Mathf.Cos(circle), Mathf.Sin(circle)) * dt * Mathf.Lerp(.5f, .9f, Difficulty);
                    Drift = FishPos * .8f; RodPull = Mathf.Min(1, PhaseTime / .25f); break;
                case FishPhase.Hooked:
                    Dip = 1; RodPull = 1; FishDepth = Mathf.Max(0, FishDepth - dt);
                    FishPos += new Vector2(Mathf.Sin(wobble * 9), Mathf.Cos(wobble * 7)) * dt * .4f; Drift = FishPos * .8f; break;
                case FishPhase.Spooked:
                case FishPhase.Gone:
                    FishPos = Vector2.Lerp(from, to, Mathf.Min(1, PhaseTime / .6f)); FishDepth = Mathf.Min(1, FishDepth + dt * 1.5f);
                    Dip = Mathf.Max(0, Dip - dt * 4); RodPull = Mathf.Max(0, RodPull - dt * 4); Drift = Vector2.Lerp(Drift, Vector2.zero, dt * 3); break;
            }
            if (Phase is not (FishPhase.Take or FishPhase.Hooked or FishPhase.Spooked or FishPhase.Gone)) Drift = Vector2.Lerp(Drift, Vector2.zero, dt * 4);
            var v = FishPos - last; if (v.sqrMagnitude > 1e-6f) FishHeading = Mathf.Atan2(v.y, v.x);
            if (Phase is FishPhase.Approach or FishPhase.Inspect or FishPhase.Nibble or FishPhase.Fake && k >= 1) Next();
            else if (Phase == FishPhase.Take && PhaseTime > TakeWindow) Enter(FishPhase.Gone, .6f); // spat the hook, bait gone
        }

        // A strike on anything but a take spooks the fish; after the window it has already spat the bait.
        public StrikeResult Strike()
        {
            if (Phase == FishPhase.Take) { Enter(FishPhase.Hooked, 0); return StrikeResult.Hooked; }
            if (Phase == FishPhase.Gone) return StrikeResult.TooLate;
            if (Phase != FishPhase.Hooked) Enter(FishPhase.Spooked, .6f);
            return Phase == FishPhase.Hooked ? StrikeResult.Hooked : StrikeResult.TooEarly;
        }

        public bool Finished => Phase is FishPhase.Spooked or FishPhase.Gone && PhaseTime > .6f;

        // 0 for a minimum-size herring, 1 for a maximum cod or conger: species heaviness plus where the kg sits in its range.
        public static float DifficultyFor(Species species, float kg)
        {
            var s = GameData.Get(species);
            float size = s.MaxKg > s.MinKg ? Mathf.InverseLerp(s.MinKg, s.MaxKg, kg) : .5f;
            return Mathf.Clamp01(s.Heaviness * .7f + size * .3f + (kg > s.MaxKg ? .15f : 0));
        }
    }
}

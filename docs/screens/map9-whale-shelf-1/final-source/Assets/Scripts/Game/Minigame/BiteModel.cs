using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    public enum FishPhase { Approach, Inspect, Nibble, Fake, Take, Hooked, Spooked, Gone }
    public enum StrikeResult { Hooked, TooEarly, TooLate }
    // How a species works the bait (docs/plans/FISHING-MINIGAME.md, variety): quick nervous darters, heavy fish,
    // bottom feeders whose take lifts the bobber flat before it slides, and eels that mouth slowly and writhe.
    public enum FishStyle { Darter, Heavy, Bottom, Eel }

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

        // Variety signals. Tilt: the bobber lying flat 0..1 (the bottom feeder's lift bite). Thrash 0..1 while hooked.
        // Jump: true on the frame a hooked jumper clears the water. HookedDone: the fight is over, start the lift.
        public FishStyle Style { get; private set; } = FishStyle.Heavy;
        public bool Jumper { get; private set; }
        public int Shoal { get; private set; } = 1; // darters can come as two or three shadows together
        public float Tilt { get; private set; }
        public float Thrash { get; private set; }
        public bool Jump { get; private set; }
        public float HookedSeconds { get; private set; } = 1.5f;
        public bool HookedDone => Phase == FishPhase.Hooked && PhaseTime >= HookedSeconds;

        public FishPhase Phase { get; private set; } = FishPhase.Approach;
        public float PhaseTime { get; private set; }
        public readonly float Difficulty, TakeWindow;

        readonly System.Random rng;
        readonly Queue<(FishPhase phase, float seconds, float depth)> beats = new();
        float beatLength, beatDepth, circle, wobble;
        Vector2 from, to;
        float approachScale = 1f, runSpeed = 1f, fightScale = 1f, nextJump = -1f;

        public static FishStyle StyleOf(Species species) => species switch
        {
            Species.Herring or Species.Mackerel or Species.Whiting or Species.RedMullet or Species.FlyingFish or Species.Lionfish => FishStyle.Darter,
            Species.Plaice or Species.Turbot or Species.Monkfish or Species.SpottedEagleRay or Species.BlueSpottedStingray or Species.GiantDevilManta or Species.Crab => FishStyle.Bottom,
            Species.Conger or Species.GiantSquid => FishStyle.Eel,
            _ => FishStyle.Heavy,
        };
        public static bool JumperOf(Species species) => species is Species.Mackerel or Species.SeaBass or Species.FlyingFish or Species.MahiMahi
            or Species.Barracuda or Species.AtlanticSwordfish or Species.YellowfinTuna or Species.GiantDevilManta;

        // The species form: difficulty from DifficultyFor, behaviour from its style.
        public BiteModel(Species species, float kg, System.Random rng) : this(DifficultyFor(species, kg), rng, StyleOf(species), JumperOf(species)) { }

        public BiteModel(float difficulty, System.Random rng) : this(difficulty, rng, FishStyle.Heavy, false) { }

        BiteModel(float difficulty, System.Random rng, FishStyle style, bool jumper)
        {
            Difficulty = Mathf.Clamp01(difficulty); this.rng = rng; Style = style; Jumper = jumper;
            // Approach speed, take window, run speed and fight length by style; Heavy is the reference (all 1).
            float window = 0;
            switch (style)
            {
                case FishStyle.Darter: approachScale = .55f; runSpeed = 1.6f; fightScale = .8f; Shoal = Roll(.45f) ? 2 + rng.Next(2) : 1; break;
                case FishStyle.Bottom: approachScale = .8f; window = .1f; runSpeed = .6f; break;
                case FishStyle.Eel: approachScale = 1.3f; window = .25f; runSpeed = .5f; fightScale = 1.4f; break;
            }
            TakeWindow = Mathf.Lerp(.9f, .42f, Difficulty) + window;
            HookedSeconds = Mathf.Lerp(1f, 2.5f, Difficulty) * fightScale;
            beats.Enqueue((FishPhase.Approach, (Range(1.6f, 2.6f) + Difficulty * 1.5f) * approachScale, 0));
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
            if (phase == FishPhase.Hooked) nextJump = Jumper ? Range(.25f, .55f) * HookedSeconds : -1f;
        }

        public void Tick(float dt)
        {
            Dart = false; Jump = false; PhaseTime += dt; wobble += dt;
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
                    FishDepth = .25f;
                    if (Style == FishStyle.Bottom)
                    {
                        // The lift bite: the fish rises with the bait, the bobber lies flat, then slides away flat.
                        Tilt = Mathf.Min(1, PhaseTime / .25f); Dip = .15f * Tilt;
                        FishPos += new Vector2(Mathf.Cos(circle), Mathf.Sin(circle)) * dt * runSpeed * Mathf.Clamp01((PhaseTime - .25f) * 4);
                    }
                    else
                    {
                        // Under and going: the bobber stays down and travels with the fish.
                        Dip = Mathf.Min(1, PhaseTime / .14f);
                        FishPos += new Vector2(Mathf.Cos(circle), Mathf.Sin(circle)) * dt * Mathf.Lerp(.5f, .9f, Difficulty) * runSpeed;
                    }
                    Drift = FishPos * .8f; RodPull = Mathf.Min(1, PhaseTime / .25f); break;
                case FishPhase.Hooked:
                    Dip = 1; Tilt = 0; RodPull = 1; FishDepth = Mathf.Max(0, FishDepth - dt);
                    // Thrash rises fast and fades as the fish tires; heavy fish make long runs, darters zigzag.
                    float tire = Mathf.Clamp01(PhaseTime / Mathf.Max(.1f, HookedSeconds));
                    Thrash = Mathf.Clamp01((.55f + .45f * Mathf.Abs(Mathf.Sin(wobble * (Style == FishStyle.Darter ? 13 : 7)))) * (1.1f - tire));
                    if (nextJump >= 0 && PhaseTime >= nextJump) { Jump = true; nextJump = Roll(.5f) ? PhaseTime + Range(.5f, .9f) : -1f; }
                    float run = Style == FishStyle.Darter ? 1.4f : Style == FishStyle.Eel ? .5f : .9f;
                    FishPos += new Vector2(Mathf.Sin(wobble * 9 * run), Mathf.Cos(wobble * 7)) * dt * .4f * run * (1 - tire * .7f);
                    Drift = FishPos * .8f; RodPull = Mathf.Lerp(1f, .75f, tire) + Thrash * .1f; break;
                case FishPhase.Spooked:
                case FishPhase.Gone:
                    FishPos = Vector2.Lerp(from, to, Mathf.Min(1, PhaseTime / .6f)); FishDepth = Mathf.Min(1, FishDepth + dt * 1.5f);
                    Dip = Mathf.Max(0, Dip - dt * 4); RodPull = Mathf.Max(0, RodPull - dt * 4); Drift = Vector2.Lerp(Drift, Vector2.zero, dt * 3); break;
            }
            if (Phase is not (FishPhase.Take or FishPhase.Hooked or FishPhase.Spooked or FishPhase.Gone)) Drift = Vector2.Lerp(Drift, Vector2.zero, dt * 4);
            if (Phase != FishPhase.Take) Tilt = Mathf.MoveTowards(Tilt, 0, dt * 3);
            if (Phase != FishPhase.Hooked) Thrash = Mathf.MoveTowards(Thrash, 0, dt * 3);
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

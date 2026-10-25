using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    public enum CagePhase { Pull, Snag, Sort, Done }

    // One crab cage hauled by the captain (docs/plans/MINIGAMES.md, section 2). Pure logic: the view reads the signals.
    // Pull: tap fast, each tap lifts the cage and the rope slips back between taps. Snag: about one cage in three
    // catches on rock halfway up; drag the way the arrow shows to free it. Sort: the crabs come onto the board one at a
    // time; flick up to keep, down to throw back. Undersize and berried crabs must go back.
    public class CageModel
    {
        public struct Crab { public float Kg; public bool Undersize, Berried; public bool Keeper => !Undersize && !Berried; }
        public struct Sorted { public Crab Crab; public bool Kept; public bool Right => Kept == Crab.Keeper; }

        public const float TapLift = .085f, Slip = .12f, SnagAt = .5f, WrongDragLock = 1f, SnagGiveUp = 3f;
        public const float HandSortedBonus = .1f, FinePerBadKeep = .5f; // fine: half that crab's price

        public CagePhase Phase { get; private set; } = CagePhase.Pull;
        public float Lift { get; private set; }             // 0 on the bottom .. 1 at the rail
        public int SnagDirection { get; private set; }      // -1 drag left, +1 drag right, 0 no snag
        public float Shudder { get; private set; }          // 0..1 rope shake while snagged or after a wrong drag
        public float Elapsed { get; private set; }
        public bool Tapped { get; private set; }            // true on the frame a tap lifted the cage
        public readonly List<Crab> Crabs = new();
        public readonly List<Sorted> Results = new();
        public int Index => Results.Count;
        public Crab? Current => Phase == CagePhase.Sort && Index < Crabs.Count ? Crabs[Index] : null;

        readonly bool snags;
        bool snagDone;
        float snagTime, locked;

        public static float LegalKg => Mathf.Lerp(GameData.Get(Species.Crab).MinKg, GameData.Get(Species.Crab).MaxKg, .55f);

        public CageModel(System.Random rng, bool heavier = false)
        {
            snags = rng.NextDouble() < .34;
            SnagDirection = rng.Next(2) == 0 ? -1 : 1;
            var data = GameData.Get(Species.Crab);
            // Most crabs in a pot are under the legal size, as at sea; a sorted cage averages about 1.5 times a crew
            // recovery (one crab) in value, which pays for the captain's time away from the rods.
            int count = 2 + rng.Next(3);
            for (int i = 0; i < count; i++)
            {
                float sample=(float)rng.NextDouble();
                if(heavier)sample=Mathf.Max(sample,(float)rng.NextDouble());
                float kg = Mathf.Lerp(data.MinKg, data.MaxKg, sample);
                Crabs.Add(new Crab { Kg = kg, Undersize = kg < LegalKg, Berried = kg >= LegalKg && rng.NextDouble() < .2 });
            }
        }

        public void Tap(float winchRate = 1)
        {
            if (Phase != CagePhase.Pull || locked > 0) return;
            Lift = Mathf.Min(1, Lift + TapLift * Mathf.Max(1, winchRate)); Tapped = true;
            if (snags && !snagDone && Lift >= SnagAt) { Lift = SnagAt; Phase = CagePhase.Snag; snagTime = 0; }
            else if (Lift >= 1) Phase = CagePhase.Sort;
        }

        // A drag while snagged: dir -1 left, +1 right. Returns true when it freed the cage.
        public bool Drag(int dir)
        {
            if (Phase != CagePhase.Snag || locked > 0) return false;
            if (dir == SnagDirection) { FreeSnag(); return true; }
            locked = WrongDragLock; Shudder = 1; return false;
        }

        // Flick up (keep) or down (throw back) for the crab on the board.
        public void Flick(bool keep)
        {
            if (Current is not { } crab) return;
            Results.Add(new Sorted { Crab = crab, Kept = keep });
            if (Index >= Crabs.Count) Phase = CagePhase.Done;
        }

        public void Tick(float dt)
        {
            Tapped = false; Elapsed += dt;
            locked = Mathf.Max(0, locked - dt);
            Shudder = Phase == CagePhase.Snag ? Mathf.Max(.45f, Shudder - dt * 2) : Mathf.Max(0, Shudder - dt * 3);
            if (Phase == CagePhase.Pull && Lift < 1) Lift = Mathf.Max(snagDone ? SnagAt * .9f : 0, Lift - Slip * dt);
            if (Phase == CagePhase.Snag && (snagTime += dt) >= SnagGiveUp + (locked > 0 ? WrongDragLock : 0)) FreeSnag();
        }

        void FreeSnag() { snagDone = true; Phase = CagePhase.Pull; Lift = SnagAt + TapLift; Shudder = 0; }

        // Sale value of what was kept, relative to the base price: hand-sorted keepers earn the bonus, kept undersize or
        // berried crabs cost a fine. The crew's automatic haul is the reference: every keeper at base price.
        public int Kept => Results.FindAll(r => r.Kept).Count;
        public int ThrownBack => Results.Count - Kept;
        public int Fines => Results.FindAll(r => r.Kept && !r.Crab.Keeper).Count;
        public float PriceMultiplier(Crab crab) => crab.Keeper ? 1 + HandSortedBonus : -FinePerBadKeep;
    }
}

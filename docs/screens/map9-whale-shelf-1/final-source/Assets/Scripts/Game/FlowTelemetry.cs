using System;
using System.Collections.Generic;
namespace Catchline.Game
{
    // Session-only observation: never calls RNG, changes work, or enters save data.
    public sealed class FlowTelemetry
    {
        public enum Kind { Rod, Net, Trap, Stored, Sorted, Chum, PrepInput, DeepLine }
        public struct Entry { public double At; public Kind Type; public float Kg, Value; }
        readonly Queue<Entry> entries = new();
        public double Clock { get; private set; }
        public double CarryBusySeconds { get; private set; }
        public double CarryKg { get; private set; }
        public int CarrySamples { get; private set; }
        public double OutputBusySeconds { get; private set; }
        public int OutputSamples { get; private set; }
        public float ChumKg { get; private set; }
        public float LandedKg { get; private set; }
        public float LostKg { get; private set; }
        public void Reset()
        {
            entries.Clear(); Clock = CarryBusySeconds = CarryKg = 0;
            CarrySamples = OutputSamples = 0; OutputBusySeconds = 0; ChumKg = 0; LandedKg = LostKg = 0;
        }
        public void Tick(float dt, int carriersBusy)
        {
            if (dt <= 0) return;
            Clock += dt; CarryBusySeconds += dt * carriersBusy;
            while (entries.Count > 0 && entries.Peek().At <= Clock - 180) entries.Dequeue();
        }
        public void Record(Kind kind, float kg, float value = 0, bool carried = false)
        {
            if (float.IsNaN(kg) || float.IsInfinity(kg) || kg <= 0) return;
            entries.Enqueue(new Entry { At = Clock, Type = kind, Kg = kg, Value = value });
            if (kind <= Kind.Trap || kind == Kind.DeepLine) LandedKg += kg;
            if (kind == Kind.Chum) ChumKg += kg;
            if (kind == Kind.Stored) OutputSamples++;
            if (carried) { CarryKg += kg; CarrySamples++; }
        }
        public void TickOutput(float dt,int workers) { if(dt>0)OutputBusySeconds+=dt*workers; }
        public float CountRate(Kind kind,float window)
        {
            int count=0; foreach(var e in entries)if(e.At>Clock-window&&e.Type==kind)count++;
            return count*60/(float)Math.Max(1,Math.Min(Clock,window));
        }
        public Entry[] Snapshot() => entries.ToArray();
        public float CarryFishPace => CarrySamples >= 3 && CarryBusySeconds >= 5 ? (float)(CarrySamples*60/CarryBusySeconds) : 0;
        public float OutputFishPace => OutputSamples >= 3 && OutputBusySeconds >= 5 ? (float)(OutputSamples*60/OutputBusySeconds) : 0;
        public void Lose(float kg) { if (kg > 0) LostKg += kg; }
        public float Sum(Kind kind, float window, bool value = false)
        {
            double start = Clock - window; double sum = 0;
            foreach (var e in entries) if (e.At > start && e.Type == kind) sum += value ? e.Value : e.Kg;
            return (float)sum;
        }
        public float Rate(Kind kind, float window, bool value = false)
            => Sum(kind, window, value) * 60 / (float)Math.Max(1, Math.Min(Clock, window));
        // Observed kg per worker busy minute. Includes pickup, walking and stow.
        // This is a working-pace estimate, never a guaranteed nameplate capacity.
        public void ResetCarryLearning() { CarryKg = CarryBusySeconds = 0; CarrySamples = OutputSamples = 0; OutputBusySeconds = 0; }
        public float CarryPace => CarrySamples >= 3 && CarryBusySeconds >= 5
            ? (float)(CarryKg * 60 / CarryBusySeconds) : 0;
        public static int Pressure(float demand, float capacity, bool blocked, bool warming)
        {
            if (blocked) return 2;
            if (warming || capacity <= 0) return -1;
            if (demand > capacity) return 2;
            // Small tolerance keeps the exact80% boundary stable across Mono/JIT arithmetic.
            return demand >= capacity * .8f - .0001f ? 1 : 0;
        }
    }
}

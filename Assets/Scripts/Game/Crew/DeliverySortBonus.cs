using System.Collections.Generic;
using Catchline.Game.Deck;

namespace Catchline.Game
{
    // A delivery during an existing sort belongs to the next sort. Cancellation spends nothing.
    public sealed class DeliverySortBonus
    {
        readonly Dictionary<Station, int> offers = new();
        readonly Dictionary<Job, int> applied = new();
        int generation;
        public void Offer(Station station) { offers[station] = ++generation; }
        public float Begin(Job job)
        {
            if (!offers.TryGetValue(job.At, out int value)) return 1;
            applied[job] = value;
            return 1.2f;
        }
        public void Complete(Job job)
        {
            if (applied.TryGetValue(job, out int value) && offers.TryGetValue(job.At, out int current) && value == current)
                offers.Remove(job.At);
            applied.Remove(job);
        }
        public void Cancel(Job job) { applied.Remove(job); }
        public void Clear() { offers.Clear(); applied.Clear(); }
    }
}

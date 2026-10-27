using System.Collections.Generic;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        readonly HashSet<Person> netFallbackHands = new();
        bool NetReadyForHand(Person h) => AssignedNet(h) == 0 ? Net == NetState.Ready
            : AssignedNet(h) == 1 && SecondNet == NetState.Ready;
        bool NetsSoakingFor(Person h) => AssignedNet(h) == 0 ? Net == NetState.Soaking
            : AssignedNet(h) == 1 && SecondNet == NetState.Soaking;
        void PreemptNetFallback()
        {
            foreach (var h in new List<Person>(netFallbackHands))
            {
                if (h.Contract?.WorkPreference != DeckhandWork.Nets || CurrentMode != Mode.Fishing)
                { netFallbackHands.Remove(h); continue; }
                if (!NetReadyForHand(h) || h.Carrying != null || IsNetUnloading(h)) continue;
                h.Stop(); netFallbackHands.Remove(h);
            }
        }
    }
}

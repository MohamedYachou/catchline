using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public bool SelectNetLoadout(NetKind kind)
        {
            if (CurrentMode != Mode.Harbour || State.Hull == 0 || Net != NetState.Stowed || NetUnloadActive || NetBasketBlocked) return false;
            State.SelectedNet = kind; SaveGame(); return true;
        }
        public bool DeepNetSelected => State.SelectedNet == NetKind.Deep;
        public float NetCatchKg
        {
            get { float kg = 0; foreach (var f in netFish) kg += f.kg; return kg; }
        }
        // Both net types share one hard mass limit. Richness affects the catch,
        // not equipment capacity; no species is imported from another ground.
        public Vector2 NetWeightRange(int spot, bool deep)
        {
            float target = State.NetCapacityKg * Mathf.Lerp(.85f, 1f, State.Richness[spot]);
            return new Vector2(target * .85f, target);
        }
    }
}

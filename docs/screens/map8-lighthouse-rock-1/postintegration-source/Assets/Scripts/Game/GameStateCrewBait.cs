using UnityEngine;
namespace Catchline.Game
{
    [System.Flags]
    public enum BaitPermission { None = 0, Scraps = 1, Worms = 2, Squid = 4, Chum = 8, All = 15 }
    public partial class GameState
    {
        public BaitPermission SelectDeepLineBait(CrewMember fisher) => Chum>0 && (fisher.BaitPolicy & BaitPermission.Chum)!=0 ? BaitPermission.Chum : BaitPermission.None;
        public bool TakeDeepLineBait(CrewMember fisher)
        {
            if(SelectDeepLineBait(fisher)==BaitPermission.None)return false;
            Chum--;return true;
        }
        public bool CanTakeBait(CrewMember fisher) => SelectBait(fisher) != BaitPermission.None;
        public BaitPermission SelectBait(CrewMember fisher)
        {
            var allowed = fisher?.BaitPolicy ?? BaitPermission.All;
            bool Has(BaitPermission b) => (allowed & b) != 0;
            if (Has(BaitPermission.Chum) && Chum > 0) return BaitPermission.Chum;
            if (Has(BaitPermission.Squid) && Squid > 0 && (UseSquid || Bait <= 0 || !Has(BaitPermission.Worms))) return BaitPermission.Squid;
            if (Has(BaitPermission.Worms) && Bait > 0) return BaitPermission.Worms;
            if (Has(BaitPermission.Squid) && Squid > 0) return BaitPermission.Squid;
            return Has(BaitPermission.Scraps) ? BaitPermission.Scraps : BaitPermission.None;
        }
        public bool TakeBait(CrewMember fisher, out bool squid, out bool chum, out bool scraps)
        {
            var selected = SelectBait(fisher);
            squid = selected == BaitPermission.Squid; chum = selected == BaitPermission.Chum; scraps = selected == BaitPermission.Scraps;
            if (chum) Chum--; else if (squid) Squid--; else if (selected == BaitPermission.Worms) Bait--;
            return selected != BaitPermission.None;
        }
    }
}

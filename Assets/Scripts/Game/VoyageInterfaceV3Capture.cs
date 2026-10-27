using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Native TEST fixtures use the real call builders and answer action, without save I/O.
        bool StageV3RadioEvidence(string screen)
        {
            if (!SessionOnly) return false;
            if (!StageRestaurantDay("new-harbour") || !StageRestaurantDay("new-plan") || !StageRestaurantDay("new-radio-out")) return false;
            if (screen == "kit3-radio-reply")
            {
                if (!AnswerRadio(0)) return false;
                Tick(.6f);
                return RadioOpen == null && radioReply != null;
            }
            if (screen == "kit3-radio-disabled")
            {
                State.Coins = 0;
                RadioOpen = LotteDeal(new System.Random(7));
                radioOpenedAt = SimTime - .6f;
                return !RadioOpen.Options[0].Enabled;
            }
            return false;
        }
    }
}

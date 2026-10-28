using UnityEngine;

namespace Catchline.Game
{
    // Mo's test day (10-28: "a test where I can test the actual 3 phases and the new restaurant"). The editor menu
    // Catchline/Test the restaurant day enters Play on a throwaway save (the real one is never read or written) on the
    // morning of a regular restaurant day: the tutorial behind, one night already played so Mira sets goals and deals
    // night cards, the harbour festival tonight. Out to sea and fishing, home and the market, then the evening service.
    public partial class VoyageGame
    {
        public const string TestDayKey = "Catchline.TestDay";

        static bool TestDayRequested
        {
            get
            {
#if UNITY_EDITOR
                return UnityEditor.SessionState.GetBool(TestDayKey, false);
#else
                return false;
#endif
            }
        }

        void StartTestDay()
        {
#if UNITY_EDITOR
            UnityEditor.SessionState.EraseBool(TestDayKey); // one test per menu press; a plain Play loads the real save again
#endif
            NewGame(); EndIntro(); showTitle = false;
            State.Tutorial = (int)TutStep.Done;
            State.Coins = Mathf.Max(State.Coins, 600);
            restaurantForced = true; // the real game opens the restaurant with the Skiff; the test day sails the rowboat
            if (State.RestaurantNights.Count == 0) State.RestaurantNights.Add("0|300|210|60|30|1|24|6||captain");
            State.RestaurantCards.Add("next=festival");
            RestaurantPhase = DayPhase.Off;
            Debug.Log("[Catchline] TEST DAY: throwaway save, restaurant open, one night played, the festival tonight");
        }
    }
}

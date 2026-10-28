using UnityEngine;

namespace Catchline.Game
{
    // Mo's test day (10-28: "a test where I can test the actual 3 phases and the new restaurant"): the Test build's
    // "Restaurant day" button (and, in the editor, Catchline/Test the restaurant day) starts a save-free game on the
    // morning of a regular restaurant day: the Skiff, the tutorial behind, one night already played so Mira sets goals
    // and deals night cards, the harbour festival tonight. Out to sea and fishing, home and the market, then the service.
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
            NewGame(); EndIntro();
            State.Hull = 1; State.Fuel = State.FuelCapacity; State.Bait = 30; State.GrantTrialCards(); RebuildBoat(); // the Skiff opens Mira's
            State.Tutorial = (int)TutStep.Done;
            State.Coins = Mathf.Max(State.Coins, 600);
            if (State.RestaurantNights.Count == 0) State.RestaurantNights.Add("0|300|210|60|30|1|24|6||captain");
            State.RestaurantCards.Add("next=festival");
            RestaurantPhase = DayPhase.Off;
            confirmReset = showSettings = paused = showTitle = false;
            Toast("Test · restaurant day · nothing is saved.");
            Debug.Log("[Catchline] TEST DAY: throwaway save, restaurant open, one night played, the festival tonight");
        }
    }
}

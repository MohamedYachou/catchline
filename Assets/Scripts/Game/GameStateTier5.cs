using UnityEngine;
namespace Catchline.Game
{
    public partial class GameState
    {
        public const int Tier5Cost = 18000; // Initial tuning, not a promised voyage count.
        public bool CanRefitTier5 => Hull == 3 && Coins >= Tier5Cost;
        public bool RefitTier5()
        {
            if (!CanRefitTier5) return false;
            Coins -= Tier5Cost; Hull = 4; Fuel = FuelCapacity;
            SecondNetOwned = true; SecondNetEnabled = false;
            EnsureCrewRoleOffers(); return true;
        }
    }
}

using System;
using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    public partial class GameState
    {
        public const int Tier5Cost = 18000; // Initial tuning, not a promised voyage count.
        public float[] Tier5Condition = Enumerable.Repeat(100f, 8).ToArray();
        public bool[] Tier5Broken = new bool[8];
        public bool CanRefitTier5 => Hull == 3 && Coins >= Tier5Cost;
        public bool RefitTier5()
        {
            if (!CanRefitTier5) return false;
            Coins -= Tier5Cost; Hull = 4; Fuel = FuelCapacity;
            SecondNetOwned = true; SecondNetEnabled = false;
            EnsureCrewRoleOffers(); return true;
        }
        public void RestoreTier5Condition(bool present, float[] condition, bool[] broken)
        {
            for (int i = 0; i < 8; i++)
            {
                Tier5Condition[i] = present && condition != null && i < condition.Length && !float.IsNaN(condition[i]) && !float.IsInfinity(condition[i]) ? Mathf.Clamp(condition[i],0,100) : 100;
                Tier5Broken[i] = present && broken != null && i < broken.Length && broken[i];
            }
        }
        public static float Tier5FaultChance(float condition) => .002f + Mathf.Pow(1 - Mathf.Clamp01(condition / 100), 3) * .35f;
    }
}

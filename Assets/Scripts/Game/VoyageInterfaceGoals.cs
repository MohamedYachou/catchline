using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Goal/hold/bait presentation is shared with the live ground card; status uses its live slab.
        void InterfaceReferenceGoals() => InterfaceV3(InterfaceVoyageStatus);

        string ReferenceCoinBalance()
        {
            // Preserve the reference's full balance at ordinary values. Large
            // balances use conventional units rather than overflowing the card.
            // Decimal also handles int.MinValue without an Abs(int) overflow.
            decimal value = State.Coins;
            decimal magnitude = System.Math.Abs(value);
            if (magnitude >= 1000000000m) return (value / 1000000000m).ToString("0.##") + "B";
            if (magnitude >= 100000000m) return (value / 1000000m).ToString("0") + "M";
            if (magnitude >= 1000000m) return (value / 1000000m).ToString("0.#") + "M";
            if (magnitude >= 10000m) return (value / 1000m).ToString("0") + "k";
            return State.Coins.ToString("N0");
        }
    }
}

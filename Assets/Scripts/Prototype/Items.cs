using UnityEngine;

namespace Catchline.Prototype
{
    public enum ItemType { FullPot, EmptyPot, Crab, BandedCrab }

    // Look of each item when it sits in a pile or is carried.
    public static class Items
    {
        public static Color ColorOf(ItemType t) => t switch
        {
            ItemType.FullPot => new Color(0.42f, 0.28f, 0.16f),
            ItemType.EmptyPot => new Color(0.66f, 0.54f, 0.38f),
            ItemType.Crab => new Color(0.86f, 0.28f, 0.18f),
            _ => new Color(0.98f, 0.62f, 0.12f),
        };

        public static Vector3 SizeOf(ItemType t) => t switch
        {
            ItemType.FullPot or ItemType.EmptyPot => new Vector3(0.34f, 0.24f, 0.34f),
            _ => new Vector3(0.2f, 0.09f, 0.16f),
        };

        // Items per layer in a pile: pots stack straight up, crabs spread 2x2.
        public static int PerLayer(ItemType t) => t is ItemType.FullPot or ItemType.EmptyPot ? 1 : 4;
    }
}

using UnityEngine;

namespace Catchline.GeminiUI
{
    public enum CatchTier
    {
        Tier1_Common = 1,        // White/Grey Glow - Normal size common
        Tier2_TrophyCommon = 2,  // Emerald Green Glow - Oversized common
        Tier3_Rare = 3,          // Sapphire Blue Glow - Normal size rare
        Tier4_GiantRare = 4,     // Royal Purple Glow - Oversized rare
        Tier5_Legendary = 5,     // Sunburst Gold Glow - Smaller sharks / rays / special events
        Tier6_Leviathan = 6      // Abyssal Red Glow - Massive sharks / whales / world bosses
    }

    [CreateAssetMenu(fileName = "NewFishSpecies", menuName = "Catchline/Gemini/Fish Species Data")]
    public class FishSpeciesData : ScriptableObject
    {
        public string speciesName;
        public CatchTier tier = CatchTier.Tier1_Common;
        public Sprite fish3DSprite;
        public GameObject optional3DModelPrefab;
        public float minWeightKg = 0.5f;
        public float maxWeightKg = 5.0f;
        public float minLengthCm = 20f;
        public float maxLengthCm = 60f;
        public int baseGoldValue = 50;
        public string specialTag = "STANDARD SIZE";
        public string subtitleNote = "Coastal Catch";
    }
}

using UnityEngine;

namespace Catchline.Game
{
    // Pack textures are retained through the existing ArtLibrary; there is no second UI/data system.
    public static class GeminiUiSkin
    {
        public static string Asset(string original) => original switch
        {
            "fish-mackerel" => "Tier1_Mackerel",
            "fish-cod" => "Tier2_TrophyCod",
            "fish-goldenpuffer" => "Tier3_GoldenPuffer",
            "fish-spottedeagleray" => "Tier4_SpottedEagleRay",
            "fish-apexreefshark" => "Tier5_ApexReefShark",
            "fish-goldtipshark" => "Tier5_GoldTipShark",
            "fish-abyssalgreatwhite" => "Tier6_AbyssalGreatWhite",
            "fish-abyssalleviathan" => "Tier6_AbyssalLeviathan",
            _ => null
        };
        // Pack PNGs include wide transparent margins. UV-trim the sprite at runtime;
        // retaining those margins in a9-slice collapses its centre into a thin sliver.
        public static Rect SpriteRect(Texture2D texture) => texture.name switch
        {
            "ActionButton_NavyPrimary" => new Rect(16, 8, 196, 81),
            "BottomDock_ActiveTab_Squircle" => new Rect(16, 8, 180, 109),
            "BottomDock_MainBar" => new Rect(16, 8, 776, 127),
            "ProgressBar_Fill_Emerald" => new Rect(22, 8, 217, 33),
            "ProgressBar_Fill_OceanBlue" => new Rect(22, 8, 217, 33),
            "ProgressBar_Track_Recessed" => new Rect(21, 8, 227, 39),
            "TopBar_DayMoney_Pill" => new Rect(16, 8, 436, 93),
            "TopBar_HoldCapacity_Pill" => new Rect(16, 8, 346, 93),
            "TopCenter_ZoneLocation_Pill" => new Rect(18, 8, 322, 73),
            "Tier1_Mackerel" => new Rect(58, 62, 412, 147),
            "Tier2_TrophyCod" => new Rect(58, 32, 412, 204),
            "Tier3_GoldenPuffer" => new Rect(190, 36, 388, 311),
            "Tier4_SpottedEagleRay" => new Rect(97, 36, 574, 312),
            "Tier5_ApexReefShark" => new Rect(86, 36, 596, 312),
            "Tier5_GoldTipShark" => new Rect(86, 36, 596, 312),
            "Tier6_AbyssalGreatWhite" => new Rect(86, 36, 596, 312),
            "Tier6_AbyssalLeviathan" => new Rect(170, 36, 428, 312),
            "fish-abyssalgreatwhite" => new Rect(86, 36, 596, 312),
            "fish-abyssalleviathan" => new Rect(170, 36, 428, 312),
            "fish-apexreefshark" => new Rect(86, 36, 596, 312),
            "fish-atlanticswordfish" => new Rect(74, 54, 620, 276),
            "fish-bluespottedstingray" => new Rect(106, 36, 556, 312),
            "fish-cod" => new Rect(58, 32, 412, 204),
            "fish-conger" => new Rect(58, 92, 408, 75),
            "fish-flyingfish" => new Rect(74, 51, 620, 282),
            "fish-giantdevilmanta" => new Rect(171, 36, 426, 312),
            "fish-giantsquid" => new Rect(74, 107, 620, 170),
            "fish-goldenpuffer" => new Rect(190, 36, 388, 311),
            "fish-goldtipshark" => new Rect(86, 36, 596, 312),
            "fish-herring" => new Rect(58, 71, 412, 133),
            "fish-lionfish" => new Rect(149, 36, 470, 311),
            "fish-mackerel" => new Rect(58, 62, 412, 147),
            "fish-oceansunfish" => new Rect(301, 36, 166, 312),
            "fish-pelagicthreshershark" => new Rect(74, 54, 619, 276),
            "fish-plaice" => new Rect(62, 11, 408, 234),
            "fish-pollock" => new Rect(58, 62, 412, 145),
            "fish-redmullet" => new Rect(58, 27, 412, 199),
            "fish-scallopedhammerhead" => new Rect(195, 36, 378, 312),
            "fish-seabass" => new Rect(58, 40, 412, 197),
            "fish-spottedeagleray" => new Rect(97, 36, 574, 312),
            "fish-turbot" => new Rect(94, 5, 341, 246),
            "fish-whiting" => new Rect(58, 69, 412, 130),
            "fish-yellowfintuna" => new Rect(150, 38, 467, 308),
            "fish-barracuda" => new Rect(77, 107, 615, 170),
            "fish-mahimahi" => new Rect(76, 58, 615, 268),
            "fish-monkfish" => new Rect(135, 38, 498, 308),
            _ => new Rect(0,0,texture.width,texture.height)
        };
        public static string Card(CatchTier tier) => Stem(tier) + "_EmptyCardTemplate";
        public static string Glow(CatchTier tier) => Stem(tier) + "_GlowBurst";
        static string Stem(CatchTier tier) => tier switch
        {
            CatchTier.BigCommon => "Tier2_TrophyCommon", CatchTier.Rare => "Tier3_Rare",
            CatchTier.BigRare => "Tier4_GiantRare", CatchTier.Legendary => "Tier5_Legendary",
            CatchTier.Mythical => "Tier6_Leviathan", _ => "Tier1_Common"
        };
    }
}

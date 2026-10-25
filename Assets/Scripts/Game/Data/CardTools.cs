using System;
using System.Collections.Generic;

namespace Catchline.Game
{
    // Crew tools (spec section 4): equipment cards from chests that speed up one job. Append only (saved as ints).
    public enum ToolKind { Rod, Reel, NetNeedle, BaitKnife, Gloves, Gaff, FilletKnife, Boots, WinchHandle, OilCan, Toolbelt, Compass, Binoculars, Charts }

    [Serializable]
    public class ToolState
    {
        public int Uid;            // unique per save, never 0
        public ToolKind Kind;
        public CardRarity Rarity;
    }

    public static class ToolInfo
    {
        public static readonly ToolKind[] All = (ToolKind[])Enum.GetValues(typeof(ToolKind));

        public static CardRole Class(ToolKind kind) => kind switch
        {
            ToolKind.Rod or ToolKind.Reel or ToolKind.NetNeedle or ToolKind.BaitKnife => CardRole.Fisher,
            ToolKind.Gloves or ToolKind.Gaff or ToolKind.FilletKnife or ToolKind.Boots => CardRole.Deckhand,
            ToolKind.WinchHandle or ToolKind.OilCan or ToolKind.Toolbelt => CardRole.Engineer,
            _ => CardRole.Navigator,
        };

        public static string Name(ToolKind kind) => kind switch
        {
            ToolKind.NetNeedle => "Net needle",
            ToolKind.BaitKnife => "Bait knife",
            ToolKind.FilletKnife => "Fillet knife",
            ToolKind.WinchHandle => "Winch handle",
            ToolKind.OilCan => "Oil can",
            _ => kind.ToString(),
        };

        // What the bonus speeds up (or, for the oil can and compass, slows down).
        public static string Job(ToolKind kind) => kind switch
        {
            ToolKind.Rod => "strike window and reeling",
            ToolKind.Reel => "reeling",
            ToolKind.NetNeedle => "setting and hauling nets",
            ToolKind.BaitKnife => "baiting pots and lines",
            ToolKind.Gloves => "sorting",
            ToolKind.Gaff => "carrying fish",
            ToolKind.FilletKnife => "table work",
            ToolKind.Boots => "walking",
            ToolKind.WinchHandle => "winching nets and pots",
            ToolKind.OilCan => "fuel use (less)",
            ToolKind.Toolbelt => "repairs and engine work",
            ToolKind.Compass => "ground thinning (slower)",
            ToolKind.Binoculars => "bite speed (half rate)",
            _ => "travel speed",
        };

        // UI art id: v2-tool-rod, v2-tool-net-needle, ...
        public static string Icon(ToolKind kind) => "v2-tool-" + Name(kind).ToLowerInvariant().Replace(' ', '-');

        // Crew use tools of their own class; the captain (role null) uses every class except navigator.
        public static bool CanUse(CardRole? role, ToolKind kind) => role.HasValue ? Class(kind) == role.Value : Class(kind) != CardRole.Navigator;

        public static bool CanMerge(ToolState a, ToolState b) =>
            a != null && b != null && a.Uid != b.Uid && a.Kind == b.Kind && a.Rarity == b.Rarity && a.Rarity < CardRarity.Mythic;

        // Bonus to one tool kind's job from a set of equipped tools: matching tools add up, capped at +50%.
        public static float Bonus(IEnumerable<ToolState> equipped, ToolKind kind)
        {
            float sum = 0f;
            if (equipped != null)
                foreach (var t in equipped)
                    if (t != null && t.Kind == kind) sum += CardProgression.ToolBonus(t.Rarity);
            return Math.Min(sum, CardProgression.ToolBonusCap);
        }
    }
}

using UnityEngine;

namespace Catchline.Game
{
    // One measured coordinate/type/art contract for BOTH sides of Mo's fish.png HUD.
    public static class FishReferenceStyle
    {
        public const float Width = 1672, Height = 941;
        public enum PanelKind { Status, Goal, Crew, Row, Toolbar }
        public enum Icon { Sun, Coin, Target, Crate, Crew, Menu, Wheel, Net, Fish, Badge, Bullet }
        public static readonly Color Ink = new Color32(4, 53, 78, 255);
        public static readonly Color AmountInk = new Color32(56, 66, 73, 255);
        public static readonly Color Secondary = new Color32(61, 85, 105, 255);
        public static string Panel(PanelKind kind) => "panel-" + kind.ToString().ToLowerInvariant();
        public static string IconName(Icon kind) => kind == Icon.Bullet ? "title-dot" : "icon-" + kind;
        public static string Caption(string value) => value switch
        {
            "Crew Roles" => "caption-Crew-Roles",
            "Crew" => "caption-Crew",
            "Current Goal" => "caption-Current-Goal",
            "Captain" => "caption-Captain",
            "Deckhand" => "caption-Deckhand",
            "Fisher" => "caption-Fisher",
            _ => null
        };
    }
}

using System;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        // Scope the restaurant kit to migrated HUD families; older screens keep their own presentation.
        void InterfaceV3(Action draw)
        {
            var kit = coastalUi.Kit;
            var display = coastalUi.DisplayOverride;
            var body = coastalUi.BodyOverride;
            coastalUi.Kit = "v3-";
            coastalUi.DisplayOverride = restaurantDisplay ??= Resources.Load<Font>("Fonts/Fredoka-Bold");
            coastalUi.BodyOverride = restaurantBody ??= Resources.Load<Font>("Fonts/Fredoka-SemiBold");
            try { draw(); }
            finally
            {
                coastalUi.Kit = kit;
                coastalUi.DisplayOverride = display;
                coastalUi.BodyOverride = body;
            }
        }
    }
}

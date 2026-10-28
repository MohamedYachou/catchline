using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        Rect ReferenceRect(float x, float y, float width, float height)
        {
            float scale = ih / FishReferenceStyle.Height;
            return new Rect(x * scale, y * scale, width * scale, height * scale);
        }
        Rect ReferenceRightRect(float x, float y, float width, float height)
        {
            var r = ReferenceRect(x, y, width, height);
            r.x += iw - FishReferenceStyle.Width * ih / FishReferenceStyle.Height;
            return r;
        }
        static float ReferenceRowTop(int i) => i switch { 0 => 130, 1 => 215, 2 => 301, 3 => 387, 4 => 475, _ => 562 + (i - 5) * 86 };
        float ReferenceCrewBottom => (ReferenceRowTop(Mathf.Max(1, People.Count()) - 1) + 91) * ih / FishReferenceStyle.Height;
        // Compatibility entries use the finished responsive HUD components and their live data.
        // The fixed reference-coordinate drawings are retired; the shared geometry helpers remain.
        void InterfaceReferenceCrew() => InterfaceV3(InterfaceVoyageCrewRail);
        void InterfaceReferenceSupplies() => InterfaceV3(InterfaceVoyageGround);
    }
}

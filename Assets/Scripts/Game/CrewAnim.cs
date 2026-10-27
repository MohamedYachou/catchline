using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // Crew puppets are the free Quaternius human bodies; their animation comes from the free Quaternius
    // Universal Animation Library (UAL1_Standard), which shares the exact same 65-bone skeleton, so each
    // clip samples straight onto a crew rig. The game asks for gameplay poses ("Walk", "Bait", "Pour"…);
    // this maps those names onto the library's clip names. Fill() also keeps the raw clip names, so any
    // code that looks a clip up by its UAL name still finds it.
    public static class CrewAnim
    {
        // game pose -> UAL clip base name (after the "Armature|" prefix is split off)
        static readonly Dictionary<string, string> Map = new()
        {
            ["Idle"] = "Idle_Loop", ["Wait"] = "Idle_Loop",
            ["Walk"] = "Walk_Loop", ["Carry"] = "Walk_Loop", ["CarryPlate"] = "Walk_Loop",
            ["Row"] = "Sitting_Idle_Loop", ["Sit"] = "Sitting_Idle_Loop", ["Eat"] = "Sitting_Idle_Loop",
            ["Bait"] = "Interact", ["Cast"] = "Interact", ["Reel"] = "Interact",
            ["Chop"] = "Interact", ["Wash"] = "Interact", ["Cook"] = "Interact",
            ["Wipe"] = "Interact", ["Pour"] = "Interact",
            ["Stow"] = "PickUp_Table",
            ["TakeOrder"] = "Idle_Talking_Loop", ["Greet"] = "Idle_Talking_Loop",
        };

        public static void Fill(Dictionary<string, AnimationClip> dict, AnimationClip[] clips)
        {
            if (clips == null) return;
            var byName = new Dictionary<string, AnimationClip>();
            foreach (var c in clips)
            {
                if (c == null) continue;
                var parts = c.name.Split('|');
                byName[parts[parts.Length - 1]] = c;
            }
            foreach (var kv in byName) dict[kv.Key] = kv.Value;              // raw UAL names (and old blob pose keys)
            foreach (var kv in Map)                                          // overlay gameplay pose aliases
                if (byName.TryGetValue(kv.Value, out var clip)) dict[kv.Key] = clip;
        }
    }
}

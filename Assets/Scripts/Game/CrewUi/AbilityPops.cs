using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // At sea, a crew ability that fires floats its name above that crew member's head in their rarity colour;
    // timed windows (Mira's call, Olaf's push...) keep a small chip with the seconds left.
    public partial class VoyageGame
    {
        readonly Dictionary<string, float> abilityPopSeen = new();
        const float PopSeconds = 1.8f;

        void InterfaceAbilityPops()
        {
            if (Abilities == null || CurrentMode == Mode.Harbour) return;
            float now = Abilities.Time;
            foreach (var p in People)
            {
                string card = p?.Contract?.CardId;
                if (string.IsNullOrEmpty(card) || p.Root == null) continue;
                var def = Cards.ById(card); var state = CardRoster.Find(State.Roster, card);
                if (def == null || state == null) continue;
                Vector3 view = Cam.WorldToViewportPoint(p.Root.position + Vector3.up * 1.9f);
                if (view.z <= 0 || view.x < 0 || view.x > 1 || view.y < 0 || view.y > 1) continue;
                float x = view.x * iw, y = (1 - view.y) * ih, stack = 0;
                foreach (var s in ActiveAbilities(p))
                {
                    var a = FindAbility(def, s.AbilityId);
                    if (a == null || a == def.Passive || a == def.Trait) continue;
                    var col = RarityColour(a.Unlock);
                    float age = s.LastFired < 0 ? 99 : now - s.LastFired;
                    string id = "pop/" + s.AbilityId;
                    if (age < PopSeconds)
                    {
                        if (!abilityPopSeen.TryGetValue(s.AbilityId, out float seen) || seen != s.LastFired)
                        { abilityPopSeen[s.AbilityId] = s.LastFired; audio?.Play(VoyageAudio.Cue.Select, .35f); }
                        float k = age / PopSeconds, rise = Ease.OutCubic(k) * 34, alpha = 1 - Ease.Clamp((k - .7f) / .3f);
                        AbilityChip(id, x, y - stack - rise, a.Name, col, alpha, 1 + .15f * Ease.Pulse(Mathf.Clamp01(k / .2f)));
                        stack += 40;
                    }
                    else if (s.Active && s.Until > now)
                    {
                        AbilityChip(id, x, y - stack, $"{a.Name} {Mathf.CeilToInt(s.Until - now)}s", col, .85f, 1);
                        stack += 40;
                    }
                }
            }
        }

        static AbilityDef FindAbility(CardDef def, string id)
        {
            foreach (var a in def.Abilities) if (a.Id == id) return a;
            return null;
        }

        void AbilityChip(string id, float x, float y, string text, Color col, float alpha, float scale)
        {
            float h = compactInterface ? 30 : 36, w = Mathf.Clamp(text.Length * (compactInterface ? 8.5f : 10.5f) + 40, 90, 320);
            var r = Centered(x, y - h / 2, w, h);
            var chip = coastalUi.Group(id, r);
            coastalUi.Sliced(id + "/bg", new Rect(0, 0, w, h), "v2-pill-cream", chip, Tint(Color.white, alpha));
            coastalUi.Sliced(id + "/dot", new Rect(6, 6, h - 12, h - 12), "v2-pill-cream", chip, Tint(col, alpha));
            coastalUi.Text(id + "/text", new Rect(h, 0, w - h - 8, h), text, Skin.Type.Small, Tint(Skin.Ink, alpha), TextAnchor.MiddleLeft, chip);
            coastalUi.Pose(id, 0, scale);
        }
    }
}

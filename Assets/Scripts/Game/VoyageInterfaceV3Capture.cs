using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        bool captureV3Art;

        // This sheet exists only in the save-isolated native capture path, never in the player flow.
        void DrawV3ArtEvidence()
        {
            if (!SessionOnly) return;
            coastalUi.Begin(interfaceWidth, interfaceHeight, 1, new Rect(0, 0, interfaceWidth, interfaceHeight), interfaceDensity);
            InterfaceV3(() =>
            {
                coastalUi.Box("kit3/art/sea", new Rect(0, 0, iw, ih), "", Palette.Hex("467584"));
                coastalUi.Text("kit3/art/title", new Rect(24, 10, iw - 48, 44), "Day at sea · kit 2", Skin.Type.Display, Skin.Cream);
                float h = Mathf.Min(compactInterface ? 230 : 300, ih - 170), w = h * .75f, gap = 12, right = 24 + (w + gap) * 3;
                coastalUi.Box("kit3/art/paper", new Rect(16, 60, right - 24, h + 18), "v3-slab");
                string[] keys = { "easy", "medium", "hard" }, labels = { "Easy", "Medium", "Hard" };
                for (int i = 0; i < 3; i++)
                {
                    float x = 24 + i * (w + gap), y = 68;
                    coastalUi.Art("kit3/art/card/" + i, new Rect(x, y, w, h), "v3-daycard-" + keys[i]);
                    coastalUi.Text("kit3/art/card-label/" + i, new Rect(x + w * .1f, y + h * .206f, w * .8f, h * .107f), labels[i], Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleCenter);
                    coastalUi.Text("kit3/art/card-copy/" + i, new Rect(x + w * .125f, y + h * .67f, w * .75f, h * .2f), (i + 1) + (i == 0 ? " stop" : " stops"), Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter);
                }
                float rw = iw - right - 24;
                coastalUi.KitSliceV3("kit3/art/banner", new Rect(right, 65, rw, 115), "v3-arrival-banner", new Vector4(132, 56, 132, 84));
                coastalUi.Text("kit3/art/arrival", new Rect(right + 70, 90, rw - 140, 54), "Back in port", Skin.Type.Display, Skin.Ink, TextAnchor.MiddleCenter);
                coastalUi.KitSliceV3("kit3/art/dash", new Rect(right + 45, 210, rw - 90, 24), "v3-route-dash", new Vector4(56, 16, 56, 16));
                coastalUi.Art("kit3/art/pin", new Rect(right + 10, 179, 76, 80), "v3-route-pin");
                coastalUi.Text("kit3/art/number", new Rect(right + 31, 191, 34, 32), "2", Skin.Type.Number, Skin.Ink, TextAnchor.MiddleCenter);
                coastalUi.Art("kit3/art/done", new Rect(iw - 106, 179, 76, 80), "v3-stop-done");
                coastalUi.Art("kit3/art/fuel", new Rect(right + (rw - 220) / 2, 253, 220, 83), "v3-fuel-chip");
                coastalUi.Text("kit3/art/fuel-value", new Rect(right + (rw - 220) / 2 + 74, 269, 129, 48), "70%", Skin.Type.Number, Skin.Ink, TextAnchor.MiddleCenter);
                string[] prep = { "knife", "ice", "crate", "pan" };
                float s = Mathf.Min(100, ih - h - 92), start = (iw - (s + 24) * 4 + 24) / 2;
                for (int i = 0; i < prep.Length; i++) coastalUi.Art("kit3/art/prep/" + i, new Rect(start + i * (s + 24), ih - s - 14, s, s), "v3-prep-" + prep[i]);
            });
            coastalUi.End();
        }

        bool StageV3KitEvidence(string screen)
        {
            if (!SessionOnly) return false;
            if (screen is "kit3-pause" or "kit3-settings-pause")
            {
                if (!StageUiV2("voyage")) return false;
                paused = true; showTitle = false; showSettings = screen == "kit3-settings-pause";
                return true;
            }
            if (screen == "kit3-reset")
            {
                if (!StageUiV2("title")) return false;
                showSettings = paused = false;
                confirmReset = true;
                return true;
            }
            if (screen is "kit3-shop-grid" or "kit3-supplies" or "kit3-refit" or "kit3-shop-poor")
            {
                if (!StageHarbourEvidence(screen is "kit3-refit" or "kit3-shop-poor" ? "harbour-h0" : "harbour-h4")) return false;
                if (screen == "kit3-shop-poor") State.Coins = 0;
                OpenShop(screen == "kit3-supplies" ? HudTab.Supplies : HudTab.Chandlery);
                if (screen == "kit3-refit") shopSelection[HudTab.Chandlery] = "refit";
                return panelOpen;
            }
            return false;
        }

        // Native TEST fixtures use the real call builders and answer action, without save I/O.
        bool StageV3RadioEvidence(string screen)
        {
            if (!SessionOnly) return false;
            if (!StageRestaurantDay("new-harbour") || !StageRestaurantDay("new-plan") || !StageRestaurantDay("new-radio-out")) return false;
            if (screen == "kit3-radio-reply")
            {
                if (!AnswerRadio(0)) return false;
                Tick(.6f);
                return RadioOpen == null && radioReply != null;
            }
            if (screen == "kit3-radio-disabled")
            {
                State.Coins = 0;
                RadioOpen = LotteDeal(new System.Random(7));
                radioOpenedAt = SimTime - .6f;
                return !RadioOpen.Options[0].Enabled;
            }
            return false;
        }
    }
}

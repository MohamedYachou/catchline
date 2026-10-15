using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // Title screen, pause menu, settings, and the "something new here" badges on the shop bubbles.
    public partial class VoyageGame
    {
        bool showTitle = true, paused, showSettings, hadSave, confirmReset;

        // Settings live in PlayerPrefs (per device), not in the save.
        static readonly float[] UiScales = { 0.85f, 1f, 1.15f };
        static readonly string[] UiScaleNames = { "Small", "Normal", "Large" };
        int UiScaleIndex
        {
            get => Mathf.Clamp(PlayerPrefs.GetInt("catchline.uiScale", 1), 0, 2);
            set { PlayerPrefs.SetInt("catchline.uiScale", value); PlayerPrefs.Save(); }
        }
        bool ShowTips
        {
            get => PlayerPrefs.GetInt("catchline.tips", 1) == 1;
            set { PlayerPrefs.SetInt("catchline.tips", value ? 1 : 0); PlayerPrefs.Save(); }
        }

        public bool MenuOpen => showTitle || paused;

        void Quit()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        void Dim(float alpha)
        {
            var prev = GUI.color;
            GUI.color = new Color(0.05f, 0.14f, 0.2f, alpha);
            GUI.DrawTexture(new Rect(0, 0, VW, 720f), Texture2D.whiteTexture);
            GUI.color = prev;
        }

        bool MenuButton(Rect r, string label, GUIStyle style = null) => GUI.Button(r, label, style ?? Ui.Btn);

        // ---- title ----------------------------------------------------------------------------

        void DrawTitle()
        {
            Dim(0.45f);
            if (showSettings) { DrawSettings(); return; }
            float w = 440f, x = VW / 2f - w / 2f;
            var card = new Rect(x, 110f, w, 470f);
            GUI.Box(card, GUIContent.none, Ui.Panel);
            GUI.Label(new Rect(card.x, card.y + 30, w, 70), "Catchline", Ui.LogoStyle);
            GUI.Label(new Rect(card.x + 30, card.y + 104, w - 60, 40), "Fish by hand. Hire a crew. Automate the boat.", Ui.MutedCenter);

            float y = card.y + 170, bw = w - 80, bx = card.x + 40;
            if (hadSave)
            {
                if (MenuButton(new Rect(bx, y, bw, 64), $"Continue\n<size=13>Voyage {State.Voyage} · {State.Coins} coins</size>")) showTitle = false;
                y += 76;
                if (MenuButton(new Rect(bx, y, bw, 54), confirmReset ? "Tap again: wipe the save" : "New game", confirmReset ? Ui.Btn : Ui.BtnAlt))
                {
                    if (confirmReset)
                    {
                        NewGame();
                        hadSave = false;
                        confirmReset = false;
                        showTitle = false;
                    }
                    else confirmReset = true;
                }
            }
            else if (MenuButton(new Rect(bx, y, bw, 64), "Play")) showTitle = false;
            y += hadSave ? 66 : 76;
            if (MenuButton(new Rect(bx, y, bw, 48), "Settings", Ui.Tab)) showSettings = true;
            y += 58;
            if (MenuButton(new Rect(bx, y, bw, 48), "Quit", Ui.Tab)) Quit();
            GUI.Label(new Rect(card.x, card.yMax - 34, w, 20), "Build 1 · Gull Harbour", Ui.MutedCenter);
        }

        // ---- pause ----------------------------------------------------------------------------

        void DrawPause()
        {
            Dim(0.5f);
            if (showSettings) { DrawSettings(); return; }
            float w = 380f, x = VW / 2f - w / 2f;
            var card = new Rect(x, 150f, w, 380f);
            GUI.Box(card, GUIContent.none, Ui.Panel);
            GUI.Label(new Rect(card.x, card.y + 24, w, 40), "Paused", Ui.TitleCenter);
            float y = card.y + 90, bw = w - 80, bx = card.x + 40;
            if (MenuButton(new Rect(bx, y, bw, 58), "Resume")) paused = false;
            y += 70;
            if (MenuButton(new Rect(bx, y, bw, 48), "Settings", Ui.Tab)) showSettings = true;
            y += 58;
            if (MenuButton(new Rect(bx, y, bw, 48), "Main menu", Ui.Tab))
            {
                paused = false;
                showTitle = true;
                hadSave = true;
                SaveGame();
            }
            y += 58;
            if (MenuButton(new Rect(bx, y, bw, 48), "Quit", Ui.Tab))
            {
                SaveGame();
                Quit();
            }
            if (CurrentMode != Mode.Harbour)
                GUI.Label(new Rect(card.x + 20, card.yMax - 40, w - 40, 30), "Progress saves in the harbour; this voyage's catch is not saved yet.", Ui.MutedCenter);
        }

        // ---- settings ---------------------------------------------------------------------------

        void DrawSettings()
        {
            float w = 460f, x = VW / 2f - w / 2f;
            var card = new Rect(x, 130f, w, 420f);
            GUI.Box(card, GUIContent.none, Ui.Panel);
            GUI.Label(new Rect(card.x, card.y + 22, w, 40), "Settings", Ui.TitleCenter);

            float y = card.y + 84, ix = card.x + 30, iw = w - 60;
            GUI.Label(new Rect(ix, y, iw, 24), "Interface size", Ui.H2);
            y += 32;
            float bw = (iw - 16) / 3f;
            for (int i = 0; i < 3; i++)
                if (GUI.Button(new Rect(ix + i * (bw + 8), y, bw, 44), UiScaleNames[i], UiScaleIndex == i ? Ui.TabOn : Ui.Tab))
                    UiScaleIndex = i;
            y += 62;
            GUI.Label(new Rect(ix, y, iw, 24), "Hints on the water", Ui.H2);
            y += 32;
            if (GUI.Button(new Rect(ix, y, iw, 44), ShowTips ? "On" : "Off", ShowTips ? Ui.TabOn : Ui.Tab)) ShowTips = !ShowTips;
            y += 62;
            GUI.Label(new Rect(ix, y, iw, 24), "Sound and music arrive with the audio pass.", Ui.Mutedish);
            if (GUI.Button(new Rect(ix, card.yMax - 70, iw, 50), "Back", Ui.BtnAlt)) showSettings = false;
        }

        // ---- badges -------------------------------------------------------------------------------

        // True when a shop has something worth a visit: shown as a "!" on its bubble.
        bool ShopHasNews(HudTab tab)
        {
            var s = State;
            switch (tab)
            {
                case HudTab.Market: return s.UnseenSale;
                case HudTab.HarbourMaster:
                    return Enumerable.Range(0, GameData.Spots.Length).Any(i => !s.Known(i) && s.Coins >= GameData.Spots[i].ChartCost)
                           || s.Active.Count < GameData.MaxActiveContracts && s.Offers.Count > 0;
                case HudTab.CrewOffice: return s.CrewCount < s.HullDef.CrewCap && s.Board.Any(c => s.Coins >= c.Fee) && (s.Hull > 0 || s.Has(UpgradeId.RodHolder));
                case HudTab.Chandlery:
                    return s.CanRefit || GameData.Upgrades.Any(u => u.Shop == "Chandlery" && !s.Has(u.Id) && s.Coins >= u.Cost && (!u.Requires.HasValue || s.Has(u.Requires.Value)));
                case HudTab.Supplies:
                    return !s.HasAnyBait || s.Bait + s.Squid < 8 || s.FoodMinutes < s.FoodCapacity * 0.5f || s.Hull > 0 && s.Fuel < GameData.TripFuel(SelectedSpot);
            }
            return false;
        }
    }
}

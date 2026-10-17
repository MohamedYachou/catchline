using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    // Title screen, pause menu, settings, and the "something new here" badges on the shop bubbles.
    public partial class VoyageGame
    {
        bool showTitle = true, paused, showSettings, hadSave, confirmReset;
        int titleBackFrame = -1;

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
            GUI.DrawTexture(new Rect(0, 0, VW, VH), Texture2D.whiteTexture);
            GUI.color = prev;
        }

        bool MenuButton(Rect r, string label, GUIStyle style = null) => GUI.Button(r, label, style ?? Ui.Btn);

        // ---- title ----------------------------------------------------------------------------

        void DrawTitle()
        {
            // HandleInput owns Escape while paused; title settings need their own Back.
            // OnGUI runs several times per frame, so consume the press only once.
            var keyboard = UnityEngine.InputSystem.Keyboard.current;
            if (keyboard != null && keyboard.escapeKey.wasPressedThisFrame && titleBackFrame != Time.frameCount)
            {
                titleBackFrame = Time.frameCount;
                if (showSettings) showSettings = false;
                else confirmReset = false;
            }
            var backdrop = Ui.Tex("title-backdrop");
            if (backdrop != null)
            {
                float drift = Mathf.Sin(Time.unscaledTime * .075f) * 8f;
                GUI.DrawTexture(new Rect(-10f + drift, -6f, VW + 28f, VH + 16f), backdrop, ScaleMode.ScaleAndCrop);
            }
            if (showSettings) { Dim(.35f); DrawSettings(); return; }
            bool compact = VH < 600f;
            float x = compact ? 34f : 52f, w = Mathf.Min(compact ? 354f : 380f, VW - x - 16f);
            var logo = Ui.Tex("logo-catchline");
            var logoRect = new Rect(x - 6f, compact ? 12f : 42f, w + 12f, compact ? 90f : 136f);
            if (logo != null) GUI.DrawTexture(logoRect, logo, ScaleMode.ScaleToFit);
            else GUI.Label(logoRect, "Catchline", Ui.LogoStyle);
            var card = new Rect(x, compact ? 110f : 210f, w, 354f);
            GUI.Box(card, GUIContent.none, Ui.Panel);
            float inset = 26f, bx = card.x + inset, bw = w - inset * 2f;
            GUI.Label(new Rect(bx, card.y + 16f, bw, 38f), confirmReset ? "Start over?" : "Gull Harbour", Ui.TitleCenter);
            if (confirmReset)
            {
                GUI.Label(new Rect(bx, card.y + 64f, bw, 96f),
                    "Your coins, crew and catch will be erased. This cannot be undone. Settings stay unchanged.", Ui.MutedCenter);
                // Separate, explicit actions: opening this confirmation never deletes data.
                if (MenuButton(new Rect(bx, card.y + 180f, bw, 52f), "Cancel · keep progress", Ui.BtnAlt))
                { confirmReset = false; return; }
                if (MenuButton(new Rect(bx, card.y + 246f, bw, 52f), "Erase & start over", Ui.Tab))
                {
                    NewGame();
                    hadSave = false;
                    confirmReset = showSettings = paused = showTitle = false;
                    return;
                }
                return;
            }
            string welcome = SessionOnly || AutoPlay ? "Test session · progress is not saved."
                : CurrentMode != Mode.Harbour ? "Voyage paused. Quit loses fish aboard."
                : hadSave ? $"Voyage {State.Voyage} · ready in harbour." : "A little boat. A sea of possibilities.";
            GUI.Label(new Rect(bx, card.y + 56f, bw, 48f), welcome, Ui.MutedCenter);
            float y = card.y + 112f;
            string start = CurrentMode != Mode.Harbour ? "Resume voyage" : hadSave ? "Continue in harbour" : "Start in harbour";
            if (MenuButton(new Rect(bx, y, bw, 52f), start))
            { confirmReset = showSettings = paused = showTitle = false; return; }
            y += 60f;
            if (hadSave)
            {
                if (MenuButton(new Rect(bx, y, bw, 48f), "New game", Ui.BtnAlt))
                { confirmReset = true; return; }
                y += 56f;
            }
            if (MenuButton(new Rect(bx, y, bw, 44f), "Settings", Ui.Tab))
            { confirmReset = false; showSettings = true; return; }
            y += 52f;
            if (MenuButton(new Rect(bx, y, bw, 44f), CurrentMode != Mode.Harbour ? "Quit (lose trip)" : "Quit", Ui.Tab)) Quit();
        }
        // ---- pause ----------------------------------------------------------------------------

        void DrawPause()
        {
            Dim(0.5f);
            if (showSettings) { DrawSettings(); return; }
            float w = Mathf.Min(420f, VW - 32f), x = VW / 2f - w / 2f;
            var card = new Rect(x, (VH - 448f) / 2f, w, 448f);
            GUI.Box(card, GUIContent.none, Ui.Panel);
            GUI.Label(new Rect(card.x, card.y + 24, w, 40), "Paused", Ui.TitleCenter);
            float y = card.y + 80, bw = w - 56, bx = card.x + 28;
            if (MenuButton(new Rect(bx, y, bw, 52), "Resume")) { paused = false; return; }
            y += 62;
            if (MenuButton(new Rect(bx, y, bw, 48), "Settings", Ui.Tab)) { showSettings = true; return; }
            y += 58;
            if (MenuButton(new Rect(bx, y, bw, 48), "Main menu", Ui.Tab))
            {
                // Keep the in-memory trip frozen behind the title, including freshness/food.
                paused = true;
                showTitle = true;
                hadSave = true;
                confirmReset = false;
                SaveGame();
                return;
            }
            y += 58;
            if (MenuButton(new Rect(bx, y, bw, 48), CurrentMode != Mode.Harbour ? "Quit (lose trip)" : "Quit", Ui.Tab))
            {
                SaveGame();
                Quit();
            }
            string saveNote = SessionOnly || AutoPlay ? "Test session · progress is not saved."
                : CurrentMode != Mode.Harbour ? "Quitting loses this trip and fish aboard. Return to harbour to save your haul."
                : "Returning to harbour saves your haul. Sell it there to collect your coins.";
            GUI.Label(new Rect(card.x + 28, card.y + 330, w - 56, 96), saveNote, Ui.MutedCenter);
        }

        // ---- settings ---------------------------------------------------------------------------

        void DrawSettings()
        {
            float w = Mathf.Min(460f, VW - 32f), x = VW / 2f - w / 2f;
            var card = new Rect(x, (VH - 448f) / 2f, w, 448f);
            GUI.Box(card, GUIContent.none, Ui.Panel);
            GUI.Label(new Rect(card.x, card.y + 22, w, 40), "Settings", Ui.TitleCenter);

            float y = card.y + 74, ix = card.x + 30, iw = w - 60;
            GUI.Label(new Rect(ix, y, iw, 32), "Text size", Ui.H2);
            y += 32;
            float bw = (iw - 16) / 3f;
            for (int i = 0; i < 3; i++)
                if (GUI.Button(new Rect(ix + i * (bw + 8), y, bw, 44), UiScaleNames[i], UiScaleIndex == i ? Ui.TabOn : Ui.Tab))
                    UiScaleIndex = i;
            y += 56;
            GUI.Label(new Rect(ix, y, iw, 32), "Hints on the water", Ui.H2);
            y += 32;
            if (GUI.Button(new Rect(ix, y, iw, 44), ShowTips ? "Hints: On" : "Hints: Off", ShowTips ? Ui.TabOn : Ui.Tab)) ShowTips = !ShowTips;
            y += 56;
            GUI.Label(new Rect(ix, y, iw, 32), "Coastal sounds", Ui.H2);
            y += 34f;
            if (audio != null)
            {
                float volume = GUI.HorizontalSlider(new Rect(ix, y, iw - 68f, 38f), audio.Volume, 0, 1, Ui.Slider, Ui.SliderThumb);
                if (Mathf.Abs(volume - audio.Volume) > .005f) audio.Volume = volume;
                GUI.Label(new Rect(ix + iw - 62f, y, 62f, 28f), audio.Volume < .01f ? "Off" : $"{audio.Volume * 100:0}%", Ui.Small);
            }
            else GUI.Label(new Rect(ix, y, iw, 38f), "Sound unavailable in this session", Ui.Mutedish);
            if (GUI.Button(new Rect(ix, card.yMax - 66, iw, 48), showTitle ? "Back to main menu" : "Back to pause", Ui.BtnAlt)) showSettings = false;
        }

        // ---- badges -------------------------------------------------------------------------------

        // True when a shop has something worth a visit: shown as a "!" on its bubble.
        bool ShopHasNews(HudTab tab)
        {
            var s = State;
            switch (tab)
            {
                case HudTab.Market: return s.UnsoldCatch.Count > 0 || s.UnseenSale;
                case HudTab.HarbourMaster:
                    return Enumerable.Range(0, GameData.Spots.Length).Any(i => !s.Known(i) && s.Coins >= GameData.Spots[i].ChartCost)
                           || s.Active.Count < GameData.MaxActiveContracts && s.Offers.Count > 0;
                case HudTab.CrewOffice: return s.CrewCount < s.HullDef.CrewCap && s.Board.Any(c => s.Coins >= c.Fee);
                case HudTab.Chandlery:
                    return s.CanRefit || s.CanRefitCompact || GameData.Upgrades.Any(u => u.Shop == "Chandlery" && s.UpgradeAvailable(u.Id) && !s.Has(u.Id) && s.Coins >= s.UpgradeCost(u.Id) && (!u.Requires.HasValue || s.Has(u.Requires.Value)));
                case HudTab.Supplies:
                    // Free scraps always permit fishing. Flag actionable purchases, not a
                    // permanent bait emergency when the player cannot afford supplies.
                    return s.Bait + s.Squid < 8 && (s.Coins >= GameData.BaitPackCost || s.Coins >= GameData.SquidPackCost)
                           || s.Hull > 0 && s.FuelFraction < .5f && s.FuelFillCost > 0 && s.Coins >= s.FuelFillCost
                           || s.Hull > 0 && s.FuelFraction <= .1f && s.Coins >= GameData.FuelPackCost
                           || GameData.Upgrades.Any(u => u.Shop == "Supplies" && s.UpgradeAvailable(u.Id) && !s.Has(u.Id) && s.Coins >= s.UpgradeCost(u.Id) && (!u.Requires.HasValue || s.Has(u.Requires.Value)));
            }
            return false;
        }
    }
}

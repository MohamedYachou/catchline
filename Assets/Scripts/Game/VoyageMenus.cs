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
        bool AutoCarryCatch
        {
            get => PlayerPrefs.GetInt("catchline.autoCarry", 1) == 1;
            set { PlayerPrefs.SetInt("catchline.autoCarry", value ? 1 : 0); PlayerPrefs.Save(); }
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

        // ---- menus (restaurant v3) ----------------------------------------------------------------------

        static readonly float[] VolumeSteps = { 0, .35f, .7f, 1 };
        static readonly string[] VolumeNames = { "Off", "Low", "Medium", "High" };

        // Title, pause, settings and protected confirmations replace the HUD so nothing underneath can be pressed.
        void InterfaceMenus() => InterfaceV3(InterfaceMenusV3);

        void InterfaceMenusV3()
        {
            var keyboard = UnityEngine.InputSystem.Keyboard.current;
            if (showTitle && keyboard != null && keyboard.escapeKey.wasPressedThisFrame && titleBackFrame != Time.frameCount)
            {
                titleBackFrame = Time.frameCount;
                if (showSettings) showSettings = false;
                else confirmReset = false;
            }
            if (showTitle) InterfaceTitle();
            else if (confirmHeadHome) InterfaceHeadHomeConfirmation();
            else if (paused) { coastalUi.Scrim("menu/dim"); if (showSettings) InterfaceSettings(); else InterfacePause(); }
            else if (SimTime < refitUntil) InterfaceRefitFx();
        }

        void InterfaceTitle()
        {
            coastalUi.Backdrop("title/backdrop", "title-backdrop", Mathf.Sin(Time.unscaledTime * .075f) * 8f);
            if (showSettings) { coastalUi.Scrim("title/dim", null, .6f); InterfaceSettings(); return; }
            bool phone = coastalUi.Phone;
            float x = phone ? 28 : 56, w = Mathf.Min(phone ? 360 : 400, iw - x - 16);
            float logoY = phone ? 8 : 40, logoH = phone ? 84 : 132;
            coastalUi.Art("title/logo", new Rect(x - 6, logoY, w + 12, logoH), "logo-catchline");
            float bh = phone ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight, sh = phone ? 48 : 52, gap = 8;
            // The test build opens on a tier chooser instead of Start / New game; it never touches the save.
            bool chooser = SessionOnly && CurrentMode == Mode.Harbour;
            float h = Skin.HeaderBand + 12 + 44 + 8 + (chooser ? (hadSave ? bh + gap : 0) + (sh + gap) * 3 : bh + gap + (hadSave ? sh + gap : 0)) + sh + Skin.SlabPad;
            var card = new Rect(x, Mathf.Min(logoY + logoH + (phone ? 4 : 16), ih - h - 8), w, h);
            coastalUi.SlabV3("title/card", card, "Gull Harbour", true);
            float bx = card.x + Skin.SlabPad, bw = w - Skin.SlabPad * 2, y = card.y + Skin.HeaderBand + 12;
            string welcome = chooser ? "Test build · pick a tier. Nothing is saved."
                : SessionOnly || AutoPlay ? "Test session · progress is not saved."
                : CurrentMode != Mode.Harbour ? "Voyage paused. Quitting loses fish aboard."
                : hadSave ? $"Voyage {State.Voyage} · ready in harbour." : "A little boat. A sea of possibilities.";
            coastalUi.Text("title/welcome", new Rect(bx, y, bw, 44), welcome, Skin.Type.Body, Skin.InkSoft, TextAnchor.MiddleCenter);
            y += 52;
            float half = (bw - gap) / 2;
            if (chooser)
            {
                if (hadSave)
                {
                    coastalUi.Primary("title/start", new Rect(bx, y, bw, bh), "Continue test", () => { confirmReset = showSettings = paused = showTitle = false; MenuSound(); });
                    y += bh + gap;
                }
                for (int i = 0; i < TestTiers.Length; i++)
                {
                    int tier = i;
                    var r = i == TestTiers.Length - 1 && TestTiers.Length % 2 == 1 ? new Rect(bx, y, bw, sh) : new Rect(bx + (i % 2) * (half + gap), y, half, sh);
                    coastalUi.Secondary("title/tier/" + i, r, TestTiers[i], () => { StartTestTier(tier); MenuSound(); });
                    if (i % 2 == 1 || i == TestTiers.Length - 1) y += sh + gap;
                }
            }
            else
            {
                string start = CurrentMode != Mode.Harbour ? "Resume voyage" : hadSave ? "Continue" : "Start in harbour";
                bool fresh = !hadSave && CurrentMode == Mode.Harbour && State.Voyage <= 1;
                coastalUi.Primary("title/start", new Rect(bx, y, bw, bh), start, () => { confirmReset = showSettings = paused = showTitle = false; MenuSound(); if (fresh) BeginFirstVoyage(); });
                y += bh + gap;
                if (hadSave)
                {
                    coastalUi.Secondary("title/new", new Rect(bx, y, bw, sh), "New game", () => { confirmReset = true; MenuSound(); });
                    y += sh + gap;
                }
            }
            coastalUi.Secondary("title/settings", new Rect(bx, y, half, sh), "Settings", () => { confirmReset = false; showSettings = true; MenuSound(); });
            coastalUi.Secondary("title/quit", new Rect(bx + half + gap, y, half, sh), CurrentMode != Mode.Harbour ? "Quit trip" : "Quit", Quit);
            if (confirmReset)
                coastalUi.ModalV3("title/reset", "Start over?", "Your coins, crew and catch will be erased. This cannot be undone. Settings stay unchanged.",
                    "Erase & start over", () =>
                    {
                        // Separate, explicit action: opening this confirmation never deletes data.
                        NewGame();
                        hadSave = false;
                        confirmReset = showSettings = paused = showTitle = false;
                        BeginFirstVoyage();
                    }, "Keep progress", () => confirmReset = false, () => confirmReset = false, null, 560, 320);
        }

        static readonly string[] TestTiers = { "1 · Rowboat", "2 · Skiff", "3 · Compact", "4 · Prep", "5 · Buoy fisher", "Restaurant night" };
        // Test build only: a fresh save-free game on the chosen hull, crewed and stocked for that tier.
        void StartTestTier(int tier)
        {
            if (!SessionOnly) return;
            if (tier == 5)
            {
                // Mo 10-27: straight into an evening at Mira's: the Skiff, a landed catch, then prep, market and service.
                StartTestTier(1);
                if (StageRestaurantDay("day-plan") && StageRestaurantDay("day-prep")) Toast("Test · restaurant night · nothing is saved.");
                return;
            }
            bool started = tier == 2 ? StartNetBoatTrial() : tier == 3 ? StartPrepBoatTrial() : tier == 4 ? StartTier5Trial() : true;
            if (tier < 2)
            {
                NewGame();
                if (tier == 1) { State.Hull = 1; State.Fuel = State.FuelCapacity; State.Bait = 30; State.GrantTrialCards(); RebuildBoat(); }
            }
            if (!started) return;
            confirmReset = showSettings = paused = showTitle = false;
            if (tier == 0) BeginFirstVoyage();
            else Toast($"Test · tier {TestTiers[tier]} · nothing is saved.");
        }

        void InterfacePause()
        {
            bool phone = coastalUi.Phone;
            float bh = phone ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight, sh = phone ? 48 : 52, gap = 8, noteH = phone ? 44 : 56;
            float w = Mathf.Min(440, iw - 32), h = Skin.HeaderBand + 16 + bh + gap + (sh + gap) * 3 + noteH + Skin.SlabPad;
            var card = new Rect((iw - w) / 2, (ih - h) / 2, w, h);
            coastalUi.SlabV3("pause/card", card, "Paused", true);
            float bx = card.x + Skin.SlabPad, bw = w - Skin.SlabPad * 2, y = card.y + Skin.HeaderBand + 16;
            coastalUi.Primary("pause/resume", new Rect(bx, y, bw, bh), "Resume", () => { paused = false; MenuSound(); });
            y += bh + gap;
            coastalUi.Secondary("pause/settings", new Rect(bx, y, bw, sh), "Settings", () => { showSettings = true; MenuSound(); });
            y += sh + gap;
            coastalUi.Secondary("pause/menu", new Rect(bx, y, bw, sh), "Main menu", () =>
            {
                // Keep the in-memory trip frozen behind the title, including freshness/food.
                paused = true; showTitle = true; hadSave = true; confirmReset = false;
                SaveGame();
            });
            y += sh + gap;
            coastalUi.Secondary("pause/quit", new Rect(bx, y, bw, sh), CurrentMode != Mode.Harbour ? "Quit (lose trip)" : "Quit", () => { SaveGame(); Quit(); });
            y += sh + gap;
            string note = SessionOnly || AutoPlay ? "Test session · progress is not saved."
                : CurrentMode != Mode.Harbour ? "Quitting loses this trip and the fish aboard. Return to harbour to keep your haul."
                : "Your progress is saved in harbour.";
            coastalUi.Text("pause/note", new Rect(bx, y, bw, noteH), note, Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleCenter);
        }

        void InterfaceSettings()
        {
            bool phone = coastalUi.Phone;
            float row = phone ? 44 : 52, label = phone ? 24 : 30, gap = phone ? 8 : 14, sh = phone ? 48 : 52;
            int rows = audio != null ? 5 : 4;
            // Five rows (Mira's voice) must still fit a landscape phone.
            if (Skin.HeaderBand + 12 + (label + row + gap) * rows + sh + Skin.SlabPad > ih - 16) { row = 40; label = 20; gap = 4; }
            float w = Mathf.Min(500, iw - 32), h = Skin.HeaderBand + 12 + (label + row + gap) * rows + sh + Skin.SlabPad;
            var card = new Rect((iw - w) / 2, (ih - h) / 2, w, h);
            coastalUi.SlabV3("settings/card", card, "Settings", true);
            float x = card.x + Skin.SlabPad + 4, cw = w - Skin.SlabPad * 2 - 8, y = card.y + Skin.HeaderBand + 12;
            void Row(string id, string title, string[] options, int active, System.Action<int> select)
            {
                coastalUi.Text($"settings/{id}/label", new Rect(x, y, cw, label), title, Skin.Type.Body, Skin.Ink);
                y += label;
                coastalUi.PageSwitchV3($"settings/{id}", new Rect(x, y, cw, row), options, active, i => { select(i); MenuSound(); });
                y += row + gap;
            }
            Row("text", "Text size", UiScaleNames, UiScaleIndex, i => UiScaleIndex = i);
            Row("hints", "Hints on the water", new[] { "Off", "On" }, ShowTips ? 1 : 0, i => ShowTips = i == 1);
            Row("auto-carry", "Auto-carry catch", new[] { "Off", "On" }, AutoCarryCatch ? 1 : 0, i => AutoCarryCatch = i == 1);
            if (audio != null)
            {
                int level = 0;
                for (int i = 1; i < VolumeSteps.Length; i++) if (Mathf.Abs(VolumeSteps[i] - audio.Volume) < Mathf.Abs(VolumeSteps[level] - audio.Volume)) level = i;
                Row("sound", "Coastal sounds", VolumeNames, level, i => audio.Volume = VolumeSteps[i]);
                Row("voice", "Mira's voice", new[] { "Off", "On" }, audio.VoiceOn ? 1 : 0, i => audio.VoiceOn = i == 1);
            }
            else
            {
                coastalUi.Text("settings/sound/label", new Rect(x, y, cw, label + row), "Sound is unavailable in this session.", Skin.Type.Body, Skin.InkSoft);
                y += label + row + gap;
            }
            coastalUi.Secondary("settings/back", new Rect(x, y, cw, sh), showTitle ? "Back to main menu" : "Back to pause", () => { showSettings = false; MenuSound(); });
        }

        void InterfaceHeadHomeConfirmation()
        {
            int overflow = DepartureOverflow();
            string body = (overflow > 0 ? $"{overflow} fish cannot fit in the hold and will go back to sea. " : "") +
                (IsNetFisher && !AllNetsStowed ? SecondNet != NetState.Stowed ? "Your second net is deployed; leaving forfeits its catch. " : Net == NetState.Ready ? $"Your net still has {NetCatch} fish to haul. Leaving forfeits them. " : "Your net is still deployed; leaving ends this soak. " : "") +
                "The trip is paused while you choose.";
            coastalUi.ModalV3("headhome", "Leave fish behind?", body, overflow > 0 ? $"Leave {overflow} fish" : "Head home", ConfirmHeadHome,
                "Keep fishing", CancelHeadHome, CancelHeadHome, null, 600, 340);
        }

        void MenuSound() => audio?.Play(VoyageAudio.Cue.Select, .45f);

        // ---- badges -------------------------------------------------------------------------------

        // True when a shop has something worth a visit: shown as a "!" on its bubble.
        bool ShopHasNews(HudTab tab)
        {
            var s = State;
            switch (tab)
            {
                case HudTab.Market: return s.UnsoldCatch.Count > 0 || s.UnseenSale;
                case HudTab.HarbourMaster:
                    return Enumerable.Range(0, GameData.Spots.Length).Any(i => !s.Known(i) && Coasts.Open(i, s.Hull) && s.Coins >= GameData.Spots[i].ChartCost)
                           || s.Active.Count < GameData.MaxActiveContracts && s.Offers.Count > 0;
                case HudTab.CrewOffice: return s.CardTier >= 1 && (s.PendingChests.Count > 0 || s.FreeBlueprints > 0 || s.Renown >= RenownRoad.Threshold(s.RenownClaimed + 1));
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

using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.InputSystem;

namespace Catchline.Game
{
    // Runtime presentation uses the supplied kit and one shared landscape layout space.
    // On the water everything is one tap: bubbles above rods and fish, and a strike minigame.
    public partial class VoyageGame
    {
        public enum HudTab { Market, HarbourMaster, CrewOffice, Chandlery, Supplies }

        static string TabName(HudTab t) => t switch { HudTab.Market => "Market", HudTab.HarbourMaster => "Harbour Master", HudTab.CrewOffice => "Crew Office", HudTab.Chandlery => "Chandlery", _ => "Supplies" };
        bool panelOpen = true;
        // Layout uses the same safe-area space as menus; no device-specific scaling.

        HudTab hudTab = HudTab.Market;

        readonly List<Rect> hudRects = new();

        Rect HudViewport => Screen.safeArea.width > 0 ? Screen.safeArea : new Rect(0, 0, Screen.width, Screen.height);
        float VH => HudViewport.height < 600 ? 480f : 720f;
        float GuiScale => HudViewport.height / VH;
        float VW => HudViewport.width / GuiScale;

        Vector2 ToGui(Vector2 screen) => new((screen.x - HudViewport.x) / GuiScale, (HudViewport.yMax - screen.y) / GuiScale);
        bool OverHud(Vector2 gui) => hudRects.Any(r => r.Contains(gui));

        // ---- input --------------------------------------------------------------------------

        void HandleInput()
        {
            var kb = Keyboard.current;
            if (ManagementOpen)
            {
                if (kb != null && kb.escapeKey.wasPressedThisFrame) CloseManagement();
                return;
            }
            if (baitSettingsCrew != null)
            {
                if (kb != null && kb.escapeKey.wasPressedThisFrame) baitSettingsCrew = null;
                return;
            }
            if (PrepOrdersOpen)
            {
                if (kb != null && kb.escapeKey.wasPressedThisFrame) { if (prepClassDropdown != 0) prepClassDropdown = 0; else PrepOrdersOpen = false; }
                return;
            }
            if (departureReady)
            {
                if (kb != null && kb.escapeKey.wasPressedThisFrame) departureReady = false;
                return;
            }
            if (NetGameActive && !MenuOpen && !confirmHeadHome)
            {
                if (kb != null && kb.escapeKey.wasPressedThisFrame) CancelNetHaulGame();
                else if (!netOrdersOpen && Application.isFocused)
                {
                    var netPointer = Pointer.current;
                    bool cancel = netPointer != null && NetGameCancelRect.Contains(ToGui(netPointer.position.ReadValue()));
                    if ((kb != null && kb.spaceKey.wasPressedThisFrame) || (netPointer != null && netPointer.press.wasPressedThisFrame && !cancel)) TapNetGame();
                }
                return;
            }
            if (confirmHeadHome)
            {
                if (kb != null && kb.escapeKey.wasPressedThisFrame) CancelHeadHome();
                else if (kb != null && (kb.enterKey.wasPressedThisFrame || kb.numpadEnterKey.wasPressedThisFrame)) ConfirmHeadHome();
                return; // H/Space and pointer strikes cannot bypass the protected choice.
            }
            if (kb != null && kb.escapeKey.wasPressedThisFrame && !showTitle)
            {
                if (showSettings) showSettings = false;
                else paused = !paused;
            }
            if (MenuOpen) return;
            if (kb != null && CurrentMode == Mode.Fishing)
            {
                if (kb.hKey.wasPressedThisFrame) { RequestHeadHome(); return; }
                if (kb.spaceKey.wasPressedThisFrame) StrikeTap();
            }

            var mouse = Mouse.current;
            if (mouse != null)
            {
                float s = mouse.scroll.ReadValue().y;
                if (Mathf.Abs(s) > 0.01f && !OverHud(ToGui(mouse.position.ReadValue()))) ZoomOffset = Mathf.Clamp(ZoomOffset - Mathf.Sign(s) * 0.3f, -1.5f, 3f);
            }

            // While the minigame is up, a tap anywhere that isn't a button strikes (on press, so it feels instant).
            var pointer = Pointer.current;
            if (pointer == null || !pointer.press.wasPressedThisFrame) return;
            if (CurrentMode == Mode.Fishing && MinigameRod != null && !OverHud(ToGui(pointer.position.ReadValue()))) StrikeTap();
            else HandleSeaTap(pointer.position.ReadValue());
        }

        // ---- drawing ------------------------------------------------------------------------

        void OnGUI()
        {
            if (!built) return;
            if (coastalUi != null) return;
            Ui.Init();
            Ui.SetTypeScale(UiScales[UiScaleIndex]);
            GUI.skin.verticalScrollbar = Ui.ScrollTrack;
            GUI.skin.verticalScrollbarThumb = Ui.ScrollThumb;
            GUI.skin.verticalScrollbarUpButton = GUIStyle.none;
            GUI.skin.verticalScrollbarDownButton = GUIStyle.none;
            GUI.matrix = Matrix4x4.TRS(new Vector3(HudViewport.x, Screen.height - HudViewport.yMax, 0), Quaternion.identity, new Vector3(GuiScale, GuiScale, 1f));
            if (Event.current.type == EventType.Layout) hudRects.Clear();

            RefreshInterface();
        }

        Rect Panel(Rect r, GUIStyle style = null)
        {
            Track(r);
            GUI.Box(r, GUIContent.none, style ?? Ui.Panel);
            return r;
        }

        void Track(Rect r)
        {
            if (Event.current.type == EventType.Layout) hudRects.Add(r);
        }

        static void Icon(Rect r, string name)
        {
            var t = Ui.Tex(name);
            if (t != null) GUI.DrawTexture(r, t, ScaleMode.ScaleToFit, true);
        }

        // The strike minigame: a close-up of the bobber with the fish circling in.

        // ---- harbour ------------------------------------------------------------------------
        //
        // The quay has five shops. Tap a building's bubble (or a tab) to open its panel.

        static string ShopIcon(HudTab t) => t switch { HudTab.Market => "icon-coin", HudTab.HarbourMaster => "icon-map-pin", HudTab.CrewOffice => "icon-crew", HudTab.Chandlery => "icon-home-anchor", _ => "icon-fuel" };
        static string ShortTab(HudTab t) => t switch { HudTab.HarbourMaster => "Chart", HudTab.CrewOffice => "Crew", HudTab.Chandlery => "Gear", _ => TabName(t) };
        static string ShopHeader(HudTab t) => t switch { HudTab.HarbourMaster => "header-harbourmaster", HudTab.CrewOffice => "header-crewoffice", HudTab.Chandlery => "header-chandlery", HudTab.Supplies => "header-supplies", _ => "header-market" };

        void OpenShop(HudTab tab)
        {
            audio?.Play(VoyageAudio.Cue.Select, .35f);
            hudTab = tab;
            panelOpen = true;

        }

        string CoinShortfall(int cost) => State.Coins < cost ? $"Need {cost - State.Coins} more coins" : null;

        int chartFocus;

    }
}

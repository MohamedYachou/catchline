using UnityEngine;

namespace Catchline.Game
{
    // First-run tutorial (Mo, 2026-10-25): the captain sails the rowboat alone, sells, saves for the skiff, opens the
    // free welcome chest that brings Mira, learns what she does, then learns that chests and crew chests bring new crew.
    // Mira speaks from a coach mark: her pose, a speech bubble, and a ring and glove on the button she means. Targets
    // are found by control id wherever the screen drew them, so the coach never duplicates a layout.
    public partial class VoyageGame
    {
        public enum TutStep { Hello, FirstCast, Sell, Skiff, Refit, Welcome, MeetMira, Recruit, Done }
        public TutStep Tutorial => (TutStep)Mathf.Clamp(State.Tutorial, 0, (int)TutStep.Done);
        TutStep tutShown = TutStep.Done;
        string tutShownText;
        float tutShownAt;

        public void SetTutorial(TutStep step)
        {
            if (State.Tutorial == (int)step) return;
            State.Tutorial = (int)step;
            SaveGame();
        }
        // A brand-new captain: the fly-in, then Mira's first line.
        void BeginFirstVoyage() { State.Tutorial = (int)TutStep.Hello; BeginIntro(); }
        public void SkipTutorial() { SetTutorial(TutStep.Done); audio?.Play(VoyageAudio.Cue.Select, .35f); }

        bool CrewOfficeOpen => CurrentMode == Mode.Harbour && panelOpen && hudTab == HudTab.CrewOffice;
        string ShopTabId(HudTab t) => "shop/tab/" + t;

        // Moves the tutorial on from what the player actually did; dialog steps also move on from their own button.
        void AdvanceTutorial()
        {
            var step = Tutorial;
            if (step == TutStep.Done) return;
            bool harbour = CurrentMode == Mode.Harbour;
            bool navigator = State.Roster.Exists(c => c.Def?.Role == CardRole.Navigator);
            switch (step)
            {
                case TutStep.Hello when !harbour: SetTutorial(TutStep.FirstCast); break;
                case TutStep.FirstCast when harbour && State.UnsoldCatch.Count > 0: SetTutorial(TutStep.Sell); break;
                case TutStep.Sell when harbour && State.UnsoldCatch.Count == 0 && State.BestVoyageFish > 0: SetTutorial(TutStep.Skiff); break;
            }
            step = Tutorial;
            // Later steps follow the boat and the roster, so a player who got ahead of Mira never waits on her.
            if (step <= TutStep.Refit && State.Hull >= 1) SetTutorial(navigator ? TutStep.MeetMira : TutStep.Welcome);
            else if (step == TutStep.Welcome && navigator) SetTutorial(TutStep.MeetMira);
        }

        (string pose, string text, string target, bool dismiss)? TutorialLine()
        {
            bool harbour = CurrentMode == Mode.Harbour;
            bool shop = harbour && panelOpen;
            switch (Tutorial)
            {
                case TutStep.Hello when harbour:
                    // The market may still be open over the port; she points at its close button first.
                    return ("wave", "Morning, captain! I'm Mira, navigator of Gull Harbour. Your rowboat is ready. Set sail and bring back some fish.", shop ? "shop/close" : "port/sail", false);
                case TutStep.FirstCast when CurrentMode == Mode.Fishing && !ManagementOpen:
                    return ("explain", "Tap Fish to cast. Tap Carry to stow your catch. When the hold is full, head home and sell.", "rod/0", true);
                case TutStep.Sell when harbour && State.UnsoldCatch.Count > 0:
                    return ("point", "Welcome back! The market buys any fish. Sell your haul.", shop && hudTab == HudTab.Market ? "market/sell" : ShopTabId(HudTab.Market), false);
                case TutStep.Skiff when harbour && !State.CanRefit:
                    return ("think", $"Next, the skiff. Bring home a full hold and save {GameData.SkiffCost:N0} coins. She has room for crew, and I'd sail with you.", null, true);
                case TutStep.Skiff when harbour:
                case TutStep.Refit when harbour && State.CanRefit:
                    if (Tutorial == TutStep.Skiff) SetTutorial(TutStep.Refit);
                    string refit = !shop || hudTab != HudTab.Chandlery ? ShopTabId(HudTab.Chandlery)
                        : shopSelection.TryGetValue(HudTab.Chandlery, out var chosen) && chosen == "refit" ? "shop/buy" : "refit";
                    return ("cheer", "You can afford the skiff! Refit her in the Gear shop.", refit, false);
                case TutStep.Welcome when harbour && reveal == null:
                    string chest = !CrewOfficeOpen ? ShopTabId(HudTab.CrewOffice) : crewTab != 1 ? "crew/tab/chests" : "chests/welcome/open";
                    return ("map", "The crew office kept a welcome chest for you. Open it, and see who's inside.", chest, false);
                case TutStep.MeetMira when harbour && reveal == null:
                    return ("explain", "That's me, your navigator! I always sail with you, and everyone aboard works 5% faster. Your hauls earn tokens to level me up.", null, true);
                case TutStep.Recruit when harbour && reveal == null:
                    if (CrewOfficeOpen && crewTab == 2)
                        return ("cheer", "The tenth chest for each crew member always holds their blueprint. A free crate comes with each day's first sale, and the renown road gives more. Fair winds, captain!", null, true);
                    return ("point", "Chests also hold blueprints. A blueprint for someone new brings them aboard. Recruit shows who you can get.",
                        CrewOfficeOpen ? "crew/tab/recruit" : ShopTabId(HudTab.CrewOffice), false);
            }
            return null;
        }

        void DismissTutorialLine()
        {
            audio?.Play(VoyageAudio.Cue.Select, .35f);
            audio?.StopVoice();
            switch (Tutorial)
            {
                case TutStep.FirstCast: SetTutorial(TutStep.Sell); break;
                case TutStep.Skiff: SetTutorial(TutStep.Refit); break;
                case TutStep.MeetMira: SetTutorial(TutStep.Recruit); break;
                case TutStep.Recruit: SetTutorial(TutStep.Done); break;
            }
        }

        static bool HasUi(string name) => ArtLibrary.Get()?.UiTex(name) != null;

        // Drawn last, over the screen it explains.
        void InterfaceTutorial()
        {
            AdvanceTutorial();
            var line = TutorialLine();
            if (line == null) { if (tutShown != TutStep.Done) audio?.StopVoice(); tutShown = TutStep.Done; return; }
            var (pose, text, targetId, dismiss) = line.Value;
            if (tutShown != Tutorial || tutShownText != text)
            {
                tutShown = Tutorial; tutShownText = text; tutShownAt = Time.unscaledTime;
                audio?.Play(VoyageAudio.Cue.CoachPop, .3f);
                audio?.Speak(text);
            }
            // Batch captures render the settled pose, not the first frame of the entrance.
            float age = Application.isBatchMode ? 10 : Time.unscaledTime - tutShownAt, now = Time.unscaledTime;
            Rect target = default;
            bool hasTarget = targetId != null && coastalUi.TryFind(targetId, out target);

            // Coach mark: a breathing ring around the button and a glove tapping toward it.
            if (hasTarget)
            {
                float pulse = 1 + .05f * Mathf.Sin(now * 4.2f);
                var ring = new Rect(target.x - 16, target.y - 16, target.width + 32, target.height + 32);
                if (HasUi("tut-ring")) { coastalUi.Sliced("tut/ring", ring, "tut-ring", null, Color.white); coastalUi.Pose("tut/ring", 0, pulse); }
                float s = compactInterface ? 52 : 64, bob = 6 + 6 * Mathf.Sin(now * 5.5f);
                // The glove points up-left from below-right of the button. Near the bottom it turns to point down;
                // near the right edge it is mirrored to sit on the button's left.
                bool low = target.yMax + s > ih - 4, flip = target.xMax + s * .8f > iw - 4;
                float gx = flip ? target.x - s * .7f - bob : target.xMax - s * .3f + bob;
                float gy = low ? target.y - s * .7f - bob : target.yMax - s * .3f + bob;
                if (HasUi("tut-pointer"))
                {
                    coastalUi.Icon("tut/pointer", new Rect(gx, gy, s, s), "tut-pointer");
                    coastalUi.Pose("tut/pointer", low ? flip ? -90 : 90 : 0, 1, flip ? -1 : 1);
                }
            }

            // Mira and her bubble take the first free corner: low right, low left, high right, high left. In an open
            // shop she is smaller and sits under the shop's tabs, so the page she explains stays readable.
            bool panel = CurrentMode == Mode.Harbour && panelOpen;
            float mh = panel ? compactInterface ? 110 : 140 : compactInterface ? 150 : 210, mw = mh * .8f;
            float bw = compactInterface ? 300 : 400, bh = compactInterface ? 128 : 150;
            float width = mw + bw - 8, height = Mathf.Max(mh, bh);
            float right = iw - Edge - width, left = Edge + (CurrentMode == Mode.Harbour && !panelOpen ? HarbourLeftWidth + 12 : 0);
            // Above the shop tab bar where it is drawn (its height differs per screen), else above the HUD's bottom row.
            float bottom = coastalUi.TryFind(ShopTabId(HudTab.Market), out var bar) ? bar.y - 8 : ih - Edge - TabBarHeight - 12;
            float yLow = bottom - height, yHigh = panel ? compactInterface ? 112 : 212 : Edge + (compactInterface ? 56 : 76);
            var spots = CurrentMode == Mode.Fishing
                ? new[] { new Vector2(right, (ih - height) * .5f + (compactInterface ? 10 : 40)), new Vector2(right, yHigh), new Vector2(left, yHigh) }
                : new[] { new Vector2(right, yLow), new Vector2(left, yLow), new Vector2(right, yHigh), new Vector2(left, yHigh) };
            var keepClear = hasTarget ? new Rect(target.x - 24, target.y - 24, target.width + 48, target.height + 48) : Rect.zero;
            // A showing toast (the sale's payout, say) is avoided too, when a spot clear of both exists.
            bool toastUp = coastalUi.TryFind("toast", out var toastRect);
            bool Clear(Vector2 c, bool andToast)
            {
                var r = new Rect(c.x, c.y, width, height);
                return (!hasTarget || !r.Overlaps(keepClear)) && (!andToast || !toastUp || !r.Overlaps(toastRect));
            }
            var spot = spots[0];
            bool found = false;
            foreach (var candidate in spots) if (Clear(candidate, true)) { spot = candidate; found = true; break; }
            if (!found) foreach (var candidate in spots) if (Clear(candidate, false)) { spot = candidate; break; }
            float x = spot.x, y = spot.y;
            float rise = 1 - Ease.OutCubic(Mathf.Clamp01(age / .35f));
            var root = coastalUi.Group("tut", new Rect(x, y + rise * 40, width, height));
            Block(new Rect(x, y, width, height));
            coastalUi.Icon("tut/mira", new Rect(0, height - mh + Mathf.Sin(now * 1.8f) * 2.5f, mw, mh), "mira-pose-" + pose, root, null, "art108-mira");

            var bubbleRect = new Rect(mw - 8, (height - bh) * .45f, bw, bh);
            var bubble = HasUi("tut-bubble") ? coastalUi.Sliced("tut/bubble", bubbleRect, "tut-bubble", root, Color.white, true)
                                             : coastalUi.Card("tut/bubble", bubbleRect, Skin.Card.Soft, root);
            coastalUi.Pose("tut/bubble", 0, Mathf.Lerp(.92f, 1, Ease.OutBack(Mathf.Clamp01((age - .08f) / .3f))));
            float pad = compactInterface ? 14 : 18, buttonH = compactInterface ? 34 : 40;
            coastalUi.Text("tut/bubble/name", new Rect(pad, pad - 4, bw - pad * 2, 22), "MIRA", Skin.Type.Caption, Skin.Teal, TextAnchor.MiddleLeft, bubble);
            coastalUi.Text("tut/bubble/text", new Rect(pad, pad + 18, bw - pad * 2, bh - pad * 2 - 18 - buttonH - 4), text,
                compactInterface ? Skin.Type.Small : Skin.Type.Body, Skin.Ink, TextAnchor.UpperLeft, bubble);
            float by = bh - pad - buttonH + 4;
            if (dismiss) coastalUi.Primary("tut/bubble/ok", new Rect(bw - pad - 120, by, 120, buttonH), "Got it", DismissTutorialLine, null, true, bubble);
            // Quiet text link: skipping is allowed, not advertised.
            var skip = new Rect(pad, by, 130, buttonH);
            coastalUi.Text("tut/bubble/skip", skip, "Skip tutorial", Skin.Type.Caption, Skin.InkSoft, TextAnchor.MiddleLeft, bubble);
            coastalUi.HitArea("tut/bubble/skip/hit", skip, SkipTutorial, bubble);
        }
    }
}

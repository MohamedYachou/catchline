@AGENTS.md

# Two Claude sessions: goals and done list

Mo runs two Claude accounts here, both Claude Code CLI in WSL: **claude1** (`cld`) and **claude2** (`cl2`, or plain
`claude` from home or this folder). Lead, takeover and live usage work as in the **catchline-team** skill (`team usage`,
`team peek`, SendMessage between the two; the `team` guard rings you when something changes). This file holds the
goals and the done list; keep it true and short, delete a goal's line when done and add it (one line, commit id) under
Done; prune Done to the last ~10. Codex orders and logs stay in comms.md. ClaudeCom.md is retired.

## Claude 1 (Windows) — goals, in order
1. Weekly plan at 91% (10-26 01:10): paused until Wed 07:00 reset. Open: review STRIKE-TAP-1 (Codex 1, then
   MAP9-FINISH-AND-MAP10-1) and BOAT-REFINE-1 (Codex 2); Claude L directs Codex meanwhile. Then: catch-card art in the
   first-catch reveal; D1 HUD mockups. Morning report to Mo with docs/QUESTIONS.md.
Holding: VoyageTutorial.cs, CrewUi/**, CoastalCanvas*.cs, Skin*.cs, LeadShots.cs, VoyageInterface.cs, VoyageMenus.cs.

## Claude 2 (WSL) — goals, in order (lead since 10-26 01:30, Claude 1 paused)
1. Direct the two Codex agents (skill codex-director); keep both queues non-empty in CONTINUE-CODEX1/2.txt.
   Codex 1: finish STRIKE-TAP-1 (review its captures in docs/screens/strike-fx), then MAP9-FINISH-AND-MAP10-1, then
   HARBOUR-PETS-1. Codex 2: BOAT-REFINE-2 (Compact, Prep, refit-card pictures, Tier5 trim).
2. Sound: Mo does the listening check (Real/sound4-listening.html; picks artifact
   https://claude.ai/artifact/BZn1HJnhiexxQdSfSHLBoC); apply his picks when they come.
3. Claude 1's open UI item while it is paused: D1 HUD mockups (17-hud-fishing, 18-hud-harbour).
4. Morning report to Mo: what was done overnight, plus docs/QUESTIONS.md.
Holding: docs/briefs/**.

## Done (latest first)
- 9b20d56 first-catch reveal uses the trophy catch-card (name/kg in its band, ribbon above, stamp on the window); tutorial checks 217 PASS
- 7cafc46 refined Rowboat/Skiff in game (Codex 2 BOAT-REFINE-1, accepted; captures intro-*, refit-skiff-*)
- 514717c / 7c0ebcd / fa54ee5 / 08531a9 cast splash, purchase glint/burst, strike-tap art (Codex 1/2, accepted)
- 9c99409 purchase coin flight, crew badge/gems/reward bands, bigger chest art, Mira's first pointer fix; Codex SOUND-WIRE-4/5, TUTORIAL-CHECK-1, UI-POLISH-ART-1 accepted
- 4095521 harbour savings goal tile (VoyageSavingsGoal.cs; captures hud-goal-*)
- 5344fd4 first-catch reveal (VoyageFirstCatchFx.cs; captures first-catch-*)
- 3ca85f6 sell coin flight into the wallet, Mira avoids toasts, sell-step captures; SOUND-4 accepted, Codex 1 ungated
- e82ba85 new-boat celebration (VoyageRefitFx.cs; captures docs/screens/overnight/refit-*)
- 89f52bf real CC0 pack installed for every cue + HARBOUR-SOUND-2 harbour calls/ambience (Codex 1, accepted)
- 05626e1 tutorial at-sea step captures
- 2d5b0b3 first-run tutorial: Mira coach marks (VoyageTutorial.cs, CoastalCanvas.TryFind, captures docs/screens/overnight/tut-*)
- cd7259a / 70d3b29 ClaudeCom channel, usage line, WSL setup (shared instructions, memory, skills)
- b21fb21 card pacing sim rerun after crew tiers (Codex 1, accepted)
- 48671cf deck berths 2/4/6/8 per boat (Codex 1, accepted)
- 7c2593b real crew office sounds (card flip, chest open/heavy, reward chime, token pour)
- f920e4a crew tiers: crew join through blueprints and crew chests, welcome chest with Mira, crew art set

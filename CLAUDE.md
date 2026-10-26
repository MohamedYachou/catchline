@AGENTS.md

# Two Claude sessions: goals and done list

Mo runs two Claude accounts here, both Claude Code CLI in WSL: **claude1** (AI team session `cld1`) and **claude2** (`cld2`).
`cld` / plain `claude` are Mo's own private chats on those accounts, not team sessions. Lead, takeover and live usage work as in the **catchline-team** skill (`team usage`,
`team peek`, SendMessage between the two; the `team` guard rings you when something changes). This file holds the
goals and the done list; keep it true and short, delete a goal's line when done and add it (one line, commit id) under
Done; prune Done to the last ~10. Codex orders and logs stay in comms.md. ClaudeCom.md is retired.

## Claude 1 (Windows) — goals, in order
1. Shipped 10-26 morning (coasts, tier-priced charts, Codex 2 boats/chart/oars): pushed to GitHub and the Real build.
   Open game work is in TODO.md (gold minigame, Jig boat wiring, refit cards, MAP11 commit, sea events).
Holding: VoyageTutorial.cs, CrewUi/**, CoastalCanvas*.cs, Skin*.cs, LeadShots.cs, VoyageInterface.cs, VoyageMenus.cs,
VoyageChart.cs, VoyageIllustratedChart.cs, Data/Coasts.cs.

## Claude 2 (WSL) — goals, in order (lead since 10-26 01:30, Claude 1 paused)
1. Direct the two Codex agents (skill codex-director); when the guard rings, queue the next brief in
   CONTINUE-CODEX1/2.txt and `team start codexN` (Codex never starts by itself; Claude 1 is away until Wed).
   Codex 1: MAP11-FIX-AND-LIFE-1 (sand fix, then kelp life); commit MAP11 after review. Codex 2: KELP-LIFE-ART-1
   (otters), then tier 6 boat concept sheet (Mo picks). Claude: wire the accepted Jig boat (TODO.md Jig item).
2. Sound: Mo does the listening check (Real/sound4-listening.html; picks artifact
   https://claude.ai/artifact/BZn1HJnhiexxQdSfSHLBoC); apply his picks when they come.
3. Claude 1's open UI item while it is paused: D1 HUD mockups (17-hud-fishing, 18-hud-harbour).
4. Morning report to Mo: what was done overnight, plus docs/QUESTIONS.md.
Holding: docs/briefs/**.

## Done (latest first)
- 1ee580d Outer coast painting, oars icon, Compact/Prep fishers re-exported (no stray plane), Tier5 trim (Codex 2, accepted)
- c3d4a28 / 26874ad / bc687f0 two charts (Gull coast / Outer coast), Coasts.cs fish rules, chart prices per boat tier
- 7f96e98 / 6533039 Head home quiet until a haul is aboard; phone shop single row fills the shelf
- 060ef70 Seal cliffs (MAP10) chart pin + cliff/gull glyph; Codex 1 recaptures MAP10 E charts
- 9b20d56 first-catch reveal uses the trophy catch-card (name/kg in its band, ribbon above, stamp on the window); tutorial checks 217 PASS
- 7cafc46 refined Rowboat/Skiff in game (Codex 2 BOAT-REFINE-1, accepted; captures intro-*, refit-skiff-*)
- 514717c / 7c0ebcd / fa54ee5 / 08531a9 cast splash, purchase glint/burst, strike-tap art (Codex 1/2, accepted)
- 9c99409 purchase coin flight, crew badge/gems/reward bands, bigger chest art, Mira's first pointer fix; Codex SOUND-WIRE-4/5, TUTORIAL-CHECK-1, UI-POLISH-ART-1 accepted
- 4095521 harbour savings goal tile (VoyageSavingsGoal.cs; captures hud-goal-*)
- 5344fd4 first-catch reveal (VoyageFirstCatchFx.cs; captures first-catch-*)
- 3ca85f6 sell coin flight into the wallet, Mira avoids toasts, sell-step captures; SOUND-4 accepted, Codex 1 ungated
- e82ba85 new-boat celebration (VoyageRefitFx.cs; captures docs/screens/overnight/refit-*)

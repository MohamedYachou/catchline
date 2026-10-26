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
1. Restaurant pivot (docs/plans/RESTAURANT.md), UI first, exact copy of the mockups. Claude: screens S1-S5 built in
   VoyageRestaurantUi.cs (captures docs/screens/restaurant-ui/, compare.html), temporary mockup crops listed in
   Art/Source/Restaurant/ui-TEMP-CROPS.md; next S6 dashboard, then wire the 3D room. Codex 1: RESTAURANT-UI-ART-1
   (clean art replacing the crops). Codex 2: RESTAURANT-LOOK-DETAIL-2 (painted, lit stage-1 room like
   ui-service-desktop.png). When the guard rings: review, queue in CONTINUE-CODEXN.txt, `team start codexN`.
2. Sound: Mo does the listening check (Real/sound4-listening.html; picks artifact
   https://claude.ai/artifact/BZn1HJnhiexxQdSfSHLBoC); apply his picks when they come.
3. Claude 1's open UI item while it is paused: D1 HUD mockups (17-hud-fishing, 18-hud-harbour).
4. Morning report to Mo: what was done overnight, plus docs/QUESTIONS.md.
Holding: docs/briefs/**.

## Done (latest first)
- ec24c40 / 92264f0 / (this commit) restaurant screens S1-S5 to the mockups, staff rail one card per person (Mo), CORE-1 logic + stage-1 3D accepted
- (this commit) Let's go no longer freezes ~30 s (SeaNav 10x faster, identical graphs, built in background); fish hang mouth-up; captain steps over the rowboat thwart; Keep primary; rowboat 5 kg, skiff = full haul + 500; Mira hi-res + voice samples; open-sea life + MAP11 sand edges art (Codex 2)
- 74f0541 Docs cleanup (69 old docs to docs/archive, CURRENT/AGENTS/README/QUESTIONS refreshed); Codex one-shot runners
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

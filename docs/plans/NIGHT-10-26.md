# Night plan 26→27 Oct (Mo: run until Mo says stop)

Mo, 26 Oct 21:00: keep both Codex and Claude going all night on the restaurant. Full UI first, then restaurant
visuals and gameplay, then crew restaurant clothes per job. Only Claude starts Codex (`team start codexN`, no
auto-restart scripts). When Claude's 5h usage resets it resumes here, finds the last DONE step in comms.md and
continues. No reason to stop except Mo saying so. Morning report in docs/QUESTIONS.md + chat.

Crew clothes (Mo): classic restaurant. Women in robes/dresses and tops, men in suits; Mira looks the best, she's
the face of the restaurant (host).

## A. Full UI, 1:1 with the mockups (first, until 100%)
Claude:
- [x] A1 S5 closing rebuilt on the rx pieces (screen-5 manifest), sbs-checked at 2532x1170.
- [x] A2 S2 phone service HUD on phone:* pieces (r25). Desktop 1440 HUD still old (A5).
- [x] A3 S1 arrange on arrange:* pieces (r33). Room behind arrange: with C4.
- A4 S6 dashboard / week screen (mockup needed → Codex cuts).
- A5 Desktop 1440/2880 checks of every screen.
Codex 1: rest of the S5 pieces, then S6 pieces, every piece trimmed and uniquely named.
Codex 2 (from 23:14): S1/S2 text-style rects, then the remaining S1/S2 pieces.

## B. Restaurant room and visuals
- [x] B1 camera frames the dressed V4 room, V4 night light recipe, Forward+ lights in the atlas shader (r31). Sea backdrop: Codex 2 paints water tile.
- [x] B2 layout tiles mirrored onto the V4 room: kitchen left, queue on the right jetty (r36).
- [x] B3 guests keep Codex 2 palettes (were remapped to crew teal) (r38). More guests: Codex 2.
- [x] B4 Dish props on the tables, candles (r46). Steam sprite: with the markers.

## C. Gameplay
- [x] C1 New-save fishing bot: stows on deck-graph hulls; new-* day chain passes.
- C2 Service sim: orders, cooking times per station, tips, reviews feed S5.
- C3 Market step, sleep step, money flow; balance pass.
- C4 Restaurant upgrades (tables, decor) using arrange mode.

## D. Crew restaurant clothes (Codex 2 3D, Codex 1 2D busts)
- D1 Outfit sheet per job: host (Mira, best), cook, server, dishwasher; women dresses/tops, men suits.
- [x] D2 CrewRig_Restaurant outfits per job in service (r41), Mira D bust on the rail (interim until Mo picks).

## Loop rules
Each Codex run ending: review, append the next order to CONTINUE-CODEXN.txt, `team start codexN`.
Every finished step: commit, DONE line in comms.md, tick here.

# Catchline — to do

Updated 2026-10-26 by Claude 1 (W), docs cleanup by Claude 2. Branch `proto/deck-sim`. Read `CURRENT.md` (what the game is now), then this file,
then the last ~100 lines of `comms.md`. The old to-do list (to 2026-10-21) is in `docs/archive/TODO-2026-10-21.md`.

## Decided today (Mo, 10-26), already in the game

- **Two charts.** Chart 1 "Gull coast" = the first 5 grounds; chart 2 "Outer coast" = the next 6, with its own
  painting (`Assets/Resources/Charts/outer-coast.png`). Rules live in `Assets/Scripts/Game/Data/Coasts.cs`.
- **Boat tiers** (as `CardTier`): 0 Rowboat, 1 Skiff, 2 Compact fisher, 3 Jig boat (not built), 4 Prep fisher,
  5 Buoy fisher, 6 next boat (not designed). One or two grounds per tier:
  | Tier | Grounds | Chart price |
  |---|---|---|
  | 0 | Harbour mouth | free |
  | 1 | Kelp bank | 800 |
  | 2 | Sandbar, Rocky point | 2,500 / 4,000 |
  | 3 | Deep channel | 8,000 |
  | 4 | Chart 2 opens (hard gate: Prep fisher). Seal skerries | 9,000 |
  | 5 | Wreck bank, Lighthouse rock | 14,000 / 18,000 |
  | 6 | Whale shelf, Seal cliffs, Kelp forest | 26,000 / 32,000 / 36,000 |
  Each chart ≈ 2–5 trips of its own boat, ≥ 4 trips of the boat before it. Kelp forest stays on chart 2 (it is in the
  painting); any further ground goes to a future chart 3.
- **Fish by coast.** Gull coast: no gold or red fish, big-rare purples about half as often. Outer coast: specimens run
  bigger, each ground adds a signature purple and a gold shark. Red (mythical) fish are off everywhere until the gold
  minigame exists.

## Open — game (Claude 1 / Codex)

- [ ] **Gold-fish minigame.** Mo is thinking about it. Claude's proposal: a line-tension fight (hold to reel, ease off
  when the line goes red, 3–4 runs). When built, it gates gold catches and lets red fish come back.
- [ ] **Jig boat (tier 3).** Art accepted 10-26 (`Art/Models/BoatsV2/JigBoatV1/`, card `v2-item-hull-jig.png`, lit lamps `JigLampGlow.fbx`). Claude wires
  it: hull data (between Compact and Prep), refit price/goal, sockets, `CardTier` mapping (today `Hull >= 3 ? Hull+1`
  skips tier 3), crew office tier 3 opens with it (QUESTIONS #3).
- [ ] **Tier 6 boat:** Mo picked hull C (10-26); Codex 2 does `docs/briefs/TIER6-BOAT-1.txt` (every earlier tier's kit). Whale shelf / Seal cliffs / Kelp forest are priced for it.
- [ ] **Refit-card pictures** from Codex 2 (`Art/Source/BoatsV2/ui/v2-item-hull{0,1,3,4}.png`, accepted art, committed
  1ee580d) are not in `Assets/` yet: import with metas and use them in the chandlery/refit cards.
- [ ] **MAP11 Kelp forest** (Codex 1, SEAL-CLIFFS-LIFE-AND-MAP11-1): its uncommitted hunks in GameData.cs, Grounds.cs,
  SeaNav.cs, VoyageScenery.cs and the map 11 assets are Codex 1's; review its DONE, then commit.
- [ ] **Sea events (light, never punishing):** not built (old night plan C4).
- [ ] **Economy check:** rerun the pacing sim (`docs/plans/CARDS-PACING.md`) with the new chart prices; Kelp bank is
  no longer free.
- [ ] Mo's listening check of the SOUND-4 cues (`Art/Audio/Real/sound4-listening.html`).
- [ ] `Assets/Editor/ChartChecks.cs` is stale (old chart017 ids); rewrite for the two-page chart or retire it.

## Docs cleanup (Claude 2) — done 10-26
`CURRENT.md` refreshed, `AGENTS.md` and `README.md` point at `CURRENT.md` + `TODO.md`, 69 old docs plus
`ClaudeCom.md`/`claudecom.py` moved to `docs/archive/` (links repointed), `docs/QUESTIONS.md` trimmed.

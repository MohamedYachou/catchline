# Catchline — to do

Updated 2026-10-26 by Claude 1 (W), docs cleanup by Claude 2. Branch `proto/deck-sim`. Read `CURRENT.md` (what the game is now), then this file,
then the last ~100 lines of `comms.md`. The old to-do list (to 2026-10-21) is in `docs/archive/TODO-2026-10-21.md`.

## Restaurant pivot (Mo, 10-26 evening): fish by day, serve at night

Catchline becomes a restaurant game with a fishing outing. The design is `docs/plans/RESTAURANT.md` (build order R0-R6
in its section 12, open questions in section 13).
- [ ] **R0 concepts (running):** Codex 2 `docs/briefs/RESTAURANT-CONCEPT-1.txt` (look options, exterior stages,
  interiors, item kit, service moment, UI mockups); Codex 1 `docs/briefs/RESTAURANT-SCALE-1.txt` (camera and room size
  for phones). Mo picks the look.
- [ ] **R1** the restaurant in the harbour with arrange mode (shop, placement, saved layout), then R2 service, R3 the
  day plan (forecast, Mira's plan card, prep on the way home, market, cats), R4 events and stages, R5 economy and story.
- [ ] Later (Mo): restaurant outfits for the crew in 2D and 3D (crew keep their ship models for now).
- [ ] Later (Mo): passive restaurant income. Not now.
- [ ] Many more Mira messages through the whole game (RESTAURANT.md section 9).
- [ ] Night fishing is half built and never reachable (`GameState.NightVoyage`, night pools); parked unless Mo wants it.

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
- [ ] **Jig boat (tier 3).** Art accepted 10-26 (`Art/Models/BoatsV2/JigBoatV1/`, card `v2-item-hull-jig.png`, lit lamps `JigLampGlow.fbx`). Codex 1 wires it next
  (`docs/briefs/JIG-BOAT-WIRE-1.txt`: saved ID 5, tier 3 via HullTier, refit 6,500): hull data (between Compact and Prep), refit price/goal, sockets, `CardTier` mapping (today `Hull >= 3 ? Hull+1`
  skips tier 3), crew office tier 3 opens with it (QUESTIONS #3).
- [ ] **Tier 6 boat:** Mo picked hull C (10-26); Codex 2 does `docs/briefs/TIER6-BOAT-1.txt` (every earlier tier's kit). Whale shelf / Seal cliffs / Kelp forest are priced for it.
- [ ] **Refit-card pictures** from Codex 2 (`Art/Source/BoatsV2/ui/v2-item-hull{0,1,3,4}.png`, accepted art, committed
  1ee580d) are not in `Assets/` yet: import with metas and use them in the chandlery/refit cards.
- [ ] **MAP11 Kelp forest**: Codex 2 softened the sand-clearing edges in the art source (accepted 10-26); reimport GullKelpForestSeaV2.fbx into Unity and check the deck frames.
- [ ] **Open-sea life** art accepted 10-26 (`Art/Models/OpenSeaLife/`: dolphins, gannet+splash, basking fin, flotsam, distant sail); place along the sailing legs.
- [ ] **Gull coast life** art accepted 10-26 (`Art/Models/GullCoastLife/`: cormorants, oystercatchers, channel
  markers, pot buoys, suggested spots in its REPORT): place it on maps 1-5 (Codex 1 after the Jig wiring).
- [ ] **Sea events (light, never punishing):** not built (old night plan C4).
- [ ] **Economy check:** rerun the pacing sim (`docs/plans/CARDS-PACING.md`) with the new chart prices; Kelp bank is
  no longer free.
- [ ] Mo's listening check of the SOUND-4 cues (`Art/Audio/Real/sound4-listening.html`).
- [ ] Stale editor checks (found 10-26, fail on HEAD too, not from the skiff/departure fixes): ReferenceHudChecks looks for the
  old `reference/status/coins` HUD; SkiffChecks expects a 27 kg skiff hold (Capacity is 40); WeightNetChecks' Version-1 legacy
  save now loads as null; FirstVoyageChecks "early strike still costs bait". Update or retire them.
- [ ] `Assets/Editor/ChartChecks.cs` is stale (old chart017 ids); rewrite for the two-page chart or retire it.

## Docs cleanup (Claude 2) — done 10-26
`CURRENT.md` refreshed, `AGENTS.md` and `README.md` point at `CURRENT.md` + `TODO.md`, 69 old docs plus
`ClaudeCom.md`/`claudecom.py` moved to `docs/archive/` (links repointed), `docs/QUESTIONS.md` trimmed.

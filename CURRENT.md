# Catchline — what is current (read this first)

Updated 2026-10-24 by Claude (lead). Branch: `proto/deck-sim` (this is the newest; `main` is behind).
This repository has months of history. Most files in `docs/` are OLD design rounds and handoffs. Only the files
listed under "Current" describe the game we are building now. If anything else disagrees with them, it is outdated.

## Current (the only design sources)

| File | What it is |
|---|---|
| `docs/MASTER-PLAN.md` | The execution plan, milestones M0–M10. Wins over every older document. |
| `docs/BLUEPRINT.md` | The game design the plan builds (crew cards, deck jobs, tiers 0–5). |
| `docs/CARDS-AND-SPEEDS.md` | All numbers: card levels, XP, wages, work speeds. |
| `docs/UI-SYSTEM.md` | The interface system (UI v2) and its screens. |
| `docs/ART-PLAN.md` | Art work for the 3D/visual agents. |
| `docs/MAP-PLAN.md` | NEW, approved: bigger navigable seas, islands with collision, tap-to-sail, border and horizon. |
| `comms.md` (last ~100 lines) | Who is doing what right now. |

## State of the build

- M0 done. M1: the rowboat runs on the new deck system (stations, baskets, sort table, jobs); the other four hulls are
  next (`docs/briefs/SOL-CODE-1.txt`). Data layers for M2 cards, M3 products/bait and M5 buyers/contracts/quota exist
  with passing checks but are not wired into the game yet.
- UI v2: kit, voyage HUD, operations and crew screens rebuilt; harbour/shops, chart, departure, sale, title, catch card
  still to do.
- 3D crew (`Art/Models/CrewV2/`): seven men and Lise, Tess, Ines, Noor finished with hair fixes; Mira being reworked;
  Ana, Rosa, Tove and a female captain not started. Portraits: `Art/Source/UIv2/crew-styles/portrait-*.png`.
- Maps: GroundsV1 (9× old size) exists; being rebuilt as navigable seas per MAP-PLAN (`docs/briefs/CODEX1-MAPS-V2.txt`).

## Who is working (live agents)

- Codex 1: map rebuild (CODEX1-MAPS-V2). Codex 2: female 3D crew. Sol: sea navigation (`docs/briefs/SOL-SEANAV-1.txt`),
  then SOL-CODE-1. Claude: lead, briefs, acceptance.

## Open design question (for Fable / Mo)

Travel between harbour and fishing grounds is 10–20 s for now, because waiting is boring. Mo is considering turning the
trip into its own half of the game loop: the crew prepares on the way (bait, gear, nets, cooking, maintenance,
navigation choices, events), and fishing on arrival is the second half. Ideas must fit the current design above
(crew cards with roles Fisher / Deckhand / Engineer / Navigator / Captain, deck stations and baskets, tiers 0–5,
products, buyers, quota, night voyages) — not older documents.

Fable's answer (2026-10-24, awaiting Mo): `docs/VOYAGE-PHASES.md` — Part A catalogues what the two legs can be
(trolling, pots on the route, scouting, errands, tender, rival fleet, mentoring, debrief, tides...), Part B builds the
plan/execute/fish/finish direction with two trips a day, Part C recommends a combination. Not design authority yet.

## Old (do not use as design input)

Everything else in `docs/` (e.g. GAMEPLAY.md, CONTINUATION.md, DASH*, PREP*, TIER4-*, TIER5-*, *-HANDOFF.md,
plans/PLAYABILITY-PLAN.md, CREW-CARDS-DESIGN.md, CARDS106-*) is history. Read it only to see why something was decided.

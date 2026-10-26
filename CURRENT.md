# Catchline — what is current (read this first)

Updated 2026-10-26 by Claude 2 (lead). Branch: `proto/deck-sim` (the newest; `main` is behind).
Most of the history lives in `docs/archive/`: old design rounds and handoffs, read only to see why something was
decided. The files below describe the game we are building now; if anything else disagrees, it is outdated.

## Current (the only design sources)

| File | What it is |
|---|---|
| `TODO.md` | Open work and today's decisions (two coasts, boat-tier ladder and chart prices, fish by coast). |
| `docs/MASTER-PLAN.md` | The execution plan, milestones M0–M10. Wins over every older document. |
| `docs/BLUEPRINT.md` | The game design the plan builds (crew cards, deck jobs, boat tiers). |
| `docs/CARDS-AND-SPEEDS.md` | All numbers: card levels, XP, wages, work speeds. |
| `docs/plans/CREW-CARDS-V2.md`, `CREW-TIERS.md`, `ABILITY-HOOKS.md`, `CARDS-PACING.md` | Crew cards v2, abilities, pacing. |
| `docs/plans/FISHING-MINIGAME.md`, `MINIGAMES.md`, `HARBOUR-PLAN.md` | Minigames and the harbour. |
| `docs/UI-SYSTEM.md`, `DESIGN.md`, `PRODUCT.md` | The interface system (UI v2) and the visual direction. |
| `docs/ART-PLAN.md`, `docs/MAP-PLAN.md`, `Art/STYLE.md` | Art and map plans, house style. |
| `docs/QUESTIONS.md` | Open questions for Mo. |
| `comms.md` (last ~100 lines) | Who is doing what right now. `CLAUDE.md` holds each Claude's goals and the done list. |

## State of the build (10-26)

- Eleven fishing grounds on two charts: Gull coast (Harbour mouth, Kelp bank, Sandbar, Rocky point, Deep channel) and
  Outer coast (Seal skerries, Wreck bank, Lighthouse rock, Whale shelf, Seal cliffs, Kelp forest), opening by boat tier
  with prices per tier (`Data/Coasts.cs`). Kelp forest (map 11) is in final fixes, not committed yet.
- Boats in game: Rowboat, Skiff, Compact fisher, Prep fisher, Buoy fisher (all refined). Jig boat (tier 3) art is
  accepted but not wired in; the tier 6 boat is being designed (hull C, carrying every earlier tier's kit).
- Crew cards v2 with the 42-ability engine, chests, deck berths; tutorial with Mira; real sound pack wired;
  catch/sell/purchase/cast/strike effects; first-catch reveal; savings goal; map life on the Outer coast grounds.
- Not built yet: the gold-fish minigame (gates gold and red fish), sea events, chart 3.

## Who is working

- Claude 2: lead (briefs, review, acceptance, commits). Claude 1: away until Wednesday 10-28.
- Codex 1 (Windows): map 11 sand fix and kelp life. Codex 2 (WSL): life art for the Gull coast grounds, then the tier 6
  boat. A Codex only runs when a Claude starts it (`team start codexN`); its orders are `Art/Source/UIv2/CONTINUE-CODEX*.txt`.

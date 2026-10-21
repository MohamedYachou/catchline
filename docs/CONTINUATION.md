# Catchline continuation — 2026-10-15

## Current pickup — 18 October 2026, CREW096

Read latest [comms.md](../comms.md) first; the 15 October continuation below is
history, not a queue to restart. Tier 5 and Management are implemented, and
**all five Real/DASH/Tier 3/Tier 4/Tier 5 launchers** use the verified Dash087
players; each Test retains its original mode. Current handoffs:

- [Tier 5](TIER5-INTEGRATION071.md), [Management math/pipeline](DASH087.md),
  [all launcher modes and verification](DASH092.md).
- [Crew ↔ Management integration](CREW-MANAGEMENT-INTEGRATION.md): shared effective
  rules, exact source hooks, batch/count/cost/cache gaps and acceptance steps.
- [Canonical crew decisions](CREW-CARDS-DESIGN.md), with latest electrical-only
  Engineer and net-use overrides; [future machinery proposals](FUTURE-MACHINERY-DESIGN.md).

Crew cards remain design only. Runtime still uses temporary contracts and legacy
Tier 5 gear condition; do not call the electrical-only redesign implemented.
Processing-equipped boats route every catch through input → processing → output
→ separate carrying → main hold. Small boats bypass processing; no phantom traps.
Preserve accepted DASH artwork and bottom-right actions when adding card effects.

## Historical continuation

Mo assigned Codex ownership of Claude's gameplay/design work and asked for GPT-6.1 Sol at medium reasoning to handle 2D/3D assets. Both original plans remain in `docs/plans/`; gameplay is `docs/GAMEPLAY.md`, asset direction is `Art/STYLE.md`. Main checkout: `Catchline`, branch `proto/deck-sim`; asset worktree: `Catchline-art-style`, branch `art/style-pass`.

## Recovered state

Claude last completed harbour dressing and sea landmarks in `2e317ca`. The skiff kit was already merged, but its refit/gameplay was unfinished. The asset queue stopped on usage-limit errors and incorrectly marked tasks05–08 done. The runner now stops on failure. UI05's pending composition work was preserved, finished and validated; tasks07/08 remain pending. No old queue process was restarted.

## This continuation

- Implemented the skiff refit, hull data, deck routes, three sockets, integrated hold/lid, outboard, fuel purchases and round-trip fuel reservation. Old rowboat saves remain valid. Added three-crew hiring, fisherman automation and the set/soak/haul gill net with a carrying backlog.
- Imported UI05: 39 additions, 83 total textures; large illustration import sizes corrected. These assets are available to the art library; title/chart/portrait layout integration remains on Claude's plan.
- Sol built the crew rig, four outfits, three hats and 11 clips, with Blender sources, FBX round-trip validation and preview sheets. Captain/deckhand/fisherman runtime integration passed actual Unity clip import, skin playback and role visibility checks.

## Next gameplay work

Claude's B1–B5 foundation is implemented. The final 30-voyage automation run reached the skiff at voyage 28 and yielded 86/133/73 gross coins/min in its first three trips (6.0/6.0/5.3 minutes), compared with late rowboat trips around 30–54. A targeted test also confirms fisherman catches without captain taps, haul backlog, role save/load, crew limits and expiring contracts. CREW026 changes role availability, not contract duration. Broader balance seeds and longer voyage pacing remain tuning work.

Continue with C (contracts/rivals/events), D (remaining UI and feedback) and the E morning wrap-up. The full night plan is not yet complete.

The asset queue05–08 is complete and merged. Task07's31 models supply visible upgrade variants, harbour residents/backdrop and sea landmarks. Task08 supplies the day boat, nine stations and seven textures for later integration. Day-boat gameplay and water material application are not enabled yet. Briefs, STATUS.md and validation evidence live under `Art/TASKS/` and each model batch.

## Verification and testing

From Windows, run `powershell -File docs/tools/check.ps1 -Name skiff -Method Catchline.EditorTools.SkiffChecks.Run`. It uses `Catchline-sim`; the main Unity project is never opened in batchmode. The ordinary check method runs the bot (`-Voyages 30`). Logs and scene renders are in the scratch project's `Logs/`; selected renders are copied to `docs/screens/`.

To test through normal play: open Catchline > Play Voyage, return with 16 fish, visit Chandlery and buy the refit, then visit Supplies for fuel and bait. Choose any fisherman/deckhand mix at Crew Office; both roles remain available after each hire, while contracts still expire by voyage. At sea, the fisherman claims a rod; your other rods retain Fish bubbles. Tap Set net with your hands free, fish during the soak, then Haul net and watch the carrying backlog. Save by returning to harbour. The first tank is included.

Scene renders do not include Unity's IMGUI HUD. They verify model placement and camera framing; interactive title/shop layout review is still outstanding.

## CREW026 update — 2026-10-16

Mo clarified that the intended fix is role availability, not permanent hiring.
Crew contracts still expire after2/3/5 voyages. Both roles have enough candidates
to fill the current hull in Real and Test, with a replacement offer after each
hire. The tier3 Test shortcut starts with an empty roster and1000 isolated coins
at the Crew Office. The separate `-deep-net-trial` mode remains available. Details
and evidence: [CREW026.md](CREW026.md).

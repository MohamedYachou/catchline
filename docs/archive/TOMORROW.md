# Catchline — resume on 16 October 2026

## Latest interface delivery — HUD-008

Mo requested a cohesive stylized HUD and full shop workspace, and chose
illustrated categories/roomy items/smaller harbour view. Native Canvas replaces
the old gameplay/shop IMGUI; menus/confirmations remain. See [HUD-008](HUD-008.md)
for exact implementation, actual desktop/landscape captures and verification.
Full combined regression and hidden Windows preview build passed. Preview stays
closed under school/background-only constraint. Physical pointer/touch and
mobile hardware performance remain unverified; no visual acceptance inferred.
Codex 2's additive CompactFisherV1 remains a separate art/design delivery.

## Current steering — WATER-006, 16 October

Mo keeps Codex 1 on water: supplied game-reference clarity and small overlapping
surface ripples, clean blue, no foam/white wash. Large swells are now rejected
because the boat stays steady; this supersedes WATER-005's larger waves. Codex 2
separately owns the skiff work/design; inspect its latest diary before runtime
mechanics pickup. All testing stays hidden while Mo is at school.
Read [current water checkpoint](PTS-WATER-NOW.md) and latest `comms.md` first.
The historical handoff below predates the integrated PTS adaptation and all four
new map deliveries. Source/runtime checks do not imply Mo's visual acceptance.

## Copy this prompt into Windows Codex

Continue Catchline's small-slice visual polish. Read AGENTS.md, PRODUCT.md,
DESIGN.md, this file, docs/CLI-ARTIST-HANDOFF.md and the latest relevant comms.md
entries first. Load design-stack and codex-cli-orchestrator. Inspect actual current
files/git state because the existing Ubuntu artist may have delivered more since
this checkpoint. Preserve all dirty work. Do not spawn app subagents.

Use the existing Ubuntu CLI artist session through the skill helper. Check its
status/context without prompting it unnecessarily; compact at an idle boundary
before another large assignment. Review its latest commits, reports, exports and
actual renders. Mo authorized it to finish ART-011, continue bounded first-location
polish and import each finished model into main so he can view it in Unity.
This authorization includes only necessary integration hooks, not unrelated content.

First finish the composed harbour-mouth map and convincing animated water together,
then rebuild the fishing HUD faithfully against the original goal renders. Show
actual Unity desktop/landscape-phone captures and an updated playable preview.
Mo rejected POLISH-002's visual quality; passing regression is not visual acceptance.
Do not add more gameplay breadth yet. Ask about visual direction only where needed.

## Current main state at handoff

- Project: C:/Users/momoy/Projects/Catchline; branch proto/deck-sim.
- ART-010 rowboat/reference delivery cherry-picked as **1bc8a59**. ART-009 day-boat
  delivery f5ce155 remains unintegrated; do not accidentally claim all art merged.
- ART-011 was still active. Its draft FBX and placement JSON were copied into
  Assets/Art/Models/Environment/ for tonight's editor test. This was a WIP import,
  not final art acceptance. Inspect newer artist delivery before relying on it.
- Runtime now uses GullHarbourMouth for spot 0 when present, offset (0,-.32,0),
  and maps its seven terrain palette slots. It replaces the old scattered rocks
  only for the first spot. Other locations are not polished.
- ArtImport rebuilds ArtLibrary after model imports. Stop and Play again in Unity
  to rebuild a running voyage from new assets; importing does not hot-swap a live boat.
- PlaytestReady.Open rebuilds the library and opens Assets/Scenes/Voyage.unity.
  Main Unity was launched interactively with that method. Never batchmode main.
- Tonight uses the earlier POLISH-002 water. **The new water is not ready or shipped.**
  Do not describe the map draft as the final map-and-water reveal.
- Prior PLAY-001 gameplay is tested and Mo confirmed the core loop works.

## Water experiments and scratch restoration

See docs/POLISH-003.md. Plunder was inspected read-only. Adapted Boat Attack did
not show a working surface in the orthographic editor study; its legacy passes
also conflict with RenderGraph. MatrixRex MIT shader compiled and rendered, but
its study still looked too flat/spotty compared with the original goal.

Experiments are not installed in main. Latest study source snapshots and the
removed experimental Boat Attack package are in Logs/polish-003-water-study/.
Upstream Matrix repo remains in Logs/water-candidate-matrix/. Scratch evidence:
Catchline-sim/Logs/water-study/ and matrix-water-study-*.log. No native-player
motion acceptance claimed from these camera stills.

Before tonight's regression, scratch manifest/lock were restored from main,
experimental Boat Attack package and Resources settings moved out, and the normal
check script mirrored main Assets (removing candidate editor scripts/assets and
restoring source render settings). Check the latest log rather than assuming pass.
An attempted replacement coastal shader patch failed atomically and did not land;
the existing CatchlineWater.shader is still the POLISH-002 implementation.

## Preservation and verification

Main has extensive uncommitted POLISH-002/003 source, docs and capture work.
Keep preexisting dirty Assets/Settings/PC_RPAsset.asset and
ProjectSettings/URPProjectSettings.asset untouched. Preexisting untracked
docs/WINDOWS-CODEX-HANDOFF.md is not ours to overwrite/stage indiscriminately.
Backups: Logs/polish-002-backup and Logs/polish-003-runtime-backup. Keep until
replacement work is verified; remove temporary backups after successful verification.

Tonight regression: Catchline-sim/Logs/check-tonight-map.log.
Main interactive editor: Logs/tonight-editor.log. Final results appended below.
Tonight's regression **passed** (FIRST VOYAGE REGRESSION PASSED).
For future checks: powershell -NoProfile -ExecutionPolicy Bypass -File
docs/tools/check.ps1 -Name NAME -Method Catchline.EditorTools.FirstVoyageChecks.Regression.
Build session-only preview with FirstVoyageChecks.BuildPreview; it preserves real saves.

## Tomorrow's order

1. Check artist status, imported files and nightly handoff. Review/reconcile exports,
   .meta GUIDs, runtime hooks and actual camera framing. Preserve dirty edits.
2. Get convincing dynamic water working against the authored seabed and shore.
   Require visible depth/biome control, hull/shore contact, refraction, stable
   highlights and calm motion. Choose the best quality result, not smallest code.
3. Rebuild the fishing HUD against original day03-small-boat.png and supplied
   UI concepts: cream/navy hierarchy, useful icons, clear actions and quiet boat area.
4. Run actual player captures at 1440x900 and 844x390, inspect and iterate. Verify
   cast/wait/bite/reel/carry/stow/full/return/sale/upgrade and preview save isolation.
5. Show Mo the map and water together and give specific playtest observations.

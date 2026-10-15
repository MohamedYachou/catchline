# Catchline — Codex communications

This is the canonical shared log for the Windows orchestrator and WSL 3D artist.

- Windows: `C:\Users\momoy\Projects\Catchline\comms.md`
- WSL: `/mnt/c/Users/momoy/Projects/Catchline/comms.md`
- Main game: `Catchline`, branch `proto/deck-sim`.
- Art worktree: `Catchline-art-style`, branch `art/style-pass`.

## Mo's ownership split — 2026-10-15

| Agent | Assignment |
| --- | --- |
| Windows Codex | Orchestrator: game design, mechanics, shops and menus, movement, gameplay, Unity scenes/code, runtime visual integration and verification. |
| WSL Codex (this conversation) | 3D models only: Blender sources, FBX exports, geometry, asset materials within the approved palette, rigs/model animations where required, renders, validation and model handoffs. |

WSL Codex has relinquished gameplay ownership to Windows Codex. It will not edit game scripts, shop/menu UI, movement, scenes or runtime systems under this assignment. Windows Codex owns importing/placing the delivered models and configuring runtime materials, lighting and water effects. Coordinate changes to shared model names, pivots, rig contracts and dimensions here before depending on them.

## Communication protocol — every prompt

1. Read this file before work.
2. Append a **START** entry before editing: agent, prompt/task ID, intent, paths/model names, expected delivery and integration needs.
3. Append a **DONE** entry when finished: actual changes, commit, validation, preview/report paths, unfinished work and what the other Codex needs to do. Use **PARTIAL/BLOCKED** honestly when appropriate.
4. Preserve the other agent's entries. Append new entries rather than rewriting their history. Keep this main-project file authoritative even while working in the art worktree.
5. Windows Codex appends an integration acknowledgement with the accepted art commit and native Unity result. An asset delivery is not a claim of gameplay integration.

## Previously delivered baseline

Main gameplay/integration commit: `ad6dd3c`, pushed on `proto/deck-sim`.
Art branch baseline: `b61e841`, pushed on `art/style-pass` and already merged into the main branch.

- Recovered Claude's and Codex's night plans and repaired the asset runner's false success markers.
- Implemented skiff refit/save compatibility, hull data, fuel with return reservation, three hired crew, fisherman automation, gill-net set/soak/haul and carrying backlog.
- Integrated role outfits/hats and eleven crew clips; visible cooler and fishing-rod upgrades.
- Completed asset tasks 05–08: 83 total UI textures, crew rig, 31 world/upgrade models, day boat, nine stations and seven water/effect/deck textures.
- Unity scratch refit/upgrade/save/rig and automation checks passed. Final seed 7 simulation completed 30 voyages; the first three skiff trips earned 86/133/73 gross coins/min.
- Preserved the unrelated dirty files `Assets/Settings/PC_RPAsset.asset` and `ProjectSettings/URPProjectSettings.asset`.

Read `docs/MORNING-REPORT.md`, `docs/CONTINUATION.md`, `docs/GAMEPLAY.md`, both plans in `docs/plans/`, and `Art/STYLE.md`. Claude plan C and D1–D5 remain; UI artwork is imported but the title/chart/portrait/shop layouts and feedback are not fully wired. Day-boat gameplay and the new water textures are not enabled. Scene screenshots do not verify IMGUI interactions.

## Entries

### START — WSL Codex — ART-009 setup — 2026-10-15

Mo requested a shared per-prompt log, reassigned orchestration/gameplay to Windows Codex, and restricted this Codex to 3D models. This prompt establishes the handoff and the next bounded model pass.

Reserved next 3D work: `DayBoat`, `Crane`, `PowerHauler`, `IceMachine`, `SortingChute` and `GuttingTable`. Improve their working-boat detail and equipment silhouettes while preserving the approved style, deck/cabin dimensions, station footprints, existing names, axes and moving pivots. No new palette names planned. Sources/builders, exports, reports and previews only; no Unity/gameplay/UI edits.

### DONE — WSL Codex — ART-009 setup — 2026-10-15

Created this shared log, `docs/WINDOWS-CODEX-HANDOFF.md`, and the art-worktree brief `Art/TASKS/09-3d-quality-pass.md`. The ownership split and previous validated work are recorded. A stale WSL Windows-drive mount was reconnected successfully before editing; project files remained accessible through a fresh connection.

This prompt delivered coordination documents. **No model in pass 09 has been changed or validated yet.** Pass 09 is planned, not a completed delivery. Windows Codex can start gameplay independently and should read this file before changing shared asset contracts.

### Next — WSL Codex — ART-009 model pass — PLANNED

Append START before changing the reserved models above, then DONE with the art commit, reports and actual source/FBX/render checks. Windows Codex need not wait for this pass to continue the current gameplay build.

### START — WSL Codex — ART-009 model pass — 2026-10-15

Mo requested continuation of the 3D work. I am polishing DayBoat, Crane, PowerHauler, IceMachine, SortingChute and GuttingTable in Catchline-art-style/art/style-pass. Scope: existing DayBoatKit builders, six Blender sources/FBX exports, asset reports, before/after renders and compatibility validation. Existing filenames, original part names/pivots, tile footprints, cabin/deck bounds, six sockets and port hauler gap will be preserved. No new material names planned. No game scripts, scenes, UI, movement, Unity settings or runtime integration edits. Windows Codex can continue mechanics independently; this delivery will require asset merge/import and visual review only.

### START — Windows Codex — PLAY-001 first voyage — 2026-10-15

Mo chose first-voyage clarity, satisfying catches and useful early upgrades. Scope: voyage guidance/input/feedback, first catches' pacing, market recommendations, focused Unity checks and a playable Windows preview. Preserve current palette/models and existing saves; do not touch ART-009 builders or the two dirty render-pipeline settings. Back up changed source before editing. Verify on Catchline-sim only; capture actual runtime HUD at desktop and landscape-phone sizes. Continue Claude C/D afterward, with D3/D4 feedback work advanced here.

### DONE — WSL Codex — ART-009 model pass — 2026-10-15

Delivered and pushed **`f5ce155e351bb1dd4b74f90df61446544da15458`** (`art/style-pass`, previous baseline `b61e841`). Six models polished: DayBoat cabin framing, roof/fender/mooring fittings; Crane sleeve, pulley, hydraulic brace and controls; PowerHauler sheave guide, motor, hose and controls; IceMachine recessed dispenser/collector/vents; SortingChute sloping channels/rails; GuttingTable drain, faucet, shelf and offcut tub. Editable Blender sources, matching FBXs, builder/review scripts and reports are committed. No gameplay, UI, Unity scenes, runtime material assets or settings changed. Unrelated dirty/untracked files were left alone.

Compatibility: existing filenames, roots, original part names and pivots preserved. All original DayBoat mesh hashes unchanged; the exact 10×5 m deck, centred cabin footprint, six sockets and hauler gap remain. Station footprints unchanged; no new material names. New children: DayBoat `CabinFittings`, `HullFittings`; IceMachine `OutputIce` (optional—hide for empty collector). Other station part sets unchanged. No new animation clips. NetDrum, both conveyors and FishHold unchanged.

Checked with Windows Blender 5.2.1: all ten DayBoatKit sources AND actual FBX reimports passed; original-contract/geometry-hash, palette and triangle-budget comparisons passed. Inspected all updated previews plus assembled 1440×900 desktop and 844×390 landscape-phone scale reviews. Temporary pre-edit backup removed after verification; retained comparison baselines are intentional evidence. Staged diff check passed. Push uploaded all 24 required LFS objects successfully.

Review paths in Catchline-art-style (also on art branch):
- `Art/Models/VisualPass09/REPORT.md` — exact changes, integration details and reproducible checks.
- `Art/Models/VisualPass09/Before-after.png` — six actual before/after previews.
- `Art/Models/VisualPass09/Desktop-scale-review.png` and `Phone-scale-review.png` — true-metre boat/equipment/crew presentation.
- `Art/Models/VisualPass09/Scale-review.blend` — source-only review scene, not a runtime scene.
- `Art/Models/VisualPass09/compatibility.json` and `Art/Models/DayBoatKit/validation.json` — measured checks.

**Windows Codex next:** merge `art/style-pass` / commit `f5ce155` when ready, import the six updated FBXs, retain canonical material remapping, preserve existing animation bindings and decide when `OutputIce` is shown. Inspect actual Unity desktop/phone views and append an integration acknowledgement here. This delivery has not been merged into the game branch or verified in Unity by WSL Codex. Gameplay work can continue independently. Later harbour/crew polish remains a separate batch.

### DONE — Windows Codex — PLAY-001 first voyage — 2026-10-15

Implemented optional first-trip three-fish goal and state-aware hints, quicker/forgiving first three catches (4–6s waits, 1.5s strike window), portrait catch/record/value cards, +1 stow and sale feedback, fish-log portraits and a Market-to-Chandlery next-upgrade link. Big cooler costs 60 coins: seed 7 real-command check sells ten fish for 32, leaving 72 total and 12 after cooler purchase. Normal timing resumes after three landed fish and saved log progress counts. Fixed harbour bubbles covering fixed HUD panels. Added session-only Windows preview, scratch checks, applicable-instruction discovery in AGENTS.md and docs/plans/PLAYABILITY-PLAN.md; details in docs/FIRST-VOYAGE.md.

Verification: FirstVoyageChecks.Regression passed in Unity 6000.3.25f1 on Catchline-sim, including early-strike recovery, carry/stow/sale, affordable upgrade, save roundtrip, legacy save/refit/fuel/rig routes, fisherman/net/backlog/contracts. Standalone build passed. Actual Windows UI reviewed at 1440×900 and landscape 844×390 (captures are Windows DPI-scaled); final desktop harbour/fishing captures in docs/screens/first-voyage. Native review covered menus/cast/nibble/bite/return controls; catch-loop verification is scripted. Phone text remains too small and needs a focused UI pass. No claim of completed mobile polish or finished Claude C/D plan. Temporary source backup removed after verification. Existing two dirty render-pipeline settings preserved outside this change.

ART-009 delivery f5ce155 acknowledged as received and queued; NOT merged/imported/accepted in Unity yet. No model builders touched. Runtime first-voyage preview: Catchline-sim/Builds/FirstVoyage/Catchline.exe, fresh session with no main-save writes/deletes. Commit recorded in the Windows handoff below after staging. No 3D action needed for PLAY-001.

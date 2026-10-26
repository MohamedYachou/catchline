# Prompt for Windows Codex

You are now Catchline's orchestrator. Mo assigned you game design, mechanics, shop/menu implementation, movement, gameplay, Unity code/scenes, runtime visual integration and testing. The WSL Codex in the other conversation is now a 3D model artist only.

Start at `C:\Users\momoy\Projects\Catchline` on `proto/deck-sim`. Read `comms.md`, `docs/MORNING-REPORT.md`, `docs/CONTINUATION.md`, `docs/GAMEPLAY.md`, `docs/plans/NIGHT-PLAN-CLAUDE.md`, `docs/plans/NIGHT-PLAN-CODEX.md` and `Art/STYLE.md`. Follow the project's applicable governance and design stack.

The previous Codex recovered both interrupted plans and completed the playable skiff milestone. Commit `ad6dd3c` is pushed and includes persistent refits, fuel, three hired crew, fisherman automation, manual gill nets, role models/animations and upgrade visuals. The asset branch through `b61e841` is already merged. Tasks 05–08 supplied the UI kit, crew, world polish, day boat/stations and water textures. Unity scratch regressions and a 30-voyage run passed. Broader balancing and native interactive UI review remain.

Continue the actual game from the current files. Claude plan C (contracts, rivals, daily reward, sea events) and D1–D5 (HUD/title/feedback/portraits/chart) remain. Own the menus, movement and mechanics Mo asks for. Day-boat assets and water textures exist, but their gameplay/material integration is future work. Do not mistake mockups or scene renders for verified UI.

WSL Codex's next 3D-only batch is model polish for DayBoat, Crane, PowerHauler, IceMachine, SortingChute and GuttingTable: clearer equipment silhouettes, warmer boat/cabin detail and readable working surfaces. It will preserve the exact deck/cabin dimensions, footprints, existing part names, axes and moving pivots, and supply Blender sources, FBX files, previews and validation. This batch is planned; no new pass-09 model delivery is claimed yet. The artist will work in `Catchline-art-style` on `art/style-pass`. Coordinate required model changes through `comms.md` instead of editing its builders concurrently.

For every prompt, read `comms.md`, append START with intent and paths before edits, then append DONE with changes, checks, commits and integration needs. Preserve the other Codex's entries. Review and integrate art commits into the game yourself; the artist does not own runtime integration.

Preserve the existing unrelated render-pipeline edits. Never run Unity batchmode on the main project while its editor may be open; use `Catchline-sim` and `docs/tools/check.ps1`. Windows Git credentials can push to origin; the WSL GitHub account previously could not access this repository. The art worktree's `.git` points to a WSL path, so push its branch through the main repository if using Windows Git. Do not reset either worktree or rerun the old queue blindly.

# Task 09 — 3D model quality pass

Status: built and verified; six-model batch delivered on `art/style-pass`. See `Art/Models/VisualPass09/REPORT.md` and canonical `comms.md` for the commit and integration handoff.

## Ownership and communication

Mo assigned this WSL Codex 3D models only. Windows Codex is the game orchestrator and owns gameplay, shops/menu UI, movement, code/scenes and runtime integration. Read and append START/DONE for each prompt to the canonical shared file:

`C:\Users\momoy\Projects\Catchline\comms.md`

WSL path: `/mnt/c/Users/momoy/Projects/Catchline/comms.md`.

Do not edit `Assets/Scripts`, `Assets/Editor`, `Assets/Scenes`, UI artwork/layouts, gameplay plans, runtime materials or Unity project settings for this model assignment. Report integration requirements to Windows Codex in comms.md.

## First bounded batch

Polish `DayBoat`, `Crane`, `PowerHauler`, `IceMachine`, `SortingChute` and `GuttingTable` in the existing approved style. Use `Art/STYLE.md`, the Day 3/Day 28 references and actual existing rendered models as visual authority.

- DayBoat: strengthen cabin/window framing, restrained roof/mast fittings and working-boat details without consuming build tiles or hiding the deck.
- Crane/PowerHauler: make the boom, hoisting path, sheave and controls readable as working equipment at game zoom; preserve stored footprints and existing animation pivots.
- IceMachine: clarify the ice outlet, collection area, controls and ventilation with broad forms.
- SortingChute/GuttingTable: clarify input/work surfaces, channel/output and useful fittings; preserve accessible operator edges and worktop scale.

## Compatibility contract

Preserve all existing asset filenames, root origins, part names and moving pivots. Additive parts are allowed if documented. DayBoat remains a 10×5 m deck with centred 3×2 m bow cabin, six sockets and the port hauler gap. Station footprints remain unchanged. Use existing canonical `M_*` palette names; no new colours planned. Keep broad bevels, clear silhouettes and sparse detail; no global outlines or noisy textures.

## Deliverables

Back up before major edits; remove only this pass's backups once verified. Supply editable Blender sources, FBX exports, before/after game-angle views, a common-scale boat/equipment presentation, phone-size review, measured geometry/part/pivot validation, and a concise report listing exact integration differences. Validate actual FBX reimports and compare original part/pivot contracts. Do not label a model complete based on a render alone. Commit scoped art changes on `art/style-pass`, then report the SHA in comms.md for Windows Codex to integrate.

Later batches can cover harbour/building silhouettes, active boat dressing and crew/model-animation polish, following current screenshots and Mo's feedback. They are not part of this first batch's completion claim.

# ART-009 — boat and working equipment

Six existing models polished in the approved navy, ivory, timber and teal palette. Editable Blender sources and matching FBXs replace their existing files. No gameplay, UI, scenes, runtime material assets or project settings changed. Windows Codex owns Unity integration.

| Model | Visual change | Triangles before → after |
| --- | --- | ---: |
| DayBoat | Framed glazing, wipers, roof/navigation fittings, lifebuoys, tyre fenders and mooring cleats | 3258 → 6442 |
| Crane | Telescopic sleeve, hydraulic brace, head pulley, turntable and controls | 208 → 824 |
| PowerHauler | Sheave guide, rope groove, motor/control housing, hose and lever | 328 → 768 |
| IceMachine | Recessed outlet, collector, ice pieces, controls and ventilation | 320 → 1264 |
| SortingChute | Sloping channels, guide rails, grate, crossbrace and handle | 332 → 924 |
| GuttingTable | Drain, faucet, shelf, empty offcut tub, handle and feet | 332 → 900 |

## Integration contract

Original filenames, root origins, part names and pivots are preserved. DayBoat's original meshes are byte-for-byte identical by geometry hash; new `CabinFittings` and `HullFittings` meshes provide all boat changes. Its 10×5 m deck, centred cabin footprint, six rod sockets and hauler gap remain intact. Equipment still uses the original 1×1 or 2×1 m footprints. No equipment is fused into the boat.

IceMachine adds `OutputIce` at the root origin. It is optional display geometry: hide that child for an empty collector. All other station part sets are unchanged. Crane `Boom` and PowerHauler `Sheave` retain their original animation pivots. Added details on those parts move with the part. No animation clips are added. No new material names are introduced; reuse the existing canonical palette remapping.

NetDrum, Conveyor_Straight, Conveyor_Corner and FishHold are unchanged. The review scene includes two existing static NPCs for scale; their source/export files are unchanged.

## Evidence and limits

- `../DayBoatKit/validation.json`: all ten source models and actual FBX reimports passed topology, finite bounds, materials, part/pivot and footprint checks.
- `compatibility.json`: checks original part names/pivots, identical original boat geometry, untouched four assets, canonical palette and triangle budgets.
- `Before-after.png`: actual old/new game-angle renders. Each individual preview auto-fits its model; use the scale review to judge relative size.
- `Desktop-scale-review.png`, `Phone-scale-review.png`: assembled equipment and two existing crew figures, all at real metre scale. `Scale-review.blend` is an editable source-only presentation, never a runtime scene.
- `scale-layout.json`: exact review placements, no model rescaling.

The rendered previews and both scale views were inspected. This pass verifies Blender sources and FBX content; Unity material remapping, imports, placement and runtime appearance require Windows Codex's game-side review. The showcase layout is illustrative, not a gameplay layout prescription. Later harbour and crew polish remains separate work.

## Rebuild

In Blender 5.2, run `Art/Source/build_day_boat.py -- DayBoat Crane PowerHauler IceMachine SortingChute GuttingTable`, then `validate_world_batches.py -- DayBoatKit`, then `review_visual_pass09.py`. With Python/Pillow, run `world_contact_sheets.py DayBoatKit`, `compare_visual_pass09.py`, and `world_batch_reports.py DayBoatKit`. Baseline-contract.json and Before previews retain the prior batch for comparison.

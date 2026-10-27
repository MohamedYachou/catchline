# Stage2Bistro — BISTRO-LOOK-1

Codex 2 (WSL CLI), 2026-10-27. Source delivery; native AFTER import remains Claude's check.

The Bistro now has soft ivory/blue-grey kitchen tile variation instead of the high-contrast checker, darker varied timber, subtle plaster/stone pigment variation, two shallow bordered runners, a framed wall menu, three herb pots, three stacked jetty crates, front-jetty and rear-terrace festoons, and two small terrace lanterns. Broad fill is reduced; the light recipe favours warm practical pools. All colours use the existing V4 atlas; no texture edits. UV cell remaps and LocalAO vertex tint survive the game's shared-material replacement.

## Grid and export contract

Room **10×5m**, kitchen **4×5m**, open terrace **3×5m** along +Blender X. V4 origin unchanged: tile `(x,y)` → `[-4+x+.5,2.5-y-.5,.04]`. Room right X=6, terrace X=6..9. Door tile `(9,0)` enters through the side wall at Y=2. Front quay remains a narrow .70m strip, with no seats. Original layout.json and final-cameras.json are byte-identical to the accepted grid-fit source.

All **164 original production meshes retain their names and world geometry**. Thirteen additive BistroLook_* meshes bring the export to **177 meshes / 95,628 triangles**, up 7,152 triangles from 88,476. No fixed usable seats were added. Runners top out at Z=.0535m, 13.5mm above the unchanged floor. Floor-standing herbs, crates and lanterns sit at the perimeter; the third herb is sill-mounted. The wall menu and high terrace cord leave the doorway and sky open. Existing kitchen/station names remain unchanged for runtime hiding. Furniture in populated proofs is REVIEW-only and never enters the FBX.

Every exported mesh uses EXPORT_ followed by its source name. Exact V4 export: `apply_unit_scale=True`, `apply_scale_options='FBX_SCALE_UNITS'`, `axis_forward='-Z'`, `axis_up='Y'`, `colors_type='LINEAR'`, `path_mode='RELATIVE'`, selected meshes only, animation disabled. FBX UnitScaleFactor=100, geometry in metres. Keep documented `[x,z,-y]` positions; the existing stage loader mirrors X.

## Lighting handoff

Import the new Stage2Bistro.fbx and lighting.json together. The recipe contains 23 POINT practicals plus the Blender sun/area reference. The current runtime reads POINT positions/powers and maps watts to Unity intensity/range; it supplies its own blue fill. Blender world strength, exposure and area lighting are proof settings, so the native result needs a lead-sim capture.

Five BistroLook_WarmPool* lights illustrate table pools in Blender. They are stored only in **preview_only_lights**, outside the importable `lights` array: the runtime already lights each player-placed table. Do not import those five preview anchors or bake the review furniture into the room. The new jetty and lantern practicals remain in the importable array.

## Evidence and checks

- `bistro-look-review.jpg`: painting mood reference, native r123 BEFORE, and matching Blender BEFORE/AFTER, both empty and with illustrative layout tables.
- `bistro-look-phone-review.jpg`: the corresponding 844×390 comparisons. Eight original PNGs live in `bistro-look-renders/` at 1440×900 and 844×390; all eight and both sheets were opened.
- `bistro-look-Check.blend`: packed review scene with accepted sea1 backdrop and illustrative furniture. Production source is Stage2Bistro.blend.
- `validation.json`: fresh FBX mesh/triangle/bounds/material checks, two UV channels, positive UV1 triangle areas, no presentation meshes; PASS.
- `bistro-look-validation.json`: fresh FBX original-name/geometry preservation, 65 floor-centre ray checks, exact grid/camera metadata, unchanged V4 atlas, shallow runners, no fixed seats, metre export; PASS.
- `bistro-look-visual-review.json` and `bistro-look-final-audit.json`: opened-proof record, image decode/dimensions and package hashes.

The menu, two rugs, lights and warm/cool room separation read at phone size. The tall room wall, approved floor grid and visible stations remain intact. Blender comparisons use the same accepted sea and atlas vertex-colour multiplication on both sides; their populated tables are illustrative, not a simulation capture. Native AFTER lighting, material binding, layout interaction and final acceptance remain unverified here. No Assets/game-code/git changes, no commit.

## Reproduction and historical files

Run bistro-look-build.py with Windows Blender 5.2 to re-export the packed delivered source idempotently; then validate.py and bistro-look-audit.py. The latter uses retained compressed ORIGINAL geometry measurements once the temporary backup is removed. Run bistro-look-proof.py for AFTER views; BEFORE PNGs are retained evidence after backup removal. Sheet/seal assembly uses `/home/mo/.venvs/catchline-ui/bin/python bistro-look-package.py` (add `--seal` after visual review).

Temporary prechange backups were removed after verification. Historical build.py is pre-fit and must not overwrite this source. fit.py can export the packed corrected stages, but it is an earlier multi-stage pipeline; prefer the Bistro-only builder for this delivery. Old fit-audit and bistro-review files describe the accepted grid-fit milestone; their former hashes/counts are historical and superseded by the bistro-look audits for the current FBX. Atlas, layout and camera contracts remain the same.

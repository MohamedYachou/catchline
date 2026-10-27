# Stage4Seafood — STAGES-LOOK-2

Codex 2 (WSL CLI), 2026-10-27. Source delivery; native AFTER import/appearance remains Claude's check.

The accepted Bistro treatment now carries into this room: soft ivory/blue-grey kitchen tiles, varied darker timber, restrained plaster/stone pigment variation, two shallow bordered runners, framed wall menu, three herb pots, three stacked jetty crates, jetty and terrace festoons, two compact terrace lanterns and warm practical light pools. Colours use the existing V4 atlas, unchanged. UV cell remaps and LocalAO tint carry the pigment through the shared runtime material. The stage's original wall silhouette, kitchen, bar and special equipment are retained.

## Grid, names and export

Room **14×5m**, kitchen **5×5m**, open terrace **3×5m** along +Blender X. Same V4 origin and 1m tile: `(x,y)` maps to `[-4+x+.5,2.5-y-.5,.04]`. Room right X=10; terrace X=10..13. Door tile **(13,0)** enters through the side wall at Y=2. Front quay remains narrow with no seats. `layout.json` and `final-cameras.json` are byte-identical to the accepted grid-fit source.

All **154 original production meshes retain their names and world geometry**. Thirteen additive `StageLook2_*` nodes bring the export to **167 meshes / 77,293 triangles**. The floor geometry remains unchanged; runners top out at Z=.0535m, only13.5mm above its surface. Floor-standing cargo, lanterns and plants sit outside the approved grid; the small third herb is wall-sill mounted. No fixed usable seats added. Furniture in populated proofs is `REVIEW_` only and never enters the FBX. Original station/layout-hide names remain stable.

Exact V4 exporter: selected MESH only, `apply_unit_scale=True`, `apply_scale_options='FBX_SCALE_UNITS'`, `axis_forward='-Z'`, `axis_up='Y'`, `colors_type='LINEAR'`, `path_mode='RELATIVE'`, `bake_anim=False`. Independent FBX metadata confirms UnitScaleFactor=100; coordinates reimport in metres. Lighting keeps the `[x,z,-y]` convention; lead handles Unity's X mirror.

## Lighting handoff

Import `Stage4Seafood.fbx` and `lighting.json` together. Recipe contains **27 POINT practicals**, plus sun/area references. World strength=.18 and exposure=-.4EV are Blender proof settings. The runtime converts Blender watt recipes to Unity intensity/range and supplies its own fill, so the native image needs a lead-sim AFTER capture.

Five `StageLook2_WarmPool*` anchors illustrate table pools in Blender only. They live in **preview_only_lights**, outside the importable `lights` array. Runtime lights its player-placed tables; do not import these illustrative anchors or bake preview tables into the room. Added jetty/lantern practicals remain importable.

## Evidence and verification

- `stages-look2-review.jpg`: painting mood reference plus same-camera BEFORE/AFTER at1440×900, empty and with illustrative tier3 linen tables.
- `stages-look2-phone-review.jpg`: matching844×390 comparisons. Eight full PNGs in `stages-look2-renders/`.
- `stages-look2-Check.blend`: packed review scene, current accepted SEA-1C backdrop and illustrative furniture. Production source is `Stage4Seafood.blend`.
- `validation.json`: independent fresh FBX mesh/triangle/bounds/material checks, two UV channels, positive UV1 triangle areas, presentation meshes excluded; PASS.
- `stages-look2-validation.json`: all original geometry/names preserved, 85 floor-centre ray checks, unchanged approved layout/cameras/atlas, shallow runners, no fixed seats, exact metre export; PASS.
- `stages-look2-visual-review.json`: actual opened-image evidence and review limits.
- `stages-look2-final-audit.json`: image decode/dimensions and package SHA256 ledger.

Comparisons use identical sea, framing and vertex-colour multiplication on both sides. The populated views are illustrative source renders, not native simulation captures. Native AFTER material/light binding, guest paths, furniture interaction and acceptance remain Claude-owned. No Assets/game-code/git changes; no commit.

## Reproduction and historical evidence

With Windows Blender5.2 run `stages-look2-build.py` (idempotent on packed delivered source), `validate.py`, `stages-look2-audit.py`, then `stages-look2-proof.py`. The preservation audit uses retained compressed ORIGINAL geometry measurements after temporary backup cleanup. BEFORE PNGs remain evidence; rerunning proof after cleanup refreshes AFTER only. `/home/mo/.venvs/catchline-ui/bin/python stages-look2-package.py` assembles sheets; add `--seal` after recording actual visual opens.

Historical `build.py` produces the earlier pre-fit layout; do not overwrite this source with it. Previous fit/review/count/hash evidence describes the accepted grid-fit milestone and is superseded by current stages-look2 audits for this FBX. Approved atlas/grid/camera contracts remain identical. Temporary backups are removed only after successful checks and visual review.

## Visual review completed

Codex 2 opened all eight individual1440/844 BEFORE/AFTER renders and both sheets. Softer ivory kitchen pigment, darker timber, bordered runners, lit jetty/terrace dressing and retained station silhouettes read at phone scale. Illustrative linen tables remain proof-only. Native AFTER still requires lead-sim verification.

Proof-only shader correction: legacy meshes without LocalAO receive neutral white in the review scene before colour multiplication. Both comparison sides use this treatment; production FBX/source are unchanged. The seafood tank and unobstructed menu remain readable.

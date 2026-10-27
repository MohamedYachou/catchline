# JigRig — PropsV2 r01

New geometry in StationsV1 palette; earlier kit used as read-only reference.

Delivery: 2,116 triangles · 34 mesh parts · metres. Pivot/use: rail clamp contact. Runtime: `Assets/Art/Models/PropsV2/PropsV2_JigRig.fbx`.

Saved source and actual runtime export independently audited in `validation.json`.
Current delivery hashes, every world-space vertex in both directions, each part origin, material assignment/colours, mesh counts, finite bounds, metre scale and protected reference hashes checked. Review: `review-sheet.png`;
source/tool snapshots and individual angle renders under `iterations/r01/`.

Maximum actual FBX bounds error: 1.7881393432617188e-07 m. Maximum vertex error: 2.1542358837725164e-07 m; part-origin error: 1.4901161193847656e-07 m. Source Z-up / -Y front; FBX -Z forward / Y up.

Read-only provenance:
- `Art/Source/Art108/build_stations.py` — read-only chunky primitive/palette reference; SHA256 `6703d4f4fdd89ab5b6e72dc010e40e565405640dd182cd7dede719c4e88eeb57`.

The existing kit is preserved. Derivative geometry is declared rather than claimed
as a new sculpt. Native Unity import, materials/alpha mode, placement and event or
lamp behaviour remain untested; no scenes or game code changed. Final visual
inspection status is recorded separately in canonical `comms.md`. No Mo acceptance claimed.

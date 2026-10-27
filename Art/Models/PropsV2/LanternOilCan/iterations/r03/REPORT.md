# LanternOilCan — PropsV2 r03

New geometry in StationsV1 palette; earlier kit used as read-only reference. Horizontal bounds centred and lowest contact set to zero for floor placement.

Delivery: 914 triangles · 12 mesh parts · metres. Pivot/use: floor/contact. Runtime: `Assets/Art/Models/PropsV2/PropsV2_LanternOilCan.fbx`.

Saved source and actual runtime export independently audited in `validation.json`.
Current delivery hashes, every world-space vertex in both directions, each part origin, material assignment/colours, mesh counts, finite bounds, metre scale and protected reference hashes checked. Review: `review-sheet.png`;
source/tool snapshots and individual angle renders under `iterations/r03/`.

Maximum actual FBX bounds error: 6.705522537231445e-08 m. Maximum vertex error: 7.210536109012275e-08 m; part-origin error: 6.565824151039124e-08 m. Source Z-up / -Y front; FBX -Z forward / Y up.

Read-only provenance:
- `Art/Source/Art108/build_stations.py` — read-only chunky primitive/palette reference; SHA256 `6703d4f4fdd89ab5b6e72dc010e40e565405640dd182cd7dede719c4e88eeb57`.

The existing kit is preserved. Derivative geometry is declared rather than claimed
as a new sculpt. Native Unity import, materials/alpha mode, placement and event or
lamp behaviour remain untested; no scenes or game code changed. Final visual
inspection status is recorded separately in canonical `comms.md`. No Mo acceptance claimed.

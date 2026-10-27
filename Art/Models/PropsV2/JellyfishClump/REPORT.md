# JellyfishClump — PropsV2 r02

Reuses named StationsV1 geometry; adds visible rope landing net. Horizontal bounds centred and lowest contact set to zero for floor placement.

Delivery: 4,168 triangles · 38 mesh parts · metres. Pivot/use: floor/contact. Runtime: `Assets/Art/Models/PropsV2/PropsV2_JellyfishClump.fbx`.

Saved source and actual runtime export independently audited in `validation.json`.
Current delivery hashes, every world-space vertex in both directions, each part origin, material assignment/colours, mesh counts, finite bounds, metre scale and protected reference hashes checked. Review: `review-sheet.png`;
source/tool snapshots and individual angle renders under `iterations/r02/`.

Maximum actual FBX bounds error: 7.450580596923828e-08 m. Maximum vertex error: 8.429369702178807e-08 m; part-origin error: 4.470348358154297e-08 m. Source Z-up / -Y front; FBX -Z forward / Y up.

Read-only provenance:
- `Art/Models/StationsV1/JellyfishClump.blend` — existing named A6 geometry derivative; SHA256 `f6cf0df1e11d6bd6e4452c0b82bcea36b079823b3349c470bd4f75fadd37eee7`.

The existing kit is preserved. Derivative geometry is declared rather than claimed
as a new sculpt. Native Unity import, materials/alpha mode, placement and event or
lamp behaviour remain untested; no scenes or game code changed. Final visual
inspection status is recorded separately in canonical `comms.md`. No Mo acceptance claimed.

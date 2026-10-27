# TableEel — PropsV2 r01

Reuses named StationsV1 geometry; fresh export and evidence, no claim of new sculpt. Horizontal bounds centred and lowest contact set to zero for floor placement.

Delivery: 948 triangles · 4 mesh parts · metres. Pivot/use: floor/contact. Runtime: `Assets/Art/Models/PropsV2/PropsV2_TableEel.fbx`.

Saved source and actual runtime export independently audited in `validation.json`.
Current delivery hashes, every world-space vertex in both directions, each part origin, material assignment/colours, mesh counts, finite bounds, metre scale and protected reference hashes checked. Review: `review-sheet.png`;
source/tool snapshots and individual angle renders under `iterations/r01/`.

Maximum actual FBX bounds error: 1.4901161193847656e-08 m. Maximum vertex error: 3.332000937312528e-08 m; part-origin error: 1.4901161193847656e-08 m. Source Z-up / -Y front; FBX -Z forward / Y up.

Read-only provenance:
- `Art/Models/StationsV1/TableEel.blend` — existing named A6 geometry derivative; SHA256 `a8f98454e6cc7edef8a7e92b3746fdc528924acd62c11400fe58a55989e1c6a5`.

The existing kit is preserved. Derivative geometry is declared rather than claimed
as a new sculpt. Native Unity import, materials/alpha mode, placement and event or
lamp behaviour remain untested; no scenes or game code changed. Final visual
inspection status is recorded separately in canonical `comms.md`. No Mo acceptance claimed.

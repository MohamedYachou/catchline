# RivalBoat — PropsV2 r01

Reuses the existing red rowboat model; no invented rival hull.

Delivery: 1,790 triangles · 10 mesh parts · metres. Pivot/use: inherited rowboat deck centre; suggested waterline Z=-0.32m. Runtime: `Assets/Art/Models/PropsV2/PropsV2_RivalBoat.fbx`.

Saved source and actual runtime export independently audited in `validation.json`.
Current delivery hashes, every world-space vertex in both directions, each part origin, material assignment/colours, mesh counts, finite bounds, metre scale and protected reference hashes checked. Review: `review-sheet.png`;
source/tool snapshots and individual angle renders under `iterations/r01/`.

Maximum actual FBX bounds error: 4.172325134277344e-07 m. Maximum vertex error: 4.172325134277344e-07 m; part-origin error: 1.4901161193847656e-07 m. Source Z-up / -Y front; FBX -Z forward / Y up.

Read-only provenance:
- `Assets/Art/Models/Harbour/Rowboat_VariantRed.fbx` — existing named rival-boat derivative; SHA256 `dee4e5c5b397eec9caeb2040256d0d8f9af2be25de410578eeeae0bbfb007f1c`.

The existing kit is preserved. Derivative geometry is declared rather than claimed
as a new sculpt. Native Unity import, materials/alpha mode, placement and event or
lamp behaviour remain untested; no scenes or game code changed. Final visual
inspection status is recorded separately in canonical `comms.md`. No Mo acceptance claimed.

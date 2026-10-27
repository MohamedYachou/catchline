# RepairKit — JIG-ART-1

Artist delivery by Codex 2 (WSL CLI). 1156/2500 triangles. Source/actual-FBX audits PASS; every final image below individually opened. No Unity/native validation, installation or git operation.

[Source](RepairKit.blend) · [Export](RepairKit.fbx) · [Build metrics](metrics/build.json) · [Actual FBX audit](metrics/audit.json) · [Image review](visual-review.json) · [Manifest](renders/manifest.json) · [Review scene](RepairKit-assembly-review.blend) · [Receipt](delivery-receipt.json)

## Integration contract

All four sibling meshes attach independently under RepairKit, zero object origins/unit scale, metres. Blender Z/up, -Y/front; FBX -Z forward/Y up. No rigs/clips/textures/lights/cameras in production.

| Child | Tris | Contract |
| --- | ---: | --- |
| TornNet |432| Panel-centre origin, lies in XY plane. Centreline1.2x.8m, outer cord bounds1.212x.812m, cord thickness12mm. Green-grey diamond mesh with real ragged~30cm centre opening. |
| MendedPatch |80| Same centre origin and plane; tan diamond cords exactly replace clipped ragged segments. Overlay at zero local translation to close the hole. Width~.311m. |
| NettingNeedle |254| Tip origin, points along+X, extends-.2m; open eye, five wound tan twine wraps, width~30mm including winding. Shared M_Twine warm wood/twine palette. |
| TwineBall |390| Bottom/base origin,10cm core plus wound strands and loose tail extending to+.089m X. Overall bounding width14cm including tail; wraps protrude.56mm below base. |

M_NetGreenGrey and M_Twine shared materials only. The patch is complementary geometry, so show it at TornNet's origin after the mend; no opaque hole plug. The isolated assembly shows the torn state, with patch alongside at(-.8,.2,.015), needle and ball on the panel. Camera55degrees down, horizontal1.88m span; panel fills~64%width at both1440x900 and844x390. Studio front/back/right are expected near-edge-on views of the flat net. Gameplay alignment, repair progress, shaders/native acceptance belong to Claude.

## Validation and reproduction

Source hierarchy, metre bounds/pivots, budgets, finite/nonzero-area geometry, allowed materials, texture independence and actual FBX ordered polygon/vertex surface equivalence PASS. Static maximum export vertex error 0.000000031m; sampled deformations match within20micrometres where applicable. No production changes after final audit. Build/audit logs and source receipts bind current files.

Shared deterministic scripts live in Art/Source/JigKit; RepairKit source entry is Art/Source/RepairKit/README.md. Run `python3 Art/Source/JigKit/run.py build,audit,render RepairKit` from project root using Windows Blender5.2. This regenerates assets/evidence and requires a fresh image review. Read-only dependency hashes are recorded in metrics/dependencies.json. No backup needed for initial additive delivery; temporary mote revision backups removed after verified correction.

## Final evidence

- [renders/TornNet/front.png](renders/TornNet/front.png)
- [renders/TornNet/back.png](renders/TornNet/back.png)
- [renders/TornNet/right.png](renders/TornNet/right.png)
- [renders/TornNet/top.png](renders/TornNet/top.png)
- [renders/TornNet/three-quarter.png](renders/TornNet/three-quarter.png)
- [renders/MendedPatch/front.png](renders/MendedPatch/front.png)
- [renders/MendedPatch/back.png](renders/MendedPatch/back.png)
- [renders/MendedPatch/right.png](renders/MendedPatch/right.png)
- [renders/MendedPatch/top.png](renders/MendedPatch/top.png)
- [renders/MendedPatch/three-quarter.png](renders/MendedPatch/three-quarter.png)
- [renders/NettingNeedle/front.png](renders/NettingNeedle/front.png)
- [renders/NettingNeedle/back.png](renders/NettingNeedle/back.png)
- [renders/NettingNeedle/right.png](renders/NettingNeedle/right.png)
- [renders/NettingNeedle/top.png](renders/NettingNeedle/top.png)
- [renders/NettingNeedle/three-quarter.png](renders/NettingNeedle/three-quarter.png)
- [renders/TwineBall/front.png](renders/TwineBall/front.png)
- [renders/TwineBall/back.png](renders/TwineBall/back.png)
- [renders/TwineBall/right.png](renders/TwineBall/right.png)
- [renders/TwineBall/top.png](renders/TwineBall/top.png)
- [renders/TwineBall/three-quarter.png](renders/TwineBall/three-quarter.png)
- [renders/Assembly/assembly-1440.png](renders/Assembly/assembly-1440.png)
- [renders/Assembly/assembly-844.png](renders/Assembly/assembly-844.png)

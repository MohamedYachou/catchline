# JigKit — JIG-ART-1

Artist delivery by Codex 2 (WSL CLI). 856/2500 triangles. Source/actual-FBX audits PASS; every final image below individually opened. No Unity/native validation, installation or git operation.

[Source](JigKit.blend) · [Export](JigKit.fbx) · [Build metrics](metrics/build.json) · [Actual FBX audit](metrics/audit.json) · [Image review](visual-review.json) · [Manifest](renders/manifest.json) · [Review scene](JigKit-assembly-review.blend) · [Receipt](delivery-receipt.json)

## Integration contract

All six children attach independently under JigKit. All object origins are zero with unit scale. Blender X/right, -Y/front, Z/up; FBX -Z forward / Y up, metres. Production geometry has no lights, cameras, textures or review ground.

| Child | Tris | Contract |
| --- | ---: | --- |
| JigPirk |244| Eye-contact origin; hangs down local Blender -Z, 140mm tip depth, 0.286mm wire clearance below pivot. Slim silver faceted body, blue spine, split eye ring and three tail hook branches. |
| JigFeathers |196| Top swivel-contact origin, 200mm drop, three orange/ivory/yellow feather hooks. |
| JigLine |12| Top origin, down -Z exactly1m; square4mm cross-section. Scale length in runtime. |
| KelpStrand > KelpRibbon |60| Armature/holdfast origin, rest2.5m tall; three bones Kelp_0 > Kelp_1 > Kelp_2, normalized skin weights. |
| SeabedRocks |244| Sand-base centre origin, 3x2m patch, four irregular fractured slabs with broad split tops and raked shoulders; highest point0.8106m. M_Steel is earlier WorldPolish rock grey. |
| MoteCloud |100| Volume-centre origin,50 flat quads, seeded full3D orientation in2m cube; runtime scroll. |

Sway is a4s cyclic action, frames1–121 at30fps, no rig/root translation. Actual FBX reimport names it KelpStrand|KelpStrand|Sway; select suffix Sway and configure Unity Legacy+Loop at import. Root armature stays fixed; about.313m maximum sampled ribbon movement; matching endpoints. Render ribbons/motes and feather planes with two-sided shared materials; they are deliberately flat. Material names/linear colors are in audit.json, authored hex palette in build.json. M_FishSilver is material-driven silver; runtime shader supplies metal response.

Assembly is an isolated water-column fixture, horizontal5.2m span, about2.29degrees down, with the lure centred. Pirk and feather review scale2, kelp.75, rocks.85, motes1.3; source meshes remain at specified metre sizes. Phone framing clips the sand/base and line top as a close-up does. Production gradient/fog, fish, scrolling and interaction are Claude-owned. Full three-hook silhouette is established in studio closeups; hooks are small at scene scale.

## Validation and reproduction

Source hierarchy, metre bounds/pivots, budgets, finite/nonzero-area geometry, allowed materials, texture independence and actual FBX ordered polygon/vertex surface equivalence PASS. Static maximum export vertex error 0.000000407m; sampled deformations match within20micrometres where applicable. No production changes after final audit. Build/audit logs and source receipts bind current files.

Shared deterministic scripts live in Art/Source/JigKit; RepairKit source entry is Art/Source/RepairKit/README.md. Run `python3 Art/Source/JigKit/run.py build,audit,render JigKit` from project root using Windows Blender5.2. This regenerates assets/evidence and requires a fresh image review. Read-only dependency hashes are recorded in metrics/dependencies.json. No backup needed for initial additive delivery; temporary mote revision backups removed after verified correction.

## Final evidence

- [renders/JigPirk/front.png](renders/JigPirk/front.png)
- [renders/JigPirk/back.png](renders/JigPirk/back.png)
- [renders/JigPirk/right.png](renders/JigPirk/right.png)
- [renders/JigPirk/top.png](renders/JigPirk/top.png)
- [renders/JigPirk/three-quarter.png](renders/JigPirk/three-quarter.png)
- [renders/JigFeathers/front.png](renders/JigFeathers/front.png)
- [renders/JigFeathers/back.png](renders/JigFeathers/back.png)
- [renders/JigFeathers/right.png](renders/JigFeathers/right.png)
- [renders/JigFeathers/top.png](renders/JigFeathers/top.png)
- [renders/JigFeathers/three-quarter.png](renders/JigFeathers/three-quarter.png)
- [renders/JigLine/front.png](renders/JigLine/front.png)
- [renders/JigLine/back.png](renders/JigLine/back.png)
- [renders/JigLine/right.png](renders/JigLine/right.png)
- [renders/JigLine/top.png](renders/JigLine/top.png)
- [renders/JigLine/three-quarter.png](renders/JigLine/three-quarter.png)
- [renders/KelpStrand/front.png](renders/KelpStrand/front.png)
- [renders/KelpStrand/back.png](renders/KelpStrand/back.png)
- [renders/KelpStrand/right.png](renders/KelpStrand/right.png)
- [renders/KelpStrand/top.png](renders/KelpStrand/top.png)
- [renders/KelpStrand/three-quarter.png](renders/KelpStrand/three-quarter.png)
- [renders/KelpStrand/Sway-0.png](renders/KelpStrand/Sway-0.png)
- [renders/KelpStrand/Sway-1.png](renders/KelpStrand/Sway-1.png)
- [renders/KelpStrand/Sway-2.png](renders/KelpStrand/Sway-2.png)
- [renders/KelpStrand/Sway-3.png](renders/KelpStrand/Sway-3.png)
- [renders/KelpStrand/Sway-4.png](renders/KelpStrand/Sway-4.png)
- [renders/MoteCloud/front.png](renders/MoteCloud/front.png)
- [renders/MoteCloud/back.png](renders/MoteCloud/back.png)
- [renders/MoteCloud/right.png](renders/MoteCloud/right.png)
- [renders/MoteCloud/top.png](renders/MoteCloud/top.png)
- [renders/MoteCloud/three-quarter.png](renders/MoteCloud/three-quarter.png)
- [renders/SeabedRocks/front.png](renders/SeabedRocks/front.png)
- [renders/SeabedRocks/back.png](renders/SeabedRocks/back.png)
- [renders/SeabedRocks/right.png](renders/SeabedRocks/right.png)
- [renders/SeabedRocks/top.png](renders/SeabedRocks/top.png)
- [renders/SeabedRocks/three-quarter.png](renders/SeabedRocks/three-quarter.png)
- [renders/Assembly/assembly-1440.png](renders/Assembly/assembly-1440.png)
- [renders/Assembly/assembly-844.png](renders/Assembly/assembly-844.png)

## Accepted-delivery rock correction

Four repeated rounded primitives replaced with authored irregular slabs. [Scoped comparison](metrics/rocks-revision.json) proves every other mesh, skin, rig and original Sway curve unchanged; their30 previously opened image reviews carry forward. Five revised rock studios and both assemblies regenerated and individually opened. Repair model/evidence/report unchanged; both receipts rebound only because authoring scripts are shared. Temporary pre-rocks backup removed after successful audit and visual preflight.

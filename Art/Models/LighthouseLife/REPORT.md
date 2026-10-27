# Lighthouse Life — LIGHTHOUSE-LIFE-1

Codex 2 (WSL CLI). Four independently exportable metre-scale assets. All four source/actual-FBX audits PASS; all 32 final images individually opened and hash-bound. Native Unity/Legacy/shader/map placement acceptance belongs to Claude.

- **Puffin**: [blend](Puffin.blend), [FBX](Puffin.fbx), [build metrics](metrics/Puffin-build.json), [actual FBX audit](metrics/Puffin-audit.json). 310 triangles, 198 vertices; Unity bounds size 0.1660, 0.3000, 0.2520 m.
- **PuffinGroup**: [blend](PuffinGroup.blend), [FBX](PuffinGroup.fbx), [build metrics](metrics/PuffinGroup-build.json), [actual FBX audit](metrics/PuffinGroup-audit.json). 974 triangles, 618 vertices; Unity bounds size 1.2000, 0.5070, 0.6500 m.
- **TideRace**: [blend](TideRace.blend), [FBX](TideRace.fbx), [build metrics](metrics/TideRace-build.json), [actual FBX audit](metrics/TideRace-audit.json). 168 triangles, 204 vertices; Unity bounds size 6.0000, 0.2192, 2.0000 m.
- **LighthouseGlow**: [blend](LighthouseGlow.blend), [FBX](LighthouseGlow.fbx), [build metrics](metrics/LighthouseGlow-build.json), [actual FBX audit](metrics/LighthouseGlow-audit.json). 64 triangles, 50 vertices; Unity bounds size 12.4500, 1.4600, 1.4600 m.

[Individual image review](visual-review.json) · [Read-only dependencies](metrics/dependencies.json) · [Assembly manifest](renders/Assembly.json) · [Isolated assembly review scene](LighthouseLife-assembly-review.blend) · [Final receipt](delivery-receipt.json)

## Common import contract

Logical root empty named exactly as the asset, origin zero, unit scales. Blender X/right, -Y/forward, Z/up; FBX -Z-forward/Y-up exports map to Unity X/right, +Z/forward, +Y/up in metres. No cameras, lights, textures or review floor in production. Material names/linear RGBA are in each audit; authored hex palette is in each build metric. Meshes are faceted. All static models have no actions/rigs.

## Puffin

`Puffin > PuffinRig > PuffinSkin`. 310/600 triangles, five bones `Root > Body > Head / Wing.L / Wing.R`. Logical root pivot between feet, standing height 0.300 m. Orange webbed feet are weighted to stationary Root; black back/wing/cap, white cheeks and belly. Broad bill uses steel/white collar, orange-red body and yellow band as actual geometry; no texture. Eyes/eye marks fit actual faceted cheeks. Feet at ground plane; no root motion.

Two actions at 30 fps: **Idle** frames 1–91, 3 s loop, small body bob/head turn; **Flap** frames 1–13, 0.4 s loop, wings extended and flapping. Export names may be `PuffinRig|PuffinRig|Idle`/`...|Flap`; select suffix. Configure **Legacy + Loop** in Unity. Flap is already wings-out at frame 1, so runtime may crossfade from Idle if desired. Root transforms remain fixed at every integer frame. Five surface samples/clip match actual FBX within 20 micrometres; matching endpoints and nonzero intermediate movement checked independently. Source sampled maximum motion: Idle 0.03974m; Flap 0.07939m.

## PuffinGroup

`PuffinGroup > PuffinGroupMesh`, 974 triangles. Three full 310-triangle puffins facing slightly different directions on one 44-triangle angular granite ledge, 1.2 m across, 0.65 m deep. Pivot at ledge base; top is slightly slanted, each bird placed by foot centre at ledge height (about 1.5 mm or less slope variation across feet). This is a **static**, single-mesh cheap perch group. Spawn independent animated Puffin at other perches when movement is wanted; the individual model is supplied separately. No borrowed terrain or anchor objects.

## TideRace

`TideRace > TideRaceMesh`, 168 triangles, exact 6 x 2 m footprint, base waterline centre pivot. Twelve staggered tapered fragments with low standing-wave facets and white crest strips lying on sloping faces. Maximum crest 0.22325m, below 0.25 m. White bands are offset only 0.6 mm to avoid z-fighting; no vertical foam fins. Shared `M_WaterTeal #2E8C8A` and `M_GullWhite #F1F0EA`, opaque two-sided surface materials. Runtime scrolls/tiles local X; hide or crossfade copies at band ends. Geometry starts 4 mm above waterline; runtime positions root on the water.

## LighthouseGlow

`LighthouseGlow > LanternCross / LanternBeam`, 64 triangles. Root is **lantern centre**, not beam tip. Beam runs local +X in Blender and Unity, exactly 12 m from source to end, radius 0.045 m at source / 0.73 m at end. Crossed XZ/YZ lantern cards are 0.9 m across, subdivided for soft centre-to-edge falloff. Whole asset span 12.45 m includes the negative-X half of the cross.

Shared **M_LampGlow #FFE7A3**. Texture-free `GlowAlpha` vertex color: soft centre/zero card edges, beam decreasing to zero at 12 m. Source uses transparent/emission nodes; export carries matching RGB, Principled opacity 0.2, emission and byte vertex colors. **FBX does not carry Blender's node graph.** Runtime should bind an unlit additive/two-sided material, vertex alpha multiplied into emission/opacity, depth writing off; use vertex alpha directly (do not multiply the export opacity 0.2 twice). Byte-color source/actual-FBX alpha matches exactly by world-position. No image dependency. Rotate root about Unity Y for the sweep. Blender evidence shows source falloff, not proof of Unity bloom/additive material acceptance.

## Assembly and visual review

Two isolated fixtures at 1440x900 and 844x390 show the three birds on their ledge beside the tide race, unit source scales. Accepted WreckLife/Skerries deck direction (.574,-.819,1), 45 degrees down; orthographic framing fits the worst landscape aspect. Exact span, placement and projected crop bounds are in [Assembly manifest](renders/Assembly.json). Only Group and TideRace participate, as briefed; glow and single-bird actions have their own studios. Tide and ledge are isolated examples; actual MAP8 water, terrain, anchors, HUD and animation timing remain external. Five true orthographic directions per asset retain edge-on wave and end-on beam views.

## Verification and reproduction

Source geometry is finite, fully referenced, nonzero-area, texture-independent and within budgets. Actual FBX reimport validates hierarchy, transforms, metre bounds, material RGBA, every ordered polygon cycle/multiplicity, and source/FBX surfaces. Worst static vertex error 0.0000000843m. Both clips checked at every integer frame for root stability and five sampled deformed surfaces. Glow RGB/Principled opacity and vertex alpha survive actual import. Source/FBX bytes match audit SHA256. Studio/assembly crop assertions passed at final render; every final PNG opened individually.

Deterministic authoring/audit/render runner: `python3 Art/Source/LighthouseLife/run.py build,audit,render Puffin PuffinGroup TideRace LighthouseGlow` then `python3 Art/Source/LighthouseLife/run.py render Assembly`, Windows Blender 5.2. Final image review must be repeated after regeneration, then review.py/document.py/finalize.py. The initial tile-grid tide preview and floating cheek eyes were rejected; owned pre-refine backup removed only after final visual/receipt preflight. Read-only dependency hashes protect shared helper/reference/design files; no Unity, Assets, git or player-save writes were performed.

## Final evidence

- [renders/Assembly/deck-1440.png](renders/Assembly/deck-1440.png)
- [renders/Assembly/deck-844.png](renders/Assembly/deck-844.png)
- [renders/LighthouseGlow/back.png](renders/LighthouseGlow/back.png)
- [renders/LighthouseGlow/front.png](renders/LighthouseGlow/front.png)
- [renders/LighthouseGlow/right.png](renders/LighthouseGlow/right.png)
- [renders/LighthouseGlow/three-quarter.png](renders/LighthouseGlow/three-quarter.png)
- [renders/LighthouseGlow/top.png](renders/LighthouseGlow/top.png)
- [renders/Puffin/action-Flap-0.png](renders/Puffin/action-Flap-0.png)
- [renders/Puffin/action-Flap-1.png](renders/Puffin/action-Flap-1.png)
- [renders/Puffin/action-Flap-2.png](renders/Puffin/action-Flap-2.png)
- [renders/Puffin/action-Flap-3.png](renders/Puffin/action-Flap-3.png)
- [renders/Puffin/action-Flap-4.png](renders/Puffin/action-Flap-4.png)
- [renders/Puffin/action-Idle-0.png](renders/Puffin/action-Idle-0.png)
- [renders/Puffin/action-Idle-1.png](renders/Puffin/action-Idle-1.png)
- [renders/Puffin/action-Idle-2.png](renders/Puffin/action-Idle-2.png)
- [renders/Puffin/action-Idle-3.png](renders/Puffin/action-Idle-3.png)
- [renders/Puffin/action-Idle-4.png](renders/Puffin/action-Idle-4.png)
- [renders/Puffin/back.png](renders/Puffin/back.png)
- [renders/Puffin/front.png](renders/Puffin/front.png)
- [renders/Puffin/right.png](renders/Puffin/right.png)
- [renders/Puffin/three-quarter.png](renders/Puffin/three-quarter.png)
- [renders/Puffin/top.png](renders/Puffin/top.png)
- [renders/PuffinGroup/back.png](renders/PuffinGroup/back.png)
- [renders/PuffinGroup/front.png](renders/PuffinGroup/front.png)
- [renders/PuffinGroup/right.png](renders/PuffinGroup/right.png)
- [renders/PuffinGroup/three-quarter.png](renders/PuffinGroup/three-quarter.png)
- [renders/PuffinGroup/top.png](renders/PuffinGroup/top.png)
- [renders/TideRace/back.png](renders/TideRace/back.png)
- [renders/TideRace/front.png](renders/TideRace/front.png)
- [renders/TideRace/right.png](renders/TideRace/right.png)
- [renders/TideRace/three-quarter.png](renders/TideRace/three-quarter.png)
- [renders/TideRace/top.png](renders/TideRace/top.png)

# GUT-ART-1 — close-up gutting kit

Codex 2 (WSL CLI), 2026-10-25. Artist delivery complete; Unity import, Legacy clip setup and gameplay acceptance belong to Claude. Studio and assembly frames are isolated Blender evidence.

[Editable kit](GutKit.blend) · [FBX](GutKit.fbx) · [Camera fixture](GutKit-camera-fixture.blend)

## Items and budgets

All six named items share zero origins intentionally. Hide unused children before displaying one; clean source/export overlaps them for modular instantiation. Sizes below use Unity local **X × Y × Z**, metres.

| Item | Tris / limit | Overall bounds, m | Pivot / use |
|---|---:|---|---|
| GutBoard | 277 / 900 | 0.7000 × 0.1013 × 0.3600 | Worktop centre Y=0; 0.70 × 0.36 substrate extends down 42mm; 4mm edge groove; steel clamp at +X rises to59.3mm. Place fish on Y=0, head toward +X. |
| GutKnife | 104 / 300 | 0.2868 × 0.0320 × 0.0460 | Blade tip at0; handle extends -X, blade lies in XZ plane. Translate tip along cut; rotate local +Y to aim -X handle behind tip. |
| BellyOpen | 72 / 200 | 1.0000 × 0.0080 × 0.0900 | Vent at X=0 to gills X=1, faces +Y. Multiply X scale by cut length in metres; Z sets width. Thin4–12mm raised flesh/cavity. |
| BellyRagged | 72 / 200 | 1.0000 × 0.0080 × 0.1166 | Same pivot/length as BellyOpen, alternating torn outer lip. Toggle clean versus ragged explicitly. |
| GutBucket | 292 / 500 | 0.2940 × 0.2970 × 0.3060 | Base centre Y=0; open top +Y; steel bucket with folded handle and3 dark offal lumps. |
| GullPerch (GullSkin) | 580 / 1500 | 0.2200 × 0.4370 × 0.4720 | Instantiate GullPerch subtree. Between feet Y=0, faces +Z; folded wings. Four-bone GullRig drives GullSkin. |

Total **1,397 triangles**. No textures, external images, cameras, lights, fish or table in the clean source/export. The six items are named direct children of GutKit; GullPerch contains GullRig → GullSkin.

## Axes, materials and actions

Blender authoring is Z-up. Unity coordinates are `(Blender X, Blender Z, -Blender Y)`. FBX declares Y-up, UnitScaleFactor100cm per geometric unit, with the standard root conversion retained for the animated rig. World geometry/zero pivots verified directly from raw FBX transforms and fresh FBX reimport; do not rotate another90 degrees or compensate with scale100. Configure Unity Model scale1 and Animation Type Legacy, matching Seal. No Unity import settings are authored here.

Materials use only the permitted names; map by slot name to shared game materials. Matte steel matches the existing GuttingTable palette.

| Slot | sRGB |
|---|---|
| M_DeckWood | #C58B50 |
| M_WoodRecess | #8C5A36 |
| M_Steel | #8FA6AC |
| M_SafetyOrange | #E36A35 |
| M_RailIvory | #F3F0DC |
| M_Rubber | #28343B |
| M_Flesh | #E8B4A0 |
| M_Offal | #6E2A2A |
| M_GullWhite | #F1F0EA |
| M_GullGrey | #9AA6AD |

Gull actions: **Idle**, frames1–121 at30fps (4s), loop; **Lunge**, frames1–31 (1s), one-shot returning to perch. Exported FBX take names carry the armature prefix (`GullRig|Idle`, `GullRig|Lunge`); expose them as Idle/Lunge when importing. Idle breathes and looks; Lunge tips body/neck/head toward +Z while feet stay fixed. Lunge max sampled vertex travel0.278m; no root translation. Four bones Root/Body/Neck/Head; weights sum1. FBX baked every frame; import Legacy, loop Idle only.

## Opened evidence

Five1000×800 orthographic studio views per item, front toward Unity -Z, right from +X. Thin inserts are deliberately edge-on in front/back.

| Item | Three-quarter | Front | Right | Back | Top |
|---|---|---|---|---|---|
| GutBoard | [three-quarter](renders/GutBoard/three-quarter.png) | [front](renders/GutBoard/front.png) | [right](renders/GutBoard/right.png) | [back](renders/GutBoard/back.png) | [top](renders/GutBoard/top.png) |
| GutKnife | [three-quarter](renders/GutKnife/three-quarter.png) | [front](renders/GutKnife/front.png) | [right](renders/GutKnife/right.png) | [back](renders/GutKnife/back.png) | [top](renders/GutKnife/top.png) |
| BellyOpen | [three-quarter](renders/BellyOpen/three-quarter.png) | [front](renders/BellyOpen/front.png) | [right](renders/BellyOpen/right.png) | [back](renders/BellyOpen/back.png) | [top](renders/BellyOpen/top.png) |
| BellyRagged | [three-quarter](renders/BellyRagged/three-quarter.png) | [front](renders/BellyRagged/front.png) | [right](renders/BellyRagged/right.png) | [back](renders/BellyRagged/back.png) | [top](renders/BellyRagged/top.png) |
| GutBucket | [three-quarter](renders/GutBucket/three-quarter.png) | [front](renders/GutBucket/front.png) | [right](renders/GutBucket/right.png) | [back](renders/GutBucket/back.png) | [top](renders/GutBucket/top.png) |
| GullPerch | [three-quarter](renders/GullPerch/three-quarter.png) | [front](renders/GullPerch/front.png) | [right](renders/GullPerch/right.png) | [back](renders/GullPerch/back.png) | [top](renders/GullPerch/top.png) |

Lunge sampled frames: [1](renders/action/Lunge-01.png), [8](renders/action/Lunge-08.png), [16](renders/action/Lunge-16.png), [23](renders/action/Lunge-23.png), [31](renders/action/Lunge-31.png).

Assembly: [1440×900](renders/assembly/gut-view-1440.png), [844×390](renders/assembly/gut-view-844.png). Camera0.9m above board,60° down,55° horizontal FOV retained at both aspect ratios. Existing GuttingTable appended read-only; canonical Fish043 Mackerel laid on its side at1.5× (~0.51m), fitted0.25m BellyOpen cut; knife, bucket and gull complete the context. Fixture placements are in [assembly.json](assembly.json). Fish meshes stay canonical and uncut: insert is an overlay and runtime should hide/interpolate it as appropriate.

## Checks and reproduction

[Actual FBX geometry/material/animation audit](metrics/roundtrip.json), [raw axes and units](metrics/fbx-axes.json), [independent camera/framing/protected-reference check](metrics/fixture-audit.json), [build bounds](metrics/build.json), [reference hashes](metrics/references.json), [individual image receipt](visual-review.json), [delivery inventory](delivery-receipt.json). Every exported rest mesh and ten sampled deformed poses match source within20µm; hierarchy/materials/weights/triangle budgets pass. Every final image was individually opened. Native HUD and actual Legacy playback remain untested.

From project root: `python3 Art/Source/GutKit/run.py build audit axes render fixture_audit`. Installed Windows Blender5.2 is launched sequentially with explicit completion markers. Rebuilds require fresh image review and finalization. [Builder](../../Source/GutKit/build.py), [FBX audit](../../Source/GutKit/audit.py), [renderer](../../Source/GutKit/render.py), [fixture audit](../../Source/GutKit/fixture_audit.py), [finalizer](../../Source/GutKit/finalize.py).

Read-only SortingBoard, GuttingTable, canonical Mackerel and Seal hashes remain unchanged. No Unity/Assets/runtime/save/git changes or native acceptance claimed.

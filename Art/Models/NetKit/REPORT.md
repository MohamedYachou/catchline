# NET-ART-1 — net kit

Delivered 2026-10-25 by **Codex 2 (WSL CLI)**. Artist delivery complete: two clean source/export pairs, three usable meshes, Slack/Taut bag controls and 24 individually opened final evidence images. Unity import, shader remapping and `VoyageNetView` integration remain Claude's work; the camera evidence is an isolated artist fixture, not native gameplay acceptance.

## Files and budgets

| Mesh | Source / export | Actual triangles | Bounds X × Y × Z, metres |
|---|---|---:|---|
| NetBunt / Bunt, Slack | [blend](NetBunt.blend) / [FBX](NetBunt.fbx) | 2,086 (<2,500) | 1.1113 × 0.7870 × 0.7834 |
| NetBunt / Bunt, Taut | same pair, `Taut` shape key | same topology | 0.9913 × 0.7171 × 1.0480 |
| NetPanelSet / NetPanel | [blend](NetPanelSet.blend) / [FBX](NetPanelSet.fbx) | 662 (<800) | 2.3880 × 0.0975 × 1.0420 |
| NetPanelSet / NetHeap | same pair | 680 (<800) | 0.6569 × 0.1903 × 0.5771 |

Panel and heap each meet the brief's 800-triangle limit; their combined export contains 1,342 triangles. Exported source geometry includes float/rope thickness, so the bunt's nominal 0.7m body reaches 0.783m overall depth. There are no textures, alpha cutouts, rigs, animation clips, modifiers or external material/image dependencies in the two asset pairs. Mesh openings are real modeled cords.

## Integration contract

All coordinates below are **Unity local metres**, +Y up, scale `(1,1,1)`. FBX raw mesh coordinates are baked Y-up with identity model rotations/scales, one metre per geometric unit (`UnitScaleFactor=100` centimetres per FBX unit). Independent raw-axis and geometry round-trip checks passed. Blender authoring coordinates are `(Unity X, -Unity Z, Unity Y)`; do not apply this conversion again to the FBX in Unity.

```
NetBunt (empty root, mouth-centre origin 0,0,0)
  Bunt (single mesh; floats, rope and bag cords included)
  Fill (empty; default local position 0,-0.09,0.31)

NetPanelSet (empty root, waterline-centre origin 0,0,0)
  NetPanel (mesh, local position 0,0,0)
  NetHeap  (mesh, local position 0,0,0)
```

**Bunt:** mouth normal is local **-Z**, toward the boat; bag extends **+Z**. Orient the root +Z away from the boat. `Bunt` contains `Basis`, `Slack` and `Taut`. Rest/Basis is Slack and the explicit Slack key duplicates it. Keep `Slack` at 0; drive Unity blendshape `Taut` from **0 to 100**. Mouth and floats inside the first 45mm depth band stay fixed. The rear body narrows 28% horizontally and 22% vertically, while depth behind that band lengthens 38%. The fixed mouth means total asset width narrows less than the rear body.

**Fill:** parent runtime fish here. An empty does not follow blendshapes automatically. For normalized tension `t` in `[0,1]`, move Fill from `(0,-0.09,0.31)` to `(0,-0.0702,0.4107)` using linear interpolation, alongside the blendshape. Pack or scale fish for the narrowing bag; the six-fish fixture uses the following Fill-local positions in Slack:

```
(-0.30,-0.090,-0.130), (0,-0.080,-0.130), (0.30,-0.075,-0.100)
(-0.30, 0.065, 0.025), (0, 0.075, 0.035), (0.30, 0.065, 0.020)
```

Fixture fish are canonical Mackerel, rotated across X (90° Z with alternating ±8°), scaled uniformly 0.82 (~0.28m long). At Taut the fixture multiplies these local X/Y offsets by 0.72/0.78 and fish scale by 0.8 (~0.22m long). This packing is evidence setup, not embedded fish in the exported net. Interpolate packing with tension if using this fixture as the runtime starting point; different catches need their own sizing.

**Panel/heap:** separate direct mesh children with common zero pivots. Both are visible in the clean source/export for inspection and occupy the same origin. On instantiation explicitly enable **one**: `NetPanel` for the flying cast, `NetHeap` for a miss. Animate the root or selected child. Panel span runs along X, cork/float line is the long **+Z** edge and steel lead/weight line is **-Z**. The shallow sag and heap folds are baked geometry; no cloth simulation is included.

## Shared material slots

Map slots by name into the existing game material system. All are opaque matte colors; no transparency shader is required.

| Slot | sRGB | Use |
|---|---|---|
| M_NetGreenGrey | #50766C | net cords |
| M_Rope | #D1AF76 | cork-line rope / bindings |
| M_SafetyOrange | #E36A35 | barrel floats |
| M_RailIvory | #F3F0DC | float centre bands |
| M_Steel | #8FA6AC | panel lead weights |
| M_Rubber | #28343B | panel lead line |

Orange barrels with ivory bands and warm rope follow the existing GillNet/CompactFisher kit. Coarse angular mesh and restrained material colors follow `Art/STYLE.md`. Renderer materials and stage are held only in the fixture; clean asset files contain no camera, lights, water, boat or fish.

## Evidence — each final image opened

Twenty 1000×800 studio images, five views for each subject/state. Front looks toward the mouth from Unity -Z; top looks down from Unity +Y. Panel front is deliberately near edge-on and confirms its thin profile.

| Subject | Three-quarter | Front | Right | Back | Top |
|---|---|---|---|---|---|
| Bunt Slack | [view](renders/NetBunt-Slack/three-quarter.png) | [view](renders/NetBunt-Slack/front.png) | [view](renders/NetBunt-Slack/right.png) | [view](renders/NetBunt-Slack/back.png) | [view](renders/NetBunt-Slack/top.png) |
| Bunt Taut | [view](renders/NetBunt-Taut/three-quarter.png) | [view](renders/NetBunt-Taut/front.png) | [view](renders/NetBunt-Taut/right.png) | [view](renders/NetBunt-Taut/back.png) | [view](renders/NetBunt-Taut/top.png) |
| Flying panel | [view](renders/NetPanel/three-quarter.png) | [view](renders/NetPanel/front.png) | [view](renders/NetPanel/right.png) | [view](renders/NetPanel/back.png) | [view](renders/NetPanel/top.png) |
| Missed-cast heap | [view](renders/NetHeap/three-quarter.png) | [view](renders/NetHeap/front.png) | [view](renders/NetHeap/right.png) | [view](renders/NetHeap/back.png) | [view](renders/NetHeap/top.png) |

Exact-camera six-fish fixture: **2m above water, 34° down, 54° vertical FOV, mouth 2.5m outward**. Mouth world position `(0.65,0.35,2.5)`; water Y=0. Sensor fit stays VERTICAL at both aspect ratios. The existing CompactFisher roller is appended read-only onto a simple rail/deck stage. Water and lighting are artist staging; runtime HUD, water effects and haul line are outside this asset review.

| State | 1440×900 | 844×390 |
|---|---|---|
| Slack, six fish | [view](renders/assembly/net-view-slack-1440.png) | [view](renders/assembly/net-view-slack-844.png) |
| Taut, six fish | [view](renders/assembly/net-view-taut-1440.png) | [view](renders/assembly/net-view-taut-844.png) |

[Editable camera fixture](NetKit-camera-fixture.blend), [fixture contract/dependency hashes](assembly.json), [visual review receipt](visual-review.json).

Review corrections incorporated: fixed a clipped oblique float, replaced the first open-ring heap with nine crossing folds, moved the real roller into the fixture's lens and repacked fish to stay inside the narrower Taut body. All final frames were reopened after the affected replacements. Cords/float silhouette and six fish remain visible at phone resolution; their smaller silhouettes are a direct consequence of the specified lens and camera distance.

## Verification and reproduction

- Fresh FBX imports preserve all world vertices and every ordered polygon cycle/multiplicity, hierarchy, triangle counts, unit scales, empty world pivots and material colors. Max position discrepancy: Slack bunt 0.067µm, Taut 0.075µm, panel/heap 0.040µm, below 20µm audit tolerance.
- Both exported blendshape channels survive; Taut geometry parity and halfway deformation pass. Slack equals Basis; the mouth band stays fixed and vertices are finite.
- Raw FBX axis/unit/model transforms and mesh extents checked separately against source Unity coordinates; Fill raw translation matches the stated contract.
- Fresh fixture reopen independently measures height2m, pitch33.999991°, verticalFOV53.999999°, outward2.5m; six fish roots/12 meshes in each state and all fish vertices inside frame at both sizes. Nominal interpolated bag-envelope maximum radial fractions: Slack0.9211/Taut0.9521. This is a geometric packing check, not collision or physics acceptance.
- Source/export SHA256 and protected fixture dependency hashes pass. Temporary rejected-iteration backups removed after verification. No Unity/Assets/runtime/save/git changes or native acceptance claimed.

Detailed results: [bunt audit](metrics/NetBunt.json), [panel/heap audit](metrics/NetPanelSet.json), [raw FBX axes](metrics/fbx-axes.json), [fixture measurement](metrics/fixture-audit.json), [delivery inventory](delivery-receipt.json).

Reproducible source: [builder](../../Source/NetKit/build.py), [independent FBX audit](../../Source/NetKit/audit.py), [raw-axis audit](../../Source/NetKit/axes.py), [studio renderer](../../Source/NetKit/render.py), [fixture builder](../../Source/NetKit/assembly.py), [fixture audit](../../Source/NetKit/fixture_audit.py), [WSL runner](../../Source/NetKit/run.py). Scripts read existing house geometry/audit helpers; they write only the two owned NetKit directories.

From the project root in WSL with the installed Windows Blender 5.2:

```sh
python3 Art/Source/NetKit/run.py build,audit,render NetBunt NetPanelSet
python3 Art/Source/NetKit/run.py assembly,axes,fixture_audit NetKit
```

Rebuilding changes evidence bytes; repeat individual-image review and regenerate review/delivery receipts before publishing a revised handoff. Claude's next action: import the two FBXs, map material slots, enable blendshapes, choose panel/heap visibility and wire Bunt/Fill into the current net view, then check actual desktop/phone runtime presentation.

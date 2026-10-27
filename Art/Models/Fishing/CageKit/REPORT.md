# Cage minigame kit — CAGE-ART-1

Codex 2 (WSL CLI), 25 October 2026. Artist delivery complete: four clean metre-scale Blender/FBX pairs, twenty-one studio views, two matched 390-pixel crab comparisons and two assembled camera views. Every final image was individually opened. Unity import, gameplay wiring and native visual acceptance remain with Codex 1 / Claude.

| Model | Triangles | Form and controls | Evidence |
|---|---:|---|---|
| [CrabCage](CrabCage.blend) / [FBX](CrabCage.fbx) | 1,352 | 0.60 × 0.45 m arched creel; approximately 0.35 m body, 0.38 m including bridle ring. Coarse lattice, inward open entrance funnel, bait box, hinged `Lid`, rope-tie `Bridle`. | [Six angles including open lid](renders/CrabCage.json), [metrics/audit](metrics/CrabCage.json) |
| [PotHauler](PotHauler.blend) / [FBX](PotHauler.fbx) | 772 | 0.30 m grooved sheave; satin steel, navy mount, teal drive box. Two lined U-clamps leave a real 50 mm rail channel. `Sheave` spins about its local X. | [Five angles](renders/PotHauler.json), [metrics/audit](metrics/PotHauler.json) |
| [SortingBoard](SortingBoard.blend) / [FBX](SortingBoard.fbx) | 608 | 0.62 × 0.30 m wet timber, raised rear lip, brass rule, physical ivory zero stop and red sliding `LegalMark`. | [Five angles](renders/SortingBoard.json), [metrics/audit](metrics/SortingBoard.json) |
| [CrabBerried](CrabBerried.blend) / [FBX](CrabBerried.fbx) | 888 | Original 672-triangle `CrabBody` unchanged; 216-triangle bright orange clutch under rear flap. Same exact total bounds, scale and base pivot. | [Five angles](renders/CrabBerried.json), [metrics/audit](metrics/CrabBerried.json), [berried 390](renders/recognition/berried-390.png), [plain 390](renders/recognition/plain-390.png) |

All four are strictly below 1,500 triangles. Shared named house-palette materials are embedded, with no textures or loose material folders. Egg orange `#FF9B24` and the red legal marker `#CF4232` supplement the existing palette for the requested distinguishing features. Satin metal and slightly lower-roughness timber keep broad colour blocks and restrained highlights.

## Integration contract

Each delivery has its named root at the base centre, positive unit scale and metre-valued controls. Authoring is Blender Z-up; FBX uses Y-up / -Z forward, with coordinate mapping **Blender (X,Y,Z) → Unity (X,Z,-Y)**. Positions below are Unity local metres. Keep the imported hierarchy and child origins; source bounds in metrics use Blender axes.

| Child | Unity local origin | Use |
|---|---|---|
| `CrabCage/Lid` | (0, 0.28385, -0.130) | Hinge on local X. Closed 0°, open upwards to -90°. Preserve its rest rotation and apply the local-X delta. |
| `CrabCage/Bridle` | (0, 0.355, -0.219) | Attach the haul rope to this world position. Ring and bridle legs are this child. |
| `PotHauler/Sheave` | (0, 0.247, 0) | Animate the child about local X, rather than spinning the whole mount. Sheave diameter is exactly 0.300 m. |
| `SortingBoard/LegalMark` | (-0.145, 0.052, -0.121) | Set local X to **-0.26 + legal length in metres**, retaining Y/Z. Initial length is 0.115 m; this is an illustrative rest position, not a rule change. |

The board's working/gauge edge is Unity **-Z**, back lip +Z. Rule zero is X=-0.26 m; endpoint X=+0.26 m, small ticks every 0.02 m and long ticks every 0.10 m. Main plank top is Y=0.041 m above the root; place the crab's base at that height. Crab claws face Unity +Z, with the rear orange clutch toward an operator on -Z. Exact overhead views naturally hide the underside clutch; the 390-pixel recognition pair uses a rear oblique view suited to the board.

The hauler rail channel is centred at local Y=0.065 m, clear width 0.05672 m and height 0.064 m. A 0.05 m rail runs along local X. Set mount root Y to rail-centre Y minus 0.065 m. The fixture keeps its clamp, wheel and axle geometry intact.

Read-only inspection of `VoyageCageView.cs` found existing stand-ins, whole-hauler local-Z spin, fixed rope offset and a separate primitive gauge. Those are **not changed here**: wiring should replace the stand-ins, use the delivered named children and dimensions, and review framing again. Codex 1 also recorded an existing populated-board crop in native captures; this Blender fixture does not certify that native camera defect resolved.

## Assembled camera evidence

Open [desktop 1440 × 900](renders/assembly/cage-view-1440.png) and [landscape phone 844 × 390](renders/assembly/cage-view-844.png). [Editable assembly](CageKit-assembly.blend) and [exact placements/camera](assembly.json) include a simple rail, deck, haul rope and transparent teal review water. These stage objects are excluded from all four clean exports.

The camera is 1 m above the rail, pitched down 30°, with the runtime's 52° vertical field of view. This is an **artist fixture layout**, not the runtime's current anchor offsets or camera height above the sea. Cage body base is source Z=-0.445 m; water Z=-0.270 m, so 0.175 m of the 0.35 m body is submerged. Lateral separation exposes the cage beside the hauler. The board overlaps the rail by 40 mm; the berried crab rests on its planks with the gauge visible. Phone review confirms distinct cage/hauler/board shapes, the red notch and orange clutch. Native water, HUD, input, animation playback and shipping scene placement were not tested.

## Verification and reproduction

Fresh FBX reimports passed exact world-space mesh comparison: vertex/face/triangle counts, every ordered polygon cycle and multiplicity, hierarchy and material-name parity. All imported object scales are one; child pivot and local-X controls were exercised after reimport. Maximum vertex error across the kit is below 0.05 micrometres. `Lid` opens upwards, `Sheave` turns on X, and `LegalMark` slides solely on X. Canonical crab vertex/face hash and original source-file SHA remain unchanged.

[delivery-receipt.json](delivery-receipt.json) binds all four asset pairs, 25 reviewed final PNGs, editable assembly, source scripts and this report by SHA-256. Individual metrics include the actual FBX geometry/control audit and studio image hashes. First cage (no entrance funnel), first hauler (solid clamp) and first assembled spacing were rejected and overwritten; they are not final evidence.

Reproduce using Windows Blender 5.2.1 from the project root:

```text
blender.exe -b -t 6 -P Art/Source/CageKit/build.py -- <model>
blender.exe -b -t 6 -P Art/Source/CageKit/audit.py -- <model>
blender.exe -b -t 6 -P Art/Source/CageKit/render.py -- <model>
blender.exe -b -t 6 -P Art/Source/CageKit/assembly.py -- --recognition
blender.exe -b -t 6 -P Art/Source/CageKit/assembly.py
```

The builder reads the existing Crab Coast geometry helper; the audit reads the existing HarbourV2 geometry comparator. These dependencies are used read-only. Renderer uses Cycles OPTIX, 24 samples, denoising, warm upper-left key and cool fill. Inspect every generated image before running `receipts.py <model>` and `finalize.py`. Logs are in `Art/Source/CageKit/`.

No Assets, Unity scenes, saves, runtime code or original prop sources changed. No git commands or commit. No subagents. Native import and acceptance remain pending.

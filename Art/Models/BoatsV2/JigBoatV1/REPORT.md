# JigBoatV1 — JIG-BOAT-1

## A. Concept selection — complete

Three painted options, each side and three-quarter, are in `Art/Source/BoatsV2/JigBoat/concepts.png` (1536×1024). Generated with the built-in imagegen tool; exact prompt in source. Opened and inspected all six views.

Selected **A**: compact enclosed forward wheelhouse, two short rail-side masts carrying one sagging lamp cable, three small jig reels, open aft deck and rail-side sorting tray. It shares the navy/ivory/honey family with Compact and Prep while the lamp string immediately distinguishes its night-squid role. B's central arch obstructs the working area; C's rigid spar feels more industrial. The 3D translation simplifies small fittings, moves the lamp string to the starboard rail, keeps the central deck clear, and preserves A's swept sheer and three clinker laps.

Nominal hull 7.0×3.3 m as requested: it is slightly longer than the 6.8 m Prep but narrower and lower in machinery/cabin mass. The equal-scale lineup will disclose this rather than artificially shrink it. No crew, sockets or gameplay wiring supplied: lead integration scope.

## B. Model — technical checks complete

New editable JigBoatV1.blend and JigBoatV1.fbx; **5635 triangles / 13,000 cap**, 43 meshes, 44 total nodes. Eight separately named lamps, three separate jig reels, one lengthwise sagging cable, two short masts, one sorting tray. No net gear or large processing machinery. Small enclosed ivory wheelhouse forward, swept sheer, three shallow clinker laps, orange boot-top, broad timber planks and restrained working fittings.

Authoring coordinates: X right, -Y bow, Z up; flat deck at Z=0. Nominal shell 7.0×3.3 m; full fittings-inclusive bounds [-1.7300000190734863, -3.566801071166992, -0.7250005602836609] to [1.7300000190734863, 3.6600000858306885, 1.950000286102295] metres. Root Catchline_JigBoatV1 at identity. Socket/deck/grid integration is intentionally left to Claude. All current meshes are children of that root.

FBX_SCALE_UNITS export, **raw UnitScaleFactor100**, matching the corrected existing boats; no extra100× root scale. Independent FBX reimport checks every mesh bounds, finite geometry, nonzero face area, parents and original source matrices. Blend/FBX max nearest vertex deviation **5.96046448e-07 m**. No oversized mesh, presentation floor, camera, light or shadow catcher is exported. The exported FBX is reimported independently to make all renders; the presentation stage exists only after export.

Clear central aft walking volume X[-0.80,0.65], Y[-0.95,2.65], Z[0.035,1.7]m checked with polygon/box clipping for EVERY exported face: no intersections. This is geometric authoring clearance, not native crew pathfinding acceptance. Flush hatch/handle stay below0.035m. Wheelhouse side paths remain open. Original B delivery used M_BandIvory on bulbs; the Lights revision below isolates those surfaces as M_JigBulb. Native night-light shader setup remains integration scope.

### Every exported mesh — world bounds (metres)

| Mesh | World minimum XYZ | World maximum XYZ | Triangles |
| --- | --- | --- | ---: |
| CabinAftDoor | (-0.32500, -1.21400, 0.02000) | (0.32500, -1.19000, 1.10000) | 28 |
| CabinBeaconAerial | (-0.41200, -2.30500, 1.43000) | (0.50500, -1.73800, 1.95000) | 116 |
| CabinDoorGlass | (-0.21500, -1.23400, 0.72000) | (0.21500, -1.20600, 1.08000) | 44 |
| CabinLifeRing | (-0.76503, -2.21700, 0.16300) | (-0.67497, -1.68300, 0.69700) | 288 |
| DeckCleats | (-1.54000, -2.73500, 0.38516) | (1.59000, 2.88500, 0.62342) | 240 |
| DoorLatch | (0.20000, -1.19600, 0.48000) | (0.26000, -1.15600, 0.58000) | 44 |
| EngineLegPropeller | (-0.19500, 3.35000, -0.67156) | (0.19500, 3.64750, 0.10156) | 68 |
| FlushHoldHatch | (-0.34000, 0.07500, -0.00000) | (0.34000, 1.02500, 0.01600) | 44 |
| FrontWindow-0.335 | (-0.60000, -2.71350, 0.74000) | (-0.07000, -2.68850, 1.22000) | 28 |
| FrontWindow0.335 | (0.07000, -2.71350, 0.74000) | (0.60000, -2.68850, 1.22000) | 28 |
| HatchHandle | (-0.09000, 0.52250, 0.02400) | (0.09000, 0.57750, 0.03000) | 44 |
| HoldHatchLid | (-0.31500, 0.10000, 0.01200) | (0.31500, 1.00000, 0.02400) | 44 |
| Hull | (-1.66800, -3.50000, -0.62000) | (1.66800, 3.50000, 0.56500) | 465 |
| InnerBulwark | (-1.65000, -3.50000, -0.02500) | (1.65000, 3.50000, 0.56500) | 76 |
| JigReel_01 | (-1.68098, -0.30000, -0.35000) | (-1.24000, 0.05500, 0.81866) | 272 |
| JigReel_02 | (-1.68098, 0.90000, -0.35000) | (-1.24000, 1.25500, 0.81866) | 272 |
| JigReel_03 | (-1.68098, 2.07000, -0.35000) | (-1.24000, 2.42500, 0.81866) | 272 |
| KeelAndRakedStem | (-0.05000, -3.56680, -0.72500) | (0.05000, 3.22000, 0.60760) | 24 |
| LampCable | (1.33800, -1.02281, 1.61961) | (1.36200, 2.94281, 1.93001) | 480 |
| MotorOrangeCap | (-0.22500, 3.26000, 0.36250) | (0.22500, 3.66000, 0.41750) | 44 |
| OutboardMotor | (-0.22000, 3.27000, -0.13000) | (0.22000, 3.65000, 0.37000) | 44 |
| PlankDeck | (-1.56420, -3.44050, -0.04500) | (1.56420, 3.44050, 0.00000) | 178 |
| RoofTimberLip | (-0.73500, -2.78500, 1.28450) | (0.73500, -1.11500, 1.31950) | 44 |
| SafetyFenders | (-1.73000, -1.41657, -0.24000) | (1.73000, 2.56657, 0.39837) | 336 |
| SideWindow-0.661-1.65 | (-0.67350, -1.92500, 0.74000) | (-0.64850, -1.37500, 1.22000) | 28 |
| SideWindow-0.661-2.35 | (-0.67350, -2.62500, 0.74000) | (-0.64850, -2.07500, 1.22000) | 28 |
| SideWindow0.661-1.65 | (0.64850, -1.92500, 0.74000) | (0.67350, -1.37500, 1.22000) | 28 |
| SideWindow0.661-2.35 | (0.64850, -2.62500, 0.74000) | (0.67350, -2.07500, 1.22000) | 28 |
| SortingTray | (0.66750, 1.72750, -0.00000) | (1.41250, 2.53250, 0.85500) | 440 |
| SquidLamp_01 | (1.28500, -0.83750, 1.50203) | (1.41500, -0.70750, 1.86203) | 114 |
| SquidLamp_02 | (1.28500, -0.34250, 1.39328) | (1.41500, -0.21250, 1.75328) | 114 |
| SquidLamp_03 | (1.28500, 0.15250, 1.32078) | (1.41500, 0.28250, 1.68078) | 114 |
| SquidLamp_04 | (1.28500, 0.64750, 1.28453) | (1.41500, 0.77750, 1.64453) | 114 |
| SquidLamp_05 | (1.28500, 1.14250, 1.28453) | (1.41500, 1.27250, 1.64453) | 114 |
| SquidLamp_06 | (1.28500, 1.63750, 1.32078) | (1.41500, 1.76750, 1.68078) | 114 |
| SquidLamp_07 | (1.28500, 2.13250, 1.39328) | (1.41500, 2.26250, 1.75328) | 114 |
| SquidLamp_08 | (1.28500, 2.62750, 1.50203) | (1.41500, 2.75750, 1.86203) | 114 |
| SternLocker | (-1.05000, 2.75500, -0.00000) | (-0.25000, 3.18500, 0.42000) | 44 |
| SternLockerLid | (-1.07500, 2.73500, 0.41000) | (-0.22500, 3.20500, 0.47000) | 44 |
| SweptCapAndRubber | (-1.70000, -3.50000, 0.27512) | (1.70000, 3.50000, 0.62200) | 304 |
| TwoShortLampMasts | (1.24000, -1.13500, -0.00000) | (1.46000, 3.05500, 1.94500) | 168 |
| WheelhouseBody | (-0.65000, -2.69000, 0.00000) | (0.65000, -1.21000, 1.32000) | 44 |
| WheelhouseRoof | (-0.76000, -2.81000, 1.31000) | (0.76000, -1.09000, 1.43000) | 44 |

### Visual evidence

`renders/` contains side, top, front-three-quarter, back-three-quarter, deck-55, low-waterline and game-exact-45, all1000×750, plus same-scale Compact/Jig/Prep lineup top and three-quarter1600×1000; labelled copies and review-sheet.png. Matched house lighting, matte materials, orthographic projection. No original neighbouring boat files are modified. Full visual opening/review status is recorded in comms.md and visual-review.txt after inspection.

### Reproduce

Windows Blender5.2: --background --python Art/Source/BoatsV2/JigBoat/build_jig.py; then review_jig.py. Python/Pillow: finish_jig.py. All steps affect only new Jig-owned paths. LinuxBlender5.0 FBX operator was incompatible with the established export flags; initial failure is retained in build.log, successful Windows run in build-windows.log.

## C. Refit card — complete

Delivered `Art/Source/BoatsV2/ui/v2-item-hull-jig.png`, **480×360 RGBA**, alpha0–255, visible bounds(35,24)–(445,336). SHA256 `22df5b8284b364e89079932fc017706e4c40f2d0900e806362b7898ab10b4136`.

Recovered the already generated master and export from the interrupted session; no regeneration or geometry changes in the C resume. Built-in imagegen provenance and exact full prompt are preserved in `Art/Source/BoatsV2/JigBoat/prompt-card.txt`; original1448×1086RGBA output in `card-master.png`. `export_card.py` crops the alpha>8 master bounds, scales within432×312 and centres the asset with Lanczos resampling, preserving alpha. Independent reconstruction matched every output pixel; dimensions, transparent corners, margins and saved SHA checked.

Opened final card individually and `Art/Source/BoatsV2/JigBoat/card-review.png` (1440×410) beside accepted Skiff and Prep cards. Checked subject against delivered `renders/game-exact-45.png`: eight bulbs on one connected wire, two short masts, three rail reels, compact enclosed wheelhouse, sorting tray and open deck all read. Navy/ivory/honey palette, shaded volume and restrained local dark illustration edges match the refit-card family. No clipping, background, stray shadow, text or extra gear visible. Card camera is a different quarter from the neighbouring cards, following the model reference so its lamp wire and reels remain separated and visible; not an equal-scale boat comparison.

`card-validation.json` records the checks; `card-receipt.json` hashes the card, master, exact prompt, exporter, independent finishing script, comparison, validation and this report. No in-game UI placement or native acceptance claimed. A/B remain as previously delivered:5635tri/13000cap, no geometry/export changes.


No git, commit, Unity, .cs, .meta or other boat edits. Native import, night lighting, gameplay and pathfinding acceptance are not claimed.

## Lights

JIG-LIGHTS-ART-1: **5635 boat triangles unchanged**, plus **1488 effect triangles** (eight 144-triangle quad-crosses and one 336-triangle water pool). Editable `JigBoatV1.blend` and `JigLampGlow.blend`; both FBXs independently reimported. Every boat vertex, face, mesh name and parent matches the pre-lights FBX exactly (maximum world vertex delta **0 m**). Only the eight bulbs’ former `M_BandIvory` face regions change to `M_JigBulb`; sockets/caps/tips retain their previous materials. No other ivory becomes emissive. Both raw FBX UnitScaleFactor=100, metre-scale geometry, no extra100× root scale or stage mesh.

### Integration contract

- `JigBoatV1.fbx`: unchanged root `Catchline_JigBoatV1`; the eight `SquidLamp_01`…`SquidLamp_08` meshes retain names, geometry and transforms. `M_JigBulb` has the original unlit ivory #F3DEA1. At night/jigging, assign warm emission #FFE7A3; day restores zero emission. Do not enable emission on shared ivory materials.
- `JigLampGlow.fbx`: one identity root `JigLampGlow` at the **same boat origin**, no offset. Parent beside the boat model and copy exactly the same model-to-runtime rotation/scale/position; do not place its origin at waterline. Authoring axes X right, -Y bow, Z up; usual FBX import maps to Unity Y up.
- `LampGlow_01`…`LampGlow_08`: each0.60m across, two perpendicular vertical feathered quad grids, centred exactly on the actual corresponding bulb’s ivory-region bounds centre. Shared `M_LampGlow` #FFE7A3, matching LighthouseGlow. `GlowAlpha` vertex COLOR alpha fades from0.38 at centre to0 around every edge.
- `WaterLightPool`: one flat oval **6.0m along boat Y ×3.5m across X**, centre authoring **(3.20,0.96,-0.395)m**, beside the starboard lamp line. `M_JigWaterLight` #CFEFC0; `GlowAlpha` centre0.22, three feather rings, perimeter0. It sits5mm above the fixture’s Z=-0.400m waterline. Adjust only this node’s height to the actual water surface after hull placement if runtime sea height differs; its local bounds and node pivot are stable.
- Both effect materials require **unlit additive**, RGB=material tint multiplied by vertex COLOR.a, double-sided, ZWrite Off, ordinary depth test, no collider, no cast/receive shadows. **Read vertex alpha**: opaque Standard/Lit rendering will show sheets. No texture needed. FBX carries tint and vertex alpha; Blender shader nodes do not configure Unity shaders. Toggle the FX root with bulb emission for dusk/night/jigging. Pool may remain independent from boat bobbing if the lead follows the live water surface.
- Four renders in `renders/lights/`: day/night1440×900 and844×390, orthographic exact45° elevation/35° azimuth, same13.7m horizontal span, same pose/framing. Night has darker sea, warm bulbs, feathered halos and pale green pool. Illustrative12W Blender point lights per bulb show nearby spill; these lights are review-only and are **not exported** or required as eight runtime lights. No heavy bloom.

### Current exported bounds (metres, authoring coordinates)

| Asset / mesh | World minimum XYZ | World maximum XYZ | Triangles |
| --- | --- | --- | ---: |
| JigBoatV1 / CabinAftDoor | (-0.32500, -1.21400, 0.02000) | (0.32500, -1.19000, 1.10000) | 28 |
| JigBoatV1 / CabinBeaconAerial | (-0.41200, -2.30500, 1.43000) | (0.50500, -1.73800, 1.95000) | 116 |
| JigBoatV1 / CabinDoorGlass | (-0.21500, -1.23400, 0.72000) | (0.21500, -1.20600, 1.08000) | 44 |
| JigBoatV1 / CabinLifeRing | (-0.76503, -2.21700, 0.16300) | (-0.67497, -1.68300, 0.69700) | 288 |
| JigBoatV1 / DeckCleats | (-1.54000, -2.73500, 0.38516) | (1.59000, 2.88500, 0.62342) | 240 |
| JigBoatV1 / DoorLatch | (0.20000, -1.19600, 0.48000) | (0.26000, -1.15600, 0.58000) | 44 |
| JigBoatV1 / EngineLegPropeller | (-0.19500, 3.35000, -0.67156) | (0.19500, 3.64750, 0.10156) | 68 |
| JigBoatV1 / FlushHoldHatch | (-0.34000, 0.07500, -0.00000) | (0.34000, 1.02500, 0.01600) | 44 |
| JigBoatV1 / FrontWindow-0.335 | (-0.60000, -2.71350, 0.74000) | (-0.07000, -2.68850, 1.22000) | 28 |
| JigBoatV1 / FrontWindow0.335 | (0.07000, -2.71350, 0.74000) | (0.60000, -2.68850, 1.22000) | 28 |
| JigBoatV1 / HatchHandle | (-0.09000, 0.52250, 0.02400) | (0.09000, 0.57750, 0.03000) | 44 |
| JigBoatV1 / HoldHatchLid | (-0.31500, 0.10000, 0.01200) | (0.31500, 1.00000, 0.02400) | 44 |
| JigBoatV1 / Hull | (-1.66800, -3.50000, -0.62000) | (1.66800, 3.50000, 0.56500) | 465 |
| JigBoatV1 / InnerBulwark | (-1.65000, -3.50000, -0.02500) | (1.65000, 3.50000, 0.56500) | 76 |
| JigBoatV1 / JigReel_01 | (-1.68098, -0.30000, -0.35000) | (-1.24000, 0.05500, 0.81866) | 272 |
| JigBoatV1 / JigReel_02 | (-1.68098, 0.90000, -0.35000) | (-1.24000, 1.25500, 0.81866) | 272 |
| JigBoatV1 / JigReel_03 | (-1.68098, 2.07000, -0.35000) | (-1.24000, 2.42500, 0.81866) | 272 |
| JigBoatV1 / KeelAndRakedStem | (-0.05000, -3.56680, -0.72500) | (0.05000, 3.22000, 0.60760) | 24 |
| JigBoatV1 / LampCable | (1.33800, -1.02281, 1.61961) | (1.36200, 2.94281, 1.93001) | 480 |
| JigBoatV1 / MotorOrangeCap | (-0.22500, 3.26000, 0.36250) | (0.22500, 3.66000, 0.41750) | 44 |
| JigBoatV1 / OutboardMotor | (-0.22000, 3.27000, -0.13000) | (0.22000, 3.65000, 0.37000) | 44 |
| JigBoatV1 / PlankDeck | (-1.56420, -3.44050, -0.04500) | (1.56420, 3.44050, 0.00000) | 178 |
| JigBoatV1 / RoofTimberLip | (-0.73500, -2.78500, 1.28450) | (0.73500, -1.11500, 1.31950) | 44 |
| JigBoatV1 / SafetyFenders | (-1.73000, -1.41657, -0.24000) | (1.73000, 2.56657, 0.39837) | 336 |
| JigBoatV1 / SideWindow-0.661-1.65 | (-0.67350, -1.92500, 0.74000) | (-0.64850, -1.37500, 1.22000) | 28 |
| JigBoatV1 / SideWindow-0.661-2.35 | (-0.67350, -2.62500, 0.74000) | (-0.64850, -2.07500, 1.22000) | 28 |
| JigBoatV1 / SideWindow0.661-1.65 | (0.64850, -1.92500, 0.74000) | (0.67350, -1.37500, 1.22000) | 28 |
| JigBoatV1 / SideWindow0.661-2.35 | (0.64850, -2.62500, 0.74000) | (0.67350, -2.07500, 1.22000) | 28 |
| JigBoatV1 / SortingTray | (0.66750, 1.72750, -0.00000) | (1.41250, 2.53250, 0.85500) | 440 |
| JigBoatV1 / SquidLamp_01 | (1.28500, -0.83750, 1.50203) | (1.41500, -0.70750, 1.86203) | 114 |
| JigBoatV1 / SquidLamp_02 | (1.28500, -0.34250, 1.39328) | (1.41500, -0.21250, 1.75328) | 114 |
| JigBoatV1 / SquidLamp_03 | (1.28500, 0.15250, 1.32078) | (1.41500, 0.28250, 1.68078) | 114 |
| JigBoatV1 / SquidLamp_04 | (1.28500, 0.64750, 1.28453) | (1.41500, 0.77750, 1.64453) | 114 |
| JigBoatV1 / SquidLamp_05 | (1.28500, 1.14250, 1.28453) | (1.41500, 1.27250, 1.64453) | 114 |
| JigBoatV1 / SquidLamp_06 | (1.28500, 1.63750, 1.32078) | (1.41500, 1.76750, 1.68078) | 114 |
| JigBoatV1 / SquidLamp_07 | (1.28500, 2.13250, 1.39328) | (1.41500, 2.26250, 1.75328) | 114 |
| JigBoatV1 / SquidLamp_08 | (1.28500, 2.62750, 1.50203) | (1.41500, 2.75750, 1.86203) | 114 |
| JigBoatV1 / SternLocker | (-1.05000, 2.75500, -0.00000) | (-0.25000, 3.18500, 0.42000) | 44 |
| JigBoatV1 / SternLockerLid | (-1.07500, 2.73500, 0.41000) | (-0.22500, 3.20500, 0.47000) | 44 |
| JigBoatV1 / SweptCapAndRubber | (-1.70000, -3.50000, 0.27512) | (1.70000, 3.50000, 0.62200) | 304 |
| JigBoatV1 / TwoShortLampMasts | (1.24000, -1.13500, -0.00000) | (1.46000, 3.05500, 1.94500) | 168 |
| JigBoatV1 / WheelhouseBody | (-0.65000, -2.69000, 0.00000) | (0.65000, -1.21000, 1.32000) | 44 |
| JigBoatV1 / WheelhouseRoof | (-0.76000, -2.81000, 1.31000) | (0.76000, -1.09000, 1.43000) | 44 |
| JigLampGlow / LampGlow_01 | (1.05000, -1.07250, 1.31453) | (1.65000, -0.47250, 1.91453) | 144 |
| JigLampGlow / LampGlow_02 | (1.05000, -0.57750, 1.20578) | (1.65000, 0.02250, 1.80578) | 144 |
| JigLampGlow / LampGlow_03 | (1.05000, -0.08250, 1.13328) | (1.65000, 0.51750, 1.73328) | 144 |
| JigLampGlow / LampGlow_04 | (1.05000, 0.41250, 1.09703) | (1.65000, 1.01250, 1.69703) | 144 |
| JigLampGlow / LampGlow_05 | (1.05000, 0.90750, 1.09703) | (1.65000, 1.50750, 1.69703) | 144 |
| JigLampGlow / LampGlow_06 | (1.05000, 1.40250, 1.13328) | (1.65000, 2.00250, 1.73328) | 144 |
| JigLampGlow / LampGlow_07 | (1.05000, 1.89750, 1.20578) | (1.65000, 2.49750, 1.80578) | 144 |
| JigLampGlow / LampGlow_08 | (1.05000, 2.39250, 1.31453) | (1.65000, 2.99250, 1.91453) | 144 |
| JigLampGlow / WaterLightPool | (1.45000, -2.04000, -0.39500) | (4.95000, 3.96000, -0.39500) | 336 |

`lights-audit.json`: actual FBX every-mesh bounds/finite-face/unit checks, original/current boat parity, bulb-only material mapping, exact eight glow alignments, source/FX FBX parity, vertex alpha and flat6×3.5m pool dimensions. `lights-original-mesh.json` is a machine-readable geometry/material audit baseline, not a backup model. The pre-lights temporary model/report backups were deleted after verified completion; the audit baseline remains.

`lights-receipt.json` seals this revision. Previous Jig A-C renders/card receipts remain historical evidence of their accepted handoff; their old report hash predates this appended Lights section. Current validation/bounds receipts now name the new boat FBX hash. No accepted concept/card/other boat content regenerated. Native import, actual water alignment, shader brightness, dusk switching and gameplay acceptance remain lead scope.

### Final visual review

Codex 2 opened all four final renders and the review sheet. Independent design review also opened all five images: PASS, eight warm lamps countable at phone size, feathered halos and green pool readable, equipment and full framing preserved. Independent technical source/audit review: PASS, no blocking finding; that reviewer did not reimport binaries or run Unity. The lead’s actual FBX import audit is recorded separately in `lights-audit.json`. These reviews establish scoped source/export and Blender-preview evidence, not native acceptance. `lights-visual-validation.json` records the reviewed image hashes.

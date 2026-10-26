# Stage 1 V2 — painted harbour restaurant

The accepted V1 geometry has been developed into a textured, dressed night-time room with chunky whitewashed stone, honey timber, blue enamel, brass, warm windows and service props. V1 is preserved. This delivery is source art and a Blender lighting target; Unity import, lightmap bake, runtime HUD and touch acceptance have not been performed.

## Start here

- [Desktop comparison](renders/compare-service-desktop.png) and [phone comparison](renders/compare-service-phone.png).
- [1440 × 900 room](renders/room-1440x900.png), [844 × 390 room](renders/room-844x390.png).
- [Production assembly](Stage1V2.fbx), [room shell only](RoomShell.fbx), [authored scene](Stage1V2.blend), [lighting/character proof](LookProof.blend).
- `items/` contains one metric FBX per reusable item. `LookProof.blend` is review-only: people/lights/camera never enter production FBX.

## A — painted shared surfaces

Exactly two 2048 × 2048 RGB maps: [base colour](textures/Restaurant_BaseColor.png) (sRGB) and [surface data](textures/Restaurant_Surface.png) (linear/non-colour). Surface R = roughness, G = metallic, B = emission mask. Thirty-two painted palette cells have 16 px inset; broad authored grain/knots, plank tone breaks, stone dabs, enamel highlights and tile edges avoid photographic noise. Atlas provenance, palette values, channels and pixel bounds are in [atlas.json](textures/atlas.json); the deterministic brush source is `paint_atlas.py`.

Every mesh has exactly UV0 (face-projected palette mapping) and UV1 (individually packed smart-projected lightmap islands). Unity channel indices are 0 and 1 respectively. UV0 deliberately reuses palette space. LocalAO is exported as the first vertex-colour layer: 12 deterministic cosine rays per vertex, 0.22 m range, 4 mm ray offset, maximum 23% occlusion. Its grayscale RGB darkening stays local to each reusable item; no placed floor shadow is baked into a movable prop. Shell self-occlusion includes its own masonry. No normal map, hidden third texture, transparent glass or water mesh.

## B — shell and setting

An 8 × 5 m interior has a 3 × 5 m cream-tiled kitchen at left and honey-plank dining floor at right. Low staggered stone blocks and rounded caps surround it; front blue shutters frame warm windows. Kitchen backsplash, extractor/short flue, real plate shelf and pot, wall trophy fish, lanterns, alley door and two cats dress the shell. Cut-stone quay/foundation, rope-linked posts and right-door jetty/steps extend beyond the interior footprint intentionally. Waterline is Blender Z = **−0.55 m** (Unity Y after axis conversion). There is no sea/presentation floor.

The assembled pass is rotated front-to-back. Per-item exports stay at origin with their own unrotated footprint; placement rotations/positions live in `build-metrics.json`. The proof includes the table-for-four and booth for art review, without asserting stage-1 gameplay availability. Terrace table/parasol and broken fryer are separate library exports and are excluded from the dressed assembly.

## C–D — complete reusable inventory and dimensions

One Blender unit is one metre. Every independent root is (0,0,0); furniture pivots are at its exact floor plane, small props at the exact base plane (minimum Z is recorded below). X = width, Y = depth, Z = height in Blender; FBX is Y-up, forward −Z, UnitScaleFactor = 100. Dimensions include all attached chairs/handles. `SmokeSocket` is a non-rendering child of FryerBroken at (0.23,0.04,0.81) m. FridgeV2 is steel; reception includes a modeled brass anchor panel. Each root has one atlas mesh/one material.

| Item / FBX | Size X × Y × Z (m) | Footprint tiles | Base minimum Z (m) | Triangles |
|---|---:|---:|---:|---:|
| [PrepCounter](items/PrepCounter.fbx) | 0.955 × 0.894 × 1.010 | 1 × 1 | 0.000 | 1,596 |
| [Stove](items/Stove.fbx) | 0.940 × 0.888 × 0.810 | 1 × 1 | 0.000 | 4,280 |
| [SoupKettle](items/SoupKettle.fbx) | 0.748 × 0.660 × 0.745 | 1 × 1 | 0.000 | 1,304 |
| [FridgeV2](items/FridgeV2.fbx) | 0.780 × 0.901 × 1.160 | 1 × 1 | 0.000 | 556 |
| [SinkDishRack](items/SinkDishRack.fbx) | 1.860 × 0.881 × 1.012 | 2 × 1 | 0.000 | 2,860 |
| [CoffeeBar](items/CoffeeBar.fbx) | 0.955 × 0.894 × 1.334 | 1 × 1 | 0.000 | 3,608 |
| [TableFor2](items/TableFor2.fbx) | 0.970 × 0.560 × 0.915 | 1 × 1 | 0.000 | 2,548 |
| [ReceptionDesk](items/ReceptionDesk.fbx) | 0.940 × 0.940 × 0.909 | 1 × 1 | 0.000 | 2,792 |
| [PassCounter](items/PassCounter.fbx) | 1.900 × 0.620 × 1.113 | 2 × 1 | 0.000 | 1,216 |
| [TrashCan](items/TrashCan.fbx) | 0.520 × 0.560 × 0.620 | 1 × 1 | 0.000 | 788 |
| [Oven](items/Oven.fbx) | 0.840 × 0.848 × 1.220 | 1 × 1 | 0.000 | 1,344 |
| [Fryer](items/Fryer.fbx) | 0.930 × 0.881 × 0.935 | 1 × 1 | 0.000 | 3,420 |
| [FryerBroken](items/FryerBroken.fbx) | 0.930 × 0.881 × 0.935 | 1 × 1 | 0.000 | 3,448 |
| [KettleStand](items/KettleStand.fbx) | 0.955 × 0.894 × 0.663 | 1 × 1 | 0.000 | 1,176 |
| [TableFor4](items/TableFor4.fbx) | 1.120 × 0.980 × 0.785 | 2 × 1 | 0.000 | 3,188 |
| [Booth](items/Booth.fbx) | 1.920 × 0.900 × 0.935 | 2 × 1 | 0.000 | 1,012 |
| [TerraceTable](items/TerraceTable.fbx) | 1.000 × 0.560 × 0.785 | 1 × 1 | 0.000 | 1,740 |
| [Parasol](items/Parasol.fbx) | 0.986 × 0.986 × 1.865 | 1 × 1 | 0.000 | 788 |
| [PlantPot1](items/PlantPot1.fbx) | 0.395 × 0.424 × 0.721 | 1 × 1 | 0.000 | 476 |
| [PlantPot2](items/PlantPot2.fbx) | 0.443 × 0.469 × 0.787 | 1 × 1 | 0.000 | 476 |
| [PlantPot3](items/PlantPot3.fbx) | 0.486 × 0.537 × 0.839 | 1 × 1 | 0.000 | 476 |
| [Barrel](items/Barrel.fbx) | 0.518 × 0.520 × 0.600 | 1 × 1 | 0.000 | 708 |
| [Crate](items/Crate.fbx) | 0.480 × 0.480 × 0.428 | 1 × 1 | 0.000 | 748 |
| [LampPost](items/LampPost.fbx) | 0.540 × 0.320 × 1.750 | 1 × 1 | 0.000 | 1,120 |
| [RopeFencePost](items/RopeFencePost.fbx) | 0.220 × 0.220 × 0.623 | 1 × 1 | 0.000 | 384 |
| [PlateClean](items/PlateClean.fbx) | 0.280 × 0.280 × 0.041 | shell / service prop | 0.000 | 336 |
| [PlateDirty](items/PlateDirty.fbx) | 0.280 × 0.280 × 0.041 | shell / service prop | 0.000 | 464 |
| [GrilledFishPlate](items/GrilledFishPlate.fbx) | 0.280 × 0.280 × 0.064 | shell / service prop | 0.000 | 3,352 |
| [SoupBowl](items/SoupBowl.fbx) | 0.212 × 0.212 × 0.095 | shell / service prop | 0.000 | 440 |
| [CoffeeCup](items/CoffeeCup.fbx) | 0.137 × 0.096 × 0.094 | shell / service prop | 0.000 | 564 |
| [Glass](items/Glass.fbx) | 0.080 × 0.080 × 0.118 | shell / service prop | 0.000 | 252 |
| [TableLantern](items/TableLantern.fbx) | 0.125 × 0.125 × 0.162 | shell / service prop | 0.000 | 696 |
| [Cloche](items/Cloche.fbx) | 0.300 × 0.300 × 0.196 | shell / service prop | 0.000 | 400 |
| [RoomShell](RoomShell.fbx) | 9.665 × 7.945 × 2.690 | shell / service prop | -0.905 | 48,368 |
| [TableLantern_B](items/TableLantern_B.fbx) | 0.125 × 0.125 × 0.162 | 1 × 1 | 0.000 | 696 |
| [PlantPot1_B](items/PlantPot1_B.fbx) | 0.395 × 0.424 × 0.721 | 1 × 1 | 0.000 | 476 |
| [Crate_B](items/Crate_B.fbx) | 0.480 × 0.480 × 0.428 | 1 × 1 | 0.000 | 748 |

`_B` roots are literal repeated-item copies, included conservatively in the library budget. TableFor2 is compact to retain the plan's 1 × 1 footprint; TableFor4 and Booth fit 2 × 1, SinkDishRack and PassCounter fit 2 × 1 in their own axes. Plants have three independently authored pot/foliage sizes. Plates, fish plate, bowl, cup, glass, candle-lantern and cloche are separate movement-ready meshes, rather than textures painted onto furniture. Smoke particles/repair logic are not art geometry.

## E — Blender target and URP reproduction recipe

`review.py` imports the final FBX afresh, then restores only the authored material datablock from Stage1V2.blend. FBX does not serialize this custom node network; do not assume importing FBX alone recreates the shader. Geometry, UVs and vertex colours in proof come from the exported FBX. Use these connections in an opaque URP Lit Shader Graph:

1. Import BaseColor as sRGB; Surface as linear, bilinear filtering, mipmaps, clamp wrap. UV0 samples both maps. Preserve imported mesh vertex colours and authored UV1. Disable automatic lightmap-UV generation to retain the supplied UV1; static shell/furniture can bake into a room lightmap, movable props use probes.
2. Base Color = BaseColor.rgb × Vertex Color.rgb. Ambient Occlusion input = 1 (the same local darkening is already multiplied, avoid a second application). Metallic = Surface.g. Smoothness = 1 − Surface.r. Alpha = 1, opaque, ordinary mesh normals; no transmission or cutout.
3. Emission = BaseColor.linearRGB × Surface.b × 2.8. The glow swatch is sRGB #FFCB64 before the authored brush variation. Use HDR multiplier 2.8 in linear working space. Windows, lantern panes and oven rack lines share that swatch; opacity stays one.
4. Start with a cool dusk environment, warm points listed below, baked indirect for fixed room lights, and probes for crew/props. Blender watts are reference values; the suggested Unity lux/lumen starting values below require native tuning and are not numerical parity claims. The URP Lit Graph exposes Base Color, Smoothness, Metallic, Emission and AO ([Unity Lit reference](https://docs.unity.com/en-us/engine/7000.0/manual/materials-and-shaders/built-in/shaders-in-universalrp/prebuilt-shader-graphs-urp/lit)); baked GI consumes static UV1 ([Unity Graphics Baked GI node](https://github.com/Unity-Technologies/Graphics/blob/master/Packages/com.unity.shadergraph/Documentation~/Baked-GI-Node.md)).

Blender: Cycles OPTIX, 48 samples, denoise; AgX Medium High Contrast, +0.35 EV; no DOF, bloom or outline. Cool world linear RGB (0.29,0.43,0.68), strength 0.18. Camera clear colour is independently dark blue linear (0.008,0.035,0.065). The directional source is at (−3,−4,7) aimed at origin, energy 0.30, angular diameter 9°, linear RGB (0.65,0.76,1). URP starting directional intensity: 0.30 lux with soft shadows; tune against the opened proof, not the raw value.

| Fixture | Blender position X,Y,Z (m) | Blender watts | sRGB light colour | Source radius (m) | Suggested Unity starting lumens |
|---|---:|---:|---|---:|---:|
| REVIEW_Lantern1 | -3.78, 2.27, 1.18 | 90 | #FFC781 | 0.16 | 220 |
| REVIEW_Lantern2 | 0.15, 2.30, 1.18 | 90 | #FFC781 | 0.16 | 220 |
| REVIEW_Lantern3 | 3.70, 2.27, 1.18 | 90 | #FFC781 | 0.16 | 220 |
| REVIEW_Lantern4 | 3.82, -1.10, 1.18 | 90 | #FFC781 | 0.16 | 220 |
| REVIEW_Lantern5 | -3.83, -2.40, 1.18 | 90 | #FFC781 | 0.16 | 220 |
| REVIEW_Lantern6 | 2.15, -2.40, 1.18 | 90 | #FFC781 | 0.16 | 220 |
| REVIEW_Candle1 | 1.32, 0.84, 0.96 | 9 | #FFCE95 | 0.11 | 25 |
| REVIEW_Candle2 | 1.20, -1.40, 0.97 | 9 | #FFCE95 | 0.11 | 25 |
| REVIEW_Window1 | -2.65, -2.95, 0.60 | 18 | #FFCA86 | 0.28 | 50 |
| REVIEW_Window2 | -0.60, -2.95, 0.60 | 18 | #FFCA86 | 0.28 | 50 |
| REVIEW_Window3 | 1.45, -2.95, 0.60 | 18 | #FFCA86 | 0.28 | 50 |

Coordinate conversion for Unity positions: (Blender X, Z, −Y). Use the FBX root transform consistently rather than rotating individual items twice. Add baked kitchen/dining fill corresponding to the two downward disk areas below; URP area illumination is a bake target, not a promise of real-time disk light support. Room indirect light and local shadows matter more than exposure alone. Bake fixed fixtures; keep only necessary moving/local additional lights per renderer for the shipping quality setting.

- REVIEW_KitchenWarmFill: position (-2.5, 0.4, 3.5) m; 190 W, 4 m disk, sRGB #FFE3B6.
- REVIEW_DiningWarmFill: position (1.6, 0.3, 3.8) m; 150 W, 4 m disk, sRGB #FFE8C7.

Suggested URP volume starting grade: ACES tonemapping, post exposure +0.35, contrast +8, saturation +5, temperature +8, tint 0; restrained bloom intensity 0.08 and threshold 1.2 only if lanterns need it. The delivered Blender proof has bloom disabled. These are proposed native settings, not a verified AgX-to-ACES match. Use a baked room lightmap and probes; restrained SSAO can supplement contacts after the supplied local AO, avoiding doubled black edges. [lighting.json](lighting.json) gives exact linear values and fixture positions, [character-scale.json](character-scale.json) names original crew/Mira files, hashes and evaluated scale.

## F — evidence, checks and remaining visual differences

Independent fresh FBX audit: **37 individual exports**, **34 assembly meshes**, **98,844 triangles for all library items + shell**, **92,868 in the dressed assembly**, both under 150,000. Two 2048 atlases. Maximum world-bounds error after FBX round trip: 5.36e-07 m.

The export audit checks exact expected mesh names/counts, finite metre bounds, unit factor, per-item footprints/base contact, triangle counts, two UV sets, finite in-range UVs, positive UV1 triangle areas and total UV1 area, and LocalAO values. This guards against the earlier oversized/presentation-mesh issue. UV1 area/range checks are not a Unity lightmap bake or exhaustive island-intersection test. The shell has many small stone/bevel islands; inspect native lightmap texel density and bake resolution before shipping. `validation.json` contains every mesh's world-bounds table, UV results and FBX hashes. `visual-review.json` records images actually opened; `independent-audit.json` checks final file consistency.

Original CrewRig is imported twice with existing deckhand/captain outfits and Idle frame 12; original Mira is imported once, unscaled. Wrapper transforms preserve animation offsets. Their sources remain unchanged. The camera is exactly 52° from horizontal and yaw 0 for both outputs. Different aspect ratios are framed to show the whole quay with no HUD; the phone view necessarily has more lateral negative space.

| Reference feature | Delivered improvement | Still different / limit |
|---|---|---|
| Painted tactile surfaces | Shared authored grain, tonal stone, tiles/grout, enamel and brass, vertex AO | Palette swatches repeat; no unique painted grime/story decals. Low-frequency strokes are intentionally restrained at phone size. |
| Chunky maritime shell | White stone/caps, shuttered glow, kitchen hood/shelf/fish, alley cats, quay/rope/right jetty | Compact metric layout and lower walls differ from the concept's illustrative perspective and proportions. No water or sea reflection is part of this mesh delivery. |
| Full service kit | Oven, working/broken fryer, steel fridge, sink/rack, coffee/reception, tables/booth/terrace, independent service props | Practical 1 m footprints produce smaller furnishings than the painting; gameplay/path availability and service anchors are integration work. |
| Warm night light | Cool sky, warm fixture points, window/oven emission, two warm indirect fills | The concept has painted bounce and bloom; native URP bake/grade needs matching. Blender proof is not native acceptance. |
| Busy service scene | Original two crew and Mira provide truthful scale | Crowd/diners, thought bubbles, UI cards, water and animation are not fabricated into the art proof. UI is another owner's scope. |

Reproduce with `python3 run.py build validate review`, then the project's existing Pillow environment for `pack.py` and `report.py`. Build/review scripts use installed Windows Blender 5.2 through WSL; no project batchmode or player save is touched. No Assets/.meta/.cs/git changes, no subagents. Delivery does not authorize bulk implementation or broader content work.

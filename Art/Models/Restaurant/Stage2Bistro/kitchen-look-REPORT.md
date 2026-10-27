# KITCHEN-LOOK-1 — Stage2Bistro

Codex 2 (WSL CLI), 2026-10-27. Source delivery; native Unity AFTER is pending Claude import and acceptance.

The rear working wall now has a tapered steel extractor canopy with dark baffles and a warm underside strip, a substantial shelf with three handled stockpots, and a brass rail carrying ladles, slotted spatulas and a whisk. Two short-range warm task practicals light the working surfaces. Kitchen floor/masonry UVs use warmer existing ivory/cream atlas cells with mild vertex pigment variation. Floor colour selection is shared across each whole 1 m tile, avoiding diagonal triangle patches. The utensil rail is on the clear wall beside the fridge (X -.98 to -.12 m), above bar height, so the original tall appliances do not conceal it. Stove, Oven and FridgeV2 retain their silhouettes and receive steel-face atlas remaps; their dark oven glass/brass accents remain.

All 177 original exported mesh names and world geometry are retained exactly at the fresh-FBX audit's five-decimal coordinate precision. Only six wall-mounted meshes are added; their lowest point is 0.945 m above floor, at the rear wall. No floor-contact object, station footprint, dining layout or walking grid was added or moved. Grid: 10 x 5 room, 4 x 5 kitchen, +X 3 x 5 terrace, door (9,0). Cameras and atlas files remain byte-identical. No Assets, code or git changes; no commit or subagents.

## Files and native integration

- `Stage2Bistro.blend` and `Stage2Bistro.fbx`: production room, 183 meshes / 96,954 triangles. `KitchenLook_*` becomes `EXPORT_KitchenLook_*` in FBX, following all existing export naming.
- `lighting.json`: existing recipe retained plus KitchenLook_Task0 (28 W Blender) and Task1 (18 W Blender), warm RGB (1,.60,.27), radius .18 m / proposed Unity range 1.6 m. Total 27 importable recipe lights; existing preview-only section unchanged. Blender watts are source recipe values, not tested Unity intensity equivalents.
- `build-metrics.json`, `validation.json`, `kitchen-look-validation.json`, `kitchen-look-baseline.json.gz`, `kitchen-look-changes.json`: exact per-node bounds/triangles, retained original measurements, UV and preservation evidence.
- `kitchen-look-renders/`: same accepted desktop 1440x900 and phone 844x390 BEFORE/AFTER; additional 1200x900 detail diagnostic is explicitly a closer non-game camera.
- `kitchen-look-review.jpg`, `kitchen-look-phone-review.jpg`: painting and native BEFORE comparison plus source BEFORE/AFTER. Native screenshots are evidence of the starting issue, never a native AFTER claim.
- `kitchen-look-Check.blend`: packed source proof scene; open the production blend for the accepted game camera, as checkscene is saved on the final diagnostic close-up.
- `kitchen-look-visual-review.json` records actual individual image opens; `kitchen-look-final-audit.json` seals production, proof and audit files after review.

**Layout-placed station finish:** the game hides the room's source Stove/Oven/FridgeV2 placeholders and instantiates station models. Their revised steel UV finish therefore requires the lead to propagate the source finish to those native station models; importing the room alone cannot change the hidden placeholders' replacements. Existing names/footprints were deliberately retained. New hood/shelf/utensils are static wall dressing. Check their relation to the game's placed stations in native AFTER. No duplicate floor station has been introduced to force the appearance.

## Verification and limits

Independent fresh import compares every original mesh name, sorted world vertices and polygon count against the pre-edit FBX. All original geometry remains identical; all bounds match build metrics within 0.00001 m. Every mesh has one atlas material, finite positions/UVs, two UV layers and strictly positive UV1 triangle area. The original atlas images, final camera JSON and layout JSON where present are byte-identical. FBX UnitScaleFactor=100 with the exact V4 exporter flags: apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y', colors_type='LINEAR'. Unity coordinate recipe stays [x,z,-y]; lead handles Unity X mirroring.

BEFORE and AFTER use the same accepted camera, backdrop and LocalAO proof shader. Missing legacy LocalAO layers are filled white in proof memory only, avoiding false black legacy appliances. Existing authored pigments remain. Source proof uses Cycles/OPTIX 24 samples. Room populations are the original source check furniture, not a native guest/layout simulation. The close-up changes framing only and is separately labelled. Actual native light conversion, station substitution/placement, guest paths, material remaps and 1440/844 visual acceptance remain unverified here.

Temporary replacement backups are removed only after the fresh-FBX checks and actual image review pass; retained compressed original measurements support repeat audit without them. The build script documents the pre-treatment backup dependency; production blend/FBX are the editable/reimportable delivery. Do not rebuild from the already-treated production blend as if it were a pre-treatment source.

# PACK-TERRACE-1 - Codex 1 (Windows app)

Source-only delivery: six exact-name `Restaurant_<stem>.fbx` files, six editable Blender assemblies and three adjacent accepted Catchline atlases. Claude owns Unity import and placement. No Assets, game code or git changes.

## Pieces

Dimensions below are Unity W x D x H metres (generated from the final manifest in the table below). Floor pivots are bottom-centred. The fence swag's origin is the rear contact plane and height centre; mount it about 1.05m above the quay. Geometry is not pretranslated to that height. HarbourBench reserves two tiles along X for its 1.4m span; the other pieces use one tile.

| Stem | W x D x H m | Mount | Pack recipe / additions |
|---|---|---|---|
| StandaloneParasol | 0.995 x 0.995 x 2.012 | floor | Kenney food plate weighted base; authored timber mast, brass runner/ribs and eight-panel cream/teal canopy. No table or chairs. |
| DeckChair | 0.597 x 0.819 x 0.909 | floor | KayKit pillow_A head cushion; authored folding timber X-frame, brass pivots, cream/teal sling and arms. |
| HarbourBench | 1.400 x 0.500 x 0.820 | floor | Kenney bench frame, warm-wood seat/back slats and brass fasteners; 1.4m wide. |
| RailingRopeSwag | 0.986 x 0.131 x 0.291 | fence | KayKit shelf_A_small mounting blocks; authored catenary-like rope with cork floats and navy/cream binding bands. |
| PotLadder | 0.624 x 0.603 x 1.174 | floor | KayKit shelf_A_small three shelf boards and jar_D_large planters; Kenney pottedPlant leaf-only crowns; authored timber A-frame, spreaders and brass fasteners. |
| QuayBollard | 0.483 x 0.506 x 0.460 | floor | Kenney food plate base, authored navy cast mooring post/crosshead with brass collars and coiled rope. |

All pack downloads are read-only. Authored additions are declared rather than represented as untouched pack models: parasol canopy/mast/ribs, chair sling/X-frame/arms, bench finishing slats, rope/float geometry, ladder A-frame, bollard and coils. Base plates reuse Kenney food plate geometry as weighted circular plinths. PotLadder uses original Kenney pointed foliage material faces with the wooden pots removed, seated in three KayKit ceramic jars. The complete Kenney bench frame and KayKit pillow/shelves remain in their assemblies.

## Export / integration

Same exporter as accepted Pack/decor2: `axis_forward='-Z', axis_up='Y', apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', bake_space_transform=True, colors_type='LINEAR', bake_anim=False`, selected mesh only, copied/embedded textures. Blender `[x,y,z]` is baked to FBX `[x,z,-y]`. Y-up, one unit = one metre (FBX UnitScaleFactor100). All FBX roots have zero translation/rotation and unit scale. One joined mesh per asset; no cameras, lights, proof floor, grid or fence supports are exported.

Fronts face Unity -Z. The parasol and bollard are approximately radially symmetric. DeckChair/HarbourBench/PotLadder and fence swag are displayed at yaw180 in proofs to expose that front to the required game-camera angle; exported roots remain identity. Textures are adjacent and byte-identical to accepted Pack root atlases. Palette remains warm wood/navy/teal/cream/brass, with natural green leaves; no diner orange.

## Evidence

- `terrace-contact.jpg`: six pieces at one scale on a 1m grid, game-camera pitch38/yaw2.
- `terrace-contact-844.jpg`: 844px-wide overview of the same grid.
- `terrace-detail-contact.jpg`: six labelled individual fresh-FBX proofs; originals under `renders/`.
- `manifest.json`, `footprints.json`: final dimensions, mount heights, pack source paths/normalisation, notes, triangle counts, FBX SHA256s.
- `fbx-transform-audit.json`: independent binary-FBX root transforms, Y-up and metre metadata.
- `geometry-audit.json`: independent binary-FBX finite vertices, actual metre sizes, bottom/wall-contact pivots and horizontal centres.
- `mesh-audit.json`: fresh Blender imports, one mesh, bounds roundtrip tolerance <.00001m, UV range, decoded atlas images, material image coverage, triangle counts and FBX hashes.
- `preservation-baseline.json`, `preservation-audit.json`: byte-for-byte original source checks, excluding this additive folder, active kitchen and generated caches.
- `audit.json`: exact six names, editable sources, manifest hashes, adjacent atlas byte identity, decoded proof images and all technical audit results. `visual-review.json` seals opened final proof hashes.

Corrections after first visual pass: aligned the CC0 bench front with the added slats; reduced the ladder from four pots to three as briefed and replaced cactus silhouettes with leafy ceramic planters. Reduced leaf height and staggered lower pots forward after catching an upper-shelf intersection in the second ladder proof. Re-exported and repeated audits and affected fresh-FBX proofs.

Standalone Blender5.2/Cycles proofs are source review evidence. Native Unity material binding, orientation, room/terrace placement, collision/navigation, shadows/performance and Mo's visual acceptance remain unverified and Claude-owned. No subagents. No commit.

## Final seal

PASS: six exact-name FBXs and six editable blends; 23,936 triangles total. Raw transforms, independent geometry, fresh-import mesh/UV/image checks, all three adjacent accepted atlases and manifest hashes pass. Ten final proof images decode and their SHA256s match the opened visual-review seal. All six projected grid boxes are inside the 2880x1800 frame. Preservation: 4,450/4,450 pre-existing files unchanged, zero exceptions. Final desktop and 844-wide contacts inspected after the last ladder correction. Temporary own .blend1 backups removed. Source delivery finished; native import/acceptance remains with Claude.

# PACK-DECOR-3 - Codex 1 (Windows app)

Source-only handoff: eight exact-name `Restaurant_<stem>.fbx` files, eight editable Blender assemblies and three adjacent accepted Catchline atlases. Native Unity import, materials, placement and Mo's visual acceptance remain Claude/Mo-owned. No Assets, game code or git changes.

## Pieces

Dimensions are Unity **W x D x H metres**. Each purchase footprint is 1 x 1 m. WelcomeMat's actual geometry is 1.00 x .60 m along X; wall origins are height-centred on the rear contact plane and should be mounted about 1.6 m above the floor. See `footprints.json` and the component paths in `manifest.json`.

| Stem | W x D x H (m) | Mount | Pack recipe and declared additions |
|---|---|---|---|
| ShipWheel | 0.761 x 0.175 x 0.764 | wall | KayKit pictureframe_small_A mounting plaque, with authored eight-spoke timber wheel, brass collar and grips. |
| PortholeMirror | 0.597 x 0.099 x 0.570 | wall | Kenney food plate turned upright and atlas-recoloured as mirror, with authored brass rim, hinge, dogs and bolts. Opaque blue-steel face; runtime reflection is importer-owned. |
| LifeRing | 0.655 x 0.141 x 0.656 | wall | KayKit shelf_A_small fastening blocks, with authored navy/cream ring sectors, rope and lashings. |
| WindowFlowerBox | 0.970 x 0.309 x 0.565 | wall | KayKit crate planter + Kenney pottedPlant leaf-only crowns, with authored cream/rose/amber flowers and wall brackets. |
| WelcomeMat | 1.000 x 0.600 x 0.037 | floor | Kenney rugDoormat + navy border, cream inner stripe and coarse woven ribs; no baked lettering. |
| HangingHerbs | 0.865 x 0.217 x 0.457 | wall | KayKit shelf_A_small brackets + Kenney pottedPlant leaf-only hanging bunches and KayKit onion bulbs, with authored ties, garlic braid and dried chilli silhouettes. |
| BarBottleShelf | 0.980 x 0.241 x 0.515 | wall | KayKit shelf_A_small + Kenney bottle-oil, bottle-ketchup and glass, with shelf brackets and small cream bottle labels. |
| ReedVase | 0.424 x 0.340 x 1.319 | floor | KayKit jar_D_large + Kenney pottedPlant dried leaf-only reeds, with authored splayed reeds and pampas heads; ceramic teal/cream. |

The wheel rim/spokes, porthole brasswork, life ring/rope, flower petals, ties/chillies, mat border/ribs, bottle labels and dried reed heads are simple authored additions to the CC0 kit assemblies. Kenney leaf-only subsets retain original plant-material faces and omit wooden pot faces, then are normalised to the recipe bounds. PottedPlant's pointed foliage is used for herbs/flowers rather than the small pack cacti. Existing pack downloads stay byte-identical. All visible model materials use the adjacent accepted atlases; no new diner-orange palette.

PortholeMirror deliberately has a stylised opaque blue-steel mirror face, not a baked reflected scene or an implemented real-time mirror. Brass uses the atlas's honey-gold swatch with matte pack shading. Bar bottles reuse oil/ketchup geometry as coloured bottle silhouettes; glasses are opaque light steel from the accepted atlas, not a custom glass shader. Garlic reuses ivory-tinted pack onions. Herbs use broad pointed leaf bunches; no botanical or simulation claim.

## Export / integration contract

One unit = one metre, Unity Y-up. Blender `[x,y,z]` is baked to FBX `[x,z,-y]`; wall fronts extend toward FBX -Z. Floor pivots are at bottom-centre of geometry footprint; wall pivots lie on the rear contact plane with height centred about the origin (not pretranslated to 1.6 m). Raw local FBX translation/rotation = zero, scale = one. Importer-owned Unity handedness is the same as accepted Pack/decor.

Exact exporter arguments: `axis_forward='-Z', axis_up='Y', apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', bake_space_transform=True, colors_type='LINEAR', bake_anim=False`, selected mesh only, copied/embedded textures. Global FBX UnitScaleFactor = 100 (metres). One joined mesh per FBX; proof floors, wall swatches, cameras and lights are excluded.

## Evidence and audit files

- `decor2-contact.jpg`: all eight at one scale on the 1 m grid; `decor2-contact-844.jpg`: phone-width grid overview. `decor2-detail-contact.jpg`: labelled fresh-FBX individual proofs. Original individual/grid renders are under `renders/`.
- Game camera: pitch 38 degrees / yaw 2 degrees. Proof-only wall swatches and wall objects are displayed at yaw 180 to expose their -Z fronts from that camera; export roots remain identity. Wall origins are mounted 1.6 m high for the proofs.
- `fbx-transform-audit.json`: independent binary-FBX root identity, Y-up and metre metadata.
- `geometry-audit.json`: independent binary-FBX vertices, finite geometry, metre sizes and floor/wall pivot/contact checks.
- `mesh-audit.json`: fresh Blender imports, one mesh, bounds roundtrip tolerance < .00001 m, UV range, decoded atlas images, material image coverage, triangle counts and current FBX hashes.
- `preservation-baseline.json`, `preservation-audit.json`: pre-existing downloaded packs, palette sources and accepted Pack furniture/dishes/decor files; active Codex 2 lights and generated caches excluded at baseline. New later folders are not part of the baseline.
- `audit.json`: exact eight names, editable sources, manifest hashes, byte-identical adjacent atlases, decoded proof images and all audit results. `visual-review.json` seals the final opened proof hashes and review notes.

Corrections found during visual review: removed visible pots from flower/herb/reed assemblies; replaced cactus-shaped small plant subsets with pointed pottedPlant leaf subsets; removed towel from the herb mounting, added visible chilli ties; raised bar bottles and glasses to the measured shelf top. Audits and affected proofs were repeated after the final changes.

These are standalone Blender 5.2/Cycles source proofs, not native game captures. Runtime material binding, wall hanging positions, reflection treatment, shadows, room fit/performance and Mo acceptance remain unverified here. No subagents, no commit, no historical queue resumed.

Final source seal: **PASS**, eight exact-name FBXs / eight editable blends / 22,828 triangles / twelve decoded proof images / three byte-identical adjacent atlases. All 4,328 baseline files unchanged, zero generated-cache exceptions. Four own temporary .blend1 backups removed after verified final exports. Source delivery complete; reservations released, IDLE.

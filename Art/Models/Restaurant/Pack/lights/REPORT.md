# PACK-DECOR-2 — Codex 2 (WSL CLI)

Six source-only drop-in Unity FBXs, six editable Blender assemblies, three adjacent accepted Catchline pack atlases, manifest/footprints, game-camera proof sheets and independent audits. Existing sources remain read-only. Claude imports and binds emission; Mo accepts the in-game look. No Assets, game code or git changes.

## Pieces

Dimensions are Unity **W × D × H metres**. Every FBX contains exactly two independent mesh nodes at identity: `Restaurant_<stem>` (atlas body) and `<stem>_Glow` (emitting element). The latter has one exclusive material also named `<stem>_Glow`, opaque base colour **#FFE0A0**, with authored emission strength **0**. There are no real lights or baked lightmaps. Claude can bind emission by the `_Glow` material suffix without illuminating the body.

| Stem | W × D × H (m) | Mount / footprint | Pack combination and glow mesh |
|---|---|---|---|
| PendantLamp | 0.438 × 0.438 × 0.900 | ceiling; 1×1 purchase footprint | Kenney lampSquareCeiling compressed into ceiling fitting + navy hanging cord, open cream/brass shade, exposed ivory bulb. Glow: `PendantLamp_Glow`. |
| WallSconce | 0.210 × 0.305 × 0.310 | wall; 1×1 purchase footprint | KayKit shelf_A_small bracket + brass arm/cup and faceted ivory globe. Glow: `WallSconce_Glow`. |
| HangingLantern | 0.270 × 0.365 × 0.582 | wall; 1×1 purchase footprint | KayKit shelf_A_small hook bracket + navy/brass lantern frame with four opaque lit panes. Glow: `HangingLantern_Glow`. |
| StringLightsLong | 2.875 × 0.105 × 0.442 | wall; 3×1 wall span | Two KayKit shelf_A_small end brackets + navy sagging cord, ten brass sockets and ten ivory bulbs. Glow: `StringLightsLong_Glow`. |
| TableLamp | 0.378 × 0.378 × 0.558 | floor/table; 1×1 purchase footprint | Kenney lampRoundTable base (original shade removed) + brass stem, open cream shade and exposed ivory bulb. Glow: `TableLamp_Glow`. |
| Brazier | 0.530 × 0.530 × 0.741 | floor; 1×1 purchase footprint | KayKit pot_A fire bowl recoloured navy + splayed legs, guard, dark coals and nine bright amber embers. Glow: `Brazier_Glow`. |

Detailed pack paths, dimensions, component recipes and FBX SHA-256 values are in `manifest.json`; placement hints are in `footprints.json`. New shade/globe/cord/lantern/ember/metalwork details are explicitly authored geometry supplementing the CC0 pack components. The pack palette is retained through unchanged atlas images; brass uses the accepted warm honey swatch, with navy metal and cream shades. No diner-orange palette additions. Lantern panes are opaque bright panels, not transparent glass. No geometry from the original downloads was overwritten.

## Placement and export

One unit = one metre. Blender `[x,y,z]` maps to FBX `[x,z,-y]`; wall faces extend toward negative FBX Z. Unity handedness is importer-owned. Both mesh nodes have zero translation/rotation and unit scale; the axis conversion is baked into vertices. Floor/table pieces have centred footprints and base at local Y=0. Wall pivots sit on the rear contact plane, height-centred; mount around 1.6m. The ceiling pendant uses its **ceiling-contact plane as local Y=0** and hangs .900m below it; place that origin at the ceiling, nominally 2.5m. TableLamp starts at its table-contact plane; nominal table height .72m. StringLightsLong is 2.875m across (3 tiles), deliberately longer than the earlier single-tile StringLights.

Exact accepted export options: selected meshes only, `axis_forward='-Z', axis_up='Y', apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', bake_space_transform=True, colors_type='LINEAR', bake_anim=False`, `path_mode='COPY', embed_textures=True`. Raw FBX UnitScaleFactor=100 (metres), Y-up. No proof supports, grid, cameras, walls or lights are present in the exports.

## Evidence and checks

- `lights-contact.jpg`: same-scale six-fixture contact on a **1m grid**, game camera **pitch38°/yaw2°**. Wall mounts are shown at display yaw180° to face this camera; export transforms remain identity. The pendant mounts at2.5m and the table lamp sits on a proof table at.72m. Proof supports are excluded from FBX.
- `lights-contact-844.jpg`: 844-wide overview of the same grid.
- `lights-detail-contact.jpg` and `renders/<stem>.png`: six enlarged game-angle fresh-FBX proofs, **base colour lighting only**. These demonstrate visibility and modelling, not Unity emission/bloom.
- `fbx-transform-audit.json`: independent binary-FBX check of all12 model nodes: exact names, identity transforms, metre scale, Y-up, mesh-only and named glow materials.
- `geometry-audit.json`: independent binary-FBX vertex checks: two nonempty geometries, finite metre-sized bounds, centred X, floor/table contact, wall contact/front or ceiling contact.
- `mesh-audit.json`: fresh import of all6FBXs: exact body+glow names, exclusive bright opaque glow material, authored emission0, decoded atlas images, finite UVs, bounds roundtrip, triangle counts, no nonmesh scene objects and manifest hashes.
- `visibility-audit.json`: rays at the game camera against fresh imports confirm visible glow for each fixture, all10strand bulbs and all9ember components. Lantern's front panel is visible; rear/side panels remain available from other angles.
- `preservation-audit.json`: SHA-256 comparison against the 4,131-file pre-existing source baseline (downloads and accepted Pack files; generated bytecode excluded).
- `audit.json`: final manifest/name/atlas/image/preservation and all four technical audits; `visual-review.json` seals the actually opened review images.

Visual correction before delivery: removed the pendant's leftover square shade geometry, compacted its ceiling fitting, and lowered both pendant/table bulbs below the open shade skirts. Re-exported, re-rendered, reopened and re-audited the two corrected lamps. Remaining four fixture exports were unchanged.

Standalone Blender5.2/Cycles proofs are source checks. Native Unity orientation, emission strength/bloom, wall/ceiling placement, performance and Mo acceptance remain Claude/Mo-owned. No native acceptance claimed. Blender6 API deprecation notices and missing optional HIP initialization are logged; rendering completed with the configured Cycles device.

## Reproduction

From Windows standalone Blender: `blender -b --python build.py -- 0:6`, then `blender -b --python review.py -- audit`, `blender -b --python audit_raw.py`, `blender -b --python check_visibility.py`, `blender -b --python review.py -- individual` and `blender -b --python review.py -- grid`. From WSL Python/Pillow run `uv run --with pillow python package.py` then `uv run --with pillow python seal.py`. Paths in these scripts resolve from their own directory. External accepted helpers are imported read-only with bytecode writing disabled.

Final source seal: **PASS** — six FBXs, 8,102 triangles total, ten decoded proof images, three byte-identical accepted atlases, all four technical audits and all 4,131 baseline files unchanged. Final individual proofs and three contact sheets were opened and inspected; visual hashes recorded in visual-review.json. Temporary rebuild backups removed after verification.

No subagents, no commit. Source delivery complete; reservations released. No historical task queue resumed.

# PACK-KITCHEN-1 — Codex 2 (WSL CLI)

Six source-only working-kitchen dressing pieces assembled from the CC0 KayKit Restaurant/Furniture Bits packs, with explicitly authored rail/tool/finish details. Existing packs and accepted deliveries remain read-only. Claude imports and places these; Mo accepts the in-game look. No Assets, game code or git changes.

## Pieces

Dimensions are Unity **W × D × H metres**. Each FBX has one atlas body named `Restaurant_<stem>`; only the hood also contains `ExtractorHood_Glow`.

| Stem | W × D × H (m) | Mount / placement | Recipe |
|---|---|---|---|
| ExtractorHood | 1.000 × 0.512 × 0.647 | wall; origin at 1.95 m | KayKit extractorhood, steel atlas finish, navy filter grille, brass controls; separate ExtractorHood_Glow task-light strip. |
| PotRail | 1.000 × 0.155 × 0.460 | wall; origin at 1.60 m | Two KayKit shelf_A_small brackets, steel rail/hooks, three hanging KayKit pan_A/pan_B and one pot_A; pans turned vertically. |
| UtensilRail | 0.840 × 0.176 × 0.441 | wall; origin at 1.60 m | Two KayKit shelf_A_small brackets and steel rail, authored ladle, slotted turner, whisk and wood spoon. |
| SpiceShelf | 0.900 × 0.220 × 0.369 | wall; origin at 1.60 m | KayKit shelf_A_small plus six varied jar_A_small/jar_B_small/jar_C_small with cream labels and navy/brass/teal lids. |
| KnifeStrip | 0.700 × 0.089 × 0.340 | wall; origin at 1.60 m | KayKit cuttingboard as wall magnet backboard plus four KayKit knife variants, steel blades and navy handles. |
| ChoppingBlock | 0.480 × 0.340 × 0.130 | counter; origin at 0.80 m | KayKit cuttingboard thickened into an end-grain butcher block; wood inlays, scored top and four small rubber feet. |

Every purchase footprint is 1×1 tiles; all pieces fit within 1m width/depth. Manifest `size_unity_m` is `[X,Y,Z]` = `[width,height,depth]`, not the table order. `footprints.json` lists dimensions, mount heights, exact node names and glow information. These are fixed dressing, with no station functionality, footprint changes or animation. The counter block is a small tabletop object: place its origin at the counter surface, nominally .80m.

## Export and placement contract

One unit = one metre. Blender `[x,y,z]` maps to FBX `[x,z,-y]`. All mesh nodes have identity local translation/rotation/scale; the axis conversion is baked into the vertices. Wall fronts extend toward **negative FBX Z**, with the pivot on the rear wall-contact plane and at the height centre. Mount hood origin at 1.95m (base about1.63m), other wall pieces at1.60m. The chopping block has a centred X/Z footprint and bottom contact at local Y=0. Unity handedness/placement remains importer-owned.

Same accepted exporter call as PACK-DECOR-2: selected mesh objects only, `axis_forward="-Z", axis_up="Y", apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", bake_space_transform=True, colors_type="LINEAR", bake_anim=False, path_mode="COPY", embed_textures=True`. Raw UnitScaleFactor=100 (metres), UpAxis=1 (Y). No proof walls, counter, grid, camera or lights are exported.

Three adjacent atlases are byte-identical copies of the accepted Catchline pack images. Steel is furniturebits light-steel swatch6; wood uses existing warm swatches, with navy/brass/teal accents. Pack geometry and atlases were not overwritten. New handles/hooks, ladle/turner/whisk/spoon, labels/lids, filter grille/controls and block inlays are explicitly authored additions. The magnetic knife strip keeps the pack knife blade/handle atlas assignment.

## Hood task light

`ExtractorHood_Glow` is a separate mesh and exclusive material, both named exactly that. It comprises the underside ivory diffuser and a visible front lip; base colour **#FFE0A0**, fully opaque, authored emission strength **0**. Claude binds emission for the existing evening bloom. The atlas hood body does not use this material. The other five exports contain no `_Glow` node or material. No actual scene lights or baked lightmaps are in the FBX.

## Evidence and audits

- `kitchen-contact.jpg`: all six fresh FBX imports at the game camera (pitch38°/yaw2°) on a same-scale 1m grid. Wall pieces are displayed yaw180° to face the camera; exports retain identity transforms. Mount heights and proof supports are labelled.
- `kitchen-contact-844.jpg`: 844-wide overview of that grid. `kitchen-detail-contact.jpg` and `renders/<stem>.png` give enlarged game-angle proofs. Proof supports are excluded from exports; colour lighting only, no Unity bloom claim.
- `fbx-transform-audit.json`: independent binary FBX exact model count/names, identity roots, mesh-only types, Y-up/metres and hood-only glow material.
- `geometry-audit.json`: independent binary vertex bounds, finite coordinates, metre dimensions, centred X, rear wall contact/front direction/height-centre or counter-base contact.
- `mesh-audit.json`: fresh imports of all six exports, exact mesh count/names, atlas-only bodies, decoded image data, finite valid UVs, bounds/pivot roundtrip, triangle counts/hash checks and exclusive bright opaque zero-emission hood material.
- `visibility-audit.json`: rays at the game camera confirm each body is visible and the hood task light is exposed. This is source visibility, not runtime bloom acceptance.
- `preservation-baseline.json` / `preservation-audit.json`: pre-existing immutable downloads and Pack files; active Codex1 decor2 and generated bytecode caches excluded. No claim is made about another owner’s concurrent changes.
- `audit.json` / `visual-review.json`: final source checks and hashes of actually opened proofs.

Visual corrections: hood was rotated to the export wall-front convention and moved so its pack rear meets the contact plane and its fascia meets the task-light strip. Spice jars, labels and lids were raised .08m to sit on the actual shelf top. Individual proof cameras were centred on the full 3D bounds to avoid cropping the deeper hood. Corrected exports were re-imported, re-rendered, reopened and re-audited.

## Reproduction and limits

Windows standalone Blender5.2: run `build.py -- 0:3`, then `build.py -- 3:6`; `review.py -- audit`, `audit_raw.py`, `check_visibility.py`, `review.py -- individual`, `review.py -- grid`. WSL: `uv run --with pillow python package.py`, then `uv run --with pillow python seal.py`. Paths resolve from each script. Accepted helper modules are imported read-only with bytecode writing disabled.

Standalone Blender/Cycles evidence verifies source geometry/export presentation. Native Unity import, orientation, wall/counter placement, emission/bloom, device performance and Mo visual acceptance remain Claude/Mo-owned. Missing optional HIP initialization and Blender API deprecation warnings are logged; completed renders use the configured Cycles device. No subagents, no commit.

## Final source seal

PASS: six exact FBXs and six editable blends; 9,706 triangles total; all four export/import/geometry/visibility audits pass. Ten proof images decode, including the 844px overview; three adjacent atlases match their accepted originals byte for byte. All 4,187 immutable baseline files remain unchanged. Final desktop, detail and phone contacts were opened; hashes are in `visual-review.json`. Temporary own rebuild backups removed after verification. No Assets/game-code/git operations. Ready for Claude import; Codex2 IDLE.

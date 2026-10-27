# PACK-DECOR-1 — Codex 2 (WSL CLI)

Source delivery: twelve exact-name `Restaurant_<stem>.fbx` files, twelve editable `.blend` assemblies and three adjacent Catchline pack atlases. Original packs and accepted furniture/dishes were read-only. No Assets, game code or git changes. Native Unity import and visual acceptance belong to Claude/Mo.

## Pieces

Dimensions below are Unity **W × D × H metres**. All pieces occupy a 1×1m purchase footprint except Rug (2×1m along X). Detailed component source paths and FBX hashes are in `manifest.json`; placement data in `footprints.json`.

| Stem | Size (m) | Mount | Pack combination / additions |
|---|---|---|---|
| PlantPot2 | .515 × .470 × 1.150 | floor | Kenney furniture `pottedPlant` + `plantSmall3`, taller two-crown variety. |
| WallShelf | .860 × .230 × .340 | wall | KayKit furniture `shelf_A_small` + Restaurant `jar_A_small`, `jar_B_medium`, `jar_C_small`. |
| FramedPicture | .700 × .104 × .480 | wall | KayKit `pictureframe_medium` + solid atlas-coloured harbour sailboat/house shapes. |
| MenuBoard | .490 × .329 × .860 | floor | KayKit Restaurant `menu` + navy slate, cream MENU mesh and four chalk rules. |
| WallClock | .400 × .097 × .400 | wall | KayKit `pictureframe_small_A` + cream face, navy ticks/hands and brass pin geometry. |
| Rug | 2.000 × 1.000 × .014 | floor | KayKit `rug_rectangle_stripes_A`, navy border/stripe treatment. |
| Bunting | .924 × .025 × .300 | wall | KayKit `book_single` end fastening + authored cord/five thick pennants in navy/teal/cream. |
| StringLights | .935 × .082 × .284 | wall | Two tiny KayKit `shelf_A_small` brackets + cord/sockets/five ivory bulbs; atlas base colour, no baked glow. |
| WineRack | .620 × .520 × .560 | floor | Kenney `bookcaseOpenLow` turned to face -Z + six `bottle-oil` meshes, two timber cradle shelves. Bottles explicitly reused as wine silhouettes. |
| CoatStand | .460 × .460 × 1.650 | floor | Kenney furniture `coatRackStanding`, warm wood atlas conversion. |
| Bookshelf | .860 × .310 × 1.030 | floor | Kenney `bookcaseOpenLow` + KayKit `book_set` + Kenney `plantSmall1`. |
| Barrel | .510 × .510 × .680 | floor | Kenney food `barrel`, retained as the pack's horizontal keg/spigot silhouette. |

Small clock/graphic/light/cord shapes supplement the CC0 pack meshes. Each result is joined into one mesh; no render floor, wall swatch, camera or lighting geometry is exported. Existing food/KayKit UV colours are retained; flat Kenney furniture colours are mapped to the accepted furniture atlas. No new diner-orange palette.

## Coordinate/export contract

One unit = one metre. Floor pieces: local Y=0 contact, footprint centred X/Z. Wall pieces: origin on the rear contact plane, height-centred; all geometry extends toward negative FBX Z. Mount wall origins around 1.6m above the floor. Wall backs are not pretranslated to their hanging height. Root translation/rotation identity and scale 1; Y-up conversion baked into mesh data. Blender `[x,y,z]` maps to FBX `[x,z,-y]`; Unity handedness conversion remains importer-owned.

Exporter: `axis_forward='-Z', axis_up='Y', apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', bake_space_transform=True, colors_type='LINEAR', bake_anim=False`, selected meshes only, copied and embedded textures. Global FBX UnitScaleFactor=100 (metres); raw model transforms are identity. `WineRack` recipe additionally rotates each oil-bottle mesh -90° about Blender X then translates it into its cradle; this is baked, not a node transform.

## Evidence and checks

- `decor-contact.jpg`: all twelve fresh-import individual proofs, with labels and dimensions. `decor-contact-844.jpg`: phone-width overview of that source sheet.
- `decor-grid-contact.jpg`: all twelve at the same scale on a 1m grid, game camera pitch 38° / yaw 2°. Wall swatches are proof-only, mounted at 1.6m. Wall pieces, MenuBoard and WineRack are displayed at yaw 180° to show their -Z faces from that camera; FBX roots remain identity. Other floor props retain their export orientation.
- `fbx-transform-audit.json`: independent raw FBX model identity, Y-up and metre metadata checks for all twelve.
- `geometry-audit.json`: independent raw FBX vertex bounds, metre dimensions, floor contact/centred footprint or wall rear contact/height centre, finite vertices for all twelve.
- `mesh-audit.json`: fresh Blender import checks, single mesh, bounds roundtrip error <.00001m, UV range, decoded atlas images/material coverage, triangle totals and current FBX hashes.
- `audit.json`, `preservation-audit.json`: exact names, editable sources, atlas byte equality, decoded proof images and pre-existing source preservation. 4,057 of 4,058 scanned files are byte-identical. The sole change is generated `Pack/__pycache__/build.cpython-313.pyc`, refreshed by importing the accepted helper; its source script and every substantive source/asset are unchanged. `preservation-audit.json` retains the strict all-files failure and separately records source preservation PASS; `audit.json` checks substantive source preservation. Future helper imports disable bytecode writes.
- `visual-review.json`: opened final contact/proof hashes and actual review observations.

Visual corrections: individual wall proofs initially intersected the studio floor (height-centred wall pivots); remounted proofs at 1.6m, with exports unchanged. Initial WineRack cabinet read as drawers; replaced it with the open pack bookcase and exposed bottles, re-exported, re-rendered and re-audited.

Proofs use standalone Windows Blender 5.2/Cycles, not Unity captures. System Linux Blender lacked numpy and was abandoned before delivery. No claim of native material binding, wall placement, runtime lighting/glow, performance or Mo acceptance. No remaining source implementation steps after the final audit seal; no subagents; no commit.

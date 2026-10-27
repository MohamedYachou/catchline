# PACK-ITEMS-1 - Catchline restaurant pack assemblies

Source-only handoff for Claude. **26 exact-name FBXs**, each a single UV-mapped mesh with a floor-centre pivot, one unit per metre, baked axis conversion and identity FBX local transforms. No Assets, game code, Unity project, save or Git changes. Native import and player acceptance belong to Claude/Mo.

## Files and use

Use `Restaurant_*.fbx` in this folder. The three adjacent PNGs are the accepted Catchline restaurant/furniture atlases and Kenney food atlas, byte-identical to their accepted source versions. Textures are also embedded in the FBXs. Kenney furniture keeps its accepted named flat-colour materials; it has no atlas. Do not replace those materials with a single restaurant-atlas material.

`manifest.json` gives every component's exact downloaded source, metre dimensions, bottom-centre offset, Z rotation, assembly bounds, triangles and incumbent source/hash. `reference-inventory.json` preserves the original imported reference bounds. `.blend` files retain the editable assembled meshes. There is no room, lighting or floor included in the item FBXs.

Axes: the builder works in Blender Z-up, takes -Y as the front, matching the incumbent Stage1V2 doors/controls, and exports to Y-up FBX with forward -Z. A 180-degree correction is baked into the assembly vertices, never the root transform. The FBX exporter axis flag alone is not a Unity-facing proof. The binary FBX local translation/rotation are zero and scaling is one. Blender restores a +90 degree X coordinate-conversion rotation on import; this is separately checked against raw FBX properties. Unity importer configuration and handedness must be checked by Claude; Blender roundtrip is not Unity acceptance.

## Item dimensions

W/H/D in metres, including chairs and accessories. All pivots remain at the logical floor-footprint centre; asymmetric geometry does not shift the pivot. Table candle uses its tabletop contact as local floor zero, and wall decor uses the bottom of its board as zero, matching the incumbent prop contract.

| Exact file stem | Incumbent W/H/D | Pack W/H/D | Triangles |
|---|---:|---:|---:|
| Restaurant_Stove | 0.940/0.810/0.889 | 0.920/0.800/0.820 | 1084 |
| Restaurant_SoupKettle | 0.748/0.745/0.660 | 0.720/0.740/0.630 | 1292 |
| Restaurant_PrepCounter | 0.955/1.010/0.894 | 0.940/0.990/0.850 | 566 |
| Restaurant_FridgeV2 | 0.780/1.160/0.901 | 0.760/1.150/0.850 | 614 |
| Restaurant_CoffeeBar | 0.955/1.334/0.894 | 0.880/1.260/0.760 | 550 |
| Restaurant_TableFor2 | 0.970/0.915/0.560 | 0.540/0.760/0.960 | 1168 |
| Restaurant_TerraceTable | 1.000/0.785/0.560 | 0.980/1.860/0.980 | 1204 |
| Restaurant_ReceptionDesk | 0.940/0.909/0.940 | 0.920/1.030/0.860 | 276 |
| Restaurant_Oven | 0.840/1.220/0.848 | 0.820/1.200/0.810 | 542 |
| Restaurant_Grill | 0.830/0.870/0.738 | 0.810/0.825/0.700 | 1280 |
| Restaurant_Steamer | 0.685/1.028/0.693 | 0.660/1.020/0.650 | 1528 |
| Restaurant_PassCounter | 1.900/1.113/0.620 | 1.870/1.050/0.675 | 620 |
| Restaurant_PlantPot1 | 0.395/0.721/0.424 | 0.380/0.720/0.400 | 60 |
| Restaurant_LampPost | 0.540/1.750/0.320 | 0.470/1.740/0.320 | 320 |
| Restaurant_Trophy | 0.880/0.380/0.146 | 0.870/0.380/0.185 | 293 |
| Restaurant_Net | 0.891/0.626/0.070 | 0.880/0.620/0.153 | 1108 |
| Restaurant_Chart | 0.880/0.680/0.113 | 0.880/0.680/0.134 | 532 |
| Restaurant_Jukebox | 0.660/1.050/0.458 | 0.640/1.020/0.430 | 754 |
| Restaurant_DrinksFridge | 0.745/1.193/0.736 | 0.730/1.180/0.720 | 426 |
| Restaurant_TableCandle | 0.125/0.162/0.125 | 0.120/0.161/0.120 | 264 |
| Restaurant_BigFridge | 1.485/1.635/0.860 | 1.460/1.620/0.840 | 614 |
| Restaurant_ReliableStove | 1.580/0.880/0.859 | 1.560/1.000/0.820 | 1394 |
| Restaurant_TableFor4 | 1.120/0.785/0.980 | 1.100/0.760/0.960 | 1880 |
| Restaurant_Booth | 1.920/0.935/0.900 | 1.800/0.760/0.945 | 1866 |
| Restaurant_SinkDishRack | 1.860/1.012/0.881 | 1.840/0.830/0.820 | 1954 |
| Restaurant_Fryer | 0.930/0.935/0.881 | 0.900/0.934/0.824 | 746 |

## Deliberate exceptions and substitutes

- TerraceTable includes the requested parasol in the same FBX. Its 1.86 m height exceeds the old table-only 0.785 m height; footprint stays within one tile.
- BigFridge and ReliableStove preserve the incumbent wide upgrade class (roughly 1.5 m wide). They need two floor tiles; squeezing them to one would fail the reference-size requirement. No layout logic is changed here.
- TableFor2 uses front/back chair centres at +/-0.33 m to align with runtime `RestaurantWorld.Seat` (+/-0.38 m); old art has side chairs. TableFor4 uses x +/-0.36 and y +/-0.33; TerraceTable keeps x +/-0.33 side chairs. Booth has three seats on each side within two tiles. The current runtime six-seat formula has a third-pair offset issue; no gameplay correction is included.
- Fryer uses a KayKit counter, shallow pan and wire rack as a fryer basket. This is a pack-geometry proxy, not a downloaded dedicated fryer.
- DrinksFridge uses a closed-door teal pack fridge rather than the incumbent glass bottle-display facade.
- Jukebox is a KayKit cabinet plus Kenney radio, a compact music-cabinet proxy. Neither selected pack has a proper jukebox.
- Trophy uses Kenney fish over a KayKit frame. Net uses a KayKit board/frame plus declared coarse rope and cork geometry. Chart uses a KayKit frame with a simple atlas-coloured coast and waypoints. No text is baked into these props.
- Terrace canopy/pole, fryer handle, grill bars, chart lines, net lattice/floats, candle and flame are declared small assembly details, rather than models falsely attributed to a pack.
- Heights are kept in the incumbent class rather than distorting every mesh to the exact old AABB. Dining surfaces are warm KayKit furniture wood; steel kitchen surfaces retain the steel swatch. Surface-dependent accessories were lowered after the first sink proof exposed a faucet-inflated source AABB.

## Proofs and checks

`after-grid-contact.jpg` and `before-grid-contact.jpg` show fresh FBX imports on a **1 m grid** at the game pitch (38 degrees) and yaw (2 degrees), using an Eevee orthographic inspection camera so pixels/metre are constant. Cycles draft jobs were stopped before producing final sheets; only the completed Eevee outputs are delivery evidence. For Stage1V2 references only, the original Restaurant_Atlas_URP material is loaded from the incumbent Stage1V2.blend, following its own review.py, because FBX omits that procedural graph. Geometry remains the fresh imported reference FBX. These are source renders, not native gameplay captures. `comparison-contact-1..5.jpg` and `comparisons/Restaurant_*.jpg` use an origin-aligned equal-size union crop for each old/new pair, without independent enlargement. Selective rebuilds changed item ordering between the two grids; the pair builder aligns each logical origin and keeps the same orthographic pixels/metre; dimensions are printed below each pair. Individual `renders/<item>.png` are draft build-stage closeups from before the final baked facing correction and have their own framing; use final grid comparisons for delivered facing and scale.

- `mesh-audit.json`: fresh import of all 26 final FBXs; single mesh, finite bounds, exact roundtrip bounds, floor contact, UVs, decoded images, expected Blender axis restore and scale, final FBX hash.
- `fbx-transform-audit.json`: direct binary FBX check of all 26 files; single Model, zero local translation/rotation, unit local scale, Y-up and UnitScaleFactor 100 (metres).
- `seat-direction-audit.json`: PASS all 11 chair backs point away from their table centre; source back geometry measured directly.
- `preservation-audit.json`: 4,184 tracked original pack/accepted palette/reference files unchanged.
- `audit.json`: PASS 26 exact names, 22,935 triangles, 33 decoded final proofs, atlas equality, dimensions/footprints and 4,184 unchanged original files.
- `visual-review.json`: opened final proof hashes and observations. Visual inspection is separate from numerical checks.

Known tooling limit: Blender 5.2 emits `use_nodes` deprecation warnings on stderr. PowerShell may report a nonzero pipeline status because of these warnings even when the log ends in BUILT/GRID_DONE. Audit records and final decoded outputs establish what completed; no failed draft is treated as evidence.

## Reproduction

From repository root, using Blender 5.2 and `uv run --with pillow python` for package scripts:

1. `blender -b --python Art/Models/Restaurant/Pack/inspect_items.py` (reference inventory only; do not regenerate the preservation baseline).
2. `blender -b -t 6 --python Art/Models/Restaurant/Pack/build.py -- 0:26` (baked source assemblies; range or comma-separated indices supported).
3. `blender -b -t 6 --python Art/Models/Restaurant/Pack/review.py -- --eevee before`, then `-- --eevee after` (fresh-FBX proof grids).
4. `uv run --with pillow python Art/Models/Restaurant/Pack/package.py`.
5. `blender -b --python Art/Models/Restaurant/Pack/audit_models.py`, `--python .../check_fbx.py`, and `uv run --with pillow python .../audit_delivery.py`.

Final source and visual review complete. Seven final contact hashes are sealed in `visual-review.json`. Native Unity validation remains pending Claude.

Both KayKit packs and both Kenney packs carry their original CC0 licenses under `Art/Downloads/`; they remain unchanged. The Catchline palette derivatives are from the accepted KAYKIT-PALETTE-1 and KENNEY-FIT-1 deliveries.

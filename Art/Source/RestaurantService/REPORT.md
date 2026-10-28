# SERVICE-PROPS-1

Delivered by Codex 2 (WSL CLI), 2026-10-28. Nineteen additive, chunky low-poly props; no git commands or commit. No C# edits, Unity invocation, existing dish changes, pier changes or Crew changes.

All 38 required frames were opened and visually inspected individually. New asset is left; the existing **Restaurant_Dish_GrilledFish** is right, at its original measured **0.22 m** plate diameter. Service view uses an orthographic camera at **38° pitch**, yaw 12°, from above and slightly behind; close view is 55°. Both use warm service light and cooler harbour fill on honey timber. Sources pack the atlas/reference images. These are Blender asset-review renders, not native game captures.

Each FBX exports one named mesh, one RestaurantAtlas material, one UV map and white vertex colours. Explicit importer external-object remaps target `Assets/Art/Models/Restaurant/RestaurantAtlas.mat` (GUID `93ede68a78343aa4bbc6d4deed7baeec`), shader `Catchline/RestaurantAtlas`, existing Restaurant_BaseColor and _Surface textures. No new texture/material assets. FBX is Y-up with UnitScaleFactor 100 cm = 1 metre per unit; importer scale 1. Pivots are bottom-centred, centred across X/Z; transforms and scale verified by FBX roundtrip. Face shading is flat. Thin surface orientation was checked explicitly for backface culling (open-surfaces.log and gull-winding.log); affected Crab/Calamari garnish evidence was rerendered after correction. Gull primary/tail colour panels meet along edges rather than overlapping; both poses were rerendered and reopened after this correction. Invisible collapsed lathe poles were welded before final export; zero degenerate triangles.

Dishes stay below 1,500 triangles; other props below 3,000. Sizes below are **Unity X × Y × Z in metres (width × height × depth)**. Triangles count the exported, triangulated mesh. Standard new plate diameter is 0.26 m; wash-up plates are 0.22 m to nest inside the measured sink opening.

| Asset | Tris | Size X × Y × Z (m) | Evidence | Blender source |
|---|---:|---|---|---|
| [Restaurant_Dish_FishAndChips](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_FishAndChips.fbx) | 804 | 0.260 × 0.071 × 0.260 | [38°](renders/Restaurant_Dish_FishAndChips-service.png) · [close](renders/Restaurant_Dish_FishAndChips-close.png) | [.blend](blends/Restaurant_Dish_FishAndChips.blend) |
| [Restaurant_Dish_Platter](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_Platter.fbx) | 530 | 0.482 × 0.088 × 0.290 | [38°](renders/Restaurant_Dish_Platter-service.png) · [close](renders/Restaurant_Dish_Platter-close.png) | [.blend](blends/Restaurant_Dish_Platter.blend) |
| [Restaurant_Dish_Crab](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_Crab.fbx) | 804 | 0.260 × 0.084 × 0.260 | [38°](renders/Restaurant_Dish_Crab-service.png) · [close](renders/Restaurant_Dish_Crab-close.png) | [.blend](blends/Restaurant_Dish_Crab.blend) |
| [Restaurant_Dish_Calamari](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_Calamari.fbx) | 852 | 0.260 × 0.070 × 0.260 | [38°](renders/Restaurant_Dish_Calamari-service.png) · [close](renders/Restaurant_Dish_Calamari-close.png) | [.blend](blends/Restaurant_Dish_Calamari.blend) |
| [Restaurant_Dish_Fries](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_Fries.fbx) | 1156 | 0.214 × 0.089 × 0.209 | [38°](renders/Restaurant_Dish_Fries-service.png) · [close](renders/Restaurant_Dish_Fries-close.png) | [.blend](blends/Restaurant_Dish_Fries.blend) |
| [Restaurant_Dish_Bread](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_Bread.fbx) | 1052 | 0.242 × 0.111 × 0.192 | [38°](renders/Restaurant_Dish_Bread-service.png) · [close](renders/Restaurant_Dish_Bread-close.png) | [.blend](blends/Restaurant_Dish_Bread.blend) |
| [Restaurant_Dish_Beer](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_Beer.fbx) | 600 | 0.094 × 0.147 × 0.094 | [38°](renders/Restaurant_Dish_Beer-service.png) · [close](renders/Restaurant_Dish_Beer-close.png) | [.blend](blends/Restaurant_Dish_Beer.blend) |
| [Restaurant_Dish_Tea](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_Tea.fbx) | 736 | 0.290 × 0.130 × 0.190 | [38°](renders/Restaurant_Dish_Tea-service.png) · [close](renders/Restaurant_Dish_Tea-close.png) | [.blend](blends/Restaurant_Dish_Tea.blend) |
| [Restaurant_PlateStackDirty2](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_PlateStackDirty2.fbx) | 532 | 0.272 × 0.041 × 0.260 | [38°](renders/Restaurant_PlateStackDirty2-service.png) · [close](renders/Restaurant_PlateStackDirty2-close.png) | [.blend](blends/Restaurant_PlateStackDirty2.blend) |
| [Restaurant_PlateStackDirty4](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_PlateStackDirty4.fbx) | 916 | 0.272 × 0.077 × 0.270 | [38°](renders/Restaurant_PlateStackDirty4-service.png) · [close](renders/Restaurant_PlateStackDirty4-close.png) | [.blend](blends/Restaurant_PlateStackDirty4.blend) |
| [Restaurant_GlassEmpty](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_GlassEmpty.fbx) | 364 | 0.094 × 0.147 × 0.094 | [38°](renders/Restaurant_GlassEmpty-service.png) · [close](renders/Restaurant_GlassEmpty-close.png) | [.blend](blends/Restaurant_GlassEmpty.blend) |
| [Restaurant_PlateStackClean](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_PlateStackClean.fbx) | 1152 | 0.260 × 0.113 × 0.260 | [38°](renders/Restaurant_PlateStackClean-service.png) · [close](renders/Restaurant_PlateStackClean-close.png) | [.blend](blends/Restaurant_PlateStackClean.blend) |
| [Restaurant_SinkPile0](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_SinkPile0.fbx) | 144 | 0.480 × 0.087 × 0.280 | [38°](renders/Restaurant_SinkPile0-service.png) · [close](renders/Restaurant_SinkPile0-close.png) | [.blend](blends/Restaurant_SinkPile0.blend) |
| [Restaurant_SinkPile3](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_SinkPile3.fbx) | 1020 | 0.480 × 0.087 × 0.280 | [38°](renders/Restaurant_SinkPile3-service.png) · [close](renders/Restaurant_SinkPile3-close.png) | [.blend](blends/Restaurant_SinkPile3.blend) |
| [Restaurant_SinkPile6](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_SinkPile6.fbx) | 1452 | 0.480 × 0.137 × 0.280 | [38°](renders/Restaurant_SinkPile6-service.png) · [close](renders/Restaurant_SinkPile6-close.png) | [.blend](blends/Restaurant_SinkPile6.blend) |
| [Restaurant_FishCrateOpen](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_FishCrateOpen.fbx) | 1617 | 0.544 × 0.252 × 0.396 | [38°](renders/Restaurant_FishCrateOpen-service.png) · [close](renders/Restaurant_FishCrateOpen-close.png) | [.blend](blends/Restaurant_FishCrateOpen.blend) |
| [Restaurant_Gull_Stand](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_Gull_Stand.fbx) | 676 | 0.183 × 0.353 × 0.384 | [38°](renders/Restaurant_Gull_Stand-service.png) · [close](renders/Restaurant_Gull_Stand-close.png) | [.blend](blends/Restaurant_Gull_Stand.blend) |
| [Restaurant_Gull_Flap](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_Gull_Flap.fbx) | 498 | 0.810 × 0.353 × 0.384 | [38°](renders/Restaurant_Gull_Flap-service.png) · [close](renders/Restaurant_Gull_Flap-close.png) | [.blend](blends/Restaurant_Gull_Flap.blend) |
| [Restaurant_Spill](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_Spill.fbx) | 200 | 0.570 × 0.014 × 0.391 | [38°](renders/Restaurant_Spill-service.png) · [close](renders/Restaurant_Spill-close.png) | [.blend](blends/Restaurant_Spill.blend) |

## Assembly and runtime handoff

- Dish servings are complete carryable models: sharing platter has a larger handled board; fries/bread have open baskets; tea includes tray, cup, saucer and pot. Beer uses an amber silhouette, pale rim/foot/highlight and foam because the canonical shader is opaque. GlassEmpty has a hollow interior and last-sip detail; transparency is not required.
- Dirty2/Dirty4 contain exactly 2/4 offset used plates, visible sauce, crumbs and a fish skeleton on top; Clean contains exactly 6 nested plates. SinkPile0/3/6 each include the same compact steel basin liner and the named number of plates, making each a complete mutually exclusive state.
- Existing `Restaurant_SinkDishRack` total bounds are 1.84 × 0.83 × 0.82 m. Its inner basin opening is only about 0.562 × 0.328 m. New liner is 0.480 × 0.280 m; place its bottom-centred pivot at approximately **Unity local (+0.399, +0.323, +0.041)** relative to that unmodified sink model root, with no extra rotation/scale. This fits the insert below the rim at Y≈0.498 m, including the six-plate pile. [Full sink service fit](renders/sink-fit-service.png) and [basin close fit](renders/sink-fit-close.png) were also opened. The asymmetric legacy sink root is the reason for the offset.
- FishCrateOpen has open hand-grip slats, pale ice, two whole fish and a teal catch-label glyph. Gulls have separate Stand/Flap FBXs, each approximately 0.35 m high; Flap span is approximately 0.81 m. Their appearance faces toward local +Z. Spill is a flat scalloped puddle with food scraps and detached drops; full height is 0.014 m.
- Runtime integration belongs to Claude: `RestaurantWorld.DishModel()` still maps several of these dishes to legacy stand-ins at inspection time. Rebuild/refresh the model catalogue and map each new asset basename (normally remove `Restaurant_` for lookup); wire table, sink, crate, gull and spill states. ArtLibrary/native rendering was not run or changed here. Native night-light/readability acceptance remains for integration.

## Verification and reproduction

[manifest.json](manifest.json) stores exact sizes/counts, FBX hashes, camera parameters and explicit inspection status. [review-notes.json](review-notes.json) records the per-item visual findings. [export-audit.json](export-audit.json) records successful reimport checks and preservation hashes for all inspected dependencies. [preservation-baseline.json](preservation-baseline.json) is the original baseline. [artifact-check.json](artifact-check.json) checks all deliverables and unique importer GUIDs. [source-and-evidence.sha256](source-and-evidence.sha256) inventories the delivered evidence and asset/source files.

`build_service.py` authors the meshes, exports FBXs/metas and renders both views. Run from the project root with Blender 5.x:

```sh
blender -b --python-exit-code 1 -t 6 --python Art/Source/RestaurantService/build_service.py
blender -b --python-exit-code 1 -t 2 --python Art/Source/RestaurantService/audit_exports.py
blender -b --python-exit-code 1 -t 6 --python Art/Source/RestaurantService/render_sink_fit.py
```

An individual recipe key may follow `--` (for example `-- FishAndChips` or `-- SinkPile6`). The Linux Blender operator registration was incomplete, so these scripts use the bundled FBX importer/exporter directly; no Blender installation files were changed. `finalize_geometry.py` performs an optional idempotent cleanup/reexport of saved blends. Each blend contains one delivery mesh and clearly named review-only reference/camera/floor/lights; only the delivery mesh goes into the FBX. Rebuilding resets visual-review status to pending and requires opening the new frames again.

No main-project batchmode or scratch Unity was used; Blender reimport, metadata and visual evidence do not claim native integration or Mo acceptance. Temporary `.blend1` backups were removed after successful verification. No remaining asset-build steps or subagents.

# SERVICE-PROPS-2

Codex 2 (WSL CLI), 2026-10-28. **Asset delivery complete: 12 FBXs and 24 individually opened evidence frames.** Additive cooking, table-payment and harbour-event assets following the accepted SERVICE-PROPS-1 atlas and chunky geometry. No git or Unity invocation. The previous delivery above remains unchanged.

All new models use one `RestaurantAtlas` material, explicitly remapped to `Assets/Art/Models/Restaurant/RestaurantAtlas.mat` (`Catchline/RestaurantAtlas`), white vertex colours and UVs on the existing atlas. Flat low-poly geometry; metres; FBX Y up. Pivots are bottom-centred, except the ferry whose explicit waterline Y=0 takes precedence. No particle, transparent-material or runtime text dependency is needed for cooking food, steam/smoke, coins or ferry windows.

Fit measurements target the specifically requested `Pack/Restaurant_<station>.fbx` files at scale 1, rather than the differently dressed `EXPORT_*` stations in Stage1V4. Local placements below are **Unity (X,Y,Z), no extra rotation, scale 1** relative to the named station root for the eight cooking props. The two tip piles, CatchBoard and Ferry rows instead give room/pier-root review placements; use the measured contact height when placing on another table or quay. Horizontal offsets account for handles and the required bottom-centred pivot. Unity placement uses the documented FBX reflection: Blender (x,y,z) → Unity (-x,z,-y). [Station measurements](cooking-measurements.json) contain Blender Z-up bounds, footprint XY bounds and Unity Y surface heights. [Station inspection](renders/cooking-stations-inspection.png) was opened.

| Asset | Tris | Unity size X × Y × Z (m) | Station / surface | Top Y (m) | Local pivot (m) | Opened evidence | Source |
|---|---:|---|---|---:|---|---|---|
| [Restaurant_Cook_Pan](../../../Assets/Art/Models/Restaurant/Pack/cooking/Restaurant_Cook_Pan.fbx) | 788 | 0.488 × 0.231 × 0.320 | Stove | 0.8 | (0.14625, 0.8, 0.138) | [38°](renders/Restaurant_Cook_Pan-service.png) · [close](renders/Restaurant_Cook_Pan-close.png) | [.blend](blends/Restaurant_Cook_Pan.blend) |
| [Restaurant_Cook_Grill](../../../Assets/Art/Models/Restaurant/Pack/cooking/Restaurant_Cook_Grill.fbx) | 361 | 0.247 × 0.231 × 0.459 | Grill | 0.825 | (-0.005984, 0.825, -0.015481) | [38°](renders/Restaurant_Cook_Grill-service.png) · [close](renders/Restaurant_Cook_Grill-close.png) | [.blend](blends/Restaurant_Cook_Grill.blend) |
| [Restaurant_Cook_FryerBasket](../../../Assets/Art/Models/Restaurant/Pack/cooking/Restaurant_Cook_FryerBasket.fbx) | 1116 | 0.416 × 0.244 × 0.502 | Fryer | 0.91 | (0, 0.91, 0.093) | [38°](renders/Restaurant_Cook_FryerBasket-service.png) · [close](renders/Restaurant_Cook_FryerBasket-close.png) | [.blend](blends/Restaurant_Cook_FryerBasket.blend) |
| [Restaurant_Cook_OvenTray](../../../Assets/Art/Models/Restaurant/Pack/cooking/Restaurant_Cook_OvenTray.fbx) | 804 | 0.597 × 0.256 × 0.340 | Oven | 1.2 | (0, 1.2, 0) | [38°](renders/Restaurant_Cook_OvenTray-service.png) · [close](renders/Restaurant_Cook_OvenTray-close.png) | [.blend](blends/Restaurant_Cook_OvenTray.blend) |
| [Restaurant_Cook_SteamPot](../../../Assets/Art/Models/Restaurant/Pack/cooking/Restaurant_Cook_SteamPot.fbx) | 960 | 0.616 × 0.466 × 0.446 | Steamer | 0.92 | (0, 0.92, -0.002086) | [38°](renders/Restaurant_Cook_SteamPot-service.png) · [close](renders/Restaurant_Cook_SteamPot-close.png) | [.blend](blends/Restaurant_Cook_SteamPot.blend) |
| [Restaurant_Cook_SoupLadle](../../../Assets/Art/Models/Restaurant/Pack/cooking/Restaurant_Cook_SoupLadle.fbx) | 608 | 0.364 × 0.218 × 0.343 | SoupKettle | 0.660388 | (-0.05413, 0.660388, 0) | [38°](renders/Restaurant_Cook_SoupLadle-service.png) · [close](renders/Restaurant_Cook_SoupLadle-close.png) | [.blend](blends/Restaurant_Cook_SoupLadle.blend) |
| [Restaurant_Cook_BreadBoard](../../../Assets/Art/Models/Restaurant/Pack/cooking/Restaurant_Cook_BreadBoard.fbx) | 568 | 0.385 × 0.104 × 0.205 | PrepCounter | 0.825 | (-0.14225, 0.825, 0.032365) | [38°](renders/Restaurant_Cook_BreadBoard-service.png) · [close](renders/Restaurant_Cook_BreadBoard-close.png) | [.blend](blends/Restaurant_Cook_BreadBoard.blend) |
| [Restaurant_Cook_Burnt](../../../Assets/Art/Models/Restaurant/Pack/cooking/Restaurant_Cook_Burnt.fbx) | 584 | 0.488 × 0.343 × 0.320 | Grill | 0.825 | (-0.08375, 0.825, 0) | [38°](renders/Restaurant_Cook_Burnt-service.png) · [close](renders/Restaurant_Cook_Burnt-close.png) | [.blend](blends/Restaurant_Cook_Burnt.blend) |
| [Restaurant_TipCoins_S](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_TipCoins_S.fbx) | 560 | 0.119 × 0.025 × 0.102 | Stage1V4 EXPORT_DiningTwo_Cloth_Four upper cloth | 0.812 | (-1.35, 0.812, -0.28) | [38°](renders/Restaurant_TipCoins_S-service.png) · [close](renders/Restaurant_TipCoins_S-close.png) | [.blend](blends/Restaurant_TipCoins_S.blend) |
| [Restaurant_TipCoins_L](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_TipCoins_L.fbx) | 1124 | 0.190 × 0.036 × 0.162 | Stage1V4 EXPORT_DiningTwo_Cloth_Four upper cloth | 0.812 | (-1.35, 0.812, -0.28) | [38°](renders/Restaurant_TipCoins_L-service.png) · [close](renders/Restaurant_TipCoins_L-close.png) | [.blend](blends/Restaurant_TipCoins_L.blend) |
| [Restaurant_CatchBoard](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_CatchBoard.fbx) | 451 | 0.592 × 0.900 × 0.410 | RestaurantPier Pier_S1 quay approach | 0 | (5.6, 0, -3.65) | [38°](renders/Restaurant_CatchBoard-service.png) · [close](renders/Restaurant_CatchBoard-close.png) | [.blend](blends/Restaurant_CatchBoard.blend) |
| [Restaurant_Ferry](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_Ferry.fbx) | 3236 | 9.004 × 3.788 × 2.773 | RestaurantPier quay / AddSea | -0.57 | (-10.5, -0.57, -2.65) | [38°](renders/Restaurant_Ferry-service.png) · [close](renders/Restaurant_Ferry-close.png) | [.blend](blends/Restaurant_Ferry.blend) |

## Fit and visual findings

- **Restaurant_Cook_Pan**: 788tris; pink fillet and golden butter clear in both final views, skillet rests on front-left burner. Station-local Unity pivot(+0.14625,0.800,0.138).
- **Restaurant_Cook_Grill**: 361tris; whole golden fish, head and tail clear, four dark scores conform to its faceted surface; rests on grate Y0.825. Thin fin/tail/char faces explicitly oriented upward.
- **Restaurant_Cook_FryerBasket**: Both final frames opened; five rounded golden pieces rest visibly on raised wire basket, navy handle reads clearly. Rim support Y0.910; 1116 triangles.
- **Restaurant_Cook_OvenTray**: Both final frames opened; cream platter, two golden fish portions, lemon and green garnish remain distinct under warm light. Tray and side grips sit on Oven top Y1.200, no centring correction; 804tris.
- **Restaurant_Cook_SteamPot**: Both final frames opened; orange two-pronged crab claw and tilted steel lid read above navy-banded pot. Recessed underside clears original 0.10m lid knob; support Y0.920. 960tris.
- **Restaurant_Cook_SoupLadle**: Both final frames opened; pale broth overlay nests within original soup/rim, navy-handled steel ladle clears rim Y0.740 and vegetables remain readable. Surface/pivot support Y0.660388; Unity X offset -0.054130. 608tris.
- **Restaurant_Cook_BreadBoard**: Both corrected final frames opened; scores conform to loaf, two cut slices show pale crumb, knife and crumbs read on board. Board fits existing PrepCounter board at Y0.825; Unity pivot(-0.142250,0.825,+0.032365). 568tris.
- **Restaurant_Cook_Burnt**: Both final frames opened; ink-black fillet, toasted cracks and thicker charcoal smoke clearly signal burnt food against warm pan. Bottom sits on Grill grate Y0.825; 584tris.
- **Restaurant_TipCoins_S**: Both corrected final frames opened; gold stack and two loose coins with folded ivory/teal note clearly rest on visible cloth Y0.812, not base furniture Y0.7225. Width0.119m;560tris.
- **Restaurant_TipCoins_L**: Both final frames opened; two raised gold stacks plus three loose coins and larger folded note distinguish large payment. Width0.190m;1124tris; visible tablecloth support Y0.812.
- **Restaurant_CatchBoard**: Both final frames opened; CATCH / of the day fixed white header reads on 0.900m honey timber A-frame at actual quay approach, blank lower slate and chalk stub clear. Final451tris, no orphan edges/degenerate faces or FBX layer warnings. Deck supportY0; blank panel contract in manifest.
- **Restaurant_Ferry**: Both final frames opened; 9.004m navy/cream passenger ferry moored beside actual quay, raised wheelhouse, glowing window rows, safety rails, four life rings, open boarding deck and benches read clearly.3236tris below4000. Local waterlineY0 with0.620m draught; room sea/pivotY-0.570. Canonical atlas emission only.

The original Steamer has a broad closed lid at Y=0.920 and a knob reaching Y=1.020. The SoupKettle already has soup at Y=0.660388, inside the rim at Y=0.740. These file/brief differences were logged as QUESTION entries and followed. PrepCounter worktop is Y=0.790; its existing cutting board is Y=0.825.

## Table, slate and ferry placement contracts

The tip evidence uses the visible `EXPORT_DiningTwo_Cloth_Four` cloth at room Y=0.811999 (rounded placement 0.812), rather than the bare furniture top at 0.7225. The raw Pack tables are different: measure their own support if using them. [All-room contact rays](service-contact-measurements.json) identify the actual upper cloth. Coin pile widths are 0.119 m and 0.190 m.

CatchBoard front faces local Unity **+Z**. Its blank drawing area is 0.40 m wide × 0.31 m high, centred at local **(0, 0.445, 0.124)**. Normalize the normal `(0, 0.191011, 1)` and up `(0, 1, -0.191011)` vectors before use to follow the backward-leaning slate; centre and vectors are also recorded without rounding in the manifest. The fixed mesh heading sits above this area. Add the fish just above the surface along that normal.

Ferry local **Y=0 is the waterline**, with 0.620 m of hull below it. In the supplied pier context set its root to sea Y=-0.570; do not put the bottom of the hull on the water. Length is 9.0036 m along local X, bow/forward **-X**. Identity rotation at room/pier `(-10.5,-0.57,-2.65)` moors it parallel to the actual quay. Window UVs use existing yellow atlas cell `(3,2)`, whose Surface.B drives the canonical shader emission ×2.8. No new material or lighting texture is required.

## Evidence and checks

Required pairs show each prop on its measured Pack station or actual room table, or at the quay, at 38° service pitch and a closer 55° angle. Warm practical light and blue harbour fill use the actual Stage1V4 room as context. Station reviews substitute the unmodified named Pack station into the room prep slot in memory only. No room/station/pier source file is edited. Production blends contain only the delivery mesh with packed atlas images; review context is reconstructed by the builder. Blender evidence does not claim native Unity import or runtime night acceptance.

[cooking-manifest.json](cooking-manifest.json) records dimensions, exact placements, counts, FBX hashes and inspection status. [cooking-visual-review.json](cooking-visual-review.json) records opened-frame findings and SHA256 hashes. [cooking-audit.json](cooking-audit.json) contains independent FBX reimport results: budgets, correct Y-up/metre global settings, bottom-centred pivots, exact sizes/counts, one material, valid UVs/white colours and zero degenerate triangles. [cooking-source-audit.json](cooking-source-audit.json) checks the twelve production blends and their packed atlas images. [cooking-artifact-check.json](cooking-artifact-check.json) checks opened-frame hashes, unique GUIDs, report links and preservation of the earlier delivery. [cooking-source-and-evidence.sha256](cooking-source-and-evidence.sha256) seals this delivery. [cooking-preservation-baseline.json](cooking-preservation-baseline.json) seals the 104 original station/dish/service/atlas/room/pier dependencies.

Reproduce one item from the project root (Blender 5.x, no Unity):

```sh
blender -b -t 8 --python-exit-code 1 --python Art/Source/RestaurantService/build_cooking.py -- Pan
blender -b -t 2 --python-exit-code 1 --python Art/Source/RestaurantService/audit_cooking.py
```

Recipe keys: `Pan`, `Grill`, `FryerBasket`, `OvenTray`, `SteamPot`, `SoupLadle`, `BreadBoard`, `Burnt`, `TipCoins_S`, `TipCoins_L`, `CatchBoard`, `Ferry`. Pass a recipe key to build one item. Regeneration resets its review status to pending; open both new frames before recording review. Runtime catalogue registration, cooking/tip/event states and native acceptance belong to Claude. No .cs, Resources/Restaurant, RestaurantPier or Crew files were changed.


# SERVICE-PROPS-3

Codex 2 (WSL CLI), 2026-10-28. Accepted by Claude/Mo and wired by Claude (comms.md 16:00). This section closes the interrupted D4/E reporting only; accepted models and existing renders are unchanged.

| Item | Tris | Delivered file | Existing evidence |
|---|---:|---|---|
| Restaurant_TipCoins_S | 1004 | [Restaurant_TipCoins_S.fbx](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_TipCoins_S.fbx) | [Restaurant_TipCoins_S-service](renders/props3-Restaurant_TipCoins_S-service.png) · [Restaurant_TipCoins_S-close](renders/props3-Restaurant_TipCoins_S-close.png) |
| Restaurant_TipCoins_L | 2124 | [Restaurant_TipCoins_L.fbx](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_TipCoins_L.fbx) | [Restaurant_TipCoins_L-service](renders/props3-Restaurant_TipCoins_L-service.png) · [Restaurant_TipCoins_L-close](renders/props3-Restaurant_TipCoins_L-close.png) |
| Restaurant_Guest_Critic | 2408 | [Restaurant_Guest_Critic.fbx](../../../Assets/Art/Models/Restaurant/Guests/Restaurant_Guest_Critic.fbx) | [Restaurant_Guest_Critic-walk-service](renders/props3-Restaurant_Guest_Critic-walk-service.png) · [Restaurant_Guest_Critic-sit-service](renders/props3-Restaurant_Guest_Critic-sit-service.png) · [Restaurant_Guest_Critic-eat-service](renders/props3-Restaurant_Guest_Critic-eat-service.png) · [Restaurant_Guest_Critic-front-close](renders/props3-Restaurant_Guest_Critic-front-close.png) · [Restaurant_Guest_Critic-side-close](renders/props3-Restaurant_Guest_Critic-side-close.png) · [Restaurant_Guest_Critic-back-close](renders/props3-Restaurant_Guest_Critic-back-close.png) |
| Restaurant_Dish_IceCream | 1344 | [Restaurant_Dish_IceCream.fbx](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_IceCream.fbx) | [Restaurant_Dish_IceCream-service](renders/props3-Restaurant_Dish_IceCream-service.png) · [Restaurant_Dish_IceCream-close](renders/props3-Restaurant_Dish_IceCream-close.png) |
| Restaurant_Dish_Pudding | 780 | [Restaurant_Dish_Pudding.fbx](../../../Assets/Art/Models/Restaurant/Pack/dishes/Restaurant_Dish_Pudding.fbx) | [Restaurant_Dish_Pudding-service](renders/props3-Restaurant_Dish_Pudding-service.png) · [Restaurant_Dish_Pudding-close](renders/props3-Restaurant_Dish_Pudding-close.png) |
| Restaurant_WarmingLamp | 1064 | [Restaurant_WarmingLamp.fbx](../../../Assets/Art/Models/Restaurant/Pack/gadgets/Restaurant_WarmingLamp.fbx) | [Restaurant_WarmingLamp-service](renders/props3-Restaurant_WarmingLamp-service.png) · [Restaurant_WarmingLamp-close](renders/props3-Restaurant_WarmingLamp-close.png) |
| Restaurant_ServiceBell | 768 | [Restaurant_ServiceBell.fbx](../../../Assets/Art/Models/Restaurant/Pack/gadgets/Restaurant_ServiceBell.fbx) | [Restaurant_ServiceBell-service](renders/props3-Restaurant_ServiceBell-service.png) · [Restaurant_ServiceBell-close](renders/props3-Restaurant_ServiceBell-close.png) |
| Restaurant_Bunting | 1400 | [Restaurant_Bunting.fbx](../../../Assets/Art/Models/Restaurant/Pack/gadgets/Restaurant_Bunting.fbx) | [Restaurant_Bunting-service](renders/props3-Restaurant_Bunting-service.png) · [Restaurant_Bunting-close](renders/props3-Restaurant_Bunting-close.png) |
| Restaurant_PlateRack | 1264 | [Restaurant_PlateRack.fbx](../../../Assets/Art/Models/Restaurant/Pack/gadgets/Restaurant_PlateRack.fbx) | [Restaurant_PlateRack-service](renders/props3-Restaurant_PlateRack-service.png) · [Restaurant_PlateRack-close](renders/props3-Restaurant_PlateRack-close.png) |

Sources: [build_props3.py](build_props3.py), [build_critic3.py](build_critic3.py), per-item `blends/props3-*.blend`, [props3-manifest.json](props3-manifest.json). Independent static FBX readback: [props3-audit.json](props3-audit.json) PASS eight non-rig props, canonical atlas, complete UV/colour corner layers, Y-up metres and no degenerate triangles; 524 dependencies preserved at that audit. [props3-critic-audit.json](props3-critic-audit.json) PASS critic 2408 tris, exact Ada 20-bone skeleton, thirteen clips, zero sampled matrix error. [props3-visual-review.json](props3-visual-review.json) records prior personally opened evidence for completed items; rack final pair existed when usage interrupted, and acceptance came from Claude/Mo. No new PROPS-3 render or runtime verification performed in this closure.

Separate lamp `Bulb`; opaque pack glass convention for sundae. Existing evidence is warm Stage1V4 room service/detail Blender renders, not native gameplay acceptance. Critic seated source proof used evidence-only height adjustment; unchanged Ada clips were delivered. Runtime wiring/acceptance belongs to Claude and is recorded in the canonical diary. No git/commit.

# SERVICE-PROPS-4

Codex 2 (WSL CLI), 2026-10-28. Ten additive harbour-cafe/event props, 9,002 triangles combined; each below 2,000 triangles. All use the existing **Catchline/RestaurantAtlas** material. No accepted SERVICE-PROPS-3 model or render was changed. Its missing report and PlateRack completion line were closed first.

| Item | Tris | FBX | Source | Inspected evidence |
|---|---:|---|---|---|
| Restaurant_Wall_ShipWheel | 1096 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/dressing/Restaurant_Wall_ShipWheel.fbx) | [blend](blends/props4-Restaurant_Wall_ShipWheel.blend) | [service](renders/props4-Restaurant_Wall_ShipWheel-service.png) · [close](renders/props4-Restaurant_Wall_ShipWheel-close.png) |
| Restaurant_Wall_FishPrint | 374 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/dressing/Restaurant_Wall_FishPrint.fbx) | [blend](blends/props4-Restaurant_Wall_FishPrint.blend) | [service](renders/props4-Restaurant_Wall_FishPrint-service.png) · [close](renders/props4-Restaurant_Wall_FishPrint-close.png) |
| Restaurant_Wall_NetFloats | 1692 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/dressing/Restaurant_Wall_NetFloats.fbx) | [blend](blends/props4-Restaurant_Wall_NetFloats.blend) | [service](renders/props4-Restaurant_Wall_NetFloats-service.png) · [close](renders/props4-Restaurant_Wall_NetFloats-close.png) |
| Restaurant_Wall_BottleShelf | 1136 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/dressing/Restaurant_Wall_BottleShelf.fbx) | [blend](blends/props4-Restaurant_Wall_BottleShelf.blend) | [service](renders/props4-Restaurant_Wall_BottleShelf-service.png) · [close](renders/props4-Restaurant_Wall_BottleShelf-close.png) |
| Restaurant_Puddle_S | 132 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_Puddle_S.fbx) | [blend](blends/props4-Restaurant_Puddle_S.blend) | [service](renders/props4-Restaurant_Puddle_S-service.png) · [close](renders/props4-Restaurant_Puddle_S-close.png) |
| Restaurant_Puddle_L | 132 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_Puddle_L.fbx) | [blend](blends/props4-Restaurant_Puddle_L.blend) | [service](renders/props4-Restaurant_Puddle_L-service.png) · [close](renders/props4-Restaurant_Puddle_L-close.png) |
| Restaurant_UmbrellaStand | 1624 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_UmbrellaStand.fbx) | [blend](blends/props4-Restaurant_UmbrellaStand.blend) | [service](renders/props4-Restaurant_UmbrellaStand-service.png) · [close](renders/props4-Restaurant_UmbrellaStand-close.png) |
| Restaurant_PaperLanterns | 1852 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_PaperLanterns.fbx) | [blend](blends/props4-Restaurant_PaperLanterns.blend) | [service](renders/props4-Restaurant_PaperLanterns-service.png) · [close](renders/props4-Restaurant_PaperLanterns-close.png) |
| Restaurant_ReservedSign | 88 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/service/Restaurant_ReservedSign.fbx) | [blend](blends/props4-Restaurant_ReservedSign.blend) | [service](renders/props4-Restaurant_ReservedSign-service.png) · [close](renders/props4-Restaurant_ReservedSign-close.png) |
| Restaurant_Wall_LifeRing | 876 | [FBX](../../../Assets/Art/Models/Restaurant/Pack/dressing/Restaurant_Wall_LifeRing.fbx) | [blend](blends/props4-Restaurant_Wall_LifeRing.blend) | [service](renders/props4-Restaurant_Wall_LifeRing-service.png) · [close](renders/props4-Restaurant_Wall_LifeRing-close.png) |

## Placement and attachment contracts

[dressing-placement.json](dressing-placement.json) is the handoff: **RoomRoot-local, Unity Y up, metres**, yaw around +Y, scale 1. Local +X is screen-left in this room. Every wall mesh faces local +Z and uses its back/contact centre as pivot. Other props use a bottom-centred pivot, except the left-end lantern string. No wall/rain/festival dressing occupies the configurable dining floor.

| Group / item | RoomRoot position (X, Y, Z) m | Yaw |
|---|---|---:|
| wall / Wall_LifeRing | [-0.36, 1.57, -2.465] | 0° |
| wall / Wall_ShipWheel | [-3.94, 0.61, -1.05] | 90° |
| wall / Wall_FishPrint | [-3.8, 1.43, -2.465] | 0° |
| wall / Wall_NetFloats | [-3.94, 0.6, -0.12] | 90° |
| wall / Wall_BottleShelf | [-3.94, 0.81, 1.46] | 90° |
| rain / Puddle_S | [2.7, 0.0255, 3.94] | -14° |
| rain / Puddle_L | [-2.55, 0.001, 3.65] | 8° |
| rain / UmbrellaStand | [-3.85, 0.001, 2.9] | -16° |
| festival / PaperLanterns | [-3, 2.5, -2.465] | 0° |
| critic / ReservedSign | [-1.35, 0.814, -0.71] | 0° |

The existing back wall already carries a fish board, menu and practical lamps; the right wall is a low cutaway with coping at about Y1.02. The five pieces fit the actual remaining wall gaps. The wheel and net remain below the right coping. The shelf is raised above the planter leaves so all five bottles read. The net has four sea-green glass floats; the framed fish and bottle labels have no words. These differences from the bare-wall brief were recorded as QUESTION entries and resolved against the files.

Rain: Puddle_S is wholly on terrace paving (upper bevel Y0.025, pivot Y0.0255). Puddle_L and UmbrellaStand sit on the actual RestaurantPier deck (Y0, pivots Y0.001), rather than the lower RoomShell understructure. The puddles are solid shallow glossy sea-blue lenses with broken glints, approximately 3 mm thick. The stand contains three furled umbrellas in coral, teal and cream, clear of the door and mat.

Festival: **Restaurant_PaperLanterns extends exactly 6 m along local +X from its left attachment**. At the suggested root (-3, 2.5, -2.465), the other end is (+3, 2.5, -2.465); papers stay above the rear coping. Each of the six `Lantern_01` … `Lantern_06` frame meshes has a paper mesh child whose raw FBX name is exactly **Glow**. Blender shows unique Glow / Glow.001 … IDs; the FBX exporter deliberately emits six exact Glow names. Papers use the existing emitting yellow atlas cell, not a new material. Export disables experimental space baking for this hierarchy; independent readback verifies bounds and parent relationships.

Critic: ReservedSign is a brass folded card with two cream inset faces and a navy beret symbol on its front, no words. **Attach it to the selected critic table**, with 2 mm clearance above that table’s actual top. Its absolute JSON position is evidence/demo only: clear rear cloth edge of EXPORT_DiningTwo_Cloth_Four, between settings and behind the candle. The suggested table offset is (0, -0.23) in local X/Z; choose a clear edge on other table models and do not use the demo room coordinates as a fixed floor spawn.

## Evidence and verification

All twenty final PNGs were opened and inspected individually. Each service image imports the delivered FBX and places it at the JSON coordinates in the actual Stage1V4 room and Stage1 RestaurantPier context; prior completed props accumulate in later views. Warm practicals, blue dusk fill and the measured live service camera (38° pitch, yaw178°, vertical FOV21.9542°) establish night readability. Close views inspect geometry, surface contact, colours and symbols. The lantern close shows one paper in detail; its service view shows all six. LifeRing evidence was refreshed with the completed scene and reopened, without changing its model.

The evidence scene hides only the obsolete baked CoffeeBar and CoffeeCup, matching their removal by RestaurantWorld.LayoutPieces. It does not edit room files. Static room evidence does not contain IMGUI/table pins or live moving guests and does not claim native gameplay acceptance; dressing is kept at walls/fixed exterior edges, and the critic card remains table-bound. Native event activation and final runtime acceptance belong to Claude.

- [props4-manifest.json](props4-manifest.json): triangles, dimensions, FBX hashes, sources and evidence paths.
- [props4-visual-review.json](props4-visual-review.json): findings and current hashes of the twenty opened images.
- [props4-audit.json](props4-audit.json): independent FBX readback for all ten; triangle budgets, Y-up/metres, pivots, dimensions, canonical material references, complete normal/UV/colour corner layers, zero degenerate triangles, six exact Glow children.
- [props4-source-audit.json](props4-source-audit.json): ten production blends; only delivery meshes, identity authoring transforms and two packed atlas images each.
- [props4-artifact-check.json](props4-artifact-check.json): current source/export/render hashes, unique importer GUIDs, placements and report links.
- [props4-preservation.json](props4-preservation.json) and [props4-external-dependency-changes.json](props4-external-dependency-changes.json): 335 of 336 baseline dependencies unchanged; one concurrent out-of-scope CrewRig_Restaurant.fbx.meta update is recorded with exact before/current hashes and left untouched. All accepted service FBXs and room/atlas dependencies remain unchanged.
- [props4-source-and-evidence.sha256](props4-source-and-evidence.sha256): final delivery inventory.

Sources: [build_props4.py](build_props4.py), [audit_props4.py](audit_props4.py), [audit_props4_sources.py](audit_props4_sources.py), [check_props4_artifacts.py](check_props4_artifacts.py), [props4_inspect.py](props4_inspect.py), [props4_review.py](props4_review.py). Builder reuses accepted service pack geometry/material helpers without editing them.

Reproduce one item with Blender 5.x from the checkout root (no Unity):

```sh
blender -b -t 6 --python-exit-code 1 --python Art/Source/RestaurantService/build_props4.py -- PaperLanterns
blender -b -t 3 --python-exit-code 1 --python Art/Source/RestaurantService/audit_props4.py
blender -b -t 3 --python-exit-code 1 --python Art/Source/RestaurantService/audit_props4_sources.py
python3 Art/Source/RestaurantService/check_props4_artifacts.py
```

Recipe keys: Wall_LifeRing, Wall_ShipWheel, Wall_FishPrint, Wall_NetFloats, Wall_BottleShelf, Puddle_S, Puddle_L, UmbrellaStand, PaperLanterns, ReservedSign. Regeneration resets review to pending; open both new frames before recording review. `--render-only` refreshes evidence without touching the FBX/source; refreshed images require a new visual hash record.

No C#, Resources, UIv3, Crew/guest source or accepted prop writes. No git commands, commit, Unity execution or subagents. Static art delivery is complete; runtime wiring and native acceptance remain outside this assignment.

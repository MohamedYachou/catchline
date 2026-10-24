# Catchline / SeaV2 art handoff

24 October 2026. Codex 1 (Windows app). All five approved MAP-PLAN art packages complete; native/Mo acceptance pending.

[Five-map overview](SeaV2-overview.png). Each map report links the authored geometry, navigation contract and review evidence.

| Map / report | Playable size | Triangles / parts | Land / shallow outlines | Buoys | Nav / fresh source checks |
|---|---|---|---|---|---|
| [Harbour mouth](GullHarbourMouth/SeaV2-REPORT.md) | 220 x 160 m | 25,596 / 327 | 7 / 7 | 28 | 61 / 43 |
| [Kelp bank](GullKelpBank/SeaV2-REPORT.md) | 260 x 180 m | 20,142 / 387 | 3 / 3 | 34 | 45 / 23 |
| [Sandbar](GullSandbar/SeaV2-REPORT.md) | 260 x 200 m | 19,458 / 217 | 1 / 1 | 36 | 37 / 13 |
| [Rocky point](GullRockyPoint/SeaV2-REPORT.md) | 280 x 200 m | 19,272 / 241 | 4 / 4 | 36 | 49 / 28 |
| [Deep channel](GullDeepChannel/SeaV2-REPORT.md) | 320 x 240 m | 19,620 / 239 | 2 / 2 | 42 | 41 / 18 |

104,088 triangles across five models; 15 original ground IDs/names/pool IDs/nominal depths retained. 233 freshly recomputed art-side navigation checks and 125 independent saved-source/actual-FBX checks pass. All 55 current per-map PNGs were individually opened and hash-recorded. The index decodes all 55 again and verifies both runtime copies for every map. All 114 protected legacy files match the pre-task SHA256 baseline.

## Files to integrate

Each `Art/Models/Maps/<Map>/` contains `<Map>SeaV2.blend`, `<Map>SeaV2.fbx`, `navigation.json`, three ground day/night pairs, wide day/night, a top base, an annotated navigation plate and a review sheet. `SeaV2-Review-only.blend` retains the boat/water/lighting setup. Source models contain geometry only; review boat, camera, water, fog and lights are excluded from FBX.

Byte-identical new `<Map>SeaV2.fbx` and `navigation.json` are published under `Assets/Art/Models/Environment/<Map>/`. Do not substitute old GroundsV1 anchors or recenter the export. All existing assets and metadata remain intact. New Unity metadata/import binding belongs to the integrating owner.

Place the model at WORLD `(0,-0.32,0)`, identity rotation/scale. Navigation uses WORLD XZ metres. Boat anchors are WORLD deck centres at Y=0, independent of the map-root translation. Authoring Blender coordinates are `(worldX,-worldZ,height)`; the compensated FBX transform is covered by actual importer readback. Model bounds include seabed and unreachable horizon art, so they do not describe playable camera bounds.

Navigation polygons are actual closed mesh slices at local waterline0 and -1m, CCW and at most64 vertices. Ground zones/harbour/buoys clear land inflated2m; ground zones also clear shallows and stay inside the border. Border buoys are25-30m apart. Independent routes for radius2m and4m connect all six harbour/ground pairs in each map; at least one ground pair per map has a blocked direct line. The annotated plates show the three direct ground-pair arrows and audited detours.

## Review and remaining acceptance

The orthographic ground camera has horizontal span10.24m, pitch45/yaw35 at1440x900. Each recorded sample anchor lies within its ground zone. Day/night share the same model; lighting/depth water/fog presets are in each map folder. Rocky point uses a clearer review-water preset to expose submerged reef crowns and the shelf edge; its preset is recorded explicitly. Wide views include smooth30m border-fog falloff and distant silhouettes.

The views are Blender art evidence. They do not establish native water appearance, HUD/crew composition, sailing feel, touch behaviour or Mo acceptance. Claude/code-owner still owns runtime binding/imports, hull clearance/turning/shallow costs, arrival/departure, camera clamps, timing, and native1440x900 plus844x390 captures. Art-side static routes do not certify runtime travel duration;10-20s is a tuning request whose feasibility depends on physical distances and the speed policy.

The seven men and their completed hair fixes were skipped as instructed. Codex2 women/PropsV2 and runtime code remained outside this task. No Unity launch, C# or scene change, git operation or commit was made by this art task.

## Evidence and reproducibility

- `SeaV2-manifest.json`: exact file hashes, consolidated checks and map counts; excludes its own hash.
- `SeaV2-source-audit.json`: independent saved-source reopen, closed terrain, fresh edge slices compared to JSON and fresh actual-FBX imports.
- Per-map `SeaV2-validation.json`, `SeaV2-audit.json`, `SeaV2-visual-review.json` and `SeaV2-delivery.json`: geometry/route/current-image/runtime evidence.
- Builders/auditors: `Art/Source/Art108/{sea_v2_layouts,build_sea_v2,audit_sea_v2,finish_sea_v2,verify_sea_v2_sources,consolidate_sea_v2}.py`.

Read-only delivery recheck: `python Art/Source/Art108/consolidate_sea_v2.py`. It refreshes audits/index/overview only and verifies published files; it does not rebuild model geometry or individually reviewed map images.

Independent source recheck: Blender background with `--python Art/Source/Art108/verify_sea_v2_sources.py`. Rebuilding a map with `build_sea_v2.py -- <Map> build` or `review` invalidates its earlier review evidence: reopen every current image and use `finish_sea_v2.py <Map> --reviewed-all` only after that inspection. Publishing refuses changes to already-existing runtime bytes; coordinate any later revision with the integrating owner.

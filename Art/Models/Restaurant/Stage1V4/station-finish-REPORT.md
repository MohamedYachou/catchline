# STATION-FINISH-1 — runtime steel finishes

Source delivery by Codex 2 (WSL CLI). All eight runtime items and their Stage1V4 dressed copies carry the revised steel finish. UV0 translations only; geometry, topology, normals, transforms, names, material names/indices, baked AO, UV1 and footprints preserved. Atlas images/layout/cameras/lighting/metrics and Assets unchanged.

## Runtime mapping

RestaurantWorld.Models selects ArtLibrary Restaurant_<model>. Import-ready sources are the individual Stage1V2 items, not the V4 room assembly. Claude owns Assets import.

| ItemId | Model | Source under Stage1V2 | Footprint | Tris | Changed faces |
|---|---|---|---|---:|---:|
| Stove | Restaurant_Stove | items/Stove.fbx | 1 x 1 | 4,280 | 196 |
| Oven | Restaurant_Oven | items/Oven.fbx | 1 x 1 | 1,344 | 72 |
| Fridge | Restaurant_FridgeV2 | items/FridgeV2.fbx | 1 x 1 | 556 | 116 |
| Fryer | Restaurant_Fryer | items/Fryer.fbx | 1 x 1 | 3,420 | 196 |
| PrepCounter | Restaurant_PrepCounter | items/PrepCounter.fbx | 1 x 1 | 1,596 | 304 |
| SoupKettle | Restaurant_SoupKettle | items/SoupKettle.fbx | 1 x 1 | 1,304 | 44 |
| Sink | Restaurant_SinkDishRack | items/SinkDishRack.fbx | 2 x 1 | 2,860 | 372 |
| CoffeeMachine | Restaurant_CoffeeBar | items/CoffeeBar.fbx | 1 x 1 | 3,608 | 152 |

Stage1V2.blend is the matching editable library; legacy Stage1V2.fbx assembly is deliberately unchanged, since it is not this runtime source. Stage1V4.blend/Stage1V4.fbx contain the corresponding dressed copies. KitchenKit2 supplies other appliances and is untouched.

## Finish choices

Steel cabinet shells/inset doors for Stove/Fryer/PrepCounter/SinkDishRack; prep/sink worktops match. Steel oven panel/frame, retaining dark glass and warm racks. Kettle dark pot and steel lid remain; heated base is steel. Coffee machine casing/canopy are steel, service cabinet remains blue with ivory counter. Fridge doors/body were already steel; long handle now matches. Wood boards, towels, crockery, food, dark vents/glass, orange/brass controls and feet are preserved.

Measured connected components are recorded in station-finish-inventory.json and explicit polygon selections in station-finish-changes.json. Each changed loop moves by integer atlas-cell offsets to cell7; within-cell UV shape is preserved. V4 polygon topology matches exactly; only selected polygons change, preserving earlier room pigment.

## Fresh FBX bounds

Before = after within0.000001m; floor pivots identity, minimum Z zero. Coordinates metres.

| Model | Min X,Y,Z | Max X,Y,Z |
|---|---|---|
| Stove | -0.47000, -0.46850, -0.00000 | 0.47000, 0.42000, 0.81000 |
| Oven | -0.42000, -0.46831, -0.00000 | 0.42000, 0.38000, 1.22000 |
| FridgeV2 | -0.39000, -0.51098, -0.00000 | 0.39000, 0.39000, 1.16000 |
| Fryer | -0.46500, -0.46631, -0.00000 | 0.46500, 0.41500, 0.93500 |
| PrepCounter | -0.47750, -0.46631, -0.00000 | 0.47750, 0.42750, 1.01000 |
| SoupKettle | -0.37378, -0.34000, -0.00000 | 0.37378, 0.32000, 0.74500 |
| SinkDishRack | -0.93000, -0.46631, -0.00000 | 0.93000, 0.41500, 1.01193 |
| CoffeeBar | -0.47750, -0.46631, -0.00000 | 0.47750, 0.42750, 1.33400 |

V4 remains 253 meshes / 157,010 triangles, no additions. Independent audit compares source and fresh imports to compressed original measurements: every original name/parent/transform/vertex/polygon/normal/material/AO/UV1 preserved; nontarget UV0 unchanged; finite UVs and positive UV1 triangle areas; all nine FBXs UnitScaleFactor100.

Exact V4 exporter convention: apply_unit_scale=True, apply_scale_options=FBX_SCALE_UNITS, axis_forward=-Z, axis_up=Y, colors_type=LINEAR, bake_anim=False. Items select only original root+children; assembly excludes REVIEW_* geometry. Image links independently checked; backup-relative V2 atlas links restored before save.

## Evidence and limitations

station-finish-renders: before/after640x640 isolated fresh-item FBXs for all eight, accepted V4 camera1440x900 and844x390 room views,1200x900 kitchen diagnostic crops. Room station mesh data comes from fresh runtime-item imports at unchanged dressed placements. Both sides bind the same V4 atlas and existing lights: this isolates UV0 changes, not a palette swap. Proof-only LocalAO multiplication uses baked colours; absent legacy AO receives neutral white.

Eight full-size item review sheets plus combined station-finish-review.jpg; room/phone/kitchen comparison sheets; packed station-finish-Check.blend. Furniture/crew are illustrative source objects. Native runtime layout, HUD, guest paths, material/light conversion and Unity AFTER appearance remain Claude-owned, unverified here.

## Reproduction and integrity

From WSL: python3 Art/Models/Restaurant/Stage1V4/station-finish-run.py audit images. Uses Windows Blender5.2. Retained station-finish-baseline.json.gz stores original measurements, not replacement backups. Builder and BEFORE regeneration require authoring-time originals; temporary backups are removed only after source/visual checks, while BEFORE PNGs are retained. Old look/kitchen receipts remain historical; station-finish-final-audit.json supersedes their hashes for these changed files.

No Assets/game-code/git changes; no commit; no subagents.

# Harbour mouth / SeaV2

24 October 2026. Codex 1 (Windows app). Approved MAP-PLAN art delivery; additive files only.

220 x 160 m playable water; 25,596 triangles / 327 mesh parts. 3 anchor zones, 7 actual waterline outlines and 7 shallow outlines, 28 red-white border buoys.

Independent actual-FBX import matched triangle counts and source vertices within 12.875 micrometres. Independent polygon/clearance/routing audit passed 61 checks. All 11 current PNGs opened individually, then hash-recorded in SeaV2-visual-review.json.

| Ground | Centre X, Z (m) | Radius | Nominal depth | Pool ID |
|---|---|---|---|---|
| Quay shallows | -65.0, 27.0 | 12 m | 1.2 m | GullHarbourMouth/quay-shallows |
| Channel | 6.0, -34.0 | 12 m | 3.8 m | GullHarbourMouth/channel |
| Mouth flats | 68.0, 0.0 | 14 m | 1.4 m | GullHarbourMouth/mouth-flats |

## Model and placement

Editable source: `GullHarbourMouthSeaV2.blend`; triangulated export: `GullHarbourMouthSeaV2.fbx`. Runtime copies are `Assets/Art/Models/Environment/GullHarbourMouth/GullHarbourMouthSeaV2.fbx` and `navigation.json`, byte-identical to the reviewed art delivery. Existing GroundsV1/original assets, JSON and .meta files remain untouched.

Source axes follow ART108 `(world X, -world Z, height)`. The export retains verified X compensation. Unity model placement is world `(0,-0.32,0)`, identity rotation/scale. Do not centre or rescale the model to fit its bounds: bounds include unreachable horizon art and the continuous seabed. Boat positions are WORLD deck centres at Y=0; translation is deck anchor minus rotated HullDef.Center, independent of map root Y.

navigation.json uses world XZ metres: islands/shallows are objects with id and CCW vertices `{x,z}`, obtained by actual closed terrain-edge slices at local waterline0 / -1m. Each outline is <=64 vertices. Border is CCW; cameraBounds uses `{min:{x,z},max:{x,z}}`. All three legacy IDs/names/pool IDs/nominal depths are preserved; the new centres/zones supersede old GroundsV1 anchors.

Every whole ground circle is outside the actual shallow polygons and the islands inflated2m, and contained by the border. Harbour and 0.6m-radius buoy bases clear the 2m island inflation. Outer markers are on the border at25-30m spacing. Horizon centres are beyond the border.

All6 harbour/ground-pair static visibility routes exist for discs of radius2m and4m. At least one ground-to-ground straight line is blocked by inflated land. Route polylines are art-side audit evidence, not runtime navigation data. Shallow costs, hull turns, speed, collision recovery and10-20s timing remain code-owner checks.

## Islands and views

- **mainland-coast:** Long working coast frames Quay shallows; quay faces the open channel.
- **west-islet:** Blocks the direct Quay shallows to Channel line; west/east passage choice.
- **east-islet:** Shelters Mouth flats and defines the eastern channel entrance.

SeaV2-navigation-plate.png shows actual waterline and -1m slices, zones, all border markers, a dashed straight arrow for each ground pair, and solid verified detours around blocked lines. SeaV2-review-sheet.png pairs all3 day/night gameplay-camera renders and the wide fog/horizon day/night views. Review sample points are recorded in navigation.json artReviewAnchors; each lies inside its zone.

SeaV2-lighting-presets.json records warm daytime key/cool ambient, cool night lighting, two warm deck pools, depth water tints and smooth30m fog falloff. Night/day share one exported model. Review-only water, fog, camera, boat and lights are retained in SeaV2-Review-only.blend and excluded from the model export.

## Evidence and limits

- SeaV2-validation.json: saved source/export/navigation hashes, counts, bounds and independent actual-FBX vertex error.
- SeaV2-audit.json: polygon/zone/harbour/buoy/border/routes/protected114-file checks.
- SeaV2-visual-review.json: exact opened-image hashes and camera/sample contract.
- SeaV2-delivery.json: runtime-copy and all11 PNG hashes.

These are Blender art reviews, without native HUD, crew, runtime water, sailing or touch behaviour. Claude/code-owner must bind SeaV2 model/navigation, import new metadata, reconcile fish pools/depths, verify all5 hulls and camera clamps, tune sailing and inspect1440x900/844x390 native captures. No Unity scenes, C#, git operations, commits or player-save changes were made by this art task.

Builder: Art/Source/Art108/build_sea_v2.py; independent audit/plate/sheet: audit_sea_v2.py; manual-review handoff: finish_sea_v2.py. Old map reports/receipts remain historical GroundsV1 evidence.

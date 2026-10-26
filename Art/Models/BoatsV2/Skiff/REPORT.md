# Skiff refinement — BOAT-REFINE-1

Additive editable source and FBX; protected Assets model remains unchanged. **3,731 triangles** (current 2,494; cap 5,000). One metre per tile. Matte canonical Art/STYLE.md palette; no textures, crews, lights, cameras or presentation floor in delivered geometry.

Curved sheer and raked forefoot replace the slab sides. Exported rail end lifts relative to amidships: **18.4 cm bow / 8.0 cm stern**; the deck stays put. Five overlapping clinker courses with three upper dark 20 mm reveals and 25 mm proud laps, swept ivory gunwale, honey rubbing strake, orange painted waterline and timber keel/stem give the silhouette a built wooden character. Inner lining, end seats and three restrained flat-colour paint chips complete the timber work. Original console, motor, propeller, hold, hinged lid and sockets remain intact; a compact outboard clamp bracket and small end benches add the working details.

## Preserved mechanical contract

Independent import of original and exported FBXs: **PASS**, 12 legacy nodes retained with identical parents and local/world matrices within 0.0001 m. Matrix checks also cover rotation/scale/origin, not only pivot translation. Deck and all retained meshes compare every world-space vertex within 0.0001 m, far tighter than the brief's 1 cm limit. Source axes X right / -Y bow / Z up and importer root conversion remain unchanged. Runtime model binding, station definitions, GameData hull dimensions and RodBases were read, never edited. 5 × 3 tile grid stays in place.

| Measurement (source world metres) | Current | Refined |
| --- | --- | --- |
| Deck minimum XYZ | (-1.50000, -2.50000, -0.05000) | (-1.50000, -2.50000, -0.05000) |
| Deck maximum XYZ | (1.50000, 2.50000, 0.00000) | (1.50000, 2.50000, 0.00000) |
| Walking surface Z | 0.00000 | 0.00000 |
| Triangles | 2494 | 3731 |

| Legacy node | Old source-world pivot XYZ (m) | New source-world pivot XYZ (m) | Maximum matrix delta |
| --- | --- | --- | ---: |
| Console | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| FishHold | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| HoldLid | (0.00000, -0.50000, 0.02500) | (0.00000, -0.50000, 0.02500) | 0 |
| Hull | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| IvoryGunwale | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| OutboardMotor | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| PlankDeck | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| Propeller | (0.00000, 3.40000, -0.60000) | (0.00000, 3.40000, -0.60000) | 0 |
| RodSocket_1 | (-1.68000, 1.75000, 0.45000) | (-1.68000, 1.75000, 0.45000) | 0 |
| RodSocket_2 | (-1.68000, 0.00000, 0.45000) | (-1.68000, 0.00000, 0.45000) | 0 |
| RodSocket_3 | (-1.68000, -1.75000, 0.45000) | (-1.68000, -1.75000, 0.45000) | 0 |
| Catchline_Skiff | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |

Unchanged mesh vertices: `Console`, `FishHold`, `HoldLid`, `OutboardMotor`, `PlankDeck`, `Propeller`, `RodSocket_1`, `RodSocket_2`, `RodSocket_3`.

New child nodes: `EndBenches`, `EndSoles`, `KeelAndStem`, `OutboardBracket`, `PaintWear`, `WaterlineBand`. All remain under the original root. Added seats/soles sit outside the rectangular build deck. Open single-face paint/sole overlays are intentional; no zero-area polygons or nonfinite vertices. No baked animations.

## Opened comparison evidence

[Review sheet](renders/review-sheet.png) shows current left, refined right at identical scale, lights and material treatment. Individual labelled full-resolution pairs:

- [front-three-quarter](renders/compare-front-three-quarter.png)
- [side](renders/compare-side.png)
- [back-three-quarter](renders/compare-back-three-quarter.png)
- [top](renders/compare-top.png)
- [low-waterline](renders/compare-low-waterline.png)
- [deck-55](renders/compare-deck-55.png)
- [game-exact-45](renders/compare-game-exact-45.png)

The requested approximate 55-degree deck view is included. Read-only runtime inspection found VoyageGame camera Euler(45,35,0); an additional exact 45-degree/35-yaw authoring pair is supplied. These are Blender authoring comparisons, not Unity screenshots or evidence of native material remapping, gameplay placement, crew clearance, or player acceptance. Claude imports after review.

Post-feedback visual correction: increased rail/rubbing-strake sheer to a measured 18.4 cm bow lift and 8.0 cm stern lift relative to amidships, leaving the five-by-three deck fixed. Added three dark 20 mm vertical clinker reveals at the upper laps, projecting 25 mm. Opened refreshed side/front-quarter, low-waterline, top and exact45 authoring renders: the sweep and three seam lines read clearly, including the game-camera angle. Retained warm lining, bow/stern benches, original console/hold/lid/motor/propeller/sockets, compact outboard bracket, continuous orange paint and restrained wear. Bow bench is clearer in top/back views than in the front quarter because the raised bow rail naturally occludes it. Previous subtle sheer/blue-lap delivery was superseded following Claude's FIX; final matched evidence is regenerated from the corrected FBX. Native Unity remapping, crew/equipment clearance and player acceptance remain untested here.

## Reproduction and receipt

Windows Blender 5.2: run `Art/Source/BoatsV2/build.py -- Skiff`, then `review.py -- Skiff`; Python/Pillow `sheets.py Skiff` creates labelled pairs. `validation.json` and `build-metrics.json` contain measured results; logs reside in source directory. Zero-area bevel fragments are removed during authoring before export. Original FBX SHA256: `174076b3ca2d4eba0fa2c3d0d056a701fad04fc0f1a2c5150d48cdc4acb06d24`.

No Assets writes, Unity launches, game-code changes, git operations or subagents. Native import and in-game acceptance remain with Claude/Mo.

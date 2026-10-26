# Rowboat refinement — BOAT-REFINE-1

Additive editable source and FBX; protected Assets model remains unchanged. **2,393 triangles** (current 3,414; cap 3,000). One metre per tile. Matte canonical Art/STYLE.md palette; no textures, crews, lights, cameras or presentation floor in delivered geometry.

Curved sheer and raked forefoot replace the slab sides. Exported rail end lifts relative to amidships: **15.6 cm bow / 8.0 cm stern**; the deck stays put. Five overlapping clinker courses with three upper dark 20 mm reveals and 25 mm proud laps, swept ivory gunwale, honey rubbing strake, orange painted waterline and timber keel/stem give the silhouette a built wooden character. Inner lining, end seats and three restrained flat-colour paint chips complete the timber work. Original oars, oarlocks and rod sockets remain intact; the centre thwart retains its original contact height with simpler geometry.

## Preserved mechanical contract

Independent import of original and exported FBXs: **PASS**, 11 legacy nodes retained with identical parents and local/world matrices within 0.0001 m. Matrix checks also cover rotation/scale/origin, not only pivot translation. Deck and all retained meshes compare every world-space vertex within 0.0001 m, far tighter than the brief's 1 cm limit. Source axes X right / -Y bow / Z up and importer root conversion remain unchanged. Runtime model binding, station definitions, GameData hull dimensions and RodBases were read, never edited. 3 × 2 tile grid stays in place.

| Measurement (source world metres) | Current | Refined |
| --- | --- | --- |
| Deck minimum XYZ | (-1.00000, -1.50000, -0.05000) | (-1.00000, -1.50000, -0.05000) |
| Deck maximum XYZ | (1.00000, 1.50000, 0.00000) | (1.00000, 1.50000, 0.00000) |
| Walking surface Z | 0.00000 | 0.00000 |
| Triangles | 3414 | 2393 |

| Legacy node | Old source-world pivot XYZ (m) | New source-world pivot XYZ (m) | Maximum matrix delta |
| --- | --- | --- | ---: |
| CentreThwart | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| Hull | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| IvoryGunwale | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| Oar_Port | (-1.12000, -0.00000, 0.49000) | (-1.12000, -0.00000, 0.49000) | 0 |
| Oar_Starboard | (1.12000, -0.00000, 0.49000) | (1.12000, -0.00000, 0.49000) | 0 |
| Oarlock_Port | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| Oarlock_Starboard | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| PlankDeck | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |
| RodSocket_Port_Bow | (-1.11500, -1.00000, 0.44000) | (-1.11500, -1.00000, 0.44000) | 0 |
| RodSocket_Port_Stern | (-1.11500, 1.00000, 0.44000) | (-1.11500, 1.00000, 0.44000) | 0 |
| Catchline_Rowboat | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 0 |

Unchanged mesh vertices: `Oar_Port`, `Oar_Starboard`, `Oarlock_Port`, `Oarlock_Starboard`, `PlankDeck`, `RodSocket_Port_Bow`, `RodSocket_Port_Stern`.

New child nodes: `KeelAndStem`, `PaintWear`, `WaterlineBand`. All remain under the original root. Added seats/soles sit outside the rectangular build deck. Open single-face paint/sole overlays are intentional; no zero-area polygons or nonfinite vertices. No baked animations.

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

Post-feedback visual correction: increased rail/rubbing-strake sheer to a measured 15.6 cm bow lift and 8.0 cm stern lift relative to amidships, leaving the deck fixed. Added three dark 20 mm vertical clinker reveals at the upper laps, projecting 25 mm. Opened refreshed side, low-waterline and exact45 authoring renders: the sweep and all three seam lines read clearly, including the game-camera angle. Retained rounded plan, end seats, warm lining, continuous orange paint, original oars/oarlocks/sockets and small restrained wear. Previous subtle sheer/blue-lap delivery was superseded following Claude's FIX; final matched evidence is regenerated from the corrected FBX. Native Unity remapping, crew/equipment clearance and player acceptance remain untested here.

## Reproduction and receipt

Windows Blender 5.2: run `Art/Source/BoatsV2/build.py -- Rowboat`, then `review.py -- Rowboat`; Python/Pillow `sheets.py Rowboat` creates labelled pairs. `validation.json` and `build-metrics.json` contain measured results; logs reside in source directory. Zero-area bevel fragments are removed during authoring before export. Original FBX SHA256: `383eb68e58a725df9ce51e134f75cd030edc5f865af0a4cfb111fc2b16d605a3`.

No Assets writes, Unity launches, game-code changes, git operations or subagents. Native import and in-game acceptance remain with Claude/Mo.

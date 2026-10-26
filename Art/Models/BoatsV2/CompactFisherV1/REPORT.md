# CompactFisherV1 — BOAT-REFINE-2

Editable Blender source and independently reimported FBX. 10863 triangles; original 10164; cap 14229 (+40%). Protected Assets FBX unchanged. Native Unity acceptance is not claimed.

Two restrained overlapping navy hull courses, swept ivory cap and honey rubbing strip; continuous orange painted band built into the shell topology. Source-like broad shoulder encloses the unchanged deck; raked lower shell/keel. One bevelled canopy drip lip follows the existing roof overhang. Cabin footprint, helm, hatch opening and sorting approach are retained.

## Mechanical diff

Independent original/exported FBX import: PASS. Every legacy node name, parent and local/world matrix preserved within 0.0001m; retained meshes compare every world-space vertex at the same tolerance. New decorative meshes use identity source-world transforms; existing independent roots stay independent. Source X right / -Y forward / Z up and FBX conversion unchanged. No station/grid/origin/scale/socket edits.

| Measurement | Original | Refined |
| --- | --- | --- |
| Deck minimum XYZ | (-1.21900, -2.50000, -0.03500) | (-1.21900, -2.50000, -0.03500) |
| Deck maximum XYZ | (1.21950, 2.34000, 0.00000) | (1.21950, 2.34000, 0.00000) |
| Triangles | 10164 | 10863 |

Exported cap bow/stern rise from amidships: 22.00/10.00cm. Walking surface/deck vertices unchanged.

| Legacy node | Old pivot XYZ | New pivot XYZ | Maximum matrix delta |
| --- | --- | --- | ---: |
| Hull | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| GunwaleHardware | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| PlankDeck | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| HullPaintBand | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| HelmConsole | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| CanopyFrame | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| HelmRoof | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| BowLocker | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| HoldLid | (-0.65000, 0.35000, 0.02000) | (-0.65000, 0.35000, 0.02000) | 1.1920929e-07 |
| FishHold | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| HoldRimHinges | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| HelmFittings | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| CanopyFittings | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| OutboardMotor | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| Propeller | (-0.53000, 2.94000, -0.55000) | (-0.53000, 2.94000, -0.55000) | 3.57627869e-07 |
| RodSocket_1 | (-1.28000, -0.10000, 0.47000) | (-1.28000, -0.10000, 0.47000) | 1.1920929e-07 |
| RodVisual_1 | (-1.28000, -0.10000, 0.47000) | (-1.28000, -0.10000, 0.47000) | 1.1920929e-07 |
| RodSocket_2 | (1.28000, -0.10000, 0.47000) | (1.28000, -0.10000, 0.47000) | 1.1920929e-07 |
| RodVisual_2 | (1.28000, -0.10000, 0.47000) | (1.28000, -0.10000, 0.47000) | 1.1920929e-07 |
| RodSocket_3 | (-1.23000, 1.65000, 0.47000) | (-1.23000, 1.65000, 0.47000) | 2.08616257e-07 |
| RodVisual_3 | (-1.23000, 1.65000, 0.47000) | (-1.23000, 1.65000, 0.47000) | 2.08616257e-07 |
| SafetyFenders | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| DeckDetails | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| SternNet_Stowed | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| SternNetRoller | (0.67000, 2.65000, 0.67000) | (0.67000, 2.65000, 0.67000) | 3.57627869e-07 |
| NetDrum | (0.67000, 2.65000, 0.67000) | (0.67000, 2.65000, 0.67000) | 3.57627869e-07 |
| NetCrank | (1.12000, 2.65000, 0.67000) | (1.12000, 2.65000, 0.67000) | 3.57627869e-07 |
| NetMountFittings | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| EngineFittings | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |
| Catchline_CompactFisherV1 | (0.00000, 0.00000, 0.00000) | (0.00000, 0.00000, 0.00000) | 1.1920929e-07 |

Retained mesh vertex sets: `PlankDeck`, `HelmConsole`, `CanopyFrame`, `HelmRoof`, `BowLocker`, `HoldLid`, `FishHold`, `HoldRimHinges`, `HelmFittings`, `CanopyFittings`, `OutboardMotor`, `Propeller`, `RodSocket_1`, `RodVisual_1`, `RodSocket_2`, `RodVisual_2`, `RodSocket_3`, `RodVisual_3`, `SafetyFenders`, `DeckDetails`, `SternNet_Stowed`, `SternNetRoller`, `NetDrum`, `NetCrank`, `NetMountFittings`, `EngineFittings`.

New nodes: `CanopyDripLip`, `KeelAndRakedStem`, `SweptCapAndRubber`.

## Export bounds and unit compatibility correction

Independent FBX reimport lists every mesh below (metres, source X/Y/Z). No presentation floor, shadow catcher or mesh outside boat-sized bounds exists. The rejected export used UnitScaleFactor=1 with compensating root scale100; this delivery uses UnitScaleFactor=100, matching the original, without the added root scale. This corrects an export representation mismatch relevant to Unity useFileScale=0/useFileUnits=1. The reported harbour plane still needs native import confirmation by Claude.

Previous versus corrected export maximum world-vertex deviation: 0 m. Geometry is equivalent to the reviewed renders. Exact FBX SHA256: `15c77d5a6538b61ac47df97ddceddac5cc6784c3dcd9c57edfbf7d385726991e`. Full local bounds, matrices, parents, material names and raw FBX model properties are in [bounds-audit.json](bounds-audit.json).

| Every exported mesh | Original world min / max | Export world min / max | Largest span m |
| --- | --- | --- | ---: |
| BowLocker | (-0.62000, -2.41000, 0.00000) / (0.62000, -2.01000, 0.35000) | (-0.62000, -2.41000, 0.00000) / (0.62000, -2.01000, 0.35000) | 1.24000 |
| CanopyDripLip | new trim | (-0.91250, -1.98250, 1.37750) / (0.91250, -0.27750, 1.43250) | 1.82500 |
| CanopyFittings | (-0.89200, -1.90000, 1.16164) / (0.89200, -0.36000, 1.49500) | (-0.89200, -1.90000, 1.16164) / (0.89200, -0.36000, 1.49500) | 1.78400 |
| CanopyFrame | (-0.83500, -1.86000, 0.00000) / (0.83500, -0.35000, 1.39000) | (-0.83500, -1.86000, 0.00000) / (0.83500, -0.35000, 1.39000) | 1.67000 |
| DeckDetails | (-1.13000, -1.98000, 0.01821) / (0.87389, 2.29400, 0.45250) | (-1.13000, -1.98000, 0.01821) / (0.87389, 2.29400, 0.45250) | 4.27400 |
| EngineFittings | (-0.96840, 2.38880, -0.00500) / (-0.29000, 2.61100, 0.24500) | (-0.96840, 2.38880, -0.00500) / (-0.29000, 2.61100, 0.24500) | 0.67840 |
| FishHold | (-0.97000, 0.37000, -0.38700) / (-0.33000, 1.13000, -0.01200) | (-0.97000, 0.37000, -0.38700) / (-0.33000, 1.13000, -0.01200) | 0.76000 |
| GunwaleHardware | (-1.44480, -2.84480, 0.32050) / (1.44480, 2.64360, 0.85200) | (-1.44480, -2.84480, 0.35651) / (1.44480, 2.64360, 1.01480) | 5.48840 |
| HelmConsole | (-0.50000, -1.77500, 0.00000) / (0.26000, -1.13600, 0.76500) | (-0.50000, -1.77500, 0.00000) / (0.26000, -1.13600, 0.76500) | 0.76500 |
| HelmFittings | (-0.50500, -1.83500, 0.48000) / (0.53402, -1.16100, 1.08805) | (-0.50500, -1.83500, 0.48000) / (0.53402, -1.16100, 1.08805) | 1.03902 |
| HelmRoof | (-0.90000, -1.97000, 1.37000) / (0.90000, -0.29000, 1.92000) | (-0.90000, -1.97000, 1.37000) / (0.90000, -0.29000, 1.92000) | 1.80000 |
| HoldLid | (-0.99000, 0.35000, -0.00000) / (-0.31000, 1.15000, 0.05050) | (-0.99000, 0.35000, -0.00000) / (-0.31000, 1.15000, 0.05050) | 0.80000 |
| HoldRimHinges | (-0.98500, 0.31750, -0.01000) / (-0.31500, 1.14500, 0.05500) | (-0.98500, 0.31750, -0.01000) / (-0.31500, 1.14500, 0.05500) | 0.82750 |
| Hull | (-1.40000, -2.80000, -0.57000) / (1.40000, 2.60000, 0.53500) | (-1.42000, -2.80000, -0.57000) / (1.42000, 2.60000, 0.66500) | 5.40000 |
| HullPaintBand | (-1.38180, -2.78880, 0.17000) / (1.38180, 2.58960, 0.36500) | (-1.25067, -2.64000, -0.37715) / (1.25067, 2.45143, -0.24890) | 5.09143 |
| KeelAndRakedStem | new trim | (-0.05500, -2.86690, -0.66500) / (0.05500, 2.44400, 0.68167) | 5.31090 |
| NetCrank | (1.09000, 2.63900, 0.67000) / (1.15000, 2.86500, 0.85000) | (1.09000, 2.63900, 0.67000) / (1.15000, 2.86500, 0.85000) | 0.22600 |
| NetDrum | (0.24000, 2.53844, 0.55844) / (1.11000, 2.76156, 0.78127) | (0.24000, 2.53844, 0.55844) / (1.11000, 2.76156, 0.78127) | 0.87000 |
| NetMountFittings | (0.24500, 2.21500, 0.04000) / (1.10500, 2.42500, 0.17900) | (0.24500, 2.21500, 0.04000) / (1.10500, 2.42500, 0.17900) | 0.86000 |
| OutboardMotor | (-0.93019, 2.37602, -0.58500) / (-0.31000, 2.99500, 0.51500) | (-0.93019, 2.37602, -0.58500) / (-0.31000, 2.99500, 0.51500) | 1.10000 |
| PlankDeck | (-1.21900, -2.50000, -0.03500) / (1.21950, 2.34000, 0.00000) | (-1.21900, -2.50000, -0.03500) / (1.21950, 2.34000, 0.00000) | 4.84000 |
| Propeller | (-0.61083, 2.82000, -0.67749) / (-0.39000, 3.01000, -0.42251) | (-0.61083, 2.82000, -0.67749) / (-0.39000, 3.01000, -0.42251) | 0.25499 |
| RodSocket_1 | (-1.33600, -0.15600, 0.47000) / (-1.22400, -0.04400, 0.61000) | (-1.33600, -0.15600, 0.47000) / (-1.22400, -0.04400, 0.61000) | 0.14000 |
| RodSocket_2 | (1.22400, -0.15600, 0.47000) / (1.33600, -0.04400, 0.61000) | (1.22400, -0.15600, 0.47000) / (1.33600, -0.04400, 0.61000) | 0.14000 |
| RodSocket_3 | (-1.28600, 1.59400, 0.47000) / (-1.17400, 1.70600, 0.61000) | (-1.28600, 1.59400, 0.47000) / (-1.17400, 1.70600, 0.61000) | 0.14000 |
| RodVisual_1 | (-1.82552, -0.42648, 0.46237) / (-1.18000, -0.06500, 1.67427) | (-1.82552, -0.42648, 0.46237) / (-1.18000, -0.06500, 1.67427) | 1.21190 |
| RodVisual_2 | (1.18000, -0.42648, 0.46237) / (1.82552, -0.06500, 1.67427) | (1.18000, -0.42648, 0.46237) / (1.82552, -0.06500, 1.67427) | 1.21190 |
| RodVisual_3 | (-1.77552, 1.32352, 0.46236) / (-1.13000, 1.68500, 1.67427) | (-1.77552, 1.32352, 0.46236) / (-1.13000, 1.68500, 1.67427) | 1.21190 |
| SafetyFenders | (-1.50500, -1.02133, -0.12000) / (1.50500, 1.17133, 0.49330) | (-1.50500, -1.02133, -0.12000) / (1.50500, 1.17133, 0.49330) | 3.01000 |
| SternNetRoller | (0.24000, 2.18000, -0.00000) / (1.11000, 2.65381, 0.67376) | (0.24000, 2.18000, -0.00000) / (1.11000, 2.65381, 0.67376) | 0.87000 |
| SternNet_Stowed | (0.29410, 2.67730, -0.24856) / (1.04590, 2.95384, 0.65856) | (0.29410, 2.67730, -0.24856) / (1.04590, 2.95384, 0.65856) | 0.90712 |
| SweptCapAndRubber | new trim | (-1.47000, -2.81400, 0.36000) / (1.47000, 2.61300, 0.73200) | 5.42700 |

## Visual evidence

[Opened seven-pair sheet](renders/review-sheet.png): identical union framing, shaders, warm/cool studio lighting and cameras. Current left, refined right. Authoring images, not runtime screenshots.

- [front-three-quarter](renders/compare-front-three-quarter.png)
- [side](renders/compare-side.png)
- [back-three-quarter](renders/compare-back-three-quarter.png)
- [top](renders/compare-top.png)
- [low-waterline](renders/compare-low-waterline.png)
- [deck-55](renders/compare-deck-55.png)
- [game-exact-45](renders/compare-game-exact-45.png)

Personally opened final seven-pair sheet, full side, front three-quarter and exact45 comparison. Two quiet raised dark laps, swept ivory perimeter and honey rubbing strip read together; canopy drip edge follows its existing roof. Corrected lower shoulder encloses original plank tips without visible timber breakthrough. Continuous orange boot-top. Deck/hatch/helm/lane and rod/net hardware remain visible in their original positions. Taller swept perimeter changes the lining silhouette; no extra deck props introduced. Authoring review only; native runtime/crew/material acceptance remains with Claude/Mo.


## Materials and reproduction

Only existing M_* palette names, including M_ClinkerRecess=#0E2C40 already present in ArtLibrary.PaletteHex; no new palette entry required. All matte. No textures/crew/review cameras/floor/lights exported. Source SHA256 `dbe3474208ef7c3c83cfd4792d8dee3db9d5c361536fe4a4179c44945d756822`.

Windows Blender5.2: `build2.py -- CompactFisherV1`, `review2.py -- CompactFisherV1`; Python `sheets.py CompactFisherV1` and `report2.py CompactFisherV1`. Sources/logs in Art/Source/BoatsV2. `validation.json` is the independent audit; receipt.json hashes the delivered files.

No git/commit/Unity/Assets/game-code/save/watchdog changes or subagents. Claude owns material remapping/import/runtime/player review.

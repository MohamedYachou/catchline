# Catchline / DayBoatKit

10 editable Blender sources, binary FBX exports and orthographic game-angle previews. Runtime groups are under `Assets/Art/Models/`; sources and previews stay in this batch directory. No existing asset is overwritten. No Unity, Scripts or Scenes edits. New material names: **none** (NPCs reuse the Task06 hair palette).

Build with Windows Blender5.2 and `Art/Source/build_day_boat.py`; optional arguments after `--` select assets. Run `validate_world_batches.py -- DayBoatKit` in Blender; create review sheets with Python/Pillow `world_contact_sheets.py DayBoatKit`. Validation checks source topology, materials, roots, finite bounds and zero-area faces; reimports every FBX and compares part names, pivots and bounds. Open surfaces are recorded in validation.json and intentional where noted.

DayBoat deck is exactly X[-2.5,+2.5],Unity Z[-5,+5],Y=0:50tiles total. Wheelhouse body is X[-1.5,+1.5],Z[+3,+5],height1.65m:columns1/2/3,rows8/9,6tiles inside the deck,44 remaining. Bow +Z; hull12x5.8m. Door faces aft. Roof overhang is separate from the authoritative body footprint. Port stern-quarter hauler gap is Unity Z[-4,-2.5]. Six named rod sockets expose attachment pivots. Mast/radar are static details. Station footprint/access/parts table is in `Stations/REPORT.md`. No baked station animation; consumer drives named moving parts. FishHold extends below deck and requires an actual opening in the boat deck at placement. The boat is supplied empty for free equipment layout.

Source coordinates X right,-Y forward,Z up. FBX converts to Unity X right,+Y up,+Z forward. Root is ground/deck/waterline centre unless explicitly documented. Part pivot table below uses **Unity local metres** `(x,z,-y)` converted from source offsets. Part rotations zero/scales one; animate each part relative to its listed pivot. Materials are original canonical M_* flat colours,no external textures or embedded preview lights. Texture pack has a separate TEXTURES.md.

| Asset | Group | Width x depth x height m | Triangles |
| --- | --- | --- | ---: |
| [DayBoat](Boats/DayBoat.blend) | Boats | 5.800 x 12.000 x 3.950 | 3258 |
| [NetDrum](Stations/NetDrum.blend) | Stations | 1.850 x 0.850 x 1.060 | 492 |
| [PowerHauler](Stations/PowerHauler.blend) | Stations | 0.750 x 0.865 x 1.400 | 328 |
| [Conveyor_Straight](Stations/Conveyor_Straight.blend) | Stations | 0.900 x 0.900 x 0.532 | 576 |
| [Conveyor_Corner](Stations/Conveyor_Corner.blend) | Stations | 0.900 x 0.900 x 0.527 | 256 |
| [SortingChute](Stations/SortingChute.blend) | Stations | 1.850 x 0.890 x 0.730 | 332 |
| [FishHold](Stations/FishHold.blend) | Stations | 1.940 x 1.940 x 0.812 | 320 |
| [IceMachine](Stations/IceMachine.blend) | Stations | 0.780 x 0.840 x 1.160 | 320 |
| [GuttingTable](Stations/GuttingTable.blend) | Stations | 1.850 x 0.830 x 0.680 | 332 |
| [Crane](Stations/Crane.blend) | Stations | 0.720 x 0.744 x 1.678 | 208 |

## Parts and pivots

### DayBoat

- `Hull`: (0.0000, 0.0000, 0.0000)
- `WaterlineStripe`: (0.0000, 0.0000, 0.0000)
- `PlankDeck`: (0.0000, 0.0000, 0.0000)
- `WheelhouseBody`: (0.0000, 0.0000, 0.0000)
- `RoofWindowsDoorMastRadar`: (0.0000, 0.0000, 0.0000)
- `Rails`: (0.0000, 0.0000, 0.0000)
- `RodSocket_1`: (-2.7500, 0.5800, -1.7500)
- `RodSocket_2`: (-2.7500, 0.5800, 0.0000)
- `RodSocket_3`: (-2.7500, 0.5800, 2.0000)
- `RodSocket_4`: (2.7500, 0.5800, -3.5000)
- `RodSocket_5`: (2.7500, 0.5800, 0.0000)
- `RodSocket_6`: (2.7500, 0.5800, 2.0000)

Exact deck X[-2.5,2.5],sourceY[-5,5],topZ=0;UnityZ[-5,5]. Cabin X[-1.5,1.5],UnityZ[3,5],3acrossx2fore-aft,rows8/9 columns1/2/3. Port hauler gap UnityZ[-4,-2.5]. 6 sockets are rigid attachment origins. Radar/mast static.

### NetDrum

- `Frame`: (0.0000, 0.0000, 0.0000)
- `Drum`: (0.0000, 0.6900, 0.0000)

### PowerHauler

- `Frame`: (0.0000, 0.0000, 0.0000)
- `Sheave`: (0.0000, 1.1600, 0.2500)

### Conveyor_Straight

- `Frame`: (0.0000, 0.0000, 0.0000)
- `Belt`: (0.0000, 0.5000, 0.0000)

UV-less ridged Belt. Recycle/translate Straight ridges or rotate Corner Belt about centre path in consumer; no texture scrolling baked.

### Conveyor_Corner

- `Frame`: (0.0000, 0.0000, 0.0000)
- `Belt`: (-0.4000, 0.5000, 0.4000)

UV-less ridged Belt. Recycle/translate Straight ridges or rotate Corner Belt about centre path in consumer; no texture scrolling baked.

### SortingChute

- `SortingChute`: (0.0000, 0.0000, 0.0000)

### FishHold

- `HoldWell`: (0.0000, 0.0000, 0.0000)
- `HatchLid`: (0.0000, 0.0750, -0.9100)

2x2 footprint, inset below-deck well. Deck must provide a matching opening. HatchLid sourceX hinge at(0,.91,.075).

### IceMachine

- `IceMachine`: (0.0000, 0.0000, 0.0000)

### GuttingTable

- `GuttingTable`: (0.0000, 0.0000, 0.0000)

### Crane

- `Pedestal`: (0.0000, 0.0000, 0.0000)
- `Boom`: (0.0000, 0.9200, 0.0000)

Compact stored Boom inside1x1 footprint; localX hinge. Operational sweep/rope placement require collision handling.

Rendered contact sheets and individual previews were inspected. Validation files document mechanical checks; runtime placement, material remapping and animation integration remain for the game branch.

# Catchline / WorldPolish

31 editable Blender sources, binary FBX exports and orthographic game-angle previews. Runtime groups are under `Assets/Art/Models/`; sources and previews stay in this batch directory. No existing asset is overwritten. No Unity, Scripts or Scenes edits. New material names: **none** (NPCs reuse the Task06 hair palette).

Build with Windows Blender5.2 and `Art/Source/build_world_polish.py`; optional arguments after `--` select assets. Run `validate_world_batches.py -- WorldPolish` in Blender; create review sheets with Python/Pillow `world_contact_sheets.py WorldPolish`. Validation checks source topology, materials, roots, finite bounds and zero-area faces; reimports every FBX and compares part names, pivots and bounds. Open surfaces are recorded in validation.json and intentional where noted.

The31 assets cover9 upgrade props,11 harbour modules,3 static crew poses and8 sea modules. BigCooler/BigIceBox are exactly1.0x0.6x0.5m and share body geometry,with HingedLid. Rod variants preserve FishingRod part names/proportions/pivots. Boat repaints preserve their full original part/pivot sets. Outboard_Small root is its transom clamp,not an underside prop root; Propeller remains separate. The40m stepped backdrop repeats along X and belongs behind the shop row. Shed shell is8x6m plus its forward slipway. NPCs are static evaluated Task06 rig poses,not new skeletons; NPC_Sitting adapts Row with horizontal thighs/vertical shins. For Bench, place its root at Unity offset(0,0.2235,+0.15) from the bench root: local outfit seat contact0.239m meets seat top0.4625m; short legs dangle. NPC_Sitting-on-Bench.png is a source-only mounting review; no bench is included in the NPC FBX. WhaleTail has a separate Tail mesh with waterline/base pivot for consumer-driven rising/sinking; no animation clips are claimed. Buoy red/green topmark geometry communicates the type in addition to colour. KelpForest is exactly4x4m and planar; use a two-sided material. Shore/water modules deliberately extend below their waterline roots.

Source coordinates X right,-Y forward,Z up. FBX converts to Unity X right,+Y up,+Z forward. Root is ground/deck/waterline centre unless explicitly documented. Part pivot table below uses **Unity local metres** `(x,z,-y)` converted from source offsets. Part rotations zero/scales one; animate each part relative to its listed pivot. Materials are original canonical M_* flat colours,no external textures or embedded preview lights. Texture pack has a separate TEXTURES.md.

| Asset | Group | Width x depth x height m | Triangles |
| --- | --- | --- | ---: |
| [BigCooler](DeckProps/BigCooler.blend) | DeckProps | 1.000 x 0.600 x 0.500 | 556 |
| [BigIceBox](DeckProps/BigIceBox.blend) | DeckProps | 1.000 x 0.600 x 0.500 | 652 |
| [RodHolderClamp](DeckProps/RodHolderClamp.blend) | DeckProps | 0.210 x 0.135 x 0.300 | 196 |
| [FishingRod_Fibreglass](DeckProps/FishingRod_Fibreglass.blend) | DeckProps | 0.179 x 0.134 x 1.600 | 1488 |
| [FishingRod_Carbon](DeckProps/FishingRod_Carbon.blend) | DeckProps | 0.179 x 0.134 x 1.600 | 1488 |
| [Outboard_Small](Boats/Outboard_Small.blend) | Boats | 0.561 x 0.735 x 1.358 | 400 |
| [FuelCan](DeckProps/FuelCan.blend) | DeckProps | 0.280 x 0.192 x 0.470 | 196 |
| [SquidTub](DeckProps/SquidTub.blend) | DeckProps | 0.330 x 0.330 x 0.184 | 728 |
| [WormTub](DeckProps/WormTub.blend) | DeckProps | 0.330 x 0.330 x 0.169 | 432 |
| [HillBackdrop](Harbour/HillBackdrop.blend) | Harbour | 40.000 x 9.000 x 9.000 | 3726 |
| [Shed_Shipyard](Harbour/Shed_Shipyard.blend) | Harbour | 8.428 x 8.204 x 6.052 | 802 |
| [MarketStall](Harbour/MarketStall.blend) | Harbour | 2.400 x 1.640 x 2.290 | 3988 |
| [Rowboat_VariantRed](Harbour/Rowboat_VariantRed.blend) | Harbour | 4.520 x 4.285 x 1.020 | 1790 |
| [Rowboat_VariantGreen](Harbour/Rowboat_VariantGreen.blend) | Harbour | 4.520 x 4.285 x 1.020 | 1790 |
| [Skiff_VariantBlue](Harbour/Skiff_VariantBlue.blend) | Harbour | 3.587 x 7.036 x 1.483 | 2494 |
| [Gangway](Harbour/Gangway.blend) | Harbour | 1.055 x 3.230 x 0.877 | 624 |
| [Ladder](Harbour/Ladder.blend) | Harbour | 0.556 x 0.170 x 1.717 | 184 |
| [LifebuoyStand](Harbour/LifebuoyStand.blend) | Harbour | 0.680 x 0.400 x 1.200 | 360 |
| [CrabPotStack](Harbour/CrabPotStack.blend) | Harbour | 1.370 x 0.590 x 0.720 | 3192 |
| [Bench](Harbour/Bench.blend) | Harbour | 1.500 x 0.547 x 1.000 | 292 |
| [NPC_Fishmonger](Harbour/NPC_Fishmonger.blend) | Harbour | 0.474 x 0.451 x 1.010 | 12860 |
| [NPC_HarbourMaster](Harbour/NPC_HarbourMaster.blend) | Harbour | 0.472 x 0.416 x 1.020 | 14020 |
| [NPC_Sitting](Harbour/NPC_Sitting.blend) | Harbour | 0.678 x 0.428 x 0.945 | 17816 |
| [RockArch](Sea/RockArch.blend) | Sea | 4.952 x 1.221 x 3.280 | 360 |
| [WreckMast](Sea/WreckMast.blend) | Sea | 2.765 x 0.150 x 3.229 | 84 |
| [KelpForest](Sea/KelpForest.blend) | Sea | 4.000 x 4.000 x 0.000 | 168 |
| [SandBank_Large](Sea/SandBank_Large.blend) | Sea | 6.400 x 3.000 x 0.115 | 40 |
| [BirdIsland](Sea/BirdIsland.blend) | Sea | 2.300 x 1.522 x 1.050 | 712 |
| [MarkerBuoy_Green](Sea/MarkerBuoy_Green.blend) | Sea | 0.564 x 0.564 x 1.360 | 246 |
| [MarkerBuoy_Red](Sea/MarkerBuoy_Red.blend) | Sea | 0.564 x 0.564 x 1.280 | 276 |
| [WhaleTail](Sea/WhaleTail.blend) | Sea | 2.900 x 0.553 x 1.170 | 236 |

## Parts and pivots

### BigCooler

- `CoolerBody`: (0.0000, 0.0000, -0.0000)
- `HingedLid`: (0.0000, 0.4444, -0.3000)

Lid origin at rear hinge (0,+0.25,+0.40); local X rotation opens front edge. IceBox shares CoolerBody geometry.

### BigIceBox

- `CoolerBody`: (0.0000, 0.0000, -0.0000)
- `HingedLid`: (0.0000, 0.4444, -0.3000)

Lid origin at rear hinge (0,+0.25,+0.40); local X rotation opens front edge. IceBox shares CoolerBody geometry.

### RodHolderClamp

- `RodHolderClamp`: (0.0000, 0.0000, 0.0000)

### FishingRod_Fibreglass

- `RodAndReel`: (0.0000, 0.0000, 0.0000)
- `ReelHandle`: (0.1070, 0.2400, 0.0000)

1.6m upright rod, 48mm blank butt / 62mm cork grip / 14mm tip; intentionally exaggerated for game zoom. ReelHandle pivot (.107,0,.24), local X spin.

### FishingRod_Carbon

- `RodAndReel`: (0.0000, 0.0000, 0.0000)
- `ReelHandle`: (0.1070, 0.2400, 0.0000)

1.6m upright rod, 48mm blank butt / 62mm cork grip / 14mm tip; intentionally exaggerated for game zoom. ReelHandle pivot (.107,0,.24), local X spin.

### Outboard_Small

- `OutboardMotor`: (0.0000, -0.3500, 3.0500)
- `Propeller`: (0.0000, -0.9500, -0.3500)

Root at transom clamp; source propeller pivot (0,.35,-.95), Unity(0,-.95,-.35). Spins source Y / Unity Z.

### FuelCan

- `FuelCan`: (0.0000, 0.0000, 0.0000)

### SquidTub

- `SquidTub`: (0.0000, 0.0000, 0.0000)

### WormTub

- `WormTub`: (0.0000, 0.0000, 0.0000)

### HillBackdrop

- `SteppedHills`: (0.0000, 0.0000, 0.0000)
- `HillHouses`: (0.0000, 0.0000, 0.0000)
- `ChurchTower`: (0.0000, 0.0000, 0.0000)
- `TreesFencesSteps`: (0.0000, 0.0000, 0.0000)

40m X repeat, end cross-sections match. Place behind shops; includes separate landscape,houses,tower,dressing.

### Shed_Shipyard

- `ShedShell`: (0.0000, 0.0000, 0.0000)
- `Slipway`: (0.0000, 0.0000, 0.0000)

8x6m shed shell; open water-facing entrance. Slipway extends2.2m in front, below ground.

### MarketStall

- `MarketStallAwning`: (0.0000, 0.0000, 0.0000)
- `ScaleAndIce`: (0.0000, 0.0000, 0.0000)

### Rowboat_VariantRed

- `Hull`: (0.0000, 0.0000, 0.0000)
- `PlankDeck`: (0.0000, 0.0000, 0.0000)
- `IvoryGunwale`: (0.0000, 0.0000, 0.0000)
- `CentreThwart`: (0.0000, 0.0000, 0.0000)
- `Oarlock_Port`: (0.0000, 0.0000, 0.0000)
- `Oar_Port`: (-1.1200, 0.4900, 0.0000)
- `Oarlock_Starboard`: (0.0000, 0.0000, 0.0000)
- `Oar_Starboard`: (1.1200, 0.4900, 0.0000)
- `RodSocket_Port_Stern`: (-1.1150, 0.4400, -1.0000)
- `RodSocket_Port_Bow`: (-1.1150, 0.4400, 1.0000)

Deck 2 m across x 3 m fore-aft, top at Z=0. Hull length4.2m/beam2.4m; oars extend beyond hull. Sockets measured from build-deck stern Y=+1.5.

### Rowboat_VariantGreen

- `Hull`: (0.0000, 0.0000, 0.0000)
- `PlankDeck`: (0.0000, 0.0000, 0.0000)
- `IvoryGunwale`: (0.0000, 0.0000, 0.0000)
- `CentreThwart`: (0.0000, 0.0000, 0.0000)
- `Oarlock_Port`: (0.0000, 0.0000, 0.0000)
- `Oar_Port`: (-1.1200, 0.4900, 0.0000)
- `Oarlock_Starboard`: (0.0000, 0.0000, 0.0000)
- `Oar_Starboard`: (1.1200, 0.4900, 0.0000)
- `RodSocket_Port_Stern`: (-1.1150, 0.4400, -1.0000)
- `RodSocket_Port_Bow`: (-1.1150, 0.4400, 1.0000)

Deck 2 m across x 3 m fore-aft, top at Z=0. Hull length4.2m/beam2.4m; oars extend beyond hull. Sockets measured from build-deck stern Y=+1.5.

### Skiff_VariantBlue

- `Hull`: (0.0000, 0.0000, 0.0000)
- `PlankDeck`: (0.0000, 0.0000, 0.0000)
- `IvoryGunwale`: (0.0000, 0.0000, 0.0000)
- `OutboardMotor`: (0.0000, 0.0000, 0.0000)
- `Propeller`: (0.0000, -0.6000, -3.4000)
- `Console`: (0.0000, 0.0000, 0.0000)
- `RodSocket_1`: (-1.6800, 0.4500, -1.7500)
- `RodSocket_2`: (-1.6800, 0.4500, 0.0000)
- `RodSocket_3`: (-1.6800, 0.4500, 1.7500)
- `FishHold`: (0.0000, 0.0000, 0.0000)
- `HoldLid`: (0.0000, 0.0250, 0.5000)

Hull 6.5m fore-aft x3.5m beam (motor excluded), pointed bow, flat transom. Deck 5x3m at Z=0, with genuine hold opening. Console tile c=2,r=0, Unity centre(1,0,-2). HoldLid pivot Unity(0,.025,.5), open with negative local-X rotation. Port sockets Unity(-1.68,.45,-1.75/0/+1.75). Propeller pivot Unity(0,-.60,-3.40), spins local Z. No standalone FishHold FBX needed.

### Gangway

- `Gangway`: (0.0000, 0.0000, 0.0000)

### Ladder

- `Ladder`: (0.0000, 0.0000, 0.0000)

### LifebuoyStand

- `Lifebuoy`: (0.0000, 0.0000, 0.0000)
- `LifebuoyStand`: (0.0000, 0.0000, 0.0000)

### CrabPotStack

- `CrabPotStack`: (0.0000, 0.0000, 0.0000)

### Bench

- `Bench`: (0.0000, 0.0000, 0.0000)

### NPC_Fishmonger

- `NPC_Fishmonger_Body`: (0.0000, 0.0000, 0.0000)
- `NPC_Fishmonger_Outfit_Fisherman`: (0.0000, 0.0000, 0.0000)
- `NPC_Fishmonger_Hat_Hood`: (0.0000, 0.0000, 0.0000)

Static evaluated Task06 mesh pose; no runtime armature/actions. Sitting root remains original floor reference; place seat beneath hips.

### NPC_HarbourMaster

- `NPC_HarbourMaster_Body`: (0.0000, 0.0000, 0.0000)
- `NPC_HarbourMaster_Outfit_Captain`: (0.0000, 0.0000, 0.0000)
- `NPC_HarbourMaster_Hat_CaptainCap`: (0.0000, 0.0000, 0.0000)

Static evaluated Task06 mesh pose; no runtime armature/actions. Sitting root remains original floor reference; place seat beneath hips.

### NPC_Sitting

- `NPC_Sitting_Body`: (0.0000, 0.0000, 0.0000)
- `NPC_Sitting_Outfit_Veteran`: (0.0000, 0.0000, 0.0000)
- `NPC_Sitting_Hat_Beanie`: (0.0000, 0.0000, 0.0000)

Static evaluated Task06 rig pose; no runtime armature/actions. NPC_Sitting adapts Row with horizontal thighs and vertical shins. Bare local outfit seat contact Z=.239; Bench seat top Z=.4625. Place NPC at Unity offset(0,.2235,+.15) relative to Bench root; short legs dangle. Crew source unchanged.

### RockArch

- `RockArch`: (0.0000, 0.0000, 0.0000)

### WreckMast

- `WreckMast`: (0.0000, 0.0000, 0.0000)

### KelpForest

- `FloatingKelp`: (0.0000, 0.0000, 0.0000)

Exactly flat at waterline Z=0: drift-aligned overlapping leaf silhouettes and four inset flattened bulbs. Planar union avoids z-fighting; no reverse faces. Regenerate JSON with build_kelp_mat.py (Shapely2.1+). Exactly4x4m planar at waterline; two-sided palette material recommended.

### SandBank_Large

- `SandBank_Large`: (0.0000, 0.0000, 0.0000)

### BirdIsland

- `IslandRock`: (0.0000, 0.0000, 0.0000)
- `SeagullBody`: (0.0000, 0.0000, 0.0000)
- `Wing_L`: (-0.0700, 0.2200, 0.0250)
- `Wing_R`: (0.0700, 0.2200, 0.0250)

Perched seagull 0.4m nose-to-tail; Wing_L/Wing_R shoulder pivots for flap.

### MarkerBuoy_Green

- `MarkerBuoy_Green`: (0.0000, 0.0000, 0.0000)

Waterline root, red cylindrical/green conical topmarks; region navigation rules set by game.

### MarkerBuoy_Red

- `MarkerBuoy_Red`: (0.0000, 0.0000, 0.0000)

Waterline root, red cylindrical/green conical topmarks; region navigation rules set by game.

### WhaleTail

- `Tail`: (0.0000, 0.0000, 0.0000)

Tail pivot at waterline base. Consumer raises/lowers whole Tail mesh for rare event; no baked clip.

Rendered contact sheets and individual previews were inspected. Validation files document mechanical checks; runtime placement, material remapping and animation integration remain for the game branch.

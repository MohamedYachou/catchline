# Task 07: upgrade visuals and world polish

Purchases should show on the boat, and Gull Harbour should feel lived in. Same pipeline rules: Blender sources, FBX, previews, REPORT, palette `M_*` only. No Unity, no Scripts or Scenes. Push after each part.

## Part A: upgrade visuals (`DeckProps/` unless noted)
- `BigCooler`: same style as Cooler, 1.0x0.6x0.5 m, with a separate `HingedLid`.
- `BigIceBox`: the ice-box version of BigCooler, with a separate `HingedLid`.
- `RodHolderClamp`: a small clamp on the gunwale socket that holds the second rod upright.
- `FishingRod_Fibreglass` and `FishingRod_Carbon`: same proportions, pivot and part names as FishingRod. Fibreglass is white and orange, carbon is dark with gold.
- `Outboard_Small` (`Boats/`): for the skiff, with a separate `Propeller` and a pivot at the transom clamp.
- `FuelCan`, `SquidTub`, `WormTub`.

## Part B: harbour polish (`Harbour/`)
- `HillBackdrop`: a 40 m wide modular backdrop behind the shops:
  - stepped hills with small houses
  - a church tower, trees, fences and steps
  - low detail, readable silhouette from the game camera
- `Shed_Shipyard`: a big boat shed with a slipway, where hull refits happen, about 8x6 m.
- `MarketStall`: an awning, a fish display on ice, a scale.
- Moored boats: `Rowboat_VariantRed` and `Rowboat_VariantGreen` (repaints with the same part names), and `Skiff_VariantBlue`.
- `Gangway`, `Ladder`, `LifebuoyStand`, `CrabPotStack` (it hints at Crab Coast), `Bench`.
- Static NPC poses using the Task 06 rig: `NPC_Fishmonger`, `NPC_HarbourMaster`, `NPC_Sitting`.

## Part C: sea polish (`Sea/`)
- `RockArch` (Rocky point landmark), `WreckMast` (a sunken mast sticking out, Deep channel), `KelpForest` (a larger kelp mat, 4x4 m), `SandBank_Large`, `BirdIsland` (small rock with gulls, Sandbar), `MarkerBuoy_Green`, `MarkerBuoy_Red`.
- `WhaleTail`, a rare visual event in Deep channel: a tail rising and sinking, with a separate `Tail` part.

# Task 08: day boat kit (hull 3) and water textures

Same pipeline rules: Blender sources, FBX, previews, REPORT, palette `M_*` only. No Unity, no Scripts or Scenes. Push after each part.

## Part A: day boat (STYLE.md hull 3)
- `DayBoat` (`Boats/`):
  - 10x5 tile deck, deck centred on the origin at Y=0, bow +Z.
  - Wheelhouse **centred, 3 tiles across x 2 fore-aft on the two bow-most rows**, as corrected in 07a1432. Windows, a door aft, a mast with a radar.
  - Rails with a gap on the port side at the stern quarter for the hauler.
  - Six rod sockets `RodSocket_1..6`.
- Stations (`Stations/`), each on a 1 m grid, origin at the footprint centre on the deck:
  - `NetDrum` 2x1 (separate `Drum`)
  - `PowerHauler` 1x1 (separate `Sheave`)
  - `Conveyor_Straight` 1x1 and `Conveyor_Corner` 1x1 (separate `Belt` for UV-less scrolling: model ridges)
  - `SortingChute` 2x1
  - `FishHold` 2x2 hatch (separate `HatchLid`)
  - `IceMachine` 1x1
  - `GuttingTable` 2x1
  - `Crane` 1x1 (separate `Boom`)
- `Stations/REPORT` table: footprint, access side, part names.

## Part B: textures (`Assets/Art/Textures/`)
- `water-tile.png` (1024, tileable): stylised top-down water in the sea teal palette with soft lighter caustic shapes and a few foam streaks. Subtle, not noisy.
- `water-tile-shallow.png` and `water-tile-deep.png`: the same for the Sandbar (lighter, sand showing) and the Deep channel (darker).
- `foam-ring.png`, `wake-trail.png` and `splash-sheet.png` (4x4 flipbook), all transparent.
- `deck-planks-detail.png`: an optional overlay for the plank deck, subtle grain.
- Document them in `Assets/Art/Textures/TEXTURES.md`.

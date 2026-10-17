# Catchline

Top-down automation game about a fishing boat that grows from a rowboat into a factory ship, crewed by little people you hire, assign and eventually replace with machines.

- Engine: Unity 6000.3.25f1 (URP, cross-platform template)
- Platforms: mobile + PC, landscape
- Large binaries (models, textures, audio) go through Git LFS, see `.gitattributes`

## Build 1: rowboat voyage (current)

Design: [docs/GAMEPLAY.md](docs/GAMEPLAY.md). Menu **Catchline > Play Voyage** (Ctrl+Shift+P) opens `Assets/Scenes/Voyage.unity` and presses Play. Code lives in `Assets/Scripts/Game/`.

Current priority: finish the small playable slice visually before growing
content. [PRODUCT.md](PRODUCT.md) and [DESIGN.md](DESIGN.md) hold the confirmed
direction; [POLISH-002](docs/POLISH-002.md) records the menu, HUD, water and
actual runtime capture workflow. Goal renders remain the visual target.

In the harbour, tap a building (Fish Market, Harbour Master, Crew Office, Chandlery, Supplies) to open its shop; progress saves there. Models and the UI kit come from Codex (`Assets/Art`, branch art/style-pass) through `Assets/Resources/ArtLibrary.asset` (Catchline > Rebuild Art Library).

Controls at sea: one tap per action. Tap the Fish bubble above a rod (the captain baits and casts), tap anywhere once when the bobber goes under (or Space), tap Carry above a landed fish. H heads home, scroll zooms.

First trip: aim for three fish safely stowed, then return or keep filling the
cooler. The first three catches have quicker bites and a 1.5-second strike
window. Catch portraits show weight and estimated value; the Market points
to your next upgrade. The 60-coin big cooler is the first storage milestone.

First-voyage checks, including skiff/crew/net/save regressions:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File docs/tools/check.ps1 -Name first-voyage -Method Catchline.EditorTools.FirstVoyageChecks.Regression
```

Build a Windows preview on the scratch project with the same command and
`-Method Catchline.EditorTools.FirstVoyageChecks.BuildPreview`. The result is
`Catchline-sim/Builds/FirstVoyage/Catchline.exe`. This preview starts fresh and
never loads, writes or deletes the main game's save. It intentionally does
not persist preview progress between sessions.

Build 2 is playable: return with 16 fish, then buy the 1,500-coin skiff refit at the Chandlery. It adds a 40-fish hold, three rods, an outboard and a gill net. Hire fishermen to work rods and deckhands to carry fish; up to three hired crew fit aboard. Tap Set net, fish during its soak, then Haul net. Supplies sells fuel; return fuel is included at departure. See [the continuation report](docs/CONTINUATION.md).

Balance check (a bot plays N voyages and logs each one, then renders a PNG to `Logs/`):

```
powershell -File docs/tools/check.ps1 -Name balance -Voyages 30
```

This runs Unity on the separate `Catchline-sim` scratch project. Do not batchmode the main project while its editor is open.

## Deck prototype (old)

Open `Assets/Scenes/DeckPrototype.unity` and press Play. Everything is built from primitives at startup by `Assets/Scripts/Prototype/DeckPrototype.cs`.

Crab pots flow hauler → sorting table → banding bench → live tank, with empty pots going to the pot rack and back into the water. Tap a person to select them, tap a station to give them that job, tap the bare deck to make them a free deckhand. Sell the catch when the tank fills; hire more crew with the money.

Headless check (simulates and renders a PNG to `Logs/`):

```
Unity -batchmode -quit -projectPath . -executeMethod Catchline.EditorTools.PrototypeTools.Snapshot -simSeconds 180 [-fullCrew yes]
```

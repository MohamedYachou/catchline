# Catchline

Top-down automation game about a fishing boat that grows from a rowboat into a factory ship, crewed by little people you hire, assign and eventually replace with machines.

- Engine: Unity 6000.3.25f1 (URP, cross-platform template)
- Platforms: mobile + PC, landscape
- Large binaries (models, textures, audio) go through Git LFS, see `.gitattributes`

## Build 1: rowboat voyage (current)

Design: [docs/GAMEPLAY.md](docs/GAMEPLAY.md). Menu **Catchline > Play Voyage** (Ctrl+Shift+P) opens `Assets/Scenes/Voyage.unity` and presses Play. Code lives in `Assets/Scripts/Game/`.

In the harbour, tap a building (Fish Market, Harbour Master, Crew Office, Chandlery, Supplies) to open its shop; progress saves there. Models and the UI kit come from Codex (`Assets/Art`, branch art/style-pass) through `Assets/Resources/ArtLibrary.asset` (Catchline > Rebuild Art Library).

Controls at sea: one tap per action. Tap the Fish bubble above a rod (the captain baits and casts), tap anywhere once when the bobber goes under (or Space), tap Carry above a landed fish. H heads home, scroll zooms.

Balance check (a bot plays N voyages and logs each one, then renders a PNG to `Logs/`):

```
Unity -batchmode -quit -projectPath . -executeMethod Catchline.EditorTools.PrototypeTools.VoyageSim -voyages 30
```

## Deck prototype (old)

Open `Assets/Scenes/DeckPrototype.unity` and press Play. Everything is built from primitives at startup by `Assets/Scripts/Prototype/DeckPrototype.cs`.

Crab pots flow hauler → sorting table → banding bench → live tank, with empty pots going to the pot rack and back into the water. Tap a person to select them, tap a station to give them that job, tap the bare deck to make them a free deckhand. Sell the catch when the tank fills; hire more crew with the money.

Headless check (simulates and renders a PNG to `Logs/`):

```
Unity -batchmode -quit -projectPath . -executeMethod Catchline.EditorTools.PrototypeTools.Snapshot -simSeconds 180 [-fullCrew yes]
```
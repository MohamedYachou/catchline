# Catchline

Top-down automation game about a fishing boat that grows from a rowboat into a factory ship, crewed by little people you hire, assign and eventually replace with machines.

- Engine: Unity 6000.3.25f1 (URP, cross-platform template)
- Platforms: mobile + PC, landscape
- Large binaries (models, textures, audio) go through Git LFS, see `.gitattributes`

## Build 1: rowboat voyage (current)

Design: [docs/GAMEPLAY.md](docs/GAMEPLAY.md). Menu **Catchline > Play Voyage** (Ctrl+Shift+P) opens `Assets/Scenes/Voyage.unity` and presses Play. Code lives in `Assets/Scripts/Game/`.

Controls: tap a rod, fish, the cooler or the deck to walk there; the big action button (or Space) does the contextual action (bait, hold to cast, strike, pick up, stow). H heads home. Scroll zooms.

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
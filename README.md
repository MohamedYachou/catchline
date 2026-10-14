# Catchline

Top-down automation game about a fishing boat that grows from a rowboat into a factory ship, crewed by little people you hire, assign and eventually replace with machines.

- Engine: Unity 6000.3.25f1 (URP, cross-platform template)
- Platforms: mobile + PC, landscape
- Large binaries (models, textures, audio) go through Git LFS, see `.gitattributes`

## Deck prototype

Open `Assets/Scenes/DeckPrototype.unity` and press Play. Everything is built from primitives at startup by `Assets/Scripts/Prototype/DeckPrototype.cs`.

Crab pots flow hauler → sorting table → banding bench → live tank, with empty pots going to the pot rack and back into the water. Tap a person to select them, tap a station to give them that job, tap the bare deck to make them a free deckhand. Sell the catch when the tank fills; hire more crew with the money.

Headless check (simulates and renders a PNG to `Logs/`):

```
Unity -batchmode -quit -projectPath . -executeMethod Catchline.EditorTools.PrototypeTools.Snapshot -simSeconds 180 [-fullCrew yes]
```
# ART-5 market states

Four public sprites: blank Sold out stamp, blank Fresh today herb tag, and square quantity-button idle and pressed faces. Labels and plus/minus signs are live Fredoka text, not baked into the paintings. Each face can serve either plus or minus; explicit repeated uses and alternate pressed placements are measured in `layout.json`.

All PNGs are tightly bounded RGBA, 3 export pixels per logical pixel. Original built-in ImageGen paintings and exact prompts are in `provenance/`. `manifest.json`, `layout.json`, `text-styles.json`, `slices.json` and measured text fits accompany actual-size context, state comparison and contact sheet. Fixed-aspect small artwork needs no nine-slicing.

The preview reconstructs row 1 with zero stock and replaces its Sell/Keep actions with Sold out. Fresh today is shown on row 2. Row 3 demonstrates kg controls with an illustrative 0.5 value; this does not set quantity increments or economy. Caller clamps quantity to available unsold kg, disables decrement at zero/increment at the maximum, and renders only one idle/pressed face per control. Keep each tap target at least the game's minimum even if the art face is 28 logical pixels. Replacing the original buttons requires the full row layout demo, not stacking new art over live price text.

Source-art delivery only: native import, quantity interaction, responsive anchors and lead/Mo acceptance remain with Claude/Mo. No Assets, production code or Git edits.

# RESTAURANT-ART-3 — arrange drawer states

Four tight RGBA3x sprites: blank Stored ribbon, blank Bistro tag with painted padlock, muted coin-price chip and accepted item-card backing. New paintings used built-in ImageGen; exact prompts are in `../coach-card/generation-prompts.json`, originals in `provenance/`. No text baked into PNGs.

`layout.json` records all repeated card/state uses and two external accepted table illustrations. `text-styles.json` has nine measured live labels. Source `ui-1-arrange.png` remains untouched; the new `ui-arrange-card-states.png` illustrates the three states side by side inside its drawer. Original wallet and example item price do not represent an affordability test; runtime must bind live values.

Stored means an already-owned item can be placed for free. Bistro tag indicates stage-gated items. Disabled price uses subdued readable text plus explicit Not enough coins; caller disables purchase and supplies the real price. Keep badge/lock/coin proportions; only card backing is sliced, with export-pixel borders recorded in `slices.json`. Scale non-sliced badges proportionally. No gameplay/economy changes.

Build with `uv run --with pillow python Art/Source/Restaurant/exact/coach-card/package.py b`. Contact shows exported cuts and actual-size cuts; context is844x390. Final audit and actually-opened hash ledger are in `../coach-card/`. Source art only; Claude imports/wires and verifies native interactions.

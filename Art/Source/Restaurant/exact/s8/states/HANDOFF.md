# RESTAURANT-ART-5 handoff

Source-art delivery complete. Eleven new public sprites across three additive packages. No Assets, production code or Git edits; no commit. Claude imports and wires the states and effects.

| Package | Exports | Review |
| --- | --- | --- |
| `exact/s8/states/` | Muted Owned card, green check, Needs-stage lock tag, four-frame purchase sparkle | `actual-size-context.jpg`, `contact-sheet.jpg`, two slice proofs, `sparkle-frames.jpg` |
| `exact/s7/states/` | Sold out stamp, Fresh today tag, shared quantity-button idle/pressed backings | `actual-size-context.jpg`, `contact-sheet.jpg`, `stepper-state-review.jpg` |
| `exact/s11/celebrate/` | Soft radial rays, six-frame confetti, blank New stage ribbon matching S5 | `actual-size-context.jpg`, `contact-sheet.jpg`, `confetti-frames.jpg` |

Paths above are relative to `Art/Source/Restaurant/`. Each package contains its own manifest, measured 844x390 layout, text styles with rectangles, slices, report, paintings/prompts and provenance. All labels, including +/minus, remain live text. The market layout includes repeated button placements. Example wallet, price and total values are illustrative art references.

Import at three export pixels per logical pixel. Tight bounding boxes and logical sizes are explicit. Original paintings are retained; 3x export resampling does not claim native 3x painted detail. Accepted lock and ribbon art was reused with source hashes. Keep source manifests intact; these are additive packages.

The purchase and confetti PNGs are **variable-width horizontal atlases**. Slice using each manifest frame's export-pixel `rect`, not equal cells. Each frame has its own normalized top-left `pivot`; Unity uses `[x, 1-y]`. Place each pivot at one shared anchor to prevent crop jitter. Purchase: four frames, 75 ms each, 300 ms total; confetti: six frames, 100 ms each, 600 ms total. Hide after playback. GIFs loop for review only. Purchase sparkle belongs over the item illustration, clear of the title/effect text. Rays scale uniformly around their centre, behind the facade at the demo's 0.55 opacity; do not nine-slice them. Reduced motion can omit bursts and retain static badges/ribbon.

`delivery-audit.json`: PASS, 11 unique tight RGBA 3x exports, 1,252 accepted source files byte-preserved, two distinct 4/6-frame sequences, 24 fitting live labels and 11 current actually-opened visual-review hashes. Source/export hashes, measured layout coverage, bounds and slice borders pass. Reproduce with `uv run --with pillow python Art/Source/Restaurant/exact/s8/states/audit_delivery.py`. Packaging steps A/B/C are in the adjacent `package.py`.

Native import, runtime timing/anchors, state conditions, responsive placement, interaction and lead/Mo acceptance remain pending. No temporary restore backups were created. Provenance and preservation baseline are retained as delivery evidence. Codex 1 is finished and all ART-5 paths are released.

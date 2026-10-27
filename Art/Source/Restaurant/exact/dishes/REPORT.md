# Restaurant dishes — ART-4

Nine new isolated menu paintings: pan-fried fish, fish and chips, seafood platter, crab, calamari, tea, beer, fries and bread. Public names are `v2-dish-*` exactly as requested.

Use `manifest.json` for tight RGBA dimensions and SHA256, and `layout.json` for a measured catalog example. All exports are **3 pixels per logical pixel**. Each aspect-fits a 91×75 logical box, using the accepted grilled dish's 91px width and soup's 75px height as the size family. The old imported references are 6× source art; they are not silently replaced. Preserve aspect when drawing in order bubbles, plan cards and receipt rows.

`actual-size-review.jpg` shows every new icon at order (24px), receipt (48px) and plan (91px) widths. `reference-comparison.jpg` compares the accepted two dishes and all nine new dishes at 48px. `contact-sheet.jpg` includes enlarged and actual-size views. These are source-art reviews, not screenshots of native integration.

Original built-in ImageGen paintings remain in `provenance/`; prompts and original output locations are in `generation-records.json`. Cropping/resizing is mechanical, and 3× resampling is not a claim of native 3× painted detail. Sprites have no baked labels. `text-styles.json` is intentionally empty for icon-only art.

Run `uv run --with pillow python Art/Source/Restaurant/exact/dishes/audit_delivery.py` for the final delivery audit after visual review. The audit checks all 14 ART-4 exports, accepted source art preservation, the existing steam strip, measured placements, text fit and current opened-review hashes. Claude owns Unity import, mapping menu IDs, live sizing and native acceptance. No Assets/code/git changes or commit.

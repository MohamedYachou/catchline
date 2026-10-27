# RESTAURANT-ART-7 — source art ready for Claude

Codex 1 (Windows app), 2026-10-27. All three assigned packages are complete. No Assets, runtime code, Unity metadata or Git changes. Claude owns native import and wiring; these are source-art and placement proofs, not runtime acceptance.

## Packages

| Folder | Public exports | Contract |
|---|---:|---|
| `exact/mira-moods/` | 8 | `v2-mira-{happy,worried,excited,proud}-{call,coach}`; call 38x51 logical / 114x153 PNG, coach 102x136 / 306x408. Happy defaults are byte-identical accepted exports. Other expressions retain Mira D host wardrobe, hair and identity. |
| `exact/s3/special/` | 2 | `v2-s3-special-board` 162x209 logical; `v2-s3-special-dish-slot` 110x78. Both sliced; title, dish name and +tips are live. Existing grilled-fish sprite shown by reference, not duplicated. |
| `exact/s2/pause/` | 3 | `v2-s2-pause-panel` 360x290 logical; `v2-s2-pause-primary` and `-secondary` 280x44. All sliced. Title and three action labels live. |

Each package includes manifest, measured layout, text styles/measurements, slices and actual-size contact sheet. Slice borders are **export pixels, left/bottom/right/top**. Layout/text rects are **top-left logical mockup pixels**. Import at the same scale as the accepted restaurant kit: divide PNG bounds by three for nominal logical bounds. Preserve aspect for portraits; use slices for panels/buttons. All PNGs have tight alpha bounds. 3x export/resampling does not claim native 3x painted detail.

## Bindings and placement

- Happy is default; worried = out of stock/breakdown; excited = birthday/tour/full house; proud = closing/best night. Switch the sprite in the existing call/coach component. `layout.json` records all alternatives. The two expression contexts show excited call and proud coach together only as a component demonstration; do not open both automatically.
- Special context replaces the right request slot in the S3 plan. Keep an active guest request readable; the art defines no priority rule between that request and the special. Supply actual dish/name/tip bonus at runtime. The sample `+tips` is not a new numeric reward rule.
- Pause phone actions have 44px minimum height; desktop actions are 64px. Runtime must pause the service clock/simulation, block room input and manage focus. Resume/Escape return to service; Speed tips uses caller-owned help; Back to the harbour uses the existing safe-exit/confirmation flow. No save/discard rules are introduced by this art. Background dim is a caller primitive: #091F30 at alpha 150/255.
- No “Last orders” sprite: call-strip text continues to be live.

## Review artifacts

`Art/Source/Restaurant/concepts/` contains:

- `ui-mira-moods-phone.png` (844x390) and `ui-mira-moods-desktop.png` (1440x900).
- `ui-3-special.png` (844x390).
- `ui-pause-phone.png` (844x390) and `ui-pause-desktop.png` (1440x900).

`expression-review.jpg` compares all moods at large, coach and tiny call sizes. Each package's `contact-sheet.jpg` shows nominal actual sizes. Special and pause have `slice-proof.jpg`. Originals and ImageGen prompts/receipts are retained under provenance. Pause and blank kit parts reuse accepted painted assets without modifying them.

## Verification

Run `uv run --with pillow python Art/Source/Restaurant/exact/mira-moods/audit_delivery.py` from the project root.

PASS: 13 unique tight RGBA exports at 3x; all source/export hashes; all layout bounds and alternative coverage; valid slice borders; 15 live labels fit; 1,532 accepted art files byte-preserved; 11 actually opened final review artifacts still match their hashes; all five concepts reconstruct exactly from declared backgrounds, layers, slices and live text. Undimmed backgrounds are unchanged outside declared placement/text rects. Reports: `delivery-audit.json`, `visual-review.json`.

Native import, responsive in-game overlap, expression state selection, pause/exit interaction, and Mo/lead acceptance remain for Claude. No commit. All ART-7 reservations released.

# PURCHASE-FX-ART-1

Codex 2 (WSL CLI). A–C complete: two transparent sprites, editable SVG masters, opened review sheet and technical receipt.

| Item | PNG in this folder and identical Assets/Art/UI/Crew copy | Size |
|---|---|---|
| A | fx-coin-glint.png | 128 × 128 RGBA |
| B | fx-buy-burst.png | 256 × 256 RGBA |

Masters: svg/fx-coin-glint.svg and svg/fx-buy-burst.svg. These extend the existing geometric FX family, with the purchase landing capture, fx-glow and fx-splash inspected before construction. Gold #E6AD38, restrained brass edge #B97924, pale gold #FFE9A3/#FFF2BC and the glint's white core tie them to the wallet coins and warm UI. No text, blur, background, glow filter or animation baked into either sprite.

A has four curved gold points around a white core. Centre/pivot is (64,64). B has twelve short tapered gold sparkle dashes radiating around (128,128), with slight controlled differences in length and angle; its central rectangle (74,74)–(182,182) is fully transparent. Preserve full square canvas and centre pivot. Code owns scale/fade; no runtime changes made.

review/sheet.png is 1440 × 900. Opened and inspected on cream #F4EBDA and navy #1C3A5A at actual 32,64,128 px for A and 32,64,200 px for B. Four-point glint and white core remain legible at the small sizes. Burst stays open-centred with separated dashes; its 32px version is deliberately delicate, with stronger detail at64/200px. Gold edges separate from cream, pale faces separate from navy. Static critique/audit/polish found no material defect; no corrective pass needed. Labels occur only in the review sheet.

Independent checks: both PNGs exact size/RGBA; outer canvas borders zero alpha; source/Assets complete bytes identical; alpha>127 forms one connected glint and twelve separate burst components; glint centre is (255,255,255,255); burst's108 ×108 central rectangle is zero alpha. Both SVGs parse and contain no text, image or filter nodes. delivery-checks.json records measured bounds and source/export/copy/sheet SHA256 hashes.

Static asset delivery only. Unity import, animation, live wallet/item placement and player acceptance remain Claude/Mo scope. Claude makes .meta files. No code files, git/commit, Unity, metas, audio, saves, watchdogs, peer edits, subagents or background work. New-only construction needed no major-change backup. No remaining artist steps or unresolved decisions; reservations released in comms.md.

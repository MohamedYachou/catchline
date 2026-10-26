# RESTAURANT-UI-EXACT-1 — Codex 2 (WSL CLI)

**Work in progress.** This report is generated from the current artifact set. Final completeness and visual status are recorded below; a generated sprite is not native/runtime acceptance.

Scope: S1 Arrange, S2 phone and desktop Service, service Mira bust, all 18 existing deck crew identities. Output folder only; no Assets, metas, C#, save, git or 3D changes.

Only style references: `Art/Source/Restaurant/concepts/ui-1-arrange.png`, `ui-2-service.png`, `ui-service-desktop.png`. Original deck portraits supply crew identity. `layout.json` records native mockup coordinates: phone 844×390, desktop 1440×900. Rectangles use top-left x/y, width/height. Placement measurements and the font match are visual estimates from raster references, not extracted vector metadata.

Artwork: imagegen with intrinsic alpha. Packaging: FFmpeg crop/resize/transparent padding and technical contacts only. Pillow reads metadata and alpha extents; it does not paint artwork. Every generated source and receipt is retained in `provenance/`. The alpha>=32 contour locates the artwork crop with a 12-source-pixel halo; no alpha keying or recoloring is applied. Six transparent export pixels surround the fitted artwork.

PNG canvas dimensions are at least three times every listed mockup placement. `asset-audit.json` explicitly reports source upscaling: canvas resolution does not imply native generated detail at that size. No UI labels are baked; pictorial currency marks/checks/arrows are integral icons.

## Pieces and review status

| Name | Export px | Primary reference x,y,w,h | Screen | Native source enlarged | Open/review |
|---|---:|---|---|---|---|
| [v2-bar-arrange](v2-bar-arrange.png) | 2532×132 | 0,0,844,43 | arrange | yes | pending |
| [v2-bar-service](v2-bar-service.png) | 4320×240 | 0,0,1440,80 | desktop | yes | pending |
| [v2-icon-bar-glass](v2-icon-bar-glass.png) | 360×360 | 169,318,22,27 | arrange | no | pending |
| [v2-icon-chair](v2-icon-chair.png) | 360×360 | 99,317,23,27 | arrange | no | pending |
| [v2-icon-coin-service](v2-icon-coin-service.png) | 360×360 | 936,13,52,52 | desktop | no | pending |
| [v2-icon-kitchen-pot](v2-icon-kitchen-pot.png) | 360×360 | 28,320,29,25 | arrange | no | pending |
| [v2-icon-star-blue](v2-icon-star-blue.png) | 360×360 | 1086,11,53,53 | desktop | no | pending |
| [v2-icon-star](v2-icon-star.png) | 360×360 | 618,7,32,32 | phone | no | pending |
| [v2-icon-sun](v2-icon-sun.png) | 360×360 | 18,5,39,39 | phone | no | pending |
| [v2-service-card](v2-service-card.png) | 960×960 | 1153,83,275,264 | desktop | no | pending |

## Nine-slice borders

Values below are L/T/R/B in final PNG source pixels. Do not use normalized values. Preserve corners and stretch the center. Illustrations, circles, arrows, placement balloons, rings, curves and speech bubbles are single sprites; their shapes must not be sliced. Full-width bars may crop their endcaps at the viewport edge.

| Sprite | Source L/T/R/B | Minimum destination px |
|---|---|---|
| v2-bar-arrange | 33 / 33 / 33 / 33 | 67×67 |
| v2-bar-service | 48 / 48 / 48 / 48 | 97×97 |
| v2-service-card | 288 / 288 / 288 / 288 | 577×577 |

## Text style sheet

Font implementation match: Fredoka Bold / SemiBold (`Assets/Resources/Fonts`) and Fredoka Medium (`Assets/Art/UI/Fonts`), inferred from the mockup. Use the listed native-screen size, fill and stroke; desktop values are measured in 1440×900 pixels, phone values in 844×390 pixels. Weight500 uses Medium, 600 SemiBold, 700 Bold. These labels must be drawn by runtime.

| Screen | Text | Weight | Size px | Fill | Stroke / px | Shadow x,y,color |
|---|---|---:|---:|---|---|---|
| s1-phone | Arrange | 700 | 27 | #FFF8EB | #062548 / 1.4 | 0, 1.5, #002944 |
| s1-phone | Undo | 700 | 15 | #062548 | #FFF4DE / 0 | 0, 0, #00000000 |
| s1-phone | 2,450 | 700 | 19 | #061F49 | #FFF4DE / 0 | 0, 0, #00000000 |
| s1-phone | Kitchen / Guests / Bar / Decor / Expand | 700 | 12 | #062548 | #8A330C / 0 | 0, 0, #00000000 |
| s1-phone | Table for2 / Table for4 / Booth (catalog) | 700 | 11 | #061E49 | #FFF5DE / 0 | 0, 0, #00000000 |
| s1-phone | 120 /220 /380 | 700 | 14 | #061E49 | #FFF5DE / 0 | 0, 0, #00000000 |
| s1-phone | 1x1 /2x1 | 600 | 10 | #123953 | #FFF5DE / 0 | 0, 0, #00000000 |
| s1-phone | Table for2 ·1x1 (world tag) | 700 | 14 | #061E49 | #FFF5DE / 0 | 0, 0, #00000000 |
| s2-phone | 18:40 | 700 | 21 | #FFF9ED | #08264D / 1 | 0, 1, #08264D |
| s2-phone | Evening service | 600 | 11 | #FFF9ED | #08264D / 0.6 | 0, 1, #08264D |
| s2-phone | NOW | 700 | 10 | #FFF9ED | #B6440A / 0.4 | 0, 1, #B6440A |
| s2-phone | 320 /42 | 700 | 18 | #FFF9ED | #08264D / 0.7 | 0, 1, #08264D |
| s2-phone | 1x /2x | 700 | 16 | #FFF9ED | #623619 / 0.6 | 0, 1, #6D3315 |
| s2-phone | Fish /Soup /Coffee | 700 | 14 | #061C49 | #FFF5DE / 0 | 0, 0, #00000000 |
| s2-phone | 8 /5 /12 (stock) | 700 | 18 | #061C49 | #FFF5DE / 0 | 0, 0, #00000000 |
| s2-phone | A late table? | 700 | 15 | #061C49 | #FFF5DE / 0 | 0, 0, #00000000 |
| s2-phone | A group just arrived. Shall we seat them? | 500 | 10 | #08234C | #FFF5DE / 0 | 0, 0, #00000000 |
| s2-phone | Seat them | 700 | 15 | #FFF8EB | #873B0B / 0.8 | 0, 1, #6C2E0E |
| s2-phone | Not tonight | 700 | 14 | #071E47 | #FFF7E5 / 0 | 0, 0, #00000000 |
| s2-phone | Cook /Serve /Fix /Coffee | 700 | 13 | #061E49 | #FFF5DE / 0 | 0, 0, #00000000 |
| s2-desktop | Mira's · Evening service | 700 | 39 | #FFF8EC | #092544 / 1.1 | 0, 2, #05233E |
| s2-desktop | 18:00 /20:00 /23:00 | 600 | 16 | #FFF8EC | #092544 / 0.6 | 0, 1, #05233E |
| s2-desktop | 18:40 (flag) | 700 | 17 | #FFF8EC | #B44C0E / 0.5 | 0, 1, #A94209 |
| s2-desktop | 320 /42 | 700 | 27 | #FFF8EC | #092544 / 0.8 | 0, 1, #05233E |
| s2-desktop | 1x /2x | 700 | 27 | #FFF8EC | #092544 / 0.7 | 0, 1, #05233E |
| s2-desktop | Tonight's stock | 700 | 22 | #071D48 | #FFF7E3 / 0 | 0, 0, #00000000 |
| s2-desktop | 8 /5 /12 (stock) | 700 | 32 | #071D48 | #FFF7E3 / 0 | 0, 0, #00000000 |
| s2-desktop | Fryer needs repair | 700 | 16 | #BE1911 | #FFF7E3 / 0 | 0, 0, #00000000 |
| s2-desktop | A late table? | 700 | 23 | #071D48 | #FFF7E3 / 0 | 0, 0, #00000000 |
| s2-desktop | A party of four has arrived. | 500 | 18 | #071D48 | #FFF7E3 / 0 | 0, 0, #00000000 |
| s2-desktop | Seat them | 700 | 23 | #FFF8EB | #8E380C / 0.9 | 0, 1.5, #8A300A |
| s2-desktop | Not tonight | 700 | 22 | #071D48 | #FFF7E3 / 0 | 0, 0, #00000000 |
| s2-desktop | Cook /Serve /Fix /Coffee /Reception | 700 | 20 | #071D48 | #FFF7E3 / 0 | 0, 0, #00000000 |

Selected Guests tab: ivory fill #FFF8EB, burnt-orange stroke #8A330C at0.7phone px; unselected category labels navy. Other state-specific overrides are retained in `text-styles.json`.

## Layout sheet

| Screen | Asset | x | y | w | h |
|---|---|---:|---:|---:|---:|
| phone | v2-btn-primary | 665 | 139 | 161 | 35 |
| phone | v2-btn-secondary | 665 | 178 | 161 | 34 |
| arrange | v2-btn-back | 23 | 5 | 51 | 33 |
| arrange | v2-btn-undo | 735 | 5 | 88 | 33 |
| arrange | v2-tab-idle | 16 | 310 | 58 | 64 |
| arrange | v2-tab-selected | 78 | 309 | 68 | 65 |
| arrange | v2-item-card | 350 | 306 | 149 | 71 |
| arrange | v2-item-card-idle | 505 | 306 | 152 | 71 |
| arrange | v2-name-tag | 650 | 138 | 175 | 37 |
| arrange | v2-btn-rotate | 512 | 151 | 44 | 49 |
| arrange | v2-btn-cancel | 559 | 151 | 45 | 49 |
| arrange | v2-btn-confirm | 607 | 151 | 44 | 49 |
| phone | v2-stock-card | 9 | 55 | 149 | 62 |
| desktop | v2-stock-slab | 16 | 90 | 194 | 316 |
| desktop | v2-stock-row | 28 | 137 | 166 | 57 |
| desktop | v2-chip-repair | 28 | 335 | 167 | 56 |
| desktop | v2-staff-card | 44 | 769 | 246 | 89 |
| phone | v2-staff-card-phone | 15 | 323 | 166 | 55 |
| desktop | v2-staff-rail | 34 | 758 | 1374 | 112 |
| arrange | v2-arrange-tray | 0 | 299 | 844 | 91 |
| desktop | v2-speed-pill | 1225 | 13 | 194 | 55 |
| phone | v2-speed-selected | 701 | 6 | 44 | 33 |
| phone | v2-speed-idle | 745 | 6 | 44 | 33 |
| desktop | v2-icon-pause | 1249 | 26 | 20 | 24 |
| phone | v2-wallet-pill | 529 | 7 | 77 | 32 |
| arrange | v2-wallet-arrange | 603 | 5 | 99 | 33 |
| phone | v2-timeline-track | 177 | 6 | 326 | 34 |
| phone | v2-timeline-flag | 359 | 3 | 34 | 22 |
| desktop | v2-timeline-dot | 650 | 30 | 15 | 15 |
| phone | v2-timeline-guest | 270 | 9 | 16 | 23 |
| phone | v2-meter-track | 71 | 99 | 75 | 10 |
| phone | v2-meter-fill | 71 | 99 | 44 | 10 |
| desktop | v2-meter-ring-track | 218 | 785 | 63 | 62 |
| desktop | v2-meter-ring-fill | 218 | 785 | 63 | 62 |
| desktop | v2-bubble-order | 931 | 165 | 69 | 65 |
| desktop | v2-mira-service-bust | 1140 | 98 | 149 | 135 |
| desktop | v2-bar-service | 0 | 0 | 1440 | 80 |
| arrange | v2-bar-arrange | 0 | 0 | 844 | 43 |
| desktop | v2-icon-coin-service | 936 | 13 | 52 | 52 |
| phone | v2-icon-star | 618 | 7 | 32 | 32 |
| desktop | v2-icon-star-blue | 1086 | 11 | 53 | 53 |
| phone | v2-icon-sun | 18 | 5 | 39 | 39 |
| arrange | v2-icon-kitchen-pot | 28 | 320 | 29 | 25 |
| arrange | v2-icon-chair | 99 | 317 | 23 | 27 |
| arrange | v2-icon-bar-glass | 169 | 318 | 22 | 27 |
| arrange | v2-icon-decor-plant | 227 | 318 | 24 | 27 |
| arrange | v2-icon-expand | 288 | 319 | 28 | 25 |
| desktop | v2-icon-pan | 151 | 800 | 54 | 44 |
| phone | v2-icon-cloche | 246 | 330 | 22 | 22 |
| desktop | v2-icon-wrench | 686 | 805 | 45 | 47 |
| desktop | v2-icon-cup | 937 | 807 | 49 | 46 |
| desktop | v2-icon-bell | 1194 | 807 | 45 | 47 |
| desktop | v2-icon-fish-stock | 41 | 145 | 65 | 49 |
| desktop | v2-icon-soup | 42 | 205 | 64 | 57 |
| desktop | v2-icon-wrench-repair | 37 | 343 | 40 | 40 |
| phone | v2-icon-warning | 127 | 64 | 20 | 22 |
| arrange | v2-item-rest-table2 | 358 | 319 | 68 | 46 |
| arrange | v2-item-rest-table4 | 517 | 314 | 69 | 56 |
| arrange | v2-item-rest-booth | 669 | 311 | 79 | 62 |
| phone | v2-timeline-curve | 186 | 7 | 308 | 28 |
| desktop | v2-timeline-curve-desktop | 551 | 22 | 286 | 27 |
| arrange | v2-placement-highlight | 545 | 195 | 84 | 58 |
| phone | v2-bar-service | 0 | 0 | 844 | 46 |
| phone | v2-icon-pause | 807 | 14 | 17 | 18 |
| phone | v2-speed-pill | 699 | 5 | 90 | 35 |
| phone | v2-speed-idle | 797 | 6 | 36 | 34 |
| phone | v2-wallet-pill | 616 | 7 | 72 | 32 |
| phone | v2-service-card | 654 | 53 | 182 | 170 |
| phone | v2-mira-service-bust | 662 | 58 | 73 | 77 |
| phone | v2-stock-card | 9 | 120 | 149 | 61 |
| phone | v2-stock-card | 9 | 184 | 149 | 63 |
| phone | v2-icon-fish-stock | 20 | 67 | 41 | 36 |
| phone | v2-icon-soup | 21 | 133 | 39 | 35 |
| phone | v2-icon-cup | 20 | 194 | 42 | 41 |
| phone | v2-btn-primary | 665 | 139 | 161 | 35 |
| phone | v2-btn-secondary | 665 | 178 | 161 | 34 |
| phone | v2-bubble-order | 404 | 131 | 57 | 46 |
| phone | v2-bubble-order | 524 | 140 | 48 | 47 |
| phone | v2-staff-card-phone | 183 | 323 | 164 | 55 |
| phone | v2-staff-card-phone | 349 | 323 | 160 | 55 |
| phone | v2-staff-card-phone | 512 | 323 | 158 | 55 |
| phone | v2-meter-track | 81 | 356 | 88 | 11 |
| phone | v2-meter-track | 249 | 356 | 88 | 11 |
| phone | v2-meter-track | 412 | 356 | 87 | 11 |
| phone | v2-meter-track | 574 | 356 | 87 | 11 |
| phone | v2-icon-pan | 81 | 332 | 22 | 15 |
| phone | v2-icon-wrench | 413 | 331 | 19 | 20 |
| phone | v2-icon-cup | 575 | 331 | 20 | 20 |
| desktop | v2-btn-back | 21 | 12 | 73 | 58 |
| desktop | v2-service-card | 1153 | 83 | 275 | 264 |
| desktop | v2-btn-primary | 1179 | 228 | 233 | 49 |
| desktop | v2-btn-secondary | 1179 | 286 | 233 | 45 |
| desktop | v2-stock-row | 28 | 201 | 166 | 59 |
| desktop | v2-stock-row | 28 | 266 | 166 | 59 |
| desktop | v2-icon-cup | 42 | 270 | 64 | 56 |
| desktop | v2-speed-selected | 1292 | 15 | 62 | 51 |
| desktop | v2-speed-idle | 1358 | 15 | 59 | 51 |
| desktop | v2-wallet-pill | 935 | 14 | 125 | 51 |
| desktop | v2-wallet-pill | 1081 | 13 | 120 | 52 |
| desktop | v2-timeline-flag | 630 | 3 | 56 | 31 |
| desktop | v2-timeline-track | 551 | 20 | 286 | 32 |
| desktop | v2-staff-card | 298 | 769 | 270 | 89 |
| desktop | v2-staff-card | 575 | 769 | 246 | 89 |
| desktop | v2-staff-card | 828 | 769 | 255 | 89 |
| desktop | v2-staff-card | 1090 | 769 | 305 | 89 |
| desktop | v2-meter-ring-track | 490 | 785 | 63 | 62 |
| desktop | v2-meter-ring-track | 741 | 785 | 63 | 62 |
| desktop | v2-meter-ring-track | 999 | 785 | 63 | 62 |
| desktop | v2-meter-ring-track | 1316 | 785 | 63 | 62 |
| desktop | v2-bubble-order | 620 | 355 | 58 | 60 |
| desktop | v2-bubble-order | 988 | 370 | 65 | 62 |
| arrange | v2-tab-idle | 151 | 310 | 56 | 64 |
| arrange | v2-tab-idle | 211 | 310 | 56 | 64 |
| arrange | v2-tab-idle | 271 | 310 | 60 | 64 |
| arrange | v2-item-card-idle | 662 | 306 | 165 | 71 |
| arrange | v2-icon-coin-service | 614 | 11 | 23 | 23 |
| arrange | v2-icon-chair | 95 | 7 | 22 | 29 |

## Limits and handoff

- `review/<sprite>-compare.png`: actual source reference crop beside the delivered sprite. Crew contacts use the original deck portrait, since the mockup does not depict all18 identities.
- `visual-review.json`: per-image openings, findings, and corrections. A review can record a mismatch; opening alone does not imply an exact match.
- Rounded-font identification and source pixel measurements are inferred. Reconstructed art can differ from the raster mockup; do not label source checks as Mo's acceptance.
- No Unity import, runtime HUD screenshot, layout assembly or native-device acceptance performed in this output-only task. Integration belongs to Claude.
- No commit. No subagents. Source/machinery stays in this owned directory; other agents' artifacts are preserved.

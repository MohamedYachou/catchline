# Restaurant exact S3–S5 source-art handoff

Owner: Codex 1 (Windows app). Reference authority: `../../concepts/ui-3-mira-plan.png`, `ui-4-prep.png`, `ui-5-closing.png`. The r10 captures are comparison evidence, not style authority.

## Delivery status

90/90 named pieces packaged. Final visual review status is recorded in `visual-review.json`; inventory/hash checks are in `asset-audit.json`. This report must not be read as lead/Mo acceptance or runtime integration.

All artwork uses the built-in imagegen tool. `provenance/<name>.json` records each exact prompt, reference paths and saved original. `provenance/<name>.png` preserves the untouched generator result. Mechanical packaging only trims alpha, proportionately fits/pads the canvas, and builds comparisons; it does not repaint/recolour artwork. The three full-bleed backgrounds and prep top strip are opaque by design. The top strip uses source crop [0,0,2154,275] to exclude unrelated white padding, then a proportional bottom-aligned fit; its untouched original is retained.

## Integration

No `Assets/`, `.meta`, `.cs`, Git, player save or watchdog changes. Claude chooses/imports the art and draws all text. Keep original metas on replacement. Shared existing names are retained here; S1/S2 alternatives belong to Codex 2, so the lead must choose shared button/icon/sign variants deliberately.

Coordinates use top-left origin on the 844×390 mockup, including illustrated overflow/shadows. They are hand-measured outer visual rectangles, typically within 1–3 px, not source layout metadata. `layout.json` lists repeated pieces too. This scope has no separate desktop mockup: S2 1440×900 desktop belongs to Codex 2. Do not multiply these into a desktop layout without checking the lead’s responsive composition.

Mira originals extend the mockup’s cropped upper-body poses to full figures as requested. Keep the mockup upper-body placement with an appropriate clip; fitting an entire standing figure into the original torso rectangle would shrink her face. Fish are single painted whole species, right-facing, 1024×512; crab/flatfish are shown from above. Extra three guest portraits are companion designs because only three review faces appear in S5.

## Slice borders

Borders are exact source-pixel import recommendations **L / T / R / B**, not Unity vector order (L / B / R / T). Rect sizes above are logical pixels. Use the source-pixel borders directly for import; canvases are not universally exactly3x. Use a centered pivot for ordinary cards. Keep all native canvases and avoid import trimming when applying these values.

| Piece | Canvas | L / T / R / B | Rule |
|---|---:|---|---|
| v2-plan-paper | 1224×885 | 80 / 95 / 77 / 82 | Preserve corners; stretch only centre/edges |
| v2-plan-dish-card | 366×369 | 34 / 37 / 34 / 38 | Preserve corners; stretch only centre/edges |
| v2-btn-accept | 417×153 | 48 / 49 / 48 / 56 | Preserve corners; stretch only centre/edges |
| v2-btn-secondary | 420×153 | 48 / 56 / 48 / 62 | Preserve corners; stretch only centre/edges |
| v2-btn-primary | 600×210 | 77 / 55 / 79 / 67 | Preserve corners; stretch only centre/edges |
| v2-btn-back | 390×153 | 45 / 47 / 45 / 49 | Preserve corners; stretch only centre/edges |
| v2-prep-catch-panel | 816×762 | 78 / 210 / 77 / 121 | Preserve corners; stretch only centre/edges |
| v2-prep-portions-panel | 1398×786 | 78 / 180 / 79 / 91 | Preserve corners; stretch only centre/edges |
| v2-paper-row | 1305×267 | 277 / 38 / 278 / 38 | Preserve corners; stretch only centre/edges |
| v2-number-field | 297×114 | 29 / 36 / 29 / 36 | Preserve corners; stretch only centre/edges |
| v2-btn-minus | 159×153 | 41 / 41 / 41 / 42 | Preserve corners; stretch only centre/edges |
| v2-btn-plus | 171×156 | 41 / 42 / 41 / 43 | Preserve corners; stretch only centre/edges |
| v2-bar-track | 306×42 | 26 / 20 / 26 / 20 | Preserve corners; stretch only centre/edges |
| v2-toggle-selected | 243×90 | 35 / 39 / 35 / 40 | Preserve corners; stretch only centre/edges |
| v2-toggle-unselected | 240×90 | 35 / 38 / 35 / 38 | Preserve corners; stretch only centre/edges |
| v2-summary-strip | 1302×174 | 154 / 52 / 152 / 52 | Preserve corners; stretch only centre/edges |
| v2-closing-board | 1821×1074 | 78 / 116 / 81 / 114 | Preserve corners; stretch only centre/edges |
| v2-closing-header | 1821×159 | 404 / 62 / 404 / 62 | Preserve corners; stretch only centre/edges |
| v2-metric-row | 585×210 | 37 / 71 / 37 / 71 | Preserve corners; stretch only centre/edges |
| v2-tonight-row | 573×171 | 70 / 48 / 37 / 49 | Preserve corners; stretch only centre/edges |
| v2-review-card | 657×210 | 34 / 34 / 34 / 34 | Preserve corners; stretch only centre/edges |
| v2-popularity-card | 504×456 | 38 / 57 / 38 / 57 | Preserve corners; stretch only centre/edges |
| v2-progress-track | 441×63 | 55 / 30 / 56 / 30 | Preserve corners; stretch only centre/edges |
| v2-progress-fill | 321×51 | 53 / 23 / 39 / 23 | Preserve corners; stretch only centre/edges |
| v2-bar-fill | 312×72 | 23 / 27 / 23 / 27 | Preserve corners; stretch only centre/edges |

The wood title sign, paper request ticket, Mira speech bubble, fish sign, characters and illustrations are **uniform-scale only**: ropes/lantern/pin/tail are authored decorations and must not be stretched. Panels with header bands preserve that band in their top border. Icons inside plus/minus buttons must remain square. Review panel sizes should remain close to the measured ratio; excessive paper-height stretch changes its shading.

## Text style sheet

The mockup contains painted lettering; an exact font identity is unproven. Use Fredoka Bold (700) / SemiBold (600), if available, as the closest runtime starting point, then compare actual captures. Sizes, strokes and shadows below are measured visual estimates in mockup pixels, **not** a verified font raster match. Scale size, outline width and shadow offset together at device resolution. UI text remains live. All general body numerals/labels are heavy navy.

| Style / screen | Visible text | Weight / px | Fill | Stroke hex / px | Shadow dx,dy / hex |
|---|---|---|---|---|---|
| title-wood / S3 | Tonight at Mira's | 700 / 32 | #FFF4DC | #281C18 / 2 | 0,2 / #311B13 |
| back / S3 | Back | 700 / 21 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| date / S3 | FRIDAY Â· 18:00 â€“ 23:00 | 700 / 25 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| forecast-guests / S3 | 18 â€“ 22 guests + walk-ins | 700 / 19 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| dish-label / S3 | Grilled fish / Fish soup / Coffee | 700 / 16 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| dish-guests / S3 | 8 â€“ 10 / 6 â€“ 8 / 10 â€“ 14 | 700 / 18 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| bring-back-heading / S3 | Bring back: | 700 / 15 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| bring-back-items / S3 | 8 mackerel / 3 kg pollock | 700 / 16 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| special-heading / S3 | Special request | 700 / 14 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| special-copy / S3 | A birthday table<br>for four | 700 / 18 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| accept / S3 | Accept | 700 / 18 | #FFF7E9 | #183525 / 1.4 | 0,1 / #103222 |
| not-tonight / S3 | Not tonight | 700 / 16 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| got-it / S3 | Got it | 700 / 27 | #FFF7E9 | #39221F / 2 | 0,2 / #5A2715 |
| prep-title / S4 | Prepare for tonight | 700 / 29 | #F9F5F1 | #142A44 / 2 | 0,2 / #0A233B |
| capacity / S4 | 30 / 30 | 700 / 21 | #17425A | #17425A / 0 | 0,0 / #00000000 |
| panel-heading / S4 | Today's catch / Portions | 700 / 26 | #FAFAFA | #19344B / 1.6 | 0,1.5 / #102A42 |
| catch-species / S4 | Mackerel / Pollock | 700 / 18 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| catch-count / S4 | 12 / 5 kg | 700 / 26 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| portion-label / S4 | Grilled fish / Fish soup / Fillets | 700 / 16 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| portion-count / S4 | 10 / 8 / 12 | 700 / 25 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| forecast-label / S4 | Forecast | 700 / 16 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| forecast-pill / S4 | Tight / +10% / +20% | 700 / 13 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| summary-label / S4 | Restaurant: / Market: / Captain's cut | 700 / 12 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| summary-value / S4 | 30 portions / 2 fish | 700 / 16 | #17425A | #17425A / 0 | 0,0 / #00000000 |
| prepare / S4 | Prepare | 700 / 27 | #FFF8EB | #3B2523 / 1.7 | 0,2 / #4D2518 |
| closing-title / S5 | A good night on the quay | 700 / 27 | #FFF9EA | #15253C / 1.7 | 0,2 / #0B243C |
| served / S5 | 22 served Â· 2 left | 700 / 16 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| metric-label / S5 | Dishes / Drinks / Tips / Tonight | 700 / 13 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| metric-number / S5 | 420 / 96 / 48 | 700 / 23 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| tonight-number / S5 | +564 | 700 / 29 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| review-quote / S5 | Fish worth the wait. / Cosy, even in the rain. / More coffee, please! | 700 / 14 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| popularity-title / S5 | Popularity | 700 / 19 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| popularity-before / S5 | 42 â†’ | 700 / 27 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| popularity-after / S5 | 46 | 700 / 32 | #F2790B | #F2790B / 0 | 0,0 / #00000000 |
| reputation / S5 | Harbour reputation / A warmer welcome | 600 / 12 | #17425A | #17425A / 0 | 0,0 / #00000000 |
| cats / S5 | 3 portions for<br>the alley cats / Value 18 | 700 / 14 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| crew-of-night-label / S5 | Crew of the night | 700 / 12 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| crew-of-night-name / S5 | Jo | 700 / 22 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| mira-bubble / S5 | Same time<br>tomorrow? | 700 / 13 | #080D2E | #080D2E / 0 | 0,0 / #00000000 |
| sleep / S5 | Sleep | 700 / 28 | #FFF9EA | #3B2523 / 1.8 | 0,2 / #56261A |

Selected forecast pills use #FFF8E8 with ~0.7 px navy outline; unselected use navy. The secondary popularity line uses #687A7D. Each text rectangle and these overrides are in `text-styles.json`.

## Piece layout and inventory

| Name | Screen | x,y,w,h at 844×390 | PNG canvas |
|---|---|---|---|
| v2-sign-plank | S3 | 234,0,398,72 | 1592×288 |
| v2-plan-paper | S3 | 258,69,408,295 | 1224×885 |
| v2-plan-dish-card | S3 | 275,162,122,123 | 366×369 |
| v2-ticket | S3 | 670,66,165,224 | 495×672 |
| v2-btn-accept | S3 | 681,184,139,51 | 417×153 |
| v2-btn-secondary | S3 | 679,230,140,51 | 420×153 |
| v2-btn-primary | S3 | 668,297,165,70 | 600×210 |
| v2-btn-back | S3 | 12,8,130,51 | 390×153 |
| v2-icon-back | S3 | 26,18,31,30 | 93×90 |
| v2-icon-calendar | S3 | 292,91,47,49 | 141×147 |
| v2-icon-special | S3 | 685,79,44,45 | 132×135 |
| v2-icon-tick | S3 | 693,311,39,36 | 117×108 |
| v2-icon-cross | S3 | 698,241,22,22 | 66×66 |
| v2-icon-guests | S3 | 301,257,21,20 | 84×78 |
| v2-catch-pile | S3 | 281,298,112,51 | 672×306 |
| v2-mira-plan | S3 | 0,44,281,346 | 1600×2000 |
| v2-bg-plan | S3 | 0,0,844,390 | 2532×1170 |
| v2-prep-catch-panel | S4 | 66,60,272,254 | 816×762 |
| v2-prep-portions-panel | S4 | 343,60,466,262 | 1398×786 |
| v2-paper-row | S4 | 81,118,244,85 | 1305×267 |
| v2-number-field | S4 | 629,112,99,38 | 297×114 |
| v2-btn-minus | S4 | 569,111,53,50 | 159×153 |
| v2-btn-plus | S4 | 734,110,57,52 | 171×156 |
| v2-bar-track | S4 | 628,150,102,14 | 306×42 |
| v2-bar-knob | S4 | 672,148,12,18 | 72×108 |
| v2-toggle-selected | S4 | 611,285,81,30 | 243×90 |
| v2-toggle-unselected | S4 | 529,285,80,30 | 240×90 |
| v2-summary-strip | S4 | 198,322,434,58 | 1302×174 |
| v2-checkbox-on | S4 | 490,333,38,37 | 114×111 |
| v2-checkbox-off | S4 | 490,333,38,37 | 114×111 |
| v2-divider | S4 | 353,331,5,41 | 30×246 |
| v2-icon-forecast | S4 | 418,287,25,24 | 75×72 |
| v2-icon-cutlery-white | S4 | 366,69,30,35 | 90×105 |
| v2-icon-cutlery | S4 | 216,331,29,35 | 87×105 |
| v2-icon-fish-white | S4 | 90,73,36,26 | 108×78 |
| v2-icon-fish-market | S4 | 366,335,44,29 | 132×87 |
| v2-icon-cooler | S4 | 642,9,43,39 | 129×117 |
| v2-icon-cloche | S4 | 650,332,43,31 | 129×93 |
| v2-sign-fish | S4 | 229,0,53,50 | 159×150 |
| v2-dish-grilled-fish | S4 | 362,111,91,51 | 546×306 |
| v2-dish-fish-soup | S3 | 408,166,110,75 | 660×450 |
| v2-dish-coffee | S3 | 541,169,99,73 | 594×438 |
| v2-dish-fillets | S4 | 364,228,90,49 | 540×294 |
| v2-bg-prep | S4 | 0,0,844,390 | 2532×1170 |
| v2-closing-board | S5 | 119,11,607,358 | 1821×1074 |
| v2-closing-header | S5 | 119,11,607,53 | 1821×159 |
| v2-metric-row | S5 | 129,96,191,45 | 585×210 |
| v2-tonight-row | S5 | 129,227,191,57 | 573×171 |
| v2-review-card | S5 | 327,64,219,64 | 657×210 |
| v2-popularity-card | S5 | 552,64,168,152 | 504×456 |
| v2-star-full | S5 | 563,107,44,42 | 264×252 |
| v2-star-empty | S5 | 471,141,21,21 | 126×126 |
| v2-progress-track | S5 | 558,154,147,21 | 441×63 |
| v2-progress-fill | S5 | 560,156,107,17 | 321×51 |
| v2-bubble-mira | S5 | 486,259,108,52 | 324×156 |
| v2-illus-cats | S5 | 130,292,104,69 | 624×414 |
| v2-dish-lemonade | S5 | 143,141,42,39 | 252×234 |
| v2-icon-coins | S5 | 143,185,44,39 | 264×234 |
| v2-icon-coin-service | S5 | 153,231,53,49 | 318×294 |
| v2-icon-bed | S5 | 562,332,43,31 | 129×93 |
| v2-icon-moon | S5 | 592,18,34,34 | 102×102 |
| v2-mira-wave | S5 | 580,209,148,167 | 1600×2000 |
| v2-portrait-crew-jo | S5 | 329,290,65,68 | 512×512 |
| v2-bg-closing | S5 | 0,0,844,390 | 2532×1170 |
| v2-review-portrait-01 | S5 | 335,68,59,56 | 512×512 |
| v2-review-portrait-02 | S5 | 335,132,59,60 | 512×512 |
| v2-review-portrait-03 | S5 | 335,201,59,60 | 512×512 |
| v2-review-portrait-04 | S5 | 335,68,59,56 | 512×512 |
| v2-review-portrait-05 | S5 | 335,132,59,60 | 512×512 |
| v2-review-portrait-06 | S5 | 335,201,59,60 | 512×512 |
| v2-fishart-mackerel | S4 | 89,132,123,61 | 1024×512 |
| v2-fishart-pollock | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-cod | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-herring | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-whiting | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-plaice | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-seabass | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-redmullet | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-turbot | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-conger | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-crab | S4 | 88,216,126,67 | 1024×512 |
| v2-fishart-squid | S4 | 88,216,126,67 | 1024×512 |
| v2-prep-topbar | S4 | 0,0,844,57 | 2532×171 |
| v2-accent-rays | S5 | 584,217,32,36 | 210×204 |
| v2-bar-fill | S4 | 629,150,52,12 | 312×72 |
| v2-icon-fish-bringback | S3 | 397,319,36,24 | 216×144 |
| v2-icon-pollock-bringback | S3 | 529,319,39,24 | 234×144 |
| v2-dish-grilled-plan | S3 | 277,165,118,68 | 708×408 |
| v2-dish-soup-prep | S4 | 362,169,91,52 | 546×312 |
| v2-dish-closing-fish | S5 | 140,101,56,34 | 336×204 |

### Additional placements

| Piece | Screen | x,y,w,h | Use |
|---|---|---|---|
| v2-plan-dish-card | S3 | 405,162,122,123 | soup card |
| v2-plan-dish-card | S3 | 533,162,122,123 | coffee card |
| v2-accent-rays | S3 | 258,169,31,39 | Mira planning emphasis; rotate to source |
| v2-paper-row | S3 | 275,292,376,61 | bring-back inset |
| v2-divider | S3 | 512,312,5,33 | catch request separator |
| v2-icon-guests | S3 | 431,257,21,20 | soup guest forecast |
| v2-icon-guests | S3 | 550,257,21,20 | coffee guest forecast |
| v2-icon-tick | S3 | 704,193,25,27 | accept button check; cream glyph |
| v2-btn-back | S4 | 13,6,53,46 | square back control; nine-slice |
| v2-icon-back | S4 | 25,16,29,25 | back arrow |
| v2-paper-row | S4 | 81,207,244,89 | second fish row |
| v2-paper-row | S4 | 359,112,435,55 | portion row 1; slice to rect |
| v2-paper-row | S4 | 359,169,435,56 | portion row 2 |
| v2-paper-row | S4 | 359,227,435,55 | portion row 3 |
| v2-btn-minus | S4 | 570,170,52,51 | soup minus |
| v2-btn-minus | S4 | 570,228,52,51 | fillets minus |
| v2-btn-plus | S4 | 734,169,57,52 | soup plus |
| v2-btn-plus | S4 | 734,227,57,52 | fillets plus |
| v2-number-field | S4 | 629,170,99,38 | soup quantity |
| v2-number-field | S4 | 629,228,99,38 | fillet quantity |
| v2-bar-track | S4 | 628,208,102,14 | soup track |
| v2-bar-track | S4 | 628,266,102,14 | fillets track |
| v2-bar-knob | S4 | 661,206,12,18 | soup thumb |
| v2-bar-knob | S4 | 662,264,12,18 | fillet thumb |
| v2-toggle-unselected | S4 | 692,285,80,30 | +20% selector |
| v2-btn-primary | S4 | 631,322,200,58 | Prepare button; nine-slice |
| v2-divider | S4 | 473,331,5,41 | market/captain separator |
| v2-metric-row | S5 | 129,65,191,31 | served count row |
| v2-metric-row | S5 | 129,141,191,42 | drinks row |
| v2-metric-row | S5 | 129,183,191,43 | tips row |
| v2-metric-row | S5 | 129,290,195,70 | cats row |
| v2-review-card | S5 | 327,132,219,64 | review row 2 |
| v2-review-card | S5 | 327,200,219,66 | review row 3 |
| v2-review-card | S5 | 327,288,219,70 | crew of the night row |
| v2-icon-guests | S5 | 148,68,28,26 | served guests |
| v2-dish-closing-fish | S5 | 140,101,56,34 | closing dishes metric |
| v2-icon-coin-service | S5 | 276,329,20,20 | cat food value coin |
| v2-btn-primary | S5 | 531,317,190,57 | Sleep button; nine-slice |
| v2-star-full | S5 | 681,149,28,28 | progress endpoint star |
| v2-star-full | S5 | 396,74,18,18 | review 1 stars start; repeat pitch 19.5, count 5 |
| v2-star-full | S5 | 396,142,18,18 | review 2 stars start; repeat pitch 19.5, count 4 |
| v2-star-full | S5 | 396,210,18,18 | review 3 stars start; repeat pitch 19.5, count 4 |
| v2-star-empty | S5 | 474,142,18,18 | review 2 fifth empty star |
| v2-star-empty | S5 | 474,210,18,18 | review 3 fifth empty star |

## Inspection and known limits

Every review pair in `review/<name>.png` places the actual mockup crop on the left and packaged piece on the right. `review/contact-s3-*.png`, `contact-s4-*.png`, `contact-s5-*.png` group four pairs per sheet. Labels/context in the reference crop are intentionally retained; final live text is removed. The report does not count an image as reviewed merely because a file exists: actual opened sheets and findings are logged in `visual-review.json`.

Native generator resolution varies by piece; exact original and final dimensions and upscale flags are recorded in `asset-audit.json`. A larger output canvas is not a claim of native painted detail. Generation may vary in contour, face, plate/food detail or backdrop reconstruction; exact-match findings remain part of manual review, rather than being implied by a passing alpha/hash check.

## Reproduce packaging

`uv run --with pillow python Art/Source/Restaurant/exact/s3-s5/build_manifest.py` regenerates reference crops/manifest only. `package.py` packages completed generator sources without overwriting finals. `report.py` regenerates these measured handoff tables. `seal.py` performs the final independent file/inventory checks. Original generation is not silently repeated by these helpers.

## Native resolution disclosure

These canvases exceed at least one original generator dimension. They meet the requested export sizes through proportionate resampling; they do not contain native detail at the export resolution. Both Mira originals are 1122x1402, exported to 1600x2000.

| Piece | Original generator pixels | Export canvas |
|---|---|---|
| v2-mira-plan | 1122x1402 | 1600x2000 |
| v2-bg-plan | 1844x853 | 2532x1170 |
| v2-bg-prep | 1844x853 | 2532x1170 |
| v2-closing-board | 1634x963 | 1821x1074 |
| v2-closing-header | 1342x1172 | 1821x159 |
| v2-mira-wave | 1122x1402 | 1600x2000 |
| v2-bg-closing | 1844x853 | 2532x1170 |
| v2-prep-topbar | 2154x730 | 2532x171 |

## Art-bounds import copies

Claude requested tightly cropped artwork after integrating the first exports. Use `tight/<name>.png` with `tight-layout.json` for those imports. These retain the SAME90piece names; there are no new sprite keys. Canonical root files retain the requested Mira/fish canvas sizes. Tight copies crop the alpha>=8 artwork bounds and uniformly resample only enough to meet >=3x EACH primary/repeated placement. Their crop, actual dimensions, resample factor, exact source-pixel L/T/R/B borders and hashes are recorded per asset. Low-alpha antialias/shadow inside the crop remains. These larger tight canvases do not add painted detail.

Canonical slice coordinates now include the measured transparent margins; tight slice coordinates exclude those margins. The tight copy keeps the measured visual placement rectangle; do not add canonical padding offsets again. The conservative border reserves keep header bands/corners; very thin tracks cap vertical borders so the middle remains stretchable. Use the source-pixel table matching the actual imported file.

| Tight import piece | PNG canvas | L / T / R / B |
|---|---|---|
| v2-plan-paper | 1241x885 | 74 / 92 / 74 / 68 |
| v2-plan-dish-card | 374x369 | 29 / 29 / 29 / 29 |
| v2-btn-accept | 492x153 | 51 / 44 / 51 / 51 |
| v2-btn-secondary | 553x153 | 57 / 49 / 57 / 57 |
| v2-btn-primary | 605x210 | 64 / 51 / 64 / 64 |
| v2-btn-back | 439x153 | 45 / 42 / 45 / 45 |
| v2-prep-catch-panel | 952x762 | 79 / 176 / 79 / 68 |
| v2-prep-portions-panel | 1501x786 | 72 / 161 / 72 / 62 |
| v2-paper-row | 1305x405 | 48 / 48 / 48 / 48 |
| v2-number-field | 364x114 | 30 / 30 / 30 / 30 |
| v2-btn-minus | 161x153 | 39 / 39 / 39 / 39 |
| v2-btn-plus | 176x156 | 39 / 39 / 39 / 39 |
| v2-bar-track | 622x42 | 44 / 19 / 44 / 19 |
| v2-toggle-selected | 323x90 | 42 / 37 / 42 / 37 |
| v2-toggle-unselected | 305x90 | 40 / 36 / 40 / 36 |
| v2-summary-strip | 1302x183 | 60 / 50 / 60 / 50 |
| v2-closing-board | 1980x1074 | 70 / 70 / 70 / 70 |
| v2-closing-header | 1821x206 | 117 / 75 / 117 / 75 |
| v2-metric-row | 937x210 | 49 / 49 / 49 / 49 |
| v2-tonight-row | 714x171 | 80 / 38 / 38 / 38 |
| v2-review-card | 689x210 | 29 / 29 / 29 / 29 |
| v2-popularity-card | 554x456 | 34 / 34 / 34 / 34 |
| v2-progress-track | 482x63 | 37 / 30 / 37 / 30 |
| v2-progress-fill | 326x51 | 30 / 22 / 11 / 22 |
| v2-bar-fill | 302x42 | 18 / 12 / 18 / 12 |

### Manual findings

- Corrected and reopened solid cream dish tile, six-cell calendar, wide title sign, centre-hung fish sign, cream bed, tan divider, flat forecast, grey slider track and five-confetti single balloon.
- Rejected first prep header export: central fit selected generator white padding. Original preserved; explicit source crop 0,0,2154,275 plus proportional bottom-aligned fit now exports blue wood only. Reopened corrected pair.
- Rays reference rectangle corrected to x584 y217 w32 h36. Rejected first navy-edged version; flat-gold replacement selected, packaged and reopened against full three-ray crop. Slightly stronger highlights remain.
- All twelve species opened: mackerel bars, cod barbel, orange plaice spots, round turbot, eel silhouette, red mullet barbels, crab claws and squid arm fan differentiated. Source style reference beyond mackerel/pollock uses the same painted mockup fish rather than claiming an unavailable species-specific mockup.
- Guest portraits 01-03 reproduce the three visible review identities; 04-06 are requested companion faces styled from them, not identities present in the mockup.
- Contours and gloss are not pixel-identical. Buttons/coins/stars/dishes retain stronger generated highlights; calendar is more upright; plate garnishes, wood grain and face details vary. Lead review required.
- Prep and closing backgrounds reconstruct occluded scenery. Selected prep correction restores the reference left stonework, fish sign, lamps and bottom wood counter, replacing the earlier railing-heavy candidate. Revealed centre, boats, sky and water remain inferred and are not pixel-identical.
- Two Mira full bodies extend cropped mockup poses. Runtime must clip at torso scale to preserve face size. Originals are1122x1402, exported1600x2000 by resampling, not native1600 painted detail.
- This manual opening ledger is not lead/Mo visual acceptance, a game capture, Unity import or runtime verification.
- Thin divider final alpha peaks at252 after antialiasing; source peak255. Transparent background verified; this is an intentional thin-line audit allowance, not an opacity correction.
- All90 tight imports opened in15 paired contacts. Crops retain the selected artwork without added transparent canvas; silhouettes and shadows may contain internal transparent pixels. Same sprite names as canonical exports; runtime uses tight-layout.json slices. Shared S1/S2 naming remains lead-owned.

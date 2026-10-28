# Service UI kit 8 - evening goals

SERVICE-UI-KIT-8 / Codex 1 (Windows app) / 2026-10-28.
Exact kit2 DEFS and accepted kit4-7 palette. Editable SVG, CairoSVG 2x exports.
Shipping sprites contain no words or numerals. All sample text/numbers are review-only.

All rects are **x,y,width,height from top left in logical SVG units**.
Multiply by 2 for texture pixels; Unity bottom-left y = height - top - rectHeight.

## Badges and stamps

Eight `v3-goal-{serve,coins,perfect,combo,upsell,gulls,walkout,critic}`:
64x64 SVG / 128x128 PNG, round ivory/brass discs without tails.
Draw entire texture at 28px on the service HUD or 40px on cream.
No live text in the badge. Glyph bounds (10,9,44,43).
`v3-goal-{tick,broken}`: 32x32 SVG / 64x64 PNG, teal/check and coral/cross.
At badge width B, draw stamp at (B/2,B/2,B/2,B/2) relative to badge top-left.
Thus 28px badge: (14,14,14,14); 40px badge: (20,20,20,20).
Stamp is inside the full badge rect, after badge art; no clipping overflow needed.
Keep status text/live progress as a second cue, never color alone.

## Sprite import contract

Sprite/Single, Full Rect mesh, centre pivot, 100PPU, sRGB, straight alpha,
alphaIsTransparency, bilinear, Clamp U/V/W, no mipmaps, no NPOT scaling,
uncompressed DefaultTexturePlatform. Preserve GUIDs on regeneration.
Simple assets preserve aspect. Sliced assets use Unity Image.Type.Sliced or
equivalent nine-slice; do not stretch a whole texture. border order L/B/R/T.

The consumer must map **2 source pixels to 1 logical unit**, including slice borders.
When implementing a UI nine-slice, use the logical table for destination corner sizes
and the doubled source-pixel table for sampling. A 200px rect alone does not halve borders.

| Sprite | Logical size | PNG size | Logical slice L/B/R/T | Source-pixel slice |
|---|---|---|---|---|
| v3-goal-serve | 64x64 | 128x128 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-coins | 64x64 | 128x128 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-perfect | 64x64 | 128x128 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-combo | 64x64 | 128x128 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-upsell | 64x64 | 128x128 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-gulls | 64x64 | 128x128 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-walkout | 64x64 | 128x128 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-critic | 64x64 | 128x128 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-tick | 32x32 | 64x64 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-broken | 32x32 | 64x64 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-board | 200x170 | 400x340 | [12, 12, 12, 34] | [24, 24, 24, 68] |
| v3-goal-row | 180x40 | 360x80 | [20, 18, 20, 18] | [40, 36, 40, 36] |
| v3-goal-row-done | 180x40 | 360x80 | [20, 18, 20, 18] | [40, 36, 40, 36] |
| v3-goal-tally | 560x360 | 1120x720 | [0, 0, 0, 0] | [0, 0, 0, 0] |
| v3-goal-allthree | 120x120 | 240x240 | [0, 0, 0, 0] | [0, 0, 0, 0] |

## Rebuild and evidence

`/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit8.py --stage 3`
Cumulative stages 1/2/3 follow the brief order. Needs CairoSVG/Pillow and existing Fredoka.
`manifest.json` is machine-readable layout/import/export truth.
`capture-provenance.json` records the three frozen source screenshots and hashes.
All three simulator Logs captures were present at capture time; no fallback used.
Desktop source is 2880x1800, downsampled once to1440x900 logical; phone is2532x1170.
Frozen captures allow reproducible crops during other owners' capture passes.
No room/HUD pixels are painted out. Composites are art evidence, not runtime gameplay acceptance.
No C#, Resources, Crew, other-kit or RestaurantService/model writes; no Git or Unity invocation.

## HUD board and rows

Board200x170; desktop top-left(16,392). Minimum200x170. Header stays34px tall.
Board title(14,7,172,22); row slots(10,36,180,40), (10,80,180,40), (10,124,180,40).
Row/row-done180x40; minimum180x40; sliced corners20x18. Done uses a soft gold wash/brass edge.
Each row local badge(5,6,28,28), text(39,5,92,30), progress(134,8,38,24).
Two text baselines at local y5 and20; title11px/state10px; progress11px centred(153,20).
Board title16px. Local badge/stamp applies the same normalized lower-right overlay rule.
Fit/localize copy within92px or use two lines; keep the progress rectangle separate.
Fit progress to its38px width:11px normally, down to9px for600/600; abbreviate larger values consistently.
Met: row-done + tick + live Goal met label. Failed: normal row + broken + live Goal lost label.
Progress remains live on failure; example8/7 means 8 lost against maximum7 (fewer than8).
Expansion proof260x210 keeps borders fixed and stretches only centre strips. Reflow rows/text separately.
No completed/failed state is inferred from colour alone. Use semantic labels and overlay shapes.

## Closing tally and all-three rosette

Tally560x360 Simple, preserve aspect; phone420x270 (all live layers at75%).
Header ribbon/three row slots/coin line/primary button room are blank shipping art.
Use goal badge40x40 and stamp20x20. Draw card first, then live badge/text/coin/button layers.
Rosette120x120 Simple at card-relative(475,-28); overflows right35/top28, parent unclipped.
Show rosette and live +1 popularity only when all three goals are met.
Each met goal pays30 coins; live coin total sums met goals (0/30/60/90), never bake total.
Pending/failed rows use relevant status stamp/text and0 reward; completed rows use tick and+30.
Care goal example fewer than8 means max7;2/7 in tally means two guests lost within budget.
For critic nights replace care badge/text/progress with critic/four-star goal.
Sample live type: title25, goal18, supporting line12, progress/reward18, total18, bonus17, button21.
Live baseline origins: goal(x95,rowY+5), supporting(x95,rowY+26); progress centre(411,rowY+24), reward centre(495,rowY+24).
Existing v3-btn-primary.png is reused only in review, at(170,295,220,44); no button asset is copied or changed.
Tally rect table (all x,y,w,h top-left logical; values scale uniformly on phone):

| Live layer | Safe rectangles |
|---|---|
| title | [38, 26, 422, 30] |
| rows | [[24, 82, 512, 48], [24, 136, 512, 48], [24, 190, 512, 48]] |
| badges | [[35, 86, 40, 40], [35, 140, 40, 40], [35, 194, 40, 40]] |
| goal_text | [[95, 88, 275, 36], [95, 142, 275, 36], [95, 196, 275, 36]] |
| progress | [[375, 92, 72, 28], [375, 146, 72, 28], [375, 200, 72, 28]] |
| rewards | [[465, 92, 60, 28], [465, 146, 60, 28], [465, 200, 60, 28]] |
| coin_badge | [29, 247, 32, 32] |
| coin_line | [69, 248, 260, 28] |
| allthree_bonus | [343, 248, 185, 28] |
| button | [170, 295, 220, 44] |
| button_text | [187, 301, 186, 29] |
| rosette | [475, -28, 120, 120] |

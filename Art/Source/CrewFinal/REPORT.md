# CREW-FINAL-ART-1

Codex 2 (WSL CLI). Source-only delivery for Claude to copy; no Assets, C#, Unity or git operations.

Review status is recorded below per group. Native UI acceptance remains separate.

**Artist delivery complete: 70 requested PNG exports, groups A–F.** Exact filenames, dimensions, RGBA, transparent corners and current hashes pass in [delivery-checks.json](delivery-checks.json).

Opened review evidence: [Rosa](review/A-rosa.png), [Ines](review/A-ines.png), [Tess](review/A-tess.png), [frames](review/B-contact.png), [icons](review/C-contact.png), [chests](review/D-contact.png), [tools 1](review/E-tools-1-contact.png), [tools 2](review/E-tools-2-contact.png), [tiles](review/E-tiles-contact.png), [tile contrast](review/E-tile-contrast.png), [card back](review/F-contact.png). Each export is shown at its native size and a 56–64px sample beside existing art.

Source methods: deterministic extraction of the three approved portraits; editable SVG extensions of the existing nautical icon/frame kit for B/C/E/F; built-in imagegen for five chest states, with the earlier crate-closed reused. [Chest prompts](chest-prompts.json), [chest source hashes/bounds](chest-checks.json), [portrait extraction](portraits-manifest.json), [frame masks](frame-checks.json). Original references remain untouched. SVG equipment is cleaner and simpler than the painted portraits/chests; its kit palette, outlines, gradients and phone contrast were visually reviewed.

Integration limit: no runtime or player-save access. Lead/Mo still own native card layout, icon sizing, rarity tint and reveal acceptance. Independently generated chest states can shift body proportions; common canvas/baseline does not guarantee a pixel-stable animated hinge. No blockers or skipped asset groups.


## Group A

DONE: 15 PNGs checked RGBA, exact 400/240/96/56 sizes and transparent margins. A-rosa.png, A-ines.png and A-tess.png opened and visually inspected at full export size plus 56px, beside Mira/Tove/Noor and the three actual 3D review sheets. Source flood key and .02 top-aligned fit match the v2 cutter. Deck variants shift headgear paint to safety orange; Ines retains her helmet shape, headlamp and navy band. No face/hair redrawing. Scar/identity readable at full size; fine scar detail naturally reduces at 56px. Reproduce with build_portraits.py. Source hashes/crop/deck differences in portraits-manifest.json.

| File | Size | Mode | Alpha |
|---|---|---|---|
| v2-portrait-rosa.png | 400×400 | RGBA | 0–255 |
| v2-portrait-rosa-deck.png | 400×400 | RGBA | 0–255 |
| v2-portrait-ines.png | 400×400 | RGBA | 0–255 |
| v2-portrait-ines-deck.png | 400×400 | RGBA | 0–255 |
| v2-portrait-tess.png | 400×400 | RGBA | 0–255 |
| v2-portrait-tess-deck.png | 400×400 | RGBA | 0–255 |
| art108-rosa.png | 240×240 | RGBA | 0–255 |
| art108-rosa-96.png | 96×96 | RGBA | 0–255 |
| art108-rosa-56.png | 56×56 | RGBA | 0–255 |
| art108-ines.png | 240×240 | RGBA | 0–255 |
| art108-ines-96.png | 96×96 | RGBA | 0–255 |
| art108-ines-56.png | 56×56 | RGBA | 0–255 |
| art108-tess.png | 240×240 | RGBA | 0–255 |
| art108-tess-96.png | 96×96 | RGBA | 0–255 |
| art108-tess-56.png | 56×56 | RGBA | 0–255 |

Hashes: `manifest-A.json`.

## Group B

DONE — B-contact.png opened and visually reviewed at native size and 64px beside original frames/Mira. 480×640 RGBA; exact original aperture and silhouette masks, zero thresholded mismatches (frame-checks.json). White warm off-white/silver, Green sea green, Mythic red/gold with four small studs. Shine is a separate transparent diagonal sweep. Original blue/purple/gold untouched; runtime acceptance remains with lead.

| File | Size | Mode | Alpha |
|---|---|---|---|
| art108-frame-white.png | 480×640 | RGBA | 0–255 |
| art108-frame-green.png | 480×640 | RGBA | 0–255 |
| art108-frame-mythic.png | 480×640 | RGBA | 0–255 |
| art108-frame-mythic-shine.png | 480×640 | RGBA | 0–191 |

Hashes: `manifest-B.json`.

## Group C

DONE — C-contact.png opened and visually reviewed: each 256px and 64px export beside v2 coin, anchor and Mira. Five distinct silhouettes retain navy outlines, warm brass/cream, sea-green, deep-red and soft gradient shading. All 10 RGBA files have clear alpha margins; no lettering. Editable SVG kit extensions included. Native acceptance remains with lead.

| File | Size | Mode | Alpha |
|---|---|---|---|
| v2-icon-token.png | 256×256 | RGBA | 0–255 |
| v2-icon-token-64.png | 64×64 | RGBA | 0–255 |
| v2-icon-blueprint.png | 256×256 | RGBA | 0–255 |
| v2-icon-blueprint-64.png | 64×64 | RGBA | 0–255 |
| v2-icon-star.png | 256×256 | RGBA | 0–255 |
| v2-icon-star-64.png | 64×64 | RGBA | 0–255 |
| v2-icon-focus.png | 256×256 | RGBA | 0–255 |
| v2-icon-focus-64.png | 64×64 | RGBA | 0–255 |
| v2-icon-renown.png | 256×256 | RGBA | 0–255 |
| v2-icon-renown-64.png | 64×64 | RGBA | 0–255 |

Hashes: `manifest-C.json`.

## Group D

DONE — D-contact.png opened and reviewed: all six 512×512 exports plus true 64px samples beside existing v2 coin/anchor/Mira. Crate, iron-banded sea and navy/gold/red captain pairs have distinct tier silhouettes, raised lids, empty softly lit interiors, no lettering, clean transparent margins. Built-in imagegen made five images from style/closed-state references; existing crate-closed reused. Generated alpha preserved, export-only crop/resize to 512px with common bottom baseline480; body proportions can shift slightly between independently generated states, so native reveal acceptance remains separate. Full prompts chest-prompts.json, source hashes/bounds chest-checks.json, originals generated/.

| File | Size | Mode | Alpha |
|---|---|---|---|
| v2-chest-crate-closed.png | 512×512 | RGBA | 0–255 |
| v2-chest-crate-open.png | 512×512 | RGBA | 0–255 |
| v2-chest-sea-closed.png | 512×512 | RGBA | 0–255 |
| v2-chest-sea-open.png | 512×512 | RGBA | 0–255 |
| v2-chest-captain-closed.png | 512×512 | RGBA | 0–255 |
| v2-chest-captain-open.png | 512×512 | RGBA | 0–255 |

Hashes: `manifest-D.json`.

## Group E

DONE — E-tools-1-contact.png, E-tools-2-contact.png and E-tiles-contact.png opened and reviewed after contrast/knife revisions, all native exports plus64px samples beside existing v2 art. E-tile-contrast.png also opened: all14 tools on each of six64px tiles. 28 tool PNGs (256/64), six192px tiles, RGBA clear alpha margins; no lettering. Neutral steel-blue surfaces keep silhouettes visible across rarity backgrounds; short broad bait knife differs from long thin fillet knife. Tile gradients use exact frame colours, including original blue/purple/gold. Editable SVG sources included. Native acceptance remains with lead.

| File | Size | Mode | Alpha |
|---|---|---|---|
| v2-tool-rod.png | 256×256 | RGBA | 0–255 |
| v2-tool-rod-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-reel.png | 256×256 | RGBA | 0–255 |
| v2-tool-reel-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-net-needle.png | 256×256 | RGBA | 0–255 |
| v2-tool-net-needle-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-bait-knife.png | 256×256 | RGBA | 0–255 |
| v2-tool-bait-knife-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-gloves.png | 256×256 | RGBA | 0–255 |
| v2-tool-gloves-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-gaff.png | 256×256 | RGBA | 0–255 |
| v2-tool-gaff-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-fillet-knife.png | 256×256 | RGBA | 0–255 |
| v2-tool-fillet-knife-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-boots.png | 256×256 | RGBA | 0–255 |
| v2-tool-boots-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-winch-handle.png | 256×256 | RGBA | 0–255 |
| v2-tool-winch-handle-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-oil-can.png | 256×256 | RGBA | 0–255 |
| v2-tool-oil-can-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-toolbelt.png | 256×256 | RGBA | 0–255 |
| v2-tool-toolbelt-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-compass.png | 256×256 | RGBA | 0–255 |
| v2-tool-compass-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-binoculars.png | 256×256 | RGBA | 0–255 |
| v2-tool-binoculars-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-charts.png | 256×256 | RGBA | 0–255 |
| v2-tool-charts-64.png | 64×64 | RGBA | 0–255 |
| v2-tool-tile-white.png | 192×192 | RGBA | 0–255 |
| v2-tool-tile-green.png | 192×192 | RGBA | 0–255 |
| v2-tool-tile-blue.png | 192×192 | RGBA | 0–255 |
| v2-tool-tile-purple.png | 192×192 | RGBA | 0–255 |
| v2-tool-tile-gold.png | 192×192 | RGBA | 0–255 |
| v2-tool-tile-mythic.png | 192×192 | RGBA | 0–255 |

Hashes: `manifest-E.json`.

## Group F

DONE — F-contact.png opened after rope/anchor refinement, full480×640 and64px sample beside original blue frame, v2 anchor and Mira. Navy face-down back, diagonal rope binding, central anchor with open ring and subtle sea-line pattern, no lettering. RGBA with transparent rounded outside margins; editable SVG included. Native acceptance remains with lead.

| File | Size | Mode | Alpha |
|---|---|---|---|
| v2-card-back.png | 480×640 | RGBA | 0–255 |

Hashes: `manifest-F.json`.

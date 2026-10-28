# Kit 5 - between-night choice cards

NIGHT-CARDS-ART-1 / Codex 1 (Windows app) / 2026-10-28.
Sixteen transparent sprites, authored as SVG geometry and exported at 2x with
CairoSVG. Exact kit-2 DEFS, kit-2/4 navy/teal/coral and paper/brass/steel/wood
materials. Shipping SVGs and PNGs contain no words or numerals. All lettering
in review images simulates live UI; sample effects are illustrative copy.

## Files and sizes

Source SVGs live here; matching PNGs and Unity metas are in `Assets/Art/UI/`.
Names below have the `v3-ncard-` prefix in Assets and `ncard-` prefix here.

| Assets | SVG viewBox | PNG pixels | Purpose |
| --- | --- | --- | --- |
| gadget, night, dish | 240 x 320 | 480 x 640 | Teal wrench, coral moon, brass cloche ribbons |
| glow | 288 x 368 | 576 x 736 | Soft brass selection halo behind a card |
| warming-lamp, plate-rack, service-bell | 256 x 256 | 512 x 512 | Gadgets |
| gull-net, quick-shoes, second-pan | 256 x 256 | 512 x 512 | Gadgets |
| ferry, critic, festival, rain | 256 x 256 | 512 x 512 | Night events |
| catch, ice-cream | 256 x 256 | 512 x 512 | Dishes |

`manifest.json` lists every exact file, size, GUID, PNG SHA256 and rectangle.
`audit.json` records structural/import/preservation checks. `preservation.json`
holds hashes of incumbent source/art references, not backup copies.

## Safe rectangles and live layout

Coordinates are `(x, y, width, height)` from the **top-left of the 240 x 320
card viewBox**, including its transparent padding. Multiply all values by 2
for PNG pixels. Existing day-card title/body rectangles are retained exactly.

| Live region | SVG units | PNG pixels |
| --- | --- | --- |
| Title | 25, 66, 190, 34 | 50, 132, 380, 68 |
| Body | 30, 213, 180, 73 | 60, 426, 360, 146 |
| Illustration window | 24, 107, 192, 102 | 48, 214, 384, 204 |
| Centered square illustration slot | 69, 107, 102, 102 | 138, 214, 204, 204 |
| Kind label, after the baked symbol | 80, 34, 93, 20 | 160, 68, 186, 40 |

Fit the **whole** illustration texture in the square slot, preserve aspect,
and center it at `(120,158)`. Its internal transparent breathing room is
intentional. At a 150 px card width the slot is 63.75 px square, matching the
64 px inspection proofs. Do not stretch art across the wide window.

Use ivory text on the navy title band and navy body text. Review samples use
Fredoka SemiBold: title 17.5 logical units, body 16, kind 13. At 150 px width
these render at approximately 10.9, 10 and 8.1 px respectively. Center title
and body text horizontally; wrap body to the reserved width. Three short
body lines are demonstrated, with room for a fourth. Localized copy must be
fitted/wrapped within these rectangles. Keep gameplay values in live text.
Kind labels use ivory with a thin navy outline so brass stays legible.

For a bottom-left Unity coordinate system, convert a region with
`yBottom = 320 - yTop - height`; scale by the displayed width divided by 240.
The full card rect should retain a 3:4 aspect ratio.

## Slice borders and importer contract

**All sixteen slice borders are `(0,0,0,0)` in PNG pixels** (left, bottom,
right, top). Use Image Type **Simple**, preserve aspect; these are fixed
composition cards like the day cards, not scalable panel backgrounds.
Nine-slicing would deform the pin, ribbon, window and bottom ornament.

Metas follow the existing v3-card importer: Sprite/Single, 100 PPU, centered
pivot, Full Rect mesh, sRGB, alpha transparency, bilinear filtering, Clamp,
no mipmaps, NPOT scaling disabled, uncompressed default platform. Existing
GUIDs are retained on regeneration. No Resources copies are made.

Place the glow **behind** a card, centered on the same rect, at
`cardWidth * 288/240` by `cardHeight * 368/320`. It adds 24 logical units on
each side; at a 150 x 200 card its rect is 180 x 230, offset -15,-15. Use
normal alpha blending and preserve the full glow rect. Do not crop its
padding or let it receive pointer input. No selection animation is baked in.

## Evidence and regeneration

The combined [contact sheet](review/contact-sheet.png) shows all three 150 px
cards with final sample illustrations and live lettering on cream and night,
plus all twelve illustrations at actual 64 px on both backgrounds. It is also
published as `docs/screens/ui-v3/art-kit-5.png`.

- `review/cards-cream.png`, `cards-night.png`: larger composites plus actual
  150 px selected cards.
- `review/cards-safe-rects.png`: final composition with safe-area overlays.
- `review/contact-cream.png`, `contact-night.png`: separate background crops.
- `review/ncard-*-review.png`: each illustration at 224 px and actual 64 px,
  on both backgrounds.
- `review/frames-*.png`: item-1 proofs using incumbent kit-2/4 art before new
  illustration work, retained as the ordered review trail.
- `visual-review.json`: personally opened images with hashes. Reopen any
  image whose hash changes; a generator run cannot grant visual acceptance.

Run from the project root in Ubuntu WSL:

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit5.py --stage 3
```

Requires CairoSVG and Pillow plus the existing Fredoka SemiBold font.
Stages are cumulative: 1 frames/glow, 2 all art and final proofs, 3 complete
delivery including this README. Builders from other kits are read, never
imported/executed. Only assigned kit-5/night-card output paths are written.

All originals and proof PNGs were opened before item completion. Structural
checks and small-scale visual reviews passed. Native Unity import, actual
card-pick interaction, localization and runtime acceptance remain with Claude;
no Unity invocation, C# change, Resources write, Git operation or commit was
performed for this art task.

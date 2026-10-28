# Service art, kit 4

19 transparent v3 assets for the three-minute service night. Editable SVG originals
live here; production PNGs and fresh Unity import GUIDs live in `Assets/Art/UI/`.
All assets are text-free. Labels and sample numbers appear only in review evidence.

Regenerate from the project root in WSL:

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit4.py
```

`--stage 1`, `2`, `3`, `4` exports cumulative priority groups. Existing GUIDs are
preserved. The generator reads the exact kit-2 `DEFS` literal without executing
kit-2, uses the same palette, CairoSVG 2x export, `v3-card.png.meta` importer
template, manifest and contact-sheet pipeline. No Unity or Git invocation.

## Sizes and use

Every square asset below has a **128x128 viewBox and 256x256 PNG**, with zero
slice borders. Keep square when drawing; the old staff-task rectangles in
`TaskIcon` are rectangular and will need a drawing adjustment by the runtime owner.
Stroke/detail widths are at least3 viewBox units before downsampling; SVG geometry
has no raster dependencies, lettering or numerals.

| Production key | Meaning / silhouette | Group |
| --- | --- | --- |
| `v3-svc-seat` | Chair: seat a party | 1 |
| `v3-svc-order` | Order pad: take the order | 1 |
| `v3-svc-pour` | Pitcher and drop: pour | 1 |
| `v3-svc-plate` | Cloche above stacked plates: ready to carry | 1 |
| `v3-svc-wipe` | Folded cloth and wipe strokes: clear the table | 1 |
| `v3-svc-pay` | Two brass coins: collect payment | 1 |
| `v3-svc-cook` | Pan and flame: cook | 1 |
| `v3-svc-repair` | Open wrench: repair | 1 |
| `v3-svc-wash` | Plate and large water drop: wash | 1 |
| `v3-svc-queue` | Coral enamel badge; centre reserved for live queue number | 2 |
| `v3-svc-ring` | Thin teal annulus; transparent centre | 2 |
| `v3-svc-combo` | Coral burst behind live `Combo!` | 3 |
| `v3-svc-perfect` | Brass/gold halo behind a dish | 3 |
| `v3-svc-burnt` | Solid smoke puff with broad curls | 3 |
| `v3-svc-gull` | Gull on pointed paper: table warning | 3 |
| `v3-svc-upsell-drink` | Teal stemmed drink in a thought bubble | 3 |
| `v3-svc-upsell-dessert` | Coral cake and cream in a thought bubble | 3 |
| `v3-svc-coins` | Three-coin pickup, transparent around the pile | 3 |

Group4 is `v3-svc-clock-pill`: **320x96 viewBox, 640x192 PNG**. It contains a
fixed teal pause cell and brass divider, with an empty paper clock cell.

The nine task markers and gull warning share a paper disc and downward pointer.
Align the pointer tip `(64,121)` in viewBox space with the intended anchor above
the table; normalized tip `(0.5,0.9453125)` from top left. The importer keeps the
kit's centre pivot. Thought bubbles use separate small circles instead of a pointer.

## Slices and live text

`manifest.json` uses kit-2 conventions: `slice_pixels` is **PNG/source pixels,
left/bottom/right/top**; `safe_text_svg_units` is **x/y/width/height, top left**.
Multiply safe rectangles by2 for source PNG pixels, or scale them with the image.
All unspecified safe text rectangles are null because those assets carry a glyph.

| Asset | Slice border in source pixels (L/B/R/T) | Safe live text in viewBox units |
| --- | --- | --- |
| queue | `(0,0,0,0)` | `(35,34,58,58)` |
| combo | `(0,0,0,0)` | `(21,44,86,39)` |
| clock-pill | **`(200,86,86,86)`** | clock **`(106,19,167,50)`**; pause hit `(9,9,69,69)` |
| all other assets | `(0,0,0,0)` | none |

For the clock pill the same borders in viewBox units are `(100,43,43,43)`.
Keep the left100 units fixed, including pause and separator. Stretch only the blank
horizontal clock cell. Keep logical height96 before applying a uniform display
scale; vertical stretching would distort the pause symbol. Minimum slice geometry
is width143 and height86 logical units; use a practical width320 or wider to leave
room for the clock. At a stretched width448 the clock safe rectangle becomes
`(106,19,295,50)`; its right inset47 stays fixed. The examples show live `2:14` and
`3 left` at widths320 and448, plus a224x48 phone-sized display.

Keep the pause **input target at least44 screen pixels** even if its painted cell
is smaller after scaling. The whole pill is artwork, not a button hierarchy. The
runtime owner creates the pause hit area and live clock label separately.

For existing `CoastalCanvas.KitSliceV3`, pass explicit source-pixel borders as for
kit-2 and retain its image multiplier2. Unity importer borders are also set for
Sprite consumers. Runtime `Sprite.Create` users must pass borders explicitly.

Draw patience as a square **unsliced** image. A full annulus can be the dim track;
overlay a second copy using `Image.Type.Filled`, `Radial360`, top origin and
clockwise fill, with live patience as `fillAmount`. Teal band is6 logical units
inside a10-unit navy band; centre radius47 is completely transparent. Tint the
active copy for warning states. Never stretch the annulus into an ellipse.

The perfect halo has a transparent centre radius36 and a3-unit navy edge for
contrast over warm gold floors. Put the dish in front of it.
Combo is a live-text backplate and can display larger than a32px task marker;
`functional-preview.png` demonstrates its text at128px. Queue samples show live
numbers at actual32 and48px. No label is baked into the production assets.

## Evidence and verification

- [Cream and dark night contact](../../../../docs/screens/ui-v3/art-kit-4.png)
- [Cream panel](review/contact-cream.png), [night panel](review/contact-night.png)
- [Live text, radial-fill and nine-slice proof](review/functional-preview.png)
- Each `review/svc-*-review.png`: cream/night presentation, actual28/32/36px
  composites, and a nearest-neighbour4x loupe of the32px raster.
- Each `review/svc-*-service-32.png`: separate unchanged service crop with an
  exact32px icon bounding box (the clock pill is32px wide, preserving aspect;
  its practical size is shown separately in the functional proof).
- `review-evidence.json`: capture/crop provenance and review-image SHA256 hashes.
- `audit.json`: export invariants and byte-preservation checks.
- `visual-review.json`: inspected image hashes and human-visible review notes.
- `delivery-check.json`: final reproducibility, GUID/importer, file and hash audit.

The requested scratch capture was absent. As permitted in the brief, composites
use `docs/screens/restaurant-mood/r157/day-service-1440.png`, native dimensions
1996x1248, crop `(1000,330,1224,474)`. Source pixels are neither tinted nor darkened.
Dark background review uses `#182f3a`; production assets remain transparent.

The three kit-2/template dependencies stayed byte-identical. The separately owned
`VoyageRestaurantUi.cs` changed during this run; its baseline remains recorded and
the audit reports that observation instead of resetting or overwriting the file.

Every production PNG, individual review card, separate32px composite, final
contact sheet/panels and functional proof was opened and inspected. The art
audit is separate from Unity import/runtime/physical-phone acceptance. No C#,
Resources, other kit, Crew, Codex2 props or RestaurantService files were edited.
No commit; no Git commands; no Unity execution. Runtime wiring belongs to Claude.

# Service kit 6 - kept cards, the critic, rain

SERVICE-UI-KIT-6 / Codex 1 (Windows app) / 2026-10-28.
SVG geometry, exact kit-2 DEFS and kit-4/5 palette; CairoSVG exports at 2x.
Shipping art has no baked words, numerals, scores or filled rating stars.
Review lettering, sample rating and kit-5 illustration overlays are evidence only.

## Chips - item 1

| Key (in Assets/Art/UI) | SVG viewBox | PNG pixels | Use |
| --- | --- | --- | --- |
| v3-chip-gadget | 96x96 | 192x192 | Teal rim, blank cream face |
| v3-chip-dish | 96x96 | 192x192 | Brass rim, blank cream face |
| v3-chip-night | 96x96 | 192x192 | Coral rim, blank cream face |
| v3-chip-new | 40x40 | 80x80 | Wordless brass starburst |

All rectangles here are **x/y/width/height from top-left, in SVG units**.
Double for source PNG pixels. The blank cream face is a circle centred at
`(48,47)`, radius `33.5`. Fit the **whole** kit-5 illustration texture inside
`(14.4,13.4,67.2,67.2)` (70% of chip width); keep its own transparent padding.
At a 40px chip the illustration rect is `(6,5.5833,28,28)`.

For the last-kept flag, draw the entire burst texture in a 14x14 display rect
at `(chipLeft+31,chipTop-5)` relative to a 40px chip. Reserve five pixels of
overflow above/right and disable clipping there. Layer chip, illustration,
then burst. The proof includes all three actual40px on the sampled cream rail
and night sea, plus one burst and the actual rail-right crop. Chip colours
identify kind; the separately drawn illustration identifies the actual card.

## Critic - item 2

| Key | SVG viewBox | PNG pixels | Use |
| --- | --- | --- | --- |
| v3-svc-critic | 128x128 | 256x256 | Kit-4 pointed paper pin, beret, round glasses, notebook |
| v3-svc-critic-review | 320x200 | 640x400 | Torn newspaper clipping, beret seal and five empty star slots |

Keep the critic pin square, usually **32x32 display pixels** (28/32/40 proofs).
Its tip is `(64,121)`, normalized `(0.5,0.9453125)` from top-left, matching kit4.
Keep it anchored over the critic's table throughout the night. It conveys
presence independently of a changing order/task marker; runtime owns placement.

The clipping's live rating slots are:

| Star, left to right | SVG rect | Source PNG rect |
| --- | --- | --- |
| 1 | (88,35,32,32) | (176,70,64,64) |
| 2 | (128,35,32,32) | (256,70,64,64) |
| 3 | (168,35,32,32) | (336,70,64,64) |
| 4 | (208,35,32,32) | (416,70,64,64) |
| 5 | (248,35,32,32) | (496,70,64,64) |

Each empty five-point outline has outer radius14, inner/outer ratio0.46,
starts at twelve o'clock, and is centred in its slot. Overlay a filled gold
five-point star of outer radius13 in the same centre (2-3px slot inset).
The proof fills four and leaves the fifth empty. Keep any gameplay score live.

**Live body safe rect `(28,101,264,48)`**, PNG `(56,202,528,96)`.
Use one centred navy line, e.g. Fredoka SemiBold15 at logical320px card width.
Fit/localize the line within264px, vertically centred at125; sample copy is
only in review images. For Unity bottom-left coordinates use
`yBottom = viewBoxHeight - yTop - height` before applying display scale.

## Import and draw contract

Chips, burst, pin and clipping: Image Type **Simple**, preserve aspect.
**All slice borders are `(0,0,0,0)` source pixels, L/B/R/T. No nine-slicing.**
Sprite/Single, Full Rect mesh, centred pivot,100PPU, sRGB, straight alpha with
alpha transparency enabled, bilinear filtering, no mipmaps, no NPOT scaling,
uncompressed default platform. Clamp except the repeating rain tile, if present.
GUIDs are retained on regeneration; runtime-only resources are not copied here.
Do not atlas the rain tile when repeating UVs across its whole texture.

## Regeneration and evidence

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit6.py --stage 3
```

Requires CairoSVG/Pillow and the existing Fredoka font. Stages1/2/3 are cumulative
in brief priority order. Builders from older kits are parsed/read, never imported.
Only assigned kit6 paths are written. `manifest.json` contains exact sizes,
safe rectangles, GUIDs, wraps and hashes; `audit.json` checks structure/imports
and incumbent hashes. `visual-review.json` records personally opened image hashes;
regeneration cannot itself grant visual approval.

Review files `01-*` show actual40px composited and blank chips; `02-*` show
the actual32px service pin, sample live rating/line and blank shipping critic art.
Capture: sibling `Catchline-ui2-sim/Logs/uiv2-native/day-service-late-1440.png`,
actual2880x1800 pixels. Native logical1440x900 is obtained by2x downsampling.
Room crop source pixels `(1240,450,2776,1474)` gives1536x1024, or768x512 logical.
The unchanged source includes existing order pins. Crop pixels are not tinted
or darkened. Phone capture `day-service-late-844.png` is2532x1170 and was inspected
as context; no rail is fabricated on that different layout.

Art evidence is separate from Unity import, gameplay wiring and native acceptance,
which remain Claude's work. No C#, Resources, other-kit, Crew, Restaurant model
or RestaurantService writes, no Git commands/commit and no Unity execution.


## Rain - item 3

| Key | SVG viewBox | PNG pixels | Wrap |
| --- | --- | --- | --- |
| v3-fx-rain | 256x256 | **512x512** | Repeat U/V |
| v3-fx-rain-splash | 256x32 | **512x64** | Clamp |

These requested512px dimensions are the final textures. Both are2x exports:
the splash's eight logical32x32 cells become64x64 PNG frames. No extra scaling
or duplicate texture is needed. Both have zero slice borders; use Simple/UVs.

Rain:42 soft pale ice/steel streaks per tile, falling **15 degrees from vertical,
down-left**. Main stroke authored alpha is0.22-0.31; two are0.40, with much
fainter soft shoulders. Fully transparent between streaks; no fog/mist/wash.
Use normal straight-alpha blending, **white tint alpha1**; alpha is baked into
each streak. Intended repeat size **256x256 logical/display pixels** at1440x900,
equivalent to512x512 source-capture pixels. Proof uses exactly3x2 unscaled PNG
tiles over the1536x1024 source crop, displayed at768x512 for the service-scale
comparison. Keep tile aspect square; repeat UVs instead of stretching one tile
over the room. Suggested scroll direction UV(-0.067,+0.25) tiles/second in
top-left coordinates; for bottom-left UV flip the V sign. Speed is runtime-owned.

Draw rain above the room but below service pins, labels, dialogs and the crew
rail; mask it to the room/deck viewport. Disable raycast/input on rain and
splashes. The conservative proof also puts rain over the sample critic/order
pins, so their legibility is visible even with that layering. Do not atlas the
tile or sample only a subrect when repeating. Repeat importer is supplied.

Splash: eight64x64 source-pixel frames, left-to-right. Exact source rects:
`(0,0,64,64)`, `(64,0,64,64)`, `(128,0,64,64)`, `(192,0,64,64)`,
`(256,0,64,64)`, `(320,0,64,64)`, `(384,0,64,64)`, `(448,0,64,64)`.
Per-frame contact centre **PNG(32,42)**, logical(16,21), normalized(0.5,0.65625)
top-left; bottom-left normalized(0.5,0.34375). Keep contact anchored to the
puddle as the elliptical ring expands. Display32x32 logical pixels per frame,
or uniformly smaller for depth; retain the transparent cell padding. Atlas UV
width1/8, full height; inset each UV sample by half a source texel when using
bilinear UV quads to prevent frame bleed. The supplied importer is Sprite/Single
for the entire strip; runtime owns frame UV selection, no auto-slicing expected.

Suggested **0.04s/frame,0.32s one-shot**; frame8 is fully transparent. Spawn
sparingly on visible deck/puddle positions with staggered times and small scale
variation; do not synchronize the strip across the floor or loop one fixed ring.
The eight-frame proof includes actual strip pixels and separate enlarged frames.

`review/03-rain-tiled-3x2.png` is the exact512px3x2 overlay; `03-rain-and-splashes.png`
compares dry/rainy at actual service scale and shows the strip/deck samples;
`03-rain-tile-blank.png` shows the raw tile over cream/night; `03-splash-frames.png`
shows every frame. `review/contact-sheet.png` is byte-identical to
`docs/screens/ui-v3/art-kit-6.png`, joining all three items without downscaling
the40/32px evidence. Final manually opened images are hashed in visual-review.json.

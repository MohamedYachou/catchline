# Service kit 7 - the deal, night announcement, timeline

SERVICE-UI-KIT-7 / Codex 1 (Windows app) / 2026-10-28.
Editable SVG geometry, exact kit2 DEFS and accepted kit5/6 palette.
CairoSVG exports at2x; shipping assets have no words or numerals.
Review labels and sample content simulate separate live UI layers only.

## Item 1 - card deal

| Sprite in Assets/Art/UI | SVG viewBox | PNG pixels |
| --- | --- | --- |
| v3-ncard-back |240x320|480x640|
| v3-ncard-shine |240x320|480x640|

Back matches kit5 frame alpha exactly, including its outer brass outline,
ivory inset and4-unit downcast shadow. Neutral navy wave field with a brass
eight-point compass; no card-kind information appears before the flip.
All coordinates below are top-left SVG units. Double them for PNG pixels.
Flip about the **full rect centre(120,160)**. Keep back and face on the same
240x320 rect; horizontal scale only, preserve height and position. Swap sides
while edge-on; use abs(scaleX) on each side so text never becomes mirrored.
Proof sequence is back1,.5,.1 then face.5,1 at actual150x200px.

Suggested runtime choreography (not implemented here): stagger landings by
70-100ms, short settle, then flip each card over about240-300ms. Keep input
ready once faces are readable; reduced motion can reveal without a flip.
Shine uses normal alpha, white tint at1, max alpha<=.34. Draw above card art
and below live text. Slide its rect from -240 to+240 logical units relative
to the card, once in about400ms; keep its240x320 size and clip the moving layer
to the **face rounded rect(12,8,216,304), radius16**. Sprite edges alone do not
clip a translated sweep. At150px card width these offsets become -150/+150px.
Disable input/raycast on the sweep; no additive blend, loop or opaque wash.

## Import contract

Every sprite: Image Type Simple, preserve aspect, zero slice borders L/B/R/T.
Sprite/Single, Full Rect, centre pivot,100PPU, sRGB, straight alpha with alpha
transparency, bilinear, Clamp, no mipmaps or NPOT rescale, default uncompressed.
Regeneration preserves GUIDs. No Resources copies. Runtime wiring and native
gameplay/touch acceptance remain Claude's scope; static proofs do not prove them.

## Regeneration and evidence

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit7.py --stage 3
```

Requires existing CairoSVG/Pillow environment and Fredoka SemiBold.
Stages are cumulative in brief order; older builders are read, never imported.
`manifest.json`: dimensions, GUIDs, safe rects and hashes. `audit.json` checks
source/export/import/preservation; `visual-review.json` separately records
personally opened images. Regeneration cannot itself approve an image.
Item1 proofs: `review/01-reveal-150px.png`, `01-back-and-shine.png`.
No C#, Resources, other-kit, Crew or Codex2 art writes; no Git/Unity invocation.


## Item 2 - night-start event ribbon

`v3-event-banner`:640x200 SVG,1280x400 PNG. Fixed3.2:1 aspect, no nine-slice.
Draw640x200 desktop or420x131.25 phone (uniform scale0.65625).
The left window is blank cream. Fit the **whole** kit5 ferry/critic/festival/rain
texture in its illustration slot; preserve its internal transparent padding.

| Region | Top-left SVG x,y,width,height | PNG pixels |
| --- | --- | --- |
| Illustration |52,38,124,124|104,76,248,248|
| Title |227,55,354,40|454,110,708,80|
| One line |227,104,354,30|454,208,708,60|

Window circle centre(114,100), radius69; source PNG centre(228,200),radius138.
The124x124 illustration square has7 units of inset from the circle bounding
square. Kit5's internal padding keeps all four illustrations inside the circle.
Clip any different/new art to the window circle.
Title: navy Fredoka SemiBold30 logical units; line: navy19. At420px banner
width they become19.69/12.47px. Left-align to227 and vertically centre in
the safe rectangles. These are live text layers; fit localized copy to width354.
Use one line for the subtitle; shorten or reduce type to a readable bound.
For Unity bottom-left, yBottom=200-yTop-height. At phone scale multiply all
positions/sizes by420/640. Safe rects include the full text ink, not just baseline.

Suggested reveal: settle the banner below the top bar as doors open, then
release it after the announcement. Runtime owns event timing and dismissal.
Keep it clear of the top-bar controls and staff rail, above the room. The
review's room location is an art-compositing proof, not final gameplay placement.
`02-banner-service-420-640.png` shows both display widths over unmodified crops
of the supplied2880x1800 service image at2source pixels per display pixel.
`review-evidence.json` records crop bounds. `02-banner-four-events.png` shows
all four kit5 illustrations; `02-banner-safe-rects.png` shows live layout.
The requested simulator Logs files vanished during a new capture pass.
Evidence follows saved `docs/screens/ui-v2/day-service-late-1440.png`, frozen
as `review/source-service-late-1440.png` (2880x1800). It has the same inspected
room/top-bar composition; no byte-equivalence to the vanished file is claimed.
Actual source hash and fallback provenance are recorded in review-evidence.json.


## Item 3 - upcoming events on the evening curve

| Sprite | SVG viewBox | PNG pixels | Display width |
| --- | --- | --- | --- |
| v3-tl-ferry |48x56|96x112|22-26px, preferred24px|
| v3-tl-critic |48x56|96x112|22-26px, preferred24px|
| v3-tl-glow |80x88|160x176|40px when pin width24px|

Ivory pointed brass-rim discs: ferry hull/cabin/windows versus critic beret and
spectacles. Keep aspect48:56. A24px-wide pin is24x28 display pixels.
Pin tip **(24,53)**, normalized top-left(0.5,0.9464285714); Unity bottom-left
normalized pivot equivalent(0.5,0.0535714286). Importer remains centre pivot;
set the UI anchor/offset explicitly. Tip at24px display width is(12,26.5).
Place this tip at the event's due-time point on the existing evening curve.
Do not confuse the pin's bottom edge with its tip:3 logical units of padding.
If the full-rect centre is used, offset centre from desired tip by(0,-25)
SVG units, or(0,-12.5) screen pixels at24px width (top-left y positive down).

Halo uses normal alpha, authored max0.40. Match its logical scale to the pin;
its pin rect is(16,16,48,56), so halo top-left=pin top-left-(16,16) logical
units, or-(8,8) pixels at24px pin width. Body centre(40,39) aligns to pin's
(24,23); halo tip reference(40,69) aligns to pin tip. Draw behind the pin,
above the top-bar background, disable raycast/input. Last10 seconds before
arrival: show halo; a restrained opacity pulse is optional. Remove the halo
when the event arrives. Runtime owns the countdown and removal of the pin.
Reduced motion: steady halo. These small markers announce future events;
the larger kit6 critic pin continues to identify the seated critic.

Keep current-time flag, hour labels and controls clear. Multiple nearby events
need runtime spacing/collision handling while preserving due-time tip anchors;
show distinct markers or a deliberate stack, never silently hide an event.
Proof positions are illustrative, not a new schedule or a runtime layout change.
Actual source crop(900,0,1560,160) downsamples2:1 to330x80. Both24px pins are
shown on that real bar with/without halo, plus22/26px checks. Sample due tips
in this crop are(240,33),(280,37); existing21:00 flag remains unobstructed.
No bar repainting, tint or artificial widening. `03-timeline-source.png` shows
the exact exported textures. Final contact `review/art-kit-7.png` is mirrored
at `docs/screens/ui-v3/art-kit-7.png`; proof sections retain their actual sizes.

Independent check (does not import or execute any builder):
`/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/kit-7/verify_delivery.py`
`delivery-audit.json` records export dimensions/alpha padding/importers, unique
UI-folder GUIDs,261 incumbent hashes and all16 personally opened image hashes.
`reproducibility.json` records a second full stage3 run with identical generated
file hashes, including sprite metas and both final contact copies.

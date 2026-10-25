# FIRST-CATCH-ART-1

Codex 2 (WSL CLI). A–E artist delivery complete. Nine transparent straight-alpha RGBA PNGs are saved here and copied byte-for-byte to `Assets/Art/UI/Crew/`. No meta files, script files, scenes, audio, integration changes or git operations.

## Assets

| Group | PNG | Canvas | Notes |
|---|---|---|---|
| A | fx-stamp-new | 256×256 | Coral #E0603A NEW, outlined Fredoka glyphs, -11° rotation, irregular ink edge and restrained pinhole texture. Legible at64px. |
| B | catch-card | 512×640 | Cream #F4EBDA, navy outline, brass corners, empty opaque sea-blue upper window, plain lower text band. |
| C | fx-splash | 256×256 | Centred teal crown with white crests and three airborne droplets; no fish. |
| C | fx-droplet | 48×48 | Single teal drop, ivory reflection, navy outline. Inset to avoid edge alpha fringe. |
| D | goal-jar-0..4 | 128×128 each | Empty, quarter, half, three quarters, full with overflow and glint. Same glass contour, mouth, baseline and reflections throughout. |

## Card placement contract

All pixel coordinates below use the512×640canvas and **top-left origin**.

- Window rect **(x40, y44, w432, h344)**, rounded radius18; navy6px stroke centred on boundary. This is an opaque sea-blue window, not an alpha hole. Draw the fish ABOVE the card; drawing it behind the card will hide it.
- Fish safe inset: **(46,50,420,332)**, rounded radius15, respecting any runtime clip. A contain-fit352×244fish was used for the separate scale study.
- Bottom-left origin window rect: **(40,252,432,344)**. Normalized bottom-left rect: **(.078125,.39375,.84375,.5375)**.
- Name/weight safe band: **(56,422,400,152)**. The sample review puts name centre(256,465), weight centre(256,523); no sample text is baked into the export.
- Stamp is a separate transparent layer; scale/position/timing are Claude’s. The static study uses116px stamp at(365,22)over the top-right window.

## Glass and small-size use

Jar glass uses translucent sea tint, opaque navy outline and pale reflections. Preserve alpha rather than flattening it to a background. All states share the same native SVG body contour, rim and reflections; only coins and the full-state overflow/glint change. Fit all states using the same128pxcanvas without trimming or per-state rescaling. Confirmed at actual64px on both backgrounds; glint is intentionally restrained against cream. Fill states encode progress geometrically as well as by gold colour.

## Source and rendering

This extends the existing native SVG UI icon family from Art/Source/CrewFx/svg, rather than using image generation. Editable SVGs for all nine assets are in `svg/`; lettering is actual path outlines from supplied Fredoka-Medium.ttf, with no runtime font dependency. Sources reference the existing rank ribbon, burst, glow, card/pill styling and Design/Style palette; brief-specific cream/coral values take precedence. Exports use CairoSVG at3×/4× with Lanczos downsampling. No generator script file was created, per brief. SVG files can be rendered at their declared canvas sizes; retain supersampling for the same antialias character. No existing art was overwritten.

## Evidence and checks

- `review/sheet.png`:1920×1200, all A–D on exact navy#1C3A5A and cream#F4EBDA; A and all D also at actual64px. Opened and inspected; NEW remains legible, five fill states distinct, brass corners outside the window, text band clear.
- `review/assembly.png`: static card/fish/stamp scale study, opened and inspected. Reuses existing Assets/Art/UI/fish-cod.png only as the brief’s scale reference. Sample name/weight/fish/stamp placement is review-only and not a native game capture.
- `review/A-stamp.png`, `B-card.png`, `C-splash.png`, `D-jars.png`: retained family proofs on both backgrounds; B/C refreshed after corrections.
- `delivery-checks.json`:9/9 exact size, RGBA, transparent canvas borders, alpha0/255range, source/Assets byte equality and SHA256. Jar contour shared in every SVG; opaque gold pixels within glass body increase0,1102,2259,3441,4464.

The initial export check caught a faint droplet bottom-edge alpha fringe; its SVG was inset and the entire nine-file check passed afterward. Final visual sheet and assembly were opened after this correction. Native animation, Unity import/filtering, text rendering and actual harbour/first-catch layouts remain Claude/Mo’s integration checks; no runtime acceptance claimed. No unfinished artist step or temporary backup remains.

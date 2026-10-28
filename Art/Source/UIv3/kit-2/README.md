# Day-flow art, kit 2

Run `../build_kit2.py` with the Catchline UI Python environment to regenerate the twelve PNGs, import metadata, SVG originals, manifest and contact sheet. Existing GUIDs are preserved on regeneration.

All lettering is live UI text. `manifest.json` lists PNG dimensions, safe text rectangles in the SVG viewBox coordinates, and nine-slice borders in **source pixels, left/bottom/right/top**. Scale safe rectangles with the image. The transparent outer margin is intentional.

- Day cards: 240×320 viewBox, PNG at 2×. Header `(25,66,190,34)`; body `(30,213,180,73)`. Teal/coral/navy, one/two/three dots, increasing fish silhouette. Keep the 3:4 aspect.
- Route pin: 96×100 viewBox. Centre the live stop number inside `(27,16,42,40)`.
- Fuel chip: 256×96 viewBox. Reading such as `70%` inside `(86,18,150,56)`.
- Arrival banner: 448×124 viewBox. Text inside `(70,26,308,60)`. Slice border `(132,56,132,84)` pixels preserves both pins and folded ends.
- Route dash: slice border `(56,16,56,16)` pixels. Draw at 24 logical units high (the source height at 2×); shorter heights compress the centre stroke. Use a short segment per gap; the centre dash stretches between fixed end dashes. Chain segments for long routes.
- Prep icons: 256×256 viewBox, PNG at 2×. Knife, ice, fish crate and pan use the kit's paper, navy, teal and brass.

`CoastalCanvas.KitSliceV3` accepts explicit pixel borders for these two sliced assets. Its image multiplier is 2, matching the existing kit. Unity importer borders are also set, for Sprite consumers. Runtime `Sprite.Create` callers must pass borders explicitly.

Contact sheet: `docs/screens/ui-v3/art-kit-2.png`, cream and sea panels. Native TEST fixture: `kit3-art`, with Fredoka text overlays, a stretched arrival banner and route segment. The fixture is capture-only and cannot appear during normal play.

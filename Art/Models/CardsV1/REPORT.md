# ART108 — crew portraits and card frames

Art-side A3 imagery delivery, 23 October 2026. Eleven individual built-in
imagegen calls created Mira, Noor, Dirk, Sam, Kofi, Ana, Mats, Lise, Olaf,
Pim and Tove. Each exact prompt and untouched original PNG is under
`Art/Source/Art108/portraits/`. The approved Crew concept and existing
portrait sheets were style/identity references, never cropped for delivery.

Self-contained editable SVGs embed the source artwork and define a shared
curved shoulder crop. The crop removes stray pixels below the illustrated
bust while keeping the original generation intact. These are raster-backed
SVG compositions, not falsely claimed vector drawings. Runtime PNGs are
240×240, with supplied 96×96 and 56×56 versions; all use real alpha.

The four vector-native 480×640 frames are blue, purple, gold and locked.
Unlocked portrait windows are transparent. Name bands and three ability
slots contain no baked text. `manifest.json` gives the exact rectangles,
export hashes and source paths. Text/icon binding belongs to the UI session.

`build_cards.py` renders with resvg-py and checks dimensions, transparent
corners, non-empty portraits and opaque image coverage. The final review
plate has been inspected at 96/56 px. The initial unresolved external-image
packaging was caught visually and corrected by embedding the PNG data;
the stronger coverage check prevents blank portrait exports passing again.

The original generated portrait identities were preserved where available.
Mira and Tove are new designs. Olaf now wears the specified engineer helmet;
Noor/Tove use teal sorting aprons and Mats an ivory table apron. The source
Sheets/Concepts and current production UI assets were not replaced.

Runtime paths: `Assets/Art/UI/Portraits/art108-*.png` and
`Assets/Art/UI/Cards/art108-frame-*.png`. No Unity import, roster binding,
mobile input acceptance or installed-game update is claimed. No commit yet.

Publication update (24 October 2026): Mo authorized GitHub publication of this delivery. See Art/ART-PLAN-PROGRESS.md and comms.md for the commit/push receipt. Earlier no-commit wording describes the original pre-publication handoff. Native acceptance remains pending.

# RESTAURANT-ART-9 — Codex 1 source delivery

Ready for Claude's import/review. No Assets, production code or git changes. No commit. Native rendering, touch acceptance and gameplay binding remain unverified.

## Hiring board

- Final mockup: `Art/Source/Restaurant/concepts/ui-17-hire.png` (844×390).
- This folder: 13 text-free tight RGBA exports at 3×; `manifest.json`, `layout.json`, `text-styles.json`, `slices.json`, `text-measurements.json`.
- `layout.json` lists every repeated card use and accepted external bust/job icon path with hashes. Keep those external dependencies; no redundant copies are included.
- Text stays live: 22 measured labels. Font, colour, rect, size, stroke/shadow and alignment are explicit. Sample candidates are Tess/Cook, Jo/Waiter and Ines/Barista, matching the accepted outfit manifest.
- Wallet, rarity, wage and trait examples are **presentation samples**, not economy rules or candidate availability. `sample-data.json` marks this explicitly. All rarities share a blank teal ribbon with a live label.
- Four action hit rects are at least 44px high. PNG dimensions/borders are in export pixels; layout/text rects are in logical pixels. Borders follow left, bottom, right, top. Divide export measurements by three for logical dimensions.
- `contact-sheet.jpg` shows each piece at actual logical size. `slice-proof.jpg` checks alternate card/ribbon/button dimensions. `hire-reconstructed-3x.png` independently reconstructs the final concept exactly.
- Full initial ImageGen painting and prompt are in `provenance/`. It predates packaging; the final concept uses accepted painted-kit pieces and corrected fixed-job identities. The initial painting is provenance, not the reconstruction reference. Exports declare resampling; no native 3× painted-detail claim.

## Additional guests

- Public PNGs: `Art/Source/Restaurant/clothes/guests/v2-guest-09.png` through `v2-guest-16.png`, each 192×192 RGBA for a 64×64 logical review slot.
- Contact: `clothes/guests/contact-sheet-extra.jpg`. Actual-size accepted/new comparison: `clothes/guests/extra/reference-comparison.jpg`.
- 09 mother, 10 father, 11 daughter (family); 12 older tourist; 13 fisherman; 14 young diner; 15–16 elegant older couple.
- Guest `manifest.json` retains its original 12 entries verbatim and appends eight. `extra/manifest.json` contains only the new set; `extra/layout.json` documents the alternative review-slot uses. No guest text is baked in.
- The original accepted guest PNGs and original contact sheet are unchanged. These new concepts do not change the production guest roster or claim matching additional 3D models.
- ImageGen originals and exact prompts are retained in `extra/provenance/`. Requested mechanical alpha crop and Lanczos resize retain circular transparency. Tight bounds and transparent corners are checked.

## Verification

`uv run --with pillow python Art/Source/Restaurant/exact/s17/audit_delivery.py`

PASS: 21 exports, 1,732 baseline accepted files unchanged, original 12 guest manifest entries preserved, 22 live labels fit, every placement/use and four hit rectangles checked, valid slice/hash/alpha/dimension contracts, unique public names, one pixel-exact mockup reconstruction, five current opened review hashes.

Evidence: `delivery-audit.json`, `visual-review.json`, `preservation-baseline.json`, `guest-manifest-before.json`. Packaging helpers only write this source-art delivery. `package.py a` rebuilds the board; `package.py b` rebuilds/appends the eight guests from preserved originals. Guest comparison helper is `clothes/guests/extra/review.py`.

Codex 1 finished; all ART-9 reservations released. IDLE awaiting a new current assignment.

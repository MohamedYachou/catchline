# S6 - weekly restaurant dashboard

Delivered reference: `../../concepts/ui-6-dashboard.png`, exactly **844 x 390**. It follows the accepted cream paper, navy contours, orange selection, teal buttons and blue timber wall. The selected **This week** view contains weekly income and its seven daily bars, popularity/change/stars and seven-point trend, three menu-performance rows, and the next Bistro upgrade with its requirement/progress. Live service and crew priorities are navigation entries; their detailed views are outside this single mockup. All numbers are illustrative, not proposed balance values.

## Import handoff

- **31** unique `v2-s6-*.png` sprites; **51** measured placements including every repeated row, bar, star, divider and chevron. `layout.json` has the 844x390 top-left canvas, measured asset inventory and named `use` entries with `z` ordering. The right chevron reuses the left with `flipX`.
- **49** individual text entries in `text-styles.json`, each with unique kebab ID, screen 6, exact mockup-pixel region, colour, weight, stroke/shadow and font size. Fredoka Bold is the closest supplied runtime face; actual metrics are calibrated to the measured regions. Painted font identification is not proven. `painted_size_estimate` retains the initial visual estimate.
- **16** sliced sprites. `slices.json` and each manifest `borders` use **left, bottom, right, top in exported PNG pixels**. Import at the recorded rect; use Sliced for these backgrounds/tracks/bars, Simple for illustrations, icons, sign and circles. Borders preserve corners/pins and leave positive stretch centres. Bar/progress text stays separate.
- Sprites have text-free centres. Only the described euro currency emboss remains painted. Cream paper/button interiors are intentionally opaque; outer backgrounds are transparent. The wall is fully opaque. Every export is exactly three times the largest width and height needed by its measured uses; no transparent canvas padding.

## Source and processing disclosure

The built-in ImageGen painted the mockup using accepted S3/S5 concept references. It returned **1844 x 853**, about 2.185x the requested logical canvas, preserved unchanged in `provenance/s6-generated.png`; the 844x390 reference is a mechanical downsample. This is not a native-3x painted master.

Each individual piece was isolated/cleaned with ImageGen using its measured crop and the full mockup. `provenance/*-generated.json` retains complete prompts, crops and original local paths; original output PNGs are retained. `references/` contains the exact measured source crops. These clean exports follow the reference geometry and style but have regenerated painted detail; they are **not pixel-identical literal cutouts**. Their alpha bounds are cropped after discarding generator specks below 8/255 opacity, then mechanically resized to the recorded 3x dimensions. `manifest.json` records original/output sizes, alpha crop, method and SHA256s. No claim of native 3x detail is made for resized exports.

## Verification

`audit.json`: all 31 PNGs pass RGBA, tight visible-alpha canvas bounds and >=3x for every use; opaque wall checked; all 51 placement names resolve and have named uses; all 49 text IDs unique; all text/placement rects fit 844x390; no external `v2-s6-*` filename collisions; all 16 border definitions fit their PNGs.

Opened all six `review-*.jpg` crop-versus-export contacts (every sprite), all three `layout-measure-*.jpg`, all three `text-measure-*.jpg`, both `slices-review-*.jpg`, and `reconstruction-compare.jpg`. The latter recomposes the actual exports and measured Fredoka text at display size; `reconstructed-3x.png` retains the large offline proof. Regenerated outline/shading and font differences remain visible beside the painting. This is an art handoff proof, not Unity/runtime acceptance. Claude owns import, binding and native review.

Helpers here only crop, resize, compose review evidence, measure and audit this art package. Reproduction order: `metadata.py`, `package.py`, `measurements.py`, `recompose.py`, `final_audit.py` (Pillow via uv). `prepare.py` records the crop jobs; do not regenerate accepted artwork just to rerun audits. No temporary before-backups were needed for these new files.

Mira C/D was completed separately in `../../clothes/2d/mira-cd-REPORT.md`, with individual sheets/fronts/busts/comparisons and A-D beside Noor/Ines. No selection is implied.

No Assets, production code, .meta, save, watchdog or Git edits. All authored paths released on DONE; no subagents. Waiting for lead review/new assignment.

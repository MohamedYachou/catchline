# S6 live chart / S14 harbour entry / S9 states

Art delivery complete. No Assets, runtime code or Git changes. Claude owns import/wiring and native acceptance. The independent `delivery-audit.py` passes ten exports, 55 preserved accepted sprites, current actually-opened review hashes, tight RGBA 3x sizes, unique names, seamless chart columns and untouched harbour pixels outside the entry.

## S6: draw the real week

Four additions to `../s6/manifest.json`; local metadata and examples in `../s6/live-chart/`.

- `v2-s6-trend-dot`: place on each data point, above links.
- `v2-s6-trend-segment`: horizontal source, midpoint pivot; stretch its full width to the distance between two points, then rotate. Do not use the old painted trend for live data.
- `v2-s6-trend-fill`: repeat horizontally, clamp vertically; clip the gradient below the actual curve and above the baseline. Both repeat edges match exactly.
- `v2-s6-bar-empty`: faint no-service placeholder; example uses render opacity 0.28.

See live-chart/REPORT.md and live-data-proof.jpg. Root static layout remains unchanged because these primitives need live data positions.

## S14: harbour entry

`../../concepts/ui-14-harbour-entry.png` preserves the original 1920x1080 HUD canvas. Import the three PNGs from this folder using manifest/layout/text-styles/slices. Button and badge are blank; facade has no baked lettering. Live labels are “Mira's” and “Service tonight”. Hide the badge when there is no service tonight; the art defines no unlock rule.

Entry rect is [36,276,440,146] below the harbour status. Anchor/scale its group with the harbour HUD; do not treat 1920-space rects as 844-space rects. Original pixels outside the entry are byte-equal. Preview: context-review.jpg; text measurements: text-layout-review.jpg.

## S9: interaction overlays

Three additions to `../s9/manifest.json`. `../s9/interaction-states/layout.json` is state-only: do not draw it permanently on the static screen.

Replace the normal chip while dragging and overlay its current task, number and handle. Show the transparent drop rim at the valid target. Locked-job bubble explains fixed card jobs and task reordering; use its measured live labels. Tooltip pointer is protected by the large left slice; minimum logical width 120. Preview both states and stretch proof in interaction-states/.

All slice borders use source pixels in left/bottom/right/top order. All rects use logical top-left coordinates; exports are exactly 3x. Original generated paintings/prompts and deterministic packaging helpers are retained. Upscaling does not claim native 3x painted detail. Art audits and visual reviews do not establish Unity rendering, live hit targets or interaction acceptance.

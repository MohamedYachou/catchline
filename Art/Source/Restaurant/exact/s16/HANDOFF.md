# RESTAURANT-ART-8 — Codex 1

Source-art delivery complete. Native import, state binding and lead/Mo acceptance remain pending. No Assets, production code or git changes.

- Week report: `../../concepts/ui-16-week.png`, 844x390. Sixteen `v2-s16-*` exports, seven independently placed income bars, best-dish medal and dish slot, accepted Jo bust slot, popularity change, total coins and Next week.
- Reservation: `../../concepts/ui-3-reservation.png`, 844x390. Package in `../s3/reservation/`: five reusable pieces and one context-only wall patch. Guest, party/time, wished dish, Accept and Decline are live content.
- Each package has manifest, layout, text-styles with measured rects, slices, text-measurements, actual-size contact sheet, reconstructed 3x frame and slice proof. Border order is left, bottom, right, top in export pixels. Layout/text rects use logical screen pixels.

## Import notes

Keep labels live; the exported controls/panels contain no required labels. Example values are illustrative: 280, 360, 320, 410, 450, 560, 460 total 2,840; popularity 40 to 46; Grilled fish 48 served; Jo. Bind the real seventh-night results. This art introduces no economy or popularity rules.

S16 bars reuse a single teal sprite and gold best-night sprite, vertically sliced. Preserve caps; hide a zero-height bar and retain its zero/day label. For tiny values, clamp drawing height to the cap minimum without changing the numerical label. The arrow is a separate sprite, avoiding font glyph dependence. Best-dish and crew content are external accepted assets with source hashes in layout.json. Replace them with actual results.

The reservation replaces the existing right-hand request ticket; do not stack it with the chalkboard/special card. Hide the old ticket in the native layout. `v2-s3-reservation-wall-patch` exists only to remove the baked ticket in the reference painting; do not import it as a UI overlay. Ada and grilled fish reference accepted external assets. Accept and Decline hit rectangles are 144x44. Existing central plan and Got it remain reference context.

## Evidence and limits

`delivery-audit.json`: PASS, 22 RGBA exports at exactly 3x logical size, tight alpha bounds (two declared opaque backgrounds/context exceptions), unique public names, source/export hashes, valid slice borders, all placements in bounds and all exports used. Thirty-five live labels fit their measured rects. Both concepts reconstruct pixel-for-pixel from metadata. All 1,699 baseline accepted files retain their hashes. Six opened final review artifacts match the review ledger.

Built-in ImageGen painted the initial week/reservation compositions and the new medal. Original outputs and prompts remain in provenance. Final mockups are exact composites assembled from those paintings and the accepted restaurant kit, with the accepted Jo/Ada/dish identities and live labels. Three-times export dimensions include resampling; they are not a claim of native 3x painted detail. This is source-art QA, not Unity runtime or touch acceptance.

Reproduce with `uv run --with pillow python Art/Source/Restaurant/exact/s16/package.py all`, then `uv run --with pillow python Art/Source/Restaurant/exact/s16/audit_delivery.py`. The visual-review ledger intentionally detects changed final review files; inspect changed outputs before refreshing that ledger.

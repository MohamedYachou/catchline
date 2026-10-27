# S13: First night with Mira

Official mockup: ../../concepts/ui-13-first-night.png, 844x390. Four small frames coach seating guests, kitchen cooking, serving hot plates and counting the takings at close. Mira wears the accepted interim host D look. Copy is a visual proposal; it is not a wired tutorial implementation.

## Import

Nine unique v2-s13-* tight RGBA sprites at 3x their recorded logical size; 26 measured placements including repeated uses; nine individual text entries with unique IDs, screen 13, measured rects, explicit line breaks and fitted Fredoka Bold sizes. No coaching text is baked into the bubble. Speech bubble, curved gold pointer and Mira host portrait are reusable independently. Frame, title sign, step label and bubble have left/bottom/right/top borders in exported pixels in slices.json. The bubble tail is protected by its right border.

The background is accepted blue timber. First three stills mechanically crop the accepted ui-2-service.png, retaining its existing painted order bubbles; their gold pointers indicate a table, kitchen counter and hot plate. The closing still is a new ImageGen companion view with cleared tables and a receipt ledger. It deliberately avoids inheriting the old Seat them / Not tonight choice. The closing pointer indicates the ledger, not a live close button. No animation, interaction targets or gameplay state transition is implied by this sheet.

All pieces are assembled into reconstructed-3x.png; its 844x390 downsample exactly matches the official mockup. Other than the room stills, the reusable UI pieces have no painted text. Original pointer/closing paintings and prompts are preserved in provenance/. Other pieces reuse accepted kit artwork through requested mechanical alpha crops, nine-slice composition and resizing. 3x exports do not claim native generated 3x detail.

audit.py checks RGBA/tight bounds, exact 3x dimensions per use, name/use/ID uniqueness, source and export hashes, text fit, in-canvas placements, slice centres and concept/reconstruction equality. cuts-review.jpg, text-measure.jpg and slice-proof.jpg support actual visual review; visual-review.json records reviewed hashes. Slice stress examples preserve corners and the bubble tail at two widths.

Ready for Claude review/import. Unity alpha/rendering, responsive layout, text line wrapping, live room anchors, coaching triggers and lead/Mo acceptance remain unverified. No Assets, production code, metas, save, watchdog or Git changes; no commit. Helpers in this source-art folder only package and audit the requested artwork.

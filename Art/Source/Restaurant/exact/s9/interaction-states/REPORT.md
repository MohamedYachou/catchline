# S9 interaction states

Three text-free RGBA exports, tight at 3x. The existing 24 accepted sprites and the static S9 concept/layout are preserved. `manifest.json` here contains the three additions; the parent manifest also includes them.

- `v2-s9-chip-drag`: raised cream chip, navy lip and cast shadow included. Replace the normal chip visual while dragging; overlay the existing live task label, number and handle.
- `v2-s9-slot-target`: teal/gold insertion highlight with transparent centre. Show behind the dragged chip for a legal destination, then hide on drop/cancel.
- `v2-s9-tooltip`: blank fixed-job explanation bubble. Use the two live labels in `text-styles.json`. Jobs belong to the card; tasks can be reordered.

`layout.json` contains sample state placements on the 844x390 screen, not permanent additions to the static layout. Coordinates are top-left logical pixels. Slice borders are source pixels, ordered left/bottom/right/top. Tooltip's large left border protects its pointer; minimum logical width 120. Clamp the bubble group to the safe area.

Generated source paintings and prompts are retained in provenance. Alpha values below 8 were trimmed before export; resizing to 3x does not claim native 3x generated detail or pixel-identical extraction from the original mockup.

Audit PASS: 3 tight RGBA sprites at exact 3x dimensions, 2 measured live labels, 3 slice definitions, transparent slot centre, and all 24 accepted sprite hashes preserved. Actually opened context-review, cuts-review and two-width slice-proof; hashes recorded in visual-review.json. No Unity import, interaction or native acceptance claimed. No Assets/code/git edits.

# RESTAURANT-ART-6 handoff

All requested source art delivered; no Assets/code/Git edits. **Claude import and native verification pending.**

| Package | Public cuts | Review / contract |
|---|---:|---|
| `exact/transition/` |5| [REPORT](REPORT.md), [layout](layout.json), [text](text-styles.json), four `concepts/ui-transition-*.png` |
| `exact/s9/jobs/` |7| [REPORT](../s9/jobs/REPORT.md), [bindings](../s9/jobs/job-bindings.json), [all jobs at actual size](../s9/jobs/all-jobs-actual-size.jpg), [S9 context](../s9/jobs/actual-size-context.jpg) |
| `exact/badges/` |2| [REPORT](../badges/REPORT.md), [context](../badges/actual-size-context.jpg), [states](../badges/count-and-flag-state-review.jpg) |

All packages include manifest, layout, measured text-styles, slices, contact, provenance and actual-size review. Every label is separate/live. Six job icons include the requested dishwasher task icon; it does **not** add a fixed gameplay job. Transition title band, job tag, count and flag have nine-slice metadata; icons preserve aspect. Top-left logical coordinates; PNGs are3x; slice borders are export pixels in left,bottom,right,top order. Public names are unique across accepted cuts.

Audit command from project root:

`uv run --with pillow python Art/Source/Restaurant/exact/transition/audit_delivery.py`

Final PASS:14 tightRGBA3x exports;1497 accepted files unchanged;24 measured live labels fit;15 actually opened review hashes current;4 transition concepts exactly reconstruct from delivered backgrounds/band/live text. [Audit result](delivery-audit.json), [review ledger](visual-review.json). Ten original paintings generated with built-in ImageGen (two harbour scenes,six job icons,two badges); source paths/prompts/receipts are under each package's provenance. Two accepted kit elements reused (title band/job field). 3x resampling is not native3x painted detail.

Next: import only public manifest PNGs, bind the appropriate phone/desktop transition composition, keep labels live, apply slices, wire flow/job/count/new conditions, and verify on actual native HUD. Source-art reviews are placement proofs, not game captures. No commit, no temporary restore backups, no subagents. Codex1 finished; all ART-6 reservations released.

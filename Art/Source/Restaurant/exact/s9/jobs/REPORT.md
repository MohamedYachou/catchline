# RESTAURANT-ART-6 — restaurant job icons

Seven tight RGBA 3x public cuts: `v2-s9-job-host`, `-cook`, `-waiter`, `-dishwasher`, `-barista`, `-handyman`, `-tag`. All six icons use aspect-preserving bounds within 28×28 logical pixels. The cream tag is166×34 logical with export borders `[24,24,24,24]`, left,bottom,right,top. Icons preserve aspect; only the tag stretches.

The six new paintings use built-in ImageGen, with originals/prompts/receipts in `provenance/`. The blank tag reuses accepted `s9/v2-s9-job-field.png`. Mechanical crop/resampling only; 3x exports are not a native 3x detail claim. Manifest includes source/export hashes and exact tight dimensions. Layout includes the measured original S9 row positions and a separate six-icon legend. Text remains live at14px in crew rows,22px in the legend. Handyman's original y313 backing alignment was restored before final review; no old label peeks below it.

`job-bindings.json` maps Reception→host, Cook→cook, Waiter→waiter, Barista→barista, Handyman→handyman. **Dishwasher is an auxiliary task/presentation icon, not a newly introduced RestaurantData.Job.** No data/roster/gameplay change. Helper can use its current task's icon; caller chooses.

Actually opened `contact-sheet.jpg`, `actual-size-context.jpg`, `all-jobs-actual-size.jpg`, and `job-tag-slice-review.jpg`. Icons and all six words remain readable at final size. The reference roster remains unchanged, including two Waiter rows. The static demonstration replaces lock glyphs with job icons; runtime lock/state handling remains Claude-owned.

Whole-delivery audit and visual hashes: `../../transition/delivery-audit.json`, `../../transition/visual-review.json`. Run packaging/audit from `../../transition/`. Source-art delivery only; Claude imports and verifies actual service rail/crew HUD. No Assets/code/Git edits; no native acceptance claimed.

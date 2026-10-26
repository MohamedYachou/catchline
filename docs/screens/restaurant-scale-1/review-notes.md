# Final review

Codex 1 individually opened all 48 corrected final captures and all eight final contact sheets. Labels fit, no room envelope crosses the HUD bands, the pass reads as a counter after its navy-front/light-top correction, and the warm kitchen and wood guest zones remain distinct. This is a scale greybox, not final restaurant art or touch acceptance.

Two isolated read-only reviewers completed their assignments:

- `scale_design_review`: favored orthographic 52 degrees for consistent footprints and body readability. At 60 degrees heads dominate; at 45 degrees tile depth suffers. Flagged the original pass as floor-like; corrected in the scratch generator and all captures replaced. Flagged stove-top visibility as insufficient evidence for kitchen-floor visibility; separate aisle-floor rays added and their occlusions reported.
- `scale_metric_review`: confirmed all 48 dimensions, scaler calculation, all 24 phone failures, and the one desktop threshold failure. Caught perspective width sampled at the near edge of the back row; corrected to the far edge and all captures/metrics replaced. Crew height remains projected renderer bounds, not segmented visible silhouette; the README states this limit.

Lead consolidation: use orthographic 52 degrees for the working direction, with a separate placement zoom/pan on phone. No tested full-room phone view meets both 44 px tile dimensions. Proposed zoom ratios and floating drag ghosts need interactive validation. Stove-top probes pass, while floor probes reveal real counter/crew occlusion. No remaining correction is required for this study's declared scope.

Both reviewers finished; no delegated implementation or production files.

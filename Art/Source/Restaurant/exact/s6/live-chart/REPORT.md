# S6 live-chart handoff

Four additive 3x tight RGBA sprites; root manifest appended, accepted artwork unchanged. See manifest.json for dimensions, hashes, pivots, rects and rendering rules. No text in these assets.

- trend-dot: accepted teal jewel isolated from the trend. Logical 12x12; overlay at each data point.
- trend-segment: accepted painted straight interval, rectified; uniform repeatable centre column. Logical 48x6; stretch horizontally, rotate about midpoint, draw under nodes. Border [0,0,0,0] (L/B/R/T); the entire segment is stretchable. Square ends are covered by jewels.
- trend-fill: accepted-area sampled tint with smooth vertical alpha profile, identical columns. Logical8x49; repeat X, clamp Y; clip upper edge to actual polyline, baseline at bottom. No fixed painted week. Maximum alpha72/255 falls to1/255.
- bar-empty: built-in ImageGen pale variant of accepted teal bar, trim/export. Logical24x36, border15px each side (source pixels L/B/R/T). Render opacity0.28 for faint placeholder. Zero service must not be presented as positive income.

Opened cuts-review.jpg and live-data-proof.jpg. Audit PASS: four tight RGBA3x, both repeat seams exactly equal, all31accepted sprite hashes preserved. Offline proof, no native runtime acceptance. Extraction/resampling does not establish native3x painted detail. Built-in ImageGen used only for empty-bar painting; accepted stroke/node pixels and sampled gradient are deterministic extraction. Original bar painting retained. No Assets/code/git.

# ART-5 stage celebration

Three public sprites: soft radial gold/ivory rays, six-frame confetti atlas, and a blank New stage ribbon reusing the accepted S5 best-night ribbon family. The New stage! label is separate live text. The stage illustration and original panel are accepted S11 reuses, not new exports. All exports are tightly bounded RGBA, three export pixels per logical pixel; this does not claim native 3x painted detail.

`manifest.json` records all public sprites and animation frames. `layout.json` measures the 844×390 peak-frame demo, draws rays behind the facade at 0.55 opacity, and keeps the right-hand unlock list and Wonderful action clear. Rays are **radial**, uniformly scalable, not nine-sliced; preserve their centre and aspect. No hard rectangular clipping. The same effects reuse at every restaurant stage.

Confetti is painted by built-in ImageGen. Separate alpha components are extracted from that source painting into `provenance/particles`, then deterministically moved, rotated and faded across **six frames / 600 ms**. Each frame is cropped tightly and packed horizontally at variable width. Use explicit export-pixel `rect` values, frame duration and normalized top-left `pivot` values. In Unity convert pivot y to `1-y`; place each pivot at one shared anchor. Equal-cell slicing will be wrong. Hide at end, no looping; GIF preview loops only to aid review. Reduced motion may omit the burst and keep the static ribbon/rays.

Sources, prompts, extraction provenance, actual-size context, contact and frame-sequence/GIF proof are included. No labels are painted into the exported backings. `text-styles.json` provides measured live rectangles.

Source-art verification only. Native import/playback/anchor/trigger checks and lead/Mo acceptance remain with Claude/Mo. No Assets, production code or Git edits.

# ART-5 upgrade states

Four public sprites: muted blank Owned card, green check badge, stage-lock tag, and four-frame purchase sparkle strip. All exports are tightly bounded RGBA at three export pixels per logical pixel. Upscaling is not native 3x painted detail.

`manifest.json` is the import list; `layout.json` measures the 844×390 demonstration and records accepted reused pieces. `text-styles.json` holds separate live labels and illustrative values. The muted card and lock tag have export-pixel nine-slice borders in `slices.json`. The owned check is fixed-aspect; do not stretch it.

The card says Owned after a successful purchase and its buy action becomes unavailable. The stage lock label is live (`Needs Bistro` in the sample); callers substitute the actual required stage. The old price is removed beneath either state. Sample states do not redefine upgrade progression or wallet balance.

The purchase strip has **four variable-width, tightly packed frames**, **300 ms** total. Read each export-pixel frame rect and top-left normalized pivot from `manifest.json`; restore that pivot to one stable success anchor. In Unity's bottom-left pivot convention use `[x, 1-y]`. Do not divide the atlas into equal quarters. Hide at completion; there is no final held frame. The preview GIF repeats for inspection only. Skip motion or briefly show the peak frame for reduced motion. Never play for an unaffordable/locked purchase.

New paintings use built-in ImageGen; original PNGs and exact prompts live in `provenance/`. The accepted lock painting is reused. `package.py` builds only this and the other two ART-5 source-art folders. Contact, real-size context, frame sequence, GIF and two-width slicing proofs accompany the package.

Source-art verification does not establish Unity import, runtime interaction, timing or lead/Mo acceptance. Claude owns integration. No Assets or production code changed, no commit.

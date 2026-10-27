# RESTAURANT-ART-6 — transition art

Source-art delivery, Codex 1 (Windows app). No Assets, runtime code, save, watchdog or Git edits. Native import, flow timing, device checks and lead/Mo acceptance remain Claude-owned.

Five public RGBA PNGs: `v2-transition-evening-phone`, `v2-transition-evening-desktop`, `v2-transition-morning-phone`, `v2-transition-morning-desktop`, `v2-transition-title-band`.

The four backgrounds are text-free full-bleed paintings. Phone uses 844×390 logical pixels (2532×1170 export); desktop uses 1440×900 (4320×2700 export). The two original built-in ImageGen paintings are in `provenance/`, with final prompts and generation receipts. Each painting has a recorded aspect-preserving crop for both screen sizes. The blue-awning restaurant and harbour remain visible in each crop. Dawn and evening are separate illustrations, not identical harbour geometry under relighting.

The cream/gold title band reuses the accepted S6 income-summary family. It is a separate 600×90 logical sprite with 3x export borders **left90, bottom75, right90, top75**. Stretch with nine-slicing; do not scale the corner radii with the whole panel. Phone placement `[122,284,600,90]`; desktop `[270,712,900,144]`. Separate live title and one-line subtitle rects/sizes are in `text-styles.json`. No text is baked into the backgrounds or band. The subtitle strings are illustrative, not new gameplay rules. Caller owns localisation/reflow for longer text.

`layout.json` has four named screens, explicit ordered uses and top-left logical coordinates. `manifest.json` has public names, dimensions, source/export hashes and crop provenance. `slices.json` records borders in export pixels, ordered left,bottom,right,top. Concepts with the live labels are in `../../concepts/ui-transition-{evening,morning}-{phone,desktop}.png`. Full 3x reconstructions remain here for exact comparison.

Actually opened all four final concept images, the cut contact and the two-width band proof. Rounded band corners were corrected before final review. Timing/transition animation is not specified by these static assets; use an immediate cut or simple fade for reduced-motion settings. No extra action button is introduced.

`package.py` is a source-art mechanical composition helper, not production code. Built-in ImageGen made the two paintings; Python only cropped/resampled and composed existing/generated artwork with live-label previews. 3x resampling does not claim native 3x painted detail. `audit_delivery.py` independently checks the whole ART-6 delivery. Final PASS:14 exports,1497 accepted files byte-preserved,24 live labels fit,15 actually opened review hashes current,4 concepts reconstructed exactly from delivered layers/text. No temporary restore backups were created.

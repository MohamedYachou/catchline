# RESTAURANT-ART-3 — Mira coach card

Three tight RGBA sprites, logical dimensions in manifest, exports at 3x. Accepted S13 speech panel, Mira D host portrait and S1 orange button reused without identity regeneration. `ui-coach-phone.png` (844x390) uses the arrange reference; `ui-coach-desktop.png` (1440x900) uses the service reference. These demonstrate the reusable coach overlay inside two restaurant screens; underlying requests and illustrative numbers remain reference art.

`layout.json` specifies each sprite use, phone/desktop destinations, z order, background hash and interaction bounds. `text-styles.json` contains separate live body, Got it and Skip labels, Fredoka Bold and measured rects. A 110-character sample wraps to exactly three lines at 16px phone / 23px desktop; `capacity.json` and `text-measurements.json` record fit. Different wording/localization needs wrapping and fit validation. Skip is visually quiet, with an expanded44px hit height specified in layout.

Use sliced rendering for panel and orange button. Borders in `slices.json` are **export pixels**, ordered left,bottom,right,top; divide by3 when rendering in logical pixels. Keep the right speech-tail cap intact. `slice-proof.jpg` shows548px and800px widths. Preserve portrait aspect. The caller owns tutorial line/step, focus, optional pause, Got it advance and Skip coaching dismissal. No extra Last orders artwork: that is live call-strip text.

Source paintings, mechanical crops, source/export hashes and resampling limits are recorded in manifest. No native3x-detail claim. Build with `uv run --with pillow python Art/Source/Restaurant/exact/coach-card/package.py a`. Only the source-art package is delivered; imports, native behavior and lead/Mo acceptance remain pending.

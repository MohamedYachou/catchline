# RESTAURANT-ART-6 — HUD badges

Two tight blank RGBA 3x cuts: `v2-hud-count-badge` (30×22 logical) and `v2-hud-new-flag` (45×24 logical). Built-in ImageGen painted both; originals/prompts/receipts are retained in `provenance/`. Mechanical alpha cropping/resampling only; no native3x painted-detail claim.

Nine-slice borders are in **export pixels**, left,bottom,right,top: count `[27,27,27,27]`; flag `[24,21,42,21]`. Preserve flag's right-hand notch. Labels are separate live Fredoka-Bold cream text. Count uses22×22 for1-9,30×22 for10-99; caller hides at0. Larger numbers need a defined cap or wider label; this delivery only specifies1-2digits. Flag has separate localisable New text; width can grow from45 to64 as shown. These are overlays; parent controls retain the full tap target and accessible name/state.

`layout.json` demonstrates count at `[345,54,30,22]` on the Live service tab corner and New at `[787,319,45,24]` on Upgrades. Count was moved clear of tab text before final review. `text-styles.json` has measured live-label rects, and `state-text-fits.json` covers1,9,12,99 and two flag widths.

Actually opened contact, actual844×390 dashboard context, count/flag state proof and both slice proofs. Icon/count/new visibility and acknowledgement conditions remain Claude-owned. See `behavior-notes.json` for import-facing notes. No runtime code or UI asset imports made.

Whole-delivery audit and visual hashes are in `../transition/`. Final source-art audit PASS; native import/render/interaction and lead/Mo acceptance remain pending.

# RESTAURANT-ART-10 — source delivery

Codex 1 (Windows app), 2026-10-27. Complete; native import belongs to Claude.

Three new tight RGBA sprites, packaged at 3×. No existing cut or manifest was replaced. No Assets, game code, or Git changes.

| Sprite | Location under exact/ | Texture / logical size |
|---|---|---|
| v2-s9-swap-glyph | s9/ | 39×39 / 13×13 |
| v2-s9-swap-glyph-selected | s9/ | 39×39 / 13×13 |
| v2-s2-call-bubble-2line | s2-call/ | 960×186 / 320×62 |

The swap glyph has two curved arrows in navy. The selected version has the same alpha and a 1.22× RGB highlight; combine it with the existing selected/lifted chip backing. It uses the same 18 measured positions as the old handle. This communicates the agreed tap-first, tap-second swap behavior. [Actual-size chip contact](swap-actual-size.jpg).

The taller bubble has a cream interior, navy rim and a right-pointing tail. Labels remain live. Nine-slice borders, **texture pixels, left/bottom/right/top: 60/45/120/45** (logical 20/15/40/15 at 3×). [Slice stress review](call-slice-review.jpg).

| Frame | Bubble x/y/w/h | Text x/y/w/h | Fredoka Bold / line height |
|---|---|---|---|
| Phone 844×390 | 190,50,320,62 | 207,63,278,36 | 14 / 18 |
| Desktop 1440×900 | 444,86,430,76 | 465,103,370,44 | 18 / 22 |

Keep the original host placement and top bar. The long state extends to phone y112 / desktop y162. Reserve that HUD area when projecting world markers. Four sample messages per device fit within two lines; text is navy #173F57, left aligned and vertically centered. If a localized message exceeds two lines, split it or use the coach card instead of shrinking type.

[Phone actual size](call-phone-actual-size.jpg), [desktop actual size](call-desktop-actual-size.jpg), [phone measured](call-phone-measured.jpg), [desktop measured](call-desktop-measured.jpg). The 3× reconstructions are in this folder. These are source-art layout demonstrations over accepted mockups, not native game captures. The proof removes the old bubble from the base before placing the new one, so its old tail cannot leak through.

The count badge itself is unchanged. [10 and 99 proof](../badges/art10-two-digit-actual-size.jpg) uses the existing 90×66 cut at 30×22 logical, Fredoka Bold 14, cream #FFF4DC, centered in a 24×18 inset at 3,2. Both digit pairs fit without stretching or reducing type.

Import metadata is additive: `s9/art10-manifest.json` + `art10-layout.json`; `s2-call/art10-manifest.json`, `art10-layout.json`, `art10-text-styles.json`. The consolidated manifest here uses paths relative to **exact/**. Existing manifests stay read-only for lead-controlled merging. `swap-layout.json` names every repeated use. `text-fit.json` and `badge-text-fit.json` contain measured ink boxes.

Built-in ImageGen created the swap and taller bubble. Raw outputs and the exact prompts are retained in `provenance/`; alpha threshold/crop, Lanczos export, selected-state tint, nine-slice and proof composition are mechanical packaging. No claim of newly painted native 3× detail.

Verification: all 1,531 pre-existing exact PNGs retain their starting SHA256; all three delivered sprites are tight RGBA at the declared sizes; the two glyph states have identical alpha; 18 placements preserved; all measured message/digit fits pass. Actual-size and slice proofs opened and reviewed. `audit.json` records output hashes; `independent-audit.json` records a separate read-only verification. Native import/render/input behavior remains unverified. No temporary replacement backups were required because the delivery is additive.

Rebuild from project root: `uv run --with pillow python Art/Source/Restaurant/exact/art10/build.py`.

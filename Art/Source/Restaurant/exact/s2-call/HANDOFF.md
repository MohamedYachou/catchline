# RESTAURANT-ART-2 — source art delivery

Codex 1 (Windows app). All three assigned items complete as source artwork. Claude owns import and wiring; HUD concepts await Mo's review. No Assets, production code, metas, saves or Git changes. No subagents.

## Mira call and Close door

Four public sprites in this folder; `manifest.json` records dimensions, hashes and painted sources. `layout.json` has separate phone 844×390 and desktop 1440×900 placements with top-left origin. `text-styles.json` contains measured live labels, not baked text. The accepted host Mira D bust and accepted speech/speed-button surfaces are reused; the door icon is newly painted.

- `v2-s2-call-bubble`: logical 320×44, 960×132 export. Nine-slice borders **[48,36,114,36] source pixels**, order left/bottom/right/top. Desktop width 430, height 54. Tail points toward Mira.
- `v2-s2-call-mira`: logical 38×51, transparent tight crop. Use measured portrait placements, preserving aspect.
- `v2-s2-close-door-button`: logical 97×32, 291×96 export, borders 24 source pixels on every side. Navy idle speed-button family.
- `v2-s2-close-door-icon`: tight transparent door, separate from button and live label.

Call text is 14px phone / 18px desktop Fredoka Bold; measured 40- and 42-character examples fit the actual text rectangles. Review `line-length-slice-review.jpg` and `line-fit.json`. Arbitrary wider/localized lines should wrap; these are representative fit checks, not an all-language guarantee.

The reference top bar needs the measured reflow in `layout.json` to make room for Close door. Phone timeline is narrower; desktop title becomes “Mira's · Service”. Back, wallet, stars and speed controls retain their reference positions. Timeline crops in review pictures are static demonstrations: draw the live timeline into the destination rectangle. The strip is non-blocking; toast timing, queuing, door state, disabled state and hit-target logic remain runtime work.

Actual-size pictures: `../../concepts/ui-2-mira-call-phone.png` and `ui-2-mira-call-desktop.png`. Reconstruction proofs retain exact reference pixels outside the measured edit rectangles at 3×.

## Event markers

Four additions in `../s15/`: `v2-s15-event-birthday`, `-regular`, `-tour`, `-captain`. Manifest entries appended to the original 16 without changing their entries or sprite hashes. Package details in `../s15/events/`: manifest, demo layout, text-free styles, slices, provenance, contact sheet and actual-size event context. World anchors in the demo are illustrative; runtime binds the corresponding table/event. Preserve aspect, do not slice icons.

## HUD concepts — no cuts

`../../concepts/ui-v3-17-hud-fishing.png` and `ui-v3-18-hud-harbour.png`, 1920×1080. Painted cream/navy/gold/orange treatment over the reference layouts. Fishing retains the information, wallet/home, Fish/Carry, lower-left crew and lower-center bite-panel regions. Portrait cards have more height for the busts. The proposal is not a pixel-exact layout or world render replacement.

`../../concepts/hud-v3-review/` has source/proposal comparisons, original rejected paintings, corrected paintings, prompts and hash manifest. Corrected versions restore calm water, reference captain/Sam identity and the harbour reference's 250-coin ice-box price. All reference quantities/copy are illustrative historical mockup content, not proposed balance/data edits. No HUD sprites were cut. Mo chooses direction before implementation.

## Verification

Run `uv run --with pillow python Art/Source/Restaurant/exact/s2-call/audit_delivery.py` from the project root. PASS: eight public tight RGBA exports, all dimensions exactly 3× logical sizes, unique filenames, source/export hashes, all 16 accepted S15 entries and sprites preserved, metadata rects in bounds, text fits, service reference unchanged outside measured edit rectangles. `delivery-audit.json` is the result. `actual-open.json` identifies the visually inspected final proofs by hash. `hud-v3-review/manifest.json` records concept sizes and source hashes.

No native build, import, listening, interaction or runtime acceptance is claimed. No remaining assigned art steps; reservations released after final diary DONE. No commit.

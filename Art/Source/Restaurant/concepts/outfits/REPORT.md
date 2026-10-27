# RESTAURANT-OUTFITS-2D-1

Codex 1 (Windows app), 2026-10-27. Source art delivery complete; native import and acceptance belong to Claude/Mo. No Assets, gameplay code, or Git edits. No subagents.

## Delivery

- `outfit-sheet.jpg`: all six full-front restaurant outfits plus the dishwasher task variant, at consistent reference height. Mira is the finest-dressed host: navy tailored coat-dress, gold piping, teal scarf and jewellery, pinned curly hair. Dirk wears chef whites/toque; Ana a teal dress with cream collar; Sam a navy suit/bow tie; Ines a smart cream blouse/teal waistcoat/navy skirt; Olaf a rolled-sleeve shirt/navy waistcoat. Dishwasher is a Dirk task-clothing variant, not a new roster member or fixed job.
- `<id>-front.png` for mira, dirk, ana, sam, ines, olaf; `dirk-dishwasher-front.png`.
- `v2-s9-bust-<id>-rest.png` and `v2-portrait-<id>-rest.png`, six of each, tight RGBA, exact 3x dimensions. `manifest.json` records source, output hashes, incumbent canvas sizes and transparent trim offsets. `bust-layout.json` gives trimmed S9 placements within the original frames.
- `contact-actual-size.jpg`: the deck identity references beside the new rail portraits at 90px and S9 cuts at their logical size.
- `v2-s5-mira-host.png`: **444 x 501 RGBA**, matching the existing S5 **148 x 167** mockup rect **[580,209,148,167]**. Same happy waving pose and opposite hand at hip, wearing Mira D's host outfit, without captain hat, gloves or captain coat. This is an upper-body painting suitable for the visible region above Sleep.
- `closing-old-new-actual-size.jpg`: old/new at the same logical size, with a second comparison showing the existing Sleep layer covering the lower torso.
- `closing-manifest.json`, `layout.json`, `text-styles.json` (no painted labels), exact generation prompt and original output in `provenance/`.

## Import notes

All files remain in this source folder for the lead to import. Keep the unique requested names.

The six original accepted full-front paintings and matching busts in `clothes/2d/` already satisfied the new classic-uniform order. They were reused, mechanically cropped/resized and assembled into this delivery; no claim that those six paintings were newly generated. The dishwasher draft from the prior interrupted run was opened, checked against Dirk, and packaged. Closing Mira was repainted with the built-in ImageGen tool, using the old waving art as pose reference and Mira D as outfit/identity authority. The exact prompt is `provenance/mira-host-wave-request.json`.

**Bust framing:** preserve aspect ratio. The approved painted busts have different silhouettes from the older deck/S9 crops, especially Dirk's toque. Exports contain the whole approved bust inside the old canvas, then trim away transparent margins. Apply `trimInCanvas` when retaining an incumbent UI frame; do not stretch the trimmed piece to fill the old full width. `bust-layout.json` supplies S9 coordinates. Rail entries use an untrimmed 1200px square (= the incumbent 400px canvas at 3x). These rail exports enlarge accepted source paintings: 3x is the delivery grid, not a claim of newly generated high-resolution detail.

**Closing placement:** `VoyageRestaurantUi.cs` currently overrides the mockup with parent clip `[520,0,324,390]` and absolute portrait rect approximately `[543,198,222,278]`, including a small bob. This was inspected read-only. Claude owns the replacement hook and whether to retain that runtime override. Keep Mira below the existing Sleep button in draw order. The contact is a source compositing proof, not a native AFTER capture; the lead must check the live upper-body crop above Sleep at phone and desktop size.

## Verification

`uv run --with pillow python Art/Source/Restaurant/concepts/outfits/audit-outfits.py`

PASS: 13 named export PNGs decoded as RGBA, dimensions match manifests and divide by 3, real transparent backgrounds, alpha bounds fill their trimmed canvases, output SHA256 matches. All 394 accepted source files from the prior-run preservation baseline and all 18 identity reference hashes remain unchanged. 24 delivered PNG/JPG files decoded successfully. `audit.json` records the evidence.

Opened the final full-front sheet, final deck/rail/S9 actual-size contact, generated closing Mira, and closing old/new actual-size contact. An intermediate wide S9 resize flattened faces; an intermediate upper crop clipped Dirk's chin. Both were discarded by regenerating the same new outputs with aspect-preserving contain and complete face/toque framing before final audit. Final contact shows complete faces, readable roles and host prominence.

No Unity import, runtime screen change or player acceptance is claimed. No temporary replacement backups were needed: accepted sources were read-only and all delivery files are additive. No commit. Released this source scope after the DONE entry in comms.md; idle pending a new assignment.

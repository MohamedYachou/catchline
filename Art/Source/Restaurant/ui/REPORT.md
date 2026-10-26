# Restaurant UI source art

Owner: Codex 1 (Windows app). Assignment: RESTAURANT-UI-ART-1, including the 19:30 and 19:50 addenda and the lead's temporary-crop names. This is source artwork for review, not an integrated or accepted screen. Generated reproductions differ from the accepted painting; pixel-identical matching is **not established**.

Technical delivery complete: **112/112 final sprites individually opened, six review contacts opened, no missing names or dimension/mode/alpha/hash errors**. Three runtime aliases are byte-identical. The independent seal is [delivery-receipt.json](delivery-receipt.json), covering 453 files. All image-generation jobs finished; none remain running. No commit was made.

The inventory is [delivery-audit.json](delivery-audit.json). It lists exact names, opened-file count, dimensions/hash/alpha issues and the explicit ring exclusion. Visual-match and runtime acceptance remain with the lead/Mo, with the known differences below.

## Review images

- [Service icons and people beside the accepted service screen](contact-service.png)
- [Dishes and planning pieces beside the accepted planning screen](contact-dishes.png)
- [Arrange cards beside the accepted Arrange screen](contact-arrange.png)
- [Frames and details beside the accepted closing screen](contact-frames.png)
- [Nine-slice proof](contact-slice-proof.png)
- [All sprites](contact-all.png)

Each final sprite is individually opened before its `opened` flag is set in [asset-audit.json](asset-audit.json). That receipt records the final SHA256, exact canvas size, visible alpha bounds, source size and packaging method. Contacts are review compositions; their cream ground is not baked into the transparent sprites.

## Names and sizes

The complete contract is [expected-assets.json](expected-assets.json): 46 icons, 13 dishes, six crew busts, 25 Arrange item illustrations, 19 other pieces and three byte-identical runtime aliases, 112 final PNG names total. Icons are 80x80 (40 logical), dishes and item illustrations 320x240 (160x120 logical), crew busts 240x280 (120x140 logical), Mira wave 400x400, fish sign 124x100, cats 160x108, catch pile 212x96. Logical sizes assume the brief's 2x convention; the runtime may fit them into its own rects.

Free-size frames were trimmed again after packaging to remove faint, nearly transparent generated padding. Their current dimensions are below; use these final files rather than the untrimmed generated originals.

| File | PNG pixels | Purpose |
|---|---:|---|
| v2-sign-plank.png | 790x180 | Blank hanging wood sign |
| v2-ticket.png | 423x546 | Blank pinned catch ticket |
| v2-review-card.png | 600x321 | Cream closing/review card |
| v2-staff-card.png | 480x118 | Blank staff rail card |
| v2-stock-card.png | 369x607 | Blank service stock slab |
| v2-bubble-order.png | 148x109 | Blank world order bubble |
| v2-chip-repair.png | 360x140 | Red repair alert backing |
| v2-timeline-flag.png | 120x72 | Orange flag, no baked time text |
| v2-timeline-dot.png | 40x40 | Navy/cream timeline dot |
| v2-speed-pill.png | 400x108 | Blank three-segment control |
| v2-speed-selected.png | 128x100 | Orange selection backing |
| v2-btn-rotate/cancel/confirm.png | 96x112 each | Placement controls |
| v2-restaurant-backdrop.png | 2560x1440 | Opaque evening scene |

Aliases preserve existing screen names: `v2-item-rest-table2` = `v2-item-rest-table-2`, `table4` = `table-4`, `booth` = `booth-6`. No patience ring is delivered: the 19:30 override says to use the lead's tintable `Assets/Art/UI/v2-ring-task.png`.

## Slice settings

Borders below are **source pixels**, ordered **left / top / right / bottom**. For a Unity Sprite border vector the order is left / bottom / right / top. At 2x divide these values by two when doing a logical-pixel nine-slice. The centre must remain stretchable. Use a centred pivot for cards; the order bubble's tail is a world anchor and the fish sign is a uniformly scaled illustration.

| File | L / T / R / B | Minimum width x height, source pixels |
|---|---|---:|
| v2-sign-plank.png | 110 / 84 / 110 / 80 | greater than 220x164 |
| v2-ticket.png | 250 / 72 / 70 / 70 | greater than 320x142 |
| v2-review-card.png | 40 / 40 / 40 / 40 | greater than 80x80 |
| v2-staff-card.png | 30 / 28 / 30 / 28 | greater than 60x56 |
| v2-stock-card.png | 40 / 40 / 40 / 40 | greater than 80x80 |

The asymmetric ticket left border keeps the pin unscaled; after horizontal expansion the pin stays at its original distance from the left edge. It is not automatically recentered. The wood sign works best at its native 180px height with width expansion; large height increases visibly stretch the wood grain. The top/bottom borders preserve ropes and studs. The proof deliberately exercises wider/taller rectangles to expose these limits. Bubble, repair chip, timeline shapes, selection patch and buttons should be scaled uniformly; the speed pill has internal dividers and should retain its aspect ratio. Runtime labels, counts, rings and progress fills remain code-owned.

## Provenance and packaging

Each new illustration was generated separately with the built-in image generator, using accepted mockups and, for people, existing deck portraits as references. Exact prompts, source-path receipts and original full-resolution PNGs are retained in `provenance/`. Initial role-icon prompts use the short filenames `pan`, `cloche`, `wrench`, `cup`, `bell` there. No generated text is intended as a UI label.

Mechanical packaging only: alpha-bounds trim, proportional Lanczos resize into the requested canvas, and small transparent padding. Frames also trim faint outer alpha (threshold 8, four-pixel guard). No hue or face repaint, geometry synthesis or vector substitute is used in packaging. `prepare_assets.py` packages newly completed receipts without overwriting reviewed finals; `review_delivery.py` creates aliases, contacts, slice proofs and validates the final receipt.

Four matching existing Catchline kit sprites are reused through proportional trim/downsample: trash, tick, moon and the service fish coin. The generated dollar-symbol coin and first coloured-guests version were rejected and archived under provenance; the selected guests asset uses navy silhouettes. Existing kit originals remain unchanged.

The backdrop is an exception to the transparency requirement: it is a full-bleed opaque scene. Its generator returned **1672x941**, then it was proportionally fitted/upscaled to the requested **2560x1440**. That final canvas is not native generated 2560px detail. Other originals and actual dimensions are recorded per file rather than assuming a uniform generator size.

## Visual and integration limits

The assets follow the navy outline, cream, orange, warm timber and top-left light direction. They are separately generated candidates, not exact extracted copies: face proportions, some silhouettes, bevel thickness, wood grain and food/furniture details vary. Some category icons use coloured objects where the small accepted mockup reads as a navy silhouette. The backdrop has a harbour-water composition and a clearer foreground than the reference's softly blurred restaurant interior. Staff card framing is lighter/gold edged. These gaps remain for lead/Mo review; clean alpha, a complete inventory and opened images do not prove visual acceptance.

No `Assets/` file, `.meta`, `.cs`, Unity project/player, installed build, save or Git state was changed by this art task. The lead owns replacement of temporary crops while retaining their metas, layout fitting, code/tint/progress bindings and native desktop/phone review. No runtime/touch acceptance is claimed here.

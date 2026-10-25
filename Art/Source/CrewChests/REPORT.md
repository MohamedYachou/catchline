# CREW-CHEST-ART-2 delivery

Codex 2 (WSL CLI), 2026-10-25. Artist construction A–F complete. Eighteen transparent PNGs are present here and byte-identical in `Assets/Art/UI/Crew/`. No metas, scripts, scenes or runtime changes; no git operations.

- A: `v2-chest-crew-{closed,open,base,lid,interior}.png`, each512×512. Deep navy lacquer, ivory trim and brass corners; round portrait aperture is genuinely transparent in closed/open/base.
- B: `v2-chest-welcome-{closed,open,base,lid,interior}.png`, each512×512. Smaller sea-green gift with ivory bow/ribbon and brass compass rose.
- C: `v2-tier-1.png` through `v2-tier-5.png`, each96×96. Existing brass palette and Fredoka numeral outlines; inspected at actual28px.
- D: `v2-lock.png`,96×96; `v2-silhouette-mask.png`,256×320, featureless soft navy fisher. Feather RGB is navy throughout; tint mask for contrast if the background is the same navy.
- E: `fx-porthole-glint.png`,128×128, warm-white diagonal sweep. Intended additive blend is SrcAlpha/One. `glint-spec.json` records construction parameters.

## Placement and layers

Chests share the accepted512px canvas, horizontal centre256 and art floor y480. Crew is fitted within448px, welcome within384px to retain its smaller gift scale. Alpha below16 in generated masters was removed before fitting; above248 made opaque. This avoids near-invisible model-generated fringe affecting the art bounds.

Draw base then lid at identical canvas coordinates for the closed state. Both pairs reconstruct their closed PNG with zero RGBA differences. Base includes hidden dark top-plane fill; optional interior overlay includes the same fill. Welcome interior additionally contains the wood/trim repair hidden under the hanging lid clasp; keep the overlay aligned to the stationary base. Its isolated patch is intentional. The clasp travels with the welcome lid. Use the closed coordinate layers for hinge animation, with the static open PNG as the alternate open illustration.

Suggested rear hinge art points, not validated runtime pivots: crew(194,150), welcome(196,231). They are recorded with cut contours in `chest-checks.json`. The independently generated open illustrations have some perspective/body variation; no claim of a seamless transition from rotated closed layers to the open PNG. Native rig tuning remains integration work.

Crew aperture clear bounds: closed/base x126–253,y250–383; open x128–235,y288–398. Closed clear centre(190,310), open centre near(180,340). The brass ring is roughly38% of the projected whole chest width; its clear opening is narrower due to ring width and perspective (closed128px across a448px overall fitted object). Use these actual bounds when fitting a portrait. Put the portrait behind the chest and clip it to the aperture, rather than behind the entire transparent canvas.

## Evidence and limits

`review/sheet.png` was opened and visually inspected after final corrections. It shows every export on #F4EBDA and #1C3A5A, actual28px tier samples, and crew closed/open beside captain closed/open at equal canvas scale. `review/tier-readability.png` gives native96 and actual28px samples. `review/crew-recomposite.png`, `review/welcome-recomposite.png` and zero-difference images preserve layer checks. `delivery-checks.json` records file sizes, SHA256s and alpha counts for all18 exports.

Verified: RGBA and required dimensions; transparent canvas edges; source/Assets SHA256 equality; exact closed layer recomposition for both chests; fully transparent crew aperture centres; opened visual review. The lock's initial faint top-edge resampling fringe was corrected by insetting its SVG and all18 checks rerun successfully. Native HUD placement, portrait clipping, hinge animation and additive shader appearance were not tested. Claude owns integration/metas; Mo/Claude retain native acceptance.

Chest illustrations used built-in image generation with accepted captain references, followed by requested layer extraction, alpha aperture preparation and hidden-surface fill. Generated masters and an earlier study are retained in `generated/`; generation requests are in `prompts.json`. Badge/lock/silhouette SVGs extend the existing source-native icon system and are retained in `svg/`. All new construction stayed within the assigned source/export scope; no temporary backups remain.

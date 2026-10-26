"""Package the concept review and exact prompt history; no image generation here."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
rows=[
('look-options.png','look','Whitewashed stone/blue shutters; teal timber/red roof; harbour brick/green awning. Mo chooses 01/02/03; 01 is provisional.','Matching miniature corner buildings, water-facing terrace and harbour palette. Material texture and props are richer than runtime; roof/window details are not mesh specifications.'),
('exterior-stages.png','stages → stages_fix','Choose how strongly the inherited family building changes from closed house to full-frontage seafood house. Uses look01 provisionally.','Five comparable views: closed, café, bistro, joined-house restaurant, string-lit seafood house. Window contents are illustrative, not an exact countable floorplan; silhouettes are comparable rather than registered CAD cameras.'),
('exterior-night.png','night → night_fix','Choose warm amber occupancy against blue dusk, keeping stage3 expansion.','Joined neighbouring frontage, guests and queue present. Detail/noisy stonework should be simplified for actual harbour distance; the terrace railing is atmosphere rather than a walkability solution.'),
('interior-1.png','interior1 → interior1_fix → interior1_camera','Review the first café’s sparse warmth, navy/ivory appliances, reception and cats.','Two tables/two chairs each; separate fridge, soup kettle, stove, prep and coffee. Camera corrected to a front-down view. Faint grid is not an exact8x5 surveyed layout; horizontal pass explores the original brief, not the newer front-to-back runtime divider.'),
('interior-4.png','interior4 → interior4_fix','Review the full furniture family, booth/trophy wall and kitchen/guest contrast.','Five small indoor tables + booth + terrace table = seven table groups. Grill/fryer/oven/sink-rack/bar visible. Brief14x7 mood study clearly labelled; current plan14x5/low walls takes precedence for implementation. Rendered Mira corrected toward accepted identity; miniature faces remain approximations.'),
('kit-sheet.png','kit','Choose the navy enamel/ivory/honey furniture family and distinct silhouette per job.','All23 requested placeables plus one ship-clothes scale figure. Labels give proposed1x1/2x1 sizes and wall slots, with table4 corrected2x1. Plinths/chairs are illustrative: not measured collision or aisle footprints. Wall-net display has freestanding support in the concept; runtime can mount the net directly.'),
('service-moment.png','service','Review whether the five restaurant jobs read through ship clothes and station positions.','Fishers stove/grill, deckhand plates, hardhat engineer at smoking fryer, navigator coffee, Mira/queue and fish/coffee orders visible. Kitchen worktops/hands visible; waist-high pass can hide legs. No chef/waiter outfits. Crowd spacing and all foot routes unverified.'),
('ui-1-arrange.png','ui-1-arrange → ui_arrange_fix → ui_arrange_grid','Review category drawer, shop cards and local placement confirmation.','One green1x1 ghost under two-chair table; big rotate/cancel/check; clean table4 glyph/label2x1. Room is a mood background, not latest5-deep camera fit.44px targets, finger offset, undo, pathfinding, invalid-state copy and pan require interactive validation; drawer does not prove exact84px implementation.'),
('ui-2-service.png','ui-2-service → ui_service_fix','Review phone hierarchy: clock/arrival curve, stocks, staff and Mira event.','Four ship-clothes role portraits, repair cue and order bubbles. Reception is the in-world desk/event rather than a fifth phone rail slot; actual staff rail should allow Reception. Speed controls and some tabs are visibly smaller than44px; expand hit areas in implementation.'),
('ui-3-mira-plan.png','ui-3-mira-plan','Review Mira-led forecast ranges, catch list and special request acceptance.','Accepted Mira portrait language, dishes/ranges, fish/kg catch list and two special actions. Numbers illustrative; catch yields must be calculated from simulation. Plan card should be composited on the outbound voyage, not treated as a new location.'),
('ui-4-prep.png','ui-4-prep → ui_prep_fix → ui_prep_fillets','Review two-column catch/portions, forecast ticks and margin/captain’s-cut choice.','Coffee removed from catch prep;10 grilled +8 soup +12 fillets =30 portions; fridge30/30 and market2fish cleaned. Controls deliberately enlarged. Fish art depicts finished dishes as category icons; boat prepares raw forms only. Forecast numerical range/market coin value and unavailable-recipe reason still need real data and native layout.'),
('ui-5-closing.png','ui-5-closing','Review tally, reviews, popularity, cats, crew of night and Sleep.','420 dishes +96 drinks +48 tips =564. Unsupported generated reward-unlock text replaced with neutral harbour reputation copy. Names, values and reviews are examples, not economy or crew decisions.'),
('ui-service-desktop.png','ui-service-desktop → ui_desktop_fix','Review desktop spacing: stock left, event right, wider room, five-role rail.','Distinct cook/serve/fix/coffee/reception portraits, rounded title, no chef outfits. Tiny world Mira cap still varies from accepted navy compass cap; reuse accepted Mira asset in production. Crew/world positions and view fit are concept art only.'),
('contact.png','layout.py; seven A–D finals','Compare exterior01/02/03 and small-room warmth/full-room bustle in one glance.','A-D only as brief requests; UI screens are separate full-size PNGs. Contact thumbnails are for selection; inspect full sheets for detail.')]
head='''# RESTAURANT-CONCEPT-1 — concept review

Codex 2 (WSL CLI), 2026-10-26. **Concept delivery; Mo’s exterior choice is pending.** Start with [contact.png](contact.png), then [look-options.png](look-options.png). All output files are source concepts, not game assets or an implemented UI.

Built-in image generation produced the artwork; `layout.py` frames/resizes it, crops the isolated kit cells and adds clean Fredoka labels. It does not repaint scenes. Exact submitted prompts, including initial passes and targeted corrections, follow below and also live in [generation-prompts.json](generation-prompts.json). [generation-receipts.json](generation-receipts.json) preserves tool save receipts. Selected sources and earlier authoring iterations are in `generated/`; final review PNGs are at this directory’s top level. No API/CLI image fallback was used.

## What Mo chooses

1. Exterior01 whitewashed stone/blue shutters,02 teal timber/red roof, or03 brick/green awning. Progression uses01 until selected.
2. Whether the navy-enamel/ivory/honey furniture and warm-window/blue-dusk balance feels like the existing harbour. These are material/mood choices; stage progression and restaurant jobs come from the brief.
3. How much maritime decoration to keep at phone scale. Prefer big trophy/net/lantern silhouettes over the generated tiny masonry/plant details.

## New plan takes precedence when building

The brief initially requested8x5 and14x7 rooms. During this delivery Claude adopted the scale study: **52° orthographic, yaw0, five tiles deep, low cutaway walls, sideways expansion and a front-to-back pass between left kitchen/right guests**. The14x7 sheet remains the requested mood/furniture study and says so on the image. Do not trace its depth, full-height back wall, diagonal/horizontal pass or UI background into runtime. The small image was corrected toward the same frontal camera, but generative pictures do not certify identical projection or metre counts.

See [current restaurant plan](../../../../docs/plans/RESTAURANT.md), especially sections5/10, and the separate [scale study](../../../../docs/screens/restaurant-scale-1/README.md). Codex1 owns native scale evidence; this delivery makes no runtime/touch acceptance claim. Latest diary also records Codex1’s subsequent5-deep native study. No further room redesign or3D production was assigned here.

## Sheet review

Eight review PNGs are2400x1350 (seven A-D sheets and contact). Five phone PNGs are844x390; desktop Service is1440x900. Every final image was individually opened. Filename → exact prompt keys → choice → observed/style limits:

'''
parts=[head]
for name,keys,choice,risk in rows:
    parts.append(f'### [{name}]({name})\n\nPrompt: `{keys}`.\n\n{choice}\n\nReview: {risk}\n\n')
parts.append('''## Consistency and implementation limits

World concepts follow chunky bevelled miniatures, navy/ivory/honey/teal with amber evening light and no global outlines. UI deliberately uses the existing cream physical slabs, navy outlines/planks, orange primary buttons and rounded Fredoka-like lettering. Actual typeset sheet labels use the repository Fredoka font read-only; image-generated UI letters approximate it and must become real UI text. Do not ship raster mockup labels as the interactive interface.

Prompts requested existing ship clothes. Early accidental chef/officer substitutions were corrected in the selected service passes. Accepted ship rigs/portraits and Mira’s accepted navy compass cap remain authoritative; miniature generated faces/caps are not replacements. The kit’s role-scale sailor is reference only.

Kitchen tops and hands are visually readable. That does not prove visible feet or collision-free paths. Later production should use low walls and a front-to-back pass; test door-to-table/pass-to-appliance access, crew congestion, hidden kitchen floor, roof removal and tiny phone bubbles. The pictures provide no projected-tile measurements or44px hit-target certification. Stock numbers, prices, crew names, ratings and forecast counts are illustrative, independent examples between screens; they are not one saved day. Prep and closing local arithmetic was cleaned for readability, but only the simulation should determine yields/economy.

Physical kit bases are presentation plinths, not model geometry to export. Footprints are proposed design labels: appliances1x1; sink/pass/bar/table4/booth2x1; trophy/net/chart wall slots. The plan includes an additional steamer beyond the brief’s23-item kit; it was not silently added to the requested art scope.

## Evidence and reproduction

- [dimensions-and-hashes.json](dimensions-and-hashes.json): all14 final PNG dimensions/modes/SHA256 values.
- [opened-images.json](opened-images.json): human visual observations tied to those exact final hashes.
- [independent-audit.json](independent-audit.json): independent decode/dimension/hash/prompt-source checks.
- [delivery-receipt.json](delivery-receipt.json): file receipt for this source delivery.
- `layout.py`: repeatable framing/clean labels, using the existing `/home/mo/.venvs/catchline-ui/bin/python` Pillow environment. `write_report.py` regenerates this report/prompt appendix.

No Unity, git/commit, Assets writes, .meta/.cs, player save or watchdog operations. New source-art files only; no major original replacement, persistent backup or temporary backup. No subagents or outstanding image generation jobs. Art scope released after DONE in canonical comms.md; no further queue resumed.

## Exact submitted prompt history

The keys below are the literal tool submissions, retained for provenance rather than rewritten after the result. `ui-service-desktop` accidentally began with the literal `undefined`; its image references and explicit desktop spec still produced the selected composition, followed by the recorded identity/title correction. Clean final labels/totals are specified in `layout.py`, not misrepresented as imagegen output.

''')
for key,prompt in json.loads((R/'generation-prompts.json').read_text()).items():
    parts.append(f'### `{key}`\n\n{prompt}\n\n')
(R/'REPORT.md').write_text(''.join(parts),encoding='utf-8')
print(f'Report: {len(rows)} reviewed outputs;24 exact prompts')

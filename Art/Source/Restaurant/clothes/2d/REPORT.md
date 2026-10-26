# RESTAURANT-CREW-CLOTHES-1 — Codex 1 2D delivery

Completed the 2D art scope. No Assets, production code or Git edits. Claude imports/wires these files; Codex 2 owns the separate 3D delivery.

Start with [overview.jpg](overview.jpg). Mira has two review options, with no selection approval implied: [navy dress](mira-a-sheet.png) and [ivory/teal tailoring](mira-b-sheet.png). Her dressed hair, gold pin and fitted clothes mark the host. The pin is pictorial, without a painted name; a readable name belongs to the UI text layer.

## Files and roles

Every ID below has `{id}-sheet.png` (transparent body plus bust), `{id}-front.png` (tight full-body export), `{id}-bust.png` (tight rail export), and `{id}-compare.jpg` (original face, outfit, large bust and an 88px preview).

| ID | Current restaurant job | Outfit |
|---|---|---|
| mira-a | Reception | Navy tailored dress, ivory collar, gold belt/pin |
| mira-b | Reception | Ivory blouse, teal waistcoat, navy skirt, gold pin |
| noor | Waiter | Ivory blouse, navy waistcoat and skirt |
| sam | Waiter | Navy suit, ivory shirt, teal bow tie |
| ana | Waiter | Simple teal dress, ivory collar, navy belt |
| tove | Waiter | Navy short jacket, ivory blouse, teal skirt |
| dirk | Cook | Chef whites, toque and kitchen apron |
| kofi | Cook | Chef whites, toque and kitchen apron |
| rosa | Cook | Chef whites, toque and kitchen apron |
| tess | Cook | Chef whites, toque, apron, visible blonde braid |
| lise | Cook | Chef whites, toque, apron, visible red bob |
| pim | Cook | Chef whites, toque and kitchen apron |
| ines | Barista | Ivory blouse, teal waistcoat, navy skirt |
| mats | Barista | Ivory shirt, navy waistcoat/trousers, teal tie |
| olaf | Handyman | Ivory shirt, navy waistcoat, charcoal trousers, cloth at belt |
| captain | Helper | Navy three-piece suit, ivory shirt, teal tie |

Roster coverage follows the 14 current `Cards.All` identities, RestaurantSim's Mira/Ines/Mats overrides and the captain Helper API. Four legacy non-card deck portraits were excluded. Separate prep/dishwasher characters are not invented into the live card roster. Aprons appear only on cooks.

## Verification and review

- All 16 final sheets and their source comparisons were individually opened. Compared with the native arrange/service phone and desktop mockups, including cream/navy/teal colour, warm light, face/hair distinction, silhouette and 88px bust readability. [visual-review.json](visual-review.json) records the review.
- [audit.json](audit.json) passes 48 RGBA exports, live roster/job agreement, unique variants, tight body/bust alpha bounds, and both native and exported bust dimensions of at least 264px (3x the 88px staff target).
- [manifest.json](manifest.json) gives source identity paths, raw hashes, original dimensions, exact body/bust crops and resize scale. Sheets intentionally contain a transparent gap between the two figures; use the separate tight exports for runtime sprites.
- Alpha is preserved from generation. Fourteen body originals peak at 254, the two Mira originals at 255; all have zero-alpha backgrounds. Audit records each range. No painted pixels or artificial alpha normalization were added.
- Ana's first generation drifted toward Mira and was rejected. The final replacement references Ana's portrait and the restaurant mockup without Mira. The rejected source/receipt remains explicitly named `provenance/ana-rejected-01.*`; never import it. Mira B's bust crop excludes the raised hand.

Commands: `uv run --with pillow python Art/Source/Restaurant/clothes/2d/package.py package`, then `review.py`, then `audit.py` in the same folder. The review script records an already performed human review; running it alone is not visual verification.

## Provenance and integration limits

All character artwork was created with ImageGen, with local reference images. Requests, generation receipts and original PNG copies are retained in this folder and `provenance/`. Pillow only crops, resizes and assembles the review artifacts. `roster.json` describes identities/outfits; Mira requests retain prompt summaries, while the remaining request files preserve full prompt text.

This is an art handoff, with fresh outfit interpretations of existing portraits. It does not prove pixel-identical faces, Unity import, UI placement, player acceptance or completion of Codex 2's 3D work. Claude should select Mira A/B and inspect the busts in the actual staff rail before acceptance. No temporary backups remain in this 2D folder; provenance is intentional delivery evidence.

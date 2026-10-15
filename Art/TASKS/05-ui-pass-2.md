# Task 05: UI pass 2 (2D illustration and icons)

Goal: the game's screens should look like concepts 16-18 and the original Deckhand mockups. Same style rules as task 03: STYLE.md palette, Fredoka, rounded, soft shadow. Export to `Assets/Art/UI/` at 2x with transparent backgrounds, and document everything in `UI.md` and `slices.json`. No Unity, no Scripts or Scenes. Commit and push.

1. **Logo:** the `logo-catchline.png` wordmark (about 1024x384). Chunky rounded letters in navy with a cream outline, a fishing line and hook worked into the "C" or the "h", and a small orange bobber.
2. **Title backdrop:** `title-backdrop.png` (1920x1080). Gull Harbour at golden hour from the game angle (45° down, 35° yaw, bows toward 8 o'clock):
   - the quay, the five shops, the lighthouse, the rowboat
   - calm space in the centre-left for the menu card
3. **Shop headers:** `header-market.png`, `header-harbourmaster.png`, `header-crewoffice.png`, `header-chandlery.png`, `header-supplies.png`. Each 1240x220: a small illustrated scene of the shop's interior or counter, with the shop name in Fredoka.
4. **Fish portraits:** 256x256, side view, `fish-<species>.png` for herring, mackerel, pollock, seabass, conger, plaice and cod, plus `fish-unknown.png` (a navy silhouette with "?").
5. **Item icons:** 256 px, the same family as the task 03 icons:
   - `icon-rodholder`, `icon-bigcooler`, `icon-icebox`, `icon-lunchtin`, `icon-rod-fibreglass`, `icon-rod-carbon`
   - `icon-chart`, `icon-squid`, `icon-fuel`, `icon-net`, `icon-skiff`, `icon-trophy`, `icon-gift`
6. **Sea chart:** `sea-chart.png` (1240x520), an illustrated nautical chart. Gull Harbour is a small town on the land at the left. Five sea areas sit at these normalised positions (x right, y down, measured inside the area right of the harbour):
   - Harbour mouth (0.30, 0.55)
   - Kelp bank (0.42, 0.25)
   - Sandbar (0.50, 0.78)
   - Rocky point (0.70, 0.18)
   - Deep channel (0.88, 0.55)

   Each area gets a recognisable look: a lighthouse, kelp, sand, rocks, deep blue. No text; the game adds pins and labels.
7. **Crew portraits:** 256 px, `portrait-captain`, `portrait-deckhand`, `portrait-fisherman`, `portrait-veteran`. Chibi faces in the concept 15 style.
8. **Feedback sprites:**
   - `coin-pop.png`
   - `sparkle.png`
   - `catch-card.png` (9-slice frame for a "you caught" card)
   - `popup-panel.png` (9-slice dialog with a header strip)
   - `badge-new.png`
   - `daily-gift.png` (illustration, 512)
9. Update `UI.md` and `slices.json`, then push.

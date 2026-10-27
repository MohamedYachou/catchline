# RESTAURANT-DISHES-2

All 13 `DishLook` menu entries already have their own painted dish artwork. No missing drink or side was found, so this pass preserves the accepted paintings and delivers the requested S6/S3 contact sheets. No new image generation, replacement sprite, Assets edit, game-code edit or commit.

- [S6 actual-size contact](s6-contact-actual-size.jpg): every menu painting at all three measured dashboard slots, **84x47, 74x45 and 68x45** logical pixels.
- [S3 actual-size contact](s3-contact-actual-size.jpg): every menu painting in the current plan's **110x75** logical slot.
- Matching `*-contact-3x.png` files retain 3 pixels per logical pixel for close review. Review captions are separate from the icon art. Preserve aspect for every icon.

The requested tea, beer, fries and bread are in the accepted ART-4 parent folder as tight RGBA 3x cuts. Lemonade and coffee are already in `exact/s3-s5/tight/`; grilled fish and soup are there too. All remaining dishes are in the ART-4 parent folder. `manifest.json` records all source paths, imported paths, dimensions, alpha bounds and SHA256 values. No duplicate public filenames were created.

The code's `ArrangeSprite` (VoyageRestaurantUi.cs) prefers the `rx-dish-*` alias when available. All 13 aliases exist on disk. S6 and S3 both call it; the contact sheets therefore use those imported pixels. Nine ART-4 source/import pairs are pixel-identical. The older grilled fish, soup, coffee and lemonade imports have slightly different canvases/edge pixels from their tight source copies; dimensions and alpha bounds are recorded, and both versions remain unchanged. Their existing nominal scale is retained, not relabelled as newly painted 3x art.

At device size, tea's tag, beer's foam/mug, lemonade's citrus/straw, fries' golden pile and bread's sliced loaf/butter are distinct. Warm cream crockery, navy rims and broad painted highlights match the accepted food family. The narrower drinks occupy less width because they preserve aspect; no stretching or arbitrary widening was added.

Checks: independent `audit.py` verifies complete menu coverage, source/import hashes, tight exact-3x ART-4 cuts, all 52 aspect-fit contact placements, decoded proof dimensions, opened-review hashes and preservation of existing PNGs in the captured baseline. Re-run with `uv run --with pillow python Art/Source/Restaurant/exact/dishes/dishes2/audit.py`.

These are saved-image/source checks. Alias-file existence does not prove runtime `HasUi` success; import metadata, native layout, gameplay and final visual acceptance remain Claude/Mo's checks. No missing source-art item remains in this assignment.

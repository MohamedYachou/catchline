# Restaurant table dishes

Five individual FBXs and packed source `RestaurantDishes.blend`. Each FBX contains exactly one static named mesh and one Restaurant_Atlas_Dishes material. Pivots at table contact (Blender Z=0), metre scale, identity transforms. Set the object origin at the table top; no scaling needed. The separate Dishes-V4-check.blend is presentation only; its table/lights/camera never enter the exports.

| Mesh | Width x depth x height (m) | Triangles |
|---|---|---:|
| Dish_FishSoup | 0.214 x 0.214 x 0.103 | 1664 |
| Dish_FilletsLemon | 0.284 x 0.284 x 0.051 | 1628 |
| Dish_GrilledFish | 0.284 x 0.284 x 0.054 | 1476 |
| Dish_CoffeeBiscuits | 0.182 x 0.182 x 0.099 | 2684 |
| Dish_Lemonade | 0.082 x 0.082 x 0.177 | 940 |

- FishSoup: ivory/blue bowl, orange broth, three pale fish morsels and green garnish.
- FilletsLemon: two pale fillets on golden skin, char lines, a solid lemon wedge, herbs, ivory/blue plate.
- GrilledFish: whole grilled fish with head/eye, tail silhouette and char scores, lemon/herbs on matching plate.
- CoffeeBiscuits: dark coffee, ivory/gold cup and handle/saucer, **two** biscuits with dark chips.
- Lemonade: opaque blue glass as in the V4 atlas kit, pale gold liquid top, lemon and straw. No transparent shader required.

`textures/Restaurant_BaseColor.png`, `Restaurant_Surface.png` and atlas.json are byte-identical copies of Stage1V4/textures; no repaint or alternate palette. Both 2048 textures are packed in the source blend. Surface channels R=roughness,G=metallic,B=emission mask. FBX embeds the base colour; separate surface map is supplied for the lead's existing kit shader, since Blender FBX does not export the channel-separation node graph. Every face UV lies inside a single intended atlas cell with at least 16px bleed margin; no unwrapped/white placeholder geometry.

validation.json fresh-imports every FBX and verifies exact mesh/material count, <0.35m bounds, contact height, bounds roundtrip <1e-5m, loaded embedded image and all-face inset atlas UVs. Opened all five final600x600views and table-lineup.png after correcting the soup rim. Blue line now continuous. 1440x600table presentation uses V4 saved camera orientation/58mm lens translated to a closeup, warm/cool studio lights and a1.85x0.5m wooden review tabletop; full-size objects, not a native room screenshot.

Author delivery complete. Unity import/shader binding/table placement remain lead acceptance. No Assets, production code, metas, git operations or subagents.

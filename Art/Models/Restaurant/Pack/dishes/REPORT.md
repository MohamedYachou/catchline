# PACK-DISHES-1 — six source-only plated props

Codex 1 (Windows app), 2026-10-27. Source delivery complete; Unity import and native visual acceptance remain with Claude/Mo. No Assets, game code or Git changes.

## Import contract

Six exact-name `Restaurant_*.fbx` files, one mesh object each, with editable `.blend` assemblies and four adjacent accepted atlas PNGs. FBXs embed their textures as well. Geometry uses metres; Unity Y-up axis conversion is baked. Direct binary FBX inspection verifies zero root translation/rotation, unit scale, Y-up and UnitScaleFactor 100. Blender's FBX importer restores a 90-degree axis conversion, which is separate from the file's identity local transform.

The origin is the bottom centre of the complete dish AABB, ready to rest on a table. No table, camera, light, helper hierarchy or animation is exported. Disconnected food and crockery components are joined into one mesh, retaining material slots and UVs. Pack sources and accepted recipe sources are unchanged.

| Exact filename stem | Pack components | Width × depth × height |
|---|---|---|
| Restaurant_Dish_GrilledFish | Kenney plate, whole fish, lemon-half; KayKit lettuce garnish | 22 × 22 × 5.4 cm |
| Restaurant_Dish_FilletsLemon | Kenney plate, two salmon toppings with rice removed, loose fries with carton removed, lemon-half | 22 × 22 × 5.1 cm |
| Restaurant_Dish_FishSoup | Kenney plate, bowl-soup, utensil-spoon, two small salmon topping pieces | 22 × 22 × 7.7 cm |
| Restaurant_Dish_CoffeeBiscuits | Kenney cup-saucer, cup-coffee, cookie | 15 × 15 × 8.5 cm |
| Restaurant_Dish_Lemonade | Kenney soda-glass, lemon-half; accepted lemonade colour atlas | 7.8 × 6.7 × 15 cm |
| Restaurant_GrilledFishPlate | Exact same mesh positions, polygons and UVs as the served grilled-fish plate | 22 × 22 × 5.4 cm |

`manifest.json` records component source paths, sizes, rotations, bottom-centre offsets and evaluated source-to-assembly matrices, plus final bounds, triangles and FBX hashes. The six files total **3,696 triangles**.

## Appearance and scale notes

- Existing runtime mapping in `RestaurantWorld.cs` shares GrilledFish with crab/calamari, FilletsLemon with platter/fish-and-chips/fries, CoffeeBiscuits with tea/bread, and Lemonade with beer. This delivery preserves those exact model stems and does not change that mapping.
- Whole fish uses the accepted roasted atlas. It has a browned low-poly fish silhouette without a new grill-score texture. Salmon keeps its original pale bands; fries and lemon keep natural food colours. Lettuce is from KayKit Restaurant Bits.
- Soup retains the Kenney vegetable broth and adds visible salmon pieces. The spoon is rotated along its actual source long axis before sizing, and sits beside the bowl. Bowl height is 7.7 cm including its plate, intentionally taller than the approximate 5 cm flat-meal class.
- Coffee's cup is 7.5 cm tall; its saucer brings the assembly to 8.5 cm. The glass including straw is 15 cm tall.
- The old Stage1V2 carried plate is approximately 28 cm across. These plates use the current brief's 22 cm target. Reference dimensions are measured in `geometry-audit.json`; hand-pose fit in the native game remains unverified.
- Accepted `food-colormap-catchline`, `-roast`, `-lemonade` and `restaurantbits_texture-catchline` are copied byte-for-byte beside the FBXs. No new palette or source geometry edits are introduced. The salmon/fries subsets are the accepted KENNEY-FIT derivatives.

## Visual evidence

Open **contact-table.jpg** for all six fresh-FBX imports separately resting on a KayKit round table, or **contact-detail.jpg** for equal-scale food closeups. Twelve individual PNGs are in `renders/`. Both final contacts were opened and inspected after correction.

The proof table matches PACK-ITEMS' round table sizing, **0.54 m diameter × 0.69 m high**, with the accepted warm restaurant atlas. Props rest at 0.692 m, a deliberate 2 mm clearance above its top. Camera pitch is 38 degrees, yaw offset 2 degrees, lens 58 mm, matching the game's viewing direction; proof framing is a closer inspection view. All dishes have the same framing within each sheet. These are standalone Blender Eevee renders, not Unity captures. No table clipping is visible. Native room lighting, seating and server hand fit remain Claude's checks.

## Verification

- `mesh-audit.json`: PASS six fresh FBX imports, one mesh each, finite/bottom-centred bounds, roundtrip dimensions, UVs, valid embedded images, expected Blender axis restoration, unit scale and manifest hashes.
- `fbx-transform-audit.json`: PASS six direct binary FBX inspections: one root Model, identity local transforms, Y-up, metre units.
- `geometry-audit.json`: PASS exact six models, 22 cm plate widths, 15 cm glass, bottom-centred pivots; independent vertex/polygon/UV hashes prove carried and served fish plates identical. Incumbent dish dimensions included.
- `audit.json`: PASS exact six names, 3,696 triangles, four unchanged accepted atlases, all referenced component paths present, 14 decoded proof images, **4,253 original files unchanged**.
- `visual-review.json`: final opened contact hashes and observations.

Blender 5.2's material deprecation warnings can make PowerShell report exit 1 despite completed exports/renders. Completion is established by the final generated files and independent audits, not the shell status alone.

## Reproduction

Run from the project root with standalone Blender 5.2 and `uv`:

1. `blender -b -t 6 --python Art/Models/Restaurant/Pack/dishes/build.py -- 0:3`, then `-- 3:6`.
2. `blender -b -t 6 --python Art/Models/Restaurant/Pack/dishes/review.py`.
3. `uv run --with pillow python Art/Models/Restaurant/Pack/dishes/package.py`.
4. Run `audit_models.py`, `check_fbx.py` and `audit_geometry.py` with Blender, then `audit_delivery.py` with `uv run --with pillow python`.

Do not regenerate `preservation-baseline.json` during verification. Temporary Blender `.blend1` backups from the soup correction were removed after final verification. Original Kenney/KayKit CC0 licenses remain in their downloaded packs.

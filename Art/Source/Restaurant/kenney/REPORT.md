# KENNEY-FIT-1 — source handoff

Owner: Codex 1 (Windows app). 2026-10-27. Source selection, palettes and standalone Blender proofs only. No Assets, gameplay code or Git changes.

## Review first

- `dish-contact-tables.jpg`: all 13 menu dishes on the same KayKit round table.
- `dish-contact-details.jpg`: closer views at the same camera pitch.
- `decor-contact-1.jpg`, `decor-contact-2.jpg`: original / Catchline material comparisons, complete models.
- `palette-map.jpg`: food atlas before/after and furniture material colours.
- `dish-map.json`: every `RestaurantData.Dish` entry, source model paths, metre dimensions, offsets, rotation, evaluated scales and baked source-to-meal matrices.
- `decor-map.json`: 13 decor choices, source GLB/FBX paths, sizes and proposed locations. These are suggestions for fixed spots; no room placement was changed.

## Dish choices

| Game dish | Model/composition | Limitation |
|---|---|---|
| GrilledFish | Kenney fish + plate + lemon-half, dedicated roasted-fish palette | Whole fish silhouette; no grill-mark detail. |
| PanFish (Fillets) | Salmon topping from sushi-salmon + plate + lemon | Rice removed; retains the original salmon mesh and UVs. One game dish, not a second fillets entry. |
| FishAndChips | Salmon topping + loose fries + plate + lemon | Unbattered salmon is a visual proxy. A battered cod model remains an art gap. |
| Soup | Kenney bowl-soup | Vegetable-style soup proxy; no fish chunks. |
| Platter | Fish + two mussel-open models + lemon on plate-rectangle | Pack composition; not a bespoke seafood platter. |
| Crab | Existing Catchline CrabBody + plate + lemon | Neither downloaded pack has a crab. This is explicitly a Catchline fallback, including its stylised eyes. |
| Calamari | KayKit food_ingredient_onion_rings repeated on a plate | Gold battered-ring geometry reused for calamari. |
| Coffee | cup-coffee + cup-saucer | Pack coffee. |
| Tea | cup-tea + cup-saucer | Pack tea. |
| Lemonade | soda-glass + lemon-half | Dedicated pale-gold liquid palette; apply only to this drink. |
| Beer | Kenney mug | Empty tankard supplemented with two declared 8-sided liquid/foam cylinders. |
| Fries | Loose contents of Kenney fries + plate | Carton mesh removed, original fry geometry retained. |
| Bread | loaf-baguette + bread + plate | Pack bread composition. |

The complete numeric recipe is in JSON; do not infer transforms from this table. `derived/salmon-fillet.glb` and `derived/fries-loose.glb` are deterministic subsets of the originals. Their triangle positions and UVs are checked against source meshes by `audit_meshes.py`.

## Decor and palette

Selected: pottedPlant, plantSmall3, lampWall, lampRoundFloor, lampRoundTable, bookcaseOpenLow, bookcaseOpen, bench, benchCushion, rugRectangle, rugDoormat, coatRackStanding, and KayKit pictureframe_medium. Shelves and plants suit the rear dining wall; lamps warm booth/host corners; benches suit the quay or booth edge; the doormat belongs inside the entrance. Keep rugs out of kitchen work areas and the coat rack clear of the queue. Larger bookcase is suggested for Bistro and later.

Kenney Furniture uses named flat materials, not an atlas. `furniture-materials-catchline.json` supplies sRGB overrides: warm wood, navy/teal fabric, cream, muted green foliage, light steel and warm lamp diffusers. Convert sRGB to linear before assigning shader base factors. Reference `derived/decor-*.glb` already embeds the overrides. The KayKit picture frame uses the previously accepted Catchline furniture atlas.

The three food atlas variants retain the original 512×512 layout and alpha:

- `food-colormap-catchline.png`: warm cream crockery, teal purple trim; natural orange/brown/yellow/green food stays unchanged.
- `food-colormap-lemonade.png`: opt-in pale-gold replacement for the soda-glass liquid swatch.
- `food-colormap-roast.png`: opt-in warm cooked-fish skin replacement.

Do not globally replace the original atlas with the lemonade or roast variant. No downloaded source was overwritten.

## Coordinates and camera

Source proof uses metres, Blender Z-up. Meal origins are tabletop/bottom-centre; JSON Unity offsets are `[x,z,-y]`. Table reference is KayKit `table_round_A`, normalised to 0.95 m diameter and 0.76 m height. Every component records its evaluated Blender scale, rotation, bounds and mesh matrix. Raw FBX importer axes/scales can differ: reproduce evaluated bounding-box normalisation or use the baked composite as the reference, rather than copying Blender scale onto a raw Unity FBX transform.

`derived/dish-*.glb` contain the plated meal without the table, floor or lights. `derived/proof-*.blend` retain the table/camera proof. The GLBs are source interchange/reference artifacts; this delivery does not install a Unity GLB importer or prove a Unity import.

Camera follows `RestaurantWorld.cs` pitch 38°, with a 2° yaw offset and 58 mm lens. Table and detail proofs move closer for legibility; they are not captures from the whole-room camera position. Decor proofs frame each complete object individually.

## Reproduction and verification

Run from repository root (Blender 5.2; Pillow through uv):

```powershell
uv run --with pillow python Art/Source/Restaurant/kenney/build_palette.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b -t 6 --python Art/Source/Restaurant/kenney/build_fit.py -- dishes
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b -t 6 --python Art/Source/Restaurant/kenney/build_fit.py -- decor
uv run --with pillow python Art/Source/Restaurant/kenney/package.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b -t 6 --python Art/Source/Restaurant/kenney/audit_meshes.py
uv run --with pillow python Art/Source/Restaurant/kenney/audit_delivery.py
```

`inspect_pack.py` / `inspect_more.py` record source inventory and selection evidence. The original download baseline in `preservation-baseline.json` was recorded before palette/model work; preserve it rather than regenerating it for a preservation check.

Final checks PASS: all 13 enum dishes covered; 26 meal/decor GLBs freshly imported with correct dimensions, bottom pivots and available embedded images; 52 render PNGs and five review sheets decoded; 2,555 original Kenney file hashes unchanged. Salmon subset (52 triangles) and fries subset (480 triangles) exactly retain original triangle positions and UVs. All food variants preserve 512×512 layout/alpha; 64,545 tested natural orange/brown/yellow/green pixels stay unchanged. Final contacts were opened and visually inspected after fixing caption spacing.

Check records: `mesh-audit.json`, `audit.json`, `visual-review.json`. Blender 5.2 logs include API deprecation warnings and a shared-texture sampler warning on the KayKit frame; fresh imports have valid images and the final frame comparison is visually correct. Temporary rerender backups and the stale draft contact were removed after verification. Native import, room placement, on-device legibility, rendering cost and player acceptance remain Claude/Mo's integration checks.

Both Kenney packs and KayKit packs carry local CC0 licenses in their download folders. Original files and license files remain in place.

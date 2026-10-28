# Catchline high-fidelity art contract (HIFI)

Mo, 2026-10-28: "the game is still nowhere near visually as the renders. Aside from the crew, which I will provide at
very high quality, the visuals still aren't there. I can't put very high quality crew in super low poly surroundings.
I need Codex at xhigh doing a way better job, not low poly in mind."

This contract overrides the low-poly parts of `Art/STYLE.md` (chunky facets, flat colour blocks, the <2,000-triangle
prop budgets, the flat-swatch `Catchline/RestaurantAtlas` look). STYLE.md still holds for palette, axes, pivots, world
scale and camera.

## The bar

The two reference renders are the target, at 1:1, seen from the gameplay camera:
`Art/Concepts/References/day03-small-boat.png` and `day28-tuna-boat.png`. Zoom into them before modelling anything.
Proportions stay warm and toy-like and silhouettes stay chunky and readable, but every surface is a crafted, believable
thing:

- Wood: individual planks with rounded edges and real seams, grain, knots, per-plank value variation, darker weathered
  ends, nail and bolt heads. The day03 deck is about forty planks across.
- Paint on wood and metal: soft bevelled edges that catch the light, chipped and worn paint on the edges, soft grime in
  recesses. Rust only as faint accents.
- Small fittings everywhere they belong: cleats, rings, chain, rope coils with twisted strands, bolts, hinges, handles,
  tyre fenders with tread, lifebuoys with their rope loops.
- Curved forms are smooth: enough segments, smooth or weighted normals. Nothing reads as faceted low poly.
- Detail lives inside the silhouette and must read at the gameplay camera. Noise that only shows in a close-up is wasted;
  a flat colour block where the reference has planks, seams and wear is a failure.

The question for every delivery is "would this sit inside the reference render without looking cheaper?", never "is it
better than the old model?".

## Budgets (LOD0, per asset)

| Asset | Triangles | Textures |
| --- | --- | --- |
| Hull with its fixed fittings | 30k–60k (rowboat, skiff), up to 120k (big hulls) | 2048² sets, ≥ 512 px per metre |
| Deck prop, furniture piece | 1k–15k | 1024² set, or a shared 2048² sheet |
| Room shell, environment section | up to 200k for one screen | tiling 2048² materials plus a baked 2048² AO/detail set |

These are ceilings to spend, not targets to hit. Spend triangles on silhouettes, bevels and fittings, not on flat areas.

## Materials and textures (the runtime contract)

Author physically based metal/rough materials in Blender (procedural is fine) and bake them to images:

- `<Set>_BaseColor.png`: sRGB. The STYLE.md palette stays the dominant hue; detail is value variation, wear and grain,
  not hue noise. No lighting or floor shadow baked in.
- `<Set>_Normal.png`: tangent space, OpenGL convention (+Y up), as Blender bakes it.
- `<Set>_Mask.png`: linear. R = metallic, G = ambient occlusion baked from the model itself, B = 0, A = smoothness
  (1 − roughness).

Tiling surfaces (planks, stone, tiles) may use tiling sets; say so in the manifest.

Every material in the FBX is named `MH_<Set>`, one per texture set. Never name a HIFI material `M_<palette>`: the
runtime flattens those to a solid colour. No outlines, no vertex-colour-only surfaces.

Manifest beside the FBX, `<Asset>.hifi.json`:

```json
{ "asset": "Rowboat", "materials": [
  { "name": "MH_RowboatHull", "set": "RowboatHull", "tiling": [1, 1] },
  { "name": "MH_DeckPlanks", "set": "DeckPlanks", "tiling": [3, 1], "tiles": true } ] }
```

## Files and export

- Runtime: `Assets/Art/Models/Hifi/<Asset>/<Asset>.fbx`, `<Asset>.hifi.json`, `Textures/<Set>_{BaseColor,Normal,Mask}.png`.
- Source: `Art/Models/Hifi/<Asset>/` (the .blend, the build script, review renders, audit JSON, REPORT.md).
- FBX: Y-up metres, transforms applied, positive scale, normals exported, no embedded textures, no cameras or lights.
- Claude's importer (`Assets/Editor/HifiImport.cs`) builds the URP Lit materials into a `Materials/` folder beside
  the FBX and remaps the FBX onto them; never write that folder. `Assets/Art/Models/Hifi/_Probe/` is the smallest
  working example of the whole contract.
- HIFI assets live beside the old ones. Never overwrite or delete an existing model. Claude swaps the game over after
  checking the asset in the running game.
- A replacement keeps the old model's contract exactly: the same pivot, axes and outer bounds (within 3 cm), the same
  walking/deck plane, and every named node the code uses, with the same name, parent and pivot. List them in the audit.

## Done = evidence

Save under `Art/Models/Hifi/<Asset>/review/` and open every image before calling an item done:

1. `<asset>-game-camera.png`: 1440×900 from the real gameplay camera (orthographic; the brief gives the numbers), warm
   sun from the upper left, cool sky fill, on a teal sea or the real floor, beside a crop of the reference at the same
   on-screen scale (match plank width or a 1 m crew height).
2. `<asset>-turntable.png`: front 3/4, back 3/4, side and top, so no angle hides a bare side.
3. `<asset>-textures.png`: the texture sets as a sheet.
4. `<asset>-audit.json`: triangles per object, bounds, pivot, texture sizes, material names, the preserved node names
   and their transforms compared with the old model.

Write one honest line in REPORT.md about where the asset still falls short of the reference.

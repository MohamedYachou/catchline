# KAYKIT-PALETTE-1

Codex 1 (Windows app). Source texture delivery; Unity import and native appearance remain Claude's checks.

## Import targets

- `restaurantbits_texture-catchline.png` — 1024x1024 RGBA, original 8x4 swatch layout, 128x256 pixels per cell.
- `furniturebits_texture-catchline.png` — 1024x1024 RGBA, original layout including inset highlights and reversed bottom-row gradients.

Use each texture on its corresponding pack's shared material with a white material tint. These are sRGB base-colour textures, not normal maps. Keep the original UVs, original material sampler/wrap settings and model geometry. This delivery does not change any Assets importers or `.meta` files.

## Palette decisions

Restaurant: R4C7 diner-orange table/chair/counter surfaces become honey wood (`#DFB77A` bright, `#8C5A36` shade). R2C3 mint fridge/lower walls become restrained teal (`#64C7C4` to `#126773`). R2C2 red oven/paint accents become navy (`#2A6685` to `#102F43`), spanning the house navy `#173F57`. R4C6/R4C8 cabinet paint becomes cream (`#F4EFE3` to `#B8B09C`). All other 27 cells remain byte-identical, including every food/ingredient swatch, steel, glass, and shared brown/beige cells.

Furniture: 17 cells move to honey timber, lighter shelf/frame timber, navy and teal upholstery, cream drawers/linen/lampshades. Steel, terracotta, foliage, deep neutrals and the bottom-row effects remain unchanged. Insets and shaded strips keep their original locations. Adjacent cells of the same original material receive the same transform.

Important shared-UV limit: restaurant R1C7 serves both brown wood and cooked meat, while R2C6 serves both wall beige and onions. They deliberately remain unchanged. A few brown timber objects/sills therefore keep the original warm brown. Recolouring those further requires a separate UV/material decision by the model owner. The orange counter/table swatch is separate from carrots, so no such tradeoff was needed there.

## Evidence

- [SWATCH-MAP.md](SWATCH-MAP.md): all 64 cells, bright/shade endpoints and reasons; machine-readable version `swatch-map.json` includes rects and example model uses.
- `restaurant-swatch-map-1.jpg`, `restaurant-swatch-map-2.jpg`, `furniture-swatch-map-1.jpg`, `furniture-swatch-map-2.jpg`: readable original/new cell pairs.
- `restaurant-atlas-before-after.jpg`, `furniture-atlas-before-after.jpg`: full-resolution atlas comparisons.
- `restaurant-fbx-before-after.jpg`, `furniture-fbx-before-after.jpg`: actual unchanged Unity FBXs rendered with original versus exported atlas, identical lighting/camera. Sixteen representative models; `fbx-proof-inventory.json` names them. Object scale is normalized only for this proof layout. This is a source render, not a Unity capture.
- `restaurant-sample-before-after.jpg`, `furniture-sample-before-after.jpg`: flat ImageGen sample recolours, **illustrative palette studies only**. They can recolour shared brown surfaces differently from the exact atlas and are not UV or pixel-preservation evidence. Their PNGs are retained as requested optional mocks.

## Method and reproducibility

Final atlas export uses deterministic per-cell colour remapping of the original per-pixel ramp value, with specified bright/shaded RGB endpoints and nearest integer quantization. No spatial filtering, cropping, resizing, flipping, painting, noise or grain is applied. Original alpha is unchanged. This preserves each swatch's light-to-dark progression and the furniture's inset details. The two optional sample images use built-in ImageGen; prompts and original output paths are recorded in `generation.json`.

`inspect_sources.py` records cell uses from OBJ face-centroid UVs (diagnostic examples, not an exhaustive polygon rasterizer) and seals 1,214 downloaded pack files. `build_palette.py` exports the atlases/maps; `render_uv_proof.py` runs in standalone Blender with original Unity FBXs read-only. `audit_palette.py` independently checks output dimensions/alpha, unchanged cells, gradient correlations and inset edge support, source hashes and image decodability, and builds labelled comparison sheets. Use `uv run --with pillow --with numpy python <script>` for the Python scripts; invoke the render script with standalone Blender `--background --factory-startup --python`.

All work is additive inside this folder plus the append-only project diary. No production source replacement required a backup. No Assets, game code, model, git commit or native scene changes are included. No gameplay or player visual acceptance is claimed.

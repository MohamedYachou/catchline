# Mira / Sol — MIRA-R10, final r16

Codex 2 (WSL CLI), 2026-10-24. Built from Mo's approved r09, with a new rear hairstyle and reusable clothed female silhouette. Final delivery: `Mira.blend`, `Mira.fbx`, `Mira_Face.png`, `Mira_Hair.png`, and `Mira-review.png`. The complete final render set is in `iterations/r16/`.

## Changes and preservation

The flat rear hair shell and block ponytail were replaced by a corrugated rear scalp, four individually tapered overlying layers, twelve narrow flattened wavy ponytail locks across three depth layers, a small inner volume, and three fine loose ends. Curl sections are elliptical rather than round ropes. The rear colour texture follows the strand direction; it contains no baked lighting. All hair is ordinary skinned geometry, without particles, alpha sorting, simulation or extra bones.

The approved front crown, fringe, face-framing locks and their highlights are copied directly from r09: 1,358 vertices and their faces, material assignments, colours and weights. The face, eyes, cap, head scale and original face PNG are unchanged. `r10-validation.json` records the independent preservation audit. r09's source, export, texture, builder and contract were archived under `iterations/r09/` with `archive-sha256.json`; its existing eight renders were retained.

## Shared female body

`Art/Source/crew_female_shape.py` is the reusable, Blender-independent deformation module, version `CrewV2-female-1`. It changes the clothed bind shape, rather than adding a second skeleton. The waist narrows by up to 10%, the coat hip area widens by up to 8% and deepens by up to 7%, and a broad, modest chest form adds at most 12 mm under the clothing. Upper trouser hips widen by up to 6% and deepen by up to 8%, blending out before the knees. No vertex height, vertex index, weight or bone changes. Arms, hands, head and boots retain their original shape.

The same deformation is applied to tailoring and torso accessories so buttons, lapels, straps and binoculars follow the coat. The independent audit measures 764 coat/trouser vertices and 638 tailoring/prop vertices changing by more than 0.00000001 m. The sheet compares the original male garment shape on the left and the female shape on the right, in front and profile, at identical scale. No existing male asset was modified.

Later women's builders can use:

```python
from crew_female_shape import female_shape, region_for_weights

region = region_for_weights(weights_by_bone_name)
if region is not None:
    bind_position = female_shape(bind_position, female=True, region=region)
```

Apply this once to every torso garment and its attached tailoring/props in the original CrewRig bind coordinates. Apply the `hips` region to proximal trousers. Skip head meshes and do not apply twice. `female=False` is exactly the original male shape. The overlay builder exposes `--female` / `--no-female`; its default is female. Only Mira has been built with this module in this assignment; future role garments still need their own pose review.

## Budget, materials and rig

| Mesh | Triangles |
| --- | ---: |
| Face | 2,300 |
| Eyes and expression | 2,500 |
| Hair, including preserved front | 6,482 |
| Officer cap | 2,692 |
| Coat, trousers, hands and boots | 4,300 |
| Tailoring, jewellery and binoculars | 1,700 |
| **Total** | **19,974** |

Two 512 × 512 PNGs, 524,288 texels in total, below the combined 2048² allowance. `Mira_Face` uses the original face texture; `Mira_Hair` uses the new rear strand texture. Both PNGs sit beside the FBX and use relative paths in the saved blend. Existing flat part palette materials are retained; `build-manifest.json` lists their names and hex colours. New rear hair uses chocolate brown `#48271D` with restrained tonal variation.

The original 20-bone CrewRig, hierarchy, rest matrices and all 11 source actions remain unchanged. Existing vertex weights are identical to r09; new rear hair is rigidly weighted to `Head`. The actions are Idle, Walk, Carry, Bait, Cast, Wait, Strike, Reel, Row, Cheer and Stow, at 24 fps. The source uses metres, X right / −Y forward / Z up, bare scalp approximately 0.95 m, and a floor pivot between the boots. FBX export follows the CrewRig settings: −Z forward / Y up, unit scale, no added leaf bones, all actions baked without key simplification.

## Verification

Both final r16 audits **PASS**: `validation.json` and `r10-validation.json`. The first independently compares the saved source with the original CrewRig, then imports the actual FBX into an empty Blender scene and checks the mesh budget, weights, hierarchy, action ranges, texture paths, bind bounds and 44 sampled animated poses across all 11 actions. Maximum FBX bone-position error is 0.000000105 m; maximum mesh-bounds error is 0.000000179 m. All weights are normalized, with at most two influences per vertex. The second compares r09 directly with the final source: front geometry/materials/weights, face PNG, every non-hair weight, unchanged vertex heights, the reusable female field, male identity flag, and actual FBX rear texture resolution. Female-field discrepancy is below 0.000000008 m; every archived r09 file hash matches.

The final render set includes front, three-quarter, side, back, face and rear-hair close-ups; original male/female silhouette comparisons; the current deck captain beside Mira at the same scale; Idle frame 13, Walk frame 7, Carry frame 7 and Cast frame 17, plus side views of the three active poses. `Mira-review.png` contains the requested views and supplied portrait/full-body references. These are Blender visual checks; Unity integration and Mo's acceptance remain with Claude/Mo.

## Honest gaps

The drawing's painted hair highlights and very fine curls are approximated with a compact sculpt and colour texture. The ponytail remains more angular at extreme close range than the illustration, and the rear silhouette is intentionally composed of visible locks. Hair follows the head rigidly and has no secondary motion. The face, cap and existing front hair retain their approved r09 stylisation rather than being redesigned. The female tailoring is deliberately subtle under the pea coat. Representative rendered poses and sampled export poses do not constitute an exhaustive collision proof for every interpolated animation frame or future outfit.

## Reproduction

Use Blender 5.2 headlessly from the project checkout:

```text
blender --background --factory-startup --python-exit-code 1 --python Art/Source/build_mira_r10.py -- --revision r17 --render all --samples 48
blender --background --factory-startup --python-exit-code 1 --python Art/Source/validate_mira_sol.py
blender --background --factory-startup --python-exit-code 1 --python Art/Source/validate_mira_r10.py
python Art/Source/compose_mira_r10.py --revision r17
```

The builder always starts from immutable `iterations/r09/Mira.blend` and the archived r09 primitives; it does not accumulate deformations between rounds. Use a fresh revision name to preserve the reviewed r16. The final round also contains a snapshot of the overlay builder and shared female module. No generation calls/credits, Assets, game source, Unity or git changes were used for MIRA-R10.

# Rosa — detailed female crew

CREW3D-WOMEN / Codex 2 (WSL CLI), 2026-10-24. Revision **r01**, **19,949 triangles**. Delivered for Claude/Mo review; native integration and likeness acceptance remain separate.

Files: `Rosa.blend`, `Rosa.fbx`, `Rosa_Face.png` (512² RGB), `Rosa_Hair.png` (256² RGB), `Rosa-review.png`, `build-manifest.json`, `validation.json`, and individual rendered views under `iterations/r01/`. Combined texture area 327,680 pixels, below 2048²; colour-only skin/blush/fibres, no baked lighting.

The role is **Fisher**. Hair design: **pixie**, base colour `#45281B`. Reference is the approved portrait-rosa.png. Outfit follows the fixed role palette, including hat, garment and role accessories. Hair uses thin flattened layered clumps with tapered ends and continuous UVs, not round rope strands. All hair is rigidly Head weighted; no particles, simulation or image-to-3D credits.

## Reusable female body

`Art/Source/build_crew_female.py` reads per-character settings from `crew_female_settings.json` and uses the same `crew_female_shape.py` / CrewV2-female-1 deformation field as approved Mira r16. It narrows the waist, widens/deepens the hips slightly and adds a modest chest form under clothes. The builder applies the field exactly once to torso/hip vertices and garment details, by original weight region. Head, limb attachments, height, bone positions and weights remain unchanged. All eight women share this path; men never receive this field. `crew_female_hair.py` provides the per-style layered hair construction.

## Verification

Independent validator reopened the saved Blend, then imported the actual delivered FBX into a fresh scene. PASS: <=20k triangles, identical original 20 bones/hierarchy/rest matrices, all 11 unchanged source action digests, normalized weights, floor pivot, 0.95m bare scalp, metre scale, 24fps, valid texture paths/UVs and source/export geometry. Across 44 pose samples, maximum FBX bone position error 0.00000010m and mesh bounds error 0.00000024m. Details and delivery hashes are in `validation.json`.

Source axes X right, -Y forward, Z up. FBX uses original axis settings (-Z forward/Y up), metre scale, all actions and no leaf bones. Review studio is excluded. The Blend opens in Idle frame 1.

Review sheet contains front/three-quarter/side/back, rear hair close-up, face beside reference, same-scale original crew/Mira/Rosa, Walk/Idle and Carry/Cast frames. Visual likeness and clothing clearance are checked from these selected rendered poses; the numerical pose audit is a rig/roundtrip check, not an exhaustive collision test.

## Hair coverage review

`hair-coverage-hits.json` records 396 radial rays at 10-degree intervals over eleven heights (0.705–0.905m), with 293 anatomical scalp samples and **zero skin-first hits**. Every ray and exposed-face/hairline exclusion is listed. Ears, nose and neck are excluded from the scalp by connected-mesh identity. `Rosa-hair-review.png` shows six actual headshots from the supplied review script, including both sides and the nape. This is sampled coverage evidence, supplemented by the rendered views, not a continuous mathematical guarantee.

## Honest gaps

The short pixie is layered opaque locks. The eyebrow scar is shallow pale geometry. Fine painted edge wisps and skin detail are approximate.

Fixed facial expression; no face bones, hair physics, cloth simulation or finger articulation beyond the existing mitten design. No Unity playback, mobile performance or Mo acceptance is claimed.

Reproduce from project root with Blender 5.2:

```text
blender --background --factory-startup --python Art/Source/build_crew_female.py -- --name Rosa --revision r01 --render all --samples 32
blender --background --factory-startup --python Art/Source/validate_crew_female.py -- --name Rosa
python Art/Source/compose_crew_female.py --name Rosa
```

No Assets, game source, Unity, male outputs, original CrewRig or git changes by this task.

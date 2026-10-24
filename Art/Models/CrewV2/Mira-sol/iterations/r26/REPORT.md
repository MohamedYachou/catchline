# Mira — full hair rework

Codex 2 (WSL CLI), 2026-10-24. Revision **r26**, **19,940 triangles**. For Claude/Mo review; no new likeness approval or native Unity acceptance is claimed.

Authority: Mo's UPDATE16:55 in `Art/Source/UIv2/FIX-CREW3D-HAIR.txt` unlocks the entire hair, including the front. The old r20 front-only lock is superseded for this work. Immutable `iterations/r20/` retains its original source, FBX, textures, manifest and renders for comparison. All five new nonhair meshes (face, eyes/expression, cap, body/clothes and accessories) have exactly the same coordinates, topology, material slots, smoothing, UVs and skin weights as archived r20. Face texture bytes are unchanged; independent fingerprints and archive SHA256 values are recorded.

New dark-brown hair uses individually curved shallow elliptical locks, colour-only fine fibres, continuous fitted temple/nape coverage, and a full-depth gathered ponytail with outer and inner rings of wavy locks. Both sides and the back are modeled, with hooked ends and roots tucked beneath the cap. Hair is rigid Head-weighted. It has no simulation. Compared with the painted portrait the silhouette, curls and flyaways remain simplified; strand intersections and opaque pointed tips can be seen in close-up. Hair/face likeness is subject to Mo's review.

Delivered: `Mira.blend`, `Mira.fbx`, unchanged 512² `Mira_Face.png`, new 512² colour-only `Mira_Hair.png`, manifest, `validation.json`, `hair-coverage-hits.json`, `Mira-review.png`, `Mira-hair-review.png`, and seventeen individual render views plus six supplied-script headshots under `iterations/r26/`. Texture area 524,288 pixels, below 2048²; no baked illumination.

Independent validation reopens saved source and actual exported FBX: original 20 bones/hierarchy/rest matrices, eleven exact source action digests, 44 sampled animation poses, normalized weights, original metre scale/floor pivot/0.95m scalp and valid face/hair UVs with resolved texture hashes. Maximum sampled FBX bone position error 0.00000010m; bounds error 0.00000018m. Source axes X right/-Y forward/Z up, original FBX -Z forward/Y up. Studio excluded. Saved source opens in Idle frame1. This proves rig/export integrity rather than exhaustive pose collision freedom.

Scalp coverage: 396 radial rays, every10degrees at eleven heights0.705–0.905m, 304 anatomical scalp samples, zero skin-first hits. Every distance and natural exposed-face/hairline exclusion is saved. Ears/nose/neck separated by connected component. Six supplied-script views include both sides and nape. Sampled coverage plus selected renders is not a continuous mathematical guarantee.

Reproduce using Blender5.2:
```
blender --background --factory-startup --python Art/Source/build_mira_hair_v2.py -- --revision r26 --render all --samples 32
blender --background --factory-startup --python Art/Source/validate_mira_hair_v2.py
blender --background Art/Models/CrewV2/Mira-sol/Mira.blend --python docs/screens/crew-review/headshots.py -- C:/Users/momoy/Projects/Catchline/Art/Models/CrewV2/Mira-sol/iterations/r26/headshots/Mira
uv run --with pillow python Art/Source/compose_mira_hair_v2.py
```

No Unity, game source, male folders, original CrewRig, Assets crew exports or git operations.

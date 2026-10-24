# Olaf — detailed male crew

CREW3D-MEN / Codex 1 (Windows app), 2026-10-24. Revision **hair-r02**. Art delivery for Claude/Mo review; no Unity integration or Mo likeness acceptance claimed.

- **19,892 triangles** including hair, hat, clothing and props; budget 20,000. Exact per-mesh counts: `build-manifest.json`.
- Texture: `Olaf_Face.png`, 512 × 512 RGB, authored skin colour/blush without baked lighting. An additional `Olaf_Hair.png` 512 × 512 RGB atlas supplies fine colour-only beard strands. Total texture pixels: 524,288. Below 2048². Hair, eyes, knit and outfit detail use opaque skinned geometry, palette materials and the listed colour textures.
- Files: `Olaf.blend`, `Olaf.fbx`, `Olaf_Face.png`, `Olaf-review.png`; individual orthographic views in `iterations/hair-r02/`.
- Reference: `Art/Source/UIv2/crew-styles/portrait-olaf.png`; role clothes follow the approved lineup and current assignment.

The male body uses the current flat male proportions and original limb attachment positions, with smoother authored garment surfaces. The original CrewRig was loaded from its source, not rebuilt: 20 bones, unchanged names/hierarchy/rest matrices and all 11 original source actions. All mesh vertices have normalized explicit skin weights. No new rig, face bones, cloth simulation or particles.

Independent verification reopened the saved `.blend`, then imported the actual delivered FBX into a fresh empty scene. `validation.json` and `validation.log` record exact source rig/action comparison, 0.95 m scalp, floor pivot, metre scale, normalized weights, relative face texture/UV resolution, identical source/export triangle counts and 44 animation-pose samples across all 11 actions. Maximum FBX bone-position error: 0.00000010 m; maximum mesh-bounds error: 0.00000024 m. Original rig SHA256: `14f4e85a280e255a655b0205921fa97254a4260c01bb5c4a4b6a0fb80ce7a456`.

Source axes: X right, −Y forward, Z up. FBX follows the original CrewRig settings (`axis_forward=-Z`, `axis_up=Y`, metre scale, no leaf bones, all original actions, 24 fps). The review studio is excluded from FBX. The `.blend` opens in the original Idle pose, frame 1.

The review sheet contains front, three-quarter, side, back, face beside the unaltered portrait, same-camera/same-scale original crew and Mira, plus Idle frame 13 and Walk frame 7. The rear detail is a labelled crop of the actual back render. Visual review is separate from the technical JSON checks.

The hair correction is integrated in the original male builder: overlapping temple-to-ear layers (curls for Kofi), a continuous fitted original hair volume, irregular tucked nape boundaries, and character-specific side flow. The supplementary `Olaf-hair-review.png` shows six saved-source head angles beside the unaltered portrait. No rejected recovery-chat overlay helper is used. The optional pre-correction baseline comparison passes bidirectional nonhair surface distances below 1 mm; maximum observed 0.000 mm. All five nonhair topology/weight/material fingerprints match exactly. 

`hair-band-audit.json` records 324 outside-in rays: every 10 degrees around the entire head, nine heights from a fixed anatomical hairline up to 0.895 m, including the lower rear band down to 0.700 m. All pass with zero skin-first hits. The explicit hairline rises to 0.800 m above exposed ears and 0.885 m at the forehead; intended face/ear skin below it is excluded. This complements the denser 325-ray temple/crown audit in `hair-coverage-hits.json` (649 samples total). Both lists save actual skin/hair/hat hit distances; the full-band receipt includes the current source SHA256. Discrete ray checks complement the six head views and do not prove every surface point.

## Honest gaps / integration limits

The full white beard is opaque layered geometry with fine ridges rather than simulated individual hairs. Painted wisps, skin wrinkles and beard translucency are simplified.

Shared original animations are preserved, including their broad elbow/shoulder articulation. These previews do not establish Unity playback, mobile performance, hand-to-equipment contact, collision/IK, animation acceptance or player acceptance. The face is a fixed expression; there is no facial animation.

Rebuild from the project root:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Art/Source/build_crew_male.py -- --name Olaf --render all --samples 32 --revision hair-r02
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Art/Source/validate_crew_male.py -- --name Olaf
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Art/Source/audit_crew_male_hair.py -- --name Olaf
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b Art/Models/CrewV2/Olaf/Olaf.blend -P docs/screens/crew-review/headshots.py -- C:/Users/momoy/Projects/Catchline/Art/Models/CrewV2/Olaf/iterations/hair-r02/head
python Art/Source/compose_crew_male.py --name Olaf
```

No Assets, Unity scenes, gameplay code, female models or original CrewRig changes; no git operations or commit by this task.

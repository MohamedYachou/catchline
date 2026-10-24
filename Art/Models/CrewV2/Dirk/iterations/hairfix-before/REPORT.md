# Dirk — detailed male crew

CREW3D-MEN / Codex 1 (Windows app), 2026-10-24. Revision **r04**. Art delivery for Claude/Mo review; no Unity integration or Mo likeness acceptance claimed.

- **19,617 triangles** including hair, hat, clothing and props; budget 20,000. Exact per-mesh counts: `build-manifest.json`.
- Texture: `Dirk_Face.png`, 512 × 512 RGB, authored skin colour/blush without baked lighting. Hair, eyes, knit and outfit detail are opaque skinned geometry with palette materials. Total texture pixels 262,144, below 2048².
- Files: `Dirk.blend`, `Dirk.fbx`, `Dirk_Face.png`, `Dirk-review.png`; individual orthographic views in `iterations/r04/`.
- Reference: `Art/Source/UIv2/crew-styles/portrait-dirk.png`; role clothes follow the approved lineup and current assignment.

The male body uses the current flat male proportions and original limb attachment positions, with smoother authored garment surfaces. The original CrewRig was loaded from its source, not rebuilt: 20 bones, unchanged names/hierarchy/rest matrices and all 11 original source actions. All mesh vertices have normalized explicit skin weights. No new rig, face bones, cloth simulation or particles.

Independent verification reopened the saved `.blend`, then imported the actual delivered FBX into a fresh empty scene. `validation.json` and `validation.log` record exact source rig/action comparison, 0.95 m scalp, floor pivot, metre scale, normalized weights, relative face texture/UV resolution, identical source/export triangle counts and 44 animation-pose samples across all 11 actions. Maximum FBX bone-position error: 0.00000010 m; maximum mesh-bounds error: 0.00000015 m. Original rig SHA256: `14f4e85a280e255a655b0205921fa97254a4260c01bb5c4a4b6a0fb80ce7a456`.

Source axes: X right, −Y forward, Z up. FBX follows the original CrewRig settings (`axis_forward=-Z`, `axis_up=Y`, metre scale, no leaf bones, all original actions, 24 fps). The review studio is excluded from FBX. The `.blend` opens in the original Idle pose, frame 1.

The review sheet contains front, three-quarter, side, back, face beside the unaltered portrait, same-camera/same-scale original crew and Mira, plus Idle frame 13 and Walk frame 7. The rear detail is a labelled crop of the actual back render. Visual review is separate from the technical JSON checks.

## Honest gaps / integration limits

The grey moustache and temple waves are sculpted layered clumps; the portrait has softer painted transitions and more irregular grey flyaways. Facial age lines are intentionally shallow geometry.

Shared original animations are preserved, including their broad elbow/shoulder articulation. These previews do not establish Unity playback, mobile performance, hand-to-equipment contact, collision/IK, animation acceptance or player acceptance. The face is a fixed expression; there is no facial animation.

Rebuild from the project root:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Art/Source/build_crew_male.py -- --name Dirk --render all --samples 32 --revision r04
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Art/Source/validate_crew_male.py -- --name Dirk
python Art/Source/compose_crew_male.py --name Dirk
```

No Assets, Unity scenes, gameplay code, female models or original CrewRig changes; no git operations or commit by this task.

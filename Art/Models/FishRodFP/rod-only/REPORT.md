# FISH-ARMS-2 STEP 0 — rod-only handoff

Ready for Claude to wire; no Unity import performed here.

`../FishRodFP_RodOnly.fbx` and editable `.blend` retain the original14 bones, seven40fps actions and existing256px atlas. Entire sleeve/glove islands are removed:3,862 triangles remain,2,016 removed. Existing v1 files are unchanged.

`validation.json` records exact retained source geometry/UV/skin/material identity and unchanged original hashes. All269 clip-relative frames match v1 retained deformations; actual FBX reimport passes hierarchy, actions, atlas path, stage exclusion and deformation checks (maxbone1.721µm; maxvertex1.351µm).

Five angle images, `player-idle-1440.png`, and `action-playback-strip.png` were opened. The labelled strip includes start/mid/end for all seven actions; individual source frames and hashes are recorded beside it. Rod and reel remain intact, sleeve/glove geometry absent. These are Blender evidence, not native game acceptance.

Reproduce with Windows Blender5.2: `Art/Source/FishRodFP/rod_only.py`, then `review_rod_only.py`. The strip is composed from the21 recorded frames. No changes to runtime, Assets, scenes or saves. No commit.

# ART108 — Navigator V1

Additive A3 navigator, using the original CrewRig's 20 bone names and
0.95 m bare-scalp height. The original `.blend`/FBX are unchanged. New source
`NavigatorV1.blend`, matching source/runtime FBX, and `validation.json` live
here; runtime export is `Assets/Art/Models/Crew/NavigatorV1.fbx`.

Select Body + Outfit_Navigator + Hat_NavigatorCap and the binocular/strap/bob
meshes. Navy jacket and cap, ivory trim, chest binoculars and a compact bob
distinguish the navigator while retaining the shared miniature crew language.
The low-detail shared face is inherited; the illustrated card portrait has
more detail and does not imply a new face rig. No extra bones were added.

In-place, 24 fps clips: Idle 1–49 (loop), Point 1–37 (one-shot), Warn 1–37
(one-shot). Match the final suffix after `|` when selecting imported takes.
The nine start/middle/end previews have been visually reviewed. Point raises
one arm; Warn raises both; Idle has a small glance/breathing movement.

Independent Blender FBX import verified exact bone-name set, triangle totals
and all three clip names. Source bounds and original rig SHA256 are in the
receipt. Native Unity Generic-rig import/clip sampling remains with the code
owner; no runtime binding or player acceptance is claimed. Rebuild in an
isolated background Blender using `Art/Source/Art108/build_navigator.py`.

Publication update (24 October 2026): Mo authorized GitHub publication of this delivery. See Art/ART-PLAN-PROGRESS.md and comms.md for the commit/push receipt. Earlier no-commit wording describes the original pre-publication handoff. Native acceptance remains pending.

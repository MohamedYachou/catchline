# Interim formal host — Mira D

Delivery: `CrewRig_Restaurant.blend` and `CrewRig_Restaurant.fbx`. Additive sibling toggles **Outfit_HostFormal** and **Hat_HairUpClip**. Keep Body enabled; enable these two together, disable other Outfit_* and Hat_* siblings. Original face/hands and every previous outfit/hat are preserved. This updates the accepted combined rig; accepted clothes2 reports describe the earlier version.

The interim D look follows `Art/Source/Restaurant/clothes/2d/mira-d-sheet.png`: tailored navy coat dress, raised gold lapels/edges/cuffs/double hem/buckle, teal scarf, gold earrings and swept-up crown/bun with gold clip. It adapts the illustration to the existing compact crew anatomy. No final Mo choice is implied.

`formal-validation.json` independently imports the export against a snapshot of the accepted clothes2 FBX. Every one of its 17 meshes retains vertices, faces, material slots/assignments, UVs and weights. The same 20 bones/hierarchy/rest and all 11 clip ranges and five sampled poses per clip match with zero delta. There are exactly 19 meshes, only two new sibling toggles. New weights normalize; every mesh bounds under 1.5 m; no presentation meshes exported. Reference and delivery SHA256 are recorded. Snapshot removed after verification, as instructed; prior accepted source/report remain.

Opened `formal-poses.jpg` (Idle13, Walk7, Carry13) and `formal-lineup.jpg` (formal beside original host, waiter, cook). Formal is differentiated by gold trim and updo without changing the neutral original face. Renderer uses the saved V4 camera orientation and 58 mm lens translated to an actor closeup, with warm/cool studio lights; this is not an exact full-room capture. Individual images in `renders/formal-*`.

Author checks complete. Unity material import, sibling toggle wiring and unsampled transitions are lead/runtime acceptance, not claimed here. No Assets, production code, metas or git changes.

Reproduction: the temporary baseline backup was removed after delivery. To rebuild from original sources, run the accepted clothes2-build.py to recreate its baseline, then formal-build.py and formal-validate.py. The additive builder guards against applying itself twice to the final combined rig. Preserve current delivery before any rebuild.

Additional exact framing proof: formal-game-1440.png and formal-game-844.png use both saved V4 camera positions, rotations,58mm lens and resolutions without translation. All nine actors are displayed on a neutral studio floor under warm/cool lighting; source cameras recorded in formal-game-cameras.json. Both final images opened: gold trim and updo distinguish the formal host at real framing. This is camera proof, not native room integration.

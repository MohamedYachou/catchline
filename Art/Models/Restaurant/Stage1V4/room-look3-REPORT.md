# Room look 3 — source delivery

The existing Stage1V4 room now has warmer table pools, reduced broad kitchen fill, per-board floor and wall pigment variation, three preview linen runners, a wall menu, sill herbs, doorway flowers and jetty string lights. Original production mesh geometry and names remain stable; new linen uses the existing DiningTwo_ runtime-hide prefix. Atlas textures are unchanged. Exact Stage1V4 FBX exporter flags retained, including FBX_SCALE_UNITS and LINEAR colours.

Fresh-import mesh/bounds/material/UV checks: PASS (`validation.json`). Opened all four before/after camera proofs at 1440x900 and 844x390. The room remains readable at phone size; cloth rests on the proof tables, wall menu is legible as a menu silhouette, jetty strings stay below the dining sight line. `room-look3-review.jpg` puts the painting, r112 native baseline and Blender before/after together. Source proof uses populated LookProof guests; runtime seats remain game-managed.

Native AFTER proof is still required from Claude's lead-sim import. This source-only task cannot claim it: no Assets/code/import changes were made. In particular Stage1's runtime lighting is code-managed: Claude must apply `lighting.json` to get these light pools. Blender watts are a recipe, not Unity intensities. Positions retain [x,z,-y]; Unity import mirrors X as previously documented.

Files: Stage1V4.blend/fbx, lighting.json, build-metrics.json, room-look-build.py, room-look-proof.py, RoomLook3-Check.blend, room-look-renders/*, room-look-changes.json. Re-run room-look-build.py idempotently for export; proof-before requires the archived original source (temporary task backup removed after verification; saved before PNGs remain evidence). No native acceptance, no commit.

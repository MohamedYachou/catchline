# Codex 2 → Codex 1 — ART-019

Finished bounded 3D pass. Scoped art/style-pass commit **9bed005** (local; not pushed). Main already contains updated:

- `Assets/Art/Models/Boats/Rowboat.fbx` — 3,414 triangles; end cleats, outer rope
  fenders and visible stern rope coil. Same ten parts. Hull, deck, oars, oarlocks
  and rod sockets unchanged; walking rectangle and pivots retained.
- `Assets/Art/Models/Harbour/Quay4m.fbx` — 2,058 triangles; cleats, pile rope wraps,
  end-grain pads, restrained bolts and rubber rubbing blocks.
- `Assets/Art/Models/Harbour/Quay4mLadder.fbx` — 2,218 triangles; same quay detail,
  original WaterLadder mesh and access retained. Both quay footprints remain 4×2m.

Existing main metadata bytes/GUIDs are preserved. No new material slots, texture
assets, runtime hooks, gameplay/UI/water/scenery/settings/save changes. No main git
mutations, Unity/scratch or foreground apps. Five existing environments unchanged.

Sources, immutable pre-pass inputs, per-model validation, exact-camera/close
before/after renders, comparison and receipt are in the art checkout:
`Catchline-art-style/Art/Models/BoatHarbour19/`. Builder:
`Art/Source/polish_boat_harbour19.py`; task 19 brief and REPORT.md document reproduction.

Saved source matches authored data exactly. Actual FBX reimports match vertices,
triangle/part/material/parent sets; original geometry prefixes intact. Raw FBX
axes/units/node transforms match baseline, with unitScale100 and pivot tolerances
recorded. This specifically protects the delivered model's native placement when
exporting from background Linux Blender. Neutral images contain no simulated
runtime water/HUD/crew and do not establish visual acceptance.

Codex 1 pickup: normal import/rebuild Art Library, then stop/re-enter Play when Mo
is ready. No new hooks are needed. Verify actual oar movement, rod sockets, crew
walking/carrying, end coil visibility, hull fenders, quay repetition/berth clearance
and ladder access at desktop/landscape-phone sizes. Keep previews closed while
school-note/background-only preference remains. Preserve Windows runtime/settings
work. VERIFY-018 still records the separate missing new-fish/four-map library
registrations; these FBX copies do not prove Unity executed Auto Refresh.

Codex 2's pass is complete, no active model reservation or subagent. Retain
`/home/mo/catchline-art19-backup/` until native verification; remove afterwards.
Canonical comms contains per-step/delivery checkpoints and final art commit.

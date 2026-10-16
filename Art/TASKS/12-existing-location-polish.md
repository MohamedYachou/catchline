# ART-012 — existing fishing location polish — 2026-10-16

Mo directed this existing WSL artist session; no new sessions or subagents. Work
on art/style-pass. Close ART-011 then improve the existing Kelp bank, Sandbar,
Rocky point and Deep channel only. Original Day3-small-boat is the style goal;
technical checks do not constitute visual acceptance.

Windows owns water/shaders/lighting, runtime hooks, travel, sound and HUD. No
Catchline-sim runs or runtime/settings edits in this delivery. Import only
finished FBXs, manifests and matching metadata into main. Native Unity checks
are explicitly deferred to Windows rather than inferred from Blender.

Build/export/render/validate with Blender 5.2.1:

```text
blender --background --factory-startup --python-exit-code 1 --python Art/Source/build_locations12.py -- GullKelpBank build
blender --background --factory-startup --python-exit-code 1 --python Art/Source/build_locations12.py -- GullKelpBank export
blender --background --factory-startup --python-exit-code 1 --python Art/Source/build_locations12.py -- GullKelpBank preview
blender --background --factory-startup --python-exit-code 1 --python Art/Source/validate_locations12.py -- GullKelpBank
```

Repeat for GullSandbar, GullRockyPoint, GullDeepChannel. Run from this checkout
using absolute script paths if Blender starts elsewhere. Sources/reports/render
evidence: Art/Models/Locations12/<asset>/. Source build depends on existing
HarbourMouth11/ART-010 procedural helpers; these dependencies remain unchanged.
Saved individual environment .blend files and FBXs are self-contained geometry
and palette materials without external textures. Composition-review.blend
contains reference boat/crew/water for review only; never export that scene.

Exact camera: Unity orthographic3.2, Euler45/35, target(1.35,0,.20), 1440x900 and
844x390. Identity environment position(0,-.32,0), local waterline0. Never recenter
by bounds. FBX uses ART-011's measured Unity X compensation and winding reversal;
Blender validation explicitly normalizes it. Matching placement manifests carry
expected local Unity mesh centres and all material names. No new palette slots.

One closed connected terrain per map; bounded coastal parts are rooted in that
terrain. Kelp has broad underwater rooted leaves and just three surface tips.
Sandbar has a single connected exposed ridge, sloping shoals and lagoon contour.
Rocky point has a connected submerged shelf supporting joined cliff spurs.
Deep channel has a broad clear trough and only far-edge submerged toe ribs.
Each model stays below 24,000 triangles. Validator checks saved source, actual
FBX positions/bounds/triangles/parenting, 513 channel rays in both, all closed
mesh topology, both camera projections, canonical slots and protected assets.

Main comms.md and docs/CLI-ARTIST-HANDOFF.md are the canonical coordination
records. Per-map main-import-receipt.json records copied bytes and metadata GUIDs.

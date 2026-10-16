# ART-012 — GullDeepChannel delivery

A broad deep trough carries the eye through calm open water, with gently rising submerged shoulders at the outer sides. Only two small submerged toe ribs sit near the far edges. No decorative wrecks, islands or clutter were added to the fishing centre. Terrain slopes have smooth normals to avoid square shading bands.

Saved source and actual exported FBX passed in Blender 5.2.1 LTS: **3 meshes / 9,554 triangles**, under the 24,000-triangle budget. One connected closed terrain component; zero boundary/nonmanifold edges on all exported meshes. Source and imported FBX match world vertex positions, per-part bounds, triangle totals and hierarchy. Both pass 513 downward clearance rays over the reserved boat/cast channel; the highest hit must remain below local -.35. These checks do not substitute for native Unity collision/camera checks.

Exact desktop 1440×900 and landscape 844×390 projection is checked against Unity ortho3.2, Euler45/35 and target(1.35,0,.20). Identity root at world(0,-.32,0), local waterline0. Keep authored placement; do not centre the prefab by its bounds. The export applies ART-011's measured Unity X correction (-x,z,-y), reversing winding. Blender reimport explicitly undoes that X reflection before comparison. ART-011 retained positive-X Unity landmarks establish the convention; this new asset still needs its own native Windows landmark check.

Self-contained geometry and named palette materials; **no new palette slots**, textures, water surface, lights, cameras or animation in the FBX. Materials used: M_CoastWet. The canonical 197 protected art files and five retained Plunder files still match their hashes. Plunder and its licenses remain untouched. Art-only files were copied to main with byte equality and metadata GUID checks; see `main-import-receipt.json`.

- `GullDeepChannel.blend`: pure saved export source with ENV_EXPORT_ONLY and identity roots.
- `Composition-review.blend`: review scene containing reference boat/crew and source-only glass water; never export this scene.
- `Beauty-desktop.png`, `Beauty-phone.png`: exact gameplay camera Blender reviews.
- `Terrain-without-water.png`: same camera diagnostic showing rooted geometry and continuous slopes.
- `validation.json`, `validation.log`, `build-metrics.json`: actual checks and counts.
- `placement-manifest.json`: waterline segments, expected local Unity mesh centres, camera footprints and palette slots; matching runtime copy is in Assets/Art/Models/Environment.

Windows owns runtime lookup/spawn hooks, actual water/shaders/lighting/foam, travel, sound and HUD. No Catchline-sim, main batchmode or runtime/settings edits were made for ART-012. The simple review water exists only to expose geometry; it does not demonstrate the original Day3 reference's layered turquoise water or native runtime appearance. Windows should compare supplied expected Unity centres after import, then capture both native cameras with the accepted water implementation. Technical checks and artist review are **not Mo's visual acceptance**.

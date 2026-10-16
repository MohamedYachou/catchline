# ART-011 — Gull Harbour mouth

**Review authority clarified by Mo:** the original `Art/Concepts/References/day03-small-boat.png` sets the quality bar. Current world, water and UI are rejected. These delivered source/export/renders are a technical checkpoint, not an accepted visual baseline. See [REFERENCE-REVIEW.md](REFERENCE-REVIEW.md) for original-reference analysis and next-pass priorities. The ART-010 lighting/water settings below document this checkpoint only; they do not define the desired final richness.

An authored, camera-bounded working-coast location: a connected warm stone headland, a low tidal islet and a smaller outer shelf surround an open fishing channel. Offset rock strata, attached fracture faces, sage grass and deliberately grouped shrubs replace the scattered pale-rock approach. A small ivory/orange beacon, fitted stone landing, timber jetty and steps provide a working-harbour focal point. The shaped seabed connects the visible coast below water.

This is a new environment delivery for Windows integration and Mo's visual review. Passing geometry checks establishes usable source/export content; it does not establish Unity parity, runtime water quality, device performance or Mo's acceptance. No gameplay/UI/Unity setting, existing water texture, boat, crew or prior model source was changed.

The final model contains **33 meshes / 30,516 triangles**, grouped under the three named roots. All source surfaces have closed boundaries; overlapping attached terrain/detail components are deliberate. Vegetation is grounded by ray-casting against the actual shore mesh; the landing steps form a solid carved stair mass. The complete measured part inventory is in `build-metrics.json`, with actual FBX results in `validation.json`.

## Working-quay revision — evening delivery

Original Day 3 reference now informs a constructed timber working landing in the
upper camera background: individually bevelled planks/joists, braced wet pilings,
end caps, fitted mooring ropes/loops, coarse draped net with floats, stacked open
slatted crates and silver fish, banded blue barrels, a deck rope coil and tied
lifering. The beacon jetty gains rope wraps, caps and wet feet. Props are grouped
on the quay, not scattered across the sea. New parts reuse existing mapped palette
slots; there are no new shader/texture/runtime dependencies.

The working quay moves 0.20 camera-ground metres forward after construction;
its front net still clears the protected t<=1.7 channel. Cargo is brought toward
the front of the deck so it reads inside the exact gameplay crop. Crate boards
remain independent closed solids rather than welding coincident board-contact
vertices; actual FBX triangle counts match the saved source. No boundary openings (28 shared internal barrel lid/body edges are recorded as nonmanifold; overlapping closed construction is intentional),
513 channel rays and 197 protected files/Plunder preservation checks passed.

`Working-quay-detail.png` is an additional close reference, not gameplay framing.
Exact-camera `Beauty-desktop.png` and `Beauty-phone.png` are regenerated for this
revision. Original simplified reference-water settings are retained solely to
compare authored geometry under controlled light. They are still far below the
original Day 3 water richness and are not a replacement for Windows' live water.
Runtime integration and camera capture evidence are recorded in `NIGHT-DELIVERY.md`.

## Review images and sources

- `Beauty-desktop.png` / `Beauty-phone.png`: clean exact-camera views at 1440×900 and 844×390.
- `HUD-overlay-desktop.png` / `HUD-overlay-phone.png`: those same views with the existing POLISH-002 native bite-state HUD footprints. Labelled **reference composites**, not Unity screenshots or new UI designs. Retained `Runtime-HUD-source-*.png` makes their source explicit.
- `Shore-detail.png`: retained initial checkpoint close view of the beacon landing, before the rope/cap revision. `Working-quay-detail.png` is the current revision close view; both use 45°/35° with horizontal span 5.4 m, not gameplay framing.
- `Composition-plan.png`: authored coast plans, desktop/phone footprint and reserved channel.
- `GullHarbourMouth.blend`: pure environment model source, `ENV_EXPORT_ONLY` collection.
- `Composition-review.blend`: editable exact-camera scene with actual boat/props/existing Captain rig and reference-only water/lights. Never import this as the runtime environment.
- `../../../Assets/Art/Models/Environment/GullHarbourMouth.fbx`: runtime environment, containing only the model hierarchy.
- `placement-manifest.json` / matching `Assets/Art/Models/Environment/GullHarbourMouth-placement.json`: placements, roots, used material colours, camera footprint, depth samples and measured waterline segments.
- `validation.json`: source, actual binary FBX/reimport, topology, framing, clear-channel and preservation results.

## Camera and bounded scope

Unity Euler **(45,35,0)**, orthographic size **3.2**, target **(1.35,0,0.20)**, distance **40 m**, clips **0.1–120 m**, no review bob/zoom offsets. Desktop spans **10.24×6.4 m** in camera space; phone **13.850256×6.4 m**. Water-plane ground depth along the camera-up direction is **9.050967 m** at this pitch. The manifest gives all four world corners for each viewport. Raised terrain naturally projects above its water-plane footprint.

The seabed is authored over an 18×12 m rectangle in camera ground coordinates, equivalent to **18×16.970563 m** in the rotated horizontal plane. This adds about 2.075 m horizontal margin beyond each side of the wider phone frame, and 2.8 camera-ground units above/below the view. Axis-aligned world bounds are larger because the composition is rotated. This implements Mo's bounded-camera scope rather than interpreting the illustrative 10×20 m example as a mandatory measurement.

The scene preserves a clear camera-ground channel **s[-2.6,2.6], t[-1.8,1.7]**. Validation samples 513 downward rays through the shore/details and rejects obstruction above -0.35 m in that area. It is an art clearance check, not a navigation or interaction implementation. The headland and shelf intentionally continue outside the crop, so the world reads as a coast rather than a visible platform edge.

## Runtime placement and waterline

Spawn **`Catchline_GullHarbourMouth`** at Unity **(0,-0.32,0)**, rotation **(0,0,0)**, scale **(1,1,1)**. Its three named child roots are **`Shoreline`**, **`Seabed`**, **`Details`**; each uses the same origin and identity transform. Do not recenter by the bounding box. Local Unity waterline is exactly **Y=0**, so this world placement matches the existing water plane at **Y=-0.32** and leaves every boat/crew/socket/deck contract intact.

If Windows changes the runtime sea datum to Y=0, place this environment at the origin and translate the existing boat/crew/camera frame upward by 0.32 m as one world-space adjustment. Do not change asset pivots or independently raise the seabed.

Seabed top depth varies from **0.12 to 2.72 m** below the waterline; the closed bottom is at **3.5 m**. The boat's centre sample has 2.72 m depth, the near-landing sample about 0.60 m and the left shelf about 0.23 m. The actual surface is a continuous shaped mesh; the dynamic water shader can use scene depth against it. Render `Seabed` as an opaque depth-support surface. Apply collision to individual static `Shoreline` meshes only if the game needs it; **do not add a box collider around the whole map**, which would cover the open channel. Details remain visual dressing, with no invented gameplay services.

## Materials and export

The manifest lists the sixteen material colours actually used by faces. Six new terrain slots are used: `M_CoastStone` #A99A7C, `M_CoastStoneLight` #C9B89A, `M_CoastWet` #696F64, `M_CoastGrass` #729053, `M_CoastGrassLight` #98A96B and `M_SeabedSand` #BEA77D. `M_CoastSand` #D9C393 was included in the seven-slot proposal/palette declaration but is unused by this rocky-coast model. Existing navy, ivory, timber, rope, steel and orange slots supply the working-coast details. No existing material asset is recoloured. The shared mesh helper retains canonical palette slots, including unused ones; the manifest distinguishes the used faces. No external or baked albedo textures are required.

Model source is in metres, Blender X right, -Y Unity forward, Z up. The FBX contains explicit **(-x,z,-y)** vertex conversion for the Unity-specific FBX, Y-up metadata and identity model-node rotations/scales. This avoids Blender's experimental space-bake double conversion through nested empty groups. The source remains canonical Z-up; conversion happens once in export memory only. Actual FBX reimport normalizes the explicit X mirror before checking every mesh's canonical bounds, names, parents, origins and triangle count against source. This compensates actual measured Unity importer X mirroring; the scratch Unity check separately asserts positive-X beacon and working-quay centres against source. The source and review scenes remain canonical; importing this Unity-specific FBX into a different DCC requires the documented X normalization. No camera, water, preview light, Captain rig or boat is included in the environment export.

## Reference water and lighting

The beauty uses a source-only water volume to demonstrate depth support: surface Y=-0.32, base #168F9F, roughness 0.36, transmission 0.60, IOR 1.333, specular weight 0.16, a restrained #168F9F emission contribution of 0.22 and #64C7C4 absorption at density 0.10. Sparse broken shoreline strokes are reference geometry. These are not Unity shaders, live foam, wakes or water textures. Windows owns selecting and implementing the dynamic water system; none of its package trials is claimed as integrated here.

Lighting and boat placement reuse the inspected ART-010 exact-camera setup: warm disk area at Blender (-4,0,7), 1100 W / 4.5 m, cool fill at (5,4,6), 260 W / 6 m, cool ambient strength 0.45, Standard view transform, exposure 0, gamma 1. Final beauty/detail renders use Cycles 32 samples with denoising. Area-light watts are not Unity directional-light intensity equivalents. No world lightmap, global outline, noisy grain or static lighting dependence is added to the moving boat.

## Rebuild and handoff

Windows Blender 5.2.1, `--background --factory-startup --python-exit-code 1 --python Art/Source/build_harbour_mouth11.py -- preview` builds the pure source plus both beauty views. Run the same script with `-- detail` for the close view and `-- export` for the FBX. Run `Art/Source/validate_harbour_mouth11.py` to produce the checked manifest and validation; it also writes the runtime-side manifest. Python/Pillow `Art/Source/sheets_harbour_mouth11.py` builds the exact-size overlays and plan from retained HUD sources.

Windows next: integrate this environment at the manifest transform, replace the rejected scattered scenery in its runtime implementation, remap the new slots, connect the seabed to the selected dynamic water/depth path, and capture actual desktop/phone waiting/bite/carry views. Review against the original Day 3 reference; use these checkpoint images to identify remaining gaps, not as acceptance targets; source/render checks do not replace that runtime review. ART-009 remains a separate queued delivery; ART-010 is checkpointed at 1c53bc8. The art commit is recorded in canonical main `comms.md`.

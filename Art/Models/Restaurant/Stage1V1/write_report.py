"""Write final measurements and native-lighting handoff without changing models or images."""
import json
from pathlib import Path
O=Path(__file__).resolve().parent
m=json.loads((O/'build-metrics.json').read_text());v=json.loads((O/'validation.json').read_text());a=json.loads((O/'layout-audit.json').read_text());c=json.loads((O/'character-scale.json').read_text());rm=json.loads((O/'render-manifest.json').read_text());byroot={r['parent']:r for r in m['rows']}
rows='\n'.join('| '+r['root']+' | '+' × '.join(f'{x:.3f}' for x in r['local_dimensions_m'])+' | '+'×'.join(map(str,r['footprint_tiles']))+' | '+str(byroot[r['root']]['triangles'])+' | '+', '.join(f'{x:.2f}' for x in r['world_position_blender_m'])+' |' for r in a['footprint_rows'])
chars='\n'.join(f"- {r['name']}: original {r['source']}; {r['height_m']:.3f} m posed height, wrapper at {r['position_blender_m']}; {r['outfit'] or 'original Mira outfit'}, {r['hat'] or 'original Mira hat'}." for r in c)
text=f'''# Restaurant stage 1 — real-mesh look proof

Codex 2 (WSL CLI), RESTAURANT-LOOK-MATCH-1. A–C delivered for lead/Mo review. **The model family transfers; an exact screenshot match is not yet achieved or claimed.** Native Unity lighting, integration, motion and touch acceptance remain untested. This is the small proof requested before producing a larger kit.

Start with [room comparison](renders/compare-interior.png), [kit comparison](renders/compare-kit.png), [desktop](renders/room-1440x900.png), [phone](renders/room-844x390.png), and [ten-item kit](renders/kit-sheet.png). All15 delivered PNGs were individually opened after the final export, including both comparison sheets. Inspection notes and hashes are in visual-review.json.

## Delivery and import

- [Stage1V1.blend](Stage1V1.blend): metric production geometry and constant PBR materials; no presentation camera, lights, reference people or hidden floor outside the room shell.
- [Stage1V1.fbx](Stage1V1.fbx): same geometry;13 named identity roots, one mesh per root. Ten requested prop types, second table, kettle cabinet and shell. Roofless shell includes actual8×5m floor, left3×5m kitchen, low ivory walls, blue shutters, left alley door, two cats, lamps and plants.
- [LookProof.blend](LookProof.blend): independently imported FBX plus original crew/Mira, presentation camera and lights. Open this to reproduce the room; do not import it as the production asset.
- [validation.json](validation.json): independent FBX reimport, all meshes/bounds/triangles, exact file hash. [layout-audit.json](layout-audit.json): per-root footprints and floor pivots. [lighting.json](lighting.json), [render-manifest.json](render-manifest.json), [character-scale.json](character-scale.json): reproducible presentation settings.

One Blender unit is1m. Export uses `axis_forward='-Z', axis_up='Y', use_space_transform=True, bake_space_transform=False, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS'`; mesh/empty only, no animations or leaf bones. Raw FBX UnitScaleFactor is100 (centimetres per source unit), matching the metric boat pipeline. Fresh import returns the intended metre dimensions. Use file units and verify the floor measures8×5m before placement; do not add a second100× conversion. Axis/rotation mapping inside Unity still needs its native import check.

All placeable root scales are1. Geometry is merged per named placeable, preserving multi-material slots. Children are not separately animated; doors, chairs, kettle lid, till and cats are static. Split meshes in the source before building interaction animation. No colliders, service anchors, prefab metadata, custom LODs, baked texture maps, runtime materials or .meta files are supplied. No Assets/, Unity, C#, git, player-save or watchdog edits were made.

## A — geometry budget and dimensions

Self-imposed complete-shell-plus-kit budget:60,000 triangles. **Final {m['triangles']:,} triangles;13 meshes** ({m['budget']-m['triangles']:,} below budget). RoomShell alone {byroot['RoomShell']['triangles']:,}; remaining props {m['triangles']-byroot['RoomShell']['triangles']:,}. Original reference people are excluded from these numbers and excluded from the production FBX.13 meshes does not mean13 draw calls: material submeshes remain; mobile GPU performance is unprofiled.

The footprint includes all protrusions and chairs. Local dimensions below are width×depth×height in metres. Root positions are Blender X right / Y rear / Z up, room centre at0; not Unity world transforms.

| Root | Local W×D×H m | Tile cap | Tris | Root X,Y,Z m |
|---|---|---|---:|---|
{rows}

Prep/stove/coffee/kettle cabinet worktop is about0.66m for the established ~1m crew. Fridge1.16m. The portable kettle root sits0.64m high on its separate cabinet; its local base is0. Wall body is~0.98m, cap~1.06m. Whole shell includes a shallow floor foundation and a small left alley landing; these intentional bounds are enumerated in validation.json, not a presentation floor.

Initial footprint inspection caught an overly wide table/chair group and3m pass. Final table group is0.97×0.56m including both chairs, with0.56m diameter top; pass is1.90×0.62m. This satisfies the plan but makes the dining furniture tighter and relatively smaller than the painted room. Do not silently enlarge those pieces during import without resolving tile occupancy. Reception base and trash foot now meet floor0; pass plinth starts1cm above0, within the documented3cm pivot tolerance.

## B — layout, camera, characters

Kitchen occupies X[-4,-1], Y[-2.5,2.5]; dining occupies X[-1,4]. Fridge/kettle/stove are across its rear; prep/sink are on its left; coffee/trash front. The pass at(-0.68,0) is rotated90° so it runs front-to-back. Guest tables at(1.35,0.98) and(1.35,-1.20); reception by the front-right opening. Kitchen door and two cats are outside the left wall.

This deliberately follows the current8×5 LEFT-kitchen plan rather than copying the concept's rear-kitchen arrangement. Placement is a visual composition in metre space, not a snapped/saved restaurant runtime layout. Walkability, service-adjacency, chair seating poses and collision/path validation have not been implemented. The camera ray probes hit the intended station first for9 samples; the sink sample misses geometry entirely. These are diagnostic samples, not proof every surface is visible. See their exact coordinates in layout-audit.json.

Room camera: orthographic, **52° downward from horizontal, yaw0**, no DOF; Blender camera local Euler X38° points it down52°. Both requested full-resolution PNGs are true scene renders, not resizes. Horizontal span is{rm[0]['ortho_horizontal_span_m']:.6f}m at1440×900 and{rm[1]['ortho_horizontal_span_m']:.6f}m at844×390, independently framed with12% margin. Camera location is{[round(x,6) for x in rm[0]['camera_position']]}. For a Unity camera using vertical orthographic half-height, the corresponding framing values are{rm[0]['ortho_horizontal_span_m']/(1440/900)/2:.6f} and{rm[1]['ortho_horizontal_span_m']/(844/390)/2:.6f} respectively; confirm against imported bounds. No HUD, screen-safe areas or touch targets are tested. Isolated kit views are560×480 at52°/yaw−18°, same export geometry and light rig.

{chars}

All three retain original dimensions, skins and ship clothes. Idle is sampled at frame12; review-only wrapper empties supply translation/yaw so root keys cannot overwrite their placement. Source SHA256s, sampled actions and measured heights are recorded in character-scale.json. Character FBXs are read only; the wrappers and source people exist only in LookProof.blend. This is a static scale proof, not a movement pass.

## Exact light setup and Unity handoff

The proof uses Blender5.2.1 Cycles/OptiX,48 samples, denoising, AgX Medium High Contrast, exposure+0.5EV. No area lights, bloom, outline or DOF. All light colours below are **linear RGB**; material hex colours below are sRGB converted to linear by build.py. Do not paste linear numbers into an sRGB colour picker without conversion.

| Source | Blender position m | Energy | Linear colour | Soft source |
|---|---|---|---|---|
| Directional WarmKey |(-3,-4,7), aims at(0,0,0)|2.1 Blender sun energy|(1,.82,.63)|9° angular diameter|
| Lantern1 |(-3.8,2.3,1.13)|45W|(1,.64,.29)|radius0.18m|
| Lantern2 |(.15,2.3,1.13)|45W|(1,.64,.29)|radius0.18m|
| Lantern3 |(3.8,2.3,1.13)|45W|(1,.64,.29)|radius0.18m|
| Lantern4 |(3.82,-1.18,1.13)|45W|(1,.64,.29)|radius0.18m|
| Kitchen fill point |(-2.4,.2,2.7)|100W|(1,.82,.57)|radius0.55m|

Ambient is uniform linear(.55,.65,.8), strength0.35. Clear background is separately linear(1,.94,.78), strength1; it does not illuminate the scene. Lantern mesh emission is ivory #FFE7A3, strength1.2, opaque.

Rebuild the same directions, relative positions and warm/cool separation in URP using the imported room as the coordinate reference. Blender watts/sun energy are **not** asserted to equal URP light-intensity numbers. Reproduce diffuse bounce/contact softness with a room lightmap and probes for movable props/crew; use restrained SSAO only where needed. Cycles9° sun softness and finite point source radii are a bake target, not a guarantee of equivalent real-time URP shadow filtering. Bake a small lighting reference before tuning the whole room. The same room camera, exposure family and clear colour must be retained when comparing captures.

No lightmap/local AO/vertex gradient/painted texture was baked in this delivery. Production render uses constant PBR with physical bevels, shallow plaster blocks, plank colour variation and sparse actual timber-grain geometry. Roughness values: navy enamel0.32, lit blue0.34, ivory0.40, plaster0.90, honey0.45, secondary wood0.52, steel0.28/metallic0.55, brass0.30/metallic0.60, cushion0.75. Other surfaces are dielectric. Base colours: navy#173F57, blue#2A6685, ivory#F3F0DC, plaster#F0DFC2, honey#C58B50. Map roughness to smoothness1−roughness for a URP Lit handoff; inspect the metallic/roughness and lantern emission after import rather than relying on FBX material conversion. Material values and geometry are exact in build.py and both .blend files.

Use a matched native tone/colour grade to restore the warm honey/ivory separation while holding navy detail; the current AgX response is part of the Blender proof. It is not a delivered Unity post-processing preset. Avoid baking directional room shadows into movable-item base colour; use local object AO separately from room lighting. Lightmap UV generation and texture atlas consolidation still belong to native integration/production.

## C — honest comparison and next visual pass

| Area | What transfers | What still differs | Concrete way to close it |
|---|---|---|---|
| Silhouette / enamel | Round rims, heavy bevels, dark navy bodies, ivory tops, orange controls, brass pulls | Repetition is cleaner and more uniform; kettle lid is brighter/steel rather than the concept's dark enamel; coffee housing has fewer sculpted layers | Adjust kettle lid material and coffee silhouette against the isolated concept, introduce controlled edge asymmetry without changing footprints |
| Timber / plaster | Broad honey planks, joints, sparse grain, ivory blocks | Timber looks smooth/toy-like; walls are very regular, without the painting's wear and rich tonal breaks | Hand-painted shared base-colour/roughness atlas, broad vertex gradients; avoid noisy photo grain |
| Soft light / contact | Warm lamps plus cool ambient, readable bevel highlights and contacts | Cycles bounce/soft penumbra may be lost in URP; concept is warmer and has richer local glow | Room lightmap + probes, restrained local AO and matched exposure/grade; verify native captures |
| Outlines / shading | Geometric bevel separation and contact shadows | No global painted contour; a few dark joins read too evenly | Paint selective crevice/edge accents; add restrained depth/normal outline only if actual phone captures need it |
| Proportions / framing | Original crew size, camera52°, roofless8×5 room, blue shutters, two cats | Concept kitchen is rear, furniture fills the room more, and exterior/cats/plants are richer | Keep current left-kitchen specification; discuss table tile occupancy before enlarging it; add only locally needed characterful props after this proof is reviewed |
| Phone | Same exported scene renders at844×390; three people and station masses distinguishable | Cups, till details, bevels and woodgrain reduce to very few pixels; no game HUD | Judge a native HUD-overlaid capture before buying detail with more triangles; keep contrast and recognizable top shapes |

The proof is materially closer than a greybox, but it is **not visually equivalent to the accepted painted concept**. The two comparison sheets intentionally show that gap. No pixel-match score or native acceptance is invented. Whole exterior harbour/dock/water, higher-stage23-item kit, guests, restaurant UI, animation and gameplay are not part of this bounded proof.

## Reproduction and verification

From project root in WSL, `python3 Art/Models/Restaurant/Stage1V1/run.py build review layout_audit` uses the existing Windows Blender5.2 installation. The system Linux Blender lacks its numpy FBX dependency; it was not modified. `package.py` uses the existing `/home/mo/.venvs/catchline-ui/bin/python` for the three technical image assemblies; it does not repaint render pixels. `write_report.py` rebuilds this measurements report. `audit.py` performs the final full-decode/hash/link/script checks; it never claims to automate manual viewing.

Export audit: PASS{m['triangles']:,} triangles,13 expected meshes, UnitScaleFactor100, maximum source/reimport bounds delta{v['max_source_export_bounds_delta_m']:.9g}m, finite bounded vertices and no extra mesh. Local footprint/pivot audit: PASS12 placeable roots. These checks do not substitute for Unity visual/runtime acceptance. Scripts/logs retain failed intermediate investigations as diagnostics; validation.json and independent-audit.json describe the final delivery. Temporary pre-change backups are removed only after the final checks pass. No commit.
'''
(O/'REPORT.md').write_text(text)
print('REPORT written',len(text))

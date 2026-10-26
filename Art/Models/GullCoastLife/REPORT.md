# Gull coast life — GULL-COAST-LIFE-ART-1

Codex 2 (WSL CLI), 2026-10-26. Six source-art exports delivered for integrating lead review. No Unity, Assets, meta, runtime or map edits; no commit.

## Delivered assets

All dimensions below are Unity world X × Y × Z metres, rest pose; contact origin Y=0. Counts include every exported mesh. Bird caps are 600 and 400 triangles respectively.

| Export | Triangles | Bounds size (m) | Independent FBX audit |
|---|---:|---|---|
| Cormorant.fbx | 378 | 0.350 x 0.854 x 0.878 | PASS |
| CormorantRock.fbx | 806 | 1.035 x 1.098 x 0.979 | PASS |
| Oystercatcher.fbx | 316 | 0.288 x 0.419 x 0.743 | PASS |
| OystercatcherGroup.fbx | 1292 | 2.000 x 0.498 x 1.005 | PASS |
| ChannelMarkers.fbx | 520 | 2.940 x 1.780 x 0.609 | PASS |
| PotBuoyLine.fbx | 566 | 3.004 x 0.235 x 0.319 | PASS |

Each item has a same-name editable `.blend`; only the same-name `.fbx` is an import asset. `review-*.blend` and `renders/` are evidence, never import them as scenery. No presentation floor, water, review kelp, light or camera exists in the six FBXs. `metrics/*-audit.json` records every exported mesh and its source/import world bounds, hierarchy, geometry correspondence, palette and file hashes.

## Integration contract

Metres; Unity +Y up, +Z bird forward. FBX global unit factor 100 is the standard Blender metre export; import at scale 1 with unit conversion enabled, never multiply scene placement by 100. Roots have unit scale and remain at their contact/waterline origins. Apply placement at the actual map waterline, which may differ from zero.

- **Cormorant**: `Cormorant` root, `CormorantRig`, `CormorantSkin`. Seven bones: Root, Body, Head, Wing.L, Wing.R, Leg.L, Leg.R. Dark teal-black faceted feathers with pale throat, hooked horn bill, teal eyes and webbed feet. Source feather roughness .32; preserve a subdued gloss in the runtime material binding. Generic/Legacy rig, not Humanoid. Import clips as Legacy: Idle frames1–91, 3s loop; DryWings1–61, 2s loop; Dive1–31, 1s once. All sampled at30fps. FBX takes may be rig-prefixed by the importer: expose the short clip names above. DryWings holds both wings open with small flicks. Dive tips and lowers the body beneath water; root remains fixed. Hide/reset or return to Idle after Dive, rather than looping the sinking endpoint. No code-driven translation is baked into Root.
- **CormorantRock**: static two-bird group on approximately1m irregular warm-grey rock, sunk below the waterline. `CormorantRockBase`, `PerchedCormorant_1`, `PerchedCormorant_2`. Birds are .78 scale geometry baked into metres. Use the independent Cormorant rig for animated individuals; the grouped habitat has no clips.
- **Oystercatcher**: root/rig/skin follow the same naming pattern and seven-bone layout. Ivory belly and wing bars, dark body, long orange bill, pink legs. Legacy Walk1–31, 1s loop; Probe1–46, 1.5s loop. Walk is in place; translate the instance along dry sand in code if needed. Probe bends the body and lowers the bill. Root stays fixed, loops close exactly. No collider supplied.
- **OystercatcherGroup**: four static individuals on an irregular2x1m wet-sand patch, shallow skirt below contact. `WetSandBar`, `Forager_1..4`. For moving birds, hide/replace a static bird with an independent rig at its placement. Do not animate the whole sand patch.
- **ChannelMarkers**: root `ChannelMarkers`; child empties `RedCan` and `GreenCone`, local positions(-1.15,0,0) and(+1.15,0,0) in Unity metres. Each child origin is its own waterline pivot and owns its coloured mesh. Detach/reposition these children with world transform preservation; the2.3m display spacing is an assembly layout, not a prescribed navigable channel width. Bases extend .22m below water and lamps reach1.56m above. Red can/green cone also distinguish shape. Static; bob each child mildly in code. Only the small top lens uses `M_LampGlow` (#FFE7A3); bind emission/bloom at runtime. No baked light, halo, shadow catcher or floor.
- **PotBuoyLine**: waterline-centred root; three orange/ivory floats and slack curved rope. Overall rope envelope3.024m (3m centreline span plus tube radius); floats at X=-1.25,0,+1.25. Static rigid assembly: a small whole-root bob is safe; independent float displacement requires rope deformation by runtime. Do not stretch the line to fill a map.

Materials are named flat house-palette slots with no texture dependency. Main colours: feathers #25383C/#344D4A, ivory #F3F0DC, orange #E36A35, pink #C9857F, rocks #8E8A80/#6F6A61, wet sand #A69775/#8F856F, marker red #BF4F3D, green #477A56, rope #D1AF76. Runtime URP material binding remains lead-owned. Keep flat normals and opaque surfaces; no need for two-sided bird skins.

## Suggested spot per ground

Based on the five existing `Art/Models/Maps/Gull*/renders/SeaV2-wide-day.png` views, opened together in `Art/Source/GullCoastLife/map-references.png`. These are composition suggestions, not navigation-tested coordinates.

| Ground | Piece and suggested relationship to the rendered terrain |
|---|---|
| Harbour mouth | PotBuoyLine along the outside shoulder of the breakwater, parallel to its outer edge; leave the central approach and harbour entrance clear. |
| Kelp bank | PotBuoyLine just beyond the visible kelp-bed edge, orange/ivory against green water; offset from the fishing anchor and crossing routes. |
| Sandbar | OystercatcherGroup on the exposed long-bar shoulder, long axis following the sand contour. Sink its skirt into the existing sand and keep its feet above tide level. |
| Rocky point | CormorantRock beside a smaller outer rock, away from the main point silhouette; sink its base so the warm-grey facets join the existing reef. Independent Cormorants may perch on the original higher rocks. |
| Deep channel | Separate red/green marker children to opposite channel shoulders, downstream of the drop-off anchor; orient them as a channel pair while keeping the full navigation lane and casting area open. |

Lead must select final coordinates against actual terrain, HUD, navigation lanes, casts and tide/water shader. No fixed map coordinates or native placement acceptance are claimed here.

## Evidence and checks

`renders/<item>/` contains five views each (front, right, back, top, three-quarter), plus five samples per bird clip:25 action frames total. `renders/Assembly-<ground>/` contains all five ground assemblies at deck45,1440x900 and844x390,10 images total. Shared horizontal framing within each pair; isolated house teal water with asset at metre scale, not the production terrain/HUD. KelpBank's sparse background kelp is a review prop only. `review-sheet.png` and `assembly-sheet.png` provide quick review contacts. Every final image was opened by Codex 2; see visual-validation.json for exact inventory and manual observations.

Independent Blender FBX reimport checks passed for all six: triangle caps; finite nonzero faces; used vertices; every mesh bounds; complete vertex/polygon surface correspondence; material palette; hierarchy; metre units; normalized skin weights; all clips and source/import deformed surfaces at five samples; fixed Root at every integer frame; exact loop closure; terminal Dive fully below water. Audit tolerances are20 micrometres surface correspondence and2e-5m loop closure. The nested marker export initially failed a52mm surface test; disabling axis-space baking for that nested static hierarchy corrected it, and the final independent audit passes. Historical diagnostic is retained only as debugging evidence, not a final pass receipt.

Reproduce with Windows Blender5.2 via `python3 Art/Source/GullCoastLife/run.py build <names>`, then `audit`, then `render`; use ground names for assembly renders. Do not batchmode the main Unity project. `finish.py` seals source/model/audit/render SHA256 values after actual image inspection. No browser/HTML detector applies to native 3D assets; visual checks use rendered geometry. No formal Impeccable critique, independent reviewer or native runtime acceptance is claimed. Questions skipped: standing instruction requests autonomous delivery, with no unresolved art decision.

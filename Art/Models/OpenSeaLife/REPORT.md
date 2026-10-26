# OPEN-SEA-LIFE-ART-1 — sailing-leg wildlife and flotsam

Codex 2 (WSL CLI), 2026-10-26. Nine independent metre-scale FBXs and editable blends; integration assets only, no event mechanics. No Unity, Assets, meta, C# or git operations. Five views per item, five samples per clip, and paired1440x900/844x390 sailing45 assemblies are in renders/. Every82required image opened individually; contact sheets are additional quick-reference evidence.

## Coordinates, pivots, import

Blender X right, -Y forward, Z up; Unity X right, Y up, +Z forward. Scene scale1 metre, FBX UnitScaleFactor100. All object scales1. Each top-level asset root stays fixed at its waterline/contact origin. Underwater geometry is intentional; do not move the root to the mesh bottom. No presentation floor, shadow catcher, lights, cameras or water is exported. Opaque flat house-palette materials, no textures or two-sided skins. Normals follow authored facets. Production URP material binding remains the integrating lead's responsibility.

For animated assets set the Unity importer Animation Type to **Legacy**, enable animations, disable root motion, and explicitly configure clip names, frame ranges and wrap modes below. FBX action metadata carries `legacy` and `loop` hints but cannot set Unity's importer settings. FBX take names may be prefixed with the armature name and a pipe; use the final suffix as the public clip name. Use Animation.Play/CrossFade on the corresponding imported animation component; loops need Loop, once clips need Once/Clamp as appropriate. The world root never translates; animal body bones move relative to the fixed waterline pivot.

| Asset | Triangles / cap | Rest size Unity XYZ, m | Clips (30 fps; inclusive frame range) |
|---|---:|---|---|
| Dolphin | 380 / 700 | 1.000 × 0.807 × 2.461 | Swim:1–37, 1.2s, loop; Leap:1–43, 1.4s, once |
| DolphinPod | 1140 / 2100 | 3.200 × 0.807 × 3.561 | Swim:1–37, 1.2s, loop; Leap:1–43, 1.4s, once |
| GannetDive | 252 / 450 | 2.070 × 0.231 × 1.011 | Glide:1–61, 2s, loop; Dive:1–28, 0.9s, once |
| DiveSplash | 128 / 200 | 0.680 × 0.430 × 0.680 | static |
| BaskingFin | 184 / 250 | 0.290 × 0.655 × 2.170 | Cruise:1–91, 3s, loop |
| FloatingCrate | 264 / 650 | 0.640 × 0.320 × 0.630 | static |
| DriftNetBuoy | 586 / 1100 | 0.873 × 0.683 × 0.739 | static |
| DriftLog | 372 / 600 | 0.526 × 0.661 × 1.835 | static |
| DistantSail | 100 / 300 | 0.620 × 1.870 × 1.540 | static |

## Item contracts and placement

- **Dolphin**: root `Dolphin`, child `DolphinRig`, skin `DolphinSkin`. Five bones Root/Body/Tail/Flipper.L/Flipper.R. Grey back, silvery sides and pale belly, curved swept dorsal, horizontal notched flukes, elongated beak and small eyes. Rest body intersects waterline: show with production water. Swim1.2s closes exactly, with body heave/pitch, fluke beat and flipper motion; translate/rotate the world instance in code to travel. Leap1.4s is a complete local up-and-back arc, peak body rise1.65m and whole animal above water, ending at its surface starting pose. It has a small fore-aft excursion but no net root drift. Keep ~4m local clearance for the full arc.
- **DolphinPod**: root `DolphinPod`, immediate children `Dolphin_1`, `Dolphin_2`, `Dolphin_3`; each owns its identically named Rig and Skin. Child waterline pivots in Unity are(-1.10,0,-0.50),(0,0,0.60),(1.10,0,-0.20). Three distinct rigged dolphins in a loose staggered line, each380tri. Swim/Leap exported for each rig (six FBX takes total); choose each child animation independently for phase offsets. The authored preview is synchronized; runtime may stagger Swim start times and Leap triggers. Do not play every take on the pod root and assume it targets all three imported animation components. Maintain the child placements or detach with world transform preserved.
- **GannetDive**: root `GannetDive`, four-bone `GannetDiveRig`, `GannetDiveSkin`. Wingspan2.07m, ivory body, black tips, buff crown and long pale bill. Geometry starts gliding1.1m above its waterline pivot. Glide2s gently heaves at altitude. Dive0.9s pitches the bird nose-down, folds both wings aft, then plunges entirely below water. End body descent2.25m relative to glide; never loop Dive. Position the root at desired sea contact level. After Dive, hide/reset/reposition the instance explicitly; do not leave it below the water until another animation unintentionally resurfaces it.
- **DiveSplash**: root `DiveSplash`, `DiveSplashCrown` mesh; open hollow ivory crown with six alternating tall spikes and four raised droplets, waterline origin. Static128tri. Scale/fade briefly at the gannet's contact point in code; no particle system, transparency shader or timing mechanics supplied. It is a small authored splash, not persistent foam or a change to shared water.
- **BaskingFin**: root `BaskingFin`, `BaskingFinRig`, `BaskingFinSkin`, three bones Root/Body/Tail. Rounded grey-brown dorsal and smaller tail tip, separated1.7m fore-aft; unseen body intentionally omitted. Cruise3s gently sways dorsal and tail independently, fixed root. Friendly smooth silhouette, no mouth, teeth, attack cue or threat mechanic. Translate in code at a calm speed.
- **FloatingCrate**: root `FloatingCrate`, `BrokenFishCrate`. About0.64m wide with open top, floor slats and one visibly broken upper slat in two ragged pieces. Lower timber extends below water. Static; whole-root bob/roll in code. Honey timber and dark corner battens match existing working-coast props.
- **DriftNetBuoy**: root `DriftNetBuoy`, `OrangeNetFloat`, `TangledNet`. Orange float, top neck and open green net lattice draped below the waterline. Root is waterline centre, not buoy bottom. Static lattice and float move together; mild whole-root bob only unless a future runtime deformer is supplied. This is scenery, not an interactive fishing station.
- **DriftLog**: root `DriftLog`, `WeatheredLog`; child contact pivot `GullSeat` at source(0,-.23,.19), Unity(0,.19,.23), containing static `PerchedGull`. Weathered1.835m log with pale cut ends, branch stub, two restrained bark ridges. Gull is included; replace/hide it under GullSeat if runtime wants its shared animated gull. Do not add a duplicate on top without hiding the included bird. Mild roll/bob keeps feet attached.
- **DistantSail**: root `DistantSail`, `DistantDinghy`,100tri. Ivory main/jib, navy hull/deck and warm wood mast,1.54m long and1.87m total height including underwater hull depth. Static; use as a far-off silhouette, no crew or rig animation. Small hull at horizon distance, without giant scaling or a navigational promise.

## Suggested sparse sailing-leg spacing

These are art-composition suggestions, not tested navigation positions. Place wildlife off the boat's projected route and outside the HUD's top-centre destination plate and upper-right coin/home cluster (reference opened: docs/screens/map10-seal-cliffs-1/sail-out-1440.png). Let water stay quiet. Use one family at a time near camera: pod12–20m from route, other pods at least50–80m apart; individual gannet15–30m off route and separate dive splashes by20m; basking fin20–35m off route, no repeated fins within60m; flotsam6–12m off route, roughly15–30m apart; distant sails60–120m from route, at least80m between sails. Adjust all distances to actual camera visibility/map scale and never obstruct casts, lanes or shore approaches. Dense Assembly is an evidence inventory, not a proposed simultaneous spawn layout. No sea-event rules or collision/nav data delivered.

## Palette and review

The existing sailing capture has restrained muted blue-teal water. Dolphin grey/ivory, gannet ivory/black/buff, warm grey-brown fins, honey/weathered timber, green net, orange buoy and navy sail hull remain distinct without neon accents or outlines. Isolated assembly water uses #1C6E7E, matching accepted life-art evidence; this is a matte review plane, not an imitation or replacement of the live water shader. Warm key/cool fill, no bloom/DOF/global outline. Five-view studio floors sit below lowest geometry to reveal submerged portions. Animation frames hide the floor to show the complete local motion, including submerged endpoints. All action frames share one fitted camera per item so movement and disappearance are not hidden by per-frame recentering.

## Actual-FBX evidence and limits

All nine independent Blender5.2FBX reimport audits passed: finite nonzero faces, used vertices, triangle caps, every-mesh physical bounds, source/import ordered polygon surfaces, hierarchy, material colours, scale1/metres and no exported presentation geometry. Every animated vertex has normalized skin weights; roots fixed at every integer frame; all five sample surfaces per clip match source within20micrometres; all looping clips close within20micrometres. Leap wholly airborne at mid-clip and back at waterline at its end; Dive wholly submerged at end. Three pod rigs tested individually. Initial diagnostics found unbound shared pod action slots and insufficient gannet terminal descent; both corrected and final independent audits PASS. No defect waived.

Detailed metrics and exact FBX hashes: metrics/*-audit.json. Each includes everymesh bounds/palette, source/import geometry and deformed sample comparisons. renders/<item>/ contains45studio images total and35sampledclip frames; renders/Assembly/ has1440x900 and844x390 sailing45 images at equal horizontal world span. review-sheet.png and clip-sheet.png are additional contacts. visual-validation.json records actual opened-image inventory and observations. These prove source-art technical/visual checks only; production water, Unity Legacy clip import/binding, HUD, native rendering and navigation placement remain lead scope.

## Reproduce

`python3 Art/Source/OpenSeaLife/run.py build <asset...>`, then `audit <asset...>`, then `render <asset...> Assembly`, using installed Windows Blender5.2. Render independent work batches without overlapping output names. finish.py uses /home/mo/.venvs/catchline-ui/bin/python after opened-images.json records the actual review. Existing helper imports are read-only: build_crab_coast_props.py, HarbourV2/audit.py, Skerries/render.py. No browser/HTML checks apply to these 3D assets; no formal Impeccable UI audit or native acceptance claimed. No subagents, commits, background daemon, player save operations, temporary backups or changes outside the brief's art paths and canonical diary.

## Every actual exported mesh bound (source X/-Y forward/Z up, metres)

| Asset / mesh | Minimum | Maximum | Triangles |
|---|---|---|---:|
| Dolphin / DolphinSkin | (-0.5, -1.24146, -0.2775) | (0.5, 1.22, 0.53) | 380 |
| DolphinPod / Dolphin_1Skin | (-1.6, -0.74146, -0.2775) | (-0.6, 1.72, 0.53) | 380 |
| DolphinPod / Dolphin_2Skin | (-0.5, -1.84146, -0.2775) | (0.5, 0.62, 0.53) | 380 |
| DolphinPod / Dolphin_3Skin | (0.6, -1.04146, -0.2775) | (1.6, 1.42, 0.53) | 380 |
| GannetDive / GannetDiveSkin | (-1.035, -0.57014, 1.0) | (1.035, 0.44037, 1.231) | 252 |
| DiveSplash / DiveSplashCrown | (-0.34, -0.34, -0.025) | (0.34, 0.34, 0.405) | 128 |
| BaskingFin / BaskingFinSkin | (-0.145, -0.26, -0.1) | (0.145, 1.91, 0.555) | 184 |
| FloatingCrate / BrokenFishCrate | (-0.32, -0.315, -0.135) | (0.32, 0.315, 0.185) | 264 |
| DriftNetBuoy / OrangeNetFloat | (-0.22, -0.20923, -0.195) | (0.22, 0.20923, 0.35) | 100 |
| DriftNetBuoy / TangledNet | (-0.43177, -0.36682, -0.33253) | (0.44147, 0.37183, 0.25592) | 486 |
| DriftLog / PerchedGull | (-0.087, -0.48042, 0.19585) | (0.087, 0.00224, 0.504) | 160 |
| DriftLog / WeatheredLog | (-0.18998, -0.92, -0.15737) | (0.33638, 0.915, 0.25778) | 212 |
| DistantSail / DistantDinghy | (-0.31, -0.77, -0.09) | (0.31, 0.77, 1.78) | 100 |

## Exact sRGB material palette

| Material | Hex |
|---|---|
| M_DolphinBack | #708887 |
| M_DolphinSide | #A2B5B0 |
| M_PaleBelly | #DCE0CF |
| M_Ivory | #F3F0DC |
| M_Wingtip | #28343B |
| M_BuffHead | #D8BE79 |
| M_Bill | #A9B7AD |
| M_Eye | #17343D |
| M_SharkWarm | #817F70 |
| M_SharkShade | #686D64 |
| M_Wood | #C58B50 |
| M_WoodLight | #DFB77A |
| M_WoodDark | #8C5A36 |
| M_Log | #9A8B70 |
| M_LogEnd | #C2AF8C |
| M_Net | #477A56 |
| M_NetDark | #355B48 |
| M_Orange | #E36A35 |
| M_Navy | #173F57 |
| M_Rope | #D1AF76 |

## BaskingFin solid-fin correction — 2026-10-26

Supersedes the original 48-triangle constant-thickness fins only. The two closed rounded volumes now total **184/250 triangles**. Each uses six elliptical horizontal sections, a broad fleshy base, gradual backward sweep and a soft small crown; faceted grey-brown shading matches the dolphin family. Dorsal waterline width0.250m, crown0.034m; tail waterline width0.166m, crown0.024m. Both independently reimported components are closed manifold. Root, Rig, Skin, three bone names, origin and Cruise1–91/3s loop unchanged. Full refreshed actual-FBX audit covers hierarchy/palette/skin and five deformed surface samples, with fixed root at all91frames and exact loop closure. See metrics/BaskingFin-solid-audit.json and BaskingFin-audit.json.

All five studio views and five Cruise frames reopened individually after correction. Front/back/top show thickness; quarter and side show taper and sweep. Original assembly and whole-set contact sheets predate this bounded correction; use the revised renders/BaskingFin/ images for this asset. Other eight accepted assets were not rebuilt or reverified. Production camera/water/Legacy import acceptance remains lead scope.

# WHALE-SHELF-LIFE-ART-1

Codex 2 (WSL CLI), 2026-10-26. Four independent FBXs and editable metre-scale blends for Whale shelf. Source-art delivery: no Unity, Assets, meta, C# or git operations. All 37 affected evidence images reopened individually for this fix; the 20 accepted flock/bait images retain their previous individual review with unchanged hashes. Three final review sheets also reopened. Integration and native acceptance remain the lead's work.

## Import and fixed waterline contract

Blender X right, -Y forward, Z up; Unity X right, Y up, +Z forward. Scene scale 1 metre; FBX UnitScaleFactor 100. Object scales are one. Place the named top-level root at the water surface; do not bottom-align the mesh. Roots, armatures and Root bones remain fixed at every frame. Body/wing/fish bones animate within that frame. Each FBX contains one mesh, its named root, and an armature only where animated. No presentation floor, water, light, camera, oversized helper or shadow catcher is exported. Opaque flat palette materials, faceted normals, no external textures. Production material/shader binding is lead-owned.

Set animated importers to Legacy, enable animation, disable root motion. Public names are the final suffix of FBX take names, which may include an armature prefix and pipe. Explicitly assign the clip frame ranges and Loop/Once wrap modes below; custom FBX legacy/loop properties are hints, not importer configuration. Use the imported rig's Animation component. BlowSpout is static and needs no animation importer.

| Asset | Triangles / cap | Rest size Unity XYZ, metres | 30 fps clips (inclusive frames) |
|---|---:|---|---|
| Humpback | 804 / 1400 | 6.360 × 2.080 × 8.650 | Surface: 1–91, 3s, Once; Blow: 1–46, 1.5s, Once; Fluke: 1–91, 3s, Once |
| BlowSpout | 180 / 200 | 2.180 × 3.077 × 0.953 | static |
| KittiwakeFlock | 576 / 900 | 5.791 × 1.326 × 6.651 | Circle: 1–121, 4s, Loop |
| BaitBall | 384 / 400 | 3.183 × 0.099 × 3.332 | Swirl: 1–61, 2s, Loop |

KittiwakeFlock's cap is 300 per bird: each is 192 triangles, three together 576 / 900. The flock's reported rest size includes its three different positions and heights, rather than an individual bird's size.

## Items and event transitions

**Humpback**: root `Humpback`, `HumpbackRig`, `HumpbackSkin`; bones Root, Body, Tail, Pectoral.L and Pectoral.R. A broad blunt head, dark slate faceted back, lighter throat facets, long pale pectorals with three knobbles each, a small swept dorsal and broad notched solid flukes. Full length 8.65m, pectoral span 6.36m. No flat fin cards.

Surface is a complete roll-up/roll-down event: starts and ends below water, exposing the back/dorsal to 0.904m and knobbly head to 0.743m. A forward pitch rolls through the crest and the left pectoral breaks the surface exactly once. Root and rig remain fixed. Blow holds the surface pose with gentle breath motion; trigger the separate plume in code. Fluke begins at that surface pose, lowers the head/front while bending the tail stock upward independently, holds the raised vertical flukes from 0.9 to 1.5s, then slips straight down and ends wholly underwater. These are individual Once events: Surface's submerged endpoint and Blow's surface start differ. To show an extended breath, blend from Surface near its exposed midpoint into Blow, then into Fluke; alternatively show Surface as its own complete event. Do not concatenate the full Surface then Blow without a transition. The longest clip is three seconds; no world travel is baked. The Fluke end pose remains under water on Clamp; deactivate below water before resetting a new event.

Revised actual FBX Fluke geometry rises to +3.033m and finishes wholly submerged (highest vertex -1.367m). Whole-clip lowest geometry is -7.276m relative to the fixed waterline root. The front arches down while the tail stock bends upward separately: the front body stays fully below water during the 0.6s tail hold, and the fluke plane is within 4.1 degrees of vertical. From 1.5s onward its horizontal position stays constant within 0.000001m as the tail descends. Pale underside faces make the goodbye silhouette readable from the deck camera. Keep the full animated envelope in mind for skinned-mesh bounds/culling, not only the rest bounds. This anchor-depth comparison is a placement guide, not a full seabed collision audit.

**BlowSpout**: root `BlowSpout`, mesh `RoundedVapour`. 3.077m high, a tapered narrow base and four rounded decimated-icosphere lobes forming a bushy split V/heart crown. 180 triangles; ivory with a cool shadow lobe. Alpha is exactly one on all exported materials; no transparency. Static, opaque authored material. Parent to the whale with local Blender (0,-2.6,+0.17)m, corresponding to Unity (0,+0.17,+2.6)m, as a starting blowhole offset. The Blow body moves only gently; fine adjustment or a body-bone attachment can follow the imported breath pose. Scale from the base and fade using the production shader/property block in code; runtime fading is not baked or supplied. Do not leave it visible through Fluke.

**KittiwakeFlock**: root `KittiwakeFlock`, `KittiwakeFlockRig`, `KittiwakeFlockSkin`; Root and Bird_1/2/3 with left/right wing bones. Three ivory gulls, mantle-grey backs, black wingtips and yellow bills, each 1.68m wingspan. Circle makes one full orbit in four seconds at a measured 3m radius; 120-degree spacing, different base heights, small height/wing motion. Each bird's head stays 2.280–3.511m above water. The full animated XY radius is wider than 3m because of wings. Leave about 4m horizontal clearance from the flock centre and more than 3.7m air clearance. The root stays at waterline centre, not bird altitude.

**BaitBall**: root `BaitBall`, `BaitBallRig`, `BaitBallSkin`; Root and FishRing_0/1/2. Twenty-four small solid diamond-bodied fish tiles, dark teal with muted silver facets, spread across a shallow approximately 3.3m patch. Swirl is a slow ±0.16rad (18.3-degree total arc) reversing swirl with asynchronous small ripples, exactly closing in two seconds. Fish remain 0.040–0.265m below the root at every frame. Native water transparency/occlusion controls the shimmer; do not lift the root to the fish mesh surface or the tiles will break above water. No continuous fast two-second revolution.

## Suggested Whale shelf placement

Read-only references: `Art/Models/Maps/GullWhaleShelf/REPORT.md`, its SeaV2 wide/top images, Whale road day capture and WhaleSpout_1 anchor capture. The shelf is 360 × 280m; Whale road is the deeper eastern area, away from the pale crown and shallow herring shelf. The orange cylinder in the anchor image is a marker, not an accepted wildlife silhouette. Terrain, map roots, navigation and anchors remain untouched.

Use existing Unity anchor positions:

| Anchor | Unity XYZ, m | Suggested use |
|---|---|---|
| WhaleSpout_1 | (107, -0.32, -48) | One whale event, facing +Z initially |
| WhaleSpout_2 | (118, -0.32, -44) | Alternate whale event position |
| GannetDive_1 | (-89, -0.32, -41) | Optional sparse feeding patch/flock, subject to existing gannet dressing |
| GannetDive_2 | (-79, -0.32, -38) | Alternate patch rather than doubling the nearby flock |

Whale anchors are only 11.7m apart: alternate them rather than putting both full whales there simultaneously. At WhaleSpout_1, the review composition offsets suggest BaitBall (103.5,-0.32,-46.7) and flock centre (102.2,-0.32,-50.3), all with identity rotation; these are local offsets converted to Unity axes. The flock can instead share the bait-ball centre for direct feeding. Check the actual boat sightline and cast area before choosing the final composition. Keep wildlife out of movement lanes, destination approach and hook/cast paths. These spots are composition proposals, not tested navigation placements.

The map report measures terrain under the whale anchors at approximately Y=-8.513 and -8.404, versus waterline Y=-0.32: about 8.19/8.08m depth. The revised 7.276m dive gives approximately 0.92/0.81m point-depth allowance. The whale spans several metres, so the integrating lead must still confirm clearance over its whole footprint and chosen heading. Do not move this full dive onto the 3.03m-deep GannetDive shelf. Bait and airborne flock can use that shallow area. WreckGulls_1 is above-water crown rock; it is not the waterline pivot for this flock. Use one calm wildlife family near the camera, with the whale as the large focal gesture.

## Render review and audits

Five true orthographic studio views per item (20), five frames for each of five clips (25), and house-water deck45 assembly at 1440×900 and 844×390 (2): the original 47 images plus ten new opaque-water Surface/Fluke samples (57 total). Changed 37 images reopened individually for this fix; accepted flock/bait evidence inherited unchanged from the previous review. The two assemblies share a horizontal world span; no viewport approximation or Unity acceptance claimed. Review plane #1C6E7E has partial transmission to expose the shallow fish patch; production water is not reproduced. Studio floors sit below geometry; action frames omit the floor so complete submerged poses can be inspected. Action frames share one camera across all clips per asset. The dense assembly demonstrates the set together, rather than prescribing spawn density. Contact sheets are additional evidence; full-size images remain beside them.

Actual exported FBXs independently reimported in Blender 5.2: triangle caps, finite used vertices/nonzero faces, exact hierarchy, palette, every-mesh physical bounds, unit scale, source/import polygon-surface parity and normalized skin weights PASS. Every integer frame checks fixed root/rig/Root bone and world root. Five sample deformations per clip match within 20 micrometres; both loops close within 20 micrometres. Separate all-frame semantic checks cover 3m bird orbit, per-bird triangles, underwater fish envelope, humpback envelope and opaque rounded 3.077m vapour size plus revised Surface/Fluke semantic assertions. See metrics/*-audit.json and contract-audit.json, which include final source/FBX hashes. No presentation geometry is exported.

visual-validation.json records actual opened-image inventory and observations. delivery-receipt.json seals source, assets, logs and evidence with SHA-256. Native Legacy import, production material binding/water, animation culling bounds, bird speed/whale scale in context, full-footprint seabed clearance, HUD, casting and navigation acceptance remain for Claude/Mo. No native check is claimed.

## Every actual exported mesh bound (Blender XYZ, metres)

| Asset / mesh | Minimum | Maximum | Triangles |
|---|---|---|---:|
| Humpback / HumpbackSkin | (-3.18, -4.25, -1.65) | (3.18, 4.4, 0.43) | 804 |
| BlowSpout / RoundedVapour | (-1.08502, -0.46661, -0.00136) | (1.09546, 0.48662, 3.07522) | 180 |
| KittiwakeFlock / KittiwakeFlockSkin | (-1.95062, -3.31304, 2.305) | (3.84, 3.33804, 3.631) | 576 |
| BaitBall / BaitBallSkin | (-1.50846, -1.732, -0.2063) | (1.67499, 1.60011, -0.10701) | 384 |

## Full animated envelopes (Blender XYZ, metres)

| Asset / clip | Minimum | Maximum |
|---|---|---|
| Humpback / Surface | (-3.2752, -4.28939, -3.01122) | (3.27854, 4.40767, 0.90372) |
| Humpback / Blow | (-3.18, -4.25, -1.65) | (3.18, 4.40396, 0.49081) |
| Humpback / Fluke | (-3.19509, -4.25, -7.27564) | (3.18, 4.4, 3.03292) |
| KittiwakeFlock / Circle | (-3.84011, -3.84021, 2.185) | (3.84011, 3.84022, 3.64188) |
| BaitBall / Swirl | (-1.52435, -1.74652, -0.26494) | (1.67629, 1.60213, -0.03963) |

## Authored sRGB palette

| Material | Hex |
|---|---|
| M_WhaleSlate | #526B73 |
| M_WhaleLit | #70858A |
| M_WhaleBelly | #D4D9CC |
| M_ThroatGroove | #A3B4B1 |
| M_Ivory | #F3F0DC |
| M_VapourShade | #D5E3DC |
| M_Wingtip | #28343B |
| M_GullMantle | #BAC9C6 |
| M_YellowBill | #E6AD38 |
| M_Eye | #17343D |
| M_BaitDark | #31565E |
| M_BaitSilver | #8FA6AC |
| M_BaitTeal | #517F81 |

## Reproduce and ownership

`python3 Art/Source/WhaleShelfLife/run.py build <asset...>`, then `audit <asset...>`, then `render <asset...> Assembly`. Windows Blender5.2 installed locally. Run contract.py with the same Blender for all-frame semantics. finish.py uses `/home/mo/.venvs/catchline-ui/bin/python` after opened-images.json truthfully records the individual review. Accepted helper modules are read-only: OpenSeaLife/build.py, HarbourV2/audit.py, Skerries/render.py and their existing dependencies. No UI/browser/Lighthouse test applies to these offline 3D models. Design-stack/house-style guidance was read; no formal UI audit or native runtime acceptance claimed. No subagents, commit, player-save change, watchdog file, remaining temporary backup or abandoned Blender worker. Source and Models WhaleShelfLife directories are the entire implementation scope; canonical comms.md records checkpoints and handoff.

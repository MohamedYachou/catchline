# TIER6-BOAT-1 — Shelter Boat C

Codex 2 (WSL CLI). Source-art delivery only. Mo selected C, about10m, fitted with every earlier tier's fishing station. No Unity, Assets, metas, C# or git changes. Integrating lead owns game grid, placement/interaction coordinates, import palette bindings and native HUD/water/navigation acceptance.

## 0. Inventory and A. Fitted concept

Before modelling, every object from the four accepted authoring blends was inventoried: Tier5DeepLines103141nodes, PrepFisherV190, CompactFisherV133 and JigBoatV144. Full tables remain appended to ../Tier6/REPORT.md; bounds/hierarchy/source hashes are in Art/Source/BoatsV2/Tier6/station-inventory.json. All sources are read-only. The fitted painted concept Art/Source/BoatsV2/Tier6/concept-C-fitted.png has side/threequarter/top, fourteen equipment labels and crew routes. Prompt and reference retained. It is an illustrative schematic; the final audited coordinates and ten crew points below supersede its eight drawn circles.

## B. 3D and integration contract

Tier6V1.blend and Tier6V1.fbx. Hull nominal10m x5m: widened to retain the full inherited equipment kit with connected walkways. Navy clinker hull with swept sheer, three recessed laps, orange waterline band, ivory cap, warm planked deck; enclosed forward ivory wheelhouse and a long navy shelter roof over the preparation area. Two outboard buoy winch/booms, four rod holders, two articulated deep-line rigs, rear+side nets, full prep/raw/prepared storage, three jig reels, eight warm bulbs/cable and sorting tray. Ten crew stand nodes exceed Buoy fisher's eight berths. Runtime crew capacity is not changed by this art delivery.

Metres, scale1, source X right/-Y bow/Z up, fixed deck/root z0. Raw FBX UnitScaleFactor100, no space bake, FBX_SCALE_UNITS; same corrected Jig exporter contract. FBX Blender reimport restores original coordinates; Unity maps -Y to +Z. Every node remains beneath Catchline_Tier6V1. Every semantic equipment name is preserved, including rig/reel pivot parents. Rods for regular holders remain runtime equipment; no duplicate RodVisual meshes. Deep-line poles and jig reels are visible delivered geometry.

RawBuckets is a separate pair of actual stowed buckets rather than Tier5's coincident alternative cooler meshes; RawIceCoolers and PreparedHold retain their named source component hierarchies. Both variants can be toggled by their respective roots; lead should decide which runtime storage presentation to show. BuoyRig_1/2 are additional visible static winch/booms; BuoyAnchor_1/2 remain waterline hook positions for runtime buoy/pot visuals. Prepared hold and raw input aliases from Prep are retained with current storage coordinates. OptionalRodModule remains separate. No catch animation, runtime collision or navigation data is included.

**17,513tri /18,000 cap; 125meshes, 181nodes.** Independent source/FBX every ordered polygon-cycle/multiplicity comparison PASS, max vertex error 0.000000910m; hierarchy/material palette/source scale/world matrices and all57required semantic names PASS. Every mesh bounded independently; no presentation plane, hidden giant mesh, camera, light or texture exported. Degenerate zero-area faces in carried source bevels removed in the new asset only.

### Crew access

Actual exported polygons clipped against every human-clearance prism (z.045–1.65m). Main spine0.90m wide; cabin side passages0.72m; cabin cross passage0.70m; task access branches0.70m. Zero intersecting obstacle polygons. Connected prism graph checked; every Worker, Access and CrewStand node lies inside the network. The walkable deck is solid and flat atz0, centre hatch essentially flush. Roof underside1.70m clears tested crew height1.65m. Clearance is source geometry proof, not a Unity grid/pathfinding test: lead must adapt grid and crew routes to these coordinates, not reuse old hull grids blindly.

| Required semantic node | Source XYZ, m | Parent |
|---|---|---|
| DeepLineModule | (0.0, 0.0, 0.0) | Catchline_Tier6V1 |
| PrepStation | (-2.5, -1.15, 0.0) | Catchline_Tier6V1 |
| PreparedHold | (-4.15, 0.35, 0.0) | Catchline_Tier6V1 |
| RawIceCoolers | (1.77, -0.75, 0.0) | Catchline_Tier6V1 |
| RawBuckets | (0.0, 0.0, 0.0) | Catchline_Tier6V1 |
| NetModule1 | (-0.3, 0.38, 0.0) | Catchline_Tier6V1 |
| NetModule2 | (0.24, 2.15, 0.0) | Catchline_Tier6V1 |
| NetWorker_1 | (0.65, 3.7, 0.0) | Catchline_Tier6V1 |
| NetWorker_2 | (1.35, 3.7, 0.0) | Catchline_Tier6V1 |
| PrepSurface | (-1.6, -1.15, 0.72) | Catchline_Tier6V1 |
| PrepInput | (1.6, -0.75, 0.4) | Catchline_Tier6V1 |
| PreparedOutput | (-1.6, 0.35, 0.5) | Catchline_Tier6V1 |
| RawInput_1 | (1.6, -1.18, 0.4) | Catchline_Tier6V1 |
| RawInput_2 | (1.6, -0.32, 0.4) | Catchline_Tier6V1 |
| PreparedOutput_1 | (-1.6, 0.78, 0.5) | Catchline_Tier6V1 |
| PreparedOutput_2 | (-1.6, -0.08, 0.5) | Catchline_Tier6V1 |
| FishHold | (0.0, 0.0, 0.0) | Catchline_Tier6V1 |
| HoldLid | (0.0, 0.0, 0.0) | Catchline_Tier6V1 |
| HoldRimHinges | (0.0, 0.0, 0.0) | Catchline_Tier6V1 |
| LampCable | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| TwoShortLampMasts | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| SortingTray | (-2.7, 2.15, 0.0) | Catchline_Tier6V1 |
| RodHolder_1 | (-2.25, -0.3, 0.43) | Catchline_Tier6V1 |
| RodHolder_2 | (2.25, -0.3, 0.43) | Catchline_Tier6V1 |
| RodHolder_3 | (2.25, 1.85, 0.43) | OptionalRodModule |
| RodHolder_4 | (-2.25, 2.75, 0.43) | OptionalRodModule |
| RodSocket_1 | (-2.25, -0.3, 0.47) | Catchline_Tier6V1 |
| RodSocket_2 | (2.25, -0.3, 0.47) | Catchline_Tier6V1 |
| RodSocket_3 | (2.25, 1.85, 0.47) | OptionalRodModule |
| RodSocket_4 | (-2.25, 2.75, 0.47) | OptionalRodModule |
| DeepLineRig_1 | (2.22, 1.1, 0.46) | DeepLineModule |
| DeepLineRig_2 | (2.22, 2.67, 0.46) | DeepLineModule |
| DeepLineBase_1 | (2.22, 1.1, 0.46) | DeepLineModule |
| DeepLineBase_2 | (2.22, 2.67, 0.46) | DeepLineModule |
| DeepLineTip_1 | (3.69, 1.1, 3.14) | DeepLineModule |
| DeepLineTip_2 | (3.69, 2.67, 3.14) | DeepLineModule |
| DeepLineReelPivot_1 | (2.29, 1.1, 0.74) | DeepLineRig_1 |
| DeepLineReelPivot_2 | (2.29, 2.67, 0.74) | DeepLineRig_2 |
| DeepLineWorker_1 | (1.6, 1.1, -0.0) | DeepLineModule |
| DeepLineWorker_2 | (1.6, 2.67, -0.0) | DeepLineModule |
| BuoyAccess_1 | (-1.35, -3.0, 0.0) | Catchline_Tier6V1 |
| BuoyAccess_2 | (1.35, -3.0, 0.0) | Catchline_Tier6V1 |
| BuoyAnchor_1 | (-3.05, -3.0, -0.3) | Catchline_Tier6V1 |
| BuoyAnchor_2 | (3.05, -3.0, -0.3) | Catchline_Tier6V1 |
| PrepWorker_1 | (-0.75, -0.72, 0.0) | Catchline_Tier6V1 |
| PrepWorker_2 | (-0.75, -1.58, 0.0) | Catchline_Tier6V1 |
| JigReel_01 | (-0.71, 1.7, 0.0) | Catchline_Tier6V1 |
| JigReel_02 | (-0.71, 1.65, 0.0) | Catchline_Tier6V1 |
| JigReel_03 | (-0.71, 1.58, 0.0) | Catchline_Tier6V1 |
| SquidLamp_01 | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| SquidLamp_02 | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| SquidLamp_03 | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| SquidLamp_04 | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| SquidLamp_05 | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| SquidLamp_06 | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| SquidLamp_07 | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| SquidLamp_08 | (-3.49, 0.2, 0.0) | Catchline_Tier6V1 |
| CrewStand_1 | (-0.65, -1.85, 0.0) | Catchline_Tier6V1 |
| CrewStand_2 | (0.65, -1.85, 0.0) | Catchline_Tier6V1 |
| CrewStand_3 | (-0.65, -0.1, 0.0) | Catchline_Tier6V1 |
| CrewStand_4 | (0.65, -0.1, 0.0) | Catchline_Tier6V1 |
| CrewStand_5 | (-0.65, 1.65, 0.0) | Catchline_Tier6V1 |
| CrewStand_6 | (0.65, 1.65, 0.0) | Catchline_Tier6V1 |
| CrewStand_7 | (-0.65, 3.1, 0.0) | Catchline_Tier6V1 |
| CrewStand_8 | (0.65, 3.1, 0.0) | Catchline_Tier6V1 |
| CrewStand_9 | (0.0, 0.65, 0.0) | Catchline_Tier6V1 |
| CrewStand_10 | (0.0, 2.4, 0.0) | Catchline_Tier6V1 |

### Materials

All inherited station slots kept, including source suffixes when Blender distinguishes duplicate materials. Preserve actual FBX slot names when binding; do not assume a suffix indicates a new intended colour. M_JigBulb comes from accepted Jig lights and needs the same warm bulb runtime emission binding; separate JigLampGlow is not duplicated here. Boat is static; attach any future animated glows separately. Base palette follows the accepted navy/ivory/wood/teal/steel/orange family. No texture dependency.

### Opened visual evidence

Seven1000x750views: front-three-quarter,side,back-three-quarter,top,low-waterline,deck-55,game-exact-45. Two1600x1000equal-scale lineups: Prep left, Buoy fisher centre, Tier6 right. All nine opened individually, plus review-sheet.png. Checked swept sheer/clinker at side/waterline, cabin closure, shelter coverage, supported stations, lamp cable, both net modules, clear centre deck and larger working hull. Rendering uses actual exported FBXs with isolated source-only floor/lights. No export contains these presentation objects. Family lineup is equal world scale, not individually resized cards.

## C. Refit card

Art/Source/BoatsV2/ui/v2-item-hull-tier6.png,480x360RGBA. Generated from final model game45 plus accepted Prep card reference, prompt/master retained; exact alpha-bounds crop/Lanczos centred export independently reconstructed pixel-for-pixel. Alpha0–255, all corners transparent, visible bounds(33,24)–(447,336). Card and native-size comparison beside Skiff/Prep opened. Consistent thin outline, saturated navy, honey timber, ivory/teal surfaces and shaded volume. Camera follows model reference so poles/lamps stay separated; neighbouring cards show the other quarter. All silhouette margins clear. Tiny fittings simplified as in incumbent cards. Native UI acceptance not run.

## Every actual exported mesh bound

Source/rest XYZ metres, same convention as Blender authoring. These are actual FBX reimport bounds, including outboard poles/lines and engine; whole-model extent intentionally exceeds the nominal hull.

| Mesh | Minimum | Maximum | Triangles |
|---|---|---|---:|
| BuoyRig_1 | (-3.06356, -3.15, -0.3) | (-1.92, -2.85, 1.37392) | 152 |
| BuoyRig_2 | (1.92, -3.15, -0.3) | (3.06356, -2.85, 1.37392) | 152 |
| CabinAftDoor | (-0.34, -2.75, 0.02) | (0.34, -2.724, 1.36) | 28 |
| CabinBeaconAerial | (-0.515, -4.165, 1.84) | (0.615, -3.585, 2.65) | 84 |
| CabinDoorGlass | (-0.23, -2.73, 0.95) | (0.23, -2.704, 1.35) | 28 |
| CabinLifeRing | (-0.95763, -4.075, 0.305) | (-0.86237, -3.485, 0.895) | 288 |
| Deep 1 hanging fishing line | (3.68144, 1.091, -0.28) | (3.69856, 1.109, 3.14) | 36 |
| Deep 1 line guide | (2.29671, 1.065, 1.48) | (2.36329, 1.135, 1.55) | 36 |
| Deep 1 line guide.001 | (2.56671, 1.065, 2.49) | (2.63329, 1.135, 2.56) | 36 |
| Deep 1 line guide.002 | (3.06671, 1.065, 3.05) | (3.13329, 1.135, 3.12) | 36 |
| Deep 1 line guide.003 | (3.65671, 1.065, 3.14) | (3.72329, 1.135, 3.21) | 36 |
| Deep 1 orange grip | (2.18453, 1.02772, 0.77102) | (2.38547, 1.17228, 1.20898) | 36 |
| Deep 1 rail clamp | (2.1025, 0.96, 0.3075) | (2.3175, 1.24, 0.5725) | 56 |
| Deep 1 tapered pole 0 | (2.15736, 1.04008, 0.45324) | (2.39264, 1.15992, 1.48675) | 36 |
| Deep 1 tapered pole 1 | (2.2817, 1.05245, 1.46709) | (2.6483, 1.14755, 2.50291) | 36 |
| Deep 1 tapered pole 2 | (2.57389, 1.06671, 2.46669) | (3.12611, 1.13329, 3.07331) | 36 |
| Deep 1 tapered pole 3 | (3.09698, 1.08098, 3.03023) | (3.69302, 1.11902, 3.15977) | 36 |
| Deep 1 crank | (2.02788, 0.87337, 0.71476) | (2.30212, 0.92663, 0.88524) | 36 |
| Deep 1 hand reel | (2.11881, 0.95, 0.56) | (2.46119, 1.25, 0.92) | 36 |
| Deep 1 handle | (1.9991, 0.77, 0.817) | (2.0809, 0.9, 0.903) | 36 |
| Deep 1 reel flange | (2.09503, 0.925, 0.535) | (2.48497, 0.955, 0.945) | 36 |
| Deep 1 reel flange.001 | (2.09503, 1.245, 0.535) | (2.48497, 1.275, 0.945) | 36 |
| Deep 2 hanging fishing line | (3.68144, 2.661, -0.28) | (3.69856, 2.679, 3.14) | 36 |
| Deep 2 line guide | (2.29671, 2.635, 1.48) | (2.36329, 2.705, 1.55) | 36 |
| Deep 2 line guide.001 | (2.56671, 2.635, 2.49) | (2.63329, 2.705, 2.56) | 36 |
| Deep 2 line guide.002 | (3.06671, 2.635, 3.05) | (3.13329, 2.705, 3.12) | 36 |
| Deep 2 line guide.003 | (3.65671, 2.635, 3.14) | (3.72329, 2.705, 3.21) | 36 |
| Deep 2 orange grip | (2.18453, 2.59772, 0.77101) | (2.38547, 2.74228, 1.20898) | 36 |
| Deep 2 rail clamp | (2.1025, 2.53, 0.3075) | (2.3175, 2.81, 0.5725) | 56 |
| Deep 2 tapered pole 0 | (2.15736, 2.61008, 0.45324) | (2.39264, 2.72992, 1.48675) | 36 |
| Deep 2 tapered pole 1 | (2.2817, 2.62245, 1.46709) | (2.6483, 2.71755, 2.50291) | 36 |
| Deep 2 tapered pole 2 | (2.57389, 2.63671, 2.46669) | (3.12611, 2.70329, 3.07331) | 36 |
| Deep 2 tapered pole 3 | (3.09698, 2.65098, 3.03023) | (3.69302, 2.68902, 3.15977) | 36 |
| Deep 2 crank | (2.02788, 2.44337, 0.71476) | (2.30212, 2.49663, 0.88524) | 36 |
| Deep 2 hand reel | (2.11881, 2.52, 0.56) | (2.46119, 2.82, 0.92) | 36 |
| Deep 2 handle | (1.9991, 2.34, 0.817) | (2.0809, 2.47, 0.903) | 36 |
| Deep 2 reel flange | (2.09503, 2.495, 0.535) | (2.48497, 2.525, 0.945) | 36 |
| Deep 2 reel flange.001 | (2.09503, 2.815, 0.535) | (2.48497, 2.845, 0.945) | 36 |
| DoorLatch | (0.21, -2.71, 0.63) | (0.27, -2.67, 0.73) | 44 |
| EngineLegPropeller | (-0.22, 4.8, -0.82228) | (0.22, 5.1775, 0.10228) | 60 |
| FishHold | (-0.34, 0.55, -0.08) | (0.34, 1.65, -0.01) | 44 |
| FrontWindow-0.43 | (-0.77, -4.778, 0.88) | (-0.09, -4.752, 1.48) | 28 |
| FrontWindow0.43 | (0.09, -4.778, 0.88) | (0.77, -4.752, 1.48) | 28 |
| HoldLid | (-0.32, 0.575, -0.0) | (0.32, 1.625, 0.01) | 44 |
| HoldRimHinges | (0.23, 0.695, 0.009) | (0.29, 1.505, 0.021) | 24 |
| Hull | (-2.518, -5.0, -0.82) | (2.518, 5.0, 0.78) | 463 |
| InnerBulwark | (-2.5, -5.0, -0.025) | (2.5, 5.0, 0.78) | 76 |
| JigReel_01 | (-2.39098, 1.4, -0.35) | (-1.95, 1.755, 0.81866) | 272 |
| JigReel_02 | (-2.39098, 2.55, -0.35) | (-1.95, 2.905, 0.81866) | 272 |
| JigReel_03 | (-2.39098, 3.65, -0.35) | (-1.95, 4.005, 0.81866) | 272 |
| KeelAndRakedStem | (-0.05, -5.07763, -0.925) | (0.05, 4.6, 0.81521) | 24 |
| LampCable | (-2.152, -0.82281, 1.61961) | (-2.128, 3.14281, 1.93001) | 480 |
| MotorOrangeCap | (-0.26, 4.7, 0.42) | (0.26, 5.12, 0.48) | 44 |
| NetCrank | (1.014, 4.68281, 0.67) | (1.074, 4.90881, 0.85) | 72 |
| NetDrum | (0.07858, 4.55594, 0.55844) | (0.94858, 4.77906, 0.78127) | 844 |
| NetMountFittings | (0.08, 4.15, 0.04) | (0.94, 4.36, 0.179) | 184 |
| SternNetRoller | (0.075, 4.12, -0.0) | (0.945, 4.59381, 0.67376) | 144 |
| SternNet_Stowed | (0.1281, 4.74069, -0.24856) | (0.8799, 5.01724, 0.65856) | 1936 |
| Module2_NetCrank | (2.32281, 4.464, 0.67) | (2.54881, 4.524, 0.85) | 72 |
| Module2_NetDrum | (2.19594, 3.52858, 0.55844) | (2.41906, 4.39858, 0.78127) | 844 |
| Module2_NetMountFittings | (1.79, 3.53, 0.04) | (2.0, 4.39, 0.179) | 184 |
| Module2_SternNetRoller | (1.76, 3.525, -0.0) | (2.23381, 4.395, 0.67376) | 144 |
| Module2_SternNet_Stowed | (2.38069, 3.5781, -0.24856) | (2.65724, 4.3299, 0.65856) | 1936 |
| RodHolder_3 | (2.185, 1.785, 0.32) | (2.315, 1.915, 0.54) | 44 |
| RodHolder_4 | (-2.315, 2.685, 0.32) | (-2.185, 2.815, 0.54) | 44 |
| OutboardMotor | (-0.25, 4.71, -0.19) | (0.25, 5.11, 0.43) | 44 |
| PlankDeck | (-2.37, -4.915, -0.045) | (2.37, 4.915, 0.0) | 234 |
| Cutting board 1 | (-1.795, -0.973, 0.6425) | (-1.405, -0.463, 0.6775) | 100 |
| Cutting board 2 | (-1.795, -1.837, 0.6425) | (-1.405, -1.327, 0.6775) | 100 |
| Knife blade 1 | (-1.72375, -0.9515, 0.693) | (-1.51375, -0.9165, 0.711) | 108 |
| Knife blade 2 | (-1.72375, -1.8155, 0.693) | (-1.51375, -1.7805, 0.711) | 108 |
| Knife handle 1 | (-1.47875, -0.958, 0.6845) | (-1.38375, -0.91, 0.7195) | 108 |
| Knife handle 2 | (-1.47875, -1.822, 0.6845) | (-1.38375, -1.774, 0.7195) | 108 |
| Prep stainless rim | (-1.92, -1.89, 0.52) | (-1.28, -0.41, 0.62) | 108 |
| Prep table leg | (-1.9025, -0.4695, -0.0) | (-1.8475, -0.4145, 0.55) | 108 |
| Prep table leg.001 | (-1.3525, -0.4695, -0.0) | (-1.2975, -0.4145, 0.55) | 108 |
| Prep table leg.002 | (-1.9025, -1.8855, 0.0) | (-1.8475, -1.8305, 0.55) | 108 |
| Prep table leg.003 | (-1.3525, -1.8855, 0.0) | (-1.2975, -1.8305, 0.55) | 108 |
| Prep table lower shelf | (-1.825, -1.775, 0.1725) | (-1.375, -0.525, 0.2275) | 108 |
| Prep washable top | (-1.885, -1.845, 0.6125) | (-1.315, -0.455, 0.6475) | 88 |
| Insulated lid 1.001 | (-1.855, 0.462, 0.4525) | (-1.345, 1.102, 0.5275) | 108 |
| Insulated lid 2.001 | (-1.855, -0.402, 0.4525) | (-1.345, 0.238, 0.5275) | 108 |
| PREPARED freezer 1 | (-1.84, 0.482, 0.02) | (-1.36, 1.082, 0.47) | 108 |
| PREPARED freezer 2 | (-1.84, -0.382, 0.02) | (-1.36, 0.218, 0.47) | 108 |
| Recessed lid handle 1.001 | (-1.6225, 0.692, 0.5225) | (-1.5775, 0.872, 0.5475) | 108 |
| Recessed lid handle 2.001 | (-1.6225, -0.172, 0.5225) | (-1.5775, 0.008, 0.5475) | 108 |
| Storage front latch 1.001 | (-1.925, 0.742, 0.345) | (-1.9, 0.822, 0.435) | 108 |
| Storage front latch 2.001 | (-1.925, -0.122, 0.345) | (-1.9, -0.042, 0.435) | 108 |
| RawBucketStow_1 | (1.92, -1.79119, 0.04) | (2.28, -1.44881, 0.35) | 72 |
| RawBucketStow_2 | (1.92, -1.07119, 0.04) | (2.28, -0.72881, 0.35) | 72 |
| Ice marker horizontal | (1.926, -1.247, 0.2325) | (1.934, -1.117, 0.2675) | 108 |
| Ice marker horizontal.001 | (1.926, -0.383, 0.2325) | (1.934, -0.253, 0.2675) | 108 |
| Ice marker vertical | (1.92475, -1.1995, 0.185) | (1.93275, -1.1645, 0.315) | 108 |
| Ice marker vertical.001 | (1.92475, -0.3355, 0.185) | (1.93275, -0.3005, 0.315) | 108 |
| Insulated lid 1 | (1.34, -1.502, 0.4525) | (1.85, -0.862, 0.5275) | 108 |
| Insulated lid 2 | (1.34, -0.638, 0.4525) | (1.85, 0.002, 0.5275) | 108 |
| RAW ice cooler 1 | (1.355, -1.482, 0.02) | (1.835, -0.882, 0.47) | 108 |
| RAW ice cooler 2 | (1.355, -0.618, 0.02) | (1.835, -0.018, 0.47) | 108 |
| Recessed lid handle 1 | (1.5725, -1.272, 0.5225) | (1.6175, -1.092, 0.5475) | 108 |
| Recessed lid handle 2 | (1.5725, -0.408, 0.5225) | (1.6175, -0.228, 0.5475) | 108 |
| Storage front latch 1 | (1.895, -1.222, 0.345) | (1.92, -1.142, 0.435) | 108 |
| Storage front latch 2 | (1.895, -0.358, 0.345) | (1.92, -0.278, 0.435) | 108 |
| RodHolder_1 | (-2.315, -0.365, 0.32) | (-2.185, -0.235, 0.54) | 44 |
| RodHolder_2 | (2.185, -0.365, 0.32) | (2.315, -0.235, 0.54) | 44 |
| RoofTimberLip | (-2.075, -4.68, 1.665) | (2.075, -0.42, 1.705) | 44 |
| SafetyFenders | (-2.565, -3.58084, -0.3) | (2.565, 2.88084, 0.56) | 336 |
| SafetyRail | (-2.313, -1.822, 0.48027) | (2.313, 4.372, 1.003) | 468 |
| ShelterRoofAftPosts | (-2.016, -0.556, 0.0) | (2.016, -0.484, 1.7) | 56 |
| SideWindow-0.866-2.62 | (-0.879, -3.68, 0.88) | (-0.853, -2.96, 1.48) | 28 |
| SideWindow-0.866-3.65 | (-0.879, -4.71, 0.88) | (-0.853, -3.99, 1.48) | 28 |
| SideWindow0.866-2.62 | (0.853, -3.68, 0.88) | (0.879, -2.96, 1.48) | 28 |
| SideWindow0.866-3.65 | (0.853, -4.71, 0.88) | (0.879, -3.99, 1.48) | 28 |
| SortingTray | (-2.0325, 3.8775, -0.0) | (-1.2875, 4.6825, 0.855) | 440 |
| SquidLamp_01 | (-2.205, -0.6375, 1.50203) | (-2.075, -0.5075, 1.86203) | 114 |
| SquidLamp_02 | (-2.205, -0.1425, 1.39328) | (-2.075, -0.0125, 1.75328) | 114 |
| SquidLamp_03 | (-2.205, 0.3525, 1.32078) | (-2.075, 0.4825, 1.68078) | 114 |
| SquidLamp_04 | (-2.205, 0.8475, 1.28453) | (-2.075, 0.9775, 1.64453) | 114 |
| SquidLamp_05 | (-2.205, 1.3425, 1.28453) | (-2.075, 1.4725, 1.64453) | 114 |
| SquidLamp_06 | (-2.205, 1.8375, 1.32078) | (-2.075, 1.9675, 1.68078) | 114 |
| SquidLamp_07 | (-2.205, 2.3325, 1.39328) | (-2.075, 2.4625, 1.75328) | 114 |
| SquidLamp_08 | (-2.205, 2.8275, 1.50203) | (-2.075, 2.9575, 1.86203) | 114 |
| SweptCapAndRubber | (-2.55, -5.0, 0.41016) | (2.55, 5.0, 0.837) | 304 |
| TwoShortLampMasts | (-2.25, -0.935, -0.0) | (-2.03, 3.255, 1.945) | 168 |
| WheelhouseBody | (-0.85, -4.75, 0.0) | (0.85, -2.75, 1.68) | 44 |
| WheelhouseRoof | (-2.1, -4.7, 1.7) | (2.1, -0.4, 1.84) | 44 |

### Exact used material colours

| Material | sRGB hex |
|---|---|
| M_BandIvory | #F3DEA1 |
| M_BandIvory.001 | #F3DEA1 |
| M_BandIvory.002 | #F3DEA1 |
| M_ClinkerRecess | #0E2C40 |
| M_DeckWood | #C58B50 |
| M_DeckWood.001 | #C58B50 |
| M_DeckWood.002 | #C58B50 |
| M_DeckWood.003 | #C58B50 |
| M_FishSilver | #BAC9C6 |
| M_FishSilver.001 | #BAC9C6 |
| M_HullBlue | #2A6685 |
| M_HullBlue.001 | #2A6685 |
| M_HullBlue.002 | #2A6685 |
| M_HullNavy | #173F57 |
| M_HullNavy.001 | #173F57 |
| M_HullNavy.002 | #173F57 |
| M_HullNavy.003 | #173F57 |
| M_HullNavy.004 | #173F57 |
| M_HullNavy.005 | #173F57 |
| M_HullNavy.006 | #173F57 |
| M_HullNavy.007 | #173F57 |
| M_HullNavy.008 | #173F57 |
| M_JigBulb | #F3DEA1 |
| M_KelpGreen | #477A56 |
| M_KelpGreen.001 | #477A56 |
| M_OilskinYellow | #E6AD38 |
| M_OilskinYellow.001 | #E6AD38 |
| M_RailIvory | #F3F0DC |
| M_RailIvory.001 | #F3F0DC |
| M_RailIvory.002 | #F3F0DC |
| M_RailIvory.003 | #F3F0DC |
| M_RailIvory.004 | #F3F0DC |
| M_RailIvory.005 | #F3F0DC |
| M_RailIvory.006 | #F3F0DC |
| M_RailIvory.007 | #F3F0DC |
| M_Rope | #D1AF76 |
| M_Rope.001 | #D1AF76 |
| M_Rope.002 | #D1AF76 |
| M_Rope.003 | #D1AF76 |
| M_Rope.004 | #D1AF76 |
| M_Rope.005 | #D1AF76 |
| M_Rope.006 | #D1AF76 |
| M_Rubber | #28343B |
| M_Rubber.001 | #28343B |
| M_Rubber.002 | #28343B |
| M_Rubber.003 | #28343B |
| M_Rubber.004 | #28343B |
| M_Rubber.005 | #28343B |
| M_SafetyOrange | #E36A35 |
| M_SafetyOrange.001 | #E36A35 |
| M_SafetyOrange.002 | #E36A35 |
| M_SafetyOrange.003 | #E36A35 |
| M_SafetyOrange.004 | #E36A35 |
| M_SafetyOrange.005 | #E36A35 |
| M_SafetyOrange.006 | #E36A35 |
| M_SafetyOrange.007 | #E36A35 |
| M_SeaTeal | #168F9F |
| M_SeaTeal.001 | #168F9F |
| M_SeaTeal.002 | #168F9F |
| M_SeaTeal.003 | #BFE2E1 |
| M_SeaTeal.004 | #168F9F |
| M_SeaTeal.005 | #168F9F |
| M_SeaTeal.006 | #168F9F |
| M_Skin | #B9784B |
| M_Skin.001 | #B9784B |
| M_Steel | #8FA6AC |
| M_Steel.001 | #8FA6AC |
| M_Steel.002 | #8FA6AC |
| M_Steel.003 | #8FA6AC |
| M_Steel.004 | #8FA6AC |
| M_Steel.005 | #8FA6AC |
| M_Steel.006 | #8FA6AC |
| M_Steel.007 | #8FA6AC |
| M_Steel.008 | #8FA6AC |
| M_Steel.009 | #8FA6AC |
| M_Steel.010 | #8FA6AC |
| M_Steel.011 | #8FA6AC |
| M_Steel.012 | #8FA6AC |
| M_Steel.013 | #8FA6AC |
| M_Steel.014 | #8FA6AC |
| M_Steel.015 | #8FA6AC |
| M_Steel.016 | #8FA6AC |
| M_WoodHighlight | #DFB77A |
| M_WoodHighlight.001 | #DFB77A |
| M_WoodHighlight.002 | #DFB77A |
| M_WoodHighlight.003 | #DFB77A |
| M_WoodRecess | #8C5A36 |
| M_WoodRecess.001 | #8C5A36 |
| M_WoodRecess.002 | #8C5A36 |
| M_WoodRecess.003 | #8C5A36 |
| M_WoodRecess.004 | #8C5A36 |
| M_WoodRecess.005 | #8C5A36 |

## Reproduction / checks / limits

Source Art/Source/BoatsV2/Tier6/. Run Windows Blender5.2 background with build_tier6.py, review_tier6.py, then surface_audit.py; run export_card.py and finish_tier6.py with /home/mo/.venvs/catchline-ui/bin/python. inventory.py is read-only for four source blends and appends original inventory tables to the older concept report. Shared geometry2.py and HarbourV2/audit.py helpers read-only. build/review/final surface logs retained. Actual FBX audit precedes rendered review. No Unity project batchmode, import, saves or source/runtime edits performed. No subagents, no commit, no replacement backup required for new Tier6V1; accepted concept history preserved. Final receipt seals models, reports, all source scripts, input inventory, concept/card provenance, every image and audits. Source technical/visual review does not claim native integration acceptance.

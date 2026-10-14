# Gull Harbour — tier 1 modelling handoff

Built with Windows **Blender 5.2.1 LTS**, headless from WSL. This batch contains **58 editable Blender assets, 58 FBXs, 58 individual orthographic previews**, group contact sheets and [one overview beside the concept](Previews/ContactSheet.png). The [concept sheet](../../Concepts/15-gull-harbour-tier1.png) is generated artwork; the previews show the actual meshes.

## Task 03 review fixes

CaptainCap now has a closed curved crescent visor attached to its navy band, gold cord and an actual anchor badge. BreakwaterRock A/B/C have **188 triangles each**, flat soles and canonical steel/silver grey facets. KelpPatch is a drift-aligned mat of overlapping leaf silhouettes and four inset bulb disks, exactly flat at waterline. FishingRod keeps its 1.6 m height with a **48 mm blank butt, 62 mm cork grip, 14 mm tip**, enlarged reel and a separate handle pivot at Unity `(.107,.24,0)`. The exaggeration keeps it readable in the orthographic gameplay frame. CrewBody source and FBX are byte-for-byte unchanged.

The updated sources, FBXs, individual previews and contact sheets replace the previous versions. All 26 assets passed source/FBX round-trip checks again; the validator now also checks rock budgets/flat soles, curved visor geometry, rod butt width and exact zero kelp height. See the [UI kit handoff](../../../Assets/Art/UI/UI.md) for the separate 2D deliverables.

## Gameplay reference

Read the live `proto/deck-sim` checkout’s `docs/GAMEPLAY.md` before modelling: Gull Harbour is location 1, Crab Coast location 2. Tier 1 uses manual rod fishing on a rowboat, bait, a cooler and provisions. This document was an uncommitted working file at read time; it was neither merged nor edited. Its SHA-256 at handoff is `cc47a5dedb3aa313c011ca0399cae3675522890f310fd918c37747a6f247eb42`.

## Mesh inventory

Measured bounding boxes are **width × depth × height in metres** (Unity **X × Z × Y**), including all child parts. All triangles, including hidden faces and stripe geometry, count. Preview rigs are excluded. Counts are the actual triangulated totals; the crew body’s quad faces are preserved in its FBX.

| Asset / source | Triangles | W × D × H (m) | FBX |
| --- | ---: | --- | --- |
| [CrewBody](Crew/CrewBody.blend) | 5542 | 1.065492 × 0.314637 × 0.950000 | [export](../../../Assets/Art/Models/Crew/CrewBody.fbx) |
| [CaptainCap](Crew/CaptainCap.blend) | 944 | 0.354000 × 0.393000 × 0.152000 | [export](../../../Assets/Art/Models/Crew/CaptainCap.fbx) |
| [DeckhandBeanie](Crew/DeckhandBeanie.blend) | 452 | 0.348000 × 0.348000 × 0.135200 | [export](../../../Assets/Art/Models/Crew/DeckhandBeanie.fbx) |
| [OilskinHood](Crew/OilskinHood.blend) | 308 | 0.360000 × 0.234379 × 0.357000 | [export](../../../Assets/Art/Models/Crew/OilskinHood.fbx) |
| [Rowboat](Boats/Rowboat.blend) | 1526 | 4.520000 × 4.236463 × 1.020000 | [export](../../../Assets/Art/Models/Boats/Rowboat.fbx) |
| [FishingRod](Fishing/FishingRod.blend) | 1488 | 0.178500 × 0.134000 × 1.600000 | [export](../../../Assets/Art/Models/Fishing/FishingRod.fbx) |
| [Bobber](Fishing/Bobber.blend) | 184 | 0.080000 × 0.080000 × 0.120000 | [export](../../../Assets/Art/Models/Fishing/Bobber.fbx) |
| [Cooler](DeckProps/Cooler.blend) | 348 | 0.800000 × 0.500000 × 0.450000 | [export](../../../Assets/Art/Models/DeckProps/Cooler.fbx) |
| [IceBox](DeckProps/IceBox.blend) | 444 | 0.800000 × 0.500000 × 0.450000 | [export](../../../Assets/Art/Models/DeckProps/IceBox.fbx) |
| [BaitBucket](DeckProps/BaitBucket.blend) | 340 | 0.300000 × 0.300000 × 0.366928 | [export](../../../Assets/Art/Models/DeckProps/BaitBucket.fbx) |
| [LunchTin](DeckProps/LunchTin.blend) | 132 | 0.250000 × 0.184000 × 0.120000 | [export](../../../Assets/Art/Models/DeckProps/LunchTin.fbx) |
| [Herring](Fish/Herring.blend) | 264 | 0.057460 × 0.260000 × 0.054990 | [export](../../../Assets/Art/Models/Fish/Herring.fbx) |
| [Mackerel](Fish/Mackerel.blend) | 672 | 0.075140 × 0.340000 × 0.067915 | [export](../../../Assets/Art/Models/Fish/Mackerel.fbx) |
| [Pollock](Fish/Pollock.blend) | 264 | 0.122400 × 0.480000 × 0.124080 | [export](../../../Assets/Art/Models/Fish/Pollock.fbx) |
| [SeaBass](Fish/SeaBass.blend) | 264 | 0.144500 × 0.500000 × 0.152750 | [export](../../../Assets/Art/Models/Fish/SeaBass.fbx) |
| [CongerEel](Fish/CongerEel.blend) | 248 | 0.065450 × 0.800000 × 0.084600 | [export](../../../Assets/Art/Models/Fish/CongerEel.fbx) |
| [Quay4m](Harbour/Quay4m.blend) | 842 | 4.000000 × 2.000000 × 0.900000 | [export](../../../Assets/Art/Models/Harbour/Quay4m.fbx) |
| [Bollard](Harbour/Bollard.blend) | 268 | 0.440000 × 0.320000 × 0.475000 | [export](../../../Assets/Art/Models/Harbour/Bollard.fbx) |
| [LampPost](Harbour/LampPost.blend) | 352 | 0.420000 × 0.760000 × 2.800000 | [export](../../../Assets/Art/Models/Harbour/LampPost.fbx) |
| [HouseA](Harbour/HouseA.blend) | 744 | 3.344376 × 2.900000 × 3.641641 | [export](../../../Assets/Art/Models/Harbour/HouseA.fbx) |
| [HouseB](Harbour/HouseB.blend) | 744 | 3.740886 × 3.100000 × 3.942191 | [export](../../../Assets/Art/Models/Harbour/HouseB.fbx) |
| [Lighthouse](Harbour/Lighthouse.blend) | 772 | 1.900000 × 1.900000 × 6.000000 | [export](../../../Assets/Art/Models/Harbour/Lighthouse.fbx) |
| [BreakwaterRockA](Harbour/BreakwaterRockA.blend) | 188 | 1.800000 × 1.400000 × 1.000000 | [export](../../../Assets/Art/Models/Harbour/BreakwaterRockA.fbx) |
| [BreakwaterRockB](Harbour/BreakwaterRockB.blend) | 188 | 1.300000 × 1.100000 × 0.800000 | [export](../../../Assets/Art/Models/Harbour/BreakwaterRockB.fbx) |
| [BreakwaterRockC](Harbour/BreakwaterRockC.blend) | 188 | 2.100000 × 1.500000 × 1.200000 | [export](../../../Assets/Art/Models/Harbour/BreakwaterRockC.fbx) |
| [KelpPatch](Harbour/KelpPatch.blend) | 168 | 1.157554 × 0.375101 × 0.000000 | [export](../../../Assets/Art/Models/Harbour/KelpPatch.fbx) |

The Rowboat assembly bounds include the outboard oars: the hull itself is **4.2 m fore-aft × 2.4 m beam**, and its usable rectangular deck is **3 m fore-aft × 2 m across**. The deck is at local height zero; the hull extends below it. Quay bounds likewise include supporting piles below its zero-height walking surface. The floating kelp is exactly flat at waterline. Overlapping leaf silhouettes are unioned and four flat bulb disks are inset without overlapping faces, preventing z-fighting.

Exact requested dimensions: rod butt-to-tip 1.6 m; bobber total height 0.12 m; cooler and ice-box 0.80 × 0.50 × 0.45 m; fish nose-to-tail 0.26 / 0.34 / 0.48 / 0.50 / 0.80 m; bare crew 0.95 m. Sizes not supplied by Mo are art choices documented in STYLE.md and the measured table. No additional mesh budgets were imposed on this new kit.

## Parts, origins and animation handoff

All roots have zero translation/rotation and scale one. All mesh parts have applied rotation/scale, with intentional translations at moving-part pivots. Sources use Blender **X right, -Y forward, Z up**; export bakes the basis to Unity **X right, +Z forward, +Y up**. Source point `(x,y,z)` becomes Unity `(x,z,-y)`. Grounded roots follow STYLE.md; deck/waterline roots and hat mounting seats are deliberate exceptions.

| Asset | Separate parts / pivot rules |
| --- | --- |
| Rowboat | Hull, plank deck, ivory gunwale, centre thwart, oarlocks, two oars, two rod sockets. Oar pivots Unity `(-1.12,.49,0)` / `(1.12,.49,0)`. Port sockets `(-1.115,.44,-1)` / `(-1.115,.44,+1)`: 0.5 / 2.5 m forward of rectangular deck stern Z=-1.5. |
| Rod | Butt at root, rod upright along +Y for attachment. Separate reel handle at `(.107,.24,0)`. No simulated fishing line is embedded. |
| Bobber | Root at waterline; bottom Y=-.045, top Y=.075. |
| Cooler / ice box | Identical CoolerBody mesh; separate HingedLid at `(0,.40,-.25)`, rotate local X to open. Teal variant adds solid ivory frost motifs on its lid. |
| Lunch tin | Separate lid on its rear hinge. |
| Fish | Ground root, nose faces +Z; separate tail whose origin is the body-tail join. Mackerel uses solid navy stripe geometry. |
| Crew / hats | Bare scalp .95 m, hat mounting point `(0,.91,0)`. Separate cap, beanie and open-front oilskin hood, each with a seat origin. |
| Harbour | Quay root at walking plane; posts extend below it. Houses, bollard, lamp, lighthouse and rocks sit on ground. Kelp lies exactly at waterline Y=0 with upward faces; use a two-sided material for underwater views. |

Parts are siblings under an identity empty root, preserving explicit animation origins without nested mesh-parent axis-bake errors. Complete source-space pivot coordinates and per-part geometry hashes are in [build-metrics.json](build-metrics.json). No armatures, rigs or animation clips are supplied.

## Crew topology

The shared body is one connected, closed **2,442-quad** surface (4,884 render triangles), with **zero nonquad faces, nonmanifold edges/vertices or inconsistent winding edges**. Face, hair and garment accents are a separate 658-triangle detail mesh, bringing the full asset to **5,542 triangles**. Arms are extended horizontally in T-pose; hands are mitten shapes, not individual articulated fingers. Body height is 0.95 m.

The body was voxel unified then QuadriFlow remeshed into quads. Temporary vertex scaling works around QuadriFlow’s small-edge tolerance, then returns to metres before export; object scale stays one. This is a clean unrigged starting mesh for Mixamo, not a claim that automatic rigging or deformation has been tested. Mixamo upload, bone weights and animation tests remain for the rigging pass.

## Materials and visual review

No bitmap textures or embedded images. Flat named materials follow [STYLE.md](../../STYLE.md): M_HullNavy, M_HullBlue, M_DeckWood, M_WoodHighlight, M_WoodRecess, M_RailIvory, M_SafetyOrange, M_SeaTeal, M_Steel, M_Rubber, M_Rope, M_OilskinYellow, M_Skin, M_KelpGreen and M_FishSilver as used by each mesh. Canonical sRGB colours are converted to Blender linear values. Shared Unity URP material remapping is a later integration step.

Previews use an orthographic camera **45° down / 35° yaw**, cream background, broad area lights and Cycles CPU rendering (24 samples, denoised). Each asset is individually framed, so contact sheets are not common-scale diagrams. Preview-only cameras, lights and floor are in their own source collection and excluded from FBX. Shapes use broad facets, readable silhouettes and restrained bevels; the illustration contains more detail than these first meshes.

- [Boat preview](Previews/Boats/Rowboat.png)
- [Fishing gear](Previews/Fishing-contact.png)
- [Deck props](Previews/DeckProps-contact.png)
- [Fish](Previews/Fish-contact.png)
- [Crew and hats](Previews/Crew-contact.png)
- [Harbour kit](Previews/Harbour-contact.png)

## Verification

All **26 sources and 26 exports passed** the saved [validator](validation.json): dimensions, part origins, applied rotation/scale, named texture-free materials, no modifiers/armatures, crew topology, exact deck/socket/hinge/fish constraints and shared cooler-body geometry. Binary FBX axes are Y-up/Z-forward with UnitScaleFactor 100 (one stored unit = one metre), and no camera/light/texture/video attributes. A fresh Blender FBX import reproduces every mesh’s triangle count, overall bounds and moving-part origins within 0.00001 m; crew quads survive import.

The updated Crab Coast EmptyPot and FullPot also pass the original six-prop validator. Their 0.70 × 0.55 × 0.35 m frames now have chunky 0.036 m rails/posts, four rope lashings and an enlarged teal latch. Counts are **1,064 / 1,496**, both within the 1,500-triangle limit. FullPot shares PotBody and has a separate 432-triangle crab load. See [updated crab report](../Props/REPORT.md).

**Unity and Mixamo were not opened or run.** No Assets/Scripts or Assets/Scenes changes. FBX import settings, material mapping, runtime shadows, animations and device performance need later integration validation.

## Rebuild

From WSL in the art worktree:

```bash
"/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" \
  --background --factory-startup --python-exit-code 1 \
  --python 'C:\Users\momoy\Projects\Catchline-art-style\Art\Source\build_gull_harbour.py'

"/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" \
  --background --factory-startup --python-exit-code 1 \
  --python 'C:\Users\momoy\Projects\Catchline-art-style\Art\Source\validate_gull_harbour.py'

python3 Art/Source/gull_contact_sheets.py
```

Builder accepts asset-name subsets after `--`. It imports the existing crab builder helpers; both scripts must remain together in Art/Source. The contact composer uses WSL ffmpeg and DejaVu Sans. Actual sources are under `Art/Models/GullHarbour/<Group>/`, exports under `Assets/Art/Models/<Group>/`; sources and images use the repository’s existing Git LFS rules.

Task 03 kelp geometry is preprocessed by `Art/Source/build_kelp_mat.py` (Shapely 2.1+) into `kelp-mat.json`; the Blender builder reads that planar geometry without extra Blender dependencies.

## Task 04 delivery

Current measured inventory below supersedes the earlier tier 1 table. All assets include editable source, FBX and orthographic preview under the existing group directories. Existing asset names, complete part-name sets and pivots are checked against the saved Task 03 baseline, alongside source/FBX round-trip checks.

Part A: pointed rowboat bow, flat transom, rising sheer, rope fender and stripe; cooler handles/latch/rim/drain; framed house windows, steps, chimney and eave trim; quay rings/wear plus Quay4mLadder; lighthouse gallery and glazed lamp room. Cooler and IceBox still share the same body geometry.

Part B: six deck props; Plaice (0.36 m, flat) and Cod (0.70 m), each with a separate tail; seven harbour props including MarketStallAwning and 0.4 m perched Seagull with Wing_L/Wing_R; five ShopFront groups; five sea modules. Shop fronts use ground/door-centre roots, face Unity −Z, and leave the central doorway clear. Their previews are framed from the water-facing side to show papers, charts and rope displays. SandBank is exactly flat, 4 × 2 m; CliffSegment8m has matching end profiles at X ±4; DistantShip hull silhouette is 8 m fore-aft.

Part C: Skiff with 5 × 3 m deck at height zero, 6.5 × 3.5 m hull (motor excluded), Propeller, HoldLid and RodSocket_1..3. Console occupies starboard/stern tile c=2, r=0 (zero-based, columns port→starboard; rows stern→bow), Unity centre (1,0,−2); this overrides the earlier forward-console suggestion in STYLE.md. HandWinch fits 1 × 1 m with Crank. GillNetCoil, GillNetFloatLine and GillNetSection provide deck storage and 2 m water modules. SortTable fits 2 × 1 m with tray, chute and bin. FishHold is included in Skiff: HoldLid rotates local X at its rear hinge; no redundant standalone hatch is supplied. No animation clips are included. Front/side/top boat views and an open-hold render accompany the focused SkiffKit and BoatViews contact sheets.

New M_ names: **none**. All exports reuse the canonical palette. Open surfaces (nets and waterline sand) need two-sided material handling at integration. Unity was not opened; Assets/Scripts and Assets/Scenes were not touched. No requested modelling work remains unfinished in the delivered parts; Unity import/material and animation integration remain for the game branch.

| Asset | Triangles | Width × depth × height (m) |
| --- | ---: | --- |
| [CrewBody](Crew/CrewBody.blend) | 5542 | 1.0655 × 0.3146 × 0.9500 |
| [CaptainCap](Crew/CaptainCap.blend) | 944 | 0.3540 × 0.3930 × 0.1520 |
| [DeckhandBeanie](Crew/DeckhandBeanie.blend) | 452 | 0.3480 × 0.3480 × 0.1352 |
| [OilskinHood](Crew/OilskinHood.blend) | 308 | 0.3600 × 0.2344 × 0.3570 |
| [Rowboat](Boats/Rowboat.blend) | 1790 | 4.5200 × 4.2850 × 1.0200 |
| [FishingRod](Fishing/FishingRod.blend) | 1488 | 0.1785 × 0.1340 × 1.6000 |
| [Bobber](Fishing/Bobber.blend) | 184 | 0.0800 × 0.0800 × 0.1200 |
| [Cooler](DeckProps/Cooler.blend) | 556 | 0.8000 × 0.5000 × 0.4500 |
| [IceBox](DeckProps/IceBox.blend) | 652 | 0.8000 × 0.5000 × 0.4500 |
| [BaitBucket](DeckProps/BaitBucket.blend) | 340 | 0.3000 × 0.3000 × 0.3669 |
| [LunchTin](DeckProps/LunchTin.blend) | 132 | 0.2500 × 0.1840 × 0.1200 |
| [Herring](Fish/Herring.blend) | 264 | 0.0575 × 0.2600 × 0.0550 |
| [Mackerel](Fish/Mackerel.blend) | 672 | 0.0751 × 0.3400 × 0.0679 |
| [Pollock](Fish/Pollock.blend) | 264 | 0.1224 × 0.4800 × 0.1241 |
| [SeaBass](Fish/SeaBass.blend) | 264 | 0.1445 × 0.5000 × 0.1527 |
| [CongerEel](Fish/CongerEel.blend) | 248 | 0.0655 × 0.8000 × 0.0846 |
| [Quay4m](Harbour/Quay4m.blend) | 1114 | 4.0000 × 2.0000 × 1.0330 |
| [Bollard](Harbour/Bollard.blend) | 268 | 0.4400 × 0.3200 × 0.4750 |
| [LampPost](Harbour/LampPost.blend) | 352 | 0.4200 × 0.7600 × 2.8000 |
| [HouseA](Harbour/HouseA.blend) | 932 | 3.4000 × 3.0800 × 3.9300 |
| [HouseB](Harbour/HouseB.blend) | 932 | 3.8000 × 3.2800 × 4.2300 |
| [Lighthouse](Harbour/Lighthouse.blend) | 1284 | 1.9000 × 1.9000 × 6.0000 |
| [BreakwaterRockA](Harbour/BreakwaterRockA.blend) | 188 | 1.8000 × 1.4000 × 1.0000 |
| [BreakwaterRockB](Harbour/BreakwaterRockB.blend) | 188 | 1.3000 × 1.1000 × 0.8000 |
| [BreakwaterRockC](Harbour/BreakwaterRockC.blend) | 188 | 2.1000 × 1.5000 × 1.2000 |
| [KelpPatch](Harbour/KelpPatch.blend) | 168 | 1.1576 × 0.3751 × 0.0000 |
| [Quay4mLadder](Harbour/Quay4mLadder.blend) | 1274 | 4.0000 × 2.1300 × 1.2800 |
| [RopeCoil](DeckProps/RopeCoil.blend) | 1216 | 0.6711 × 0.5614 × 0.0450 |
| [TackleBox](DeckProps/TackleBox.blend) | 236 | 0.4400 × 0.3140 × 0.3311 |
| [NetBundle](DeckProps/NetBundle.blend) | 508 | 0.5590 × 0.3460 × 0.1615 |
| [SmallAnchor](DeckProps/SmallAnchor.blend) | 212 | 0.5800 × 0.1400 × 0.6800 |
| [Fender](DeckProps/Fender.blend) | 412 | 0.2040 × 0.2040 × 0.5610 |
| [Lantern](DeckProps/Lantern.blend) | 296 | 0.2400 × 0.2400 × 0.4870 |
| [Plaice](Fish/Plaice.blend) | 420 | 0.2800 × 0.3600 × 0.0590 |
| [Cod](Fish/Cod.blend) | 284 | 0.3213 × 0.7000 × 0.2385 |
| [Barrel](Harbour/Barrel.blend) | 688 | 0.5920 × 0.5920 × 0.6560 |
| [CrateStack](Harbour/CrateStack.blend) | 2244 | 0.9850 × 0.4200 × 0.6800 |
| [FishCrate](Harbour/FishCrate.blend) | 1108 | 0.4850 × 0.3400 × 0.3350 |
| [Lifebuoy](Harbour/Lifebuoy.blend) | 304 | 0.6800 × 0.1510 × 0.6800 |
| [NetRack](Harbour/NetRack.blend) | 372 | 1.9600 × 0.5000 × 1.6000 |
| [MarketStallAwning](Harbour/MarketStallAwning.blend) | 2500 | 2.4000 × 1.6400 × 2.2900 |
| [Seagull](Harbour/Seagull.blend) | 632 | 0.2200 × 0.4000 × 0.3400 |
| [ShopFront_FishMarket](Harbour/ShopFront_FishMarket.blend) | 3484 | 2.1850 × 0.5150 × 1.8250 |
| [ShopFront_HarbourMaster](Harbour/ShopFront_HarbourMaster.blend) | 392 | 2.6300 × 0.3000 × 2.5000 |
| [ShopFront_CrewOffice](Harbour/ShopFront_CrewOffice.blend) | 280 | 0.9000 × 0.1250 × 1.6000 |
| [ShopFront_Chandlery](Harbour/ShopFront_Chandlery.blend) | 1600 | 2.3400 × 0.4704 × 0.8000 |
| [ShopFront_Supplies](Harbour/ShopFront_Supplies.blend) | 1860 | 2.4060 × 1.1560 × 0.6560 |
| [SandBank](Sea/SandBank.blend) | 5 | 4.0000 × 2.0000 × 0.0000 |
| [SeaRockCluster](Sea/SeaRockCluster.blend) | 162 | 2.2658 × 1.3386 × 0.8400 |
| [CliffSegment8m](Sea/CliffSegment8m.blend) | 46 | 8.0000 × 2.8000 × 2.3000 |
| [ChannelBuoy](Sea/ChannelBuoy.blend) | 240 | 0.8600 × 0.8600 × 1.5000 |
| [DistantShip](Sea/DistantShip.blend) | 164 | 2.0000 × 8.0000 × 2.4000 |
| [Skiff](Boats/Skiff.blend) | 2494 | 3.5874 × 7.0355 × 1.4825 |
| [HandWinch](Stations/HandWinch.blend) | 1400 | 0.8000 × 0.6200 × 0.5800 |
| [GillNetCoil](Fishing/GillNetCoil.blend) | 904 | 0.7415 × 0.5460 × 0.1820 |
| [GillNetFloatLine](Fishing/GillNetFloatLine.blend) | 588 | 2.0000 × 0.1140 × 0.1140 |
| [GillNetSection](Fishing/GillNetSection.blend) | 332 | 2.0000 × 1.5300 × 0.0300 |
| [SortTable](Stations/SortTable.blend) | 536 | 1.8300 × 0.7600 × 0.6400 |

Rebuild additions with `build_task04.py -- B` or `-- C`; Part A uses the existing builder. Then run `validate_gull_harbour.py`, `gull_contact_sheets.py` and `task04_report.py`. Additional boat views use `render_task04_boat_views.py` before composing contacts. Detailed part pivots and notes are in build-metrics.json.

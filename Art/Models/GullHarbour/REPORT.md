# Gull Harbour — tier 1 modelling handoff

Built with Windows **Blender 5.2.1 LTS**, headless from WSL. This batch contains **26 editable Blender assets, 26 FBXs, 26 orthographic previews**, group contact sheets and [one overview beside the concept](Previews/ContactSheet.png). The [concept sheet](../../Concepts/15-gull-harbour-tier1.png) is generated artwork; the previews show the actual meshes.

## Gameplay reference

Read the live `proto/deck-sim` checkout’s `docs/GAMEPLAY.md` before modelling: Gull Harbour is location 1, Crab Coast location 2. Tier 1 uses manual rod fishing on a rowboat, bait, a cooler and provisions. This document was an uncommitted working file at read time; it was neither merged nor edited. Its SHA-256 at handoff is `cc47a5dedb3aa313c011ca0399cae3675522890f310fd918c37747a6f247eb42`.

## Mesh inventory

Measured bounding boxes are **width × depth × height in metres** (Unity **X × Z × Y**), including all child parts. All triangles, including hidden faces and stripe geometry, count. Preview rigs are excluded. Counts are the actual triangulated totals; the crew body’s quad faces are preserved in its FBX.

| Asset / source | Triangles | W × D × H (m) | FBX |
| --- | ---: | --- | --- |
| [CrewBody](Crew/CrewBody.blend) | 5542 | 1.065492 × 0.314637 × 0.950000 | [export](../../../Assets/Art/Models/Crew/CrewBody.fbx) |
| [CaptainCap](Crew/CaptainCap.blend) | 444 | 0.354000 × 0.381000 × 0.125000 | [export](../../../Assets/Art/Models/Crew/CaptainCap.fbx) |
| [DeckhandBeanie](Crew/DeckhandBeanie.blend) | 452 | 0.348000 × 0.348000 × 0.135200 | [export](../../../Assets/Art/Models/Crew/DeckhandBeanie.fbx) |
| [OilskinHood](Crew/OilskinHood.blend) | 308 | 0.360000 × 0.234379 × 0.357000 | [export](../../../Assets/Art/Models/Crew/OilskinHood.fbx) |
| [Rowboat](Boats/Rowboat.blend) | 1526 | 4.520000 × 4.236463 × 1.020000 | [export](../../../Assets/Art/Models/Boats/Rowboat.fbx) |
| [FishingRod](Fishing/FishingRod.blend) | 716 | 0.128000 × 0.086000 × 1.600000 | [export](../../../Assets/Art/Models/Fishing/FishingRod.fbx) |
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
| [BreakwaterRockA](Harbour/BreakwaterRockA.blend) | 20 | 1.800000 × 1.400000 × 1.000000 | [export](../../../Assets/Art/Models/Harbour/BreakwaterRockA.fbx) |
| [BreakwaterRockB](Harbour/BreakwaterRockB.blend) | 20 | 1.300000 × 1.100000 × 0.800000 | [export](../../../Assets/Art/Models/Harbour/BreakwaterRockB.fbx) |
| [BreakwaterRockC](Harbour/BreakwaterRockC.blend) | 20 | 2.100000 × 1.500000 × 1.200000 | [export](../../../Assets/Art/Models/Harbour/BreakwaterRockC.fbx) |
| [KelpPatch](Harbour/KelpPatch.blend) | 70 | 0.901051 × 0.936302 × 0.000000 | [export](../../../Assets/Art/Models/Harbour/KelpPatch.fbx) |

The Rowboat assembly bounds include the outboard oars: the hull itself is **4.2 m fore-aft × 2.4 m beam**, and its usable rectangular deck is **3 m fore-aft × 2 m across**. The deck is at local height zero; the hull extends below it. Quay bounds likewise include supporting piles below its zero-height walking surface. The floating kelp has zero thickness.

Exact requested dimensions: rod butt-to-tip 1.6 m; bobber total height 0.12 m; cooler and ice-box 0.80 × 0.50 × 0.45 m; fish nose-to-tail 0.26 / 0.34 / 0.48 / 0.50 / 0.80 m; bare crew 0.95 m. Sizes not supplied by Mo are art choices documented in STYLE.md and the measured table. No additional mesh budgets were imposed on this new kit.

## Parts, origins and animation handoff

All roots have zero translation/rotation and scale one. All mesh parts have applied rotation/scale, with intentional translations at moving-part pivots. Sources use Blender **X right, -Y forward, Z up**; export bakes the basis to Unity **X right, +Z forward, +Y up**. Source point `(x,y,z)` becomes Unity `(x,z,-y)`. Grounded roots follow STYLE.md; deck/waterline roots and hat mounting seats are deliberate exceptions.

| Asset | Separate parts / pivot rules |
| --- | --- |
| Rowboat | Hull, plank deck, ivory gunwale, centre thwart, oarlocks, two oars, two rod sockets. Oar pivots Unity `(-1.12,.49,0)` / `(1.12,.49,0)`. Port sockets `(-1.115,.44,-1)` / `(-1.115,.44,+1)`: 0.5 / 2.5 m forward of rectangular deck stern Z=-1.5. |
| Rod | Butt at root, rod upright along +Y for attachment. Separate reel handle at `(.077,.24,0)`. No simulated fishing line is embedded. |
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

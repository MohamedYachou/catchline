# TIER5-103 approved two-rig production asset

Mo approved the TIER5-102 two-pole preview. This delivers its authored geometry as **new, separately named assets**; the old model remains active. No gameplay, importer, ArtLibrary, UI, save, build or installation changes.

## Files and reproduction

- `Art/Models/Tier5DeepLines103/Tier5DeepLines103.blend`: production source, original approved hull plus two rigs, named switchable groups/anchors. No studio/camera/lights/crew. Hidden, clearly marked RENDER ONLY collection contains reference normal rods and cage/buoys, excluded from every FBX.
- `Assets/Art/Models/Boats/Tier5DeepLines103.fbx`: complete alternative boat; **139 objects, 17,096 triangles** after actual export/reimport.
- `Assets/Art/Models/Boats/Tier5DeepLineRig103.fbx`: separate two-rig module at the same hull-centred origin; **43 objects, 1,296 triangles**. Use either this additive module or the full boat, never both copies of its rigs.
- `Tier5DeepLines103-review.blend`: separate studio with reference props for image reproduction only.
- `01-rod-deepline-beauty.png`, `03-side-net-beauty.png`: final 1800×1375 orthographic rendered comparisons. Approved unchanged102 plans remain placement references (`../Tier5DeepLines102/02-rod-deepline-plan.png` and `04-side-net-plan.png`); the103receipt provides exact production mesh bounds. Final rod beauty uses64samples; final side-net beauty16samples with denoising.
- `export.json`: actual reimport receipt, SHA256, source mesh bounds, source/roundtrip anchors, material list, topology counts and checks. `export-render.log`: Windows Blender run.
- `Art/Source/export_tier5_deeplines103.py`: reproducible author/export/verify/render script. Run in **Windows Blender5.2**: `blender.exe -b --python C:\Users\momoy\Projects\Catchline\Art\Source\export_tier5_deeplines103.py`.

The production source is read directly from the approved5.2 `Tier5Production071/Tier5FisherV1.blend`, not a downgraded preview. Original source, original FBX, original exporter and approved102preview SHA256 fingerprints are recorded and checked unchanged. No temporary local-copy workflow or Unity-generated metadata was used.

## Geometry and hierarchy

Hull remains **8.50m long ×4.20m beam**, deck root at origin, six hired crew plus captain unchanged. Blender axes: X across deck, -Y bow, +Y stern, Z up. Geometry is exported with the existing071 FBX axis settings (`axis_forward=-Z`, `axis_up=Y`); actual imported transforms are recorded, rather than assuming source coordinates are directly Unity-local coordinates.

| Group | Required behavior in later integration |
|---|---|
| `DeepLineModule` | Contains exactly `DeepLineRig_1` and `_2`, worker/base/tip anchors. Show with optional rods; hide completely for side net. |
| `OptionalRodModule` | Original `RodHolder_3/4` and `RodSocket_3/4`. Show with deep-line layout; hide for side net. Actual normal rod meshes are runtime-owned. |
| `NetModule1` | Original fixed rear net geometry, always installed. |
| `NetModule2` | Existing optional net geometry rotated/moved to requested optional +X side. Show only when optional rods/deep lines are absent. |
| `RawBuckets` / `RawIceCoolers` | Preserved alternative raw storage. Select exactly one using existing upgrade state. |
| `PrepStation` / `PreparedHold` | Preserved preparation/storage. |

The FBX deliberately contains **all equipment alternatives**, as the prior production contract did. Visibility flags in a Blender review scene are not a game switch. Later runtime must toggle the complete groups AND corresponding spawned rods, jobs and anchors. Fixed `RodHolder_1/2`, sockets1/2, both buoy stations/anchors, rear net remain. RawBuckets are hidden in beauty renders, RawIceCoolers shown. No new crew types or baked crew.

The side-net parent's transformation is baked into its children's geometry before export, preserving world placement while returning the group to identity. Rig children are parented while preserving world matrices. Rod mesh rotations/scales are applied; pivots remain real named empties. Neither transformation relies on a consumer applying the side-net rotation twice.

## Exact source anchors and static placement

| Name | Blender source world metres |
|---|---|
| `DeepLineModule` | (0,0,0), also standalone asset root |
| `DeepLineRig_1` / `DeepLineBase_1` | (1.87,0.40,0.46) |
| `DeepLineRig_2` / `DeepLineBase_2` | (1.87,1.82,0.46) |
| `DeepLineWorker_1/2` | (1.25,0.40,0) / (1.25,1.82,0) |
| `DeepLineTip_1/2` | (3.34,0.40,3.14) / (3.34,1.82,3.14) |
| `DeepLineReelPivot_1/2` | (1.94,0.40,0.74) / (1.94,1.82,0.74) |
| `NetWorker_1` | **Adjusted** to (0.95,3.10,0), inboard of fixed stern net |
| `NetWorker_2` | **Adjusted** to (1.25,1.80,0), inboard of new side net |

Each reel pivot contains spool/flanges, crank and handle, with local **Y** reel axis in Blender. Poles, line and clamp remain under the rig root, outside the reel pivot. Future code can rotate the manual reel assembly around that pivot; no clips are baked. Line endpoints/tips are named, but no dynamic line behavior is implemented.

The two tall poles retain the approved positions, taper, manual reels, orange grips and hanging fishing lines. Base separation1.42m. Tips3.14m above deck (1.64m above canopy) and1.24m outside hull edge. Clamp0.22×0.30m at the rail; reel flange diameter0.41m. Inboard crank extreme approximatelyX1.65 leaves approximately0.91m to prep'sX0.74 edge. Worker centresX1.25 are in this existing side aisle. These are **static mesh placement assessments**, not pathfinding or animation proof. Deep basesY0.40/1.82 interleave existing optional rod socketsY1.10/2.55, avoiding their direct mounting positions; forward deep base is2.45m aft of buoy-service lineY-2.05. Canopy rear edgeY≈-0.90 stays clear.

Both legacy `ServiceAccess_1/2` anchors remain for saved/import/source compatibility. Actual Engineer service controls, hatch and status-lamp meshes are deleted in this NEW asset. They remain untouched in the original model. No wear, maintenance or role behavior is changed.

No third rod added: midpointY1.11 conflicts with the existing optional normal socket; an aft addition would approach rear-net work. Catch batches3/5 do not specify physical rod count.

## Materials

Existing source materials are retained to preserve the approved appearance. Canonical `M_Rope` uses STYLE.md's **#D1AF76**, converted from sRGB to linear for the new plain material. No new production material family is invented. Original numeric material datablock suffixes (such as `M_RailIvory.002`) remain where inherited by the approved source; these are existing palette variants, not new names requiring a new game palette. Exact used slot names are in `export.json`. Palette families include navy/blue, honey timber/highlight/recess, ivory, teal, orange, satin steel, rubber and rope. The review stage's separate sea material is excluded from export.

## Verification and limits

Windows Blender5.2 exports and imports both actual FBXs. Assertions check hull bounds, required old/new names, exactly two rig roots, finite mesh coordinates, positive scales, absent stage/crew/runtime-proxy/Engineer geometry, exact source tip/reel anchor positions, preserved source-to-reimport tip/worker distances, and every exported mesh’s world dimensions and distance from hull origin. Each FBX object carries `Tier5SourceName` metadata to unambiguously match original names when reimporting alongside the loaded source scene. The receipt includes every source mesh bound and required roundtrip anchor for inspection. Sorted reimport hull dimensions are approximately1.105×4.20×8.50m. Source and imported object counts/triangles are recorded separately because bevel evaluation occurs on export.

Final images are Blender renders of actual geometry, with normal rods/cage/buoys only as clearly separated runtime references. No Unity import/material hookup, native camera parity, job scheduling, route tests, crew animation, runtime layout switch, line animation, mobile readability/performance or balance acceptance is claimed. In particular, source `NetWorker` changes and new equipment visibility require later C# integration; replacing the active model without that work would be incomplete.

No commit. All original production and approved-preview files remain unchanged. This is a finished art handoff for later integration, not a playable feature delivery.

# Skerries life — artist handoff

SKERRIES-LIFE-1 · Codex 2 (WSL CLI) · 2026-10-25

Seven metre-scale Blender sources and FBX exports are complete. Source/actual-FBX geometry checks pass, the seal's three actions pass sampled deformation checks, and all **81 final PNGs were individually opened**. These are isolated Blender artist reviews. Unity import, Legacy clip configuration, runtime placement/animation and native water/HUD acceptance belong to Claude/Codex 1 and are not claimed here.

## Delivery and budgets

Dimensions below are Unity X width × Z length × Y height, in metres, measured from the authored rest geometry. Every logical root is at the base/waterline centre with unit scale. Small asymmetric faceted rock bounds need not be symmetric about that logical centre.

| Asset/source | FBX | Triangles | Dimensions | Contents |
|---|---|---:|---|---|
| [Seal.blend](Seal.blend) | [Seal.fbx](Seal.fbx) | 636 | .810 × 1.629 × .561 | Grey harbour seal, six-bone skin, three actions |
| [SealColony.blend](SealColony.blend) | [SealColony.fbx](SealColony.fbx) | 1,964 | 4.480 × 2.450 × .865 | Three static, differently posed seals on a .30m rock slab |
| [SealSwimHead.blend](SealSwimHead.blend) | [SealSwimHead.fbx](SealSwimHead.fbx) | 510 | 1.100 × 1.639 × .355 | Trimmed head/upper back and small ivory/teal V-wake |
| [ReefBreak_A.blend](ReefBreak_A.blend) | [ReefBreak_A.fbx](ReefBreak_A.fbx) | 112 | 6 × 2 × 0 | Broken crest ribbons and foam flecks |
| [ReefBreak_B.blend](ReefBreak_B.blend) | [ReefBreak_B.fbx](ReefBreak_B.fbx) | 112 | 6 × 2 × 0 | Alternate crest spacing and phase |
| [CrabBuoySet.blend](CrabBuoySet.blend) | [CrabBuoySet.fbx](CrabBuoySet.fbx) | 216 | 1.478 × 1.653 × 1.320 | Red/ivory buoy, mast, red flag, two floating lines |
| [PotStack.blend](PotStack.blend) | [PotStack.fbx](PotStack.fbx) | 2,001 | 1.985 × 1.294 × .877 | Five CageKit-derived static creels on a rock ledge |

Strict brief budgets pass: Seal **636 < 2,000**; colony + swim **2,474 < 4,000**; both reefs **224 < 600**; buoy + stack **2,217 < 2,500**. All seven together: 5,551 triangles.

No textures, image dependencies, review cameras, lights or review ground are exported. Shared named house materials use Steel #8FA6AC, FishSilver #BAC9C6, Rubber #28343B, RailIvory #F3F0DC, HullNavy #173F57, SeaTeal #168F9F, ShallowWater #64C7C4, Rope #D1AF76, SafetyOrange #E36A35, LegalRed #CF4232 and KelpGreen #477A56. Remap matching material names to the game's shared materials during import; no loose texture folders are needed.

## Placement and animation contract

The source convention is Blender X right, -Y forward, Z up. FBX uses -Z forward/Y up and metres; intended Unity convention is X right, +Z forward, Y up. Static exports bake axis conversion; the animated seal retains its rig hierarchy. Actual FBX reimport checks preserve world surfaces, unit scale and parent relationships. Unity's importer still needs its normal project settings and native verification.

- **Seal:** `Seal / SealRig / SealSkin`; bones `Root`, `Body`, `Head`, `Fore.L`, `Fore.R`, `Tail`. Its logical base is Y=0; the lowest resting skin is .004m above it. Keep the root fixed while an action plays. Set the import rig/clip type to Legacy and identify clips by the final name segment `Bask`, `Look`, `Slide`: FBX tools can prefix the rig name (Blender reimport reports `SealRig|SealRig|Bask`, for example).
- **SealColony:** place the root on the map's colony base anchor. The rock slab is included; seal feet are .30m above the root. It contains three static Seal-derived poses/scales, not three active rigs. Consume final `navigation.json` `sealColonyAnchors` from Codex 1's GullSkerries delivery rather than hardcoding the provisional positions from the diary.
- **SealSwimHead:** root at mean water Y; upper geometry is clipped to that waterline, with the V-wake at local Y=.008. All exported wake faces point upward. Face Unity +Z; translate/rotate the entire root for swimming.
- **ReefBreak_A/B:** root at water Y+.012m, or a little higher if runtime displacement requires it. Each mesh is flat at local Y=0 with upward faces. UVs span 0–1 over the exact 6×2m envelope: `U = UnityX/6 + .5`, `V = -UnityZ/2 + .5`. The geometric gaps are open water. Scrolling a uniform solid material alone has no visible effect: use Claude's shared patterned/procedural foam shader for UV scroll, or gently pulse the root scale. No shader or runtime animation is supplied by this artist task.
- **CrabBuoySet:** root at mean water+.015m; floating ropes are local Y=.009, and the mast/closed thin flag top is 1.32m. Bob/rotate the whole set. The red/ivory silhouette remains visible in both required camera sizes.
- **PotStack:** place its root on the shore/ledge base, keeping the included rock. Four lower cages and one upper cage are static; there are no interactive lids. The canonical `CrabCage.blend` components `CreelFrame`, `Lid` and `Bridle` were appended read-only, joined, collapse-decimated at .32, then cleaned and triangulated before cloning: **389 triangles per cage**, plus a 56-triangle rock. The full canonical cage is 1,352 triangles, so five unchanged cages alone would be 6,760 and exceed the brief. This static distance LOD preserves the arched navy frame/coarse net, teal hatch, orange latch and rope. Original CageKit source/FBX and the reference sea props retain their baseline SHA256 values.

| Action | Source frames at 30fps | Duration | Playback | Evidence |
|---|---|---|---|---|
| Bask | 1–121 | 4.0s | Loop: breathing and slow head lift | [Contact strip](renders/Seal/Bask-contact-strip.png) |
| Look | 1–91 | 3.0s | Loop: head turns | [Contact strip](renders/Seal/Look-contact-strip.png) |
| Slide | 1–37 | 1.2s | Once: slide/lower into water | [Contact strip](renders/Seal/Slide-contact-strip.png) |

Slide includes root-bone translation **Unity (0, -.48, +1.85)m**. Do not add duplicate forward runtime translation. Its last deformed surface moves about 1.957m from the first. Each action was compared between source and imported FBX at five frames (15 poses total); maximum surface discrepancy was 1.067 micrometres. Bask/Look return to their starting surface within the 20-micrometre tolerance, and each has measurable intervening movement. Runtime action transitions and the resulting water entry remain integration checks.

## Opened visual evidence

Five studio views are fitted orthographic 720×600. Deck views use a 45° downward angle and a **10m horizontal span** at both 1440×900 and 844×390. Rod views use a **1.7m eye height, 30° downward pitch and 52° vertical FOV** at both sizes. Wide pieces are viewed from farther back while preserving eye height/pitch; each render manifest records the actual distance. The sea backdrop is #1C6E7E. Cycles/OPTIX renders use warm key/cool fill and AgX; they are artist fixtures, not Unity screenshots.

| Asset | Five studio views | Deck | Rod |
|---|---|---|---|
| Seal | [¾](renders/Seal/three-quarter.png), [front](renders/Seal/front.png), [right](renders/Seal/right.png), [back](renders/Seal/back.png), [top](renders/Seal/top.png) | [1440](renders/Seal/deck-1440.png), [844](renders/Seal/deck-844.png) | [1440](renders/Seal/rod-1440.png), [844](renders/Seal/rod-844.png) |
| SealColony | [¾](renders/SealColony/three-quarter.png), [front](renders/SealColony/front.png), [right](renders/SealColony/right.png), [back](renders/SealColony/back.png), [top](renders/SealColony/top.png) | [1440](renders/SealColony/deck-1440.png), [844](renders/SealColony/deck-844.png) | [1440](renders/SealColony/rod-1440.png), [844](renders/SealColony/rod-844.png) |
| SealSwimHead | [¾](renders/SealSwimHead/three-quarter.png), [front](renders/SealSwimHead/front.png), [right](renders/SealSwimHead/right.png), [back](renders/SealSwimHead/back.png), [top](renders/SealSwimHead/top.png) | [1440](renders/SealSwimHead/deck-1440.png), [844](renders/SealSwimHead/deck-844.png) | [1440](renders/SealSwimHead/rod-1440.png), [844](renders/SealSwimHead/rod-844.png) |
| ReefBreak_A | [¾](renders/ReefBreak_A/three-quarter.png), [front](renders/ReefBreak_A/front.png), [right](renders/ReefBreak_A/right.png), [back](renders/ReefBreak_A/back.png), [top](renders/ReefBreak_A/top.png) | [1440](renders/ReefBreak_A/deck-1440.png), [844](renders/ReefBreak_A/deck-844.png) | [1440](renders/ReefBreak_A/rod-1440.png), [844](renders/ReefBreak_A/rod-844.png) |
| ReefBreak_B | [¾](renders/ReefBreak_B/three-quarter.png), [front](renders/ReefBreak_B/front.png), [right](renders/ReefBreak_B/right.png), [back](renders/ReefBreak_B/back.png), [top](renders/ReefBreak_B/top.png) | [1440](renders/ReefBreak_B/deck-1440.png), [844](renders/ReefBreak_B/deck-844.png) | [1440](renders/ReefBreak_B/rod-1440.png), [844](renders/ReefBreak_B/rod-844.png) |
| CrabBuoySet | [¾](renders/CrabBuoySet/three-quarter.png), [front](renders/CrabBuoySet/front.png), [right](renders/CrabBuoySet/right.png), [back](renders/CrabBuoySet/back.png), [top](renders/CrabBuoySet/top.png) | [1440](renders/CrabBuoySet/deck-1440.png), [844](renders/CrabBuoySet/deck-844.png) | [1440](renders/CrabBuoySet/rod-1440.png), [844](renders/CrabBuoySet/rod-844.png) |
| PotStack | [¾](renders/PotStack/three-quarter.png), [front](renders/PotStack/front.png), [right](renders/PotStack/right.png), [back](renders/PotStack/back.png), [top](renders/PotStack/top.png) | [1440](renders/PotStack/deck-1440.png), [844](renders/PotStack/deck-844.png) | [1440](renders/PotStack/rod-1440.png), [844](renders/PotStack/rod-844.png) |

Review: three colony silhouettes remain separate; the swim head/wake is legible above the water; reef variants retain water gaps and restrained ivory/teal crests; five stacked cage silhouettes, hatch colours and the buoy flag survive the required views. Flat reefs intentionally become almost edge-on in the low studio front/back views. No final camera frame crops the asset. The buoy's long rope reaches close to the rod frame's lower edge but remains contained.

## Machine evidence and reproduction

[delivery-receipt.json](delivery-receipt.json) binds the seven pairs, report, seven detailed metrics, seven render manifests, 81 PNGs, authoring/check scripts and read-only helper dependencies to SHA256 values. [Seal metrics](metrics/Seal.json) include all sampled action comparisons; other assets have same-name files under `metrics/`. Geometry proof compares every world vertex, vertex/face/triangle counts, ordered polygon cycle/multiplicity, hierarchy, material names and unit scale with a 20-micrometre match tolerance. Checks also validate clean source meshes, no image dependencies, normalized seal weights, upward foam normals and exported reef UV coordinates.

Authoring and checks live in `Art/Source/Skerries/`: `build.py`, `audit.py`, `render.py`, `run.py`, `contact_strips.py`, `receipts.py`, `finalize.py`, and `baseline.json`; per-model process logs record successful markers. From the project root:

```sh
python3 Art/Source/Skerries/run.py build,audit,render Seal SealColony SealSwimHead ReefBreak_A ReefBreak_B CrabBuoySet PotStack
/home/mo/.venvs/catchline-ui/bin/python Art/Source/Skerries/contact_strips.py
# Individually open every regenerated image before renewing visual acceptance.
python3 Art/Source/Skerries/receipts.py Seal SealColony SealSwimHead ReefBreak_A ReefBreak_B CrabBuoySet PotStack
python3 Art/Source/Skerries/finalize.py
```

The runner uses Windows Blender 5.2.1 from WSL and requires both process success and the expected marker (Blender can otherwise exit zero after a Python exception). Receipt validation verifies recorded evidence integrity; it does not substitute for visual review or Unity runtime acceptance. No git operation, Assets/runtime/scene/save change or watchdog marker was made. All assigned artist steps A–F are complete once the final receipt passes; integration is the external handoff.

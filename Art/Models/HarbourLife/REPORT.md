# HARBOUR-LIFE-2 artist delivery

Dog, Cat and two refit illustrations complete. Source/actual-FBX and isolated rendered acceptance only; Claude owns Unity import, Legacy playback, material conversion, placement and native refit-card acceptance. No Unity, Assets, git, save or watchdog changes.

## Production

| Item | Geometry / scale | Rig and actions |
|---|---|---|
| [Dog.blend](Dog.blend), [Dog.fbx](Dog.fbx) | 728 triangles / 430 vertices; .550 m standing | 14 bones; Trot .6s, Sit 3s, Sniff 2s |
| [Cat.blend](Cat.blend), [Cat.fbx](Cat.fbx) | 604 triangles / 354 vertices; .300 m sitting | 12 bones; Sleep 4s, Look 3s |

Both metre-scale, root empty at feet centre, identity transforms, Unity +Z forward/+Y up (Blender -Y/+Z). One skinned mesh, no external textures, no leaf bones. Every vertex has exactly one bone weight; deliberate rigid facets/parts preserve the supplied crew/Puffin language. Dog has an asymmetrical flopped right ear, white ruff/blaze/socks/tail tip. Cat is ginger with lighter chest, darker back/forehead markings, curled tail and closed sleeping eyes.

Source rest pose is saved with no active action. Exported action names end in the required names (FBX reimport names add CatRig|CatRig| or DogRig|DogRig| prefixes). Set the importer Animation Type to Legacy; use imported clips at 30 fps, looping and in place. Root is the root bone beneath DogRig/CatRig, under empty Dog/Cat. Do not remove rig tracks. Frame ranges include duplicated loop endpoint: Trot 1–19; Sit/Look 1–91; Sniff 1–61; Sleep 1–121. Runtime speed changes remain the lead’s choice.

Palette sRGB: Rubber #28343B, GullWhite #F1F0EA, HairChestnut #50392E; Cat additions Ginger #C58B50, GingerShade #9C6036, WoodHighlight #DFB77A, NoseRose #B97566. Names use M_ prefix. Principled matte, flat normals; use matching game materials for these extra Cat names. See each build/audit JSON for exact material floats and bounds.

## Actual boat cards

[hull3 PNG](../../Source/HarbourLife/ui/v2-item-hull3.png) uses current Assets/Art/Models/Boats/PrepFisherV1.fbx (Tier 4). [hull4 PNG](../../Source/HarbourLife/ui/v2-item-hull4.png) uses current Tier5DeepLines103.fbx (Tier 5), including both DeepLineModule booms. Claude copies these 480×360 RGBA PNGs into Assets/Art/UI. Full-source boat geometry is retained; optional second net/extra rods and RawBuckets hidden, RawIceCoolers visible. Exact visible/hidden mesh names and source SHA256 are in [hull3 render metadata](../../Source/HarbourLife/ui/hull3-render.json) and [hull4 render metadata](../../Source/HarbourLife/ui/hull4-render.json).

[Four-card comparison](../../Source/HarbourLife/ui/comparison.png) places the existing skiff and compact-fisher artwork above the two new cards at original 480×360 size. The brief’s v2-item-hull*.png references do not exist in the existing kit: actual references are v2-item-skiff.png and v2-item-compact-fisher.png. Art/Source/UIv2/generated/items.png and cut_ui_v2.py identify generated-sheet origin; there is no historical Blender camera/light recipe. QUESTION was logged and the recipe was reconstructed: orthographic aft three-quarter direction (-1,1.3,.78), warm key/cool fill, subdued world, navy Freestyle silhouette/creases plus 2px outer ink, restrained 64-colour post, warm wood/ivory/teal. Painterly source bevel/brush finish is approximated; exact camera/light parity cannot be claimed. This limitation is explicit rather than silently changing the reference kit. [Post recipe/size/hash metadata](../../Source/HarbourLife/ui/post.json).

## Verification and evidence

Both actual FBXs reimported and compared against source for vertices, ordered polygon topology/multiplicity, triangles, metre bounds, hierarchy, material colours and evaluated skin deformation. All integer animation frames tested for fixed root and floor contact, five deformed world surfaces per clip compared source/export, all loop endpoints close. Sleep breathing is deliberately subtle (~1.12mm maximum vertex displacement). Dog neck/foot connections and body pitch were corrected after initial renders; Cat crouching Sleep was replaced by side curl. Superseded renders/metrics were regenerated, not treated as final evidence.

[Dog build](metrics/Dog-build.json), [Dog actual-FBX audit](metrics/Dog-audit.json), [Cat build](metrics/Cat-build.json), [Cat actual-FBX audit](metrics/Cat-audit.json), [read-only dependency hashes](metrics/dependencies.json).

All 35 current animal PNGs opened individually (five exact orthographic studios per animal and five sampled frames per action). Action samples share camera within each clip. PNGs have at least 3% frame clearance and bind current blend SHA256. Both new cards and comparison opened individually: 38 final reviewed images. [Visual review/hash manifest](visual-review.json).

### Dog evidence

[three-quarter](renders/Dog/three-quarter.png) · [front](renders/Dog/front.png) · [right](renders/Dog/right.png) · [back](renders/Dog/back.png) · [left](renders/Dog/left.png)

[Trot frame 1](renders/Dog/action-Trot-0.png) · [Trot frame 5](renders/Dog/action-Trot-1.png) · [Trot frame 10](renders/Dog/action-Trot-2.png) · [Trot frame 14](renders/Dog/action-Trot-3.png) · [Trot frame 19](renders/Dog/action-Trot-4.png)

[Sit frame 1](renders/Dog/action-Sit-0.png) · [Sit frame 23](renders/Dog/action-Sit-1.png) · [Sit frame 46](renders/Dog/action-Sit-2.png) · [Sit frame 68](renders/Dog/action-Sit-3.png) · [Sit frame 91](renders/Dog/action-Sit-4.png)

[Sniff frame 1](renders/Dog/action-Sniff-0.png) · [Sniff frame 16](renders/Dog/action-Sniff-1.png) · [Sniff frame 31](renders/Dog/action-Sniff-2.png) · [Sniff frame 46](renders/Dog/action-Sniff-3.png) · [Sniff frame 61](renders/Dog/action-Sniff-4.png)


### Cat evidence

[three-quarter](renders/Cat/three-quarter.png) · [front](renders/Cat/front.png) · [right](renders/Cat/right.png) · [back](renders/Cat/back.png) · [left](renders/Cat/left.png)

[Sleep frame 1](renders/Cat/action-Sleep-0.png) · [Sleep frame 31](renders/Cat/action-Sleep-1.png) · [Sleep frame 61](renders/Cat/action-Sleep-2.png) · [Sleep frame 91](renders/Cat/action-Sleep-3.png) · [Sleep frame 121](renders/Cat/action-Sleep-4.png)

[Look frame 1](renders/Cat/action-Look-0.png) · [Look frame 23](renders/Cat/action-Look-1.png) · [Look frame 46](renders/Cat/action-Look-2.png) · [Look frame 68](renders/Cat/action-Look-3.png) · [Look frame 91](renders/Cat/action-Look-4.png)

## Reproduce and limits

Run `python3 Art/Source/HarbourLife/run.py build,audit,render Dog Cat` in WSL with Windows Blender 5.2 installed. `run.py boats hull3 hull4` rebuilds isolated source/ui boat render scenes; run `/home/mo/.venvs/catchline-ui/bin/python Art/Source/HarbourLife/post.py` for Pillow card post/comparison. Current source scripts and success logs are receipt-bound. `document.py` records already performed image review; it does not automatically inspect or confer new visual acceptance. `finalize.py --preflight` verifies required metrics, source/export/image hashes, clip contracts, references, report links and syntax. Final [delivery receipt](delivery-receipt.json) binds current bytes.

Artist checks complete. Native Unity importer/Legacy action playback, game shader matching, quay placement, animal transitions and refit/HUD rendering remain untested here and belong to Claude’s integration. No production scene/player save was launched or altered. Temporary own pose/visual backups removed only after successful preflight.

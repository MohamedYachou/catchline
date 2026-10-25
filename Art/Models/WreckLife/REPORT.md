# Wreck bank life — artist handoff

WRECK-LIFE-1 · Codex 2 (WSL CLI) · 2026-10-25

Four metre-scale Blender sources and FBX exports are complete. Actual FBX roundtrip geometry/material checks and both sampled gannet actions pass. All **32 final PNGs were individually opened**. Unity import, Legacy configuration, map placement and native water/HUD acceptance remain Claude/Codex 1 integration work.

## Delivery

Dimensions are Unity **X width × Y height × Z length**, in metres, in the rest pose. The gannet has a flight-centre pivot; the other three roots are at water level. All logical roots have unit scale and zero local position.

| Source | Export | Triangles / limit | Dimensions | Contents |
|---|---|---:|---|---|
| [Gannet.blend](Gannet.blend) | [Gannet.fbx](Gannet.fbx) | 460 / 1,500 | 1.000 × .148 × .702 | Five-bone skin; white seabird, black outer wings, buff head, grey dagger bill |
| [DiveSplash.blend](DiveSplash.blend) | [DiveSplash.fbx](DiveSplash.fbx) | 168 / 300 | .523 × .600 × .513 | Static jagged crown, central plume, five droplets |
| [CardinalBuoy.blend](CardinalBuoy.blend) | [CardinalBuoy.fbx](CardinalBuoy.fbx) | 318 / 700 | .620 × 2.400 × .620 | Yellow upper body, black lower float, continuous black mast, two upward cones |
| [HerringBoil.blend](HerringBoil.blend) | [HerringBoil.fbx](HerringBoil.fbx) | 260 / 400 | 2.999 × .034 × 1.680 | Three broken elliptical ripple bands and 20 silver breach flecks |

Total: **1,206 triangles**. Only the four named FBXs are game imports. Their matching blends are editable sources. [WreckLife-assembly-review.blend](WreckLife-assembly-review.blend) is an isolated, posed review scene containing cameras, lights and water; keep it out of game imports. Asset files contain no review geometry, textures or image dependencies. Existing Seagull is reused externally for wreck gulls.

## Integration contract

Source axes are Blender X right, -Y forward, Z up; intended game axes are Unity X right, +Z forward, Y up. FBX export is -Z forward/Y up, metre units, no leaf bones. Static assets bake axis conversion; the animated gannet preserves its rig hierarchy. Source/actual-FBX roundtrip checks preserve world surfaces and hierarchy. Check normal project import orientation and scale in Unity.

**Gannet:** hierarchy `Gannet / GannetRig / GannetSkin`; bones `Root`, `Body`, `Head`, `Wing.L`, `Wing.R`. The root is the body-centre flight pivot, with rest skin extending .067m below and .081m above it. Keep the object's forward orientation at Unity +Z. Configure the rig/clips as **Legacy** on import. Match takes by their final name segment: Blender FBX reimport reports `GannetRig|GannetRig|Glide` and `GannetRig|GannetRig|Dive`; importer prefixes may vary.

| Clip | Source frames, 30fps | Duration | Playback and movement |
|---|---|---|---|
| Glide | 1–91 | 3.0s | Loop. Wings set, gentle ±6° bank and ±2° pitch, small yaw. Runtime owns circular travel and heading. |
| Dive | 1–49 | 1.6s | Once, no loop. Brief anticipation, wings sweep back 79°, body pitches 82° nose-down, final arrow pose holds. Runtime owns descent and water entry. |

Both clips keep the object root and Root bone fixed. All bone locations remain zero throughout; articulation is rotational. Glide returns to its starting surface, with .0613m maximum intervening vertex motion. Dive's last surface moves .7435m from its first through rotation/folding, with no baked travel. Start the runtime descent as the dive pose develops; trigger the separately placed splash at water entry, hide/reset the bird after entry, and restart Glide when respawning. Do not expect the clip to move the bird to the sea. Runtime transitions remain untested here.

**DiveSplash:** hierarchy `DiveSplash / DiveSplashMesh`. Root at the centre of the water entry, local minimum Y=0 and maximum Y=.600. Scale and show/hide the whole mesh. It is opaque geometry with an open crown and disconnected droplets, without exported animation or particles. Use a two-sided shared foam material for the crown if the runtime shader culls backs. Fading requires runtime material support; visibility/scale needs none.

**CardinalBuoy:** hierarchy `CardinalBuoy / CardinalBuoyMesh`. Place root at mean water Y; black float extends **.160m below** the pivot, with the upper cone at **+2.240m**, making **2.400m total**. Bob/tilt the entire root. Both black cones point up. The paint order follows the brief's explicit **yellow over black** instruction. The included mast connects through both topmarks; no runtime rig or lights are supplied.

**HerringBoil:** hierarchy `HerringBoil / HerringBoilMesh`. Root at mean water Y; ripple faces are local Y=.008, flecks reach .042. Allow a small additional runtime water offset if sea displacement requires it. Pulse root scale/visibility like SurfPulse. This is an opaque fragmented overlay, with open gaps showing real water, no exported clips or shader. Use two-sided foam/silver materials for its thin surfaces; disable cast shadows on this overlay during integration if the water material makes them intrusive. Front/right/back studio views intentionally show its near-flat profile.

## Named materials

Remap by these exact shared names. There are no new texture files. Colours below are authored sRGB; stored shader values and audit JSON are linear RGBA. All are opaque, nonmetallic, roughness .75 in the source.

| Material | sRGB | Used by |
|---|---|---|
| M_GullWhite | #F1F0EA | Gannet, DiveSplash, HerringBoil |
| M_GullGrey | #9AA6AD | Gannet |
| M_Rubber | #28343B | Gannet outer primaries/eyes/bill line |
| M_FishSilver | #BAC9C6 | HerringBoil |
| M_RailIvory | #F3F0DC | DiveSplash droplets, HerringBoil |
| M_GannetBuff | #E8CF8F | Gannet head; new name from brief |
| M_CardinalYellow | #F2C14E | Buoy upper body; new name from brief |
| M_CardinalBlack | #23262B | Buoy float/mast/cones; new name from brief |

## Individually opened evidence

Five true orthographic studio views per item are 720×600. Ten gannet samples are 640×480, using one fixed camera across both actions. Final studio fitting centres projected bounds, explicitly uses horizontal sensor fit and checks every evaluated asset vertex for a 3% image margin before render. The initial cropped gannet evidence was replaced; hashes in [visual-review.json](visual-review.json) refer only to the final inspected files.

| Item | Five studio views |
|---|---|
| Gannet | [¾](renders/Gannet/three-quarter.png), [front](renders/Gannet/front.png), [right](renders/Gannet/right.png), [back](renders/Gannet/back.png), [top](renders/Gannet/top.png) |
| DiveSplash | [¾](renders/DiveSplash/three-quarter.png), [front](renders/DiveSplash/front.png), [right](renders/DiveSplash/right.png), [back](renders/DiveSplash/back.png), [top](renders/DiveSplash/top.png) |
| CardinalBuoy | [¾](renders/CardinalBuoy/three-quarter.png), [front](renders/CardinalBuoy/front.png), [right](renders/CardinalBuoy/right.png), [back](renders/CardinalBuoy/back.png), [top](renders/CardinalBuoy/top.png) |
| HerringBoil | [¾](renders/HerringBoil/three-quarter.png), [front](renders/HerringBoil/front.png), [right](renders/HerringBoil/right.png), [back](renders/HerringBoil/back.png), [top](renders/HerringBoil/top.png) |

| Clip | Five samples, in time order |
|---|---|
| Glide | [0.000s](renders/Gannet/action-Glide-0.png), [.733s](renders/Gannet/action-Glide-1.png), [1.500s](renders/Gannet/action-Glide-2.png), [2.233s](renders/Gannet/action-Glide-3.png), [3.000s](renders/Gannet/action-Glide-4.png) |
| Dive | [0.000s](renders/Gannet/action-Dive-0.png), [.400s](renders/Gannet/action-Dive-1.png), [.800s](renders/Gannet/action-Dive-2.png), [1.200s](renders/Gannet/action-Dive-3.png), [1.600s](renders/Gannet/action-Dive-4.png) |

Assembly: [1440×900](renders/Assembly/deck-1440.png) and [844×390](renders/Assembly/deck-844.png). Both use the accepted Skerries fixture direction (.574, -.819, 1), **45° down and exactly 10.24m horizontal orthographic span**. Target is Blender (0,0,.9). The buoy, shoal, Glide-frame24 bird, Dive-frame49 bird and splash are all contained. Phone buoy topmark has a narrow ~7px upper margin. Gliding/folded silhouettes and broken water remain distinguishable. The splash is staged beneath the descending bird to show both assets; this still does not demonstrate entry timing.

The water plane is #1C6E7E. Cycles/OPTIX, AgX and warm key/cool fill are artist lighting. No actual map terrain, Unity water, import, Legacy playback, IMGUI HUD or native capture is part of this evidence. [Assembly manifest](renders/Assembly.json) records placements and actual projected bounds for both sizes. The review blend preserves the frozen poses.

## Checks and reproduction

[Gannet audit](metrics/Gannet-audit.json), [DiveSplash audit](metrics/DiveSplash-audit.json), [CardinalBuoy audit](metrics/CardinalBuoy-audit.json), [HerringBoil audit](metrics/HerringBoil-audit.json) contain actual FBX roundtrip evidence; matching `-build.json` files contain authoring contracts and source/export hashes. Checks cover triangle limits, nondegenerate geometry, finite/used vertices, zero object positions/unit scales, expected pivots/dimensions, hierarchy, normalized skin weights, allowed material names/colours and no images. Every world vertex, face cycle/multiplicity and triangle count is compared with a 20-micrometre tolerance. Maximum observed source/export discrepancy, including all ten deformed samples, is **.170 micrometres**. Both actions are also checked for fixed root at every frame, expected duration, loop closure or arrow/nose-down finish.

[Dependency baseline](metrics/dependencies.json) binds five read-only helper/reference files; all remain unchanged. [Visual review](visual-review.json) binds the 32 individually opened image hashes and dimensions. [Delivery receipt](delivery-receipt.json) binds the current source/export/evidence/report/scripts/logs and records final verification. Its integrity check does not substitute for a visual review.

Authoring, independent checks, rendering and finalization scripts are under `Art/Source/WreckLife/`. From the project root in WSL, with Windows Blender 5.2.1 installed:

```sh
python3 Art/Source/WreckLife/run.py build,audit Gannet DiveSplash CardinalBuoy HerringBoil
python3 Art/Source/WreckLife/run.py render Gannet DiveSplash CardinalBuoy HerringBoil Assembly
# Open every regenerated PNG individually, then renew visual-review.json from actual review.
python3 Art/Source/WreckLife/finalize.py
```

The runner requires process exit zero, the expected explicit success marker and no Python traceback. `finalize.py` rejects stale pair/image hashes, missing views/samples, changed dependencies and broken report links. It does not regenerate visual approval. Temporary revision backups are removed after successful verification. No git operation/commit, Unity launch, Assets/runtime/scene/save change, watchdog marker or subagent work was performed. Artist steps A–E complete; integration and native acceptance are the external handoff.

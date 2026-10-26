# MAP11 sand fix and life continuation

MAP11-FIX-AND-LIFE-1, Codex 1 (Windows app). Claude reviews and commits; no commit by Codex 1. This directory supersedes the sand-read finding in the preserved [baseline](../README.md).

The surrounding connected bed is raised to approximately 1.15 m below water, retaining original-depth anchor pockets. Four kelp patches are localized for slow root sway. Navigation bytes, terrain obstacles and accepted post placement remain unchanged. Current export: 71,766 triangles, 299 meshes. The [source sand audit](../../../../Art/Models/Maps/GullKelpForest/sand-fix-audit.json) records the verified B snapshot. Native review then required a material-only correction: warm sand on 182 faces in irregular clearings, teal on the other 5,926 bed faces. An [independent comparison](sand-material-audit.json) proves exact equality of every vertex, face and transform of all 299 meshes, all empty transforms and navigation bytes against B. The independent source/actual-FBX audit was refreshed and passes 62 checks. Claude accepted the narrow-post broad-circle exception at 08:45 on 2026-10-26. All four real post collision outlines remain in routes.

Only MAP11's active water material receives absorption (.86,.84,.74) and green-teal 3A8F86 scattering. Shared production water shader and other maps are unchanged. The first native optics pass (.91,.94,.89) made the seabed look dry and beige; [first-optics-pass](first-optics-pass/) retains that failed pass and its launch receipt. [Green](green-optics-pass/) and [sage](sage-optics-pass/) trials retain the intermediate over-filtered sand reads. Localized sand materials resolve the broad uniform sheet without another geometry or navigation change.

## Before and after

Left is the original rejected deep-blue sand read; right is the final native frame. Both halves retain their original pixels, with a comparison header added. Individual originals remain beside each comparison. All four comparison stages use the normal player camera, HUD and production water.

| View | 1440 × 900 originals | 844 × 390 originals |
|---|---|---|
| Sand clearing | [Before](../sand-clearing-1440.png) · [After](sand-clearing-1440.png) · [Side by side](compare-sand-clearing-1440.png) | [Before](../sand-clearing-844.png) · [After](sand-clearing-844.png) · [Side by side](compare-sand-clearing-844.png) |
| Kelp edge | [Before](../kelp-edge-1440.png) · [After](kelp-edge-1440.png) · [Side by side](compare-kelp-edge-1440.png) | [Before](../kelp-edge-844.png) · [After](kelp-edge-844.png) · [Side by side](compare-kelp-edge-844.png) |
| Post line | [Before](../post-line-1440.png) · [After](post-line-1440.png) · [Side by side](compare-post-line-1440.png) | [Before](../post-line-844.png) · [After](post-line-844.png) · [Side by side](compare-post-line-844.png) |
| Sailing out | [Before](../sail-out-1440.png) · [After](sail-out-1440.png) · [Side by side](compare-sail-out-1440.png) | [Before](../sail-out-844.png) · [After](sail-out-844.png) · [Side by side](compare-sail-out-844.png) |

Chart: [1440 × 900](chart-1440.png), [844 × 390](chart-844.png). Life, including the explicitly labelled supplementary raft-camera composition: [Kelp life evidence](../../kelp-life-1/README.md).

## Checks and provenance

- Resumed terrain suite passed 60 directed MAP11 hull routes, all 33 lanes, five harbour hull roundtrips, all three MAP11 out/anchor/bait-cast/home trips, seven anchors, pools and 36,000-coin/Hull >= 3 chart gates. [Raw route receipt](routes-trips.json), [log](check-routes-trips.log), [wrapper](routes-trips-wrapper.log). That immutable snapshot predates the optional otter swap and accurately records the fallback. Navigation and terrain geometry remain identical afterward; the material-only audit proves that equality.
- Final otter/optics fixture and native scratch build passed: four localized 4–7-second sways below two degrees, continuous periodic motion, four imported raft meshes, supported two-sided materials, four post gulls and one map-local optics owner. [Final build log](check-final-build.log), [wrapper](final-build-wrapper.log), [build stamp](build.txt). Unity and wrapper exit 0.
- Full integration regression passed: 286 ability assertions, 217 tutorial assertions with zero unresolved targets, M2 and bite/cage checks. [Log](check-regression.log), [wrapper](regression-wrapper.log). Unity and wrapper exit 0. This preceded the final optical-constant, evidence-camera and delivered raft-ribbon changes; subsequent final build/life checks cover those changes.
- Guarded Windows SessionOnly native launch purchases the chart, sails normally, visits all three grounds, captures both sizes and returns home. Gameplay stays frozen while actual Unity time drives the four kelp components for 1.25 seconds; all four measured rotations change. [Native log](native.log), [launch hashes](native-run.json), [exit](native-exit.json), [completed frames](capture-complete.txt).
- [Evidence verification](evidence-verification.json) checks native dimensions, exact hashes, eight before/after pairs, life copies, live-motion markers, exit code and source provenance. Reproduce with `uv run --with pillow python Art/Source/Art108/map11_fix_evidence.py` from the project root. Launch via `Art/Source/Art108/map11_fix_native.ps1` only after building through `docs/tools/check.ps1`.

## Individual native review

Codex 1 opened all 14 final native frames and all eight comparison pairs individually; [hashed review record](visual-review.json). Sand clearing, Kelp edge and Post line now show warm sand clearings against a teal surrounding bed at both sizes, with rooted kelp and a deeper anchor pocket. The clearing boundary remains visibly faceted. Sailing retains open-water waves; chart price and labels remain readable. The live-motion pair shows subtle pose change, backed by measured movement of all four clusters.

The final imported raft includes Codex 2's delivered KELP-RIBBON-FIX: fifteen slender dark-olive ribbons. Source and import hashes are identical, and the runtime binding preserves its two olive colours. Desktop supplementary evidence shows adults and pup. At phone size the raft is small and partly covered by action labels; at the ordinary Kelp edge camera it is largely behind the left HUD. This is a recorded visibility limitation, not a claim of full ordinary-camera raft acceptance.

Final launch provenance: 158/158 runtime/import inputs matched main at launch. The exact mismatches and both source hashes, if any, are in evidence-verification.json; all MAP11-owned files matched. Concurrent lead edits are preserved, not silently folded into capture provenance. Static frames do not establish player acceptance of animation timing, installed-player behavior, listening or physical touch. No player save, main-project batchmode, shared UI edits or git operation was used. MAP12 is unassigned.

Temporary backup cleanup was rejected by automatic approval review; both own scratch backup folders remain, as recorded in [cleanup status](backup-cleanup.json). No deletion workaround was attempted. The small uniform-sand-pass directory is an explicitly incomplete historical receipt copy, not final evidence.

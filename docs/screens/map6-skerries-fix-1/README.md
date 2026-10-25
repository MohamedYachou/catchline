# MAP6-SKERRIES-FIX-1 — addendum evidence

Codex 1 (Windows app), 2026-10-25. Terrain A–C and anchor placement D are implemented/imported. All11art images and10current native frames were individually opened. **Overall status PARTIAL:** seals, breaking-surf life and the crab-buoy set are absent; Claude's navigable runtime integration and visual acceptance remain pending. Six original full-zone art assertions remain failed and disclosed. Full fresh scratch safety checks completed successfully with Unity exit0.

[Map report](../../../Art/Models/Maps/GullSkerries/REPORT.md), [art review](../../../Art/Models/Maps/GullSkerries/SeaV2-visual-review.json), [native review with per-image notes](native-visual-review.json), [build log](check-map6-addendum-build.log), [full check log](check-map6-addendum-final.log), [check receipt](map6-checks.json), [final hash receipt](verification-receipt.json), [native run hashes](native-run.json), [native log](native/native.log), [completion record](native/capture-complete.txt).

## Current native frames

| Stage | Desktop1440×900 | Landscape844×390 |
|---|---|---|
| Chart overview | [Open](native/chart-1440.png) | [Open](native/chart-844.png) |
| Normal sailing out | [Open](native/sail-out-1440.png) | [Open](native/sail-out-844.png) |
| Seal rocks | [Open](native/seal-rocks-1440.png) | [Open](native/seal-rocks-844.png) |
| Kelp gully | [Open](native/kelp-gully-1440.png) | [Open](native/kelp-gully-844.png) |
| Outer reef | [Open](native/outer-reef-1440.png) | [Open](native/outer-reef-844.png) |

The SessionOnly TEST fixture purchases the unowned700-coin chart through the normal UI, follows harbour/chart/sea departure, anchors at all3grounds, relocates and returns home. The native log records all10frames and completion. The initial1280×720 window forces each requested resolution before capture. No player-save reads/writes or installed-player replacement.

A: low flat stepped colony slabs occupy the lower corners, with visible water gaps to the hull. HUD/bottom controls cover parts of both rocks. **Neither Seal frame contains seals.** Colony empties are on the slab tops in source/actualFBX/Unity; correct anchors alone do not spawn life.

B: long parallel gully ridges enter opposite corners with kelp and open hull clearance. Both are heavily cropped; on844×390 the upper-left ridge is only a thin sliver. This is limited framing evidence, not an unobstructed two-wall overview. Both ridges lie outside the unchanged10.24m rowboat art fixture; wide/top art views show their lengths.

C: outer half-tide rocks and narrow waterline contact foam remain, with no sharp fin foam or baked ReefBreak meshes. Foreground rocks are partly cropped/covered by bottom controls. **Breaking-surf life is absent.**

D: **seals and the crab-buoy life set are absent.** `Sea/SeaScenery.cs:BuildNavigableSea` instantiates the navigable map without `DressSkerries`; only the legacy scenery path calls it. Claude owns that runtime change. Questions and exact next action are in canonical comms.md. The yellow sailing marker is navigation scenery, not evidence of the crab set. No runtime code was changed by this terrain revision.

## Checks and limits

- Current source/FBX:109PASS;29232triangles,14closed/sliced terrain obstacles,40outer buoys,ninevalid empties;17.643micrometre maximum roundtrip vertex error.
- Retained art audit:83/89PASS. Six complete-ground-circle island/shallow exclusions conflict with mandated close landmarks; assertions remain intact. All six routes at2m and4m clearance pass. No ground IDs/positions/radii moved.
- Fresh scratch native build: Unity exit0 and MAP6 TEST BUILD PASSED. Full fresh safety check: **PASS / Unity exit0**;360directed routes across6maps/5hulls,18lanes,5baselineharbourhulls and3new-ground/home trips. Nine imported anchors,700-coin chart purchase and ground-specific pools all pass.
- Native capture: chart purchase, normal departure,3anchors/home and10frames complete; all10individually opened. No exceptions in native log. This does not establish touch, installed-player, interactive fishing or life-animation acceptance.
- Lead visual review remains required, including cropped terrain/HUD coverage and the unresolved art-fixture gully framing. Route timing advisories use physical distance and are separate from collision/border safety.

[Iteration1](iteration-1-sharp-foam/) and older placement/check/build files in this folder are historical evidence of rejected/superseded geometry. Current acceptance evidence is the addendum build log, current native directory and final check. `verification-receipt.json` binds the current files, reviewed frames, imported bytes and native build, with explicit partial-acceptance limits. No git operation, main-project batchmode, save access, watchdog file or reopened Fish/Deck/Harbour work.



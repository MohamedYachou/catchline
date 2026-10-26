# MAP10 — Seal cliffs

Owned terrain, import and native test delivery complete. Lead chart handoff and acceptance are pending.

The new 340 × 260 m map has a broken north cliff line, an open sea arch, a pebble cove with three surfaced haul-out stones, and a detached sea stack. Six low faceted rocks frame the three fishing anchors. The source contains no buildings, animals, spray or baked foam. Two unreachable cliff silhouettes continue the coast beyond the boundary.

The source is `GullSealCliffsSeaV2.blend`; the runtime export is `GullSealCliffsSeaV2.fbx` (19,860 triangles). `navigation.json` is sliced from closed terrain at local waterline 0 and shallow level −1 m, with world placement (0, −0.32, 0), identity rotation and scale. Independent source/reimport audit: 100 checks, maximum export deviation below 0.019 mm. Art navigation audit: 97 checks, including all harbour/ground routes at 2 m and 4 m clearance.

The accepted MAP8 exception applies only to the six named `Terrain_CornerRock_*` meshes inside the broad fishing circles. Their genuine waterline obstacles remain in navigation; every actual anchor has over 4 m clearance. The six inherited full-circle failures are preserved in `SeaV2-audit-raw.json`. No broad coastline or route clearance failure is waived. The concave north shoreline uses outward offsets for its shallow skirt, so land stays inside its shelf.

Life empties (world coordinates):

| Empty | X | Y | Z | Placement |
|---|---:|---:|---:|---|
| SealHaulout_1 | −5 | 0.58 | 68 | Flat stone surface |
| SealHaulout_2 | 2 | 0.78 | 68 | Flat stone surface |
| SealHaulout_3 | 9 | 0.68 | 68 | Flat stone surface |
| CliffGulls_1 | −37 | 5.68 | 76 | Cliff ledge surface |
| CliffGulls_2 | 67 | 6.88 | 77 | Cliff ledge surface |
| ArchSpray_1 | −74 | −0.32 | 52 | Open water just in front of arch mouth |

Independent downward rays confirm all five solid anchors on the highest visible surface within 0.015 m, and the spray anchor free of overhead terrain. Orange cylinders in the six anchor review images are review aids only.

Requested existing-species substitutions: wrasse → RedMullet (coastal bottom fish), lobster → Crab, grey mullet → RedMullet, coalfish → Pollock, ling → Conger, halibut → Turbot. Ground weights otherwise follow the brief exactly. Requested blurb is retained, including its wrasse wording. Spot data: 36 s rowing, 1.5 bite wait, 2,600 coins, index 9 after Whale shelf.

Blender review water is a preview material. Production blue water remains unchanged. Native stills, route checks, animation and player acceptance are separate evidence. Claude owns the chart point/glyph and runtime seals/gulls/spray; the chart dependency is logged in `comms.md`.

## Runtime evidence and remaining handoff

Isolated Unity checks passed with actual Unity exit 0: ten maps, 600 directed hull routes, 30 sea lanes, five normal harbour hull trips, exact chart purchase/pools/anchors, and three new ground departure/bait-cast/home trips. The SessionOnly standalone test build succeeded. Its native capture run bought the chart through the interface, departed, visited all three anchors, returned home and exited 0. All ten 1440x900 / 844x390 frames were individually opened; dimensions and hashes are bound in docs/screens/map10-seal-cliffs-1/review.json, alongside source/asset/executable/assembly/scene hashes and actual exit receipts. No main-to-build source drift at launch (145 game sources).

Native corner rocks are faceted grey, visible around the boat with no pink materials; fishing water and primary controls remain clear. The wide coast and life-surface placements have separate authoring evidence. The chart frames explicitly FAIL the remaining lead-owned point/glyph handoff: spot 9 falls back to Harbour mouth's (.447,.445) pin, uses the generic gear glyph, and overlaps its labels at both sizes. QUESTION logged with image paths. No chart code was edited. Only this affected chart verification needs repeating after Claude's handoff; already verified terrain/routes need no restart.

No Git/commit, installed build, player save or physical device/touch acceptance. Temporary MAP10 backups remain in Catchline-sim/Backups until the pending handoff is resolved; no source/art reservations remain held. Runtime seals/gulls/spray remain Claude's scope.

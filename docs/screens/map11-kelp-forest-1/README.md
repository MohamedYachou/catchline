# MAP11 Kelp forest evidence

Current continuation: [MAP11 sand fix and native comparisons](fix/README.md), [Kelp forest life](../kelp-life-1/README.md). The frames and receipts below are the preserved pre-fix baseline. Claude accepted the narrow-post exception at 08:45 on 2026-10-26; its pending-review wording below records the earlier delivery, not the current decision. Current terrain is 71,766 triangles / 299 meshes; the additional four meshes localize the swaying patches. Current life uses the delivered otter raft, four post gulls and four gently swaying kelp clusters.

Codex 1 technical delivery is complete. Claude review and acceptance remain separate. Seal cliffs life is recorded in [its evidence](../cliffs-life-1/README.md).

The 320 by 260 m bay contains rooted ribbon kelp, sandy clearings, low weed-covered rocks and an old mooring-post line. The authored shallows palette is green-teal 3A8F86. The source/export contains 66,282 triangles and 295 meshes. Independent source reopening, terrain slicing and FBX reimport pass 62 checks with vertex deviation below 0.018 mm. All eighteen final authoring images were opened individually, including seven life-anchor reviews.

The scoped navigation audit passes 65 checks. Its raw report retains two failures where four narrow foreground posts intersect the post-line ground's broad 13 m circle. Only those four posts are excluded from that broad-circle test; their collision outlines remain in every real route check. Actual obstacle clearance from the anchor exceeds 4 m. This exception awaits Claude review. No coastline or route failure is waived.

The three base ground pools retain the requested weights using existing species: RedMullet substitutes for wrasse and gurnard, Crab for lobster, Herring for garfish, and Turbot for john dory. Claude's COASTS-2 runtime shaping adds Outer coast extras from Coasts.cs. RowSeconds is 28, BiteWait 1.4; map/ground indices remain append-only. COASTS-2 supersedes the brief's old price: 36,000 coins, Hull >= 3 (Prep fisher, tier 4). Claude's current chart point is (.216,.278) on the Outer coast page, glyph15; this supersedes the earlier (.55,.12) handoff.

Verified checks:

- Original full isolated suite: eleven maps, 660 directed routes across all five hulls, 33 lanes, all five harbour hull roundtrips, three new-ground out/anchor/bait/cast/home trips, pools/assets/anchors and build passed. Original pre-economy receipts are preserved in [pre-coasts-2](pre-coasts-2/).
- The native launch guard caught the intervening COASTS-2 source change before launching a player. Updated fixtures then rechecked all 60 MAP11 routes, all 33 lanes, five harbour hull trips and three new-ground trips. Low hull gate, 35,999 rejection and exact 36,000 purchase passed. The other 600 routes retain the unchanged baseline proof. [Baseline receipt](checks.json), [current receipt](final-checks.json), [build log](check-build.log).
- Full integration regression passed: 286 ability assertions, 217 tutorial assertions, M2 and bite/cage coverage. [Regression log](regression.log). Build, native player and regression wrappers exited0; both Unity checks exited0. [Process receipts](process-exits.json).
- SessionOnly native player captured ten frames and returned home, actual exit0. All 149 game sources matched main at launch; terrain imports and both chart resource hashes matched the built scratch. [Launch provenance](native-run.json), [native log](native.log), [exit](native-exit.json).
- Saved receipt/hash verification passes, including all ten native images and eighteen art views. No post-capture source drift at verification time. [Verification](verification.json), [reproduction](verify.py), [review](review.json). This is receipt verification, not another Unity run.

Every image below was opened individually. Chart cards and 36,000 price are readable and separate on both sizes. Kelp frames the boat clearly; posts are visible, with the left pair partly under the existing HUD. The sandy seabed is subdued under production water and needs lead visual judgement. Boat clearance and controls remain visible; no missing-material pink appeared.

| Native view | Desktop 1440x900 | Landscape 844x390 |
|---|---|---|
| Outer chart | [Open](chart-1440.png) | [Open](chart-844.png) |
| Sailing out | [Open](sail-out-1440.png) | [Open](sail-out-844.png) |
| Kelp edge | [Open](kelp-edge-1440.png) | [Open](kelp-edge-844.png) |
| Sand clearing | [Open](sand-clearing-1440.png) | [Open](sand-clearing-844.png) |
| Post line | [Open](post-line-1440.png) | [Open](post-line-844.png) |

[shared-hunks.patch](shared-hunks.patch) contains only four shared-source changes; no full source snapshots were copied into screenshots. [meta-audit.json](meta-audit.json) records 1,183 unique GUIDs and no missing owned metadata at audit time. [import-audit.json](import-audit.json) records byte-identical FBX/nav/grounds imports. Source, art reviews and raw/scoped audits are in [the authoring report](../../../Art/Models/Maps/GullKelpForest/REPORT.md).

Kelp/otter/gull animation is a later life hook; this brief supplies its anchors. Static native evidence does not establish animation timing, listening, installed-player or physical-device/touch acceptance. No player save, main-project batchmode or git mutations were used. No commit by Codex1. Claude retains the broad-circle exception and sand-read review decisions; MAP12 is unassigned.

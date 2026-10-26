# Kelp forest life

MAP11-FIX-AND-LIFE-1, Codex 1 (Windows app), for Claude review. VoyageKelpLife.cs is reached through the single DressCliffs fallback dispatch; no shared UI change.

Four authored patches nearest KelpSway_1..4 sway at 4/5/6/7-second periods with rotation below two degrees. Rest transforms are cached; Update performs quaternion/value math without per-frame allocations. PostGulls_1..2 use the existing gull life, four gulls total. At OtterRaft_1 the delivered Codex 2 OtterRaft.fbx provides two adults and one pup on a static kelp mat with gentle Floater bob. The fallback is retained but unused. Individual animated SeaOtter clips were not integrated. Thin mat leaves have owned two-sided URP materials, disposed with the raft.

| Native view | 1440 × 900 | 844 × 390 |
|---|---|---|
| Kelp edge, player camera | [Open](kelp-edge-1440.png) | [Open](kelp-edge-844.png) |
| Kelp after live movement, player camera | [Open](life-kelp-motion-1440.png) | [Open](life-kelp-motion-844.png) |
| Post gulls, player camera | [Open](post-line-1440.png) | [Open](post-line-844.png) |
| Supplement: otter raft camera composition | [Open](life-otter-1440.png) | [Open](life-otter-844.png) |

The raft is largely behind the left HUD at the ordinary Kelp edge camera. Only the life-otter pair uses an evidence camera aimed at the unchanged raft anchor; deck and HUD remain present. It is supplementary inspection evidence, not a claim that the raft is fully visible through the normal player camera. The other six life frames and every sand comparison retain the player camera. These files are byte-identical copies of the corresponding [MAP11 native originals](../map11-kelp-forest-1/fix/README.md).

Final LifeAndBuild checks cover all seven anchor transforms, four bounded/periodic sways, four raft meshes with supported materials and four post gulls. The native log also measures actual rotation changes of all four clusters over 1.25 real seconds while gameplay is frozen. Full integration regression passed 286 ability and 217 tutorial assertions plus M2/bite/cage coverage. [Logs, exit codes and launch hashes](../map11-kelp-forest-1/fix/README.md#checks-and-provenance).

All eight life images were individually opened. Rooted kelp and post gulls are visible at both sizes. The final raft uses the delivered narrow dark-olive ribbon revision. Adults and pup read on desktop; the phone supplementary raft is small and partly action-label occluded. The ordinary-camera left-HUD limitation remains. See the [hashed individual review](../map11-kelp-forest-1/fix/visual-review.json). Native Windows technical evidence does not establish installed-player, physical touch, listening or player approval of timing. No commit by Codex 1; Claude reviews and commits.

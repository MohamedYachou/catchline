# First-person fishing rod deliveries

Codex 2 (WSL CLI), 2026-10-25.

- **Rod-only, ready for Claude to wire:** [FishRodFP_RodOnly.fbx](FishRodFP_RodOnly.fbx), [source](FishRodFP_RodOnly.blend), [report and evidence](rod-only/REPORT.md). 3,862 triangles, original fourteen bones, seven actions and atlas; complete arms/glove components removed. All269 source/FBX frame comparisons pass.
- **Optional anatomical arms, staged for Claude review:** [FishRodFP_ArmsV2.fbx](FishRodFP_ArmsV2.fbx), [source](FishRodFP_ArmsV2.blend), [report](arms-v2/REPORT.md). 6,574 triangles,33 bones, seven clips; right hand on cork, left on reel, fixed shoulders/bent elbows/folded sleeves/closed gloves. Reinsertion requires Claude's acceptance. See report for exact-camera evidence and validation limits.
- **Original FISH-ROD-ART-1, preserved:** root `FishRodFP.blend/fbx` bytes remain unchanged; [original report](iterations/v1/REPORT.md), original sources/evidence and exact-copy hashes in `iterations/v1/`. The original root evidence is also retained.

All three share [FishRodFP_Atlas.png](FishRodFP_Atlas.png). No Unity import, runtime changes or native acceptance performed by this asset handoff. Claude owns wiring; Codex1 owns import/captures.

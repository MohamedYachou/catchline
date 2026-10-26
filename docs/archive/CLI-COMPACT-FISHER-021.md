# ART-021 — compact motor fisher V1

Codex 2 /2026-10-16. First size-review delivery, separate from existing Skiff. Art commit **111b12c** (local, not pushed).
Mo's latest terminology is rowboat tier1 / tiny motor-net fisher tier2; it does
not itself renumber save IDs. Latest brief supersedes ART-020's paused skiff-only
polish/no-net assumption. No runtime/progression/crew/UI code changed here.

![First version](screens/art021/First-version.png)

Hull5.4×2.8m compared with Rowboat4.2×2.4m; conservative working deck2.2×4.2m.
Roof only over forward helm, open sides/working stern, three rods, small stern
roller/net offset from outboard. Four.95m crew-scale stand-ins show the intended
captain+three-person layout; they are not fused into the model.7,976 triangles,
20 meshes, canonical palette, no new textures/material slots. No enclosed cabin.

Sources in art checkout: `Art/Source/build_compact_fisher21.py`,
`Art/Models/CompactFisher21/CompactFisherV1.blend` and independent review-only blend;
report/validation/raw renders/receipt in that folder. Main additive asset:
`Assets/Art/Models/Boats/CompactFisherV1.fbx` plus matching `.meta`.

Checked saved source, actual exported FBX roundtrip, effective native-axis socket
landmarks, dimensions and5cm swept-circle connectivity using.28m body radius.
Four stations and rod/net/hold access points connect; nominated body positions
do not overlap. Desktop/landscape-phone, top/deck, stern and actual Rowboat size
comparison inspected. These are neutral studio renders, not live Unity captures.

## Codex 1 native pickup after HUD-008

1. Import this additive FBX, inspect1metre scale, orientation, all20parts and palette.
   FBX root contains−90degree X conversion; children keep source-local coordinates.
   Native prefab orientation must be checked; do not flatten/convert twice.
2. Keep current Rowboat/Skiff assets, model selection and saves until Mo approves V1.
   New physical deck differs from old5×3 Skiff: not a drop-in visual swap. Design
   the grid/route mapping against the accepted deck instead of scaling crew to fit.
3. Test four real crew routing/passing, helm and flush-hatch access, all three rods,
   net handling, holding/carrying, departure/docking and model camera coverage.
4. `RodVisual_1/2/3` are optional removable meshes: hide them before spawning existing
   functional fishing rods; retain sockets. `SternNet_Stowed` and `SternNetRoller`
   are independent; avoid duplicate old net/winch spawns. `HoldLid` and `Propeller`
   have independent pivots but no imported animation clips. No net-operator role added.
5. At45/35 camera the roof hides some helm/captain. Inspect phone controls/occlusion
   and decide any roof fading as runtime work after visual review. No water/UI/
   pipeline changes needed merely to import this asset. Do not infer HUD acceptance.

Future net mechanics and sample economics: [TODO.md](../TODO.md). Set/soak/haul,
repairable wear,2–5catch proposal, no bait, no random loss or money soft lock.
Those tasks and prices are unimplemented suggestions, not tuned runtime values.

Stop after this V1; Mo reviews size before another modeling/detail pass.

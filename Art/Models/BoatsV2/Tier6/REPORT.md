# Tier 6 offshore boat — concept choice only

Three painted options, each in side and rear three-quarter view, are in [concepts.png](../../../Source/BoatsV2/Tier6/concepts.png). The sheet includes the existing **Prep fisher, 6.8 m**, and **Buoy fisher (Tier5DeepLines103), 8.5 m**, to show the step into a 9–10 m offshore boat. Names below identify concepts; they are not new game data.

| Option | Design | Strength / cost |
|---|---|---|
| **A — Northstar, 9.4 m** | Compact enclosed forward wheelhouse; swept deep bow; two rail-side reels and sorting bench; broad uncovered timber aft deck. | Clearest offshore upgrade while preserving the simple walkable deck and the existing fleet silhouette. Least overhead clutter. |
| **B — Channel Runner, 9.7 m** | Low starboard-offset wheelhouse, raised protective forecastle, open port passage and rail-side stern davit. | Longer clear working run and a distinctive asymmetric silhouette. Foredeck height and cabin offset need careful crew-path treatment if chosen. |
| **C — Shelter Boat, 10.0 m** | Taller forward pilothouse, short roof over a side workbench, broad heavy hull and uncovered aft half. | Most sheltered working character for Whale shelf / Seal cliffs / Kelp forest. Extra roof mass could obscure a station at the game camera angle. |

**I recommend A.** Its enclosed wheelhouse and stronger bow make the offshore step readable, while the open aft deck gives crew and stations room without adding a full trawler superstructure. It keeps the navy hull, ivory trim and honey timber that connect the existing boats. Retain the lifted sheer and quiet clinker courses in any later model; keep benches, reels and fittings beside the rails with a continuous central walking route.

This is painted art direction, not a dimensional engineering or navigation drawing. The final 1536×1024 sheet aligns five side-profile bows in one column beside the three concept three-quarter views. Painted lengths are approximate; the named metre lengths are authoritative. The side profiles provide visual size comparison; final metre dimensions, freeboard, station placement, collision clearance and mesh budget would be established only after Mo selects an option. Three-quarter views prioritize seeing the working deck and do not imply a shared orthographic scale.

Built with the built-in imagegen skill/tool. Exact original and revision prompts are preserved in `Art/Source/BoatsV2/Tier6/`. Source reference inspection used the accepted PrepFisherV1 and Tier5DeepLines103 side renders and their documented hull lengths. Painted comparison boats summarize those silhouettes; they are not replacements for accepted boat art. The final receipt records dimensions, image SHA256 and visual review. Early draft preserved as `concepts-first.png` for provenance, not the selected delivery.

**STOP: Mo picks before any 3D.** No Tier 6 model, FBX, Unity import, gameplay change or git commit was made. Codex 2 (WSL CLI); no subagents.


## TIER6-BOAT-1 STEP0 inventory — Codex 2 (WSL CLI)

Mo selected C Shelter Boat,10m, all earlier-tier equipment. This inventory was extracted directly from four accepted source blends before modelling. Full names, hierarchy, bounds and source SHA256 in `Art/Source/BoatsV2/Tier6/station-inventory.json`. Source coordinates X right,-Y bow,Z up,metres.

### Tier5DeepLines103

| Object | Type | Parent | World position (m) |
|---|---|---|---|
| BowLocker | MESH | None | [0.0, 0.0, 0.0] |
| BuoyAccess_1 | EMPTY | None | [-1.35, -2.05, 0.0] |
| BuoyAccess_2 | EMPTY | None | [0.95, -2.05, 0.0] |
| BuoyAnchor_1 | EMPTY | None | [-2.8, -2.05, -0.3] |
| BuoyAnchor_2 | EMPTY | None | [2.8, -2.05, -0.3] |
| CanopyFrame | MESH | None | [0.0, 0.0, 0.0] |
| Cutting board 1 | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Cutting board 2 | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Deep 1 crank | MESH | DeepLineReelPivot_1 | [1.815, 0.2, 0.8] |
| Deep 1 hand reel | MESH | DeepLineReelPivot_1 | [1.94, 0.4, 0.74] |
| Deep 1 handle | MESH | DeepLineReelPivot_1 | [1.69, 0.135, 0.86] |
| Deep 1 hanging fishing line | MESH | DeepLineRig_1 | [3.34, 0.4, 1.43] |
| Deep 1 line guide | MESH | DeepLineRig_1 | [1.98, 0.4, 1.515] |
| Deep 1 line guide.001 | MESH | DeepLineRig_1 | [2.25, 0.4, 2.525] |
| Deep 1 line guide.002 | MESH | DeepLineRig_1 | [2.75, 0.4, 3.085] |
| Deep 1 line guide.003 | MESH | DeepLineRig_1 | [3.34, 0.4, 3.175] |
| Deep 1 orange grip | MESH | DeepLineRig_1 | [1.935, 0.4, 0.99] |
| Deep 1 rail clamp | MESH | DeepLineRig_1 | [1.86, 0.4, 0.44] |
| Deep 1 reel flange | MESH | DeepLineReelPivot_1 | [1.94, 0.24, 0.74] |
| Deep 1 reel flange.001 | MESH | DeepLineReelPivot_1 | [1.94, 0.56, 0.74] |
| Deep 1 tapered pole 0 | MESH | DeepLineRig_1 | [1.925, 0.4, 0.97] |
| Deep 1 tapered pole 1 | MESH | DeepLineRig_1 | [2.115, 0.4, 1.985] |
| Deep 1 tapered pole 2 | MESH | DeepLineRig_1 | [2.5, 0.4, 2.77] |
| Deep 1 tapered pole 3 | MESH | DeepLineRig_1 | [3.045, 0.4, 3.095] |
| Deep 2 crank | MESH | DeepLineReelPivot_2 | [1.815, 1.62, 0.8] |
| Deep 2 hand reel | MESH | DeepLineReelPivot_2 | [1.94, 1.82, 0.74] |
| Deep 2 handle | MESH | DeepLineReelPivot_2 | [1.69, 1.555, 0.86] |
| Deep 2 hanging fishing line | MESH | DeepLineRig_2 | [3.34, 1.82, 1.43] |
| Deep 2 line guide | MESH | DeepLineRig_2 | [1.98, 1.82, 1.515] |
| Deep 2 line guide.001 | MESH | DeepLineRig_2 | [2.25, 1.82, 2.525] |
| Deep 2 line guide.002 | MESH | DeepLineRig_2 | [2.75, 1.82, 3.085] |
| Deep 2 line guide.003 | MESH | DeepLineRig_2 | [3.34, 1.82, 3.175] |
| Deep 2 orange grip | MESH | DeepLineRig_2 | [1.935, 1.82, 0.99] |
| Deep 2 rail clamp | MESH | DeepLineRig_2 | [1.86, 1.82, 0.44] |
| Deep 2 reel flange | MESH | DeepLineReelPivot_2 | [1.94, 1.66, 0.74] |
| Deep 2 reel flange.001 | MESH | DeepLineReelPivot_2 | [1.94, 1.98, 0.74] |
| Deep 2 tapered pole 0 | MESH | DeepLineRig_2 | [1.925, 1.82, 0.97] |
| Deep 2 tapered pole 1 | MESH | DeepLineRig_2 | [2.115, 1.82, 1.985] |
| Deep 2 tapered pole 2 | MESH | DeepLineRig_2 | [2.5, 1.82, 2.77] |
| Deep 2 tapered pole 3 | MESH | DeepLineRig_2 | [3.045, 1.82, 3.095] |
| DeepLineBase_1 | EMPTY | DeepLineModule | [1.87, 0.4, 0.46] |
| DeepLineBase_2 | EMPTY | DeepLineModule | [1.87, 1.82, 0.46] |
| DeepLineModule | EMPTY | None | [0.0, 0.0, 0.0] |
| DeepLineReelPivot_1 | EMPTY | DeepLineRig_1 | [1.94, 0.4, 0.74] |
| DeepLineReelPivot_2 | EMPTY | DeepLineRig_2 | [1.94, 1.82, 0.74] |
| DeepLineRig_1 | EMPTY | DeepLineModule | [1.87, 0.4, 0.46] |
| DeepLineRig_2 | EMPTY | DeepLineModule | [1.87, 1.82, 0.46] |
| DeepLineTip_1 | EMPTY | DeepLineModule | [3.34, 0.4, 3.14] |
| DeepLineTip_2 | EMPTY | DeepLineModule | [3.34, 1.82, 3.14] |
| DeepLineWorker_1 | EMPTY | DeepLineModule | [1.25, 0.4, -0.0] |
| DeepLineWorker_2 | EMPTY | DeepLineModule | [1.25, 1.82, -0.0] |
| EngineFittings | MESH | None | [0.0, 0.0, 0.0] |
| FleetIvoryCap | MESH | None | [0.0, 0.0, 0.0] |
| FleetRubbingAndQuietCourses | MESH | None | [0.0, 0.0, 0.0] |
| GunwaleHardware | MESH | None | [0.0, 0.0, 0.0] |
| HelmConsole | MESH | None | [0.0, 0.0, 0.0] |
| HelmFittings | MESH | None | [0.0, 0.0, 0.0] |
| Hull | MESH | None | [0.0, 0.0, 0.0] |
| HullPaintBand | MESH | None | [0.0, 0.0, 0.0] |
| Ice marker horizontal | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Ice marker horizontal.001 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Ice marker vertical | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Ice marker vertical.001 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Insulated lid 1 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Insulated lid 1.001 | MESH | PreparedHold | [0.0, 0.0, 0.0] |
| Insulated lid 2 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Insulated lid 2.001 | MESH | PreparedHold | [0.0, 0.0, 0.0] |
| Knife blade 1 | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Knife blade 2 | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Knife handle 1 | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Knife handle 2 | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Module2_NetCrank | MESH | NetModule2 | [-2.22, 1.0, -0.0] |
| Module2_NetDrum | MESH | NetModule2 | [2.0675, 1.8315, 0.6757] |
| Module2_NetMountFittings | MESH | NetModule2 | [-2.22, 1.0, -0.0] |
| Module2_SternNetRoller | MESH | NetModule2 | [-2.22, 1.0, -0.0] |
| Module2_SternNet_Stowed | MESH | NetModule2 | [-2.22, 1.0, -0.0] |
| NetCrank | MESH | NetModule1 | [1.344, 4.419, 0.8057] |
| NetDrum | MESH | NetModule1 | [0.8315, 4.2875, 0.6757] |
| NetModule1 | EMPTY | None | [0.0, 0.0, 0.0] |
| NetModule2 | EMPTY | None | [0.0, 0.0, 0.0] |
| NetMountFittings | MESH | NetModule1 | [0.0, 0.0, 0.0] |
| NetWorker_1 | EMPTY | None | [0.95, 3.1, 0.0] |
| NetWorker_2 | EMPTY | None | [1.25, 1.8, 0.0] |
| OptionalRodModule | EMPTY | None | [0.0, 0.0, 0.0] |
| OutboardMotor | MESH | None | [0.0, 0.0, 0.0] |
| PREPARED freezer 1 | MESH | PreparedHold | [0.0, 0.0, 0.0] |
| PREPARED freezer 2 | MESH | PreparedHold | [0.0, 0.0, 0.0] |
| Plain_Insulated lid 1 | MESH | RawBuckets | [0.0, 0.0, 0.0] |
| Plain_Insulated lid 2 | MESH | RawBuckets | [0.0, 0.0, 0.0] |
| Plain_RAW ice cooler 1 | MESH | RawBuckets | [0.0, 0.0, 0.0] |
| Plain_RAW ice cooler 2 | MESH | RawBuckets | [0.0, 0.0, 0.0] |
| Plain_Recessed lid handle 1 | MESH | RawBuckets | [0.0, 0.0, 0.0] |
| Plain_Recessed lid handle 2 | MESH | RawBuckets | [0.0, 0.0, 0.0] |
| Plain_Storage front latch 1 | MESH | RawBuckets | [0.0, 0.0, 0.0] |
| Plain_Storage front latch 2 | MESH | RawBuckets | [0.0, 0.0, 0.0] |
| PlankDeck | MESH | None | [0.0, 0.0, 0.0] |
| Prep stainless rim | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Prep table leg | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Prep table leg.001 | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Prep table leg.002 | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Prep table leg.003 | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Prep table lower shelf | MESH | PrepStation | [0.0, 0.0, 0.0] |
| Prep washable top | MESH | PrepStation | [0.0, 0.0, 0.0] |
| PrepInput | EMPTY | None | [0.0, 0.175, 0.4] |
| PrepStation | EMPTY | None | [0.0, 0.0, 0.0] |
| PrepSurface | EMPTY | None | [0.0, 0.9, 0.7] |
| PrepWorker_1 | EMPTY | None | [-0.43, 1.75, 0.0] |
| PrepWorker_2 | EMPTY | None | [0.43, 1.75, 0.0] |
| PreparedHold | EMPTY | None | [0.0, 0.0, 0.0] |
| PreparedOutput | EMPTY | None | [0.0, 2.55, 0.5] |
| Propeller | MESH | None | [-0.636, 4.6408, -0.55] |
| RAW ice cooler 1 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| RAW ice cooler 2 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| RawBuckets | EMPTY | None | [0.0, 0.0, 0.0] |
| RawIceCoolers | EMPTY | None | [0.0, 0.0, 0.0] |
| Recessed lid handle 1 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Recessed lid handle 1.001 | MESH | PreparedHold | [0.0, 0.0, 0.0] |
| Recessed lid handle 2 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Recessed lid handle 2.001 | MESH | PreparedHold | [0.0, 0.0, 0.0] |
| RodHolder_1 | MESH | None | [-1.9, -0.35, 0.43] |
| RodHolder_2 | MESH | None | [1.9, -0.35, 0.43] |
| RodHolder_3 | MESH | OptionalRodModule | [1.9, 1.1, 0.43] |
| RodHolder_4 | MESH | OptionalRodModule | [1.9, 2.55, 0.43] |
| RodSocket_1 | EMPTY | None | [-1.9, -0.35, 0.47] |
| RodSocket_2 | EMPTY | None | [1.9, -0.35, 0.47] |
| RodSocket_3 | EMPTY | OptionalRodModule | [1.9, 1.1, 0.47] |
| RodSocket_4 | EMPTY | OptionalRodModule | [1.9, 2.55, 0.47] |
| SafetyFenders | MESH | None | [0.0, 0.0, 0.0] |
| ServiceAccess_1 | EMPTY | None | [0.65, -1.05, 0.0] |
| ServiceAccess_2 | EMPTY | None | [-0.85, -1.05, 0.0] |
| SternNetRoller | MESH | NetModule1 | [0.0, 0.0, 0.0] |
| SternNet_Stowed | MESH | NetModule1 | [0.0, 0.0, 0.0] |
| Storage front latch 1 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Storage front latch 1.001 | MESH | PreparedHold | [0.0, 0.0, 0.0] |
| Storage front latch 2 | MESH | RawIceCoolers | [0.0, 0.0, 0.0] |
| Storage front latch 2.001 | MESH | PreparedHold | [0.0, 0.0, 0.0] |
| orange beacon | MESH | None | [0.0, 0.0, 0.0] |
| patched plank over previous hold | MESH | None | [0.0, 0.0, 0.0] |
| short mast | MESH | None | [0.0, 0.0, 0.0] |
| squared helm canopy | MESH | None | [0.0, 0.0, 0.0] |
| teal canopy brow | MESH | None | [0.0, 0.0, 0.0] |

### PrepFisherV1

| Object | Type | Parent | World position (m) |
|---|---|---|---|
| BowLocker | MESH | None | [3.85, 0.0, 0.0] |
| Bucket handle | MESH | RawBuckets | [-0.624, 0.13, 0.3] |
| Bucket handle.001 | MESH | RawBuckets | [-0.096, 0.13, 0.3] |
| Bucket handle.002 | MESH | RawBuckets | [0.096, 0.13, 0.3] |
| Bucket handle.003 | MESH | RawBuckets | [0.624, 0.13, 0.3] |
| CanopyDripLip | MESH | None | [0.0, 0.0, 0.0] |
| CanopyFrame | MESH | None | [3.85, 0.0, 0.0] |
| CanopyTimberKnees | MESH | None | [0.0, 0.0, 0.0] |
| Chum pail under table | MESH | PrepStation | [0.0, 0.72, 0.25] |
| Cutting board 1 | MESH | PrepStation | [-0.36, 0.72, 0.66] |
| Cutting board 2 | MESH | PrepStation | [0.36, 0.72, 0.66] |
| EngineFittings | MESH | None | [3.85, 0.0, 0.0] |
| Fish on cutting board 1 | MESH | PrepStation | [-0.4, 0.72, 0.705] |
| Fish on cutting board 2 | MESH | PrepStation | [0.32, 0.72, 0.705] |
| GunwaleHardware | MESH | None | [3.85, 0.0, 0.0] |
| HelmConsole | MESH | None | [3.85, 0.0, 0.0] |
| HelmFittings | MESH | None | [3.85, 0.0, 0.0] |
| Hull | MESH | None | [3.85, 0.0, 0.0] |
| HullPaintBand | MESH | None | [3.85, 0.0, 0.0] |
| Ice marker horizontal | MESH | RawIceCoolers | [-0.36, -0.128, 0.25] |
| Ice marker horizontal.001 | MESH | RawIceCoolers | [0.36, -0.128, 0.25] |
| Ice marker vertical | MESH | RawIceCoolers | [-0.36, -0.127, 0.25] |
| Ice marker vertical.001 | MESH | RawIceCoolers | [0.36, -0.127, 0.25] |
| Insulated lid 1 | MESH | PreparedHold | [-0.36, 2.04, 0.49] |
| Insulated lid 1.002 | MESH | RawIceCoolers | [-0.36, 0.14, 0.49] |
| Insulated lid 2 | MESH | PreparedHold | [0.36, 2.04, 0.49] |
| Insulated lid 2.002 | MESH | RawIceCoolers | [0.36, 0.14, 0.49] |
| KeelAndRakedStem | MESH | None | [0.0, 0.0, 0.0] |
| Knife blade 1 | MESH | PrepStation | [-0.18, 0.705, 0.702] |
| Knife blade 2 | MESH | PrepStation | [0.54, 0.705, 0.702] |
| Knife handle 1 | MESH | PrepStation | [-0.18, 0.855, 0.702] |
| Knife handle 2 | MESH | PrepStation | [0.54, 0.855, 0.702] |
| NetCrank | MESH | None | [1.12, 3.532, 0.76] |
| NetDrum | MESH | None | [0.675, 3.43, 0.6699] |
| NetMountFittings | MESH | None | [3.85, 0.0, 0.0] |
| OutboardMotor | MESH | None | [3.85, 0.0, 0.0] |
| PREPARED freezer 1 | MESH | PreparedHold | [-0.36, 2.04, 0.245] |
| PREPARED freezer 2 | MESH | PreparedHold | [0.36, 2.04, 0.245] |
| PlankDeck | MESH | None | [3.85, 0.0, 0.0] |
| Prep stainless rim | MESH | PrepStation | [0.0, 0.72, 0.57] |
| Prep table leg | MESH | PrepStation | [-0.59, 0.5, 0.275] |
| Prep table leg.001 | MESH | PrepStation | [-0.59, 0.94, 0.275] |
| Prep table leg.002 | MESH | PrepStation | [0.59, 0.5, 0.275] |
| Prep table leg.003 | MESH | PrepStation | [0.59, 0.94, 0.275] |
| Prep table lower shelf | MESH | PrepStation | [0.0, 0.72, 0.2] |
| Prep washable top | MESH | PrepStation | [0.0, 0.72, 0.63] |
| PrepStation | EMPTY | None | [0.0, 0.0, 0.0] |
| PrepWorker_1 | EMPTY | None | [-0.36, 1.4, 0.0] |
| PrepWorker_2 | EMPTY | None | [0.36, 1.4, 0.0] |
| PreparedHold | EMPTY | None | [0.0, 0.0, 0.0] |
| PreparedOutput_1 | EMPTY | None | [-0.36, 2.04, 0.24] |
| PreparedOutput_2 | EMPTY | None | [0.36, 2.04, 0.24] |
| Propeller | MESH | None | [-0.5004, 3.695, -0.55] |
| RAW bucket 1 | MESH | RawBuckets | [3.85, 0.0, 0.0] |
| RAW bucket 2 | MESH | RawBuckets | [3.85, 0.0, 0.0] |
| RAW ice cooler 1 | MESH | RawIceCoolers | [-0.36, 0.14, 0.245] |
| RAW ice cooler 2 | MESH | RawIceCoolers | [0.36, 0.14, 0.245] |
| Raw fish in bucket | MESH | RawBuckets | [-0.43, 0.13, 0.31] |
| Raw fish in bucket.001 | MESH | RawBuckets | [-0.29, 0.13, 0.31] |
| Raw fish in bucket.002 | MESH | RawBuckets | [0.29, 0.13, 0.31] |
| Raw fish in bucket.003 | MESH | RawBuckets | [0.43, 0.13, 0.31] |
| RawBuckets | EMPTY | None | [0.0, 0.0, 0.0] |
| RawIceCoolers | EMPTY | None | [0.0, 0.0, 0.0] |
| RawInput_1 | EMPTY | None | [-0.36, 0.14, 0.24] |
| RawInput_2 | EMPTY | None | [0.36, 0.14, 0.24] |
| Recessed lid handle 1 | MESH | PreparedHold | [-0.36, 2.04, 0.535] |
| Recessed lid handle 1.002 | MESH | RawIceCoolers | [-0.36, 0.14, 0.535] |
| Recessed lid handle 2 | MESH | PreparedHold | [0.36, 2.04, 0.535] |
| Recessed lid handle 2.002 | MESH | RawIceCoolers | [0.36, 0.14, 0.535] |
| RodSocket_1 | MESH | None | [-1.6, 0.0, 0.47] |
| RodSocket_2 | MESH | None | [1.6, 0.0, 0.47] |
| RodSocket_3 | MESH | None | [-1.5375, 2.2037, 0.47] |
| RodVisual_1 | MESH | None | [3.85, 0.0, 0.0] |
| RodVisual_2 | MESH | None | [3.85, 0.0, 0.0] |
| RodVisual_3 | MESH | None | [3.85, 0.0, 0.0] |
| SafetyFenders | MESH | None | [3.85, 0.0, 0.0] |
| SternNetRoller | MESH | None | [3.85, 0.0, 0.0] |
| SternNet_Stowed | MESH | None | [3.85, 0.0, 0.0] |
| Storage front latch 1 | MESH | PreparedHold | [-0.36, 1.79, 0.39] |
| Storage front latch 1.002 | MESH | RawIceCoolers | [-0.36, -0.11, 0.39] |
| Storage front latch 2 | MESH | PreparedHold | [0.36, 1.79, 0.39] |
| Storage front latch 2.002 | MESH | RawIceCoolers | [0.36, -0.11, 0.39] |
| SweptCapAndRubber | MESH | None | [0.0, 0.0, 0.0] |
| Worker standing mat 1 | MESH | PrepStation | [-0.36, 1.4, 0.016] |
| Worker standing mat 2 | MESH | PrepStation | [0.36, 1.4, 0.016] |
| orange beacon | MESH | None | [0.58, -1.9, 1.98] |
| patched plank over previous hold | MESH | None | [-0.8125, 1.07, -0.018] |
| short mast | MESH | None | [0.58, -1.9, 1.71] |
| squared helm canopy | MESH | None | [0.0, -1.6, 1.43] |
| teal canopy brow | MESH | None | [0.0, -0.74, 1.43] |

### CompactFisherV1

| Object | Type | Parent | World position (m) |
|---|---|---|---|
| BowLocker | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| CanopyDripLip | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| CanopyFittings | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| CanopyFrame | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| Catchline_CompactFisherV1 | EMPTY | None | [0.0, 0.0, 0.0] |
| DeckDetails | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| EngineFittings | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| FishHold | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| GunwaleHardware | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| HelmConsole | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| HelmFittings | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| HelmRoof | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| HoldLid | MESH | Catchline_CompactFisherV1 | [-0.65, 0.35, 0.02] |
| HoldRimHinges | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| Hull | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| HullPaintBand | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| KeelAndRakedStem | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| NetCrank | MESH | Catchline_CompactFisherV1 | [1.12, 2.65, 0.67] |
| NetDrum | MESH | Catchline_CompactFisherV1 | [0.67, 2.65, 0.67] |
| NetMountFittings | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| OutboardMotor | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| PlankDeck | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| Propeller | MESH | Catchline_CompactFisherV1 | [-0.53, 2.94, -0.55] |
| RodSocket_1 | MESH | Catchline_CompactFisherV1 | [-1.28, -0.1, 0.47] |
| RodSocket_2 | MESH | Catchline_CompactFisherV1 | [1.28, -0.1, 0.47] |
| RodSocket_3 | MESH | Catchline_CompactFisherV1 | [-1.23, 1.65, 0.47] |
| RodVisual_1 | MESH | Catchline_CompactFisherV1 | [-1.28, -0.1, 0.47] |
| RodVisual_2 | MESH | Catchline_CompactFisherV1 | [1.28, -0.1, 0.47] |
| RodVisual_3 | MESH | Catchline_CompactFisherV1 | [-1.23, 1.65, 0.47] |
| SafetyFenders | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| SternNetRoller | MESH | Catchline_CompactFisherV1 | [0.67, 2.65, 0.67] |
| SternNet_Stowed | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |
| SweptCapAndRubber | MESH | Catchline_CompactFisherV1 | [0.0, 0.0, 0.0] |

### JigBoatV1

| Object | Type | Parent | World position (m) |
|---|---|---|---|
| CabinAftDoor | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| CabinBeaconAerial | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| CabinDoorGlass | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| CabinLifeRing | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| Catchline_JigBoatV1 | EMPTY | None | [0.0, 0.0, 0.0] |
| DeckCleats | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| DoorLatch | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| EngineLegPropeller | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| FlushHoldHatch | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| FrontWindow-0.335 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| FrontWindow0.335 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| HatchHandle | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| HoldHatchLid | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| Hull | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| InnerBulwark | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| JigReel_01 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| JigReel_02 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| JigReel_03 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| KeelAndRakedStem | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| LampCable | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| MotorOrangeCap | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| OutboardMotor | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| PlankDeck | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| RoofTimberLip | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SafetyFenders | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SideWindow-0.661-1.65 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SideWindow-0.661-2.35 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SideWindow0.661-1.65 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SideWindow0.661-2.35 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SortingTray | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SquidLamp_01 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SquidLamp_02 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SquidLamp_03 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SquidLamp_04 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SquidLamp_05 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SquidLamp_06 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SquidLamp_07 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SquidLamp_08 | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SternLocker | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SternLockerLid | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| SweptCapAndRubber | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| TwoShortLampMasts | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| WheelhouseBody | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |
| WheelhouseRoof | MESH | Catchline_JigBoatV1 | [0.0, 0.0, 0.0] |

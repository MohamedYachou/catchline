# HARBOUR-ART-1 — growing harbour kit

Codex 2 (WSL CLI). A–D individual art complete. E supplies five reviewed occupied clearance proposals; the adopted runtime layout still needs the corrections below.

Editable sources and FBXs are in this directory. Authoring script: `Art/Source/HarbourV2/build.py`; independent round-trip audit: `audit.py`. Blender 5.2.1 LTS. Metres, shared STYLE.md palette material names, matte broad bevels. No textures or external material folders. Preview cameras, lights and floor are excluded from FBX.

## Import and placement

New models face Unity local **-Z**. Old HouseA/B face +Z; the plan’s yaw180 for old houses must not be copied to new front-facing buildings. Use yaw0 for new doors/windows facing the water. Jib is an exact direct child of QuayCrane, pivot on the slew axis at local Y3.16. Gangway child pivot is at its quay end, local Y.35.

Absolute harbour-datum assets (root Y0): Slipway deck .35 to -.9; PontoonSegment/FuelDock deck0; PontoonGangway .35 to0; BreakwaterWall/End cap .6; OuterWharf deck .35; MouthBeacon rock sole -.8. Place other ground-contact buildings/props on the surface they stand on. Submerged construction is intentional.

## Individual asset checks

Each accepted row has a source+FBX triangle/material/mesh/bounds round-trip PASS and five individually opened 600px renders. Image hashes are in `reviewed-images.json`; full metrics and part details in `metrics/<name>.json`.

| Group | Model | Tris / limit | W × D × H (m) | State |
| --- | --- | ---: | --- | --- |
| A | Slipway | 456 / 1500 | 8.00 × 7.00 × 1.62 | Individual PASS |
| A | PontoonSegment | 1202 / 1500 | 2.14 × 4.00 × 0.52 | Individual PASS |
| A | PontoonGangway | 700 / 1500 | 1.26 × 3.05 × 1.19 | Individual PASS |
| A | FuelDock | 1342 / 1500 | 2.14 × 2.00 × 1.81 | Individual PASS |
| A | QuayCrane | 684 / 1500 | 1.15 × 4.59 × 4.87 | Individual PASS |
| A | BreakwaterWall | 544 / 1500 | 4.06 × 3.59 × 1.55 | Individual PASS |
| A | BreakwaterEnd | 540 / 1500 | 3.57 × 3.56 × 1.55 | Individual PASS |
| A | OuterWharf | 388 / 1500 | 4.00 × 1.87 × 1.59 | Individual PASS |
| A | WharfLight | 364 / 1500 | 0.42 × 0.42 × 2.71 | Individual PASS |
| A | MouthBeacon | 416 / 1500 | 1.92 × 1.61 × 3.02 | Individual PASS |
| B | HarbourMasterHut | 784 / 3000 | 2.87 × 2.41 × 3.65 | Individual PASS |
| B | NoticeBoard | 776 / 1500 | 2.24 × 0.89 × 2.64 | Individual PASS |
| B | SuppliesShed | 1984 / 3000 | 3.30 × 2.85 × 3.10 | Individual PASS |
| B | IceHouse | 740 / 3000 | 3.79 × 3.91 × 3.19 | Individual PASS |
| B | NetLoft | 1052 / 3000 | 3.31 × 3.57 × 4.66 | Individual PASS |
| B | BoatyardShed | 932 / 3000 | 9.28 × 5.35 × 4.85 | Individual PASS |
| B | BoatCradle | 560 / 3000 | 7.30 × 3.00 × 1.18 | Individual PASS |
| C | CompactFisherV1_VariantRed | 10164 (inherited boat exception) | 3.65 × 5.85 × 2.60 | Individual PASS |
| C | PrepFisherV1_VariantGreen | 13968 (inherited boat exception) | 4.56 × 7.25 × 2.70 | Individual PASS |
| C | Tier5DeepLines103_VariantBlue | 17096 (inherited boat exception) | 5.54 × 9.04 × 3.89 | Individual PASS |
| C | Skiff_VariantYellow | 2494 (inherited boat exception) | 3.59 × 7.04 × 1.48 | Individual PASS |
| D | ChannelMarkerRed | 420 / 1500 | 0.51 × 0.49 × 2.65 | Individual PASS |
| D | ChannelMarkerGreen | 420 / 1500 | 0.51 × 0.49 × 2.65 | Individual PASS |
| D | BellBuoy | 432 / 1500 | 1.36 × 1.36 × 2.30 | Individual PASS |
| D | Wreck | 428 / 1500 | 8.00 × 2.96 × 1.43 | Individual PASS |
| D | SealRocks | 1476 / 1500 | 6.23 × 3.24 × 1.71 | Individual PASS |
| D | FloatingCrate | 588 / 1500 | 0.76 × 0.62 × 0.53 | Individual PASS |
| D | Dolphin | 330 / 1500 | 2.20 × 1.01 × 0.89 | Individual PASS |
| D | SeagullDive | 280 / 1500 | 0.48 × 0.39 × 0.86 | Individual PASS |
| D | HandCart | 1352 / 1500 | 1.06 × 0.87 × 1.48 | Individual PASS |

Paint variants retain the exact released production hull geometry. Their inherited triangle counts exceed the generic 1500-triangle prop budget; this explicit exception follows the brief’s same-mesh requirement. Every variant has independent canonical-source and FBX triangle-surface identity checks. Newly authored buildings and props retain strict limits.

## Occupied assemblies — E

Five editable scenes and ten final renders are in `assembly/clearance/`: tier0–tier4, whole harbour1440×900 and landscape phone844×390. All final images were individually opened. Orthographic pitch45°, yaw35°. All five actual-mesh audits report zero boat/boat or boat/solid triangle-surface intersections. Canonical and variant meshes are unchanged. The initial portrait crops were superseded because they excluded berth edges.

At phone size the hut/notice board/stall, boatyard/pontoon/fuel station, net loft/crane, and ice house/shopfront groups read as distinct silhouettes. Small paper and shop symbols are decoration rather than readable text. The whole views show the increasing building set, older moored boats, the lighthouse exit and every berth. Water covers intentionally submerged foundations; buildings and landing supports meet their authored datums.

### Required placement handoff to Claude

This is a **clearance proposal**, not proof that the current runtime layout fits. `assembly/updated/tier4-audit.json` preserves four actual-mesh surface collisions in the latest rowboat/outer-slot coordinates, even after presentation datum/front corrections. Both rowboats at Z−1.8 intersect the slipway (196/200 triangle pairs); outer slot1 at X24.2 intersects two east-wall sections (453/1229 pairs), reaching X28.719. Earlier plan diagnostics remain in `assembly/plan/`.

| Item | Reviewed proposal (Unity metres) | Reason |
| --- | --- | --- |
| Rowboats | X−27.35/−22.65, Y0, **Z−4.8**, level | Z−3.7 still intersects ramp rails; Z−4.8 clears without pitching |
| Slipway | (−25,−.05,2.4) | Sunk ramp, unchanged mesh |
| Outer boats | X**11.9/21.4**, Y0; Z=−10.6+.9+.3+actual beam/2, bow−X | Full hulls clear each other, wharf and east wall |
| Breakwater/outer wharf | wall rootsY0, Z−12; wharf rootsY0, Z−10.6 | Authored local cap .6 and deck .35 already include heights |
| Quay4m | rootY.217 | Existing mesh top reaches .35 at this root |
| Gangway | (−13,0,3.5) | Local .35→0 ramp meets quay and pontoon without added height |
| Supplies shed | (−28,.35,6), yaw0 | Separate roof from boatyard, front toward water |
| Boatyard/cradle | both X−35,Z6.5; shedY.35, cradleY.35 | Cradle is inside shed, clear of adjacent roof |
| New buildings | yaw0, ground-contactY.35 | New fronts−Z; old HouseA/B keep yaw180 |
| Beach | Cut ramp opening, shore landing at (−25,−.12,3.65), 8×.94×2.5 | Excludes ramp/boat overlap and supports head of ramp |
| Crane | (16.5,.35,4.2) | Keeps quay service area clear |

Exact per-tier boat/asset transforms, occupied bounds, source hashes and camera settings are in each `tierN.json`; `assembly.py` reproduces them. Surface intersection tests do not establish containment-free solid clearance. Visual review supplements the test; it does not replace native runtime verification. This correction proposal is the remaining runtime dependency, assigned to Claude/Codex1.

## Delivery boundary

Individual exports, editable sources, 150 studio review hashes and ten final assembly review hashes are complete. Unity imports, actual runtime placement, lighting and native captures belong to Codex1/Claude. No Unity/gameplay/save/scene/build/install acceptance is claimed. No Assets or existing baseline sources were edited. No git operations. FISH-ARMS-2 follows this art handoff.

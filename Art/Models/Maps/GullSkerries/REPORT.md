# Seal skerries — MAP6-SKERRIES-FIX-1 addendum A–D

Codex 1 (Windows app), 2026-10-25. Revised terrain is exported and imported. Source/FBX checks, eleven-image art review, ten-image native capture/review and full fresh scratch safety checks are complete. Overall acceptance is PARTIAL: absent runtime life, retained art-contract conflicts and lead visual review remain unresolved. Lead visual acceptance remains pending. Accepted chart, spot and navigation integration is preserved.

The playable map remains 300 × 240 m. Ground IDs, centres, radii, depths and pool IDs are unchanged: Seal rocks (-84,-25), radius14m; Kelp gully (8,57), radius15m; Outer reef (99,-35), radius18m. Source geometry uses metres and the existing compensated FBX transform. Runtime map origin is (0,-0.32,0).

## Terrain and placement

- Four principal islands now have angular grey-pink granite, split slabs/boulders, pale wet bands, dark waterline weed and stone seabed. Fourteen closed terrain objects supply actual mesh slices for navigation.
- **A — Colony slabs:** near-flat stepped tops 0.85m and1.05m above local water, broken rectangular edges, both7.659m from Seal rocks. Added dome boulders removed. Exported colony empties are on the flat tops. Broad slab footprints are5.4×3.6m before the inset terraces.
- **B — Gully:** parallel13m granite ridges,2.15/2.65m high, either side of the unchanged ground, kelp between. Conservative waterline-edge clearance is at least5m beyond the8.5×4.2m hull's circumscribed radius. Added dome boulders removed.
- **C — Reef/foam:** six half-tide reefs remain8–15m from Outer reef. All baked ReefBreak/OuterReefBreakingPatch meshes and fin foam removed. Six named ReefBreak empties remain for Claude's animated art. Only narrow static contact foam rings at rock waterlines remain,3.5cm above local water.
- The northern granite stack is7.68m high plus a separate cairn. Forty outer marker buoys and the harbour contract remain intact.

## Life-anchor contract

Nine named empties survive actual FBX import and are checked in Unity against their expected world coordinates. The map's local waterline is0; runtime waterline is-0.32. Colony tops therefore have worldY0.53/0.73. The buoy remains9.666m from Seal rocks.

| Empty | World X | World Y | World Z |
|---|---:|---:|---:|
| SealColony_1 | -91.61896 | 0.53 | -25.76902 |
| SealColony_2 | -82.11680 | 0.73 | -32.42250 |
| ReefBreak_1 | 100.4392 | -0.24 | -39.9168 |
| ReefBreak_2 | 101.9624 | -0.24 | -41.2306 |
| ReefBreak_3 | 107.9758 | -0.24 | -40.6077 |
| ReefBreak_4 | 110.9758 | -0.24 | -39.6077 |
| ReefBreak_5 | 112.3758 | -0.24 | -37.6077 |
| ReefBreak_6 | 112.7758 | -0.24 | -35.1077 |
| CrabBuoy_1 | -80 | -0.32 | -33.8 |

**Runtime dependency D:** current `Sea/SeaScenery.cs:BuildNavigableSea` instantiates the map without calling `DressSkerries`. The legacy `VoyageScenery` path calls it. Claude owns this runtime integration; Codex1 did not modify it. Native evidence below must explicitly record visible/absent life. Anchor existence alone does not establish life visibility or animation.

## Verified source and art evidence

[Build validation](SeaV2-validation.json) and [independent source/actual-FBX audit](SeaV2-source-audit.json):29232triangles,761meshes,14closed terrain objects,40buoys,nineempties;109assertions PASS. Maximum vertex roundtrip error17.643micrometres. Source/FBX/import navigation hashes agree. Rebuild entrypoint: `Art/Source/Art108/map6_skerries.py`.

The retained [art audit](SeaV2-audit.json) passes83of89assertions, including all six routes at2m and4m clearance and unchanged114protected legacy files. Six original assertions fail because the complete14/15/18m ground circles intersect the required nearby rocks/shallows. No assertion was removed or relaxed. Anchoring and actual sailing paths are checked separately in Unity. Claude must resolve this full-zone contract conflict.

All eleven final images were individually opened; [visual review](SeaV2-visual-review.json) binds their hashes. [Seal day](SeaV2-seal-rocks-day.png), [Seal night](SeaV2-seal-rocks-night.png), [Gully day](SeaV2-kelp-gully-day.png), [Gully night](SeaV2-kelp-gully-night.png), [Reef day](SeaV2-outer-reef-day.png), [Reef night](SeaV2-outer-reef-night.png), [Wide day](SeaV2-wide-day.png), [Wide night](SeaV2-wide-night.png), [Top](SeaV2-top-base.png), [Navigation](SeaV2-navigation-plate.png), [Sheet](SeaV2-review-sheet.png).

The art camera remains orthographic10.24m horizontal span, pitch45°/yaw35°,1440×900, centred at unchanged grounds. Low colony slabs occupy cropped lower corners; the half-tide reef enters lower-right. The mandated gully hull clearance puts both ridges outside this narrow rowboat fixture. This is an unresolved framing limitation, recorded for Claude; neither camera nor anchor was moved to conceal it. Wide/top views show both long ridges. No runtime life or HUD is present in this art-only fixture. Native tier5 views are separate evidence.

## Native handoff and limits

Fresh scratch verification passed with Unity exit0:360directed routes across6maps/5hulls,18sea lanes, five harbour baseline round trips, all three new-ground tier5 out/anchor/home trips,9imported anchors and700-coin chart purchase. Ground-specific pools are ready. Ten desktop/landscape native frames, per-frame observations, source/build hashes, check logs/JSON and final receipt are in [the fix evidence folder](../../../../docs/screens/map6-skerries-fix-1/README.md). Native frames confirm terrain framing but show no seals, animated breaking surf or crab-buoy life set; D remains partial pending Claude runtime wiring. Prior [MAP6 evidence](../../../../docs/screens/map6-skerries-1/README.md) and iteration1 captures are historical rejected terrain.

No git operation, main Unity batchmode, installed-player replacement, player-save access, watchdog marker, or reopened Fish/Deck/Harbour queue. Claude owns runtime life and final acceptance. Temporary before-state backups were made under Catchline-sim/Temp; scratch Unity startup cleared that temporary directory. No backup remains and no additional backup deletion is needed. Final source/export checks and image evidence remain available.



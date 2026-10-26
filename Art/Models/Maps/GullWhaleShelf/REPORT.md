# Whale shelf — MAP9-WHALE-SHELF-1

Codex 1 (Windows app), 2026-10-25. Terrain/import/check delivery and scoped chart handoff complete; lead review/commit pending.

New spot 8 beyond Lighthouse rock: 360 × 280m open continental shelf, one low angular bird-whitened sea mount, connected underwater terrace and sand-coloured shoals. No buildings or baked life. The three grounds use the exact requested existing-species weights, RowSeconds 34, BiteWait 1.5 and ChartCost 1920.

The source contains 25,466 triangles, one real waterline obstacle, seven shallow contours and 46 boundary buoys. Six angular underwater corner landmarks have centres 6.24m from their ground anchors. They remain below the waterline; the connected shelf falls away into deep water. Colours are 2A7F96 and 102F4F. Navigation comes from fresh closed-mesh slices, not hand-drawn islands. FBX uses the established axis compensation and identity Unity root at world Y=-.32.

[Independent source/FBX audit](SeaV2-source-audit.json): 49 checks pass, including fresh .blend and imported FBX geometry/slices. [Scoped navigation audit](SeaV2-audit.json): 49 pass. [Raw audit](SeaV2-audit-raw.json) retains three inherited full-ground-circle shallow conflicts. Claude's 17:47 MAP8 acceptance permits corner landmarks within those circles; the MAP9 adapter excludes only those named submerged shelves and still requires 4m actual anchor clearance. Historical common auditors are unchanged. This exception does not waive real route, lane or hull checks.

Six EMPTY life anchors are supplied for Claude's dispatch. [Downward-ray audit](SeaV2-anchor-audit.json) proves the gull anchor on the highest visible crown and all five water anchors unobstructed at Y=-.32. Temporary orange cylinders in anchor PNGs are review markers only and never enter the FBX.

| Anchor | World position |
| --- | --- |
| GannetDive_1 | (-89, -.32, -41) |
| GannetDive_2 | (-79, -.32, -38) |
| WhaleSpout_1 | (107, -.32, -48) |
| WhaleSpout_2 | (118, -.32, -44) |
| CardinalBuoy_1 | (9.016, -.32, 63.3644) |
| WreckGulls_1 | (-23, 1.08, 15) |

Pipeline: `map9_whale_shelf.py build|review|anchors`, `map9_source_audit.py -- GullWhaleShelf`, `map9_audit.py`. Blender previews use clear transmissive review water; Unity optics are reviewed separately. No foam fins or runtime props are baked. All 17 final art PNGs were individually opened and hash-bound in `art-review.json`. The underwater corner shelves look faint in Blender night renders, but are clearly visible at both native sizes.

[Native and scratch evidence](../../../../docs/screens/map9-whale-shelf-1/README.md) records actual source/build hashes, completed checks and ten individually opened native frames. The original full run passed 540 nine-map/five-hull routes, then failed an inherited horizon-island assertion. The own fixture preserves older-map horizon checks and applies MAP9's open-shelf contract; shared checks stay unchanged. Final revised terrain passes all 60 affected routes, nine-map scene assets, all 27 sea lanes, five baseline harbour hull trips and three ordinary MAP9 captain bait/cast/home trips. The final wrapper and native process both exit 0.

Native author review: two faceted corner ledges at each ground, clear hull and bubble space, floating cardinal buoy, visible whale-tail silhouette. The left ledges are partly behind the existing HUD. All 126 game sources matched main at native launch. Frozen stills do not prove life animation, caught-fish yield, physical touch or installed-player acceptance.

Chart handoff resolved 2026-10-26: Claude spot8 point(.06,.40) and whale-tail glyph verified in exact1440x900/844x390 standalone frames. Whale shelf pin/card clears Harbour mouth. Three affected normal ground/bait-cast/home trips and new standalone build passed; final native exit0. All ten rerun frames individually opened and dimensions/hashes recorded in docs/screens/map9-whale-shelf-1/chart-handoff/. Production blue water explicitly accepted for this delivery; future optics, trip landmarks and life remain lead-owned. No player-save access, main Unity batchmode, installed-player replacement, git, watchdog marker or subagents.

The temporary `Catchline-sim/Backups/map9-before` cleanup was rejected by automatic approval review as "blocked by policy". It remains outside the production checkout; no alternate deletion method was attempted. The crew rollback backup is retained as separate evidence.

# MAP8 Lighthouse rock — native and safety evidence

Codex 1 (Windows app), 2026-10-25. Terrain/import, the buried puffin ledges and the off-rock cardinal buoy are delivered for Claude's review. Source and scratch checks pass; six inherited full-ground-circle art failures remain explicit pending the lead's contract decision. See the [terrain report](../../../Art/Models/Maps/GullLighthouseRock/REPORT.md). Final integrity manifest: `verification-receipt.json`.

Reproduction commands (Catchline-sim only; preserve the original safety snapshot):

```powershell
powershell -File Art/Source/Art108/map8_resources.ps1
powershell -File docs/tools/check.ps1 -Name map8-safety-build -Method Catchline.EditorTools.LighthouseRockMapChecks.RunAndBuild
powershell -File docs/tools/check.ps1 -Name map8-lighthouse-life -Method Catchline.EditorTools.LighthouseLifeChecks.Run
powershell -File docs/tools/check.ps1 -Name map8-postintegration -Method Catchline.EditorTools.LighthouseRockMapChecks.PostIntegrationAndBuild
powershell -File Art/Source/Art108/map8_native.ps1
uv run --with pillow python Art/Source/Art108/map8_evidence.py age
uv run --with pillow python Art/Source/Art108/map8_evidence.py native
uv run --with pillow python Art/Source/Art108/map8_evidence.py life
uv run --with pillow python Art/Source/Art108/map8_evidence.py final
```

Full safety/build passes eight maps, 480 directed hull routes across five hulls, 24 sea lanes, five baseline harbour hull trips and three normal new-ground bait/cast/home trips: [JSON](map8-checks.json), [Unity log](check-map8-safety-build.log), [verified wrapper](safety-build-wrapper.log). Its immutable [125-input snapshot](safety-source/source-hashes.json) represents the actual original scratch run. That run predates the final ledge and buoy-anchor fixes; its exact-anchor assertions and native build are superseded. Every navigation field other than four life anchors, and all ground/pool data, remain unchanged. The raised puffin shelves are above the navigation cuts.

The final targeted check uses Claude's chart point (.66,.24), checks three approach lanes with 4.5m clearance, three normal bait/cast/home trips, life component counts, shader availability/material and final anchor transforms, renders six perches, then builds the native player: [JSON](map8-postintegration-checks.json), [Unity log](check-map8-postintegration.log), [verified wrapper](postintegration-wrapper.log). Actual Unity exit 0. Its [131-input snapshot](postintegration-source/source-hashes.json) retains changes since the original full run without rewriting historical evidence.

Puffin anchors are now world (-16,2.08,-5), (-6,3.38,-4.7), (8,4.68,-3.8). Independent 84 surface rays prove support for the rotated 2.64m groups and offset birds without overhead rock. CardinalBuoy_1 is now (99.015998,-.32,-48.635642), 1.51776m outside the nearest waterline rock. TideRace_1..2 and LighthouseLamp_1 remain unchanged. See the [anchor audit](../../../Art/Models/Maps/GullLighthouseRock/SeaV2-anchor-fix-audit.json).

All six dressed perch images and four production life-check images were individually opened and bound in [life review](life-visual-review.json): [perch 1 deck](perch-1-deck.png), [top](perch-1-top.png), [perch 2 deck](perch-2-deck.png), [top](perch-2-top.png), [perch 3 deck](perch-3-deck.png), [top](perch-3-top.png), [life map](life-check/lighthouse-life-map.png), [puffins](life-check/lighthouse-life-PuffinLedge_2.png), [race](life-check/lighthouse-life-TideRace_1.png), [lamp](life-check/lighthouse-life-LighthouseLamp_1.png). All groups and separate birds are exposed and supported; bright shelf tops reflect this review lighting.

Required production LighthouseLifeChecks logs LIGHTHOUSELIFE PASS and actual Unity exit 0: [log](life-check/check-map8-lighthouse-life.log). Its generic [wrapper](lighthouse-life-wrapper.log) returns 1 because the method exits directly without the wrapper's default snapshot sentinel. This is a wrapper limitation, not a claimed wrapper pass. The earlier genuine missing-shader failure is retained in [failed log](lighthouse-life-missing-resource.log) and [wrapper](lighthouse-life-missing-resource-wrapper.log). check.ps1 excludes Resources; the scoped resource helper copied production shader resources byte-for-byte into scratch. No production life/checker code was changed.

The final SessionOnly native fixture buys the 1370-coin chart through actual UI, departs normally, reaches all three named grounds, returns home and quits with actual exit 0. [Launch/build/source hashes](native-run.json), [exit](native-exit.json), [log](native.log), [ten capture records](capture-complete.txt), [individual review](native-visual-review.json). All 125 game source files matched main at launch. Ten final frames were individually opened:

| View | Desktop / landscape | Observation |
| --- | --- | --- |
| Chart | [1440×900](chart-1440.png) / [844×390](chart-844.png) | Lighthouse glyph, label and 1370 price readable; labels fit. |
| Sail out | [1440×900](sail-out-1440.png) / [844×390](sail-out-844.png) | Native route, hull, progress and HUD visible. |
| The pinnacle | [1440×900](the-pinnacle-1440.png) / [844×390](the-pinnacle-844.png) | Two low angular corner rocks; left partly behind existing HUD; clear hull and bubble space. |
| Tide race | [1440×900](tide-race-1440.png) / [844×390](tide-race-844.png) | Corner rocks and production race pieces visible; clear hull and bubbles. |
| Deep ledge | [1440×900](deep-ledge-1440.png) / [844×390](deep-ledge-844.png) | Corrected cardinal buoy visibly floats in water beside the rock at both sizes. |

Native frames use current production blue water. The central lighthouse, cottage and puffins lie outside the tight fishing crops and are covered by wide/detail terrain and dressed perch evidence. Twelve art PNGs are hash-bound in the terrain report; the final buoy-only empty move did not change terrain pixels. Reviews are the author's evidence, with lead/player acceptance pending.

The six art failures are the requested 6–12m corner landmarks intersecting inherited 12–20m full-ground circles; assertions were retained. Real routes, borders and lanes pass independently. MapNav timing advisories remain separate. Frozen-time stills do not prove animation, physical touch, caught-fish yield or installed-player behavior. No player-save/PlayerPrefs access, installed replacement, main Unity batchmode, git, watchdog marker or subagents. MAP9 starts only after Claude reviews and commits MAP8.

Temporary backup cleanup was attempted only for the verified absolute task path `C:/Users/momoy/Projects/Catchline-sim/Backups/map8-before`; automatic approval review rejected the deletion as "blocked by policy". The backup remains outside the production checkout. No alternate deletion method was attempted.

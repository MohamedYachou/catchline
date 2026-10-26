# MAP9 — native and safety evidence

Codex 1 (Windows app), 2026-10-25. Own MAP9 delivery finished, waiting on Claude chart/water integration and review. [Terrain report](../../../Art/Models/Maps/GullWhaleShelf/REPORT.md). Final integrity manifest: `verification-receipt.json`.

The first full nine-map check passed 540 directed routes across five hulls, then failed the inherited scene assertion that every map has horizon island silhouettes. The open shelf deliberately has one sea mount and no horizon islands. Its actual failed log is retained in `check-map9-safety-build.log`, with [132 actual inputs](safety-source/source-hashes.json). This run predates the final submerged-corner placement revision; it is not a successful full build.

The final fixture preserves horizon checks on the older eight maps and checks MAP9 against its open-water contract; shared `SeaSceneChecks` is unchanged. All 60 affected MAP9 routes, nine-map scene assets, 27 sea lanes, five baseline harbour hull trips and three MAP9 bait/cast/home trips pass on the final terrain. The wrapper verifies actual Unity exit0 and successful native TEST build: [JSON](map9-final-checks.json), [Unity log](check-map9-final-build.log), [wrapper](final-build-wrapper.log). [Final input snapshot](final-source/source-hashes.json) differs from the original only in the MAP9 FBX/navigation and own fixture.

All 17 final art images were individually opened, including six anchor markers: [hash-bound author review](art-review.json). Submerged corner ledges are faint in Blender, especially at night, but clearly visible in native frames at both sizes. Author review does not establish lead acceptance.

The fixture checks the 1919-coin refusal and exact 1920-coin purchase, all six imported anchor world transforms, all three precise species pools, ordinary harbour/chart/sea departure, arrival, captain bait/cast into water and all return-home legs. None of these assertions proves caught-fish yield, animation, physical touch or installed-player behavior.

The native SessionOnly test buys the 1920-coin chart through actual UI, departs normally, reaches all three grounds, returns home and quits with actual exit0. All 126 game sources match main at launch: [source/build/scene hashes](native-run.json), [exit](native-exit.json), [log](native.log), [ten frame records](capture-complete.txt), [individual review](native-visual-review.json). All ten final frames were individually opened:

| View | Desktop / landscape | Observation |
| --- | --- | --- |
| Chart | [1440×900](chart-1440.png) / [844×390](chart-844.png) | Whale shelf and 1920 price readable; pin shares Harbour fallback and card partly covers Harbour subtitle. |
| Sail out | [1440×900](sail-out-1440.png) / [844×390](sail-out-844.png) | Correct route HUD, hull and dashed route; buoy visible. |
| Herring shoals | [1440×900](herring-shoals-1440.png) / [844×390](herring-shoals-844.png) | Two pale faceted corner ledges, clear hull and bubble space. |
| Shelf edge | [1440×900](shelf-edge-1440.png) / [844×390](shelf-edge-844.png) | Two grey ledges and cardinal buoy floating beside the hull. |
| Whale road | [1440×900](whale-road-1440.png) / [844×390](whale-road-844.png) | Both ledges, whale-tail silhouette and birds visible. |

Left ledges are partly behind the existing HUD. Claude owns chart point/glyph, trip-chart landmarks, water biome and life. QUESTIONS remain: supply distinct spot8 chart point/glyph; review requested clear teal/navy shelf optics (tight grounds currently use production blue water); review life animation. Frozen-time captures do not establish spout/tail animation, touch or installed-player acceptance. Next pickup starts with Claude's integration/readiness, then capture only changed dependencies; the verified earlier terrain steps remain closed.

Reproduction uses only the scratch project:

```powershell
powershell -File docs/tools/check.ps1 -Name map9-safety-build -Method Catchline.EditorTools.WhaleShelfMapChecks.RunAndBuild
powershell -File docs/tools/check.ps1 -Name map9-final-build -Method Catchline.EditorTools.WhaleShelfMapChecks.FinalTerrainAndBuild
powershell -File Art/Source/Art108/map9_native.ps1
```

Before launching checks, copy production Assets/Resources/Shaders byte-for-byte to scratch with `map9_resources.ps1`: the shared wrapper excludes Resources. Preserve original evidence snapshots when repeating a check. Final reviews/receipt use `uv run --with pillow python Art/Source/Art108/map9_evidence.py native-review` and `receipt` only after individual openings. No commit, subagents, player-save access, main-project Unity batchmode or watchdog marker.

Temporary backup cleanup was attempted only for the verified absolute task path `C:/Users/momoy/Projects/Catchline-sim/Backups/map9-before`; automatic approval review rejected deletion as "blocked by policy". The backup remains outside the production checkout. No alternate deletion method was attempted. Separate crew rollback evidence is retained.

Chart handoff RESOLVED2026-10-26: see chart-handoff/README.md and review.json. Exact1440x900/844x390 native chart frames clear Harbour mouth,three affected ground/bait-cast/home trips pass,new standalone build/nativeexit0. Production blue water accepted. Earlier unresolved chart/optics notes above are historical.

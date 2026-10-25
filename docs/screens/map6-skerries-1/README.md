# Seal skerries native evidence

25 October 2026, Codex 1 (Windows app). MAP6-SKERRIES-1 map/import/check delivery is complete. Claude-owned species pools, landmark labels, chart glyph and runtime life placement/animation remain pending. No installed-player or touch acceptance is claimed.

[Map report](../../../Art/Models/Maps/GullSkerries/REPORT.md) describes art, coordinates and all remaining dependencies. [Verification receipt](verification-receipt.json) binds this delivery to source, import, build and frame hashes.

## Final native frames

All ten were opened individually. Each came from the same isolated SessionOnly TEST player, with actual chart purchase, normal departure, ground relocation and return home. The helper froze simulation for each pair of resolutions. It did not replace the installed game or read/write the player's save.

| View | Desktop 1440x900 | Landscape 844x390 | Review |
|---|---|---|---|
| Chart | [PNG](native/chart-1440.png) | [PNG](native/chart-844.png) | Corrected pin/card clear Contracts; price 700. Pin still uses lead-owned home glyph. |
| Sail out | [PNG](native/sail-out-1440.png) | [PNG](native/sail-out-844.png) | Normal SeaOut leg; water, departure banner and HUD reviewed. |
| Seal rocks | [PNG](native/seal-rocks-1440.png) | [PNG](native/seal-rocks-844.png) | Ground arrival and boat/HUD reviewed; colonies not yet wired. |
| Kelp gully | [PNG](native/kelp-gully-1440.png) | [PNG](native/kelp-gully-844.png) | Kelp visible; phone Fish callout overlaps 65s timer. Logged for Claude. |
| Outer reef | [PNG](native/outer-reef-1440.png) | [PNG](native/outer-reef-844.png) | Submerged reef and boat/HUD reviewed; animated reef life not yet wired. |

All three ground frames show the fallback Shallow label. Their actual navigation ground IDs and positions are in [capture-complete.txt](native/capture-complete.txt). Species-specific ground pools are not accepted: `groundPoolsReady=false` in the scratch receipt. [Native log](native/native.log) confirms all ten frames, TEST/no save reads or writes, and return home. No exception/error was found in this final native log.

`iteration-1/` preserves the ten individually reviewed earlier frames and their log. Its chart pin overlapped Contracts; that layout was rejected and corrected before the final capture. Use `native/` for the final evidence.

## Verified checks

- [Initial scratch receipt](map6-checks.json): six real maps, 360 directed hull routes, 18 clear sea lanes, five baseline harbour trips, each of the three new ground/home trips, chart affordability at 699/700 coins, asset lookup and both empty-anchor world transforms. [Full log](check-map6-skerries.log).
- [Changed chart entry recheck](map6-chart-recheck.txt): three affected lanes at 6.50 m clearance and all three new ground/home trips passed after moving point 5 to `(0.375,0.115)`. [Full log](check-map6-chart-final.log).
- [Life import checks](map6-life-import.txt): seven ArtLibrary models, exact mesh triangle counts, six-bone seal and stable Legacy Bask/Look/Slide clips. Sampled baked-skin motion and loop closure passed. [Full log](check-map6-life-import.log). [Artist/source/import hash parity](life-import-hashes.json).
- [Final build stamp](map6-build.txt): scratch Windows native build succeeded after the life import checks. The verification receipt hashes its executable and managed assembly.
- Map-folder art receipts record 49 independent audit checks, 32 fresh source/FBX checks, 11 individually reviewed art PNGs and 114 protected legacy files unchanged. Old static check summary strings still say five maps or 6/5; their actual loop/count is six maps and 360 routes.

Static Seal skerries routes range from 8.15 to 30.50 seconds across hulls; some retain the existing 10-20 second target warnings. Collision, border and arrival checks passed. No hull speeds or existing spot rules were changed.

## Reproduction

Run from the main checkout in PowerShell; these commands use `Catchline-sim`, never batchmode the main project:

```powershell
./docs/tools/check.ps1 -Name map6-skerries -Method Catchline.EditorTools.SkerriesMapChecks.RunAndBuild
./docs/tools/check.ps1 -Name map6-chart-final -Method Catchline.EditorTools.SkerriesMapChecks.RecheckChartAndBuild
./docs/tools/check.ps1 -Name map6-life-import -Method Catchline.EditorTools.SkerriesLifeImport.CheckAndBuild
```

The last method rebuilds `../Catchline-sim/Builds/Map6Capture/Catchline.exe`. Launch that exact scratch player with `-capture-map6 <absolute-new-output-directory> -logFile <absolute-log-path> -screen-fullscreen 0`. Use a new output directory to preserve this reviewed evidence. The generated scene is SessionOnly; the capture helper refuses a save-enabled scene. Native capture drives travel and chart purchase; it does not validate the fishing minigame or species distributions.

No git operation, player-save change, installed-player replacement or watchdog file. All temporary own source backups were removed after verification. Claude's runtime and Codex 2's original artist sources were not edited.

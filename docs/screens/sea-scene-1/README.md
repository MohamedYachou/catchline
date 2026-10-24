# SEA-SCENE-1 native acceptance

Codex 2 (WSL CLI), 2026-10-24. All five SeaV2 maps render in the native TEST player. Water remains continuous beyond the buoys; fog and darkening increase over the last 30 metres. Explicit Sail/Fish here controls gate movement, with snapping, rerouting, stop, gear confirmation, eased steering/camera, route and fading wake. Return travel retains the real map until the navigation harbour is reached.

The final 80 PNGs below were each opened and visually inspected at their captured size. Anchored and sailing hulls retain their normal wood/navy appearance. Ground cues use the finished gull model and a thin teal ripple, replacing the opaque white disc. Border framing keeps the hull visible, and wide horizon views show distant authored scenery without the earlier rectangular water seam. The rowboat fixture covers all three grounds per map, a moving route/wake, border, wide horizon, return transit and actual harbour arrival.

## Checks and reproduction

- `regressions.tsv`: all 16 invocations PASS (`success=true`, `result=true`): MapNav Run/Gameplay (five maps, 300 routes), SeaScene Assets, SeaMode, M0, M1Graph, Rowboat, Skiff, Compact, Prep, Buoy, M2 runtime, M2/M3/M4/M5 data/checks.
- `final-checks.tsv`: final SeaScene Assets, SeaMode and M4 PASS after visual polish. SeaMode also checks preserved 3.2 anchored zoom and border hull viewport framing.
- `capture-compile.tsv`: no compile errors. `build-command.tsv` and the receipt record a successful scratch Win64 build. `native.log`: TEST launch, all 80 frames, completion; no exception/shader error. `capture-result.txt`: exit 0 and unchanged player-save SHA256.
- `verification-receipt.json`: every checked sea source/resource plus the three integration files and all five SeaV2 model files matches the built scratch copy byte for byte; executable and managed assembly hashes included. `frames.json` records dimensions and SHA256 for every inspected PNG.
- Reproduce in Windows PowerShell: run `./docs/screens/sea-scene-1/capture.ps1`, then `regressions.ps1` and `final-checks.ps1`. These use only the live **Catchline-ui2-sim** Editor; never open/batchmode the canonical project. Capture sync excludes ArtLibrary.asset and prunes only deleted scratch script copies. The fixture scene is created only in scratch, requires SessionOnly, and never loads/writes the player's save.

## Scope and limits

These are actual native Win64/D3D11 frames with runtime HUD. The fixture advances real game API/simulation code with manual ticks and freezes presentation while taking both sizes. It clears transient toasts to expose the sea, so it does not accept toast layout during return travel. Horizon frames use a deliberately wide inspection zoom; anchored frames use normal gameplay zoom. The focused checks exercise Sail/gear modal/stop/snap transitions, but physical touchscreen gestures and a full hand-played Real session were not performed. The installed Real/Test pair needs the lead's normal rebuild/install to include this task; this task built and ran only the isolated acceptance player.

No fish tables, save formats, main scenes or art assets were edited. Schools.cs changes only cue construction (gull model and ripple). Existing PropsV2/SeaV2 art and scratch ArtLibrary are dependencies, not new art delivered by this task. Shared UI/deck/minigame work is untouched.

## Individually inspected final captures

### GullHarbourMouth

| State | 1440 × 900 | 844 × 390 |
| --- | --- | --- |
| ground-1 | [GullHarbourMouth-ground-1-1440.png](GullHarbourMouth-ground-1-1440.png) | [GullHarbourMouth-ground-1-844.png](GullHarbourMouth-ground-1-844.png) |
| ground-2 | [GullHarbourMouth-ground-2-1440.png](GullHarbourMouth-ground-2-1440.png) | [GullHarbourMouth-ground-2-844.png](GullHarbourMouth-ground-2-844.png) |
| ground-3 | [GullHarbourMouth-ground-3-1440.png](GullHarbourMouth-ground-3-1440.png) | [GullHarbourMouth-ground-3-844.png](GullHarbourMouth-ground-3-844.png) |
| mid-sail | [GullHarbourMouth-mid-sail-1440.png](GullHarbourMouth-mid-sail-1440.png) | [GullHarbourMouth-mid-sail-844.png](GullHarbourMouth-mid-sail-844.png) |
| fog-border | [GullHarbourMouth-fog-border-1440.png](GullHarbourMouth-fog-border-1440.png) | [GullHarbourMouth-fog-border-844.png](GullHarbourMouth-fog-border-844.png) |
| horizon | [GullHarbourMouth-horizon-1440.png](GullHarbourMouth-horizon-1440.png) | [GullHarbourMouth-horizon-844.png](GullHarbourMouth-horizon-844.png) |
| home-mid | [GullHarbourMouth-home-mid-1440.png](GullHarbourMouth-home-mid-1440.png) | [GullHarbourMouth-home-mid-844.png](GullHarbourMouth-home-mid-844.png) |
| home-arrived | [GullHarbourMouth-home-arrived-1440.png](GullHarbourMouth-home-arrived-1440.png) | [GullHarbourMouth-home-arrived-844.png](GullHarbourMouth-home-arrived-844.png) |

### GullKelpBank

| State | 1440 × 900 | 844 × 390 |
| --- | --- | --- |
| ground-1 | [GullKelpBank-ground-1-1440.png](GullKelpBank-ground-1-1440.png) | [GullKelpBank-ground-1-844.png](GullKelpBank-ground-1-844.png) |
| ground-2 | [GullKelpBank-ground-2-1440.png](GullKelpBank-ground-2-1440.png) | [GullKelpBank-ground-2-844.png](GullKelpBank-ground-2-844.png) |
| ground-3 | [GullKelpBank-ground-3-1440.png](GullKelpBank-ground-3-1440.png) | [GullKelpBank-ground-3-844.png](GullKelpBank-ground-3-844.png) |
| mid-sail | [GullKelpBank-mid-sail-1440.png](GullKelpBank-mid-sail-1440.png) | [GullKelpBank-mid-sail-844.png](GullKelpBank-mid-sail-844.png) |
| fog-border | [GullKelpBank-fog-border-1440.png](GullKelpBank-fog-border-1440.png) | [GullKelpBank-fog-border-844.png](GullKelpBank-fog-border-844.png) |
| horizon | [GullKelpBank-horizon-1440.png](GullKelpBank-horizon-1440.png) | [GullKelpBank-horizon-844.png](GullKelpBank-horizon-844.png) |
| home-mid | [GullKelpBank-home-mid-1440.png](GullKelpBank-home-mid-1440.png) | [GullKelpBank-home-mid-844.png](GullKelpBank-home-mid-844.png) |
| home-arrived | [GullKelpBank-home-arrived-1440.png](GullKelpBank-home-arrived-1440.png) | [GullKelpBank-home-arrived-844.png](GullKelpBank-home-arrived-844.png) |

### GullSandbar

| State | 1440 × 900 | 844 × 390 |
| --- | --- | --- |
| ground-1 | [GullSandbar-ground-1-1440.png](GullSandbar-ground-1-1440.png) | [GullSandbar-ground-1-844.png](GullSandbar-ground-1-844.png) |
| ground-2 | [GullSandbar-ground-2-1440.png](GullSandbar-ground-2-1440.png) | [GullSandbar-ground-2-844.png](GullSandbar-ground-2-844.png) |
| ground-3 | [GullSandbar-ground-3-1440.png](GullSandbar-ground-3-1440.png) | [GullSandbar-ground-3-844.png](GullSandbar-ground-3-844.png) |
| mid-sail | [GullSandbar-mid-sail-1440.png](GullSandbar-mid-sail-1440.png) | [GullSandbar-mid-sail-844.png](GullSandbar-mid-sail-844.png) |
| fog-border | [GullSandbar-fog-border-1440.png](GullSandbar-fog-border-1440.png) | [GullSandbar-fog-border-844.png](GullSandbar-fog-border-844.png) |
| horizon | [GullSandbar-horizon-1440.png](GullSandbar-horizon-1440.png) | [GullSandbar-horizon-844.png](GullSandbar-horizon-844.png) |
| home-mid | [GullSandbar-home-mid-1440.png](GullSandbar-home-mid-1440.png) | [GullSandbar-home-mid-844.png](GullSandbar-home-mid-844.png) |
| home-arrived | [GullSandbar-home-arrived-1440.png](GullSandbar-home-arrived-1440.png) | [GullSandbar-home-arrived-844.png](GullSandbar-home-arrived-844.png) |

### GullRockyPoint

| State | 1440 × 900 | 844 × 390 |
| --- | --- | --- |
| ground-1 | [GullRockyPoint-ground-1-1440.png](GullRockyPoint-ground-1-1440.png) | [GullRockyPoint-ground-1-844.png](GullRockyPoint-ground-1-844.png) |
| ground-2 | [GullRockyPoint-ground-2-1440.png](GullRockyPoint-ground-2-1440.png) | [GullRockyPoint-ground-2-844.png](GullRockyPoint-ground-2-844.png) |
| ground-3 | [GullRockyPoint-ground-3-1440.png](GullRockyPoint-ground-3-1440.png) | [GullRockyPoint-ground-3-844.png](GullRockyPoint-ground-3-844.png) |
| mid-sail | [GullRockyPoint-mid-sail-1440.png](GullRockyPoint-mid-sail-1440.png) | [GullRockyPoint-mid-sail-844.png](GullRockyPoint-mid-sail-844.png) |
| fog-border | [GullRockyPoint-fog-border-1440.png](GullRockyPoint-fog-border-1440.png) | [GullRockyPoint-fog-border-844.png](GullRockyPoint-fog-border-844.png) |
| horizon | [GullRockyPoint-horizon-1440.png](GullRockyPoint-horizon-1440.png) | [GullRockyPoint-horizon-844.png](GullRockyPoint-horizon-844.png) |
| home-mid | [GullRockyPoint-home-mid-1440.png](GullRockyPoint-home-mid-1440.png) | [GullRockyPoint-home-mid-844.png](GullRockyPoint-home-mid-844.png) |
| home-arrived | [GullRockyPoint-home-arrived-1440.png](GullRockyPoint-home-arrived-1440.png) | [GullRockyPoint-home-arrived-844.png](GullRockyPoint-home-arrived-844.png) |

### GullDeepChannel

| State | 1440 × 900 | 844 × 390 |
| --- | --- | --- |
| ground-1 | [GullDeepChannel-ground-1-1440.png](GullDeepChannel-ground-1-1440.png) | [GullDeepChannel-ground-1-844.png](GullDeepChannel-ground-1-844.png) |
| ground-2 | [GullDeepChannel-ground-2-1440.png](GullDeepChannel-ground-2-1440.png) | [GullDeepChannel-ground-2-844.png](GullDeepChannel-ground-2-844.png) |
| ground-3 | [GullDeepChannel-ground-3-1440.png](GullDeepChannel-ground-3-1440.png) | [GullDeepChannel-ground-3-844.png](GullDeepChannel-ground-3-844.png) |
| mid-sail | [GullDeepChannel-mid-sail-1440.png](GullDeepChannel-mid-sail-1440.png) | [GullDeepChannel-mid-sail-844.png](GullDeepChannel-mid-sail-844.png) |
| fog-border | [GullDeepChannel-fog-border-1440.png](GullDeepChannel-fog-border-1440.png) | [GullDeepChannel-fog-border-844.png](GullDeepChannel-fog-border-844.png) |
| horizon | [GullDeepChannel-horizon-1440.png](GullDeepChannel-horizon-1440.png) | [GullDeepChannel-horizon-844.png](GullDeepChannel-horizon-844.png) |
| home-mid | [GullDeepChannel-home-mid-1440.png](GullDeepChannel-home-mid-1440.png) | [GullDeepChannel-home-mid-844.png](GullDeepChannel-home-mid-844.png) |
| home-arrived | [GullDeepChannel-home-arrived-1440.png](GullDeepChannel-home-arrived-1440.png) | [GullDeepChannel-home-arrived-844.png](GullDeepChannel-home-arrived-844.png) |

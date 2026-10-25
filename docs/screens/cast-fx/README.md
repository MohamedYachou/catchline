# Cast landing splash

CAST-SPLASH-1, Codex 1 (Windows app). Review delivery; no commit or player install.

A real cast's Flying -> Waiting transition records its landing world point. For 0.7 simulated seconds the accepted foam ring expands and fades there; droplets pop for 0.32 seconds. Every draw projects that point through the current camera. Captain close-up and deck rods share the hook. Existing landing splash audio is preserved without a second playback. Missing ring art falls back to pale teal fx-glow; missing droplets are skipped.

| After landing | 1440 x 900 | 844 x 390 |
| --- | --- | --- |
| 0.1 seconds | [Desktop](cast-1440-1.png) | [Phone](cast-844-1.png) |
| 0.3 seconds | [Desktop](cast-1440-3.png) | [Phone](cast-844-3.png) |
| 0.6 seconds | [Desktop](cast-1440-6.png) | [Phone](cast-844-6.png) |

Additional real deck-clock landings: [desktop](deck-1440.png), [phone](deck-844.png).

All eight images were opened and inspected. The six close-up images show droplets at 0.1 seconds, a broader ring at 0.3 seconds and a faint ring at 0.6 seconds. The bobber stays readable, the supplied oval keeps its authored aspect, and pause/reel controls remain clear. The two deck images show the effect at the ordinary bobber, below the established HUD. No visual correction required after this pass.

These are scripted Unity scratch scene renders composited with the production CoastalCanvas, following LeadShots. They are not interactive player or device acceptance; the landscape image is a Unity render at phone dimensions.

## Scope and checks

New runtime partial `Assets/Scripts/Game/VoyageCastFx.cs` and editor harness `Assets/Editor/CastFxCapture.cs`, with fresh metas. Shared changes are exactly one tick-hook replacement in VoyageGame.cs and one draw-hook addition before the RodView early return in VoyageInterface.cs. No other shared-file edits, art edits, new audio, save writes, or git operations.

`CastFxCapture.Run`: 59 assertions passed in Catchline-sim (Unity exit 0). Production captain cast and deck-clock cast both record landing; recorded position equals CastTarget; rings expand/fade and use the accepted imported sprite; short droplets expire; moving the camera reprojects the ring; Waiting does not retrigger it; retained ids hide after 0.7 seconds. Six required frames and two additional deck frames captured. `checks.json` records the count. The fallback paths are source-reviewed; accepted sprites were present during these captures.

Full `CrewCardsAbilityChecks.Regression`: passed, Unity exit 0. Includes ability 286 assertions, M2 data/M2, BiteModel/CageModel PASS, tutorial 217 assertions, and the final integration PASS marker. Full `regression.log` and `capture.log` are retained beside `verification.json`.

Source provenance: `capture-inputs.json` records every main/scratch C# hash and verifies exact equality for the capture run. `capture-source-baseline.json` retains the initial main source inventory. Final verification confirms all 232 main/scratch C# files still match the tested inputs; the full logs and receipt accompany this report.

Reproduce in the assigned scratch only:

```powershell
& docs/tools/check.ps1 -Name cast-fx-capture -Method Catchline.EditorTools.CastFxCapture.Run
& docs/tools/check.ps1 -Name cast-fx-regression -Method Catchline.EditorTools.CrewCardsAbilityChecks.Regression
```

The wrapper's success marker and Unity process exit must both pass; the main Unity project must never run in batchmode.


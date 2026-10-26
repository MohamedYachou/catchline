# Strike tap effects

Codex 1 (Windows app), 2026-10-26. Technical delivery complete; no commit.

A gently pulsing gold TAP! badge sits beside the mint bobber ring while a bite is actionable. Accepted strike input starts a round mint ripple at the actual pointer position; keyboard/programmatic input uses the bobber. It grows from .3 to 1.4 and fades over .45 seconds. Missing sprites are guarded; strike rules remain unchanged.

Four final images individually opened against `Art/Source/StrikeTap/review/goal-strike-panel.png`: bite-1440.png, bite-844.png, ripple-1440.png, ripple-844.png. The burst clears the ring at maximum pulse; label/controls remain legible and ripple remains round. These are Unity editor URP renders with the production native Canvas composite, not standalone/device screenshots.

capture.log records pickup8: Unity exit0 and 88 assertions for pointer position/edge, fallback, positioning/pulse, growth/fade/expiry and unchanged strike outcome. regression.log records complete CrewCardsAbilityChecks.Regression: Unity exit0,286 ability assertions,M2,bite/cage,217 tutorial action/save/skip assertions,zero unresolved targets and final integration marker.

Sources: VoyageStrikeFx.cs and StrikeFxCapture.cs with metas; one hook in VoyageGame.cs and one in Minigame/VoyageRodView.cs. review-receipt.json binds opened images and source hashes. Capture-only manual Input System settings restore afterward. Temporary Catchline-sim/Backups/strike-tap-before retained: deletion was rejected by automatic approval review as blocked by policy; no alternate deletion attempted.

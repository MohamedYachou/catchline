# SOUND-WIRE-5

Fifteen SOUND-5 recordings installed, three variants per cue. Existing cue IDs remain unchanged; the five new cues are appended. Stand-ins work when recorded variants are unavailable.

| Cue | Trigger (under Assets/Scripts/Game) | Gain | Stand-in |
| --- | --- | --- | --- |
| NewSpecies | VoyageFeedback.cs:33 — ShowCatch, new species only | .50 | RewardChime |
| FishLeap | VoyageFeedback.cs:33 — alongside NewSpecies | .45 | Splash |
| StampThud | VoyageFirstCatchFx.cs:15 — first observed reveal time >= .8, once per reveal | .40 | Click |
| CoinLand | VoyageCoinFx.cs:77 — observed coin landing count increases | .12 | Coins |
| GoalReady | VoyageSavingsGoal.cs:24 — savings tile changes from unready to ready | .35 | Bell |

Stamp guard resets for each catch and the preview entry point. Savings readiness rearms after becoming unready and resets when there is no next boat. Coin timing retains the existing presentation behavior: one cue per observed increase, including when multiple contacts fall within one frame.

## Verification

- installed-audio.json: source/resource SHA256 equality and fresh Bell-cloned importer GUIDs (15 files).
- source-snapshot.json: production source hashes before isolated verification.
- audio-baseline.json: existing resource bytes to preserve; protected Horn_1/2 and SealBark_1/2 also match the SOUND-WIRE-4 audit.
- SoundWire5Checks.cs.txt: isolated test harness. A scratch-only observer at VoyageAudio.Play entry checks cue dispatch, gains and once guards; imported PCM and exact generated fallback samples are also checked. This observer is never added to the main project.

Isolated audio/trigger verification: **53 assertions PASS, Unity exit 0** (audio-checks.json and audio-checks.log), including purchase-flight CoinFx. Claude subsequently adjusted only the purchase arc control point; the tested sound dispatch and gain are unchanged. final-audio-audit.json confirms all 15 copies/importers/GUIDs and all 234 existing resource files unchanged. Full regression: **PASS, Unity exit 0**, including **TUTORIAL CHECKS PASSED: 217**, M2 DATA, 286 ability assertions, M2, BITEMODEL, CAGEMODEL and the final integration marker. See regression.log, verification.json and regression-sources.json/final-sources.json. Claude corrected Hello to point at shop/close while the market overlays the port; the test follows that real action and then verifies port/sail at desktop and landscape phone sizes. The earlier genuine target failure is preserved in regression-before-fix.log and verification-before-fix.json. The check.ps1 wrapper can incorrectly accept an earlier Snapshot marker after a failure; this delivery independently verifies Unity exit 0 and all required PASSED markers. No listening or player acceptance is claimed; Mo owns listening and mix acceptance. Producer source/licensing/measurement evidence: Art/Audio/delivery-receipt-sound5.json and Art/Audio/REPORT.md.
The isolated harness is copied to Catchline-sim/Assets/Editor/SoundWire5Checks.cs. Its runtime observer needs a scratch-only public static Action<Cue, float> Sound5Observer field in VoyageAudio and Sound5Observer?.Invoke(cue, gain) at the first line of Play. Main source remains unchanged. The normal check.ps1 source mirror removed both modifications before the full regression; zero observer references and no harness file were verified in that scratch tree.
Temporary backup Catchline-sim/Backups/sound-wire5-before (five source files) remains because automatic approval review rejected its deletion as blocked by policy, without a further reason. No cleanup executed. The scratch-only observer and harness were already removed by the normal source mirror before regression; this backup is separate from those test modifications.
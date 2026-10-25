# SOUND-WIRE-4

## Step 0: installed cue provenance

Audit UTC: 2026-10-25T22:32:07.1780978Z. Source: `Assets/Scripts/Game/VoyageAudio.cs` (SHA256 `25F4F987FF27C0EEE65878C16CFA928DE5752939BCDB73055CFD464337182C3A`).

Enumerated all 32 current `VoyageAudio.Cue` members and all five Resources loader slots (0..4), finding 96 packed WAVs. Each was compared against every WAV in `Art/Audio/Real/SFX` by SHA256, then exact complete byte equality; alternate filenames count as matches. Full paths and hashes: [resources-audit.json](resources-audit.json).

**Cues with a Resources clip not from Art/Audio/Real: 4 variants.**

| Cue | Installed variants | Exact Real matches |
| --- | --- | --- |
| Cast | 0, 1, 2 | 3/3 |
| Splash | 0, 1, 2 | 3/3 |
| Bite | 0, 1, 2 | 3/3 |
| Reel | 0, 1, 2 | 3/3 |
| Land | 0, 1, 2 | 3/3 |
| Stow | 0, 1, 2 | 3/3 |
| Moor | 0, 1, 2 | 3/3 |
| Sale | 0, 1, 2 | 3/3 |
| Select | 0, 1, 2 | 3/3 |
| Purchase | 0, 1, 2 | 3/3 |
| Gull | 0, 1, 2 | 3/3 |
| Bell | 0, 1, 2 | 3/3 |
| Creak | 0, 1, 2 | 3/3 |
| Horn | 0, 1, 2 | 1/3 |
| Click | 0, 1, 2 | 3/3 |
| Winch | 0, 1, 2 | 3/3 |
| CrabClack | 0, 1, 2 | 3/3 |
| SealBark | 0, 1, 2 | 1/3 |
| NetSlap | 0, 1, 2 | 3/3 |
| Gut | 0, 1, 2 | 3/3 |
| Coins | 0, 1, 2 | 3/3 |
| CardFlip | 0, 1, 2 | 3/3 |
| ChestOpen | 0, 1, 2 | 3/3 |
| ChestHeavy | 0, 1, 2 | 3/3 |
| RewardChime | 0, 1, 2 | 3/3 |
| TokenPour | 0, 1, 2 | 3/3 |
| Puffin | 0, 1, 2 | 3/3 |
| Foghorn | 0, 1, 2 | 3/3 |
| DogBark | 0, 1, 2 | 3/3 |
| Meow | 0, 1, 2 | 3/3 |
| PotDrop | 0, 1, 2 | 3/3 |
| Stitch | 0, 1, 2 | 3/3 |

### Non-Real variants

- `Assets/Resources/Audio/SFX/Horn_1.wav`: `C954550D6969C211E8767E132B3F7288487EB13E30A4AC1DCA06E6F6985CEAD3`
- `Assets/Resources/Audio/SFX/Horn_2.wav`: `075B2A40F43E5360A400869968A52297888A0941E7F0A44F9B0608243E908509`
- `Assets/Resources/Audio/SFX/SealBark_1.wav`: `7217BE11922E6EA196F1A7F1FCE6339C0E6582347418FACBD8AE7967F809796D`
- `Assets/Resources/Audio/SFX/SealBark_2.wav`: `6E52066FFC76D8C6E7C30FB949EA4198905A15BA71419CC5C7D6762442F2FE7E`

Cues with no packed variants: none. The generated MakeCue fallbacks still exist in source for missing-resource recovery; this inventory describes installed WAV bytes, not runtime playback or listening acceptance.

## Integration

SOUND-4 technical delivery accepted and gate lifted by Claude; subjective listening belongs to Mo. Fifteen recordings are installed with exact source bytes and fresh GUIDs cloned from Bell_0.wav.meta. [installed-audio.json](installed-audio.json) records WAV/meta hashes and GUID uniqueness. The four S0 exceptions above remain unchanged. The S0 inventory is the pre-integration baseline (32 cues); five cues are now appended (37 total).

| Cue | Trigger (repository file:line) | Gain before master volume | Success / repetition guard |
| --- | --- | --- | --- |
| CoachPop | `Assets/Scripts/Game/VoyageTutorial.cs:107` | 0.30 | Existing tutorial step/text-change gate; replaces CardFlip |
| RefitFanfare | `Assets/Scripts/Game/VoyageGame.cs:328,338,346` | 0.35 | Skiff, Compact and Prep only after successful refit; below old Product purchase gain 0.60 |
| RefitFanfare | `Assets/Scripts/Game/VoyageTier5.cs:42` | 0.35 | Tier-5 only after successful refit |
| TabTap / PageTurn | `Assets/Scripts/Game/VoyageHud.cs:155` | 0.35 | OpenShop: chart gets PageTurn; other shops get TabTap, replacing Select without stacking |
| CoinBuy | `Assets/Scripts/Game/VoyageInterfaceShop.cs:145,164` | 0.60 | Both Product buy actions: only if the action actually spends coins; failures and free toggles/mending stay silent |
| CoinBuy | `Assets/Scripts/Game/CrewUi/CrewRecruit.cs:27` | 0.60 | Only after non-null successful chest result; replaces Purchase |

Fallbacks: CoachPop -> Click; RefitFanfare -> Bell; TabTap -> Click; CoinBuy -> Coins (existing Sale fallback); PageTurn -> Creak. Appended enum values preserve all previous numeric IDs. Fishing cues, market sale audio, habitats, timers and layouts were not changed by this task.

The Product callbacks return void. Actual coin debit is used to confirm a paid purchase, so a stale enabled button cannot produce a success sound after a rejected buy. Refit celebrations and their Product coin clink are separate brief-requested events.

## Verification

Required scratch regression PASS, Unity exit 0: M2 data, 286 crew ability assertions, M2, BiteModel, CageModel and CREW ABILITY INTEGRATION REGRESSION. Command: `powershell -File docs/tools/check.ps1 -Name sound-wire4-regression -Method Catchline.EditorTools.CrewCardsAbilityChecks.Regression`. [Regression evidence](regression-evidence.txt).

Scratch-only audio smoke PASS, Unity exit 0: 52 assertions cover all fifteen imported mono 44.1kHz clips/duration caps, preserved enum IDs, exact fallback sample equality, packed/missing-pack Play calls and session-only mute. [Audio evidence](audio-evidence.txt), [audio-checks.json](audio-checks.json).

[verification.json](verification.json) binds source/log hashes and identifies concurrent source drift against [the tested scratch source manifest](regression-sources.json). This is a check of that snapshot; later peer edits are outside its result. Harness retained as [SoundWire4Checks.cs.txt](SoundWire4Checks.cs.txt), outside production Assets. Resources copied separately because check.ps1 excludes Resources. No main-project batchmode, player save, git, installed-player, auditory or player-acceptance claim.
Final readback: the only tested/current difference in VoyageInterfaceShop.cs was peer whitespace at the sail rectangle; both sound action lines match. Claude also advanced VoyageSavingsGoal.cs after the tested snapshot. No source rerun is claimed for those later changes.

Temporary cleanup was rejected by automatic approval review as blocked by policy (no specific reason supplied). The pre-edit source backup remains at `Catchline-sim/Backups/sound-wire4-before`; the scratch-only harness and its meta remain at `Catchline-sim/Assets/Editor/SoundWire4Checks.cs`. Neither is production code. No own Unity/check process remains. No git/commit.

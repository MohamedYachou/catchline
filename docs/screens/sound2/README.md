# HARBOUR-SOUND-2 integration

The delivered SOUND2 pack is installed at `Assets/Resources/Audio`: 18 SFX variants and two ambience loops, each with a fresh GUID and the existing Bell AudioImporter settings. All 20 WAV hashes match `Art/Audio/delivery-receipt-sound2.json`.

| Sound | Trigger (relative to repository root) | Gain before master volume | Cooldown / schedule |
| --- | --- | --- | --- |
| PotDrop | `Assets/Scripts/Game/VoyageTier5.cs:99`: first positive soak tick after deployment or recovery, for small pots and tier 5 traps | 0.22 | 0.8 s shared guard; simultaneous pots give one drop |
| Stitch | `Assets/Scripts/Game/Minigame/VoyageRepairView.cs:98`: a graded mend trace, after rejecting empty/invalid strokes | 0.20 | 0.2 s guard; no repeated frame playback |
| Puffin | `Assets/Scripts/Game/VoyageAudio.cs:101`: fishing on Rocky point (3), Seal skerries (5), Lighthouse rock (7) | 0.16 | 35-70 s; 30 s shared guard |
| Foghorn | `Assets/Scripts/Game/VoyageAudio.cs:103`: at a far fishing ground (4-8) | 0.18 | 90-160 s; independent global 90 s guard |
| DogBark | `Assets/Scripts/Game/VoyageAudio.cs:97`: harbour only | 0.12 | 45-85 s; 45 s guard |
| Meow | `Assets/Scripts/Game/VoyageAudio.cs:99`: harbour only | 0.10 | 60-110 s; 60 s guard |
| HarbourDusk | `Assets/Scripts/Game/VoyageAudio.cs:86`: harbour with existing `harbourEvening` flag from Mix caller `VoyageGame.cs:831` | 0.16 looping bed | Replaces HarbourDay; changes only when selected clip changes |
| LighthouseRock | `Assets/Scripts/Game/VoyageAudio.cs:87`: ground 7 while at a fishing ground | 0.23 looping bed | Replaces OpenSea; existing Skerries bed retained elsewhere |

Every new SFX gain is below the existing Bell gains (0.25 in intro / 0.4 at the buoy). Ambient calls use their own AudioSource with random pitch 0.95-1.05, leaving fishing/crew-office effects at their original pitch. Only one new ambient call plays at a time; calls stop on habitat changes, pause suppresses scheduling and mutes effects. Opening menus does not produce catch-up bursts. Initial calls wait at least 35 / 90 / 45 / 65 seconds respectively. Existing master-volume preferences are preserved; tests use session-only volume.

Fallbacks: Puffin -> Gull, Foghorn -> Horn, DogBark/Meow -> SealBark, PotDrop -> Splash, Stitch -> Click. New enum members are appended, preserving old numeric cue IDs. Mending exists, so a net-stow stand-in trigger was unnecessary. There is no sea day/night clock used here; the brief's far-ground alternative drives the foghorn.

**Provenance question for Claude:** the brief describes real CC0 recordings, but the artist's SOUND-2 report explicitly identifies these files as original deterministic synthesis with no downloaded audio or recordings. This integration uses the exact delivered files and does not establish recording/CC0 provenance. The issue is also logged in `comms.md`.

Verification results will be appended after the scratch checks finish. `HarbourSound2Checks.cs.txt` is the reviewable scratch-only harness; it is not installed in the production Assets tree. No main-project batchmode, save changes, git operations or listening acceptance are claimed.

Verified results:

- Required exact shared-source run: `powershell -NoProfile -File docs/tools/check.ps1 -Name harbour-sound2-final -Method Catchline.EditorTools.CrewCardsAbilityChecks.Regression` — Unity exit 0. Ability checks 286, M2 data/economy, BiteModel, CageModel and integration regression passed. Full log: `C:/Users/momoy/Projects/Catchline-sim/Logs/check-harbour-sound2-final.log`; concise output in `regression-evidence.txt`.
- Audio harness: 52 assertions passed, full regression also passed, exit 0. This earlier isolated run used a scratch-only tutorial definite-assignment fix; the later required regression copied Claude's corrected source and used no workaround. Log: `Catchline-sim/Logs/sound2-patched-scratch.log`. Harness removed from scratch by the final source sync.
- `verification.json` binds all 20 WAV/meta files and four changed source hashes, with main/scratch source equality and globally unique new GUIDs. `audio-checks.json` records the audio smoke result. Audio Resources were copied separately because `check.ps1` excludes Resources.
- Source scope: `VoyageAudio.cs`, one Mix-call update in `VoyageGame.cs`, one Play line in `VoyageTier5.cs`, one Play line in `Minigame/VoyageRepairView.cs`. `VoyageCrabPots.cs` was restored to its pre-task bytes after rejecting an unreachable visibility trigger. No UI/Data/Art/scenes changes by this task; no git operations. Temporary pre-change backup removed after verification.
- These checks prove import/mixer/cooldown behavior and simulation regression. They do not establish subjective timbre, loop perception, live listening balance or player acceptance. Claude/Mo should hear one deployment, a mend trace, an evening harbour stay and lighthouse/far-ground ambience before accepting the final mix.

# Integration check — four night deliveries

Codex 1 (Windows app), 2026-10-26. Verification only; no production edits, staging or commit. Lead review remains separate.

## File ownership for review and staging

[inventory.md](inventory.md) lists **every changed/new file** classified by delivery, including authoring sources, imported assets, metas and evidence. [inventory.json](inventory.json) is the machine-readable list; [status-before.txt](status-before.txt) preserves the full dirty-tree inventory. Files in `other/unassigned` are explicitly outside these four deliveries and must not be swept into their commit. That section includes ongoing Codex 2 boat/crew work, Claude UI/capture/settings changes and earlier uncommitted deliveries. Unknown provenance is flagged there rather than assigned to this work.

Shared production hunks against HEAD, using **current-tree line numbers**:

| File | Lines | Delivery |
| --- | --- | --- |
| Assets/Editor/ArtImport.cs | 86 | HARBOUR-PETS-1: import Dog/Cat animations |
| Assets/Scripts/Game/Minigame/VoyageRodView.cs | 80 | STRIKE-TAP-1: draw effect |
| Assets/Scripts/Game/VoyageGame.cs | 1001 | STRIKE-TAP-1: record accepted strike |
| Assets/Scripts/Game/VoyageScenery.cs | 68 | HARBOUR-PETS-1: dress harbour pets |
| Assets/Scripts/Game/VoyageScenery.cs | 106 | MAP9 + MAP10: append both environments |
| Assets/Scripts/Game/Sea/SeaNav.cs | 19 | MAP9 + MAP10: append both navigation maps |
| Assets/Scripts/Game/Data/Grounds.cs | 79–83 / 84–88 | MAP9 / MAP10 ground pools |
| Assets/Scripts/Game/GameData.cs | 186–191 / 192–197 | MAP9 / MAP10 spot entries |

[shared-hunks.patch](shared-hunks.patch) contains the exact zero-context hunks. These seven files contain only the listed feature changes at the inventory snapshot. SeaNav and the environment-array line are shared by both map deliveries and should be staged together. The inventory provides individual paths for `git add`; no Git mutation was performed.

New Assets files: [meta-audit.json](meta-audit.json) records each GUID. All new files have companion metas; all 1,174 Assets metas were scanned, with **zero duplicate GUIDs**. New folder metas are included in the full inventory.

## Execution and provenance

One scratch standalone build is requested. [check-with-fixture.ps1](check-with-fixture.ps1) is a copy of `docs/tools/check.ps1` with one pre-launch injection after its unchanged Assets sync. [prepare.ps1](prepare.ps1) supplies scratch-only orchestration/native capture fixtures, redirects the two existing capture output directories into this delivery, and synchronizes production Resources before library generation. Production gameplay code is unchanged; the only edits to existing scratch C# are capture output paths. [IntegrationChecks.cs](IntegrationChecks.cs) runs the existing suites independently so one failure does not suppress other evidence, then calls the existing `SealCliffsMapChecks.BuildNative` once. [IntegrationNative.cs](IntegrationNative.cs) adds the explicit `-capture-integration` mode only to the scratch build.

The original MAP9 checker runs unchanged. It still asserts exactly nine maps and fails immediately against the ten-map tree. This is a **QUESTION for the lead**, not a repaired checker or a claimed pass. The first ability regression also fails at `CrewCardsAbilityChecks.cs:145` because this driver initially ran it before generating the ArtLibrary/deck references. The raw failure is retained; the subsequent full regression passed after library generation, supporting fixture initialization as the cause of that initial failure.

The first standalone built successfully (Unity exit **0**). The combined wrapper exited **1** because it detects the retained initialization NullReferenceException; the driver catches individual suite failures, so its Unity exit is not a clean integration pass. [suites.tsv](suites.tsv) preserves every initial suite result.

The first native launch exited **8** before capturing frames: the harness counted pets immediately after `NewGame` scheduled the previous scenery for deferred destruction. The scratch-only harness now yields one frame before the unchanged exact-one-dog/cat assertions. Original evidence remains in [native-initial.log](native-initial.log), [native-initial-exit.json](native-initial-exit.json) and [native-initial-run.json](native-initial-run.json). This required **two standalone builds and two native launches**, rather than the requested one; no production correction was made. The corrected build passed with wrapper **0**, Unity **0**.

| Check | Result |
| --- | --- |
| Initial ability regression | FAIL: missing generated ArtLibrary station references; retained |
| MAP9 existing checker | FAIL: stale nine-map assertion at `WhaleShelfMapChecks.cs:37`; QUESTION for lead |
| MAP10 existing checker | PASS: 10 maps, 600 directed hull routes, 30 lanes, all three new-ground round trips, anchors, chart purchase and species pools |
| Strike FX existing checker | PASS: 88 assertions; four captures opened |
| Pets existing checker | PASS: 66,902 assertions, 600 simulated seconds, 50 stops and 20 looks; four captures opened |
| Fresh full regression via original `docs/tools/check.ps1` | PASS: wrapper **0**, Unity **0**; 286 ability assertions, 217 tutorial assertions, M2/bite/cage suites |
| Corrected native SessionOnly run | PASS: native process **0**, wrapper **0**; exact-one pets, chart9 purchase, normal departure, cast, bite, accepted hooked strike, return home; eight frames |

The MAP9 failure remains unresolved. MAP10's 600-route sweep includes every Whale shelf hull route, but this does **not** replace the MAP9 checker's skipped map-specific assertions. This delivery is completed verification with outstanding findings, rather than an unconditional integration pass. Route timing warnings from the existing navigation suite remain in the log.

Raw evidence: [initial check log](check-integration-1.log), [corrected build log](check-integration-native-retry.log), [full regression log](check-integration-regression.log), [regression wrapper](regression-wrapper.log), [MAP10 receipt](map10-checks.json), [native log](native.log), [native process exit](native-exit.json), [process exits](process-exits.json).

## Capture review

All captures are kept inside this directory. The editor [strike-fx](strike-fx/) captures show a readable TAP burst and separate mint bobber ring at both sizes; after the accepted strike the TAP cue disappears and a ripple remains. The editor [pets](pets/) captures show the black/white dog on the quay and ginger cat on its supported crate; both closeups were opened.

The native [1440 chart](chart-1440.png) and [844 chart](chart-844.png) were opened individually. Whale shelf and Seal cliffs use distinct pins and clear labels, with no overlap with Kelp bank, Rocky point or Harbour mouth.

**Native pet visibility QUESTION:** the [1440 harbour](harbour-pets-1440.png) and [844 harbour](harbour-pets-844.png) were opened, but the tier-five overview makes the pets too small/occluded to identify confidently. The native exact-one-pet assertions pass, and editor closeups establish their appearance; the native overview alone does not establish pet visual acceptance. No camera or UI changes were made.

The native [bite at 1440](bite-1440.png), [bite at 844](bite-844.png), [strike at 1440](strike-1440.png) and [strike at 844](strike-844.png) were opened individually. At Seal cliffs' arch-pool, the TAP burst and bobber ring are clear at both sizes; the accepted strike removes TAP and shows the ripple around the hooked fish. The nearby arch fills the upper part of this rod-view framing; these captures establish effect visibility, not new terrain or camera acceptance.

[capture-complete.txt](capture-complete.txt) records all eight frames from the successful single continuous session. [native-run.json](native-run.json) records executable/assembly hashes and the source snapshot at launch: all 146 production gameplay C# files matched scratch, with one additive capture fixture. The later original regression-wrapper sync removes that fixture from scratch, but does not change the built executable.

[verification.json](verification.json) records all 16 PNG dimensions and SHA256 values, unchanged production baseline hashes, and 146/146 final gameplay source matches. [review.json](review.json) records the opened images and review findings. No merging/staging conflict was found in the seven shared feature files; the remaining dirty files remain excluded in the inventory.

Final pickup audit: all 16 images were reopened individually, their hashes checked, and every local README evidence link resolved. [closeout.py](closeout.py) exited **0** after writing the missing review and process-exit receipts; [finalize.py](finalize.py) exited **0** with zero production-baseline drift and 146/146 source matches. No Unity checks were repeated during this final report pass. The ownership inventory and shared patch describe the pre-check snapshot; the lead should compare any later peer changes before staging.

## Limits

Scripted SessionOnly native evidence does not establish installed-player, physical-device/touch, listening or Mo's acceptance. The player save and the main Unity project are outside this check. No watchdog files, peer assets or production source were changed.

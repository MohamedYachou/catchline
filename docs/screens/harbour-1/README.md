# HARBOUR-IMPORT-1 native evidence

Codex 1 (Windows app), 2026-10-25. All 18 final PNGs in this directory were opened individually. These are native installed **Test** player GPU captures, including the IMGUI HUD, at **1440×900** and **844×390**. They are clock-controlled SessionOnly fixtures, not a hand-played or physical-touch acceptance run.

The assigned `Catchline-lead-sim` scratch editor rebuilt both Real and Test using `GameBuild.BuildBoth`; the canonical `docs/tools/install-shortcuts.ps1` installed the pair. The exact input hashes are in [build-inputs.json](build-inputs.json), the installation result in [install-result.json](install-result.json), and final installed-file, shortcut, save and frame checks in [verification-receipt.json](verification-receipt.json). Build/check logs remain under `../fish-polish-1/`. No main-project batchmode, save edit or git commit.

## Opened images and findings

Each row covers both `-1440.png` and `-844.png`.

| Stage | Native review |
| --- | --- |
| `harbour-h0` | Both rowboats and the widened slipway render with embedded materials. The player boat is partly behind bottom navigation; this crop cannot establish keel/rail clearance. An earlier build's first desktop frame was black and rejected (`h0-retry.log`). The final build's run starts at 1280×720 to force the first resize; its first desktop frame renders correctly and both final images were reopened. |
| `harbour-h1` | The skiffs sit level, pontoon and gangway read clearly. No obvious floating building in this view. Parts of the berth remain outside the local camera crop. |
| `harbour-h2` | The local boat/buildings render. **Supplies world button overlaps the bottom Market tile on desktop and the Chart tile on phone.** The UI needs an owner fix. |
| `harbour-h3` | The larger boat and quay render. **Supplies overlaps the bottom Market control**, and the world Crew label obscures part of the building entrance/sign. The crop cannot establish all berth clearances. |
| `harbour-h4` | The deep-lines boat renders level; some outer-berth geometry is off-frame. **Supplies overlaps bottom Market navigation.** This is not proof that the east-wall/boat conflict reported by Codex 2 is resolved. |
| `depart-lane` | Harbour, lighthouse, breakwater and the moving boat are visible; progress panel and Faster button remain readable at both sizes. No obvious collision at this sampled moment. |
| `chart-leg` | Painted chart, route dots, Bell buoy label and active marker render. Labels remain readable on phone. **The heading still says “Harbour mouth” during chart transit.** |
| `sea-entry` | Boat, channel markers and dashed route render at sea. **Heading still says “Harbour mouth”** despite the sea-route subtitle. |
| `arrival-crates` | Production homebound trip completes; crates appear on the quay and slipway, Set sail is disabled and desktop says “Sell your haul first”. The compact phone panel omits that explanatory subtitle. Boat remains partly behind bottom navigation. |

The harbour status heading also says “Harbour mouth” while moored. Questions about these headings and overlapping controls were appended to `comms.md` for Claude. Runtime harbour/trip code was left with its owner.

![Harbour tier 2 at phone size: Supplies overlaps the Chart tile](harbour-h2-844.png)

## Imports and checks

[IMPORT.md](IMPORT.md) reports all **30** unchanged FBXs, per-model Unity triangles, metre bounds, root pivots, rotation/scale and materials. Scratch `ArtImport.BuildLibrary` and exact `ArtLibrary.M(name)` lookup passed for all 30. Dimensions match source metrics within 0.002 m; no null/external material references. Four inherited boat variants retain their source root X rotation of 270.0198°, which runtime placement must preserve.

Tier5's Unity 17,006 triangles equal the artist's 17,096 total minus 90 inherited zero-area triangles found by Codex 2 in the exact delivered FBX. Importer removal of degenerates is an evidence-supported inference; no source geometry was changed. See the full import receipt and recorded answer in `comms.md`.

All **21** capture fixtures passed in scratch. The first 16 passes are retained in `stage-check-initial.log`; its initial cage-snag failure was corrected only in the capture fixture. The final five passes and completion/exit 0 are in `../fish-polish-1/harbour-remaining-stage-check.log`. The cage-snag fixture temporarily selects the existing production random branch, then restores the RNG. No minigame rules changed.

Native review then found that the cage-board fixture stopped before the first animal reached the board. Its capture-only delay was increased from 0.4 to 1.1 seconds. The focused [board-stage-check.log](../fish-polish-1/board-stage-check.log) passes both staging and the populated-board assertion, with exit 0. Both players were rebuilt/reinstalled and all 54 native images refreshed after this correction. [build-inputs-initial.json](build-inputs-initial.json) and [check-build-initial.log](../fish-polish-1/check-build-initial.log) retain the earlier build's audit trail; `build-inputs.json` and `../fish-polish-1/check-build.log` describe the final installed pair. Each set's `native-run.json` records the producing executable/assembly hashes and launch time; the final checks reject stale frames or a different installed producer.

## Limits and related evidence

Codex 2's five-tier **proposed** collision-free assembly is separate from Claude's adopted runtime layout. Their report recorded rowboat/ramp and east-wall intersections in the earlier adopted layout. These local native crops cannot disprove that mesh audit; no full-layout collision acceptance is claimed. Lighting/water/materials and HUD in the sampled frames are native evidence, while motion between samples and user input need play review.

The additional homebound/intro/cage/net set is in [overnight/native](../overnight/native/README.md); fishing items 3–5 are in [fish-polish-1](../fish-polish-1/README.md). The final file hashes and exact sizes are in `frames.json`, with the individual review list in `reviewed-images.txt`. The real player's save hash, size and timestamp are compared in `save-before.json` and `save-after.json` by the final delivery check.

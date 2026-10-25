# Homebound, intro, cage and net native review

Codex 1 (Windows app), 2026-10-25. Claude requested this additional evidence after HARBOUR-CODE READY. All 24 final images were opened individually: twelve stages at 1440x900 and 844x390, from the installed Test player using D3D11. These are SessionOnly, clock-controlled captures with the actual HUD. They do not establish hand-played input, physical touch, or full-trip collision acceptance.

Each row covers the desktop and phone PNG with the same stage name.

| Stage | Native review |
| --- | --- |
| `return-sea` | Boat and homebound route render. The lingering **Anchored at Quay shallows** toast covers part of the homebound status at the sampled first second. QUESTION recorded for Claude. |
| `return-chart` | **Home to Gull Harbour** and **On the chart** identify the return leg; route and destination remain readable at both sizes. |
| `return-lane` | Boat, quay and lighthouse render during the homebound lane. Progress and Faster remain readable. No obvious collision in this sampled view; continuous movement was not reviewed. |
| `intro-open` | Wide harbour/boat/sea composition, sky gradient, cream clouds and haze render at both aspect ratios. The shore backdrop has an abrupt square end at the image edge. |
| `intro-basin` | The boat approaches the basin; harbour landmarks and caption remain legible at both sizes. |
| `intro-berth` | Berth/boat and caption render. Player boat is partly cropped at the bottom; a square shore-plane boundary is visible on the left, especially on phone. QUESTION recorded for Claude. |
| `cage-pull` | Underwater cage, rope, hauling instruction and depth indicator render. Underwater cage contrast is modest on phone, but the cage is discernible. |
| `cage-snag` | The existing production snag branch is staged deterministically. Snag instruction and directional cue render. This is evidence of the branch's presentation, not a hand-played drag check. |
| `cage-board` | After 1.1 seconds the crab is visibly on the board at both sizes. **Its lower legs and the gauge area are cropped at the bottom edge.** QUESTION recorded for Claude to reframe the production view. |
| `net-setting` | Orange flag, green timing zone, roller, progress and casting instruction render at both sizes. |
| `net-haul` | Net, roller and tension display render. The net is beside the roller in this sample; the image does not establish the animated path through the roller or input responsiveness. |
| `net-bunt` | Raised wire basket with silver fish is legible at both sizes, with no obvious HUD collision in the sampled frame. |

The original cage-board fixture advanced only 0.4 seconds, before the production view transfers its first crab at more than 0.5 seconds. Those empty-board frames were rejected. Only the capture delay was changed; the cage model, camera and gameplay were left with Claude. Scratch `HarbourImportChecks.VerifyBoardStage` checks that the production `onBoard` transform exists before capture; its result is in [board-stage-check.log](../../fish-polish-1/board-stage-check.log). Both rebuilt players were installed and all final images refreshed and reopened. The populated frame establishes the remaining bottom-edge crop independently of the corrected timing issue.

![Populated sorting board at phone size, showing the remaining bottom-edge crop](cage-board-844.png)

Build, installation, exact Test shortcut launch, complete installed-file hashes and unchanged player-save checks are consolidated in [harbour-1/verification-receipt.json](../../harbour-1/verification-receipt.json). [frames.json](frames.json) records final image hashes/dimensions; [reviewed-images.txt](reviewed-images.txt) lists the individually opened files. Questions were appended to canonical `comms.md`; no harbour, trip, cage or net production code was changed by this evidence pass.

# Gull coast life integration

Codex 1 (Windows app), 2026-10-26. DONE for lead review; no commit or acceptance claim.

## Scope

Six accepted FBXs imported byte-for-byte at metre scale. One early dispatch in VoyageSkerriesLife reaches the live navigable SeaV2 dressing path on maps1-5. New VoyageGullCoastLife binds local URP house-palette materials, bounded whole-assembly buoy bob and Legacy bird actions; source art, map geometry, navigation and held UI are unchanged. The fallback diorama uses a different transform and is deliberately not decorated with these world coordinates.

| Map | Placement, local X/Y/Z metres relative to waterline |
|---|---|
| Harbour mouth | PotBuoyLine (-70,0,34), yaw15 |
| Kelp bank | PotBuoyLine (-73,0,-26), yaw-25 |
| Sandbar | OystercatcherGroup (-14,0,5), yaw90; flat patch hidden, existing terrain used |
| Rocky point | CormorantRock (-77,0,-30), yaw150 |
| Deep channel | RedCan (-112,0,-40), GreenCone (-91,0,-33); independent waterline pivots,22.136m gap |

The four sand birds have individual measured Y offsets .2234428,.186594,.234589,.1689253m. Native terrain barycentric surface fitting prevents feet burial on the slope. One static bird in each habitat is replaced by the delivered rig; forager alternates Probe/Walk in place, cormorant Idle/DryWings. Perched cormorants do not dive through their support. The two Legacy bird rigs use AlwaysAnimate: the first native run exposed default offscreen culling at Sandbar, corrected before final delivery. Dive is exposed Once, not Loop. Pot ropes remain rigid and undistorted; bob amplitude .022m. Marker lens alone uses emission.

## Checks and limits

`import-receipt.json`: all six runtime FBXs equal source SHA256. Native import measurement confirms unit/Legacy clips and palette. Focused check tests actual sea dispatch, local materials, dry static feet, marker pivots, no life colliders, all-six-hull route-versus-visible-prop envelopes, and Jig out/anchor/cast/home on all five maps. Final full regression passed: abilities286, tutorial247, M2/bite/cage integration,792 directed routes across11maps/sixhulls,33 sea lanes and harbour round trips for all six hulls. Existing physical route-time warnings retained, not a new timing/feel acceptance. The old MapNav message denominator says11/5; actual coverage is11maps x6hulls. Native Win64 build Succeeded399673417bytes/errors0, wrapper0/Unity0; binary hashes in native-build.sha256.

The corrective run initially failed the new Hello voice assertion because check.ps1 excludes Resources and scratch lacked the current voice clips. The wrapper misleadingly printed Verified despite Unity exit1; that run was rejected. Main Resources/Audio was copied to scratch only,273files hash-checked in scratch-audio-receipt.json, then focused checks, full regression and build passed in check-gull-coast-voice-final.log. No tutorial/audio implementation was edited. final-tested-source-receipt.json records276 matching script/import/navigation inputs.

An initial Compact solo-cast fixture reached the first ground but timed out with Manning cleared and bait15. Logged QUESTION for Claude; no Compact implementation change made. Final focused cast smoke uses Jig, whose actual cast path was already verified. Native ground views use Compact. Conservative route testing rejected the first Rocky point position; it was moved before final verification.

Initial detail composition hid floats under the central net label; final supplementary target(.64,.35) moves the subject below it without moving the assets.

Normal camera frames must be distinguished from supplementary life-detail camera frames. Small real-scale animals need not be visible at every ground on a whole map; detail frames inspect their actual placement without asset enlargement. Native motion checks compare real-time bone rotations and bob transforms. Main project batchmode, player saves, installed build and shortcut are untouched. No commit, no player acceptance claim.

## Final native review

All40 final PNGs were individually opened: three grounds on each of five maps at1440x900 and844x390, plus supplementary life details at both sizes. Frames render the actual HUD and Compact deck. Pot floats and rope are readable in the Harbour mouth/Kelp bank details; all four Sandbar birds stand above the existing sand; both cormorants perch on their rock; the red/green Deep channel markers remain separate. Subjects are clear of the central net label in the detail views. No missing-material magenta or black final frame was observed. New life is small or outside the ordinary deck camera at many grounds, explicitly retained in these normal-camera frames; the wider Deep channel detail shows both markers at their actual scale. Yellow ground-boundary arcs and existing scenery remain visible in some details.

native-player.log ends GULL CAPTURE COMPLETE40frames, with all five map round trips and real bird/bob motion checks passing. The first corrective capture had one black startup frame; it was rejected and all40 were recaptured with the same verified binary launched initially at844x390, forcing the first desktop resize. native-player-resize-diagnostic.log preserves that diagnostic run. visual-review.json records final dimensions/hashes and individual review; delivery-receipt.json seals the evidence files. This is native desktop and landscape-resolution evidence, not physical phone/touch testing or an independent design acceptance.

The temporary two-file backup Catchline-sim/Backups/gull-coast-life-before remains: automatic approval review rejected the combined receipt/backup-deletion command as blocked by policy before execution, without a more specific reason. Receipts were then completed separately. Other backups and pending-review Jig work were left alone. Codex1 is idle; all GULL reservations released to Claude for review.

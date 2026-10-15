# First-voyage slice — PLAY-001, 2026-10-15

Mo chose clearer actions, satisfying catches and useful early upgrades.

## What changed

- Optional three-fish first-trip goal, with the safe-stow count in the HUD.
- State-aware hints for casting, waiting, striking, carrying and returning.
  Settings can hide hints. Existing first-use wall of text shortened.
- First three landed catches use 4–6 second bite waits and at least a
  1.5-second strike window. The normal upgrade-dependent window resumes after
  that; saved fish-log progress counts. Early strikes still lose bait.
- Portrait catch cards show species, weight, estimated current sale value,
  new species and personal records. Stowing floats +1; selling toasts coins.
- Fish-log portraits and a Market link to the next useful Chandlery upgrade.
- Big cooler costs 60 instead of 200 coins. Seed 7's ten-fish manual-command
  check earns 32 coins (72 total), buying storage with 12 left for supplies.
- Harbour world labels yield to fixed HUD panels instead of covering the goal.
- Session-only preview support: never load, save or delete main-game progress.

## Verification

Unity 6000.3.25f1 on Catchline-sim, never batchmode the main checkout:

- `FirstVoyageChecks.Regression` passed: actual cast/early-strike/recovery,
  catch/carry/stow/return/sell, tutorial timing transition, cooler affordability,
  repeat-purchase rejection and fish-log save round trip.
- Skiff checks passed: refit, models, grid routes, legacy saves, fuel/travel,
  hiring/cap/roles, autonomous fisherman, gill net and carrying backlog.
- Windows standalone build passed. Review uses the actual native HUD, not
  scene-only renders. Manual native review covered menus, casting, nibble/bite
  feedback and return controls; the repeatable catch-loop check is scripted.
- Impeccable's mechanical detector returned no findings for the changed HUD
  targets. Its detector has limited applicability to Unity C#.

Logs: Catchline-sim/Logs/check-first-voyage-regression.log and
check-first-voyage-polished-preview.log. The 2.54-minute checked trip uses
immediate commands and strikes, so it is not a measured human completion time.

## Try it

Run `Catchline-sim/Builds/FirstVoyage/Catchline.exe`. Play → Set sail → Fish.
Wait through nibbles; tap clear water or press Space when the bobber goes under.
Tap Carry after landing. Bring three home, or fill all ten slots. Head home
sells automatically; visit the Chandlery from the Market to buy the cooler.

Preview progress is intentionally temporary. The main Unity scene uses the
normal persistent save. The two existing dirty render-pipeline settings remain
outside this change.

## Remaining

Phone framing was inspected at 844×390, but existing HUD text is too small at
that size. Mobile needs a dedicated layout/type pass, not a readiness claim.
Audio, full title/chart integration and remaining Claude C/D tasks remain.
ART-009 commit f5ce155 is delivered by the WSL artist and queued for runtime
review/integration; it was not merged as part of this first-voyage slice.

Next feedback from Mo: how the first catch feels, whether waiting drags, and
whether the first storage upgrade makes the next trip inviting.

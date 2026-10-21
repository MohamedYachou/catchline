# PACE036 - quicker fish handling, stationary prep crew

Mo's correction supersedes PREP035's per-job station allocation and idle behaviour.

- All deckhands now pick up and release fish at **3x** the previous action speed. Applies to rod catches on every hull and gathering/stowing net catch. Walking speed and captain timings are unchanged. On the Compact/Prep fisher, base handling durations fall from1.4s pickup/3s stow to approximately0.467s/1s, before the usual grade and crew pace multiplier.
- Prep duty assigns one stable standing position per hand (max2). A hand goes to the table once, including when it has no input yet, and waits there. No cosmetic patrol when stock is full, inputs run out or nothing meets the filter. Another hand leaving does not reassign the remaining worker's position.
- Subsequent jobs do not enqueue walking. Reach for the front input, cut on the table, then turn/reach to the box behind. Fish visual moves; feet stay planted. Base cycle:0.15s take +0.9s chum cut or1.1s preparation cut +0.15s place. The existing grade/crew work multiplier applies.
- Chum-to10 priorities, two-worker reservations, input filters, frozen prepared quality/no spoilage, sale premium, weight accounting and safe cancellation remain intact. A hand already carrying a fish when reassigned finishes that delivery before taking its table position.

Verification and delivery evidence will be appended after the isolated checks and native run. No model/UI redesign or real-save change.

## Verification

`docs/tools/check.ps1 -Name pace036 -Method Catchline.EditorTools.HandlingPaceChecks.ValidateAndBuild` exit0: PACE036, PREP035, TIER033 and COMPACT FISHER checks passed; standalone player built. Actual grade1/pace1 elapsed pickup0.468s, release1.002s (2ms sampling), matching base1.4/3 and3xhandling. Station regression checks both workers' planar positions on every tick across8s empty wait,24fish processed to10chum+14prepared, each take/cut/place phase, immediate refill after chum consumption, and remaining worker keeping its spot when the other changes duty. Complete existing freshness/quality/save/target/cancellation, deck/rod/socket/routes/net/dock and prior-hull checks also passed. The existing compact120s trace logged23landed/21held/0lost; this is a regression observation, not a controlled performance comparison.

Native player `pace036-native.log` confirms TEST/no-save mode and normal capture completion. Inspected the new1440x900 and844x390 working-table views plus844order modal: both hands on separate work positions, fish on boards, cutting activity labels, contained/readable HUD. Six screenshots saved under `docs/screens/pace036`; timings/stationary motion are verified by simulation, not inferred from still images. No physical touch/player acceptance claimed.

Updated desktop **Catchline - Tier 4 Test** installation at `Catchline-play/Tier033` with the verified build. EXE/game assembly/resources hashes match scratch build (`installed-build.json`); shortcut still uses `-prepboat-trial -native-display`. No capture process remains. Verified source UTF8/SHA256 receipt is `verified-source.json`. Six temporary source backups were removed after verification. No commit/push and no real-save changes.

# DASH082 — Mo's Management Dashboard

Owner: Codex 2 (WSL CLI). Supersedes the unfinished MANAGEMENT078 layout.

**Current delivery: [DASH087](DASH087.md)** corrects forecast availability, worker
time, raw catch value and costs; moves the actions bottom-right; and integrates
persistent Real. The forced-Tier-5 Test installation and earlier forecast
assumptions below are historical DASH082 behavior, superseded by DASH087.

## Player contract

Management is a button on the right beside the crew rail. Income and Operations
are two tabs of the same screen. The simulation continues while it is open.
The back arrow or Escape returns to fishing. Tap an income source for the catch
mix and a per-100-catch or per-haul estimate. Tap an operations stage or the
recommended fix for its actual queues and crew/processing controls.

DASH1 and DASH2, supplied by Mo, are the visual authority. The originals live
unchanged in `Assets/Resources/ManagementReference/DASH1.png` and `DASH2.png`.
Native UGUI displays the original artwork; live fields cover the example
numbers, graph, clock, status pills, costs, insights and recommendation. Native
geometry draws live round bars, chart strokes and the efficiency ring. No
example numeric value or chart is intended as game data. Dynamic lettering
uses bundled OFL Roboto Condensed regular/bold, with sizes measured in reference
pixels. Static reference lettering and icons retain the original pixels.

The reference composition is 1672 × 941. It scales uniformly inside the safe
area, with the coastal artwork filling surplus space. This preserves the
original proportions on landscape phone, desktop and 4:3 displays. Invisible
hit targets expand to at least 44 physical pixels. Detail views use a readable
native scroll panel rather than shrinking their text with the reference art.

## Real processing pipeline

Hull 0–2: catch lands on deck/baskets → carrying → main hold.

Hull 3–4: catch lands on deck/baskets → carrying to processing input → table
processing → processing output → separate carrying trip → main hold.

Crab recovery now lands on deck beside its buoy access, then uses the same
inbound carrying route. Raw/finished queues are distinct collections outside
`Cooler`, which is now exclusively the main hold. Each queue has actual fish
models at the boat's table input/output. Their combined mass has a finite
buffer budget equal to main-hold capacity. Reserved fish stay in their queue
until the next stage commits; a cancelled carrying/cutting job releases its
claim without deleting or duplicating the fish. Processing visuals hide the
reserved input model while the worker handles it.

Dedicated Prep workers prioritize table work and preserve their positions.
Nets workers prioritize their rig and baskets, then cover hauling during soak;
Fish workers prioritize finished output before gathering loose incoming fish.
Tier 5 retains idle processor fallback. The captain can help prepare queued
input before the hold fills and can help carry finished fish from stage details.
Fish excluded by processing/chum filters wait in input until orders allow them.
Chum consumes input, and its mass is tracked separately for reconciliation.

Returning home cancels jobs and salvages queued raw and prepared fish into any
remaining hold space; excess is recorded as lost. Auto-salvage does not count
as operating throughput. Prepared premium and quality survive the harbour
copy. No existing save schema, fish price, action duration or crew-card ability
was changed.

## Expected income

Income predicts nominal catch worth, independent of spoilage, cooler ownership
and declining market prices. The processing bonus is included on processing
boats, under the stated assumption that their table keeps up. Actual sell
proceeds remain governed by the existing game economy; these are forecasts,
not awarded coins. Player decisions and good fishing can exceed them.

Rod species weights use the location table, hull eligibility, baseline .55 cast
power, and each fisher's currently permitted available bait. Deterministic
128-point specimen integration applies the actual specimen-size transforms and
size premium. Species probabilities sum to one. Detail shows expected counts
and worth per 100 catches. Cycle rates include bait/cast, flight, expected bite
wait with the existing 15-second cap, reel time, upgrades and worker speed.

Net estimates use 128 independently seeded probability samples of the same
weighted, bounded-mass catch procedure, including the residual school-fish
fallback. The live RNG and richness are untouched. Selected shallow/deep gear,
net capacity/refit, location, stock and installed rig count affect the result.
Details show fish and nominal worth per haul. Recovery timing includes the
soak, setting, hauling, estimated travel/handling, and the existing non-Tier-5
crew tear probability. Crab estimates integrate its actual size/value range
and recovery cycle for both traps.

These are supplied-equipment projections, not a full future voyage simulation:
shared captain/crew jobs, servicing faults, supply exhaustion, changing catch
richness and player actions affect realized results. The forecast refreshes
when loadout, bait policy, crew or the richness band changes. The chart records
those forecasts at five-second intervals during this voyage; it invents no
past or future samples. Net values are fixed-seed numerical estimates; rod
probability weights are analytical.

Best Earner uses expected value/minute. Highest Margin uses allocated estimated
costs. Most Stable waits for a minute of actual catch data, then compares the
variation of landed value in six ten-second bins. Empty-data insights say
Measuring instead of naming an unsupported winner.

## Operations metrics

Stages show incoming workload / estimated capacity in fish/minute, with actual
completion rates available in stage details. Fishing uses expected catch rate;
hauling learns fish per worker busy minute from real completed jobs. Inbound
and outbound share the available crew budget according to observed work time.
Processing capacity uses actual assigned table worker speeds and the unchanged
4.8-second preparation cycle. Mean fish weight is not treated as a guarantee
that all stages have the same work cost. Shared-duty hauling remains an estimate.

For downstream stages, green means below 80%; orange means 80–100%; red means excess incoming work or
a blocked queue/hold. Fishing compares actual production with a probability forecast, so beating that estimate stays healthy; a physically blocked intake alerts. Text labels accompany color. No-capacity learning is
neutral. Boats without a processing table show Not fitted and explain the
bypass. Efficiency compares actual stored output with the measured limiting
stage, and waits for hauling samples before asserting a percentage.

Costs allocate existing crew contract fees per contracted voyage over estimated
trip duration, current bait replacement cost, net uses/expected replacement,
and powered-boat fuel. Shared transport wages split between inbound/outbound.
These are explanatory estimates; opening the dashboard never charges money.
Net profit is expected nominal value minus allocated estimated operating cost.

## Verification

Evidence and native captures are under `docs/screens/dash082/`.
The full isolated suite passed: pipeline cancellation/restart/outbound storage,
small-boat bypass, probability normalization/RNG isolation/nominal value,
Management event accounting and 180-second mass reconciliation, stationary
handling, prep orders/save, physical Prep/Compact hulls, rarity filters, both net
modules, balance/bait/captain rules, net minigame, Tier 5 and PTS water. Full
regression evidence is `integrated-check.log`; `unity-check.log` is the final
focused run including actor-weighted 100-catch estimates, manual captain hauling,
actual callbacks and original imported raster dimensions.

The final standalone completed 25 native captures with no listed runtime
exceptions, at 1672x941, 1440x900, 844x390 and 1024x768. Native review covered
both tabs, entry, startup, method details, blocked/full states and smaller-boat
bypass. Six static comparison regions (title, boat icon, tabs in both references)
match the supplied references at 100% exact RGB pixels at 1672x941;
`reference-pixels.json` contains the measurements. The whole dynamic screen is
not compared as identical: actual numbers, labels, statuses and graphs replace
example content. Source PNG SHA256 equals Mo's supplied originals.

Installed: `C:/Users/momoy/Projects/Catchline-play/Dash082/Test/Catchline.exe`.
Desktop shortcut: **Catchline - DASH Management Test**, with arguments
`-tier5-trial -native-display`. It opens an isolated playable Tier 5 session.
Tap **Management** on the right beside the crew rail. The source is also in the
main Unity project for subsequent builds.

Installation compared 34 source/resource files with the tested scratch project,
verified all 174 shipping files after copying, read back the new shortcut, and
confirmed the existing real save's fingerprint was unchanged. Receipt:
`installed-build.json`. Existing installed Real/Tier 5 shortcuts were not
retargeted. No commit made; unrelated uncommitted work preserved. Temporary
pre-change backups removed after verification.

Limits: capacity, cost and future-income figures remain estimates under shared
jobs; baseline catch projections can exceed realized income when downstream
work is blocked. Existing native UGUI has no screen-reader bridge, and physical
touch hardware is not tested. Review was performed by Codex 2 from actual native
frames and source; no independent agent critique is claimed.

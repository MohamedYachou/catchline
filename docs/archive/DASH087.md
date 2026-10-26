# DASH087 — boat-specific Management, verified math and Real integration

Crew-card implementation pickup: [CREW-MANAGEMENT-INTEGRATION.md](CREW-MANAGEMENT-INTEGRATION.md).
It maps the current code and remaining shared-rule, batch, payroll and cache work.
Selected cards are not yet implemented; future effects must change actual jobs
and their forecasts together. Latest crew/electrical decisions remain canonical.

Owner: Codex 2 (WSL CLI). Follow-up to DASH082; Mo accepts the dashboard artwork.

## Corrected behavior

The previous DASH Management Test shortcut forced `-tier5-trial`, so it showed
Tier 5 equipment rather than the player's saved rowboat. The new Test starts an
isolated fresh rowboat. The Real build loads existing persistent progress. Both
launch normally with `-native-display`, without a forced hull.

Forecasts now inspect actual fitted gear and working operators. Hulls 0–3 have
no crab traps and show **No traps fitted**, zero value, zero share and no crab
catch mix. Tier 5 has two actual traps; their forecast requires available recovery
workers and excludes broken/deactivated traps. Fitted nets without an assigned
Nets worker or an active captain net job show **Assign Nets or work a net**, with
zero income/minute. Their per-haul potential remains available in details.

The captain has one activity budget, and automatic fishing/recovering traps
shares a finite worker-time budget. One Nets worker does not independently run
two rigs at full rate. Duty, equipment, supplies, damage, hull and current captain
job changes invalidate the forecast. A full hold reports zero future catch
income. Percentage rounding allocates integer shares totaling 100% when there
is positive forecast income; absent methods always receive 0%.

Management is in the bottom-right corner. Boat / duties, formerly bottom-left,
is immediately to its left in the same bottom-right cluster. Home, Crew duties
and Prep orders use separate nonoverlapping footer positions. Fishing hints
leave this cluster clear at desktop and landscape-phone sizes.

## Meaning of the estimates

Expected income is the nominal raw worth of fish, using their actual species
probabilities, specimen sizes and rounded size-dependent prices. It excludes
freshness loss, market depletion and an unearned processing bonus. Real sale
proceeds still follow the existing economy. Processing actually completed can
add value; it is not silently credited to every predicted catch.

Rod details show expected counts and worth per 100 catches, weighted by each
operator's expected catch rate. The baseline cast power is .55; selected available
bait, hull/location eligibility, specimen-size transforms, capped bite waits,
strike chance, actual worker speed, reel upgrade and damage affect the estimate.
512-point numerical integration matches the actual raw-value and timing rules.
Manual captain carrying adds estimated handling and path time when no automatic
hauler is available. Good play can exceed this baseline.

Net details show expected fish and worth per haul. Gameplay and prediction use
the same extracted, unchanged bounded-mass net sampler. Forecasting uses 256
independent deterministic samples and never consumes gameplay RNG. Installed
rigs, selected shallow/deep net, stock, actual operators, soak, setting/recovery,
handling, route time and the existing crew tear/fault probabilities affect rates.
The runtime sampler's catches and subsequent RNG sequence remain unchanged.

Crab projections use the real size/value range, equipment soak efficiency,
recovery/fault rules and estimated round-trip path time. Rod and trap recovery
cannot each spend the same worker's full minute. Actual fishing, carrying,
processing and outbound-storage rates remain separate in Operations, with real
queue/event accounting from DASH082. Small boats bypass the processing stages.

Costs estimate supplies, powered-boat fuel and existing prepaid crew contract
fees per contracted voyage. Fees amortize over projected total voyage time,
including elapsed fishing, return travel and remaining storage/fuel-limited time;
a stalled powered boat cannot invent an enormous fill time to make wages vanish.
Costs refresh as fuel/time/hold change. Shared transport fees split between
inbound and outbound; no money is charged by opening Management.

These are ongoing supplied-work projections, not a simulation of every future
crew interruption, repair, bait exhaustion, changing grounds or player decision.
Forecast catch worth can exceed actual stored throughput when downstream stages
are overloaded; that is what the separate bottleneck display helps identify.

## Verification

Evidence lives in `docs/screens/dash087/`; scripts are in `docs/tools/dash087-*.ps1`.
Independent checks compare 80 hull/location/bait cases against 20,000 actual
rod rolls each (1.6 million total), including species probabilities, mean weight
and actual nominal value. A frozen pre-change net oracle verifies 120 seeded
catch lists, bounded mass and the next RNG value. Forecasting leaves gameplay
money, bait, richness and RNG unchanged.

Cross-hull tests switch from Tier 5 down to the rowboat, checking actual fitted
gear, absent/unoperated/broken methods, shared work budgets, duty/cache updates,
zero full-hold income, bounded cost allocation and exact percentage totals.
Footer bounds/nonoverlap are checked at 1672×941, 1440×900, 1024×768 and 844×390.
A controlled real recovery job verifies crab identity and conserved mass through
physical deck pickup, table input, processing, separate outbound carrying and
main-hold storage. The older Tier 5 stress check now verifies crab landings
rather than assuming they bypass the processing backlog by a fixed deadline.

The complete existing dashboard/handling/orders/save/physical-hull/net/balance/
Tier 5/water regression suite accompanies these checks. Native verification uses
actual standalone Test and persistent Real players, not scene-only screenshots.
The Real probe loads a copy of the player's save into a gated temporary directory,
departs, opens the dashboard, returns and saves there. The original player save
is fingerprinted before and after. Normal Real launches use the ordinary save.

Native capture covers entry, Income and Operations for all five hulls at
1440×900 and 844×390, plus entry/Income from the copied actual Real save: 34 frames.
Accepted DASH1/DASH2 artwork stays unchanged; only live values, availability
labels, boat identification and footer placement change. See DASH082 for the
original static reference-pixel proof; full dynamic-screen equality is not claimed.
Native UGUI has no screen-reader bridge; physical-touch hardware is untested.

## Installation

Installed and verified after the final exact-source suite and native Real probe.
Compared 34 source/resource files with the tested scratch project and all
174 shipping files per build after copying. Shortcut targets/arguments
passed readback, and the original player save fingerprint remained unchanged.
Receipt: `docs/screens/dash087/installed-build.json`. Versioned directories are
`C:/Users/momoy/Projects/Catchline-play/Dash087/Real` and `Dash087/Test`.
Desktop **Catchline - Real Game** uses persistent Real; **Catchline - DASH
Management Test** uses isolated Test. Previous versioned builds remain available.
No save-schema or gameplay balancing change, no crew-card implementation, no
commit. Unrelated working-tree changes are preserved.

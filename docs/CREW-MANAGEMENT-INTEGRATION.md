# Crew cards ↔ Tier 5 ↔ Management integration handoff

CREW096 · Codex 2 (WSL CLI) · 18 October 2026.

This is the implementation handoff for future crew cards. It documents current
code and the required connections; it does **not** implement cards or claim that
all future abilities already update the dashboard automatically. Read the latest
canonical [crew decisions](CREW-CARDS-DESIGN.md) before choosing behavior or values.

## Current delivery and authority

- Tier 5 is saved Hull **4**, the 8.5 × 4.2 m Buoy fisher, captain plus six hired
  crew. Rod-heavy has four rods/one net; net-heavy has two rods/two nets. Both
  have two actual crab stations and processing. Earlier hull IDs remain intact.
- Hulls 0–2: landing → carrying → main hold. Hulls 3–4: landing → carrying to
  processing input → preparation → processing output → separate carrying → hold.
  Crabs land on deck and follow this route; they never bypass the table on Tier 5.
- DASH1/DASH2 are the accepted Income/Operations art. Management sits bottom-right;
  Boat / duties sits immediately left. Keep the existing interactive tabs/details.
- All five active Desktop launchers use verified Dash087 players: Real Game uses
  persistent Real; DASH Management Test and Tier 3/4/5 use isolated Test with
  their original trial flags. See [DASH092](DASH092.md), including the launcher table.
- Existing crew contracts/grade speeds remain runtime behavior. Collected cards,
  levels, automatic abilities, team passives and per-voyage card wages remain
  future implementation. Do not infer that design selection equals shipped code.
- Latest approved design (CREW094/095): Engineer maintenance applies **only to
  electrical units**, not bare rods/nets/cages; normal nets have unlimited uses,
  deep nets have three uses. The shipped Tier 5 still has legacy eight-slot gear
  condition/fault logic. Replace that old maintenance model when implementing
  the approved redesign, together with its forecasts/UI/save compatibility.
  Future powered-machine families and tier order remain proposals in
  [FUTURE-MACHINERY-DESIGN.md](FUTURE-MACHINERY-DESIGN.md).

Installed/native evidence: [DASH087](DASH087.md), [DASH092](DASH092.md) and their
`docs/screens/` receipts. The latest diary is [comms.md](../comms.md). This handoff
adds no runtime verification beyond those already recorded deliveries.

## One calculation path for gameplay and predictions

Resolve card effects in shared gameplay calculations, then make jobs and
Management consume those same results. Never apply a bonus only to dashboard
labels, or copy an ability's formula into separate gameplay and UI branches.
An effective work calculation needs the actor/card ID and level, current duty,
method/rig, target fish or batch, installed equipment, applicable team passives
and temporary state. Return the actual permitted work, duration, yield, load,
supply cost and worker occupation for that context. These are requirements for
the future implementation, not names of an existing API.

Keep scope explicit: personal effects act on that worker's job; team effects
act on eligible workers/jobs once. Level, stacking, exclusions, rounding and
wage values follow the canonical decisions; unresolved values remain open.
A processing-only bonus must not speed walking or fishing simply because
`Person.Speed` currently affects both movement and busy timers.

| Effect or ability | Existing gameplay location | Management connection required |
|---|---|---|
| Role/level speed, walking vs job speed | `DeckActors.cs` (`Person.Tick`), `VoyageGame.cs` (`WorkMult`, `FishHandlingSeconds`) | Use effective speed for that action in forecasts; relearn hauling pace when effective configuration changes. |
| Rod catch weights, specimen sizes, reel/strike changes, extra hooked fish | `GameState.cs` (`RollFish`), `DeckActors.cs` rod state machine, `VoyageGame.cs` landing | Keep `CatchExpectation.Rod` and cycle timing aligned with real rolls; per-100 counts/value, incoming workload and operator time must include actual extra fish. |
| Net capacity, simultaneous/alternating jobs, recovery, deep-net use saving | `VoyageNet.cs`, `VoyageSecondNetModule.cs`, `VoyageNetUnload.cs`, net loadout/state | Feed shared capacity/yield/timing/use rules into `CatchExpectation.RollNet` and `UpdateManagementForecast`; keep independent rig ownership and finite worker time. |
| Cage tending/recovery and any extra cage work | `VoyageTier5.cs` (`TryBuoyWork` and buoy ticking) | Count real fitted stations and real tasks; charge tending/recovery/travel against shared fishing-worker time. No traps on a smaller boat means zero crab output. |
| Pickup/stow speed, loaded walking, carry weight and whole-station loads | `VoyageGame.cs`, `VoyageNetUnload.cs`, `VoyageProcessingPipeline.cs` | Count carried fish/mass and worker occupation separately from trips; preserve inbound/outbound budgets and actual destination capacity. |
| Processing speed, small-fish batches, large-fish cutting, bulk batches | `VoyagePrepOrders.cs` (`TryPrepWork`), `VoyageCaptainPrep.cs`, `VoyageProcessingPipeline.cs` | Replace single-fish capacity formulas in both `ReportManagement` and `UpdateForecastCosts` with the same batch/job rules used by workers. |
| Electrical maintenance and recovery while a repair continues | `GameStateTier5.cs`, `VoyageTier5.cs` (`EngineerThink`, service/fault logic), future actual machine state | Remove legacy manual-gear wear assumptions from forecast availability, failure/efficiency and Boat / duties together; reflect actual machine uptime and busy engineers without granting free extra labor. |
| Per-voyage card wages, supplies, resulting sale value | `GameState.cs`, crew lifecycle, net-use charging, `VoyageStorage.cs` | Replace legacy `Fee / ContractVoyages` cost allocation with actual agreed card wage policy; use raw catch worth for Income and actual completed preparation/sale rules where appropriate. |

Source locations above are under `Assets/Scripts/Game/`. Main readers are
`VoyageManagementForecast.cs`, `VoyageManagement.cs`, `CatchExpectation.cs` and
`FlowTelemetry.cs`. `VoyageProcessingPipeline.cs` owns the separate queues and
outbound claims. No new station or machine is implied by this table.

## Known gaps to address when cards are implemented

1. **Processing capacity is currently one fish per 4.8 base work seconds.**
   `TryPrepWork` currently takes .15 input + 4.5 preparation + .15 output, scaled
   by the worker's speed and global work multiplier. `ReportManagement` and
   `UpdateForecastCosts` each contain a separate `60 / 4.8` estimate. Both must
   consume shared batch-aware duration/throughput rather than retain that number
   when a card changes the real job. Station limits, eligibility and output space
   still constrain work; two stations do not mean two free workers.
2. **Events currently assume one specimen per `Flow.Record`.** `CountRate` counts
   entries, so recording a multi-fish batch as one event would undercount fish.
   Either record each actual specimen exactly once at its committed stage
   transition, or add an explicit specimen count to the event format and update
   every consumer. Do not fabricate aggregated fish or count claims as completions.
   `CarrySamples`, `OutputSamples` and busy-time learning must remain consistent
   with the chosen units; distinguish trips, fish, kilograms and worker-seconds.
3. **Effect changes need explicit invalidation.** The forecast signature includes
   current worker speed, duty, gear, bait, hull, supplies and legacy damage, but
   has no card ID/level/team-effect revision. `flowCrewSignature` currently checks
   names/duties/hull/net layout and misses speed/ability changes. Add a shared
   effective-configuration revision or equivalent complete signature to both.
   Invalidate predictions and call `Flow.ResetCarryLearning` when hauling ability
   changes; do not erase actual catch events or rewrite earlier chart samples.
4. **Legacy payroll and maintenance are not card-ready rules.** New wages,
   electrical-only maintenance, full repair behavior and the selected repair
   exception need real implementations first. Do not reinterpret old rod-condition
   arrays as approved future electrical machines, or count deep-net uses as wear.
5. **Current forecasts are supplied-work estimates.** Stateful chains, tending,
   alternating nets, finite buffs or special routing require explicit expected
   work/uptime models. If a new ability lacks a defensible estimate, show a clear
   Measuring/estimate explanation and real observed output rather than silently
   applying the old formula or inventing guaranteed capacity.

## Selected abilities with special integration consequences

These examples point to existing decisions, not new card packages or approval:

- Batch Cutter and Heavy Cutter require eligible-fish/batch-specific work time;
  a single universal processing multiplier cannot describe both correctly.
- Heavy Lifter requires a distinction between base walking and loaded walking,
  actual carried mass and any slowdown condition. Changing `Person.Speed` alone
  would incorrectly change unrelated work.
- Power Lifter's whole-station loads and heaviest eligible-load priority need
  safe reservation/preemption and finite destinations. It does not create more
  hold space or duplicate another carrier's committed load. Current whole-net
  basket carrying already ignores weight, so normal bounded-load mechanics must
  be defined to make the personal exception meaningful; see canonical section 16.
- Bulk Processor uses whole fish and a **strictly above 5 kg threshold**, not a
  hard 5 kg cap. A single fish over 5 kg is alone; the final fish is the smallest
  available one that crosses the threshold. If available input totals 5 kg or less,
  start processing it immediately, with no batching wait. Preserve Mo's 4.9+4.9
  and 4.9+0.5 examples. Intermediate selection details, timing, growth and team
  passives remain governed by canonical section 17; do not invent unresolved rules.
- Deep-Net Saver changes actual use consumption as well as expected supply costs;
  successful personal deep-net hauls and failed hauls must follow their distinct
  canonical rules. A personal saving must not automatically apply to another rig.
- Engineer cards must be reconciled with the latest electrical-only scope before
  forecasts are extended. Do not implement superseded rod/net/cage wear packages.

## Accounting and presentation invariants

Keep original fish identities, weights, nominal values and preparation flags
through claims, batches and queues. Cancellation or safe preemption releases
uncommitted claims; already carried/processed work commits once. Input, output,
carried cargo, hold, chum and explicit loss reconcile with landed mass. A batch
finishing creates one completion per real fish, not one fictitious fish with a
new size-based value. Separate preparation and outbound carrying remain visible.

Income is expected **raw nominal catch worth**, not promised sale revenue or
stored output. Do not add a processing premium to every forecast catch merely
because a processor card exists. Per-100/per-haul details, value/minute, shares,
trend, margins and stage costs must derive from the same effective calculation.
Zero absent/unoperated gear stays zero; positive shares total 100%; empty income
has zero shares. Preserve worker-time budgets across rods/traps/rigs/carrying.

Operations retains actual completed rates, estimated capacity, real queues and
text-labeled green below 80%, orange 80–100%, red excess demand/blocked stages.
Beating a rod probability forecast is good play, not automatically a bottleneck.
A faster fisher can move the bottleneck downstream; improving only the fishing
bar while leaving carrying/processing unchanged is a valid consequence.
Keep the accepted art and fit explanatory ability details into existing panels.

## Future implementation pickup and acceptance

A. Read latest `comms.md`, canonical crew/machinery decisions and this handoff.
Confirm which card packages/levels/wages/stacking are actually selected. Preserve
legacy saves; decide migration explicitly before replacing contracts or gear state.

B. Implement shared effective rules and real worker jobs first, with no dashboard
side effects on RNG, inventory, money, task ownership or card state. Wire all
forecast/cost/capacity readers to those rules in the same change. Track actual
stage commits and worker occupation; add complete effect-cache invalidation.

C. Check neutral/card-off behavior against current baselines, then each personal
and team effect on its actual eligible actor/job. Verify equip/remove/level/duty
changes, source buffs ending, batch overshoot/partial input, cancellation,
preemption, original fish value/mass, two-rig budgets, absent gear, supply use,
actual wages and processing/hauling capacity. Compare probability-changing cards
with real rolls, not only a duplicated formula. Compare capacity-changing cards
with completed work under controlled queues. Old learned hauling capacity must
not remain falsely green after a card is removed.

D. Run isolated checks via `docs/tools/check.ps1` / Catchline-sim. Extend
`DashboardMathChecks.cs`, `DashboardChecks.cs`, `ManagementChecks.cs` and relevant
actual job tests as needed. Do not batch the main project. Rebuild persistent
Real plus isolated Test, verify the changed cards in native Income/Operations
at desktop/phone sizes, then update **every active launcher**, preserving trial
flags. DASH092's sync script is pinned to the Dash087 receipt; a new card build
must update the verified version/receipt input rather than accidentally pointing
shortcuts back to Dash087. Preserve actual player saves during verification.

E. Record source/runtime/native/install evidence and release paths in comms.
A compilation pass or selected card design alone is not complete integration.

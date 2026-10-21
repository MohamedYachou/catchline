# TIER5-102 — Astra research before the question gate

Owner: Codex 2 (WSL CLI) / Astra child. Date: 20 October 2026.
Status: research and preliminary questions only. No 30-card roster, accepted rebalance, gameplay implementation, new build or fresh runtime acceptance. Next phase requires Mo's answers and explicit greenlight through the lead.

## Authority and reading

Read global/project instructions, governance/role guidance, CONTINUATION and active playability plan; the entire 1,105-line CREW-CARDS-DESIGN including original options and later overrides; original crew-decision diary sequence CREW053–099 (not just the final canonical summary), relevant earlier crew availability/progression/bait/processing decisions, Tier5 and Management history; FUTURE-MACHINERY-DESIGN, withdrawn ENGINEER-OPTIONS097, CREW-MANAGEMENT-INTEGRATION, GAMEPLAY current overrides, TIER5-INTEGRATION071, DASH087 and DASH092. The project is absent from the governance project registry; use the established miscellaneous logging fallback.

No external-game mechanics are asserted here. Local code supplies the economy facts; historical manufacturer references in the machinery documents are not independently reverified or adopted as design authority. This is game-system research, not a visual/UI implementation pass.

Latest Mo instruction and lead BRIEF override older notes. In particular, the old prohibition on *inventing existing* deep-line equipment does not forbid the new explicitly requested deep-line proposal. Old machinery ladders, Engineer-dependent manual gear and crew-replacing machines are superseded. Sol's new side-net preview relocation is not current shipped geometry.

## What Mo was trying to achieve

MGMT052/CREW053–067: boats felt similar and full crews left too little meaningful captain work. The aim is flexible method builds, visible queues, persistent crew identities and a real reason to change staffing/equipment. Equal base speed for a role/level; rarity comes from skills, not an invisible base-stat advantage. Crew cards and levels persist; deployed crew cost wages per voyage. Named duplicates cannot deploy together. Levels follow a fixed path; exact levels, acquisition and wage curves remain open.

CREW064–067: adding a passive to a blue-sized personal burst did not make a purple compelling. Purple/gold should support a recognizable sustained method/team strategy. Extra rods that displace other fishers, bait/cloud/feeding-area gimmicks and ability-reset loops were rejected. Small blue periodic effects remain liked; blues need not dominate endgame.

CREW075–081: simple rerolls, cash multipliers and erasing friction did not make a legendary interesting. Back-to-Back was selected over Split Haul because it changes when a real net can restart. Cage Foreman's genuinely new tending assignment was expressly liked. Strong intake should produce hauling/processing/storage demand; successful support is allowed to solve it. Do not create compulsory failure, arbitrary penalties or a useless operator job just to justify a card.

CREW083–089: two processing purples were requested. Heavy Cutter must work on the first lone big fish, rather than needing a big-fish queue/streak. Power Lifter is Mo's custom one-station arbitrary-weight carry rule, with no invented slowdown. Bulk Processor uses whole fish and immediate partial batches, not wait-to-fill or a hard 5kg cap.

CREW094–099: no engineering wear on manual tackle; normal nets unlimited uses, deep nets three uses. Electrical reels/haulers, robotic crew replacement and live-tank upkeep as the central new progression were rejected. Later machinery should unlock additional human operations, not replace fishers/hands. Those future diver/crane/spearfishing directions do not authorize new Tier5 roles.

## Preserved roster starting point

This is the existing 13-fisher/10-deckhand working set, not 23 fully finalized packages. Latest authorized expansion is 15+15, each 7 blue / 4 purple / 4 gold. That creates seven additional slots: Fisher +1 purple/+1 gold; Deckhand +2 blue/+1 purple/+2 gold. No existing selected blue needs deletion to hit 30.

| Existing identity | Recorded selection/status |
|---|---|
| F01 Strong Start | First successful personal rod cast each voyage lands 3 total fish. |
| F02 First Set | First personal net deployment each voyage has half soak duration. |
| F03 Fast Bite | Every third rod cast has half bite wait. |
| F04 Loaded Net | Every third personal net deployment gains 25% catch capacity for that haul. |
| F05 Quick Soak | Every third personal cage deployment has half soak time; map reset attribution explicitly. |
| F06 Quick Retrieve | Every third personal longline retrieval has half retrieval time. Previously future-dependent; proposed fit to new deep lines must be explicit. |
| F07 Quick Reset | After third completed personal fishing cycle, NEXT setup has half duration. |
| F08 Deep-Net Saver | Successful personal deep-net haul spends no use; failures spend one. Team deep-net capacity +15%. |
| F09 Rod Leader | While working rods, staffed rods have 25% less bite wait; team rod reeling takes 20% less time. Explicit team-active exception. |
| F10 Heavy Cages | Personal hauls +50% catch mass; team cage soak -15%. Actual legal specimen composition still open. |
| Back-to-Back Netter | Selected finite two-haul basket/redeploy-before-unloaded capability; team soak -20%, haul rate +20%. Old manual wear surcharge withdrawn by electrical-only direction. |
| Twin-Hook Specialist | Unselected prototype: two independent hook waits on own rod, sequential retrieval. Not an approved replacement/doubled yield. |
| Cage Foreman | Tending capability endorsed. Proposed tending rate and remaining passives not finalized. Tenders occupy actual workers. |
| D01 Quick Hands | Every third loose pickup takes half pickup time. |
| D02 Deck Runner | First three loaded trips each voyage walk 25% faster. |
| D03 Quick Stow | Every third delivery takes half stow time. |
| D04 Basket Hand | Every third basket trip +25% carrying allowance; baseline carrying allowance not yet defined. |
| D05 Prep Hand | Every third processed fish takes half processing time. |
| D06 Batch Cutter | Three small fish in processing time for two; team small-fish processing rate +15%. Eligibility/fallback details need specification. |
| D07 Heavy Cutter | Personal large-fish processing takes half time, even one fish; team large-fish processing rate +15%. |
| D08 Heavy Lifter | Twice normal weight allowance; 20% slower while exceeding normal allowance; team loaded walking +15%. Selected tradeoff, not permission to add arbitrary penalties elsewhere. |
| D09 Power Lifter | Remaining eligible contents of ONE station in one trip regardless of weight; heaviest reachable station priority, safe preemption, no stealing carried cargo. Full remaining skill package open. |
| D10 Bulk Processor | Heaviest starter; single >5kg fish alone, otherwise whole-fish batch strictly above5kg with smallest crossing finisher. If total available <=5kg, process immediately. One ordinary cycle per batch remains timing proposal; passives open. |

D10 examples must survive: 4.9+4.9 →9.8 when only those exist; 4.9+4.8+0.5 →5.4, leaving4.8. Exact5 alone processes now; with additional eligible fish available, finish above5. Multi-small-fish intermediate fill order remains a derived proposal. No trimming/specimen rerolls/value changes. D09's load is a pickup-time snapshot, excludes already carried fish and cannot merge incompatible destinations.

All abilities automatic. Blue1 active; purple1 active+1 passive; gold2 active+1 passive or1 active+2 passives. Latest personal-signature/thematic same-role support preference must retain F09's explicitly chosen team-active exception. Any reevaluation should show original, proposed change and reason side by side; an unselected alternative must never become a historical selection.

## Source audit: current behavior, not the proposed redesign

All source references below are in `Assets/Scripts/Game/`.

### Fish, bait, probabilities and value

`GameData.cs`, `GameState.RollFish`, `CatchExpectation.cs`:
- Thirty current species IDs; Crab29 is cage-only. Five local ground tables and hull eligibility gates are real. Catch rarity/color is not crew rarity.
- Rod species weight is local table weight × lerp(1−0.7h,1+1.6h,p), with h species heaviness and p clamped catch power. Fisher casts use0.55; squid adds0.4 to catch power. Bite wait still uses original cast power.
- Specimen fraction is U^(1.5−p); squid remaps to0.35–1, chum0.75–1. Squid multiplies small-h weights by0.04 and others by0.65+1.6h; chum multiplies by0.01+8h². Scraps ignore the local table and yield 50/50 herring/mackerel in their bottom20% size ranges.
- Nominal raw value rounds kg × base price/kg × (1+0.5×species-relative specimen size), minimum1. Actual sale also uses market and freshness; prepared Tier5 fish get1.5×, earlier/legacy prepared fish1.25×. Prepared quality freezes existing quality, not automatically restored freshness.
- Deep-channel normal pool: pollock25, cod40, conger25, turbot10, tuna6, monkfish5 plus rare/legendary low weights. New deep lines can bias this existing eligible pool without inventing species or importing another ground. The exact bias remains a proposal.
- `GameStateCrewBait.cs` selects permitted available chum first, then squid/worms according to preference/stock, then free scraps if permitted. Every real bait action consumes one selected portion. Worm prices1 or0.8 coins/unit (standard/bulk); squid3 or2.4. Crew permissions exist already.
- `VoyagePrepOrders.cs` chum consumes an actual input fish, produces ceil(kg/0.5) clipped to target, and costs3.5+0.3 base work seconds. However Tier5 explicitly disables chum production, including the high-rarity preparation by-product, and voyage start resets chum. Mandatory chum-fed deep lines therefore need an explicit supply redesign; cannot assume today's boat can feed them.
- Freshness:60s grace, then7%/min to60% floor without ice; prepared fish preserve achieved quality. Current higher-hull depletion is0.0035×landed kg down to0.3 richness; returns recover richness. Market changes on actual sale. These need voyage-level modeling, not nominal-price-only profit claims.

### Real operation timing and occupation

`DeckActors.cs`, `VoyageGame.cs`, `VoyageTier5.cs`, `VoyageNet.cs`:
- Global work factor0.7. Legacy grade speeds1/1.5/2 alter both action time and walking; this is not the future equal-role/level rarity model. Normal walking2.2×speed×0.7 m/s; exact routed distance matters.
- Rod bait1.2 and cast0.45 base work seconds, flight0.6 wallseconds, bite min(15,(5+4U+5p)×spotWait/max(0.3,richness)); reeling clamp(0.8+0.3kg,0.8,2.5) divided by worker speed/global factor/reel upgrade/legacy gear efficiency. Biological wait is not divided by actor speed.
- Tier5 staffed strikes currently succeed, followed by legacy equipment-fault risk. Earlier hulls use grade strike probabilities80/85/90%. Unattended self-hook/retry is separate; do not silently apply guaranteed staffed success while worker is elsewhere.
- Current FisherThink first claims a rod; without a free rod it returns before buoy recovery. It can recover cages in suitable rod gaps. Desired independent method permissions/general fisher dispatcher therefore require new behavior, not merely renaming Nets deckhand duty.
- Each current cage soaks65s (legacy efficiency modifies progress), then requires2 base work seconds recovery plus travel. One uniform0.5–1.8kg crab lands onto deck and follows both haul stages. No current bait cost per cage. Tending and extra catch mass are unimplemented card mechanics.
- Nets: shallow40s/deep60s soak; worker set2/retrieve5 base work seconds plus travel. Current Nets worker is a deckhand; desired fisher migration must separate fishing retrieval from downstream transport. During soak current net hands can help carry/bait, so do not count a freed Engineer berth AND another fully free net worker without reconstructing their actual workload.
- Current primary/secondary assignments and global net-unloader ownership must be replaced/extended for independent fisher operation, bounded carrier loads and Back-to-Back queues. Current operator begins unloading after haul; new role boundary must hand off physical catch.

### Net load and consumption

`GameStateProgression.cs`, `VoyageNetLoadout.cs`, `CatchExpectation.RollNet`:
- Tier5 net hard mass budget30kg, upgraded44kg. Actual target = capacity×lerp(0.85,1,richness); at minimum richness0.3 this is89.5% capacity, not30%.
- Shallow pool is local herring/mackerel/whiting/pollock at5–25% of species weight span. Deep first uses all local eligible fish with weight factor0.08+6h² and65–100% specimen span; remaining budget can fall back to small-school fish. It packs within remaining mass, never imports absent species. At Deep channel shallow fish are pollock, so “small net fish” does not always mean herring-sized cargo.
- Successful deep haul spends one of3uses, each purchased net100coins; failed deep haul also spends one. Normal net has no successful-use decrement, but legacy tear failures can destroy its stock item (30coin replacement). Selected normal-unlimited/manual-wearless direction must be distinguished from legacy failures; future model should not restore arbitrary tear tax after removing engineering.
- Higher net mass may mean more fish OR heavier fish. Downstream demand needs both individual count and kg, not a universal kg/time formula.

### Carrying, preparation, buffers and losses

`VoyageNetUnload.cs`, `VoyageProcessingPipeline.cs`, `VoyagePrepOrders.cs`, `VoyageStorage.cs`:
- Ordinary loose and finished-output carrying currently takes one whole fish regardless of weight. Net inbound carrying claims an entire eligible basket in one batch regardless of weight, gather1.2/stow1.8 basework plus walking. There is no general baseline kg carrying allowance yet.
- Deckhand pickup/stow handling divides base seconds by3; it does not divide walking or cutting. Loose/output pickup1.4+stow3 basework on these hulls becomes2.095 wallseconds for novice, excluding walking. Whole-net gather/stow becomes1.429 wallseconds excluding walking, independent of fish count/mass. This is why a weight-limited baseline is necessary to make D04/D08/D09 meaningful.
- Raw→inbound carry→ProcessingInput→prepare→ProcessingOutput→outbound carry→hold is implemented for hulls3/4, including crabs. Small boats bypass processing. Excluded processing orders leave input waiting, not automatic raw bypass.
- Ordinary preparation is one fish per .15+4.5+.15=4.8 basework seconds regardless of kg; max2 hired jobs/positions. A novice stationary processor therefore has theoretical8.75fish/min, experienced13.125, veteran17.5 before starvation and other work. Captain preparation is a separate interactive timing job; its source allows help alongside hired preparation and must be modeled explicitly, never assumed identical to another8.75fish/min worker.
- Input+output share a current processing mass threshold equal to hold capacity240/360kg. Delivery checks current mass before each whole fish; like hold, allows one whole-fish overshoot. This is not two independent240kg buffers or a hard per-fish limit. Processing moves mass between queues without freeing total buffer; outbound does free it.
- Hold accepts one whole fish if presently below capacity, then blocks later insertions. Existing net deliveries check fish individually, not accept the whole overloaded batch. Power Lifter must preserve remaining cargo when a destination cannot accept it; arbitrary carrying weight is not arbitrary destination capacity.
- Loose rod/crab catches currently disappear overboard after25s unclaimed (`TickDeckFish`); basket catches bypass that timeout. Returning salvages only what fits and records remainder as loss. Latest requested no whole-fish loss/no vanishing catch is a proposed redesign boundary, not current behavior. Model safe backpressure, retained cargo and explicit end-of-voyage treatment; do not use disappearance to make overloaded builds look stable.

### Costs and forecast limitations

`GameState.cs`, `GameData.cs`, `VoyageManagementForecast.cs`, `FlowTelemetry.cs`:
- Legacy hand fees30/60/150 for2/3/5voyages; fishers cost2×. Thus existing per-voyage amortized hand fees15/20/30, fisher30/40/60. These are reference costs only, not approved rarity wages.
- Fuel burns1 unit/min while fishing/travel, refill1coin/unit; tanks10/20min, forced return at10%. Food is inactive under current override. Do not charge hypothetical food/engineer/electricity costs in Tier5 comparisons.
- Forecast uses nominal raw catch worth, not automatically secured processed sale value. Separate actual stage rates/queues reveal bottlenecks. Current raw forecasts can exceed sustainably stored throughput.
- Rod expectation uses512-point quadrature; net expectation256 independent deterministic samples with shared actual sampler. It respects current rig/operator availability and a finite captain activity budget; rods/cages share fisher time. This remains a supplied-work estimate, not a scheduler simulation of all interruptions and depletion.
- Forecast processing still duplicates the4.8 formula and assumes one specimen per event. New batches need per-specimen commits or an explicit count field; new card/level/team changes need cache invalidation and hauling pace relearning. Contract fee amortization must be replaced with actual proposed voyage wages.
- DASH087 records1.6million actual rod rolls and120 exact net-oracle comparisons; DASH092 records all5launchers on those players. These are prior evidence, not tests run for this research.

## Small numerical sanity checks, not balance acceptance

A temporary Python512-midpoint transcription of local rod formulas at Hull4/power0.55 produced the following approximate nominal averages. Python rounding/float precision is not a Unity oracle; use actual C# or distribution tolerance in the later reproducible model.

| Ground / bait | Mean kg/fish | Nominal coins/fish |
|---|---:|---:|
| Harbour / worms |0.398|6.67|
| Harbour / squid |0.982|19.06|
| Harbour / chum |0.933|18.38|
| Deep channel / worms |4.322|98.54|
| Deep channel / squid |5.764|142.47|
| Deep channel / chum |6.586|169.74|

This is evidence that existing probabilities/size/value already vary strongly by ground and bait, not a reason to revive rejected bait-centric crew skills. Chum rows describe the formula only; Tier5 cannot currently supply it. New deep-line selection rules are not assumed identical to rods.

Three fish per whole-module60–90s gives2–3fish/min before setup/retrieval; upgraded five gives3.33–5. If instead per physical rig, two base rigs yield4–6fish/min, while three upgraded rigs yield10–15. That3× upgrade interpretation radically changes processing/carrier demand. It must be answered before expanding cards or multiplying simulated outputs.

Finite hires supply360worker-seconds/min total, plus at most60 captain-seconds/min if fully active. Not every passive soak occupies a person; every travel/setup/retrieval/tending/carry/cut does. Independent per-stage maxima cannot all be achieved by the same six workers.

## What is confirmed, what is open

Confirmed for the new proposal: no Engineer/new profession on Tier5; fishers rods/nets/cages/deep lines; hands hauling/processing; fixed2rods+2cages+rear net; optional2normalrods+compact deep-line equipment OR side net with optional rod module absent;2physical deep-line rigs, possible3upgrade; six hired berths baseline; automatic abilities; expanded30-card permission; historical selected unique identities preserved pending transparent review. Third Management page is later preferences work, not part of this implementation phase.

Open player preferences requiring the single question round: deep-line catch target unit; independent purchasable supply versus required onboard small-catch supply chain; desired captain dependence. See ASTRA-QUESTIONS.md. Default60–90s soak plus human work is offered explicitly, not silently selected.

Open tuning/engineering decisions Astra can propose after approval without another preliminary questionnaire: load allowance/indivisible-fish handling, deep-line eligible bias/bait quantities/costs, passive soak/retrieval scheduling and local queue, batch timing, effect attribution/counters, stacking caps/order, level/wage curves, exact small/large eligibility (presentation classes differ from kg), destination partial acceptance and safe claims. These require review with the final proposal, not invented historical approval. Evaluate six berths first; a seventh is a comparison only.

## Next phase modeling plan — deliberately not started

1. Extract a versioned baseline dataset from source with ground/species/weight/value/bait/net/cage/timing/cost/route data; label every proposal separately. Include no-cards/current code and redesigned no-cards baselines to avoid attributing foundational changes to rarity.
2. Build an event/worker scheduler with actual6actors and optional captain, finite stations/buffers/whole fish, passive soaks, setup/retrieval/travel, separate inbound/outbound and atomic job claims. Use measured path distances or explicitly bounded geometry estimates; do not invent exact animation travel.
3. Preserve specimen identities/mass/value through every batch. Ledger: landed = queued + in-transit + processing + stored + intentionally consumed bait/chum (plus separately identified legacy-only losses). Blocking must retain cargo. Simulate partial buffers and Power Lifter safely.
4. Compare rod, shallow/deep-net, cage, deep-line and mixed builds; all-fisher/all-deckhand edge compositions can expose missing coverage without making every installed module compulsory. Compare marginal swap of fisher for hauler/processor, Power Lifter/Bulk Processor together, and method leaders sharing finite work.
5. Report fish/min, kg/min, raw nominal coins/min, sustainable stored/prepared coins/min, actual voyage net after wages/bait/net stock/fuel, worker-seconds by duty, batches/trips, queue growth, storage/fuel-limited duration. Report warmup and steady supplied-work separately from full voyage.
6. Monte Carlo across seeds/local pools and scenario sensitivity for bait, richness, trip length, captain budget, wage/level assumptions. Include stochastic interval and structurally uncertain assumptions; no claim that spreadsheet ranking alone proves game balance. Later native implementation/playtesting remains necessary.
7. Produce one recommended30-card roster with exact rarity slots, original-versus-revised status, varied meaningful alternatives where useful, strongest synergies and counter-bottlenecks. Test transparent wage/ability choices rather than tune every build to identical earnings.

This plan creates no files beyond this research and the questions until Mo's greenlight. Canonical designs, game source, production assets, installs, launchers and saves remain untouched.

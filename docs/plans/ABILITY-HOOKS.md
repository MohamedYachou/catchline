# Crew cards v2 ability hook map

Codex 1 (Windows app), 2026-10-25. CREW-CARDS-UI-1 step 0.
Authority: [CREW-CARDS-V2.md](CREW-CARDS-V2.md), section 8. This is a read-only
source audit and implementation proposal, not an implemented ability engine.
No Unity launch, compilation, save access or production edits in this step.
Claude's core is changing during this audit; reconcile API signatures after the
literal `CARDS-CORE READY` handoff in `comms.md` before step 1.

## Source key and shared integration contract

All paths below are relative to `Assets/Scripts/Game/`. Each table names an
existing method observing the condition and an existing method applying the
effect, followed by the **new** state/hook required. Short source keys resolve
to these exact files (methods are on `VoyageGame` unless qualified):

| Key | File and relevant existing methods |
|---|---|
| Clock | `VoyageGame.cs`: `Step`, `Tick`, `BurnFuel`, `LandFish`, `SellHaul` |
| Rod | `DeckActors.cs`: `Rod.Cast`, `Rod.StartWait`, `Rod.Tick`, `Rod.TickReading`, `Rod.StartReel`; `Person.Do`, `Person.Tick` |
| Reading | `Minigame/BiteModel.cs`: constructors, `Tick`, `Strike`, `StyleOf` |
| Bridge | `VoyageDeck.cs`: `SetupDeckGraph`, `SyncDeckWorkers`, `TickDeckGraph`, `LandOnDeck`, `PersonActor.Skill`, `PersonActor.Act`, `PersonActor.WalkTo`, `FlushDeckGraph` |
| Scheduler | `Deck/DeckScheduler.cs`: `Land`, `PickSort`, `PickTable`, `BuildHaul`, `PickHaul`, `RunBench` (local `Done`), `RunHaul`, `Deliver`, `Cancel`, `HaulWalkMultiplier` |
| Worker | `Deck/Jobs.cs`: `Worker.HandCount`, `HandKg`, `PowerLifter`, `WholeBasket`; `Job`, `IDeckActor` |
| Net | `VoyageNet.cs`: `StartCompactNet` (local `Complete`), `TickNet`, `RollCompactCatch`, `FinishHaul`, `ResetPrimaryNet` |
| Net2 | `VoyageSecondNetModule.cs`: `StartSecondNet` (local `Complete`), `TickSecondNet`, `ResetSecondNet` |
| Line | `VoyageDeepLines.cs`: `TryDeepLineWork` (local `Finish`), `TickDeepLines`, `ResetDeepLines` |
| Cycle | `DeepLineRules.cs`: `DeepLineRules.Roll`, `DeepLineRules.Options`, `DeepLineCycle.Deploy`, `Tick`, `Collected`, `Reset` |
| Pot | `VoyageTier5.cs`: `TryBuoyWork` (locals `Land`, `Finish`, `Recovered`, `Sorted`), `TickTier5`; `VoyageCrabPots.cs`: `ConfigurePotLine`, `TickPot` |
| Prep | `VoyagePrepOrders.cs`: `TryPrepWork` (locals `Pick`, `Begin`, `Finish`, `Release`), `SortFish` |
| Products | `Data/Products.cs`: `TableOrders.Process`, `Run`, `Peek`, `Products` definitions (pure rules, currently not wired to deck jobs) |
| State | `GameState.cs`: `RollFish`, `RollBiteWait`, `FishTable`, `OnCatch` overloads, `Freshness`, `ValueOf`, `SpecimenPricePerKg`; `CaughtFish` |
| Bait | `GameStateCrewBait.cs`: `SelectDeepLineBait`, `TakeDeepLineBait`, `SelectBait`, `TakeBait` |
| Ground | `Data/Grounds.cs`: `Grounds.Drain`, `NightFactor`; `VoyageGrounds.cs`: `TickGrounds` |
| Hold | `VoyageStorage.cs`: `TryStore`, `HoldKg`, `HoldFull`; `VoyageHaul.cs`: `CurrentHaul`, `FreshnessStatus` |
| Travel | `VoyageTrip.cs`: `TickHarbourLane`, `TickChart`, `TickTrip`, `TripRate`; `VoyageSea.cs`: `TickSeaTravel`; `Sea/BoatSailor.cs`: `Tick`; `VoyageTravel.cs`: `UpdateTravel` |

Proposed engine: one voyage-owned instance under `Crew/`, keyed by deployed
card ID, using `CardProgression.HasAbility` and the actual handed-off API.
At audit time the new signature is `HasAbility(CardRarity, AbilityDef)` and
`WorkMult(CardState)` exists; do not implement the spec's abbreviated signature
without checking Claude's final code. Owning a card alone must not activate it.

* Update clocks once per simulation step, before work is consumed; use game `dt`,
  never wall-clock time. Existing pause/capture gates must also freeze abilities.
  Use elapsed time at sea for the proposed timer baseline; no accumulation in
  harbour, no missed-timer bursts, no advancing timers in UI repaint calls.
* Retain gear operator identity through the committed cycle. Rod has `Fisher`;
  nets clear their worker before landing; deep lines clear theirs after baiting.
  Store setters/haulers per rig separately, with a cycle ID. A cancelled attempt
  cannot count as a haul, landing, sort or product completion.
* Separate `BeforeCatchRoll`, `CatchCommitted`, `SortCommitted`,
  `HaulDelivered`, `ProductCommitted` and `HoldInserted` events. These names are
  proposed hooks, not existing methods. Never count a duplicated Tess catch as
  another trigger or recursively repeat its bonus.
* Resolve specimen changes before models, telemetry, depletion, prices and catch
  cards read the final weight. A second weight roll keeps the selected species,
  legal bait bounds and source distribution; it does not roll another species.
  Apply a guaranteed top-quarter floor after the two-roll choice.
* Work rate = skill/100 x `WorkMult` x (1 + matching tool bonus, capped at .50)
  x applicable ability factors. Duration is base / rate. Avoid dividing the
  scheduler duration and accelerating `Person.Tick` by the same factor twice.
  Tools also have non-work effects (fuel, thinning, bite, travel) with their own
  consumers; never treat every navigator/engineer tool as generic work speed.
* Speed multipliers (+15% work = x1.15 rate) differ from wait reductions
  (30% sooner = x.70 duration). Existing waits need a progress-rate hook, so a
  buff starting mid-wait works without repeatedly shrinking remaining time.
  Deep lines need phase-specific progression; do not speed dropping/raising
  when a bite buff is intended only for soaking.
* Every instant/batch action must use normal claim, reservation, keep/throw,
  table-routing and hold checks. Preserve `Scheduler.Balanced`; never duplicate,
  discard or steal claimed fish. Advance counters/consume armed bonuses only
  when their intended result commits; cancellation releases reservations.
* Reset voyage timers/counters/armed bonuses with voyage setup/teardown, not
  every `SyncDeckWorkers` or ground change. Persist only specimen annotations
  needed by unsold catch. Claude owns their data/save changes.

## Ability map (42 abilities plus First mate)

G = Green passive, P = Purple automatic, M = Mythic automatic. Every row below
describes **new work**, including replacements of older hard-coded abilities.

| ID / ability | Existing condition observation | Existing effect consumer | New hook / state needed |
|---|---|---|---|
| 01 Mira G — Chart reader | State `OnCatch(spot, kg, species, net)` sees species/source and active ground; fallback overload sees map depletion | Ground `Grounds.Drain`; State fallback `OnCatch(spot, kg)` | Engine thinning multiplier .85, applied once at drain input, for all catches while Mira deployed. State is Claude-owned: request multiplier injection rather than editing it now. |
| 02 Mira P — Shoal call | Clock `Step` sees active voyage time | Rod `StartWait` / `Tick` waiting branch; Line `TickDeepLines` -> Cycle `Tick` soaking phase; captain Reading `Tick` before Take | 120 s timer; global .70 bite-wait duration for 20 s. Add owner-aware bite rate and phase-specific line clock. Reading needs approach/inspection clock support without speeding the take/strike window or hooked fight. |
| 03 Mira M — Mate's eye | Clock `Step` arms 30 s window every 240 s; each source's catch-roll site observes catch | Rod `Cast` (captain) / `Tick` at bite (crew); Net `RollCompactCatch`; Cycle `DeepLineRules.Roll`; Pot `TryBuoyWork.Land` and captain cage rolls | Shared source-aware specimen roller with second draw of weight only; keep heavier. Net rolls happen before hauling and captain rod rolls before landing: propose roll-time window qualification so model and payout agree. See Q8. |
| 04 Noor G — Quick sort | Scheduler `RunBench` knows worker and `JobKind.Sort` | Bridge `PersonActor.Act` / Rod-file `Person.Tick` | Job-specific sort rate x1.10, gated Green+, replacing unconditional legacy Noor skill bonus. |
| 05 Noor P — Same again | Scheduler `RunBench.Done` sees each successfully sorted species | Scheduler `RunBench` next sort timing through Bridge `PersonActor.Act` | Per-Noor previous species and one armed x1.30 next-sort rate after two consecutive matching completed sorts. Snapshot at job start, consume on completion, restore on cancellation. |
| 06 Noor M — Bucket brigade | Net `FinishHaul`; Net2 `StartSecondNet.Complete` commit a whole basket | Bridge `LandOnDeck`, Scheduler `Land` / `RunBench.Done` routing | Basket-landing event with rig/cycle batch identity; first five eligible unclaimed fish receive zero sort time through normal routing. Not five per `Land` call. Noor must be deployed; no arbitrary teleport across the deck. See Q6 for proposed scope. |
| 07 Dirk G — Steady strike | Rod `Tick` enters Bite with `Fisher`; captain Reading is separate | Rod assignment `biteWindow = g.StrikeWindow`; Clock `FisherThink` automatic strike logic | Worker-specific window x1.15 for Dirk only, gated Green+. Do not globally modify `VoyageFeedback.StrikeWindow` or accidentally buff captain. |
| 08 Dirk P — Rod line | Clock `LandFish` receives successful Dirk rod catch | Other Rod `Tick` waiting branch / `StartWait` | Per-owner landing event arms 15 s .80 wait factor for other rods (exclude source, include captain Reading via proper phase hook). No lines in this ability. |
| 09 Dirk M — Trophy hunter | Clock `LandFish` is success commit, but species/weight was already rolled in Rod `Tick` | Rod catch-roll site before hook/model/landing | Reserve ordinal for in-flight catch; every third successful Dirk landing uses weight >= min + .75*(max-min). Failed strikes must not advance counter. Since each fisher runs one rod, prepare next-success ordinal at roll, commit only on land. |
| 10 Tess G — Quick reel | Rod `Tick` Reeling knows `Fisher` | Same reeling progress expression using `Fisher.Speed` | x1.15 reel-only rate for deployed Tess Green+, alongside work/tool rate once. |
| 11 Tess P — Feathers | Clock `LandFish` knows Tess and final species | Clock `LandFish` -> Bridge `LandOnDeck` / legacy deck spawn | One 20% roll for Herring/Mackerel/Whiting; one additional legitimate landed fish. Shared emission path updates stats, telemetry, ground drain and backpressure per actual fish. No recursive event. |
| 12 Tess M — String of feathers | Clock `Step` 120 s timer; Clock `LandFish` next eligible Tess shoal species | Same landing emitter as 11 | Armed token makes the qualifying catch total three fish. Proposed precedence replaces 11's extra roll on that catch (Q7); cancellation/noneligible species leaves token armed; no unbounded stacking. |
| 13 Sam G — Extra fish | Bridge `SyncDeckWorkers` resolves Sam's card | Worker `HandCount`; Scheduler `BuildHaul` | Base count +1 only with Green passive; remove unconditional Sam count 4. Preserve kg and destination limits. |
| 14 Sam P — Heavy lifter | Scheduler `PickHaul` / `BuildHaul` sees specimen kg and Sam | Worker heavy eligibility; Scheduler `HaulWalkMultiplier`; Rod-file `Person.Tick` walk budget | Per-job heavy load rule permits two fish >3 kg, no heavy slowdown for Sam. Existing model has no general heavy walk penalty: see Q1. Replace Gold-only `PowerLifter`, preserve safe destination capacity. |
| 15 Sam M — Shoulder load | Clock `Step` arms every 120 s; Scheduler `BuildHaul` sees net source basket | Scheduler `BuildHaul`, `RunHaul`, `Deliver` | Next net basket can exceed hand count/kg as a single atomic load, constrained by one destination/reservations/hold. Add source-kind and cycle provenance; token commits on successful delivery, returns on cancel. |
| 16 Kofi G — Fast set | Net `StartCompactNet`; Net2 `StartSecondNet` know setter and `haul=false` | Their `person.Do("Setting net", ...)` -> Rod-file `Person.Tick` | Net-setting-only x1.15 work rate for Kofi; apply to both rigs. |
| 17 Kofi P — Good spot | Net `RollCompactCatch` and Net2 `TickSecondNet` expose kg; haul commit confirms success | Net/Net2 set-completion assignments to `netSoak` / `secondNetSoak` | Track Kofi's setter/hauler association and actual catch kg / that rig's catch capacity. Successful >.80 fill arms next soak x.75, consumed only on successful reset/set. Clarify ownership Q4. |
| 18 Kofi M — Back-to-back | Net `StartCompactNet.Complete` / Net2 `StartSecondNet.Complete` successful Kofi haul | Net `FinishHaul` -> `ResetPrimaryNet`; Net2 `ResetSecondNet` then next set transition | Every third success arms zero setting-work next cycle. Still require stock, safe access, empty output, ground and available operator. Never instantly refill a blocked basket or count torn/cancelled hauls. |
| 19 Rosa G — Strong back | Net/Net2 start `haul=true` with Rosa | Their `person.Do("Hauling net", ...)` | Haul-only x1.15 rate, both rigs, no soak reduction. |
| 20 Rosa P — Full bag | Clock `Step` 180 s timer; Net/Net2 haul starts with Rosa | Net `RollCompactCatch` occurs earlier at soak completion; Net `FinishHaul` / Net2 haul completion emit stored catches | Arm next Rosa haul and add up to 30% catch kg at haul commit using same legal local catch distribution, before depletion/telemetry for bonus fish. Existing roller needs budget/size policy (Q5); do not re-drain original fish. |
| 21 Rosa M — Shake out | Net `FinishHaul`; Net2 haul `Complete` retain successful hauler identity | Normal Scheduler sort routing -> `OnStowed` -> Hold `TryStore` | First six eligible keepers from Rosa's net batch bypass timed sort/carry, count as properly sorted, use hold checks and hide model once. Overflow follows normal deck path. Add committed bypass event and keep landed/stowed/thrown accounting balanced. |
| 22 Ana G — Quick walk | Bridge `PersonActor.WalkTo` resolves Ana | Rod-file `Person.Tick` walk budget / `Person.WalkMultiplier` | x1.10 walking only, gated Green+, compose with haul effects. Remove unconditional Ana skill boost (which currently affects other haul actions too). |
| 23 Ana P — Hand-off | Scheduler `Deliver` knows Ana and target `SortIn` basket | Scheduler `RunBench` next Sort at that exact station | Per-table pending x1.20 next-sort rate on each delivered fish; propose one nonstacking charge per next sort, not exponential scaling. Reserve/consume on sort completion, release on cancel. |
| 24 Ana M — Clear deck | Clock `Step` 60 s cooldown; Scheduler `OnDeck`/baskets/Loose expose >=6 waiting fish | Scheduler `PickHaul` / `BuildHaul` / `RunHaul` / `Deliver` | New claim-safe sweep job spanning sources/routes. Waiting means unclaimed deck fish, excluding hands/in-flight gear; cooldown starts after actual sweep delivery. Normal destination/hold backpressure leaves undeliverable fish intact. See Q6. |
| 25 Mats G — Quick knife | Scheduler `RunBench` TableWork; Prep `TryPrepWork` | Bridge `PersonActor.Act`; Prep `Begin` timed table stage | x1.10 table-work-only rate, gated Green+, replacing unconditional Mats skill bonus. Must not speed walk/pickup twice. |
| 26 Mats P — Offcuts | Scheduler `RunBench.Done` TableWork; Prep `Finish` successful non-chum job | Scheduler `OnTableDone` callback; Products `TableOrders.Process`; `State.Chum` credit at actual product commit | Add one chum per actual product job, not per callback retry. Product conversion is not connected in current deck path (Q2); do not equate default pass-through processing with a product without decision. |
| 27 Mats M — Batch cut | Scheduler `PickTable` and completed TableWork count for Mats | Scheduler `PickTable` currently claims one; `RunBench.Done` iterates `job.Fish` | Every third successful product job may atomically claim/reserve a second eligible fish and process both in one work interval. Never fabricate a second when unavailable; product/count semantics need Q2. |
| 28 Lise G — Night eyes | `State.NightVoyage`, Rod `Fisher` at wait | Rod `StartWait` / `Tick` waiting | Night-only Lise .80 wait factor. No nonexistent jig implementation needed; current speciality is rods as spec says. |
| 29 Lise P — Lamp lure | Clock `Step`, night flag, 120 s timer | All Rod waiting/Reading pre-take; Line/Cycle soaking | Global .75 wait factor for 30 s at night. Remove active effect immediately outside night; shared bite hook with 02. |
| 30 Lise M — Deep night | Clock `LandFish` successful Lise catches at night; Rod pre-roll can reserve next ordinal | Rod `Tick` catch selection before rendering/landing | Every fourth night success selects legal local heavy predator and top-quarter weight. No predator tag exists; propose approved species list intersected with local eligibility, fallback to top-quarter original legal species, Q3. `FishStyle.Heavy` alone is not a predator definition. |
| 31 Ines G — Headlamp | Clock `Step` and `State.NightVoyage`; deployed card set | Shared work rate through Bridge/Rod; net/pot/line owner work | Night-only team x1.05 work rate. Include all deployed working crew; captain inclusion separate Q9. Never multiply environmental bite/soak by generic work bonus. |
| 32 Ines P — Ice watch | Hold `TryStore` changes `HoldKg` across .5 capacity | State `Freshness`, Clock `SellHaul` valuation; harbour age conversion in `VoyageGame` return path | One crossing trigger per voyage, 180 s freshness-age freeze without restoring prior loss or causing catch-up decay. Track overlap per fish, including newcomers; owner requests data/save/value hook from Claude (Q10). |
| 33 Ines M — Floodlights | Clock `Step` at night every 180 s | Shared Rod/Line bite clocks and Bridge/Rod deck-work rate | 40 s global .75 bite-wait factor and x1.15 deck-work rate. Keep work/soak clocks distinct; do not accelerate strike/reveal animation or fuel by scaling whole `Step`. |
| 34 Olaf G — Tuned engine | Clock `BurnFuel` sees motor hull and deployed Olaf | Same `State.Fuel - dt/60` deduction | Multiply consumption .90, never increase tank capacity. Compose engineer oil-can fuel reduction in same consumer, once. |
| 35 Olaf P — Winch tune | Clock `Step` every 120 s while Olaf aboard | Net/Net2 haul `person.Do`; Pot `TryBuoyWork` recovery; Cycle raising phase | 30 s x1.25 winch rate. Spec names nets and pots, so exclude deep-line raising unless lead confirms; Cycle named here only for tool-family separation. Pot currently combines work (Q11). Captain cage needs pull-specific hook if global effect includes captain. |
| 36 Olaf M — Full steam | Sailing state/leg in Clock `Step` and Travel `TickTrip` | Travel `BoatSailor.Tick`, `TickHarbourLane`, `TickChart`, legacy sailing `modeTimer` | Interpret “25% faster” as travel rate x1.25 (time x.80); confirm wording if lead intends 25% shorter trips instead (rate 1/.75). Compose Charts tool; accelerate travel simulation only, not deck/fuel/freshness clocks. Keep turning/braking/collision steps consistent; skip/reverse remain valid. |
| 37 Pim G — Fast bait | Line `TryDeepLineWork` starts bait action; pots have no bait action | Line `fisher.Do("Baiting deep line", ...)`; prospective Pot separate bait stage | x1.25 bait-work rate. Pot portion unavailable until a pot bait phase exists (Q11); do not speed the complete recover/soak as a substitute. |
| 38 Pim P — Chum saver | Line `TryDeepLineWork.Finish` rechecks bait before `TakeDeepLineBait`; prospective pot bait commit | Bait `TakeDeepLineBait`; pot has no consumption | 30% waive consumption while still requiring/using eligible chum; only roll at committed bait use and preserve bait policy. Claude-owned Bait change request; pot portion needs Q11. |
| 39 Pim M — Pot luck | Clock `Step` 300 s timer; Pot `TryBuoyWork.Finish` / Line `TickDeepLines` successful recovery | Pot local `Land`; Line loop over `DeepLineRules.CatchCount` | One armed extra catch on next Pim-owned successful pot/line haul. Store deep-line operator across all phases; one extra legal roll, depletion/stat/telemetry per added fish. Do not consume on cancel/blocked rig. |
| 40 Tove G — Steady hands | Scheduler sort job species == Crab; crew have no pinch condition | Scheduler `RunBench` -> Bridge `PersonActor.Act`; captain-only `CageModel` has snag, no pinch | Crab-only x1.20 sort rate; no-pinch clause currently vacuous, not implemented immunity. Remove unconditional Tove all-sort +10%. Q12 proposes keeping no-pinch as future-proof trait without adding a penalty system. |
| 41 Tove P — Grader | Scheduler `RunBench.Done` successful Tove sort, kg >= min+.75*(max-min) | State `ValueOf` -> State sale loop; Clock `SellHaul` | Per-specimen x1.10 sale annotation set once at sort commit and preserved through baskets/hold/harbour/save. `CaughtFish` has only Species/Kg/StowedAt today: request Claude-owned metadata/value/save API (Q10). |
| 42 Tove M — Keen eye | Scheduler `RunBench.Done` counts Tove's successful sorts | Same per-specimen `ValueOf` consumer | Every tenth actual sorted fish gets x2 sale annotation once. Proposed multiply with Grader (x2.20 combined); don't advance on throw/cancel, Q7. Preserve metadata across every copy. |
| 43 Mira trait — First mate | Deployed Mira found at engine setup and deployment refresh; rarity read there | Shared work rate across Bridge `PersonActor.Skill`, Rod reeling/baiting and other crew action paths | Team x1.05 or x1.08 at Mythic; independent of Green unlock. One team factor, never once per teammate. Does not change environmental bite time/ground richness; captain scope Q9. |

## Missing mechanics and decisions for Claude

These are implementation questions, not requests to reopen the agreed card economy.
Concrete alternatives are proposals until the lead records a decision.

* **Q1 — Heavy carrying:** `Person.Tick` has no kg slowdown. `Worker.PowerLifter`
  currently unlocks only exact Gold Sam and `HandKg` defaults to 6. Proposed:
  implement Purple Sam's two-heavy-fish capacity and leave his movement at the
  normal rate; do not introduce a universal heavy-fish penalty solely to make
  immunity visible. Replace legacy same-route Sam team walk buff.
* **Q2 — Product pipeline:** `Products`/`TableOrders` are pure, unconnected rules.
  `SetupDeckGraph` does not wire `OnTableDone`, so scheduler TableWork currently
  just forwards fish; the legacy Prep path makes chum or sorts full-value fish.
  Proposed interim definition: non-chum completed table work is Mats's product
  job (Offcuts grants one chum, Batch cut processes two real fish normally).
  Alternative is Claude wiring actual product inventory/conversion first. Do
  not claim oil/special production exists from data definitions alone.
* **Q3 — Predator identity:** no predator metadata exists; `FishStyle.Heavy` is a
  behaviour category, not a biological predator tag. Proposed explicit approved
  species list intersected with `State.FishTable`, hull eligibility and bait
  rules; if intersection empty, apply top-quarter weight to the original legal
  catch and show that narrower effect. Avoid spawning an out-of-map shark.
* **Q4 — Kofi ownership:** setter and hauler can differ; net catches lack cycle
  owner metadata. Proposed Good spot follows the setter Kofi's rig and successful
  delivery; Back-to-back explicitly counts Kofi's own hauls. Record both identities
  per rig so delegation never silently credits the wrong crew member.
* **Q5 — Full bag:** fullness is kg-based in this code, not a fish-count gauge.
  Proposed target 1.30 x original kg, capped at normal rig capacity, emitted as
  extra locally legal specimens until the remaining budget cannot fit one.
  A full net gains nothing; confirm if the intended perk instead allows overflow
  above normal rig capacity. Never inflate existing specimen kg above species max.
* **Q6 — Basket and sweep scope:** no cross-source sweep job or instant net-sort
  event exists. Proposed Noor marks first five net-batch fish for zero sort work
  once they reach a sort table, retaining carry pressure. Ana starts a real route
  over all eligible unclaimed waiting fish, carrying permitted destination loads
  until the snapshot is cleared; no teleport. Sam's explicit whole-basket perk
  alone bypasses hand limits. Lead may choose literal teleport semantics instead.
* **Q7 — Bonus stacking:** proposed Tess Mythic total three replaces Purple extra
  fish on that catch; Tove bonuses multiply to 2.20; repeated Hand-off grants a
  nonstacking next-sort charge. Independent team work buffs multiply. Confirm
  overlapping bite reductions' policy before tuning (proposed multiplication,
  minimum positive wait; no permanent stacking of repeated timed windows).
* **Q8 — Catch time:** Mira says fish *caught* during the window, but captain rods
  pre-roll at cast, nets at soak completion and cages before sorting. Proposed
  roll-time eligibility so previews and landed specimen match. If landing-time
  eligibility is required, reserve two weights at source and choose before first
  visible specimen; a late landing-only mutation would disagree with rod art.
* **Q9 — Team means crew:** proposed First mate/Headlamp affect deployed crew
  including operator work; captain remains outside these two crew-only phrases.
  Global all-rods/lines effects include captain. Floodlights deck-work scope needs
  explicit captain decision; avoid silently changing the captain baseline.
* **Q10 — Durable specimen state:** freshness freeze and sale multipliers have no
  fields/API in current `CaughtFish`. Proposed Claude supplies sale multiplier and
  effective freshness-age accounting, copied on return/unsold save and respected
  by `ValueOf`. Transient engine dictionary alone loses bonuses at harbour copies
  or reload. Ice watch should freeze age, never heal or defer a decay cliff.
* **Q11 — Pot bait/winch phases:** pots automatically soak; crew recovery is one
  2 s action, with no bait stage or chum cost. Proposed add separate paid bait and
  winch stages before re-soak, preserving initial availability/stock rules; this
  changes pot economics and needs lead decision. Interim alternative implements
  Pim bait/saver on deep lines only and Olaf on the existing recovery action,
  with UI text explicitly reflecting the restricted behavior. Captain cage pull
  is interactive; do not speed the sort/snags when applying a winch bonus.
* **Q12 — Crab pinch:** only captain rope snag/wrong-drag lock exists in
  `Minigame/CageModel`; neither is a crab pinch or Tove action. Proposed crab
  sort x1.20 now, pinch immunity reserved for any future crew pinch mechanic;
  alternative replace clause with explicit uninterrupted crab sorting. Never
  disable captain rope hazards under the name of Tove immunity.

## Existing effects to replace, not stack

`VoyageDeck.PersonActor.Skill` unconditionally adds +10% for Noor/Tove sort,
Mats table and Ana haul, irrespective of the new unlock. `SyncDeckWorkers` gives
Sam four hands unconditionally. `Deck/Jobs.Worker.PowerLifter` and `WholeBasket`
test exact Gold, so they fail at Mythic and don't match the v2 perks.
`DeckScheduler.HaulWalkMultiplier` applies an old Sam same-route x1.30 team buff.
Replace these with one engine path after handoff; leaving them produces doubled
bonuses or the wrong unlocks. `VoyageCards.ConfigureCardPeople` currently sets
level multiplier alone and supplies the walk callback; reconcile with the new
rarity/star/tool formula and `PersonActor.Skill`, not a second competing model.

## Later verification plan (not run in step 0)

Run editor checks only in `Catchline-sim` via `docs/tools/check.ps1`, after the
core handoff and actual implementation. New files stay within
`Assets/Editor/CrewCards*Checks.cs`; preserve Claude's core checks.

1. Deployment/unlocks/work family: each passive off below unlock, on at unlock
   and Mythic; inactive owned cards off. Mira first, .05/.08 team factor exactly
   once. Match work formula by job, captain/tool class rules and x.50 tool cap.
2. Clocks: advance simulation through start/end boundaries and large-dt slices,
   pause and harbour; verify every timer's trigger and duration, all rod paths,
   both net rigs and phase-specific deep-line effects. Work buffs do not alter
   freshness/fuel/strike clocks; travel buffs do not alter deck time.
3. Catch family: deterministic seed/forced rolls prove Mira double weight keeps
   species/distribution bounds, Dirk third/Tess extras/Lise fourth/Pim extra,
   Rosa fullness and successful ownership; misses/cancels never advance counts.
4. Sort/haul family: Noor repeated species and five-fish batch, Sam capacity and
   whole basket, Ana delivery/sweep, Tove tenth/quarter annotations. Assert real
   identities, claims/reservations, routes, throw rules, overflow and
   `Landed == Stowed + Thrown + OnDeck` after commit and cancellation.
5. Product/economy family: Mats counters and two-input atomic commit, exact chum
   delta, Pim consumption waiver only on successful use; Ines freshness freezes
   without healing/cliff, Tove multipliers survive harbour copies and save/reload.
   These depend on Q2/Q10/Q11 and Claude's APIs.
6. UI: after step 1, runtime HUD captures for garage/card/tools/chests/odds/reveal/
   renown/sale at desktop and landscape phone, opened and inspected. Scene-only
   rendering does not prove IMGUI or touch acceptance. Use isolated session saves.

Step 0 exit: 14 crew x 3 abilities + one trait mapped, missing mechanics logged
as QUESTION lines in `comms.md`. Step 1 remains gated on `CARDS-CORE READY`.

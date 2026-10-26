> **CREW098 — authoritative correction from Mo:** Electrical machinery must have its own support jobs and introduce additional management bottlenecks. It must not take over the fishing, hauling or processing jobs that give fishers and deckhands their purpose. Electric reels/haulers and the crew-replacement premise of CREW097 are rejected. That eight-card draft is withdrawn pending a machine-role redesign; earlier selected crew cards are preserved. Historical machine proposals below are not approval and must be reassessed against this constraint. No new machinery or replacement card has been selected.

# Catchline — crew cards and the production ecosystem

Design record, 18 October 2026. Owner: Codex 1 (Windows app), with Mo.

Canonical file: `C:/Users/momoy/Projects/Catchline/docs/CREW-CARDS-DESIGN.md`.
The copy delivered in the chat's outputs folder is a dated snapshot. Continue updating
this project file when future decisions are made. Coordination history is in `comms.md`,
especially CREW053–CREW081. This document is design for a future build, not a claim
that crew cards or the proposed workload changes are implemented.

**Latest scope change — CREW094 / section21:** only electrical components of
powered machines have Engineer-maintained condition. Bare rods/nets/cages have no
engineering wear. This supersedes earlier generic fishing-gear wear discussions.
CREW095 confirms normal nets have unlimited uses and deep nets have three uses each.
These consumable uses are separate from electrical condition; Deep-Net Saver remains.

## 1. Read this before designing or building another card

Mo's objective is to manage a working boat, with satisfying automation and decisions
that matter after hiring the crew. Crew should enable rod, net, cage and mixed builds.
More fishing output should create pressure on the rest of the boat. Income is earned
by sustaining that output, not simply by equipping the highest rarity.

The key question for every ability is:

**What additional work does it create, where does that work accumulate, and what
choices let the player sustain it?**

- Faster fishers create collection, hauling, processing, storage and servicing demands.
- More demanding gear operation consumes equipment condition faster. Good engineers
  become more valuable as the player pushes production.
- A strong fisher can make an unsupported boat worse. Swapping a fisher for a deckhand
  or engineer should sometimes increase actual voyage earnings.
- Bottlenecks are unwanted by the player but deliberately created by the design.
  They must be understandable and solvable through crew, modules, duties and captain work.
- Higher rarity should enable stronger, more demanding operating patterns. Do not
  automatically remove wear, queues or other constraints as the rarity reward.
- The captain can intervene in ordinary work. Abilities remain automatic; the player
  manages the operation rather than pressing twelve crew-skill buttons.
- Designing a sustainable boat must remain possible. The goal is useful operating
  decisions, not guaranteed collapse or arbitrary emergencies that demand constant taps.

Illustration only, not balance: if fishing supplies 12 kg/min but carrying sustains
8 kg/min, the queue grows by 4 kg/min. Adding fishing speed does not fix it. The player
could assign another carrier, change the fishing loadout, help carry, or reduce intake.
Processing and maintenance have their own workload measures and may become the next
bottleneck after carrying improves.

Mo specifically identified Cage Foreman's new **tending job** as the kind of legendary
ability wanted: a new capability for fishers that changes staffing and strategy.
Do not revert to making every legendary a collection of ordinary upgrade percentages.
Speed passives are welcome when they strengthen that coherent operating pattern.

## 2. Established crew-card rules

| Topic | Decision |
|---|---|
| Ownership | Collected cards and their levels are retained permanently. |
| Payment | Pay deployed crew per voyage, with wages depending on rarity and level. Exact prices open. |
| Named duplicates | One copy of a named crew member per boat. Duplicate acquisition rewards open. |
| Base work speed | Equal within the same role at the same level across rarities. Skills create rarity differences. |
| Levelling | Fixed upgrades and preset identity; no branching upgrade choices. Exact cap and milestones open. |
| Common / blue | One automatic active, no passive. |
| Rare / purple | One automatic active and one passive. |
| Legendary / gold | Two actives plus one passive, or one active plus two passives. |
| Active meaning | An automatic signature effect, rule or triggered ability. Never a skill button. |
| Passive scope | Generally supports the team. Actives mainly affect their owner, except clear team-support identities. |
| Choices | Mo participates in each new card, normally through about three alternatives or iterations. |

Do not restart the already selected fishers as another questionnaire. Review their
interactions together against the ecosystem principle. Any necessary changes should
be presented as a consolidated proposal, not silently substituted for their choices.
Commons may primarily serve early progression; protecting their endgame usefulness
must not prevent meaningful rare/legendary builds.

### Intended role split versus current implementation

- **Fishers:** operate the fishing methods, including rods, nets and cages in the
  proposed whole-game crew rework.
- **Deckhands:** catch collection, carrying/stowing and preparation/processing support.
  Do not center their future roster on bait or fictional feeding areas.
- **Engineers:** equipment servicing and repairs plus meaningful operating support;
  not merely a mandatory tax with no interesting identity.
- Slower basic coverage across roles and captain work should allow small crews to
  operate early boats. Exact coverage rules and efficiencies remain open.

Current Tier5 integration retains deckhands operating nets and fishers operating
rods/buoys, with an Engineer role. That is the delivered temporary role model, not
proof the future card-role migration has happened. Coordinate any change explicitly.

## 3. Working collection size

Original agreement: 30 cards, including 12 fishers with two legendaries. Mo subsequently
requested **three fisher legendaries**: rods, nets and crab support. Retaining the
other selected cards gives this expanded working roster:

| Role | Common blue | Rare purple | Legendary gold | Total |
|---|---:|---:|---:|---:|
| Fishers | 7 | 3 | 3 | 13 |
| Deckhands | 5 | 3 | 2 | 10 |
| Engineers | 3 | 3 | 2 | 8 |
| Total | 15 | 9 | 7 | 31 |

Do not delete a selected common to force the old total of 30. These are unique cards
in the collection, not required crew counts or mandatory equal-role boat staffing.
Tier5 currently has six hired crew plus captain. Earlier discussion of roughly
11–12 eventual crew is a later progression aspiration, not the current Tier5 capacity.

## 4. Selected common fishers

All are automatic personal effects. Names are working identifiers, not final character
names. Exact level growth is unselected. Preserve the selected starting effects.

| ID | Working name | Selected effect | Dependency / clarification |
|---|---|---|---|
| F01 | Strong Start | Their first successful rod cast each voyage lands **3 fish total**. | Once per voyage; not 3 additional fish. |
| F02 | First Set | Their first net deployed each voyage needs **half normal soak time**. | Earlier wording said “50% faster”; selected intent was halved duration. |
| F03 | Fast Bite | Every third rod cast has **half normal bite-wait time**. | Does not bypass strike, failure or collection. |
| F04 | Loaded Net | Every third net they deploy gains **25% catch capacity for that haul**. | Increases catch mass budget, not boat storage. |
| F05 | Quick Soak | Every third cage/pot they deploy needs **half normal soak time**. | Cages are now confirmed/added. Map “deploy” and personal attribution to the actual buoy reset cycle when implementing. |
| F06 | Quick Retrieve | Every third longline they haul needs **50% less retrieval time**. | **Future-dependent concept. Longline gameplay is not confirmed or implemented.** Retain the chosen card concept pending explicit method/replacement decision. |
| F07 | Quick Reset | After every third completed fishing cycle, their **next** cast/deployment setup takes **half normal time**. | The following setup, e.g. after cycle 3, not the third setup itself. Define cross-method cycle attribution before implementation. |

## 5. Selected rare fishers

### F08 — Deep-Net Saver

- **Personal automatic active:** their successful deep-net hauls consume **no net use**.
  Failed hauls still consume one use.
- **Team passive:** **all deep nets have 15% more catch capacity**.
- Personal capacity was explicitly changed to team-wide by Mo.
- No waiver of equipment condition damage, carrying, processing, storage or failures.
- Conservation of net stock is distinct from engineering wear. Do not conflate them.

### F09 — Rod Leader

- **Team-support active:** while they work a rod, all staffed rods, including the
  captain's when applicable, need **25% less bite-wait time**.
- **Team passive:** all rod fishers need **20% less reeling time**.
- Explicit team-player exception to the usual personal-active scope.
- No unmanned rod operation or taking over another worker's station.
- Personal reeling passive was explicitly changed to team-wide by Mo.

### F10 — Heavy Cages

- **Personal automatic active:** their cage hauls produce **50% more catch weight**.
- **Team passive:** all cages need **15% less soak time**.
- Personal soak passive was explicitly changed to team-wide by Mo.
- Exact catch composition, specimen limits and handling/condition consequences need
  definition against the actual cage system. Do not silently exceed species limits.

These rares stay selected. Their interaction with the stronger ecosystem and
condition rules needs a consolidated balance pass, not another card-by-card restart.

## 6. Net legendary — Back-to-Back Netter

**Status: retained by Mo, including the latest comparison against Split Haul.**
One personal automatic active plus two team passives.

### Active — Back-to-Back

The fisher can reset/redeploy their net while its previous landed catch still needs
unloading. The basket can hold at most **two hauls**. At that limit, further
redeployment pauses until a haul slot is cleared.

- This requires a new finite basket/queue rule. It is not existing card functionality.
- The fisher still performs setting and retrieval. Deckhands still carry and stow
  all catches. Net uses and equipment wear remain.
- No automatic stowing, disappearing overflow, free storage or extra unmanned net.
- Normal hold-full limits remain. Exact checks before setting/landing need design.
- Define a haul-slot's physical mass capacity and release rule. Partial collection,
  in-flight carrying, interruptions and multiple baskets must not lose or duplicate fish.
- The ability lets the player run ahead of support temporarily. It does not remove
  the eventual unloading bottleneck.

### Selected team passives

1. **All nets need 20% less soak time.** Duration multiplier 0.8.
2. **All nets haul 20% faster.** Rate multiplier 1.2, duration divided by 1.2.

The second wording is not mathematically identical to “20% less haul time.” Preserve
the chosen wording until a deliberate normalization decision is made.

### Equipment burden

Mo explicitly wants this operation to strain tools more and need a good engineer.
The current proposal is **50% extra operating condition damage per personal haul**,
on top of performing more cycles. The exact percentage is **provisional**, not a
locked balance decision. Do not apply it to unrelated rigs or idle time by accident.

### Intended build and decisions

Net intake speeds up. A second net adds more demands on shared workers. The player
chooses net-heavy versus rod-heavy modules, supports carrying/processing/servicing,
and can help where queues accumulate. Condition can fall if servicing cannot keep
up. A powerful crew build becomes profitable only if those supporting jobs hold up.

### Alternative reviewed — Split-Haul Master

Proposed personal signature: one net catch lands in two portions during retrieval,
letting deckhands carry the first while the fisher retrieves the second. It retains
the same two speed passives for comparison. It requires new staged landing behavior.

This overlaps carrying with hauling but does not allow the next cycle to begin with
a backlog. **Mo chose Back-to-Back instead.** Keep Split Haul as an unselected
alternative; do not implement it in addition or quietly replace Back-to-Back.

## 7. Rod legendary prototype — Twin-Hook Specialist

**Status: proposed, not explicitly selected by Mo.** The request to save these ideas
does not finalize this card. One personal active plus two team passives proposed.

### Proposed personal active

Their assigned rod fishes **two hooks from one cast**. Each hook has an independent
bite timer. The fisher reels catches **one at a time**; the waiting hook can progress
while the first is retrieved. Maximum two pending fish/hook states, not another rod.

- This is a new rod state/queue mechanic, not a promise the current actor supports it.
- No stealing another fisher's station or making them idle.
- Two genuine hook/catch sequences, not a reroll or duplicating one landed specimen.
- Every fish requires ordinary landing, collection, storage and processing work.
- Extra operation/strain should cost equipment condition; exact surcharge open.
- Define overlapping bites, strike handling, hooked-fish waiting limits, missed fish,
  partial resets, captain interaction and the moment both hooks can be recast.
- Any timeout/default policy must be automatic. No mandatory ability micromanagement.

### Proposed team passives

1. All rods have **20% shorter bite waits**.
2. All rods have **20% faster casting setup**.

These numbers and the entire package remain unapproved. Extra intake should burden
collection and servicing; avoid matching free boosts to all support jobs.

## 8. Crab support legendary — Cage Foreman

**Status: Mo explicitly likes and endorses the new cage-tending capability.**
Its exact numbers, passives and final character identity remain proposals. This is
the example to preserve when interpreting what “creative legendary” means here.
One team-support automatic active plus two smaller general fishing passives proposed.

### Team signature — unlock cage tending for fishers

While the leader is assigned to cages, every fisher gains access to a **cage-tending
assignment**. A fisher can actively tend a soaking cage to accelerate it.

Proposed working rules:

- One tender can benefit each cage at a time.
- Proposed tending bonus: **50% faster soak progress while actively tended**.
- The tender is a real occupied worker, unavailable for simultaneous rod/net work.
  This is a staffing opportunity cost, not an extra invisible worker.
- A ready cage still needs recovery. Another available fisher or the captain can
  recover it; define how the tender can transition to recovery when no helper is free.
- The leader can also do actual cage work. Do not require an otherwise idle aura body.
- Add and validate physical approach/work positions if multiple people work one rig.
- Do not silently add more cage hardware, cage capacity or boat sockets.
- Tending priority is a crew-duty choice; execution is automatic, not a skill button.
- Define progress when the tender leaves, faults occur, a cage becomes ready, the
  leader changes assignment, or the hold fills. Never award instantaneous retroactive progress.

This lets multiple fishers form a cage-focused operation around the existing stations,
instead of support being only a personal catch bonus. More fishers devoted to tending
means fewer working rods. Faster cage turnover generates recovery, processing,
storage and engineering work.

### Proposed smaller speed passives across fishing

1. **10% shorter bite waits and soak times** across rods, nets and cages.
2. **10% faster retrieval** across rod reeling, net hauling and cage recovery.

These affect fishing work, including the leader's relevant work; they do **not**
increase carrying, processing or repair speed. This preserves downstream pressure.
Exact numbers and stacking with specialist cards need Mo's choice and balance work.

### Current-game distinction

Tier5 fishers already leave rods in suitable gaps to recover ready buoy catches.
That fallback behavior is not this legendary ability. **Tending during soak is new.**
Current crab catches go directly to storage; they do not currently require deckhand
carrying. Giving crabs a carrying stage would be an explicit core-mechanic proposal,
not something to assume was approved with this card.

## 9. Mechanical foundations needed before implementation

Source observations from this design session, not fresh runtime acceptance:

| Actual system | Design implication |
|---|---|
| `VoyageNetUnload.cs`: gathers a whole eligible basket batch in a base 1.2s action, then stows the batch in a base 1.8s action, plus walking/role modifiers. | Bigger catches barely increase carrying effort. Bounded loads and/or weight-linked handling are needed for real deckhand pressure. |
| Existing net unloading has batch ownership and basket backpressure. | Back-to-Back needs explicit finite queues and safe partial unloading; it cannot be only removal of a blocking condition. |
| `VoyagePrepOrders.cs`: preparation is an individual-fish job, base 4.5s in the inspected source. | Processing capacity currently follows fish count, not just kilograms. Larger fish alone may even reduce job count per kg. |
| `VoyageTier5.cs`: crab recovery creates a crab and stores it directly. | Current cage bottlenecks differ from rod/net carrying. Do not invent an existing cage deck queue. |
| `DeckActors.cs` / `VoyageGame.cs`: each fisher ordinarily owns one rod and a rod follows cast/wait/bite/reel states. | Twin hooks require a new two-hook state model and correct worker ownership. |
| Tier5 equipment has condition, operating damage, faults and engineer service. | More cycles must create actual service demand; condition/repair should not be cancelled by legendary passives. |

Audit the current checkout again before coding: Codex 2 has separately implemented
Tier5 and is working on management telemetry/UI. This note is not authorization to
modify their active paths, override their work or resume an old implementation queue.

### Across tiers and small boats

The whole-game crew rework should backport appropriate mechanics across tiers. Current
maintenance implementation being Tier5-specific does not meet that whole-game design
by itself. Define smaller-boat servicing and captain/basic-role coverage before imposing
a dedicated engineer requirement. Early boats must operate with their actual berth count.
Skill benefits cannot depend on equipment or positions a hull does not possess.

### Management information needed

Show actual incoming catches, secured cargo, processing work, queues, condition and
service workload. Give units and distinguish actual rates from estimated capacity.
Different stages can use fish/min, kg/min, job time or condition/min as appropriate;
do not pretend all stages scale with the same quantity. Use prominent bars and numbers
to show where work accumulates, rather than expecting players to diagnose animations.

Handling limits and servicing changes are proposed dependencies, not implemented
features or permission to change runtime code now.

## 10. Boundaries and discarded directions

- No invented “deep-line” equipment. Deep channel is a fishing location. Current
  rods have actual upgrades; nets have shallow/deep variants. Cages are confirmed.
- Longline gameplay remains unconfirmed despite the retained F06 concept.
- No bait/chum-centric crew builds. Mo rejects bait as a useful strategy focus.
  This is not permission to remove existing bait code.
- No feeding areas, fish clouds or moving schools: catches are rolls and those
  spatial simulations do not exist. Fixed-position fishing remains a constraint.
- No skill-reset/rearming synergies. Mo explicitly rejected that direction.
- No tiny next-two/three-cast bursts as the defining purple/gold ability pattern.
  Keep the already selected common count-based abilities.
- No reroll-based legendary packages, arbitrary sale multipliers, processing-deadline
  premiums or empty-basket cash/catch rewards as substitutes for coherent fishing work.
- No free reduced-wear Fisher legendary passives that erase engineering pressure.
  CREW090 later permits considering wear reduction as the technical Engineer's
  specialty, earned through actual servicing and bounded rather than permanent immunity.
- Discarded **Master Netter** half-soak/capacity/reduced-wear package is superseded by
  Back-to-Back. Do not resurrect it because it was briefly selected earlier.
- The earlier **Clear Deck** bonus-catch and **Fresh to Market** timed sale-premium
  passives were rejected. Neither belongs to Back-to-Back.
- No extra simultaneous rod takeover that displaces another fisher. The proposed
  twin-hook idea occupies its owner's single rod and is still unselected.

## 11. Pickup checklist for the future build

1. Read latest `comms.md`, instructions, this document and current source. Identify
   active owners and inspect the delivered Tier5/management state before editing.
2. Keep Back-to-Back; retain Cage Foreman's endorsed tending capability. Get targeted
   feedback on Twin-Hook and unfinalized cage passives/numbers, without replaying all
   earlier common/rare selections.
3. Make one consolidated workload model: arrival frequency, batch sizes, carrying
   effort, processing jobs, storage, tool uses, condition damage and service time.
4. Reconcile global role ownership and actual berth counts. Decide the future-dependent
   F06 longline card and early-tier maintenance/captain coverage explicitly.
5. Define stacking, attribution and edge cases. Do not multiply overlapping speed
   bonuses into arbitrarily short cycles or declare an unchosen stacking formula final.
6. Define fixed level progression, unlock/milestone behavior, per-voyage wages,
   acquisition and duplicate rewards. None of their exact curves are approved yet.
7. Continue deckhand and engineer cards with Mo's participation. Their identities and
   skills have not been selected; only role counts and broad scope are established.
8. Implement only after Mo authorizes gameplay work. Validate real queues, physical
   jobs, faults, interruptions, storage boundaries and older tiers. Compilation alone
   is not runtime/visual/balance acceptance. Use the project’s isolated validation workflow.

No crew-card code was changed to create this record. No balancing, gameplay tests,
build, install or player acceptance is claimed by this document.

## 12. Common Deckhand batch — alternatives and selected result

CREW082: Mo asks for all blue Deckhands together. These are three alternatives per
card, not three skills on each card. Every final blue has one automatic personal
active and no passive. The alternatives below were presented as drafts.
Mo subsequently selected **D01A, D02C, D03A, D04B, D05A** (CREW083):

- D01: every third loose-fish pickup takes half the pickup time.
- D02: first three loaded trips each voyage walk25%faster.
- D03: every third delivery takes half the stowing time.
- D04: every third basket trip can carry25%more weight, pending bounded carrying.
- D05: every third processed fish takes half the processing time.

Those five are selected. Unchosen alternatives are retained below for history only.

Deckhands cover collection, transport, stowing and processing. They do not catch
fish, retrieve fishing gear as their card role, repair equipment, or create income
bonuses. Current legacy net-operator roles must be migrated explicitly later.
These modest personal work bursts should help a particular stage, not erase all
downstream bottlenecks. Durations marked halved mean 50% less time; walking boosts
are rates. Skill counters belong to the individual and reset per voyage in this
draft. Duty changes do not delete fish or interrupt already claimed loads unsafely.

| ID / proposed identity | A | B | C |
|---|---|---|---|
| D01 Quick Hands — loose-fish collection | Every third loose-fish pickup takes half normal pickup time. | First three loose-fish pickups each voyage take half normal pickup time. | Every third pickup can gather two nearby loose fish in one pickup, within normal carrying weight limits. |
| D02 Deck Runner — transport | Every third loaded trip walks25%faster. | After every third delivery, the next empty return toward a collection job walks50%faster. | First three loaded trips each voyage walk25%faster. |
| D03 Quick Stow — unloading into hold | Every third delivery takes half normal stowing time. | After personally stowing a net load, their next loose-fish delivery takes half normal stowing time. | Their first net-load delivery each voyage takes half normal stowing time. |
| D04 Basket Hand — net-basket collection | Every third net-basket gathering action takes half normal gather time. | Every third basket trip can carry25%more weight than their normal carrying allowance. | After personally delivering five loose rod fish, their next net-basket gathering action takes half normal gather time; then the counter restarts. |
| D05 Prep Hand — processing | Every third fish they process takes half normal processing time. | Personally delivering a catch load arms one half-time fish-processing job; at most one charge held. Further deliveries do not stack charges. | First three fish they process each voyage take half normal processing time. |

D01C and D04B depend on the proposed bounded-load carrying foundation. Current net
unloading has effectively whole-batch transport; do not pretend a25%load allowance
is meaningful before limits exist. Gathering2fish is never permission to exceed
the weight allowance. A loaded trip runs from pickup/gather to successful stow;
changing routes cannot farm extra activations. D03 discounts only stowing, D01/D04
only gathering, D02 only walking, and D05 only processing, not its input/output moves.
Mixed-role options D03B/D04C/D05B intentionally reward completing an actual support
job before boosting the other job. Jobs still follow player-assigned duties.

Current crab catches go straight to storage, so do not automatically apply loose-fish
or basket carrying effects to cages without an explicitly chosen handling change.
Processing effects can apply to eligible crab processing through the ordinary job.
The choices above supersede the original unselected status of this batch.

## 13. Rare Deckhands — three draft cards for batch review

CREW083: Mo requests at least two processing-only purples. Draft allocation is two
processing specialists plus one transporter. D06A and D08A were subsequently selected;
D07's original alternatives were rejected; revised D07A in section14 is now selected. Each has
one personal automatic signature (choose A/B/C) and one team passive. No fishing,
repair, extra sale-value or bait skills. Names and numbers remain tunable.

Important new dependency: Codex2 DASH082 now has Mo's explicit instruction to build
catch→inbound haul→processing→outbound haul→hold on processing-equipped boats;
smaller boats bypass processing. This supersedes the older source observations above
as the intended pipeline. Implementation is peer-owned and in progress at this note.
Do not treat these card drafts as instructions to alter its code or assume every
detail already delivered. A card that finishes processing faster must still feed a
finite finished-output queue awaiting carriers.

### D06 — Batch Cutter, processing only

**Selected: A**, including team small-fish processing15%faster (CREW084).

Personal signature alternatives:

- A: process three small fish together in the normal processing time for two.
- B: process two small fish together in the normal processing time for1.5fish.
- C: process up to three small fish together, each taking25%less processing time
  inside the batch; supports mixed eligible species without requiring a full trio.

Proposed team passive, same for all alternatives: all processors process small fish
15%faster. Small/big classification should use existing specimen-size classes rather
than invent a global kg threshold during this draft; exact eligibility needs signoff.
Batch grouping does not require same species in this proposal. A/B need enough eligible
fish; if a full batch cannot form promptly, work normally rather than wait forever.
Define automatic fallback timeout later. One operator/station, not theft of a second
processor's slot. All fish must reach the table and be carried onward. Processing
time excludes inbound/outbound hauling; no exemption from per-fish tool workload.
Creates processing-output bursts and rewards net/small-fish supply plus outbound support.

### D07 — Heavy Cutter, processing only

**All original alternatives below rejected.** Mo says big fish usually arrive singly,
so queue/streak requirements do not fit. Revised alternatives are in section14.

Personal signature alternatives:

- A: consecutive large-fish processing jobs build10percentagepoints of personal
  processing-rate bonus per completion, up to40%. Bonus applies to subsequent jobs;
  resets on changing duties or being starved of eligible input for10seconds.
- B: while at least two large fish await processing, own large-fish processing is
 30%faster. Finish any started job consistently if queue occupancy changes.
- C: consecutive large fish of the same species process40%faster after the first;
  changing species or duties resets the chain. Input selection follows assigned
  processing filters/priority; no species generated/replaced to feed the chain.

Proposed team passive, same for all alternatives: all processors process large fish
15%faster. Uses existing large-specimen class eligibility, independent of species
rarity. No claim current processing duration increases with weight; these skills
accelerate actual eligible jobs. Provides a contrasting large-fish supply specialist
to Batch Cutter. Continuous input needs inbound workers, while faster completion
increases outbound handling pressure. Does not make this worker a hauler.

### D08 — Heavy Lifter, transporting only

**Selected: A**, including team loaded walking15%faster (CREW084). Extra capacity
still depends on defining bounded carrying; exact interaction of personal slowdown
and team movement bonus is not a new approved stacking formula.

Personal signature alternatives:

- A: personal carrying allowance is twice normal weight; while carrying above the
  normal allowance, walk20%slower. Work normal loads normally if less cargo is ready.
- B: personal carrying allowance is1.5times normal weight, with normal movement rate.
- C: personal net-basket loads can weigh twice normal allowance, but gathering and
  stowing overloaded loads take25%longer. Does not increase loose-fish/output allowance.

Proposed team passive, same for all alternatives: all catch carriers walk15%faster
while loaded, applying to inbound and outbound jobs (captain included). No effect
on processing, fishing or repair. These signatures trade trip count against carrying
or handling effort; they are not free cargo teleports. Raw/finished destinations and
individual fish identity remain correct. All depend on bounded carrying allowance,
not current unlimited whole-basket transport. Do not gate ordinary intelligent routing
behind a rare card. Even faster transfers can create input/output bursts and block
behind a slower processing line or full hold. Overload only when cargo is available;
never wait forever to fill a load. Exact cargo packing, indivisible heavyfish rules
and job limits need definition against DASH082 delivered baseline.

D06A and D08A, including their listed passives, are selected. Revised D07A and its
team passive in section14 are also selected; all three Rare Deckhands are chosen.
Exact stacking, queue occupancy, cancellation and size eligibility need definitions
before coding. The selected five Common cards remain unchanged.

## 14. Revised single-big-fish processor — D07A selected

**Selected by Mo (CREW085): A Heavy Cutter**, with the team passive below.
Their own large-fish processing takes half normal processing time; all processors
process large fish15%faster. Applies even when only one big fish arrives. These
are processing effects, not carrying, free catch, additional sale value or repair.
Other alternatives below are retained as unselected history, not additional skills.

CREW084: useful on the very first individual big fish. No requirement for multiple
big fish in the queue, a continuous large-fish supply or a same-species streak.
Three alternative personal signatures, with one proposed team passive:

- **A — Heavy Cutter:** own large-fish processing takes half normal processing time,
  always. One fish is enough. All inbound/outbound carrying and tool workload remain.
  This is the simplest direct processing specialist; no new portion representation.
- **B — Progressive Fillet:** process one big fish in two stages. First half becomes
  finished outbound cargo at halfway through processing; second half finishes at
  the end. Total processing work is unchanged. Carrier can start moving first output
  while processor finishes the rest. Newly proposed partial-output rule, not existing
  functionality. Rewards coordination rather than creating extra catch/value.
- **C — Shared Cut:** divide the one big fish into two processing portions, enabling
  a second processor to work on one while the owner handles the other. Uses two real
  workers and available station positions, each performing their share; same total
  processing work. A second worker is the cost, not a second big fish requirement.
  If solo, process normally. New collaboration rule, not existing functionality.

**Selected team passive with A:** all processors work15%faster on large fish.
The numerical interaction of personal half-time and team rate modifiers still needs
the global stacking rule; do not silently invent a final combined processing time.
The card remains processing-only. B/C require exact mass/parent identity and value
conservation. Portioning must not count as extra fish/catches/skill triggers, reset
freshness, reroll size/species or alter the original specimen's total sale entitlement.
No free table positions, teleporting cargo or finished-output overflow. Respect
finite queues; define stalls and partial-job cancellation against actual DASH082
pipeline before implementation. Do not assert a large-fish kg-time penalty exists.

## 15. Two legendary Deckhands — six new core-ability drafts

CREW086: Mo requests both legendary Deckhands at once, three new rule-changing ideas
for each, preserving bottlenecks. All six below are unselected alternative core
signatures when originally proposed. Mo subsequently chose custom D09D Power Lifter
and rejected all D10 alternatives; see sections16–17. Choose final direction before completing its1active2passive or
2active1passive package. No new percentages/passives finalized by these drafts.
All execution automatic under assigned duties. Inputs, cargo mass, work, costs,
source/destination and finite queues remain real. No fishing or engineer takeover.

### D09 — handling/logistics legendary, choose one direction

**A — Relay Foreman.** While deployed and assigned logistics, enables loaded-cargo
handoffs among deckhands at a designated reachable transfer point. One worker covers
landings-to-table, another table-to-hold, or workers split a long carrying route.
Foreman is an actual working relay participant. Loads move physically, every transfer
takes handling time, and a handoff requires a receiver or finite transfer buffer.
No extra workers, faster feet by fiat, cargo teleportation or raw-to-hold shortcut.
Helps divide routes and sustain feed/clearance; tying up staff in relays can starve
processing or other collection. Stalls propagate if receiving worker unavailable.
Exact point/standing positions and small buffer limit are new design, not current
universal staging mechanics. Do not gate ordinary route correctness behind rarity.

**B — Team Lift Captain.** Enables this worker plus one assigned deckhand to carry
a heavy fish/load together above an individual's carrying allowance. Both workers
are occupied for pickup, the loaded route and set-down; not a doubled capacity aura
for every worker. Pair has finite combined allowance, slower loaded movement and
valid approach/path requirements. Potentially removes a heavy-load transport barrier
and consolidates net-batch trips, at cost of abandoning parallel smaller deliveries.
No creation of giant fish or mandatory new cargo types. Requires bounded carrying,
clear rules for indivisible oversizedfish and actual paired-route clearance. Rates
and capacity multiplier unselected; must be worthwhile versus two ordinary workers.

**C — Live Receiver.** Works alongside an assigned net fisher, receiving successive
portions into a real carrying load as the fisher retrieves the net, rather than
waiting for the whole catch to land before pickup. Can depart with first load while
retrieval continues. Waiting/receiving occupies the Deckhand; fisher still does all
gear retrieval. Load is bounded and excess stays in normal basket, blocking as usual.
Not an invisible funnel: absent receiver means ordinary landing. Requires explicit
staged catch release, claims and catch conservation. Different from replacing the
chosen net legendary: this is a separate support-worker collaboration and can pair
with Back-to-Back. Improves overlap at the price of a dedicated receiver, potentially
leaving finished output or rod catches waiting. Do not promise current net controller
already releases intermediate portions.

### D10 — processing legendary, choose one direction

**A — Mobile Filleter.** Can process landed raw fish at a valid collection location
using a personal field-preparation job, rather than requiring inbound delivery to
the main table. Owner stands/works there; finished fish still need collection and
carrying to the hold. Field processing should take longer than table processing
(exact penalty open), and use a finite existing-source area/output allowance, not
an invisible unlimited new rack. Frees table/inbound journeys, but ties a processor
to the catch source and may obstruct its catch queue until outbound helpers clear it.
Actual processing work/value entitlement unchanged. New prepared-at-source state,
safe work position, personal kit presentation and routing exception required. No
automatic processing while walking or skipping all transport. Mainly supports raw
fish actually landed on deck; do not assume a new crab handling stage exists.

**B — Prep Foreman.** While working the main table, opens a simple pre-cleaning
assistant job to other deckhands. A carrier can deliver raw input, spend actual time
pre-cleaning a fish at a valid assistant position, then resume carrying. Foreman
performs the final cutting/preparation at the table. This splits one job's total
work between workers without reducing it for free; assistant labor releases some
of the specialist's time, at the cost of incoming/outgoing carrying time. It works
on a single fish and does not need multiple big specimens. Finite pre-cleaned WIP
queue, no final completion without actual finishing work. Foreman is an actual
processor, not idle support. New assistant duty, stage attribution/work split,
physical work position and pipeline state required. Can generate a new bottleneck
when too many carriers are helping prepare and nobody clears finished cargo.

**C — Passage Processor.** Allows this processor and explicitly assigned support
carriers to continue their ordinary pipeline jobs during existing travel/return
time. No new fishing underway, extra travel duration, free processing or automatic
salvage. Existing queues/cargo persist, staff must do normal work, and finite voyage
travel time caps the opportunity. Lets player depart a ground with unfinished
backlog and plan to finish some en route; too much backlog remains unfinished.
Requires new underway crew-job simulation/lifecycle/ownership, preserved mass and
clear harbour-arrival handling. Current queue salvage on return is not equivalent
to real processing/carrying. Do not allow free infinite-worktime by orbiting harbour
or imply arrival magically upgrades unfinished fish. Fuel/time rules still apply.
This is explicitly a team-support signature, not a personal processing-speed bonus.

### Selection and passives next

D09A/B/C unselected; custom D09D selected in section16. D10A/B/C rejected; new bulk
processing direction proposed in section17. Then design their
remaining skills within the established rarity slots. Proposed abilities change
work routing, available jobs or working window rather than award larger percentages.
Support bonuses, if chosen later, must stay in their work fields and preserve other
stages' capacity limits. Global core improvements must not be sold back as rare-only
permission to perform ordinary safe routing or basic carrying.

## 16. Selected handling signature — D09D Power Lifter

CREW087: **Mo's custom ability, selected in direction with explicit dispatch rules.**
Full legendary skill package/passives remain open.

### Ability and load unit

Can carry the remaining available contents of **one station in one trip, regardless
of weight**, including a heavy net basket that ordinary bounded-load workers cannot
clear in one go. This is a personal carrying exception, not an increased boat/table
capacity or whole-boat collection sweep. No arbitrary slowdown added to Mo's rule.

- One station's uncarried eligible cargo, with a common proper destination. Define
  whole-station pickup as a snapshot when pickup commits; later catch forms next load.
- Already-carried fish belong to their current carrier and are excluded.
- Raw cargo still goes through processing on equipped boats; finished cargo goes to
  hold. Do not merge incompatible raw/finished jobs into an unlawful direct-storage load.
- Does not remove ordinary gathering, movement or stowing work, or auto-process fish.
- Handling throughput beyond weight allowance is not an unselected instantaneous
  pickup/stow bonus. Exact handling time still needs workload-model definition.
- A full processing destination/hold still blocks delivery; preserve all remaining
  cargo safely. No silent deletion, infinite destination capacity or magic overflow.

### Heaviest-load priority and safe preemption

When free, select and reserve the **heaviest reachable eligible station load** using
actual cargo weights, accounting for jobs/destinations and already carried cargo.
Only the station assigned to this worker gets the reservation; ordinary workers
remain free to work other loads/tasks.

- Other crew walking toward that load or reserving it before pickup disengage and
  re-plan elsewhere as soon as Power Lifter becomes available and claims it.
- Crew with fish/load already in hand finish their proper delivery, then choose
  another task. Do not reverse, drop or steal their carried fish.
- Power Lifter takes the remaining station contents. Existing batch-owner/claims
  require atomic release/transfer so no fish duplicated or orphaned.
- No constant mid-trip retargeting as weights change; one selected job is committed.
- If Power Lifter is busy/unavailable, ordinary crew keep working normally. No idle
  workers holding every heavyload indefinitely in anticipation of their return.
- Re-plan to real available work; if none exists, waiting is explicit rather than
  oscillating between the same reservation/claim.

The route surge can clear a full basket and restart fishing quickly, but dumps a
large input into processing. Supporting the next stage is still necessary. Net
retrieval stays with fishers, servicing with engineers. Current whole-basket transport
must become bounded for ordinary workers before this legendary is meaningfully unique.

## 17. Replacement processing direction — D10 Bulk Processor

**Latest rule: CREW088, selected whole-fish threshold batching below.** This
supersedes the original hard-cap and small/big-class proposal retained afterward.
Insufficient-stock policy selected in CREW089: process available fish immediately.
Complete timing and passives remain open.

### Mo's corrected batching rule

Use actual fish weight, not specimen class/species rarity. Start with the heaviest
available eligible fish. A fish heavier than5kgforms a complete batch alone.
Otherwise fill the batch with whole fish until total weight is **strictly above5kg**.
The final fish is the **smallest available fish that takes the current batch over5kg**.
The5kgvalue is an overshoot threshold, not a hard maximum. No fish splitting or trimming.

Examples explicitly supplied by Mo:

- Available4.9kg+4.9kg only: process both together,9.8kg.
- Available4.9kg+4.8kg+0.5kg: choose4.9+0.5=5.4kg; leave4.8forlater.
- Any singlefish>5kg: process thatfishalone.

Proposed deterministic generalization, preserving those examples: after heaviest
starter, if a remaining fish can cross5kg, take the lightest such fish and finish.
If none can cross yet, add the heaviest remaining fish and repeat. For example,
3+2+0.2 yields5.2kg, not a stop at exactly5. The intermediate fill order is a
derived proposal where Mo did not give an explicit many-smallfish sequence; retain
the final-smallest-crossing requirement and confirm edgecases before coding.
Pick from genuinely eligible/unreserved processinginput, preserving exact weights
and cargo identity. No repeated recalculation from rounded display weights.

**Selected shortage policy (CREW089): execute immediately.** At job start, use the
currently eligible/unreserved fish. If enough weight exists, form the above-threshold
batch under the heaviest-starter/smallest-crossing-finisher rule. If all available
fish total5kgorless, process those fish now as a partialbatch. No batching timer,
minimumfill requirement, delay waiting for arrivals or additional underfill penalty.
Exactly5kgavailable also processes immediately; if another eligible fish is available,
use the smallest crossing fish under the fullbatch rule. Emptyinput has nojob; no
zero-fish triggers. Later arrivals belong to the next job, not an ever-growing batch.

One normalprocessingcycle percompletebatch remains the timing proposal from the
preceding turn, not explicitly restated/locked by Mo's weight-rule correction.
The previous comparison claiming goldnecessarilylessspecialized on a lonebigfish
is historical; final speedpassives/timing have not been chosen.

### Earlier proposal history — superseded where contradicted above

CREW087: Mo rejects all three earlier processing legendary directions and asks about
current weight limit. **Actual source:** one fish per processingjob, irrespective
of kg, with normal Preparingfish basework4.5seconds plus0.15input/0.15output actions.
Person.Speed and work multiplier modify elapsed time; do not promise4.8wallseconds.
Two processing positions/jobs can run concurrently on current equipped hulls.
No perjob5kgcap exists; total processingqueuekg capacity is a separate restriction.

Mo proposes either **one big fish OR5kgofsmallfish all at once**. Develop as:

- Personal job accepts one largefish, or a batch of whole smallerfish totalingup5kg.
- No requirement for multiple bigfish, fivefish exactly, or a full5kgqueue before
  useful work. Use available eligible fish; any optional short batching wait needs
  definition and must not starve a quiet boat.
- Define large/small classification with Mo. A single indivisible fish above batch
  allowance must remain processable solo; never strand a non-big-class heavy species.
- Current proposal: one batch uses **one ordinary fish-processing job's worktime**,
  not a separate full job per fish. This timing is proposed, not yet approved.
- No splitting fish merely to hit5kgexactly unless separately chosen. Each source
  specimen retains mass, identity, freshness and full normal value; no extra catches.
- Batch reserves all its fish atomically from actual ProcessingInput and emits
  them as finished output, leaving normal outbound carrying/storage work.
- A single position/operator, not an implicit theft of both table positions.
- Surge of finished fish can overwhelm outbound carriers. Input/output buffers
  remain finite; should work/condition burden scale by kg/fish, define explicitly.
- A lone bigfish in normaljobtime is less individually specialized than selected
  Rare HeavyCutter's half-time. Gold's proposed strength is bulk flexibility; do not
  silently give it the Rare skill too to force universal rarity dominance.

D10 whole-fish threshold direction selected as above; timing, levelgrowth and team
passives are unselected. D09 remaining
legendary skills also unselected. Do not invent a full approved package from this note.

## 18. Engineer collection — eight unselected drafts

CREW090: Mo's requested structure is three blue system specialists, three broadly
capable purple mechanics, and two golds (crew/boat support and technical maintenance).
These are proposals, not selected cards or implemented behavior. Three iterations
per card below. Blue has one automatic operating profile, no passive. Purple chooses
one signature and one listed proposed team passive. Gold core directions first;
remaining skills will be fitted to1active2passives or2actives1passive after selection.

Current engineering facts: eight tracked rods/net/buoy positions on Tier5, normal
service3basework restores14condition, faultrepair7basework restores45and clears fault.
Normal service already permits ongoing operation. Basic fault/lowestcondition priority
is baseline, not a unique card. Processing tables/carrying equipment currently lack
wear tracking. No existing electrical-power distribution is assumed by these drafts.

### Common blue — one system-biased tuning profile each

E01 Rod Rigger targets rod reeling, E02 Winch Tuner targets net hauling, E03 Cage
Mechanic targets cage recovery. Each supports routine normal servicing as its role.

For EACH card choose one profile strength:
- A: target retrieval rate20%faster, other two fishing methods5%slower retrieval.
- B: target retrieval rate30%faster, other two methods10%slower retrieval.
- C: target retrieval rate40%faster, other two methods15%slower retrieval.

One profile counts as one signature with its cost, not a separate bonus passive.
This is a proposed automatic method-biased rigging rule maintained by assigned
engineer work, not actual electric-power rerouting or permanent global basespeed.
Do not speed biological bite/soak waits by claiming a mechanic changes fish behavior.
Profile activation/expiry and multiple engineer/profile stacking need decisions.
No penalty to carrying/processing/repairs hidden inside other-method retrieval.
More cycles still spend uses/condition; no free durability bonus. Card bias is
for a concentrated strategy at opportunity cost to other fishing methods.

### Rare purple E04 — All-Round Mechanic

Personal signature alternatives:
- A: routine maintenance work25%faster on all gear; no faster fault repair.
- B: each normal maintenance job restores25%more condition on any gear; same worktime.
- C: a normal service also banks one brief follow-up visit on that rig: the next
  visit completes faster, but only after actual first servicing. Exact visit bonus
  and expiry unselected; no free repeated recursion.

Proposed team passive: all servicing crew/captain walk10%faster on actual service
routes. Does not speed unrelated fishing/carrying/processing. Can support other
engineers without requiring multiple hired engineers to function.

### Rare purple E05 — Fault Specialist

Personal signature alternatives:
- A: a short temporary repair returns broken gear at reduced efficiency, but a full
  repair still needs doing later. Proposed2basework bypass/50%efficiency, tuning open.
- B: normal repair becomes two stages, partial operation after stage1 and normal
  operation only after stage2; total repair work is unchanged.
- C: after personally repairing a fault, own next routine maintenance on that rig
  restores twice normal condition. One follow-up only, then flag clears. No faster
  repair, free future fault clearance or permanent immunity; actual follow-up needed.

Proposed team passive: all routine maintenance restores10%more condition per visit.
New bypass/staged/reserve states require implementation; current fault is binary.
No spontaneous auto-clear, condition reset or removal of actual operating costs.

### Rare purple E06 — Equipment Optimizer

Personal signature alternatives:
- A: gear personally serviced gains15%faster retrieval for next3completed uses.
- B: gear personally serviced gains10%faster retrieval for next5completed uses.
- C: one personally tuned rig gains25%faster retrieval until engineer tunes another
  rig; old rig loses its boost. Others work at normal rates.

Proposed team passive: all servicing crew perform routine maintenance10%faster.
All signatures work across rod/net/cage retrieval instead of favoring one method.
Earn tuning through actual service work, not passive global free overdrive. Extra
cycles increase condition/use demand. One rig's boost cannot recursively stack.
Do not claim existing equipment has a tune-state. Tuning should not change species,
specimen rolls, price, processing speed, boat fuel capacity or wear immunity.

### Legendary E07 — Support Engineer

Core direction alternatives, remaining slots open:
- A Care Foreman: enables brief station-care actions by operating crew between
  production jobs. Crew spend real productive time performing a small condition
  touch-up on used gear, engineer still needed for larger work/repairs. Bounded
  recovery must remain below operating/service needs; no self-sustaining no-wear
  loophole or sale of ordinary cross-role basic service as a gold perk. New automatic
  inter-job care action, not a passive global condition regeneration. Applicable
  gear/crew positions and opt-in persistent duties need definition.
- B Service Coordinator: engineer and that station's assigned operator can perform
  a joint service, splitting normal work between them. Faster elapsed servicing
  costs operator production time; total work not deleted. Requires both physical
  workers and clear gear availability. No extra ghostworker or unnecessary join
  if second person would finish their ordinary job sooner. Distinct from the
  baseline ability for each person to service alone.
- C Parts Scavenger: engineer can take condition/parts from an explicitly idle
  compatible spare rig to restore a working rig, spending real transfer work.
  Donor loses condition and becomes less ready for later use; no condition created.
  Same-method compatibility, finite transferable amount and physical visits matter.
  Never cannibalize a rig mid-use or without a selected persistent donor policy.
  If no suitable donor exists, do ordinary maintenance. Does not repair all gear
  without costs or assume a universal rod-to-net spare-part economy.

These are explicit team/support signatures, engineer also performs actual normal
maintenance. Support passives remain open; do not grant work speed across every
stage by default and erase the very pressure intended.

### Legendary E08 — Precision Engineer

Core direction alternatives, remaining slots open:
- A Preventive Specialist: actual completed maintenance gives that rig a finite
  protective tune, proposed25%less operating wear for next3uses. No boost from merely
  being aboard; high-throughput rig consumes protection quickly and needs revisiting.
  Never zero wear, no protection against every fault, no same-effect stacking.
- B Service Reserve: can spend actual additional maintenance work on healthy gear
  to bank one finite future upkeep action there. Reserve triggers at a defined
  condition threshold, then is gone. Engineer did work earlier and saved a future
  return trip; this is not free automatic repair or infinite condition regeneration.
  Fault repair remains separate, maximumone reserve perrig and no bank refresh loops.
- C Deep Overhaul: longer stationary service takes a rig out of production, restoring
  condition thoroughly and applying finite wear protection afterward. Work duration,
  restoration and protection unselected; pay real production downtime and engineer
  commitment. Do not imply routine maintenance currently stops gear. Automatic
  upkeep policy chooses timing, no skillbutton or player babysitting each action.

TechnicalEngineer can be excellent at sustaining demanding gear through prevention
rather than just a giant repair-speed number. Finiteprotection/reserves/downtime
keep maintenance essential and create routing/service priorities. No exact effect,
passive package, condition floor, timer or skilllevel milestone approved.

### Dependencies and next selection

No Engineer card chosen yet. Requestedwearprevention is an Engineer-specific proposed
direction under Mo's latest instruction, not repeal of Fisher maintenancefriction.
All prototypes must fit equalrole/level basespeed, pervoyage wages, automaticexecution,
physicalroutes, realwork/capacity and older-tiercoverage. Finalprofilemath, stacks,
servicecancel/fault/reserveedgecases and normalworkerweight limits remain open.
Choose blue variants and purple/gold directions together or byrarity at Mo's pace.

## 19. Engineer baseline reset and partial selections — CREW091

Mo says standard engineer behavior is not yet established for this design, so skills
are hard to judge. Pause new Engineer card drafts. Preliminary Tier5 code exists
but is not authoritative approval of this crew rework's normal behavior. Do not
claim user has already accepted every current implementation parameter.

### User-specified baseline

- Equipment has a maintenance/condition level.
- Engineer walks to equipment below80%condition and starts maintaining it.
- If equipment breaks, engineer must come and fix it.
- Ordinary broken equipment stays stopped until repaired to100%.
- Selected FaultSpecialist5B is the explicit exception: resume halfway through its
  repair while that engineer continues repairing it to completion.
- No manual ability management introduced.

### Concrete baseline proposal to settle before further cards

Faults take priority over routineupkeep. Routineupkeep starts below80and continues
until100rather than stopping immediately at80. Allhealthygear>=80means no newroutine
job, so engineer can wait; do not endlessly chase99to100. Repairs finish at100and
clear fault, not merely applyan arbitraryconditionincrement. Progressvisible in
management/equipmentbars. Routinecareandrepairbothrequire realwalking and occupied
worktime. If interrupted, preserve validprogress; do not make cancellation reset all
work or accidentally unlock a partlyrepaired brokenrig.

These finish/prioritization/interrupt details are coherent proposals consistent
with Mo's baseline; exactrates/damage/faulttriggers stillneed decisions/verification.
No automaticrepairwithoutvisit, remoteconditionregeneration or arbitrarily new
penalties implied. No new globalpowerallocation/temporarytuning overlay needed
to understand the standardrole. Fastergearcreatesmoreoperatingservice demand.

Actualsourcecheckedthisturn selectslowestconditionwithoutan80%entryfilter (even100canbeselected) andrepairswith+45condition;
it does NOT implement latestbaseline. Future authorizedimplementationmust reconcile
this explicitly,notpretendit alreadyworks. No sourceeditednow.

### Card status from latest reply

- E01A RodRigger selected: rodreeling20%faster,net/cageretrieval5%slower.
- E02A WinchTuner and E03A CageMechanic selected after Mo's explicit CREW092
  clarification that2q/3qmeantAforboth. AllthreeBlueengineers nowselected:
  rod/net/cage retrieval20%faster for ownspecialty,other2methods5%slower.
- E04A AllRoundMechanic selected: routine maintenance25%faster acrossequipment;
  previouslylistedteamservicewalking10%faster retained aspackage,subjectfuturebalance.
- E05B FaultSpecialist selected: stagedrepair/operationresumeshalfway,engineerkeeps
  working untilfullrepair. Previousteamroutineconditionrestoration+10%retainedas
  draftpackagebutthisneeds explicitreconciliationwithcontinuous80to100baseline;
  do not silently transformitinto extraoverall speedorinstant100.
- E06 shelved/unselected. Earlieridea wastemporaryretrievalspeedearnedbyservice,
  butMo saysmeaningunclear. Do notcontinueexplainingtune-states asestablishedmechanic.
- E07allthreecoreproposalsrejectedasboring. No supportgoldselected.
- E08B upkeep/reserve direction appealed, but notfinalized; normal80%maintenance
  mustnotbepresentedasGoldonlyability. Revisitafterbaselineagreed.

Retainallselectedotherroles andnorepeatedcardquestionnaire. No Engineer remaining
passives/levels/wagesfinalized bythisbaselineconversation. TwoGoldengineerabilities
remainopen;noqueueofrejectedideasshouldberesumedwithoutMo'sdirection.

## 20. Whole-game machinery first — CREW093

Mo clarifies GoldEngineers should relate to future higher-tier machinery and that
NO future machine list is decided. Do not ask Mo to supply a predetermined equipment
plan or mistake oldartistassets/GAMEPLAYaspirations for approval. Research real
equipment and propose what nextfive tiers could contain.

See [FUTURE-MACHINERY-DESIGN.md](FUTURE-MACHINERY-DESIGN.md) for researched,
UNSELECTED Tier6–10 proposal: poweredhaul/jigging, conveyorgrading, machineprocessing,
longline/cage specialization, integrated dualroutes/sharedpower. Includesprimary
manufacturer/FAOsources, fixedpositionfit, finitequeues/staffing/condition/capacity,
optionalcoldchain/currentpreparedfreshnessconflict and machine-linkedGoldEngineer
directions. Neither futuremachines nor Engineer6/7/8 were selected by this work.
Allselectedcrew retained. No gameplay implementation authorized by designdiscussion.

## 21. Electrical-only engineering — latest scope, CREW094

Mo explicitly changes the whole-game design: remove engineering wear from rods,
nets and comparable fishing gear. ONLY electrical components are maintained by
engineers. This section supersedes prior generic equipmentwear andcardstrain rules.

### Maintenance boundaries

- Bare rods, net cloth, cages, hooks and other manual fishing tackle have no Engineer
  condition bar, routine servicing or engineering breakdowns.
- Electrically powered reels/haulers, conveyor drives, sorter controls and processing
  machine drives may have electrical condition. These machine types remain proposed;
  do not reclassify all existing haulingequipment as electrically driven without
  defining it. A hydraulic unit fits only via a chosen electrical power/control unit,
  not a separate hose/rope/mechanicalwear system smuggled back into the rules.
- Start with one readable electricalconditionbar per poweredunit, not independent
  counters for every wire, motor and controller.
- Engineer walks to electricalunits below80% and services them. Prior proposedfinish100
  still baselineproposal; ordinaryfaultedunit stops untilrepairedto100,selectedE05B
  exception allowsresumehalfwaywhilerepaircontinues. Actualrates/faulttriggeropen.
- Physicalinput/outputtransport,processing,storage and manual alternatives remain.
  An electricallyfailedmachine's poweredfunction stops, not everymanualjobonboat.
- Boatswithout electricalmachines do notneed an engineer to keep manual tackleworking.
  Earlytierengineering usefulness follows actualelectricalequipment, not invented
  rodwear simplytoforceawageslot.
- No new battery/fuel/electricalsupply economy automatically approved bythischange.
  Machinepowerbudgetstillafutureproposal,separatefromcondition.

### Operating pressure and existing selected cards

More productivecycles/load can consume more electricalcondition on apowereddrive;
do not damage ordinarygearforbeingused. Netuses/consumablestockambiguity is asked
separately becauseMo'sselectedF08depends onit. KeepF08decisionpendingthatclarification.

Back-to-Back keeps its personalqueueability and acceptednet-speedpassives. Itsold
proposed+50%genericpersonalhaulwear MUSTNOT damage manualnets. If electricdriveused,
consider extra driveworkload as tuningproposal,not alreadyselectedconstant. A manual
Back-to-Back build pressuresdeckhands/processingwithoutan artificialengineerrequirement.
PowerLifter remainspersonalwhole-stationcarryexception,not an electricalsystem.
OtherFisher/Deckhandselectedsignaturesretained; noautomaticmass/economychanges.

### Suggested Engineer remap — all new scopes provisional

Preserve agreed profile strength20%targetfaster/otherfamilies5%slower as startingpoint,
but oldRod/Net/Cage-specificBluefamilychoices need explicitremapfeedback:
- E01 Retrieval Electrician: powered fishingreels/haulers,includingchosen jig/net/cage
  machines. No boost/penaltytoordinarymanualrodoperations.
- E02 Processing Electrician: electricalgutting/filleting/preparationmachines.
- E03 Handling Electrician: conveyor/sortingdrives.
These are proposedreplacementfamilies,notsilentnewselectedcards. Costs applyonly
otherpoweredfamilies; no mechanicalpenalty on manualgear or fictionalelectricbus.

Retain E04A selected25%fasterroutineupkeep now electricalonly; servicingwalkpassive
samefield. Retain E05B selectedpartial-restartrepair on electricalfaults; its
condition-restorationpassive needs reconciliationwithcontinuousmaintenancebaseline.
E06 unselected: efficiency specialist reducing supportedmachines'electricalpower
demand is a possible replacement, conditionalonpowerbudgetselection. Do not claim
existingboatpowerdrawsystemor reviveunexplainedtemporaryrigspeedboosts.

Gold E07 unselected support focus: operating/control capability for machines,
potentially one eligiblefedmachine can run withoutcontinuousoperator at extraelectrical
strain. CONDITIONAL ongenuinemeaningfulnormaloperatorwork andphysicallyautomaticfeed;
neverinventuselessoperatorjob merelytojustifycard orskipmanualfeed/outputs.
Gold E08 unselected technical focus: engineer spendsactualpreventivework to earn
finite reducedelectricalwear or bankoneupkeepreserve. Protection is not generic
physicaltackledurability,a freeglobal aura orordinary80%routine soldasGold.
Both remainroles/directions,notfinalabilitypackages; exactchoices requiremachine
contracts. Prior8Bdierctionlikednotlocked,prior7draftsrejected.

### Documentation status / next decisions

No gameplaysourceedited. Currentruntime stillhasgenericrod/net/buoycondition and
doesnotimplementthisscope. Future implementationrequires explicitmigration/removal
ofoldcondition/forecast/UIservicingtargets; preservenetuses untilMoanswersseparately.
Confirmnewmachinefamilycardscopes andmachineoperatingcontracts beforefillingremaining
skills. Do not restartFishers/DeckhandsquestionnaireormarktheseEngineerproposalsselected.

## 22. Net-use clarification — CREW095

Confirmed by Mo: normal nets have unlimited uses; each deep net has3uses.
Consumable deep-net uses are distinct from engineer-maintained electricalcondition.
Deep-Net Saver F08 remains selected: ownsuccessfuldeepnethaulspendnouse,failedhauls
stillspendone,teamdeepnetcapacity+15%. Rods/netcloth/cagesdonotregainengineeringwear.
This resolves all pending-net-use questions in section21 and earlier discussion.
No runtime netstock/save/economy changes made; only design record updated.

## 23. Electrical engineer alternatives — CREW097

Mo requests three options for each of the eight engineers, with one whole-boat
support legendary and one maintenance legendary. See [ENGINEER-OPTIONS097.md](ENGINEER-OPTIONS097.md).
All 24 alternatives, shared passives and numbers are UNSELECTED proposals; prior
selections remain recorded pending replacement choices. Scope is electrical machines
only. No new machine roster, power economy or gameplay implementation is approved.
Power Lifter removes carrying weight limits but retains travel/delivery and downstream
capacity; engineer abilities must account for finite labor, processing, output and
condition. A fully supported build is allowed to work well; no forced random failures.


## CREW099 — latest machinery direction: enable new crew operations

Mo rejects the live-catch tank suggestion as the desired foundation. Big machinery
should unlock new income activities: oversized catches (Mo gives sharks/whales as
examples), supporting scuba-diving operations and a scuba-diver crew role, launching
or supporting a small boat beside the main vessel so the captain can spearfish,
and craning oversized catches aboard. Machinery makes new human work possible;
it does not replace fishers, hauling hands or processors with robotics.

This is approved direction, not approval of exact species, tier order, hull sizes,
machine specifications, staffing numbers, oxygen economics, or individual cards.
The historical Tier6-10 machine ladder and CREW097 engineer options are not the
current implementation plan. Do not substitute live-tank upkeep for this direction.
Electrical components remain the engineer's maintenance scope. Normal nets have
unlimited uses, deep nets three uses. Existing selected cards remain intact.

Proposed game-design chains to develop with Mo:
- Diver + human support + dive-support equipment -> underwater retrieval -> deck
  handling/storage. Air preparation/turnaround and recovery capacity are candidate
  bottlenecks, not selected real-world diving procedures or automatic fatal hazards.
- Captain's small-boat sortie -> spearfishing -> human rigging of oversized catch ->
  powered crane recovery -> onboard handling/processing/storage. Engineer sustains
  electrical equipment; deckhands retain rigging/receiving jobs. Exact operators open.
- Several operations sharing one recovery crane/landing area could compete for real
  recovery time. Modules and crew berths constrain simultaneous activities. Existing
  rods/nets/cages remain legitimate builds; no compulsory checklist of all new modules.

Important boundary for later approval: water-to-deck recovery is a different job
from Power Lifter's already-landed one-station cargo transport. Preserve his selected
unlimited-weight station pickup; do not silently invent a carrying cap. Whether he
also handles new oversized landed objects, and whether Bulk Processor handles them,
requires explicit eligibility decisions before implementation. Ordinary caught-fish
rules cannot silently change to invalidate selected legendary abilities.

Engineer design now follows expedition support, recovery/lifting and electrical
readiness; exact card families wait for these operation contracts. Diver roster size,
rarities, permanent role versus card specialization and levels remain open.

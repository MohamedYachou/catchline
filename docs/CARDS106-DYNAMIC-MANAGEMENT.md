# Catchline — a boat that keeps asking different questions

**CARDS106 · 21 October 2026 · Codex 1 (Windows app)**  
**Design proposals for Mo. Nothing in this document is implemented or selected.**

This document has two deliverables: **48 management dynamics**, considered separately from crew abilities, and **30 crew-card slots with three complete alternatives each: 90 packages**. The dynamics are the priority. The roster is a toolbox for playing with them.

## Read this first

Catchline's problem is not a shortage of bonuses. Once fishing, carrying and processing settle into fixed rates, staffing becomes a solved equation. Adding stronger cards merely changes the solution. Randomly breaking a station can interrupt that solution, but does not necessarily create a better game.

My strongest direction is to make **what the boat should optimize change during a voyage**. Sometimes fish count matters; sometimes kilograms, processing time, next-cycle timing, chum supply, or remaining space before return. The captain should anticipate and choose between worthwhile operating plans. Crew execute those plans competently.

A good crew must still earn periods of smooth operation. Upset an established plan by presenting a different situation, not secretly reducing its output whenever it succeeds. A robust conservative plan should remain valid; the player who adapts should capture additional opportunities, not merely avoid scripted punishment.

**Recommended first combination:** M01 method-changing water phases, M02 catch-composition shifts, M09 chum versus sale allocation, M17 finite processing staging, and M10 deliberate catch-wave scheduling. This uses the existing boat and its real jobs. It needs no sickness, boat chase, Engineer, or routine captain carrying. Do not implement all 48 ideas together.

### Reading routes

- For the central proposal: sections 1–5 and the worked voyage in section 6.
- For the idea bank: section 4, M01–M48. Neighboring entries are often alternatives or interactions, not cumulative requirements.
- For the roster: sections 8–9. CF/CD identifiers are NEW proposal slots, not historical F/D identifiers or saved IDs.
- For what to try first: sections 7 and 11.
- For evidence and limits: sections 2–3 and 12.

## 1. Current brief and boundaries

Mo's current instructions take precedence over earlier saved research:

| Topic | Baseline for this proposal |
|---|---|
| Captain at Tier 5 | Directs priorities, allocates labor, anticipates pressure. Routine fish pickup is not the intended occupation. Occasional later events may call for manual help. |
| Crew | Six hires plus captain. Fishers operate rods/nets/cages/deep lines; Deckhands collect, carry and process. No Tier 5 Engineer or new profession. |
| Layout | Fixed two normal rods, two cages and rear net. Optional two normal rods plus deep lines OR side net. No at-sea hardware teleportation. |
| Deep lines | Two base rigs, upgrade to three. One larger-biased fish per baited rig: two total or three total. Slow, 60-second baseline soak; automatic raise; Deckhands collect directly. No manual retrieval requirement. |
| Deep-line bait | Self-made chum for now. Mo allows fish as production input and wants small catches useful. Direct small-fish bait is a possible future alternative, not an extra approved rule. |
| Cards | 15 Fishers and 15 Deckhands. Each role: seven blue, four purple, four gold. Three different alternatives per slot. Full rethink permitted. |
| Rarity | Equal role/level base speed. Blue: one automatic active. Purple: one automatic active + one team passive. Gold: one automatic active + two team passives here. No ability buttons. |
| Collection | Permanent cards/levels, voyage deployment wages, one deployed copy per named identity. Exact acquisition, wages, levels and stacking not selected. |
| Tone | Deliberate management. Avoid constant reassignment, reflex deadlines and repetitive maintenance errands. |
| Fish | Real local eligible species, whole specimens and honest queues. No rerolls dressed up as expertise, fish duplication or value creation through splitting. |

Complete rethink permits new alternatives to old cards; it does **not** silently reopen every rejected game premise:

- **No chasing moving schools, feeding clouds or spatial attraction simulation.** A stationary ground's catch-table conditions may change, explicitly as a NEW abstract model.
- **No Engineer wear on manual rods, nets or cages.** Normal nets have unlimited uses; purchased deep nets have three uses. Deep nets and deep lines are different systems.
- **No robots/electric reels replacing human operating jobs.** Later machinery should enable new work.
- **No bait-aura crew roster.** Chum allocation is now requested as a production decision; that does not revive rejected Chum Captain/School Caller abilities.
- **No reset/rearm loops, arbitrary cash multipliers, processing-deadline premiums or tiny next-three-cast purple/gold identities.**
- **No legendary that merely takes another fisher's occupied rod.**
- **No big-fish processor requiring several big fish to become useful.** One specimen must be enough.
- **No guaranteed failure because the player built a capable crew.** Pressure must be visible and solvable.

Historical selected Power Lifter and Bulk Processor are retained as identified alternatives, not weakened secretly. Mobile Filleter, Prep Foreman pre-cleaning and Passage Processor were rejected earlier; they are not recycled here under new names.

## 2. What the local research establishes

Read for this task: current AGENTS.md, relevant comms.md sequences LOOP051, MGMT052, CREW053–099, TIER5-102/103, DEEP104 and CARDS105; TODO; GAMEPLAY; CONTINUATION; the active playability plan; CREW-CARDS-DESIGN; CREW-MANAGEMENT-INTEGRATION; saved ASTRA-RESEARCH/QUESTIONS; current deep-line/preparation source where it affects this proposal.

The project is being changed concurrently by Codex 2. Latest diary records independent fishing-task tickboxes, net role migration, third-rig and Tier 5 chum work. Current source inspection already shows StandardRigCount=2, MaximumRigCount=3, one catch per rig, and new chum rules. This is source evidence, not a claim those changes are installed or visually accepted. TODO and older research still contain superseded two-rig-only/no-chum notes.

The older Astra audit remains useful for structural facts:

1. Fishing yield, carrying load, processing job count and hold mass are different units. Fewer heavy fish can occupy more hold but take fewer processing jobs than a small-fish net.
2. Passive soaking does not occupy a fisher, but walking, setting, recovering other gear and operating rods do. Six workers cannot each contribute a full minute to several jobs simultaneously.
3. Equipped boats route landing → inbound carrying → processing input → preparation → output → outbound carrying → hold.
4. Unlimited whole-basket carrying makes many carrying-card concepts meaningless. An ordinary load rule must exist before carrying capacity is strategic.
5. Historical combined input/output capacity being tied to the entire hold can hide local pressure. Smaller meaningful staging is proposed, not an existing small buffer.
6. Existing processing is principally per specimen. Heavier fish do not automatically take more processing time unless we deliberately change that rule.
7. Richness depletion and market saturation already exist. Their names are not new ideas. Proposals below identify additional decisions or interactions.
8. A rate forecast is not secured profit. Actual sale depends on landed/processed/stored cargo, fish sacrificed to chum, supplies, wages, fuel and market conditions.

Establish honest baseline work and buffers before crediting cards with fixing bottlenecks. Do not preserve broken routing to sell a legendary solution.

## 3. Lessons from other games — verified references, original adaptations

Sources checked on 21 October 2026. Historical developer posts describe the design at publication, not necessarily the current version.

| Reference | Supported observation | Borrow for Catchline | Leave behind |
|---|---|---|---|
| [Against the Storm — Forest Mysteries](https://eremitegames.com/recipes-cookbook-update/) | Seasonal effects are revealed for a settlement; activation depends on season and hostility. | Known conditions change which operating plan is attractive. Combine environmental timing with production consequences. | Death penalties and unrelated debuffs. |
| [Against the Storm — balancing combinations](https://eremitegames.com/twitch-integration-update/) | The developer adjusted combinations and severity after overly punishing runs. | A pressure budget, recovery windows and combination testing. | A director secretly countering the player's best crew. |
| [Factorio — Spoils of Agriculture](https://www.factorio.com/blog/post/fff-414) | Biological production links inputs, outputs and replenishment; freshness makes flow matter more than stockpiling. | Chum is catch that could have been sold; staging and replenishment make production circular. | Disappearing catches, compulsory rot cleanup or reversing prepared-fish preservation. |
| [Into the Breach — official description](https://subsetgames.com/itb.html) | Attacks are telegraphed so players plan a response. | Show coming return collisions or a water-phase change. Surprise can combine known facts. | Combat and perfect knowledge of random fish identities. |
| [Timberborn — Update 5 announcement](https://steamcommunity.com/games/1062090/announcements/detail/7034115464063354888) | Badtides add another water-cycle challenge rather than only extending droughts. | Different phases demand different responses, not stronger copies of one shortage. | Survival collapse and pollution infrastructure. |
| [RimWorld — early storyteller design](https://ludeon.com/blog/2013/09/title-screen-update/) | The developer describes different approaches to arranging tension. | Preparation, pressure, consequence, recovery. Compare paced and irregular voyages. | Treating old settings as current facts or making sickness the whole answer. |

The mechanics below are my synthesis. Sources support the observations above, not proposed fish probabilities, card values or balance claims.

## 4. Forty-eight ways to keep management fluid

**FIRST** = strongest initial experiment; **EXPLORE** = credible extension/alternative; **LATER** = substantial new content; **CAUTION** = easily becomes a chore. All are unselected. Some entries are deliberately interactions or variants, identified as such, not 48 independent systems to install.

### A. The same anchored ground asks for different methods

### M01 — Water phases change the preferred method · FIRST

**Change:** A visible local water cycle alternates between, for example, ordinary-rod-favored and cage/deep-line-favored periods. Change method-specific encounter weights or rates within the local pool. This is an abstract rule, not moving fish on the map. Keep the 60-second deep-line clock; vary eligible outcomes rather than silently changing approved timing.

**Captain decision:** Maintain mixed coverage, concentrate on the favored method, or use the weaker phase to clear cargo and make chum. A slow rig commits supply and future landing time.

**Pressure:** Rod phases supply many pickups; deeper phases supply fewer heavy arrivals and consume chum. Versatile fishers gain value.

**Anti-solved test:** A fixed phase sequence becomes routine. Combine it with current stock, catch composition and landing commitments. Automatic policy may handle repetition; the captain decides when today's cargo makes the usual policy wrong.

**Guardrail:** Show the next phase and affected methods. Lock paid-cycle outcome rules at deployment where appropriate. No unusable methods or demands for absent equipment. Do not add M03/M04 as extra clocks in the first experiment.

### M02 — Change catch shape, not just total weight · FIRST

**Change:** A ground temporarily favors many small specimens or fewer large specimens, using local species and legal sizes. Similar kg/min can produce different fish/min, trips and processing demand.

**Decision:** Move a hand from carrying to processing, give the small-fish specialist a table, convert eligible low-value inputs into chum, or temporarily reduce intake.

**Pressure:** Small-fish runs strain per-fish handling; heavy runs strain load allowance and hold headroom. One staffing ratio cannot optimize both.

**Anti-solved test:** Randomness alone is noise. Give each composition a readable interval and trend, with uncertain actual samples. Do not secretly predetermine fish to defeat the player's orders.

**Dependency:** Ordinary loads must be bounded. Define small/large by actual work, not color alone. No species imported from another ground.

### M03 — Useful conditions arrive in the wrong order · EXPLORE

**Change:** A deep-line-friendly interval arrives before a cheap small-fish supply interval; another voyage reverses them. **Decision:** Sacrifice a valuable eligible input for early chum, start ordinary rods and miss some upside, or wait. Carryover chum is NOT baseline. **Pressure:** Startup economics change with order. **Guardrail:** Preserve free-scraps bootstrap. This is M01 sequencing, not another weather system; never strand an empty-stock boat.

### M04 — A favorable window overlaps a committed return · EXPLORE

**Change:** An announced favorable catch distribution overlaps a net return. **Decision:** Keep its fisher on net work, delay redeployment to use rods, or dedicate another fisher and weaken support. **Pressure:** Opportunities compete for fisher-seconds. **Anti-solved test:** Both responses must sometimes win depending on the queue. Windows last through real job boundaries; missing one means ordinary fishing, not punishment. Existing catches remain safe.

### M05 — Method-specific local exhaustion · EXPLORE

**Change:** Extend existing depletion into a few method-accessible catch groups. Repeated net harvest reduces its group's attractiveness more than deep opportunities. **Decision:** Rotate methods, persist with specialists, or return partially full. **Pressure:** Success alters later opportunity. **Guardrail:** Slow, disclosed recovery and a useful floor; no toggle farming. If it becomes a fixed rotation, combine with actual cargo or keep it between voyages. This extends existing depletion, not merely renames it.

### M06 — Forecast confidence becomes a budget decision · EXPLORE

**Change:** Coming composition is a range until actual catches narrow it. **Decision:** Keep spare support, commit a specialist early, or sample before spending a deep-net use. **Pressure:** Flexibility has value. **Guardrail:** Basic observations are universal, not a rare-card privilege or manual scouting chore. Distinguish unknown conditions from changing ones. Alone this is solved by experience; pair with M02.

### M07 — Grounds have different rhythms · EXPLORE

**Change:** One ground alternates small/heavy arrivals; another is steadier with less upside; another has short well-forecast opportunities. **Decision:** Choose for crew and desired attention, then adapt. **Pressure:** No single map should suit every build. **Limit:** Primarily between-voyage variation, insufficient alone. Keep signatures learnable; variation changes the instance, not every rule. No boat chase.

### M08 — Opportunity arrives near a sensible return point · EXPLORE

**Change:** An attractive phase approaches near the fuel/capacity limit. **Decision:** Clear cargo now, reserve space for that phase, or take a secure return. **Pressure:** End-of-voyage planning replaces 'fish until full.' **Guardrail:** No free fuel or forced dangerous overtime. Returning should often be correct. This changes the planning horizon, not a countdown bounty.

### B. Your successful plan creates the next problem

### M09 — Chum and sale preparation compete for fish and table · FIRST

**Change:** Self-made chum consumes real catch and table labor that could secure sale cargo. Small-fish flushes provide cheap inputs; heavy-only runs make replenishment expensive.

**Decision:** Maintain reserve, pause deep redeployment, temporarily dedicate a table position to chum, or permit a valuable input. Use persistent filters and protected specimens, not individual approvals.

**Pressure:** Deep success depletes stock; replenishment delays sale preparation; delayed preparation fills input; pausing deep lines frees recovery time. This is a feedback loop.

**Anti-solved test:** 'Maintain ten' solves stable supply. Mix composition, table occupancy and upcoming demand so target/eligibility decisions sometimes change. No tapping each portion.

**Dependency:** Peer-owned yields are changing; use actual portions/specimen and work seconds later. Chum may use any eligible fish under Mo's direction; filters are player choices, not a hidden ban on valuable fish. Preserve free-scraps bootstrap. Caught fish are not economically free.

### M10 — Catch waves are commitments you can stagger · FIRST

**Change:** Two/three deep returns can coincide with a net landing and finished output. Average rate fits; the burst does not.

**Decision:** Deploy together for concentrated opportunity, stagger starts, leave a cleared rig unbaited, or allocate a temporary carrier. Scheduling controls belong to everyone.

**Pressure:** Intake occupancy → processing surge → output clearance. Delayed deployment may miss a favorable phase.

**Anti-solved test:** Fixed cycles can be staggered once. Collection delays, weights and opportunities alter the next useful start. Do not randomly jitter paid rigs to defeat good scheduling. Good staggering should help.

### M11 — A valuable fish is also the next bait supply · EXPLORE

**Change:** The only eligible chum input is a specimen normally protected for sale. **Decision:** Consume it, sell it later, or wait for cheaper supply; show foregone sale value and estimated stock coverage. **Pressure:** Future opportunity competes with secured progress. **Guardrail:** Never auto-consume protected records or promise positive ROI. This is an M09 interaction, not a bait-efficiency card.

### M12 — Deep-net stock creates a transition point · EXPLORE

**Change:** Existing three-use deep nets run out while normal nets remain unlimited. New element: forecast the transition and permit a reserve policy. **Decision:** Spend a use now, reserve it for the coming composition, use normal nets next, or bring more stock. **Pressure:** Heavy-catch support becomes small-fish processing. **Guardrail:** Deep-Net Saver may solve this tension; respect that strength. No new tax or manual wear.

### M13 — Clearing a station changes the next wave · EXPLORE

**Change:** Collecting a blocked deep catch restarts access to its next paid cycle; clearing a net basket enables another batch. **Decision:** Prioritize the method fitting the coming phase, not always today's largest pile. **Pressure:** Hauling choices alter future clocks. **Limit:** Backpressure already exists; the proposal is explicit look-ahead and policies. Basic safe dispatch is not a legendary ability.

### M14 — Committed work consumes flexibility · EXPLORE

**Change:** In-transit and processing fish represent labor already promised, even with spare hold space. **Decision:** Gate new deployment against committed work, finish one method, or pursue one selective final catch. **Pressure:** Delayed commitments make anticipation useful. **Guardrail:** Project actual work, not a fabricated stress meter. If a forecast solves routine control, that is earned automation; changing composition supplies new decisions.

### M15 — Specialization consumes its cheapest support input · EXPLORE

**Change:** Deep specialization yields valuable heavy fish but few cheap chum inputs. **Decision:** Accept expensive feed, rotate a fisher to small-catch supply, or lower deep output. **Pressure:** Net supply can help chum but overload processing if misrouted. **Guardrail:** This is M02+M09 interaction, not compulsory extra hardware. Any eligible fish can be chum; the cost is foregone sale, not artificial ineligibility.

### M16 — Choose an ambitious operating objective · EXPLORE

**Change:** Choose steady income, early filling or large-specimen targeting as priorities over real work. **Decision:** Stick with ambition or secure a conservative result when conditions change. **Pressure:** Self-chosen commitment changes acceptable queue/risk. **Limit:** No free production buff or secret adverse-event spawns. This framing needs actual dynamics; another goal checklist alone is not a solution.

### C. Physical flow creates changing constraints

### M17 — Finite local staging that actually matters · FIRST

**Change:** Give processing input and output meaningful finite staging instead of treating the whole hold allowance as a giant convenient workbench. Preserve whole-fish acceptance and a safe way to handle one oversized specimen. Exact capacities need the actual model/layout and fish distributions.

**Decision:** Clear finished output to reopen processing, clear an incoming station to reopen fishing, or stop intake and let the line drain. A carrier can be busy yet assigned to the wrong end.

**Pressure:** A processing upgrade can create an output blockage. A hauling upgrade can flood input. Different fish compositions change which side fills first.

**Anti-solved test:** Small buffers alone only produce a tighter fixed ratio. Combine with arrival waves and mixed workloads. Never make tiny buffers just to force clicks. Automatic fallback should clear obvious deadlocks; the captain sets priorities between viable objectives.

**Guardrail:** Cargo remains real and retained when blocked. Power Lifter does not enlarge destinations. No deliberate pathfinding failure, crowding bug or fish disappearance used as challenge.

### M18 — Reserve landing space for a known commitment · EXPLORE

**Change:** A ready net and soon-returning deep rig compete for a proposed shared receiving allowance. **Decision:** Reserve capacity for the committed heavy catch or unload the net immediately. **Pressure:** Fishing commitments constrain logistics before landing. **Dependency:** NEW shared staging, not current geometry. Never prevent automatic deep return or discard its catch; it remains at its rig. An overcomplicated reservation interface would make this worse than M17.

### M19 — Flexible staging allocation · EXPLORE

**Change:** A small shared work area can be assigned more input or more finished-output space between jobs, within a fixed physical footprint. **Decision:** Prepare for a net surge or give fast processors room to finish. **Pressure:** More space at one stage removes it from another. **Guardrail:** No resizing occupied cargo, no teleportation, no mid-job move. If best play is flipping allocation each batch, reject; use meaningful phases and automatic safe boundaries.

### M20 — Many destinations beat one giant carrying number · EXPLORE

**Change:** Loads need correct destinations: raw input, chum feed where applicable, finished hold cargo. The crew cannot merge incompatible jobs just because capacity is huge. **Decision:** Dedicate a carrier to the busy lane or let a flexible carrier serve several. **Pressure:** Power Lifter clears one station brilliantly but cannot be everywhere. **Limit:** Existing route distinctions are not new content; optional route specialization and observed demand give them meaning. Do not invent detours to weaken a gold card.

### M21 — A single large specimen changes the return plan · EXPLORE

**Change:** A legal local specimen arrives larger than the remaining comfortable capacity. Existing whole-fish overshoot means acceptance can end intake. **Decision:** Prioritize it for storage and return, finish current profitable cargo first, or keep it safely queued while deciding. **Pressure:** One meaningful catch can change the operating horizon. **Guardrail:** No forced loss, arbitrary giant-fish minigame or weight reroll. Clearly show consequences of storage order; never secretly sell or discard the loser.

### M22 — Draining the boat is its own phase · EXPLORE

**Change:** Near departure, temporarily stop new deployment while passive rigs finish and crew clear committed work. **Decision:** Start winding down early for a clean return or take one more paid cycle. **Pressure:** Fishers lose useful jobs while hauling/output dominate. **Limit:** Partly existing lifecycle, proposed explicit operation mode. Captain stays managerial. Do not revive rejected underway processing; all work here happens while still fishing at the ground, burning ordinary time/fuel.

### M23 — Limited optional overflow buffer · EXPLORE

**Change:** An optional finite landing crate provides surge capacity but occupies a real module/staging allocation. **Decision:** Fit resilience before departure or keep the productive alternative; during play, decide when to use the buffer. **Pressure:** Buys time, never throughput. **Guardrail:** No unlimited deck pile, fish expiry punishment or convenient extra deck footprint without art/route review. This is equipment planning, not a required Tier 5 addition.

### M24 — Available travel routes change during real operations · CAUTION

**Change:** A future physically meaningful large recovery temporarily occupies a passage, with an alternate route. **Decision:** Clear output before recovery, choose the work sequence, or accept longer trips. **Pressure:** Route geometry rather than generic walk speed matters. **Dependency:** Not current normal net/deep mechanics; requires authored safe space and alternate access. Never intentionally make crew bump/stall or charge a random 'traffic tax.' Lower priority than honest queues.

### D. What is worth doing to the fish changes

### M25 — Preparation has work families · EXPLORE

**Change:** Instead of every specimen taking essentially one fixed cycle, a few plainly named preparation families have different work profiles: many quick small fish, one long heavy fish, specialized crab work. This is a new processing baseline, not a claim about current code.

**Decision:** Switch processor/filter priorities, bring specialists, keep a versatile processor, or reduce intake of a poorly supported family. One big fish can matter immediately.

**Pressure:** The same fish count can create different cutting workload. **Anti-solved test:** No hidden taxonomy of thirty recipes. Start with two/three useful families; if every fish just scales linearly with kg, it may collapse back into one ratio. Preserve prepared premiums and whole-specimen identity; no forced cutting minigame.

### M26 — Processing setup versus queue urgency · EXPLORE

**Change:** Under M25, changing a table's family requires a modest real setup action. Batching similar work saves setup, but makes other cargo wait.

**Decision:** Keep a specialist run, switch for one valuable arrival, or dedicate two table positions to different families. **Pressure:** Efficiency competes with responsiveness.

**Guardrail:** Do not introduce gratuitous cleaning/knife-maintenance chores. A setup cost needs visible physical meaning and should be amortizable automatically. It must not require big-fish streaks for a card to function. This is an alternative direction to test, not a prerequisite for the whole roster.

### M27 — Two legitimate preparation products · EXPLORE

**Change:** Add two explicit work recipes for an eligible specimen: ordinary preparation and a more labor-intensive product with a different market use. This requires new product rules; it is not a card granting free sale value.

**Decision:** Process for throughput, invest spare table time, or hold input until a carrier clears output. **Pressure:** Quiet periods become an opportunity to add work; busy periods favor the simpler recipe. **Guardrail:** No perishable deadline bonus, no duplicate fish, and account for exact output value/mass. Do not make the premium recipe always economically superior.

### M28 — A finite buyer, not infinite premium demand · EXPLORE

**Change:** Extend existing market/contract systems with a visible limited buyer allocation chosen before departure: a small quantity of a preparation type, then normal market value. **Decision:** Stop that recipe after fulfillment or continue because its ordinary economics still work. **Pressure:** The production target changes mid-voyage. **Boundary:** Contracts and quotas already exist; this is a recipe/workload extension, not 'add quests.' No random radio task every minute or card-owned cash aura.

### M29 — Protect a record while feeding the operation · EXPLORE

**Change:** A specimen's collection/record purpose conflicts with its usefulness as input or hold space. **Decision:** Lock it from consumption, accept the space cost, and adapt the rest of the plan. **Pressure:** Personal goals change optimal logistics. **Limit:** Journal expansion is still separate content. Basic protection is universal; no rarity gate. Useful occasionally, not an excuse to flood the player with confirmation popups.

### M30 — Known market trajectory changes the endgame · EXPLORE

**Change:** Existing saturation information is extended into a transparent forecast for the cargo actually aboard and one next-voyage outlook. **Decision:** Finish a mixed haul, stop a saturated method, or accept saturation because current catch value remains good. **Pressure:** kg/min stops being the only objective. **Limit:** Primarily economic planning, not enough intra-voyage action alone. Do not rewrite prices during a catch based on the player's card loadout or add arbitrary timed premiums.

### M31 — A useful secondary output with competing uses · LATER

**Change:** A future explicit processing recipe produces a finite byproduct used by a later support operation. **Decision:** Keep it for that operation or choose a different recipe for the current catch. **Pressure:** The best recipe depends on downstream stock. **Guardrail:** Mass/value ledger must account for outputs; no free infinite chum scraps from preparing a fish that is also sold whole. Needs its own product design, not silently added to current chum.

### M32 — Cargo mix changes optional harbor commitments · EXPLORE

**Change:** After a voyage, choose a future buyer/route commitment based on the crew and fish mix you actually have. **Decision:** Specialize the next departure or retain flexibility. **Pressure:** Persistent choices create different opening states rather than a universal best boat. **Limit:** This is longer-term variety, not a fix for a static ten-minute voyage. Existing contracts must be audited before adding another overlapping screen/system.

### E. Labor and station flexibility become real resources

### M33 — Keep one worker flexible, or maximize one stage · FIRST COMPARISON

**Change:** No new fatigue meter: compare a crew with one genuine flexible Deckhand against a narrow specialist crew under M02/M10/M17. **Decision:** Pay the opportunity cost of flexibility or exploit a strong phase with specialization. **Pressure:** Support headroom becomes valuable only when demand changes. **Limit:** This is a testable staffing pattern, not a standalone event mechanic. All basic duties/fallbacks remain available without cards; cards alter capacity, not permission to work sensibly.

### M34 — The two table positions have different best uses · EXPLORE

**Change:** One position is committed to chum or a long preparation job while a new workload arrives. **Decision:** Let it finish, reserve the next job for a different family, or switch the other position. **Pressure:** Work in progress limits immediate reallocation. **Guardrail:** Safe policy changes at job boundaries and retained progress; do not punish players with destructive cancellation. This emerges from M09/M25 rather than a third artificial constraint.

### M35 — A profitable task needs two real workers · LATER

**Change:** A later genuinely new operation, such as oversized recovery, requires coordinated positions for a finite interval. **Decision:** Temporarily reduce fishing/hauling or decline that operation. **Pressure:** A six-person stable crew has to reallocate labor. **Guardrail:** Do not retrofit two-worker requirements onto ordinary fish merely to defeat Power Lifter. Capability must earn its extra labor. No fictional useless operator whose only purpose is making a gold useful.

### M36 — Refit a method while the others continue · EXPLORE

**Change:** Allow changing shallow/deep net loadout at a safe empty-rig boundary through an actual short fisher job, if this is compatible with the equipment rules. **Decision:** Invest time and stock now for the upcoming composition or keep the current cycle. **Pressure:** Fisher setup competes with rod/cage work. **Guardrail:** Not swapping whole boat modules at sea. Clearly label NEW functionality and consumed stock rules; no net uses refunded by refitting.

### M37 — Voluntary shift relief with a bounded payoff · CAUTION

**Change:** An optional later labor model lets a worker take a predictable break in exchange for a sustained subsequent benefit; ordinary work remains competent without it. **Decision:** Stagger breaks around arrivals or skip them. **Pressure:** Future capacity versus immediate coverage. **Risk:** Likely to become a repeating timer chore or disguised mandatory fatigue. Test only after core dynamics; omit if an obvious schedule automates all value. No punishment exclusive to common crew.

### M38 — Temporary absence handled by crew policy · LATER

**Change:** Occasional sickness or another later event removes one worker for a disclosed period. **Decision:** Reduce a method, redeploy a flexible hand, or choose optional captain intervention. **Pressure:** Established operating plan must change. **Guardrail:** Mo already identified this future direction; it is not a newly discovered solution. Do not stack absences, erase retained cards, or require manual carrying as the only recovery. Always offer a viable reduced-output plan.

### M39 — Crew commitments carry between voyages · CAUTION

**Change:** A future voluntary longer assignment reserves a crew member for a specific voyage objective while others remain flexible. **Decision:** Take the commitment and build around it or keep the roster open. **Pressure:** Team composition changes without arbitrary illness. **Risk:** Can feel like preventing use of earned cards. Never expire ownership or force a bench tax. This needs a strong benefit and is lower priority than within-voyage dynamics.

### M40 — Choose between two useful simultaneous captain decisions · EXPLORE

**Change:** Announce a coming method opportunity while a production queue needs a strategic change. Both are manageable through orders. **Decision:** Accept one opportunity and leave the conservative policy on the other, or prepare ahead for both. **Pressure:** Attention is limited without requiring fast taps. **Guardrail:** Pausing remains available and ordinary crew execution is automatic. Do not hide controls or generate alerts faster than they can be understood. This is scenario composition over existing proposals, not a new skill button.

### F. Stronger later changes and optional disruptions

### M41 — A shared recovery operation for future expeditions · LATER

**Change:** A diver return and an oversized catch need the same future crane/receiving area. **Decision:** Sequence recoveries, reduce other landing work, or postpone one expedition. **Pressure:** Two individually profitable activities compete for a shared human-supported service. **Guardrail:** Follows Mo's new-operation machinery direction. No Tier 5 crane/Engineer assumed, no oxygen-death countdown, and no weakening Power Lifter's already-landed cargo ability.

### M42 — Captain leaves on an optional spearfishing sortie · LATER

**Change:** The captain chooses an actual future side-boat activity while the crew continues an agreed operating policy. **Decision:** Leave a resilient plan or stay aboard to exploit a management opportunity. **Pressure:** Reliability matters over a predictable absence. **Guardrail:** Explicitly later, optional hands-on content from Mo's direction. Do not make every voyage require returning to manual fishing. Crew do not become incompetent merely because the captain leaves.

### M43 — A forecast sea state changes landing convenience · EXPLORE

**Change:** A game abstraction makes certain new deployment/recovery windows less convenient, without manual-gear damage. **Decision:** Delay a voluntary set, prioritize protected/steady methods, or accept normal extra work through a known condition. **Pressure:** Timing competes with opportunity. **Guardrail:** Deep automatic returns still work and cargo remains safe. Avoid a uniform all-work slowdown; if every response is 'wait,' cut this idea. This is weather affecting jobs, not real-world seamanship guidance.

### M44 — Optional flotsam recovery ties up support · LATER

**Change:** A recoverable object appears beside the anchored boat and offers a clearly described optional job. **Decision:** Divert real crew or ignore it while fishing. **Pressure:** A good opportunity competes with current work. **Boundary:** Drifting/tappable crates have appeared in prior discussion; a tap-for-coins is not new management. Only worth revisiting with actual crew/recovery demand and varied outcomes, not more manual clicking or chasing.

### M45 — Temporary dock/service availability shapes departure · LATER

**Change:** Future harbor services offer different predictable windows for buying supplies or outfitting, with sensible alternatives. **Decision:** Take a shorter voyage for a useful service or continue the profitable haul. **Pressure:** Planning horizon changes. **Guardrail:** No real-time login schedule, mandatory waiting, missed-day punishment or dependence on online time. This is optional progression content, not the first fix for current sea play.

### M46 — A visible voyage modifier changes one relationship · EXPLORE

**Change:** A departure offers an optional condition such as abundant small-catch opportunities but scarce heavy opportunities, or stronger phase contrast. **Decision:** Adapt crew/loadout or choose ordinary conditions. **Pressure:** Different relationships, not flat difficulty scaling. **Guardrail:** Show the rule before committing and do not secretly counter the selected crew. Avoid drawing impossible modifiers for installed gear. Variation supplements within-voyage change; it does not replace it.

### M47 — Earned difficulty through an optional commitment · EXPLORE

**Change:** The player accepts an operational challenge involving a real workload—e.g. secure a mixed catch while leaving reserve space for a late heavy arrival. **Decision:** Optimize under the commitment or abandon its optional bonus and take ordinary sale. **Pressure:** The player chooses which solution is insufficient today. **Boundary:** Existing contracts/quotas are not novel; use only if the commitment creates a different work plan. No base-catch confiscation or punishment for declining.

### M48 — A voyage rhythm director, not a sabotage director · EXPLORE

**Change:** Scenario generation arranges a limited combination of conditions into preparation, pressure and recovery intervals. It can schedule an opportunity after a quiet period, but never secretly target the weakest crew member or invalidate the successful method.

**Decision:** Read announced conditions, pursue optional upside, or hold a conservative policy. **Pressure:** Different combinations keep a learned system fresh.

**Anti-solved test:** Pure randomness can still produce the same optimal response. Require at least two qualitatively different decisions in authored test voyages, then generate variations. Sample the environmental sequence independently of card strengths; use current state only to avoid impossible/overlapping demands and to pace notifications. Do not conceal rubber-banding behind 'fluidity.'

## 5. Controls and fairness that make the ideas playable

These are ordinary management capabilities, **not extra counted dynamics or rare-card privileges**:

1. Per-worker allowed duties, priorities and safe job-boundary changes. Never interrupt a committed catch or dump cargo just because an order changed.
2. Per-method start/stop-after-current-cycle and optional stagger targets. No repeated manual activation of every ability.
3. Persistent chum target and input filters, protected fish, and clear projected consumption. A captain can change a policy without approving every fish.
4. Show the next relevant event/phase, estimated incoming fish/kg, current work commitments and uncertainty. Not a perfect prophecy of RNG.
5. Actual fish/min, kg/min, input/output queues, time to clear, and the cause of a blockage. Forecast and gameplay share the same work rules.
6. Pause to plan; notifications only for changed priorities, risk or opportunity. No alarm for each automatic fish.
7. Sensible automatic fallback prevents deadlock. No permanent station reservation by an absent worker and no empty-basket waiting when useful permitted work exists.
8. A clear return/wind-down policy. Explain unfinished cargo and costs before departure; do not rely on silent loss to settle overproduction.

### Pressure budget — provisional pacing, not final numbers

For an initial 8–12-minute test voyage, try **three to five meaningful decision windows**, not thirty. A window is a changed strategic choice, not every click. Give roughly 30–60 seconds of useful warning where the event is predictable, allow conditions to persist long enough for real work to respond, and leave recovery time. These are prototype targets, not changes to the approved 60-second deep-line clock.

One external change plus one resulting internal bottleneck is enough. Avoid simultaneous sickness, bad weather, stock collapse and storage emergency. Favor an opportunity and a tradeoff over an unavoidable penalty. A no-intervention crew should earn a decent result; adaptive management should gain something measurable.

Not every voyage needs a crisis. If every good solution is immediately punished, improving the boat feels pointless. Let players recognize and enjoy a successful phase before asking a different question.

## 6. A worked voyage: the captain never picks up a fish

Illustrative story, **not simulated output or a promised profit**. Six hires: two Fishers, two carriers, a processor, and a Deckhand who can switch between processing/carrying. Two table positions; base two deep rigs, plus fixed equipment. Everyone's labor is counted once.

| Situation | What the captain sees | Two valid choices | What changes next |
|---|---|---|---|
| Departure | No chum; a small-catch-favored opening and later deep opportunity. | Use ordinary fishing to bootstrap cheap feed; or prioritize sale preparation and enter deep fishing later. | Starting reserve competes with early secured income. |
| Small-fish flush | Input fish count rises although kg remains modest. | Assign the flexible hand to table work; or reduce the small net and retain stronger hauling. | Extra processing creates an output wave, not instant hold revenue. |
| Deep phase approaches | Enough chum for current deployments; rear net and two deep returns may overlap. | Stagger one deep start; or accept the wave with temporary carrier focus. | The first choice smooths intake, the second captures more of the current opportunity. |
| A large fish lands | More hold commitment, fewer cutting jobs than the preceding small-fish wave. | Free the flexible hand for output hauling; or keep them making reserve chum for another cycle. | Support shifts from fish count to stored mass and future supply. |
| Only expensive chum input remains | Automatic policy protects the valuable catch; next deep start is blocked. | Broaden the allowed input policy; or leave deep lines idle and use ordinary rods. | The player prices a future uncertain catch against a real fish already aboard. |
| Fuel and hold horizon narrow | One more overlapping wave could leave unfinished work. | Wind down and secure cargo; or leave headroom for a selective last cycle. | Departure is a management decision, not an inevitable full-hold popup. |

The interesting event is often **good news arriving at an inconvenient moment**: a heavy fish, a cheap bait supply, or a favorable phase. Nothing breaks. The crew does its jobs. The captain decides which success is worth pursuing.

## 7. What I would choose, defer, and reject

### First design experiment: one boat, five connected ingredients

1. Honest bounded carrying and finite safe staging (M17 prerequisite).
2. Two readable catch-composition/phase patterns (M01/M02).
3. Chum allocation against sale preparation (M09).
4. Deliberate return scheduling and station backpressure (M10/M13).
5. Conservative versus flexible staffing comparison (M33).

Do not initially add new product recipes, fatigue, illness, crane jobs, temporary harbor events or fifty modifiers. They are options for later depth, not excuses to avoid testing the basic management loop.

### Three alternative directions if that loop is still too static

- **Production puzzle:** M25/M26 preparation families and setup make cargo composition alter table planning. Stronger system change, potentially excellent for processor cards, but risks industrial clutter.
- **Opportunity captain:** M04/M08/M28 limited opportunities compete with secure throughput. More decisive moments; risks feeling like a stream of errands if contracts dominate.
- **Expedition fleet:** M35/M41/M42 genuinely new operations compete for recovery/support. Strong long-term direction already consistent with Mo's wishes, but cannot fix current Tier 5 cheaply.

### What I would not use as the main fix

Random universal slowdowns, compulsory knife cleaning, weather that disables everything, lower buffer capacities solely to demand clicks, bait-attraction auras, moving-school chasing, unfair hidden counters, or mandatory manual captain hauling. More bars do not create more decisions. Existing priorities/contracts/depletion are useful foundations, not new content by themselves.

## 8. How to read the 90 card packages

Choose **A OR B OR C** for each slot. Never equip all three versions as three skills. Names are working identities; they are not thirty approved characters. Each blue option has one automatic signature. Each purple option has its listed signature plus the shared passive stated in that slot. Each gold option has its signature plus the two shared passives stated in that slot. This explicitly makes every option a complete rarity package without repeating identical passive text three times.

**All quantities below are illustrative tuning anchors.** They are specific enough to compare mechanisms, not tested balance or locked numbers. No wage/profit rankings are claimed. A gold's capability must justify its berth and wage in an actual build; its title does not guarantee superiority in every situation.

### Shared rules for all options

- Basic task permissions, priorities, protective filters, forecasts, safe routing and queue throttles belong to all workers. An ability changes work capacity, permitted physical cooperation or a production rule; it cannot sell back competent baseline behavior.
- No ability activates from paused time, mere reassignment, empty jobs or cancel/retry loops. Completed-job counters are personal, once per real committed action, and reset per voyage where applicable. Carrying a batch is one trip, not one proc per fish.
- Persistent mode choices are management orders, not repeatedly pressed skill buttons. Finish committed actions; never reset soak, specimen rolls or cooldowns by changing duty.
- Fishing signatures do not skip collection or processing. Deckhands do not retrieve fishing gear or create extra catches.
- Passives apply only while the card is deployed and eligible for its relevant duty, including temporary normal waiting. All tasks off means no support. No requirement to keep a useless worker physically standing still to maintain an aura.
- Passive scope includes eligible captain work unless stated otherwise, but the balance baseline assumes **zero routine captain labor**. No simultaneous free captain worker at several stations.
- Same passive family from multiple cards: strongest value only as the initial comparison rule. Different families combine only on their named stage. Never multiply unrelated global work-speed bonuses. This is a proposal, not a selected stacking rule.
- '20% faster' is rate ×1.2 (duration /1.2); '20% less time' is duration ×0.8. Soak, walk, handling, cutting and setup are separate.
- Proposed ordinary carrying: finite load allowance, but one indivisible heavier specimen can still travel alone. Exact allowance unselected. A capacity perk combines more compatible cargo; it cannot strand ordinary workers or enlarge destinations. Loads depart with available cargo, not after waiting to fill.
- Small/large processing eligibility needs a shared work definition. Here **small** provisionally means at most 1 kg; **large** above 1 kg. This is a proposed work threshold, not the game's rarity color. Test alternatives before choosing it; Bulk Processor uses its separate explicit 5 kg rule.
- No retroactive roll changes. A size-targeting ability modifies one legal specimen distribution before rolling; it does not roll several fish and select the best. 'Upper half' means upper half of that species' legal weight range, not 50% extra maximum weight.
- A processed batch preserves each fish's identity, mass, freshness and value entitlement. Processing time excludes inbound/outbound work. All output still needs carrying.
- Dependencies are honest: **Core** means existing job concepts with new ability code; **Load** needs bounded ordinary cargo; **Flow** needs new finite queue/physical handling rules; **Family** needs M25/M26; **Phase** needs M01/M02; **Kit** needs new visible card equipment/position validation. None means 'already implemented.'

### Roster map

| Role | Blue: seven | Purple: four | Gold: four |
|---|---|---|---|
| Fishers | CF01–CF07 | CF08–CF11 | CF12–CF15 |
| Deckhands | CD01–CD07 | CD08–CD11 | CD12–CD15 |

Fishers cover rods, nets, cages and deep lines with one purple and one gold focus each. Deckhands cover inbound, outbound, flexible carrying, small/large processing and cooperation. The 30 slots are a collection, not a demand for 30 workers or all methods on every boat.

## 9. The 30 cards — three alternatives each

### CF01 — Blue Fisher · Rod opener

**Role in management:** Choose early momentum, consistent rhythm or heavier individual catches. **Dependencies:** Core. Historical Strong Start remains one reference option.

- **A — Strong Start. Active:** First successful personal ordinary-rod cast per voyage lands three independently generated legal fish total. One real opening burst, never duplicate a specimen. **Choice/pressure:** Strong when early handling is ready; can overwhelm a boat still bootstrapping chum. Repeated dock/reset farming must cost the normal voyage transition/wages.
- **B — Fast Bite. Active:** Every third personal ordinary-rod cast has half its bite wait. **Choice/pressure:** Recurring intake rather than an opening burst; helps longer voyages, increases regular pickup demand. Counter advances on paid committed casts, so misses do not freeze it indefinitely. Historical blue concept, not a purple identity.
- **C — Patient Hook. Active:** This fisher's ordinary rod can use a persistent patient-cast mode: 20% longer bite wait, with one weight draw restricted to the upper half of the chosen species' legal range. **Choice/pressure:** Fewer larger arrivals fit a count-limited processor but use hold/chum-input value differently. No species rarity guarantee or reroll.

### CF02 — Blue Fisher · Rod handling

**Role:** Ordinary rod labor rather than biological waiting. **Dependencies:** Core; B needs explicit interruption state.

- **A — Firm Reel. Active:** Personal reeling of a large eligible specimen takes 25% less work time. **Choice/pressure:** Useful on the first big fish; frees fisher labor for other allowed fishing tasks. Does not speed bites or carriers.
- **B — Secure Strike. Active:** After this fisher has personally struck a fish, an unavoidable permitted job transition can leave it securely hooked for a bounded eight-second grace before reeling resumes. **Choice/pressure:** Finish a genuinely urgent ready-gear action without losing that struck fish. One pending catch, no second rod or unattended pre-strike guarantee; no benefit from deliberate cancel spam.
- **C — Ready Cast. Active:** This fisher's cast action, after baiting, takes half normal work time. **Choice/pressure:** Small dependable advantage in fast rod phases; weaker when bite waits dominate. Bait preparation, walking, waits and reeling remain full work. A coherent humble blue, not a hidden all-stage speed bonus.

### CF03 — Blue Fisher · Net setup

**Role:** Opening timing versus ongoing rig labor. **Dependencies:** Core; C adds a genuine pre-setting job.

- **A — First Set. Active:** The first net this fisher deploys each voyage uses half normal soak duration. **Choice/pressure:** Early batch and early processing demand; ordinary catches, retrieval and deep-net uses remain. Historical selection retained as an option.
- **B — Quick Rig. Active:** Personal physical net-setting work takes half time on every deployment. **Choice/pressure:** Helps one fisher combine net operation with another method; no biological soak speed. Modest if actual setup is a tiny share of the cycle.
- **C — Prepared Rig. Active:** At an empty idle net, this fisher may perform its full setup labor in advance, leaving one prepared-but-not-deployed state. Later deployment needs the normal release action but no repeated setup. **Choice/pressure:** Spend quiet time to meet a later window; work moved, not deleted. Preparation occupies real fisher time and belongs to that rig; no preparing a net still soaking.

### CF04 — Blue Fisher · Net cargo profile

**Role:** Different shapes of one net haul. **Dependencies:** Core sampling; C requires selectable small-catch mode. No added basket capacity implied.

- **A — Loaded Net. Active:** Every third personal net deployment gets 25% more catch mass budget for that haul. **Choice/pressure:** Larger waves reward planned support; local pools and whole-fish limits remain. Historical blue retained; not extra hold capacity.
- **B — Fine Mesh. Active:** A persistent small-catch setting narrows this fisher's normal-net specimen weights toward the lower part of eligible ranges while retaining the normal kg budget. **Choice/pressure:** More small fish can feed chum but increase preparation job count. No new species, guaranteed exact count or free bait.
- **C — Wide Mesh. Active:** A persistent selective setting excludes the smallest eligible specimen band before generating this fisher's haul; if the remaining pool cannot fill the ordinary budget, the net returns underfilled. **Choice/pressure:** Fewer processing jobs and potentially better individual catches at the risk of lower total mass. No reroll or guarantee of rarity; unlike A, it trades coverage for selectivity.

### CF05 — Blue Fisher · Cage worker

**Role:** Cage cadence, recovery or commitment. **Dependencies:** Core; C new cycle choice. All remain two installed cages, not extra hardware.

- **A — Quick Soak. Active:** Every third personally deployed/reset cage has half its next soak duration. **Choice/pressure:** A periodic return that may collide with deep rigs; attribution belongs to the worker who starts that cycle, not whoever collects it.
- **B — Clean Recovery. Active:** Personal cage recovery takes half its normal work time. **Choice/pressure:** Better mixed-method coverage without producing extra crabs; especially useful when several ready jobs compete. No effect while cages are merely soaking.
- **C — Patient Pot. Active:** Personal cage cycles may use a persistent extended soak: 25% longer, with a single legal crab-weight draw from the upper half of its range. **Choice/pressure:** Fewer, heavier crab deliveries versus frequent small ones. No doubling beyond species limits or arbitrary sale multiplier.

### CF06 — Blue Fisher · Deep-line setter

**Role:** One fish per line stays fixed; distinguish labor and size. **Dependencies:** Core; C snapshot of normal setup state. These are operating skills, not chum creation/attraction auras.

- **A — Quick Baiting. Active:** Personal physical deep-line baiting/setup work takes half time. Every deployment still consumes its required real chum. **Choice/pressure:** Less fisher occupation across two/three rigs; it does not halve the 60-second soak or automatic return.
- **B — Selective Depth. Active:** This fisher can set a line to a larger-specimen mode: an extra three base work seconds at setup, then one draw from a higher legal weight band. **Choice/pressure:** Spend scarce fisher labor for fewer handling jobs per kg. Still one fish per rig and the same automatic return; exact bias needs sampling tests.
- **C — Rig Preparation. Active:** On an empty uncommitted line, the fisher may complete non-bait setup work ahead of time; the later bait/launch action consumes fresh chum normally. **Choice/pressure:** Use a lull while waiting for chum, then launch promptly. One prepared state per line; no advance bait stock created, no work on an occupied line. Unlike A, labor moves in time rather than shrinking.

### CF07 — Blue Fisher · Mixed-method relief

**Role:** A cheap flexible fisher with a narrow personal advantage. **Dependencies:** Core.

- **A — Quick Reset. Active:** After three completed personal fishing cycles, the next personal setup takes half time. **Choice/pressure:** Flexible across allowed methods, with one stored discount. One cycle per completed rig/cast, not per specimen; no stacking charges or resetting other cards.
- **B — Light Feet. Active:** Walk 20% faster only on actual empty-handed approaches to a permitted fishing job. **Choice/pressure:** Covers separated stations better; does not speed hauling, soaking or operating actions. Gives geographic flexibility without changing base role speed.
- **C — Cold Start. Active:** The first personal setup after a real 20-second interval with no eligible fishing work takes half time. **Choice/pressure:** Useful as a relief worker when opportunity returns. Manual disabling, pause and voluntary idle time do not qualify; no incentive to sabotage work to farm the perk.

### CF08 — Purple Fisher · Rod strategy

**Shared passive for A/B/C:** Eligible team ordinary-rod reeling takes 15% less work time. **Dependencies:** Core; B new species-selection mode, C real helper position. Purple signature persists throughout its relevant work.

- **A — Rod Leader. Active:** While working an ordinary rod, reduces bite wait on staffed ordinary rods by 25%. **Choice/pressure:** Sustained rod team, with real crew on each station; powerful intake still needs deck support. Historical team-active exception, no unmanned rods.
- **B — Selective Angler. Active:** This fisher's rod can target one captain-selected eligible local species group by excluding other groups at cast time, with 30% longer bite waits and no replacement rolls. **Choice/pressure:** Stabilize a desired cargo/work family at lower encounter rate. Cannot target absent or locked species; selection is persistent, not per-cast clicking.
- **C — Rod Partner. Active:** May occupy a real helper position beside one staffed rod during reeling, contributing ordinary work to that same reel job. Owner does not run another rod simultaneously. **Choice/pressure:** Concentrate two fishers for brief large-catch recovery or keep them on independent production. Useful only if saved commitment time justifies helper travel; this is new cooperation, not stealing the rod.

### CF09 — Purple Fisher · Net strategy

**Shared passive:** Team deep-net catch mass budget +15%; normal nets unaffected. **Dependencies:** Core; B optional M36 refit job. Different packages deliberately support different types of net planning.

- **A — Deep-Net Saver. Active:** Personal successful deep-net hauls spend no use; failed hauls still spend one. **Choice/pressure:** Historical selected signature; makes stock pressure less relevant but does not remove retrieval, queues or load. If future baseline has no failures, admit that this yields indefinite successful uses; do not invent failures to nerf it.
- **B — Net Changer. Active:** At an empty rig, can perform an actual shallow/deep loadout change in half the ordinary refit work time. **Choice/pressure:** Adapt to composition/stock without needing a whole return trip, if M36 is selected. Consumes/retains stock by shared rules; no refunded used charges. Falls back to ordinary operation if refitting is not needed.
- **C — Compact Haul. Active:** Personal normal-net hauls use a larger-specimen-biased eligible distribution with a 20% smaller mass budget. **Choice/pressure:** Trade total catch for lower fish-count burden and fewer processing jobs. More specialized than a short proc; does not promise improved profit. Deep-net passive still supports a teammate even when owner chooses normal net work.

### CF10 — Purple Fisher · Cage strategy

**Shared passive:** All permitted cage cycles have 15% less soak duration. **Dependencies:** Core; B labor cooperation; C retained-catch cycle state.

- **A — Heavy Cages. Active:** Personal cage catches use a higher legal weight distribution, targeting approximately 50% greater mean mass only if the species bounds allow it. **Choice/pressure:** Retains historical direction without making impossible oversized crabs. A feasible smaller increase is preferable to secretly exceeding limits; final value unselected.
- **B — Cage Tender. Active:** Personally tend one soaking cage, contributing 50% additional soak progress while physically occupied there. **Choice/pressure:** Converts spare fisher time into cage output instead of rods. Leaving stops extra progress; no retroactive bonus, no ghost helper. Useful without the gold that enables team tending.
- **C — Reserve Chamber. Active:** This fisher's fitted cage kit can retain one finished catch while starting one further cycle; maximum two catches, then blocked. **Choice/pressure:** Tolerates temporary fisher recovery gaps but creates clustered collection later. Requires new visible cage state; no extra station, no unbounded catch storage or double simultaneous cycles. Ordinary recovery still lands each specimen for Deckhands.

### CF11 — Purple Fisher · Deep-line strategy

**Shared passive:** Team physical deep-line setup takes 15% less work time; chum cost, soak and automatic raise unchanged. **Dependencies:** Core; A new hold/release protocol, B eligible depth mode, C actual setup teamwork.

- **A — Timed Setter. Active:** Can complete a real baited deployment preparation into a secure ready state, then release it automatically at a captain-selected future offset without another worker visit. **Choice/pressure:** Shape a wave without tying up the fisher at release. One paid pending setup per rig; no other cycle can use it; cancellation does not refund consumed chum. Basic start delays remain universal, this saves the return visit through a new physical ready-state mechanism.
- **B — Deep Selector. Active:** May spend 50% more physical setup work on a setting that narrows the eligible local pool to a chosen heavy-species group. One legal specimen is still generated per completed line, never a guaranteed rare class. **Choice/pressure:** More predictable work composition costs fisher time; narrower targeting must justify its cost in sampler comparisons. No empty eligible group can be selected, no reroll or second fish.
- **C — Tandem Setter. Active:** Owner and one consenting allowed fisher can share the physical setup of a line, dividing the unchanged total work between them. **Choice/pressure:** Meet a close deployment window at the cost of abandoning parallel jobs. Both walk/occupy real positions; no useful second worker means owner works normally. No reduction of passive soak or automatic-raise labor because that labor is already absent.

### CF12 — Gold Fisher · Rod captain

**Shared passives:** Team staffed ordinary rods need 15% less bite-wait time; team ordinary-rod casting work takes 15% less time. No hauling/processing bonus. **Dependencies:** Core + new rod states; B cooperative handoff positions. These passives do not stack additively with stronger same-family Rod Leader effects.

- **A — Twin-Hook Specialist. Active:** Own rod fishes two independent hooks from one cast, each with a real eligible fish sequence; owner retrieves one at a time. **Choice/pressure:** More fish through one station, with bounded two-hook waiting and sequential human work. Neither another occupied rod nor duplicated specimens. Extra bait requirement must be explicit in the proposal's later balance; two portions is the conservative starting assumption. Historical unselected idea, not previously approved.
- **B — Live Rod Relay. Active:** Enables an explicit handoff of the owner's live rod to one consenting available fisher without losing its already committed cast. Incoming worker walks in and takes over; outgoing worker is freed for another permitted fishing job. **Choice/pressure:** Rotate attention toward ready net/cage work while preserving rod investment. Both workers and a short overlap are required; only one operates the rod at a time. It is not automatic multi-rod labor or baseline emergency fallback sold as gold.
- **C — Early Reader. Active:** During this fisher's personally hooked catch, identify its species and a weight band before the long reel completes; under a standing filter, release an unwanted fish and begin an entirely new paid cast normally. **Choice/pressure:** Trade spent bait/wait and foregone catch for saved reel/handling/hold work. One sampled fish is genuinely released, never replaced inside that cast. Useful for selective end-of-voyage plans, not guaranteed better RNG. Basic landed-fish information remains universal.

### CF13 — Gold Fisher · Net captain

**Shared passives:** All team nets have 20% less soak time; team human net retrieval rate +20%. **Dependencies:** A Flow; B Kit/cooperation; C new verified load-selection kit. Historical manual-wear surcharge stays withdrawn.

- **A — Back-to-Back Netter. Active:** Redeploy own net while its previous catch awaits unloading, with a hard limit of two landed-haul slots. **Choice/pressure:** More continuous fishing but larger support surges. When both slots are occupied, stop; unloading does not teleport. Release a slot only when its remaining cargo has physically left that basket. Historical selected core retained intact.
- **B — Net Team Leader. Active:** Opens a real second-fisher recovery position on the net this owner operates. A helper contributes work to its retrieval, with total work conserved and a nonzero joint finishing action. **Choice/pressure:** Compress a large retrieval into a short window or keep the helper on other fishing. Strong if timing matters, weak when support is already full. Real second position/rig animation required; this is not the previously rejected Split Haul staged landing.
- **C — Selective Net Kit. Active:** Before setting, choose a persistent sorting-mesh profile that generates only eligible local specimens in its selected size band, at a lower total catch-mass budget. **Choice/pressure:** Shape the downstream workload rather than enlarge it; can protect a small processing team or intentionally feed small-fish batching. One constrained haul generation, no rerolls or cherry-picking a second hidden haul. Compared with blue Wide Mesh, permits narrow lower/middle/upper bands; must earn gold status through useful control, not merely a percentage. If the control is too basic to gate, make it equipment instead and reject this option.

### CF14 — Gold Fisher · Cage captain

**Shared passives:** Team cage recovery work takes 20% less time; team cage catches use a modest larger-specimen bias within legal bounds, magnitude to sample. **Dependencies:** A cooperation; B/C Kit/Flow. No new cage sockets.

- **A — Cage Foreman. Active:** While assigned cage work, enables genuine tending for other permitted fishers: one occupied tender per soaking cage adds proposed 50% soak progress while present. Owner can also tend/recover. **Choice/pressure:** Concentrate fishers on two cages or free them for rods/nets. A completed cage still needs recovery and downstream work. Historical endorsed capability; no phantom workers or automatic catching without the necessary labor.
- **B — Turnaround Cage Kit. Active:** Owner's kit holds one recovered ready-to-deploy cage insert at the existing cage station. Preparing the spare requires real work while the current cycle soaks; after ordinary recovery, exchange inserts and restart promptly. **Choice/pressure:** Move setup labor into a quiet interval to reduce turnaround, then handle closer returns. No two simultaneous soaking cages, no extra catch per cycle, no skipped recovery. Needs a visible finite spare and useful baseline setup labor; reject if the existing setup is too trivial to support the identity.
- **C — Selective Cage Keeper. Active:** At recovery, owner can keep the single actual live catch in a separate one-catch compartment for later ordinary landing while starting the next cycle; at most one held plus one soaking. **Choice/pressure:** Deliver cages in a deliberate wave or defer one arrival while processors clear. Unlike purple Reserve Chamber's passive tolerance, the owner can explicitly schedule that held catch's landing with a real recovery action. No growth, reproduction or sale bonus while held; no third catch. Risk of overlap with Back-to-Back is real—choose only if cage-specific timing proves distinct.

### CF15 — Gold Fisher · Deep-line captain

**Shared passives:** Team deep-line physical setup takes 20% less time; team deep-line specimens get a modest higher legal-weight bias, magnitude unselected. **Dependencies:** Kit/new setup state. Every option preserves one fish per rig, the baseline passive soak, automatic raise and direct Deckhand collection. No free chum.

- **A — Spare-Trace Specialist. Active:** Owner has one physical spare trace per fitted rig and may prepare/bait it while that rig's current line is soaking. After automatic return and Deckhand clearance, owner performs a short real exchange/release job to start the next line. **Choice/pressure:** Move next-cycle labor into quiet soak time, spending chum early and committing to another cycle before seeing the current catch. Only one soaking line and one paid spare per rig; no double catch, deployment through blocked cargo or free preparation. Unused spare treatment on return must be disclosed; conservative comparison charges its consumed chum without a refund. Unlike purple Timed Setter, this prepares the NEXT cycle on occupied equipment.
- **B — Line Reader. Active:** During a soaking line, owner may perform a real short inspection that reveals a coarse weight band of its already committed specimen, without changing it or the automatic return time. **Choice/pressure:** Spend fisher time to reserve suitable handling/hold space or decline the next deployment; otherwise keep fishing with ordinary probabilistic forecasts. Requires sampling and preserving the specimen at deployment instead of generating it at landing, a substantial NEW state rule. No rerolls, guaranteed rares or essential dashboard information withheld from other crews. Information alone must earn its wage through better commitments; if it rarely changes a decision, this is not a worthy gold.
- **C — Depth Rig Specialist. Active:** Fit this fisher's existing deep rigs with a choice of two physical setting profiles before deployment: broad heavy pool with ordinary setup, or narrow trophy-size band with substantially more setup work. Selection persists, with one legal outcome per line. **Choice/pressure:** Commit labor/hold space to large catches or use more flexible supply; changes operating plan instead of adding hooks. Distinct from CF11B's species targeting: this controls specimen-size band across the permitted pool. Needs a genuinely consequential work tradeoff, not free premium fish.

### CD01 — Blue Deckhand · Loose catch collection

**Dependencies:** Core; B Load. **Role:** Many small landings versus infrequent heavy ones.

- **A — Quick Hands. Active:** Every third personal loose-fish pickup takes half handling time. **Choice/pressure:** Historical modest collection perk; walking, cutting and storage remain ordinary. A batch pickup counts once.
- **B — Paired Pickup. Active:** Can gather up to two compatible loose fish from the same landing station in one pickup action, within normal carrying allowance. **Choice/pressure:** Reduces trip starts during small-fish waves. No reaching across the boat, merging destinations or waiting for a second fish.
- **C — Heavy Grip. Active:** Picking up one indivisible fish above the ordinary load allowance takes half its pickup work time. **Choice/pressure:** Useful immediately on a heavy arrival; the fish still occupies a whole solo load and needs normal travel/delivery. No new weight penalty invented just for this perk.

### CD02 — Blue Deckhand · Walking

**Dependencies:** Core. **Role:** Different route patterns rather than global work speed.

- **A — Deck Runner. Active:** First three loaded trips per voyage walk 25% faster. **Choice/pressure:** Early startup support, then ordinary performance. Historical choice retained; count completed loaded trips, not cancelled routes.
- **B — Return Runner. Active:** Empty travel to an actual assigned collection job is 25% faster. **Choice/pressure:** Frequent short loads benefit, while occupied cutting time does not. Cannot trigger on idle wandering or fishing walks.
- **C — Heavy Pace. Active:** Loaded movement while carrying one large specimen is 20% faster. **Choice/pressure:** Heavy-catch builds benefit more than packed small-fish baskets. Does not alter picking, stowing or baseline speed when empty.

### CD03 — Blue Deckhand · Input delivery

**Dependencies:** Core; B Flow; C Load. **Role:** Reopen fishing stations without pretending input is the final hold.

- **A — Quick Set-Down. Active:** Every third successful delivery into processing input takes half set-down time. **Choice/pressure:** Smooth recurring feed; no effect on finished-output deliveries. Distinct from a universal stow discount.
- **B — Receiving Hand. Active:** While physically waiting at an input station for another carrier's arrival, can perform that carrier's set-down work, freeing the delivering worker after a real handoff. **Choice/pressure:** One stationary receiver versus two independently circulating carriers. One active receiving job, no automatic fish movement or duplicate labor; test whether the saved walking pattern earns a berth.
- **C — Basket Grip. Active:** Compatible net-basket inbound loads may use 25% more personal carrying allowance. **Choice/pressure:** Fewer trips for basket waves; raw loose fish/output retain ordinary loads. Needs the bounded-load baseline; never raises input capacity.

### CD04 — Blue Deckhand · Finished cargo

**Dependencies:** Core; B Load. **Role:** Prevent a fast processor from filling its output.

- **A — Quick Stow. Active:** Every third completed delivery into the main hold takes half stow work time. **Choice/pressure:** Historical identity narrowed to the actual final stage; cannot farm procs by splitting a load voluntarily.
- **B — Output Basket. Active:** Compatible finished-output loads may use 25% more personal allowance. **Choice/pressure:** Consolidates finished fish, but leaves inbound uncovered. No direct raw-to-hold bypass.
- **C — Ready Receiver. Active:** When this hand has physically waited beside a processing output for at least one normal pickup-action duration, the next completed fish can enter their hands through the processor's ordinary output placement, avoiding a separate pickup action. **Choice/pressure:** Trade worker waiting for immediate clearance. One real hand/one next output, no free advance processing or infinite reserved queue.

### CD05 — Blue Deckhand · Small-fish preparation

**Dependencies:** Core/new batch reservation. **Role:** Fish-count pressure. Small uses the shared provisional work threshold, not rarity.

- **A — Prep Hand. Active:** Every third personally processed fish has half cutting time. **Choice/pressure:** Works across ordinary eligible fish; completion emits one actual fish. Historical blue option; no discount to carrying.
- **B — Pair Cutter. Active:** Process two available small fish together in 1.75 ordinary cutting cycles. **Choice/pressure:** Modest count efficiency; starts one normally if only one is available, without waiting. One position, both real specimens reserved atomically.
- **C — Tiny-Fish Specialist. Active:** Own cutting work on fish at most half the small-fish threshold takes 30% less time. **Choice/pressure:** Stronger on genuinely tiny supply, ordinary elsewhere. Does not create tiny catches or change chum yield.

### CD06 — Blue Deckhand · Large-fish preparation

**Dependencies:** Core; C new safe saved-work state. **Role:** Useful on the first lone large specimen.

- **A — Heavy Cutter's Mate. Active:** Own large-fish cutting takes 20% less time, including a single arrival. **Choice/pressure:** Modest reliable heavy support; no queue/streak requirement and no extra sale entitlement.
- **B — One-Fish Setup. Active:** For a large specimen, the owner's input-positioning and output-placement actions together take half their usual work time. **Choice/pressure:** Improves handling at the table, not cutting. Likely small under current timings; retain only if observed value justifies the slot.
- **C — Safe Pause. Active:** Can checkpoint one partially cut large specimen into a dedicated one-fish table tray, perform another allowed Deckhand task, then resume retained work. **Choice/pressure:** Rescue a temporary outbound blockage without losing cutting progress. Tray occupies real finite space and no extra processing position; no cutting while walking. Unlike rejected Mobile Filleter, preparation remains at the table.

### CD07 — Blue Deckhand · Flexible support

**Dependencies:** Core; B Load; C Family. **Role:** A small incentive to cover a changing gap.

- **A — Relief Hands. Active:** First completed handling action after a genuine switch between inbound and outbound duty takes half work time, at most once per 30 seconds of productive work. **Choice/pressure:** Rewards actual mixed logistics; toggling orders without jobs does nothing. One personal automatic benefit, not another card reset.
- **B — Versatile Basket. Active:** Can carry compatible small fish from two adjacent stations on one bounded route before delivery, if destinations match and total load fits. **Choice/pressure:** Consolidate sparse arrivals; added walking may be worse than a direct trip. No waiting for cargo or crossing half the boat to fill a load.
- **C — Quick Change. Active:** Personal processing-family setup takes half time. **Choice/pressure:** A cheap generalist for mixed inputs if M25/M26 is chosen; no benefit in the current single-recipe baseline. Clearly conditional rather than inventing a hidden setup cost now.

### CD08 — Purple Deckhand · Small-fish processor

**Shared passive:** Team small-fish cutting rate +15%. **Dependencies:** Core/batches; C new output staging within one job. One processing position per job.

- **A — Batch Cutter. Active:** Process three available small fish in the normal cutting work for two. With one/two available, process immediately at ordinary per-fish work; do not wait to fill. **Choice/pressure:** Historical core with an explicit proposed shortage rule; produces output bursts and needs carriers.
- **B — Continuous Cutter. Active:** On every small-fish job, owner combines input positioning with the previous output placement when both are physically available at the same table position, charging one shared handling action instead of two. **Choice/pressure:** Sustained stream efficiency, but no shortcut when starved/blocked. Does not shorten cutting itself; prototype must show a meaningful gain before accepting purple rarity.
- **C — Serial Batch Cutter. Active:** Reserve up to three small fish for a run using one input setup and one final cleanup, but release each completed specimen to ordinary output immediately. Each fish still takes its ordinary cutting work. **Choice/pressure:** Less staging overhead than independent jobs and smoother output than A, at lower bulk cutting efficiency. Finite output may stop progress safely; no hidden extra table worker.

### CD09 — Purple Deckhand · Large-fish processor

**Shared passive:** Team large-fish cutting rate +15%. **Dependencies:** Core; B two-worker physical cooperation; C new whole-specimen staged work. No option requires a second large fish.

- **A — Heavy Cutter. Active:** Own large-fish cutting takes half normal time, even for a lone specimen. **Choice/pressure:** Preserves the selected direction; promptly creates outbound work. Do not claim it increases value or solves carrying.
- **B — Shared Cut. Active:** This worker can divide one large specimen's cutting job with another available processor at the second real position. Total cutting work is conserved and final completion waits for both portions. **Choice/pressure:** Finish one important fish sooner by sacrificing parallel processing. Physical portions retain one fish identity/value; no extra catch count. This was an unselected historical alternative, not one of the rejected D10 concepts.
- **C — Rough-and-Finish. Active:** Owner can perform the first half of cutting on a large specimen, safely stage it as unfinished work, then let an ordinary processor perform the final half later. **Choice/pressure:** Decouple specialist availability from final completion while preserving total work and one original fish. No finished output until all work is done; this is a handover of actual cutting, not the rejected assistant pre-cleaning aura. If indistinguishable in play from ordinary job handoff, make it baseline rather than a card.

### CD10 — Purple Deckhand · Heavy transport

**Shared passive:** Team loaded walking rate +15%. **Dependencies:** Load; C Flow/Kit. No increased table or hold capacity.

- **A — Heavy Lifter. Active:** Twice ordinary load allowance; 20% slower loaded movement only when exceeding ordinary allowance. **Choice/pressure:** Historical explicit tradeoff. Large batches reduce trips but may block destinations. Personal slowdown and team passive combine on loaded travel only, not all work.
- **B — Sling Carrier. Active:** When carrying one indivisible fish heavier than ordinary allowance, a personal sling leaves room for one additional bounded bundle of compatible small fish from that same station, up to half the ordinary allowance. **Choice/pressure:** Heavy-plus-small mixed arrivals can share a trip; ordinary all-small loads receive no capacity increase. No added slowdown, cargo teleportation or combination of raw and finished destinations. Unlike A, this changes packing around an oversized specimen rather than multiplying every load limit.
- **C — Two-Stop Carrier. Active:** Use two bounded compartments to carry a compatible inbound load and a finished-output load on a planned two-stop route when both can be picked up without destination conflict. **Choice/pressure:** More useful travel, but waiting/extra detours can erase the gain. Combined weight still respects ordinary allowance; physically separate raw/finished compartments and safe reservations required. No raw fish silently stored as prepared.

### CD11 — Purple Deckhand · Flexible processing and logistics

**Shared passive:** Team pickup/set-down work rate +10%; no cutting/walking increase. **Dependencies:** A Core, B Flow, C Family. Aim: a sustained flexible role, not a tiny triggered purple.

- **A — Working Processor. Active:** Owner's ordinary non-chum cutting takes 25% less time while assigned both processing and carrying duties. **Choice/pressure:** A genuinely useful flexible hand whose processing speed is moderate rather than specialist-level. They still execute one job at a time; permissive flags alone do not create extra labor. If optimal play simply enables an unused flag, require actual mixed jobs over a broad recent window or redesign—not a hidden punitive timer.
- **B — Transfer Bench. Active:** Owner can accept one real unprocessed specimen directly from an inbound carrier into their free table position, combining that carrier's set-down with the owner's input positioning. **Choice/pressure:** Helps a starved table start promptly while input staging is tight. Owner must be present/free; ordinary input routing remains available. Does not bypass cutting or final output and must not create a third station.
- **C — Recipe Generalist. Active:** Owner retains setup for two preparation families at one position, changing between those two without paying repeated setup; switching to a third replaces one. **Choice/pressure:** Handles mixed supply smoothly but lacks narrow specialist cutting strength. Requires M25/M26 and real two-kit footprint, not free extra table capacity.

### CD12 — Gold Deckhand · Station clearance

**Shared passives:** Team loaded walking rate +15%; team inbound set-down work rate +15%. **Dependencies:** Load/Flow; B/C Kit. The owner is still one physical worker.

- **A — Power Lifter. Active:** Pick up the remaining eligible contents of ONE station in one trip regardless of weight. Choose the heaviest reachable eligible station; pre-pickup claimants yield safely, already carried cargo stays with its carrier. **Choice/pressure:** Clear a huge basket to restart fishing, but dump a surge into finite processing. No invented slowdown, no merging incompatible destinations and no enlarged hold. This preserves Mo's custom selected ability exactly in direction.
- **B — Exchange Crate Porter. Active:** Own two finite compatible cargo crates that can be loaded by ordinary hands while the owner carries the other. Owner physically swaps an empty crate for a loaded one, then travels/delivers normally. **Choice/pressure:** Separate collection from transport, spending another worker to keep the route supplied. Crates have bounded mass, occupy actual staging, and do not hold cargo from incompatible stages. Unlike A, this changes collaboration rather than abolishing weight limits.
- **C — Rolling Platform. Active:** Use one manually moved platform with a larger finite load, gathering from several compatible stations on a planned route before delivering. **Choice/pressure:** Consolidate distributed arrivals rather than empty one station. Needs wide validated routes and real gathering; platforms do not fit arbitrary current corridors by assumption. No engine/robot, hidden speed boost or waiting to fill. Strong only where geometry makes a route worthwhile.

### CD13 — Gold Deckhand · Bulk preparation

**Shared passives:** Team small-fish cutting rate +10%; team processing output-placement work rate +15%. **Dependencies:** Atomic whole-fish batches and real output space. All options start with available inputs immediately; no mandatory batching timer.

- **A — Bulk Processor. Active:** Start with the heaviest eligible fish. If it exceeds 5 kg, process it alone. Otherwise add whole fish until strictly above 5 kg, choosing the smallest available crossing finisher; if total supply is 5 kg or less, process it immediately. Proposed work: one ordinary cutting cycle per batch. **Choice/pressure:** Preserves Mo's rule: 4.9+4.9 becomes 9.8; 4.9+4.8+0.5 becomes 5.4, leaving 4.8. Huge count efficiency can flood output. Intermediate fill order remains proposed; no splitting or trimming.
- **B — Same-Work Batch. Active:** Process up to four available small fish of one preparation family together, using one base cutting cycle plus a quarter cycle for each additional fish. A lone large fish works normally. **Choice/pressure:** Efficient uniform supply; mixed families lose batch opportunities. Unlike A, count/family determines benefit, not a weight-crossing puzzle. Requires clearly defined families or initially one simple small-fish family; immediate partial batches.
- **C — Companion Cut. Active:** One large fish may share a cutting job with up to two available small fish on a dedicated side portion of this owner's bench kit; total cutting work is the large-fish job plus half a small-fish job per companion. With no large fish, process small fish normally; with no small fish, process the large one normally. **Choice/pressure:** Rewards genuinely mixed intake rather than pure small-fish volume. One position, reserved real specimens and no delay awaiting partners. Added bench footprint must fit; no extra sale value or simultaneous phantom worker.

### CD14 — Gold Deckhand · Logistics cooperation

**Shared passives:** Team pickup work rate +15%; team final hold-stow work rate +15%. **Dependencies:** New cooperative route/transfer jobs; finite staging. Do not combine these passives with weaker same-family boosts additively.

- **A — Relay Foreman. Active:** Owner participates in an explicit cargo relay with another hand across a real reachable transfer point. Each covers a route segment; transfer takes real work and needs a receiver or one bounded buffer. **Choice/pressure:** Divide an uneven route or keep two independent carriers. Cannot teleport, skip processing or spawn a helper. Historical unselected D09 direction; separate from rejected D10 pre-cleaning/mobile processing.
- **B — Loading Partner. Active:** Owner can work beside one carrier at a landing station and perform that carrier's gathering while the carrier receives the load; then the carrier departs and owner continues another allowed job. **Choice/pressure:** A dedicated gatherer helps a high-capacity carrier leave sooner, but consumes a berth that might clear output. Total handling is performed, not deleted; coordination saves only actual overlap/duplicated transitions. Distinct from A's geographic route split.
- **C — Destination Marshal. Active:** Owner staffs a receiving point and splits arriving compatible loads into already reserved destination jobs, handing them to available outbound/next-stage carriers. **Choice/pressure:** Break a large incoming batch into work that fits finite destinations, while other carriers avoid standing with incompatible partial loads. Owner and receivers occupy real jobs; no auto-processing or magic overflow. High implementation/geometry risk; reject if competent baseline dispatch already achieves the same result without a dedicated marshal.

### CD15 — Gold Deckhand · Flexible production lead

**Shared passives:** Team processing input-positioning work rate +15%; team empty walking to Deckhand jobs rate +10%. **Dependencies:** A/B Family/Kit; C Flow and physical station handover. No global speed aura or chum-yield bonus.

- **A — Dual-Kit Master. Active:** Owner keeps both ordinary preparation and a second selected preparation family ready at the same table position, and can checkpoint one unfinished job in a finite tray while working the other. **Choice/pressure:** React to mixed urgent supply without repeating setup or discarding progress. One active job at a time; tray consumes staging. Unlike CD11C, adds actual work suspension, not just retained setup. Needs M25/M26; otherwise unsuitable.
- **B — Changeover Lead. Active:** While personally working at a table, owner can perform the next recipe setup for the neighboring empty position as part of a real separate preparation job, before its processor arrives. **Choice/pressure:** Spend specialist time to make a forthcoming team reassignment fast. No extra job overlap in the owner's clock, no assisting an occupied position, and no free cutting. Gold value depends on meaningful family changes; this is not the rejected pre-cleaning-assistant ability.
- **C — Shift Handover. Active:** Owner can accept a partly completed processing job at a real handover, or hand theirs to another permitted processor, preserving work and keeping the table in its current setup. The released worker can perform carrying/chum work elsewhere under normal rules. **Choice/pressure:** Reallocate people around long jobs without abandoning cargo. Both workers must meet; one job never counts twice. If ordinary shared work should already allow this, make it baseline and reject the card—do not make everyone else forget how to finish a cut to sell gold.

## 10. Choosing between the packages

### What is deliberately retained, replaced or reopened

| Historical direction | Treatment here |
|---|---|
| Strong Start, Fast Bite, First Set, Loaded Net, Quick Soak, Quick Reset | Retained among blue alternatives, not assumed final. |
| F06 Quick Retrieve on longlines | Replaced: deep lines return automatically, so a manual retrieval-time skill has no honest job to accelerate. CF06 affects setup or targeting instead. |
| Deep-Net Saver, Rod Leader, Heavy Cages | Retained/reconciled among purples; legal specimen limits made explicit. |
| Back-to-Back Netter, Cage Foreman | Retained among gold alternatives; no withdrawn manual-wear surcharge. |
| Twin-Hook | Still an unselected reference option; needs real two-hook behavior. |
| Power Lifter | CD12A retains unlimited weight from one station and no added slowdown. |
| Bulk Processor | CD13A retains whole-fish threshold and immediate partial-batch rules; timing remains a proposed value. |
| Heavy Cutter | CD09A works on the first lone large fish. |
| Chum Captain/School Caller; rearm/reset synergies; Master Netter wear package; Clear Deck/Fresh to Market | Not restored. |
| Mobile Filleter; Prep Foreman pre-cleaning; Passage Processor | Not reused. Some new handover proposals are explicitly cutting/logistics work, with a baseline-versus-card test. |
| Engineer roster | Outside the 30. Later expedition machinery needs its own role contract before its cards. |

### My strongest directions, without pretending every option is equally good

**Best established anchors:** CF08A Rod Leader, CF09A Deep-Net Saver, CF13A Back-to-Back, CF14A Cage Foreman, CD09A Heavy Cutter, CD12A Power Lifter and CD13A Bulk Processor. They have distinct work consequences or already reflect Mo's specific ideas.

**Most promising newer directions to compare:** CF12B live rod handoff, CF12C early catch selection, CD10C two-stop carrying, CD12B exchange crates and CD13C mixed companion batches. These alter timing, routing or workload shape. They need physical-state prototypes before being called better than their alternatives.

**Most conditional:** CF15 preparation/inspection and CD15 family/handover concepts. Their value depends on meaningful work or decisions to affect. With tiny setup times, predictable catches and one universal preparation recipe they risk becoming an elaborate name for a negligible benefit. The document supplies three proposals per slot as requested, but I would not inflate numbers to pretend these are automatically compelling golds.

**Likely equipment/baseline rather than cards if testing says so:** selective mesh controls, basic handovers and sensible route consolidation. If every captain should reasonably have a control, put it in the base game. A card must add a real capability or measurable efficiency beyond it.

### Four six-person build sketches

These illustrate role allocation, **not tested optimal builds**. Pick one option per named slot. Assume ordinary allowed-duty controls and no routine captain labor.

| Build | Six hires | What makes it work | What makes the captain reconsider |
|---|---|---|---|
| Rod-heavy | CF08A, CF12A, CD01B, CD04B, CD08A, CD11B | Two actual rod fishers, two carriers, two possible processors. Twin hooks raise count; batching and receiving keep table feed moving. | Small-fish flood fills output; one processor may need carrying duty. Only two ordinary rods are staffed; extra rods do not earn phantom income. |
| Net-heavy | CF13A, CF09A, CD12A, CD10B, CD13A, CD09A | Two fishers for two fitted nets; powerful inbound clearing, mixed-load sling carrier, two processing types. | Deep-stock saving changes economics; many small normal-net fish favor bulk, isolated heavy catch favors Heavy Cutter. Power Lifter can still flood output. No deep-line income on the side-net layout. |
| Deep mixed | CF11A, CF05B, CD10A, CD04B, CD09A, CD11B | Two fishers divide deep setup/cages/allowed rods; two carriers, two possible processors including chum. | Cheap feed disappears, deep returns collide with ordinary catch, or chum production consumes a needed table position. Count every real job once. |
| Adaptive mixed | CF07B, CF10B, CD07B, CD10C, CD08A, CD11C | Less maximum output, more movement/route/family flexibility; one flexible carrier and a generalist processor. | Favorable phases may justify concentrating a fisher, while unusual composition rewards the generalist. CD11C only makes sense if preparation families are adopted. |

No build runs every installed device continuously. Disabling an optional method is a legitimate decision, not a failure to use the boat. No mandatory one-of-every-role template.

### Why 90 options do not mean 90 equally independent mechanics

Blue alternatives intentionally include straightforward timing/load benefits; earlier feedback allowed those. Purple and gold aim at sustained strategies and capability changes. Some options are cross-method counterparts or share a physical foundation. That is useful for comparison, but selection should remove redundant identities. CF11A schedules an empty rig's already prepared deployment; CF15A prepares a subsequent paid trace during the occupied rig's soak. If these still feel like the same job in play, keep only the more useful identity.

## 11. How to test whether this actually fixes the problem

No runtime, spreadsheet Monte Carlo or play-balance simulation was run for this document. The following is a proposed next design experiment, requiring separate implementation authorization.

### Compare systems before comparing card power

1. Current/no-cards baseline with its actual source snapshot.
2. Redesigned ordinary-load/buffer baseline, still no cards.
3. Add composition/phase changes and chum competition, still no cards.
4. Compare representative selected card packages and six-worker allocations.

Otherwise a carrying limit or a new queue can be falsely credited to an exciting legendary.

### Use matched scenarios

Give the same environmental sequences and random seeds to a fixed-policy crew and an adaptively managed crew. Include: steady supply, many-small wave, few-heavy wave, deep/net return collision, empty chum startup, cheap feed disappearing, output blocked, nearly full hold, both layouts, base/upgraded deep rigs, unavailable optional machinery, and an intentionally idle captain.

The adaptive player may change policies and real duty assignments at safe boundaries. They do not get extra invisible labor, perfect fish foresight or free time while paused. Compare actual stored/prepared sale entitlement and net voyage income, not theoretical landed value alone.

### Measure decisions, not clicks

| Question | Evidence to collect | Failure signal |
|---|---|---|
| Does the best response change? | Record the circumstance, two viable options and which actually wins under matched scenarios. | Every pressure is solved by adding one carrier or using the same fixed priority. |
| Does management matter without carrying? | Captain manual labor seconds, policy changes, secured income and queue recovery. | Adaptive gain requires repetitive manual pickup. |
| Is the change legible? | Can a player explain why input/output is growing and predict the next commitment? | Guesswork, hidden modifiers or staring at crew animations. |
| Does automation still feel earned? | Conservative unattended performance and length of calm intervals. | Every improved crew is immediately targeted by stronger penalties. |
| Are cards distinct? | Marginal swap in the same scenario, worker-seconds and stage consequences. | One gold dominates all phases or three alternatives differ only in label. |
| Are pauses strategic? | New decision quality after pausing, not punishment avoided through fast clicking. | Required interactions every few seconds. |
| Are outputs honest? | Landed mass = queued + carried + processing + stored + explicitly consumed chum inputs + separately recorded intentional losses. | Batching creates fish, partial destinations lose fish, or consumed input is still sold. |

### Stop conditions for bad ideas

- If the dynamics do not create at least two different advantageous responses in a voyage, revise the dynamics before adding more cards.
- If a sensible permanent policy handles everything and the captain has no interesting optional opportunity, variety is cosmetic. Change competing objectives or work shape, not random failure rates.
- If an automatic policy handles routine repetition but the captain still makes worthwhile occasional commitments, that is success, not a reason to remove the automation.
- If a proposed helper spends more time traveling/waiting than it saves, do not grant a magical global buff to rescue the fantasy. Reject or redesign the physical job.
- If staged work is mainly reservation/debug complexity with no clear player choice, make ordinary safe behavior robust and remove the card.
- If losing a forecasted opportunity feels like punishment rather than a tradeoff, soften or lengthen it; no forced reload optimization.

### Initial review order

First choose the dynamic combination and the captain's decision rhythm. Then choose four/five anchor cards, compare ordinary support against them, and only then select the remaining collection. The document contains all 30×3 now so Mo can explore directions, but implementing ninety drafts or finalizing their wages before the core loop earns them would waste work.

## 12. Evidence, status and handoff

**Document status:** complete proposal set, not an approved design specification. Values are illustrative. No source, assets, save data, installed players or existing canonical card selections were changed by CARDS106. No subagents were dispatched. No claim that compilation, native play, balance simulation or visual review occurred for these proposals.

**Project source anchors:**

- `comms.md`: LOOP051/MGMT052 problem framing; CREW065/066/067 rejection sequence; CREW075–089 logistics and processing; CREW094–099 electrical-only/new human-operation direction; TIER5-102 saved research; DEEP104 current implementation; CARDS105 current answers; CARDS106 this document.
- `docs/CREW-CARDS-DESIGN.md`: historical selected alternatives, exact Power Lifter/Bulk Processor rules, automatic ability structure, discarded ideas.
- `docs/TIER5-102/ASTRA-RESEARCH.md` and `ASTRA-QUESTIONS.md`: prior source/history audit; superseded catch count/timing/chum/captain assumptions identified in sections 1–2.
- `docs/CREW-MANAGEMENT-INTEGRATION.md`: actual work accounting, shared forecast calculations, batches and effect invalidation.
- `docs/GAMEPLAY.md`, `docs/CONTINUATION.md`, `docs/plans/PLAYABILITY-PLAN.md`, `TODO.md`: gameplay and progression context; older entries are not proof of current installed behavior.
- `Assets/Scripts/Game/DeepLineRules.cs`, `VoyageDeepLines.cs`, `VoyagePrepOrders.cs`: read-only current deep setup/return and processing/chum context. Peer is actively editing these; re-snapshot before numeric modeling.

External source links are embedded next to their supported observations in section 3. Catchline proposals are original adaptations, not copied game specifications. No real-world fishing safety or legal claims are made.

**Canonical proposal:** `C:/Users/momoy/Projects/Catchline/docs/CARDS106-DYNAMIC-MANAGEMENT.md`. The chat output is an identical dated copy. Continue selection in this proposal or a follow-up decision record; do not overwrite historical approvals as if they had never existed.

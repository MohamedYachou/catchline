> **CREW098 — authoritative correction from Mo:** Electrical machinery must have its own support jobs and introduce additional management bottlenecks. It must not take over the fishing, hauling or processing jobs that give fishers and deckhands their purpose. Electric reels/haulers and the crew-replacement premise of CREW097 are rejected. That eight-card draft is withdrawn pending a machine-role redesign; earlier selected crew cards are preserved. Historical machine proposals below are not approval and must be reassessed against this constraint. No new machinery or replacement card has been selected.

# Electrical engineer alternatives — CREW097

Design only; all alternatives and numbers below are proposals, not replacements already selected. Eight engineers: three blue, three purple, two gold. Choose one A/B/C signature per card. Purple/gold listed passives are shared across their three alternatives and can be changed separately.

## Rules and workload

Only electrical machines have engineer condition. Manual rods, nets and cages do not. Normal nets have unlimited uses; deep nets have three consumable uses. Standard maintenance starts below 80%; broken machines require repair to 100%, except the selected Fault Specialist early-restart ability. Proposed ordinary service completion is 100%.

Machine families here are proposed future modules: retrieval (electric reels/net/cage haulers), processing, handling (conveyors/sorters). No machine roster or power economy is selected by this document.

Power Lifter removes one station load's carry-weight limit, not collection/travel/delivery time or destination capacity. His large deliveries pressure processing; Bulk Processor then pressures outgoing transport/storage. Do not secretly cap these selected abilities. A complete, well-supported build SHOULD run well. Challenge comes from finite crew/deck slots, workloads and different catch patterns, not forced random breakdowns.

More machine cycles create more electrical service demand per minute. Ordinary speed increases need not additionally increase wear per cycle; overdrive explicitly can. Idle/blocked machinery does not incur productive-cycle wear. No ability skips finite input/output, cargo identities, physical feeding, machine eligibility or storage.

## Blue — one automatic signature each

Family scopes replace old rod/net/cage specialization only if Mo chooses them. They affect electrical machines, not manual worker speed. All rates are tuning proposals.

### E01 Retrieval Electrician
A — Retrieval Bias: powered retrieval 20% faster; powered processing/handling 5% slower.
B — Hard Pull: powered retrieval 30% faster, with 30% more electrical condition consumed per completed retrieval; other families unchanged.
C — Dedicated Service: personally restores retrieval-machine condition 40% faster, but other electrical machines 15% slower.
Pressure: A/B bring fish aboard faster; C sustains retrieval while other machines can build a service backlog.

### E02 Processing Electrician
A — Processing Bias: powered processing 20% faster; powered retrieval/handling 5% slower.
B — Hard Cut: powered processing 30% faster, with 30% more electrical condition consumed per processed workload; other families unchanged.
C — Dedicated Service: personally restores processing-machine condition 40% faster, but other electrical machines 15% slower.
Pressure: faster processing needs sufficient feeding and output collection; specialist upkeep spends less time here but is weaker elsewhere.

### E03 Handling Electrician
A — Handling Bias: powered conveyors/sorters 20% faster; powered retrieval/processing 5% slower.
B — Fast Transfer: powered conveyors/sorters 30% faster, with 30% more electrical condition consumed per transferred workload; other families unchanged.
C — Dedicated Service: personally restores handling-machine condition 40% faster, but other electrical machines 15% slower.
Pressure: clear one transport leg faster and fill the next queue. Manual disconnected routes still require workers.

## Purple — one signature and one team passive each

### E04 All-Round Mechanic
A — Quick Service: personal routine maintenance 25% faster across electrical machines. Retains the previously selected direction.
B — Thorough Service: personal routine service takes 25% longer; serviced machine consumes 20% less electrical condition until its next ordinary service threshold crossing below 80%. No stacking or fault immunity.
C — Walking Workshop: during routine service, also service one second electrically healthy machine within explicitly defined reach at 40% of normal maintenance rate. Main job remains normal rate; only eligible below-80 jobs start. No remote service, no second fault repair.
Shared passive: all engineers walk to service jobs 10% faster.
Pressure: A saves service labor; B buys fewer visits with longer visits; C rewards compact machine placement but ties this engineer to one location.

### E05 Fault Specialist
A — Fast Recovery: personally repairs broken electrical machines 35% faster; restart still requires 100%.
B — Early Restart: personally repaired machine resumes at half repair progress, while this engineer continues to 100%. Retains selected ability; exact repair-progress/condition mapping remains an implementation decision.
C — Patch and Return: at half repair progress, personally repaired machine may resume at 50% operating speed and engineer may leave. Full speed requires finishing the repair. Existing wear still applies; no repeated patch resets or permanent fault immunity.
Shared passive: all engineers perform routine maintenance 10% faster. This proposes a clear rate replacement for the older ambiguous condition-restoration passive; not silently approved.
Pressure: A costs full downtime; B occupies the engineer while production resumes; C temporarily restores several routes at reduced capacity while accumulating unfinished repairs.

### E06 Machine Tuner
A — Balanced Tune: all electrical machines work 15% faster; normal electrical wear per workload.
B — Aggressive Tune: all electrical machines work 25% faster and consume 25% more electrical condition per workload.
C — Selective Tune: electrical machines with occupied input and free output work 30% faster while this engineer physically attends ONE of them. They cannot maintain anything during this operating job. Normal wear per workload.
Shared passive: all engineers perform fault repairs 10% faster.
Pressure: A/B increase actual service jobs per minute; B also costs more service per fish. C makes the player choose machine assistance versus maintenance through duty priorities. No bonus for bite/soak time or manual processing.

## Gold E07 — boat-support engineer

One support signature plus two team passives. Applies across electrical machine families.

A — Overdrive Operator: this engineer can attend one healthy machine and run it 50% faster. That machine consumes 50% more condition per workload. The engineer cannot service other machines while operating it; automatic job priorities govern attendance. Empty/full queues stop productive work normally. Creates a new operating job usable at the current weak stage; no promise that one engineer automatically solves every bottleneck.

B — Service Foreman: while this engineer performs routine upkeep, up to TWO available deckhands can assist at that same machine. Each contributes 50% of a normal engineer's maintenance rate. They physically attend, leave their usual work, and cannot repair breakdowns independently. Normal engineer work continues. This adds a new deckhand support job; priorities/cap control it automatically. Faster recovery costs hauling/processing labor.

C — Emergency Drive: this engineer can install ONE portable substitute drive/controller on a broken compatible electrical machine, restoring operation at 50% speed while its original unit awaits full repair. Installation/removal occupy the engineer; original repair work is unchanged. Substitute has finite electrical condition and needs physical service too; no duplicate drive. This is a proposed new card-enabled machine capability, not existing equipment. One essential route can limp along, but throughput and repair debt remain.

Shared proposed passives:
- All electrical machines operate 10% faster.
- All engineers perform routine maintenance 15% faster.

Pressure: A pushes a chosen stage at a maintenance cost; B borrows workers from production; C accepts reduced throughput while repairing the boat. Neither passive speeds manual crew jobs. Support legend is good at its own baseline maintenance too.

## Gold E08 — maintenance engineer

One technical signature plus two team passives.

A — Reserve Service: after personally servicing a machine to 100%, engineer can spend an additional half-normal service duration to install a 20-point condition reserve. Future wear uses that reserve first. One reserve per machine, no stacking; renewal requires another actual service visit and extra work. Gives a visibly finite buffer against surges by spending labor before them. Does not erase fault causes independent of condition.

B — Hot-Swap Specialist: carries ONE compatible spare electrical module. A physical swap replaces a failed module and restores the machine to 100%; then engineer must repair the removed module through the full ordinary repair workload before another swap is available. Swap itself takes time (proposed 25% of ordinary full repair duration). Total engineer work increases; machine downtime falls. Abstract standardized electrical module compatibility must be explicitly designed, not assumed real-world universal. No swapping fish/queues or repairing two units simultaneously.

C — Service Crawler: deploys ONE small maintenance device at a healthy machine below 80%. It restores condition at 40% normal engineer maintenance rate while engineer works elsewhere; stops at 100%. It cannot fix breakdowns or move itself between machines. Deployment, retrieval and relocation occupy the engineer. This is a proposed new card-enabled device, not existing machinery. Grants limited parallel routine upkeep, while faults and other machines still compete for the engineer.

Shared proposed passives:
- All engineers perform routine maintenance 20% faster.
- All engineers perform fault repairs 15% faster.

Pressure: A trades extra present labor for future tolerance; B moves repair downtime from machine to occupied engineer; C adds one slow service job but requires placement/travel. No whole-boat unlimited wear immunity.

## Build sanity checks and open balance work

Illustrative, not measured: 24 kg/min arriving, 35 carried, 12 processed => processing caps output near 12. If processing is improved to 20 while output carrying is 14, output carrying is next constraint. Real capacities must use fish mix, batches, walking and shared labor; do not treat every existing job as kg-linear.

Power Lifter plus Bulk Processor plus support gold and maintenance gold spend four crew berths before fishers/other workers. On six-crew Tier5 this matters; future 12-crew layouts need actual machine/space/queue/service balance. Do not claim these packages are balanced without simulation.

No forced re-selection of existing fisher/deckhand cards. Previously selected engineers remain recorded; these are replacement candidates only. One signature per new blue; one plus passive per purple; one plus two passives per gold. Numbers, stacking and levels need later tuning. When several percentage speed cards combine, define shared stacking and include their actual service consequences in Management; do not silently compound everything.

Recommended starting discussion: 1A/2A/3A, 4A, 5B, 6A, 7A or 7B, 8B. Recommendations are not selections.



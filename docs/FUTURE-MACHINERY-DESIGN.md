> **CREW098 — authoritative correction from Mo:** Electrical machinery must have its own support jobs and introduce additional management bottlenecks. It must not take over the fishing, hauling or processing jobs that give fishers and deckhands their purpose. Electric reels/haulers and the crew-replacement premise of CREW097 are rejected. That eight-card draft is withdrawn pending a machine-role redesign; earlier selected crew cards are preserved. Historical machine proposals below are not approval and must be reassessed against this constraint. No new machinery or replacement card has been selected.

# Future machinery and five-tier progression — proposal

18 October 2026 · CREW093 · Codex 1 (Windows app), for Mo.

## Status and scope

Mo confirms no higher-tier machine roster is decided and asks us to propose one.
This is a researched game-design proposal for tiers6–10 after currentTier5, not
an approved machine list, boat size plan, implementation task or finished balance.
Older GAMEPLAY/artist notes mention conveyors, haulers and freezing but are not
current approval. Their old school-chasing/trawling direction does not override
the present fixed-position fishing constraint. Preserve all selected crew cards.

**Latest approved scope, CREW094:** Engineer upkeep applies only to electrical
components of powered equipment. No condition/wear on bare rods, nets or cages.
Interpret machine-condition discussion below as its electrical drive/control unit,
not every physical component. CREW095 confirms normal nets have unlimited uses and
deep nets have three uses each, separate from electrical condition. This scope
change is design, not implemented runtime behavior.

The crew decision record is [CREW-CARDS-DESIGN.md](CREW-CARDS-DESIGN.md).
Canonical document is this project file; chat outputs copy is a snapshot.

## Real equipment worth adapting

- Hydraulic pot haulers mechanically retrieve pot lines; [Mustad's manufacturer
  description](https://mustadautoline.com/pot-haulers/) explains that equipment.
- Electronic jigging machines work a hooked line vertically and automatically retrieve
  catches. [Mørenot's R1](https://www.morenot.com/fishery/jigging-machines/r1-jigging-machine)
  supports depth settings and species-oriented programs. This is a useful candidate
  for a fixed-position game; the game still needs its own fishing/catch model.
- [Mustad coastal autoline](https://mustadautoline.com/coastal-hydrelic-systems/)
  provides longline equipment on coastal boats. A game deployment from one station
  would abstract real line setting/retrieval, not imply real vessels deploy entire
  lines without moving. It would make the retained F06 longline concept usable if chosen.
- [JBT Marel's onboard processing](https://jbtmarel.com/en/fish-and-seafood/whitefish/)
  includes weighing, grading and filleting. A fish-processing machine is not one
  universally compatible appliance for every species/size.
- [Marel marine graders](https://cms.prd-jbt.marel-envr.com/en/products/marine-graders/)
  weigh separate products and distribute them into grades/batches. This supports
  a gameplay sorter directing different catches to different work queues.
- [FAO's freezing-at-sea guidance](https://www.fao.org/4/V3630E/V3630E14.htm)
  distinguishes actual freezing from later cold storage and discusses processing,
  handling and limited space. Cooling would be a functional stage only if the game
  gives it a purpose beyond already-permanent prepared freshness.

These sources establish real equipment families. Tier order, rates, power budgets,
crew jobs and abilities below are our proposed game abstractions, not manufacturer
recommendations or realistic sizing/capacity promises.

## Proposed progression: one new management problem per tier

### Tier6 — Powered handling

Offer a powered net/pot hauler upgrade plus an alternative jigging-reel module.
Keep modules competitive for limited deck positions rather than install everything.
Powered retrieval is faster and supports greater intake, but still needs fishers,
catch collection, processing and stowing. Crew unloading the catch can become slower
than the hauler. Engineer visits now have multiple productive machines to sustain.

Powered equipment needs an explicit energy source: initially propose the main
engine supplying a bounded mechanical/hydraulic budget, not a free infinite supply.
Exact hydraulic/electrical simulation can be simplified to one readable power bar.
Manual rigs remain lower-output options with lower machinery support demands.

### Tier7 — Conveying and sorting

Offer short conveyor modules and a size/weight sorter. The sorter routes smaller
fish to batch processing and larger fish to suitable manual/specialist work.
Basic routing/filter controls are normal player features, not a legendary ability.

Conveyors replace specific walking legs that they physically connect. Deckhands
still feed/unload disconnected endpoints, handle output and deal with fish unsuitable
for a selected line. Buffers are finite. A full processor blocks its upstream belt
and eventually the landing station; do not delete excess fish or force random jams
just to create activity. Engineer must service the added mechanisms.

This creates an alternative to Power Lifter's crew-based bulk transport, not a rule
that makes his existing ability invalid. Space, power, workers and reliability differ.

### Tier8 — Machine processing

Offer gutting/filleting equipment with an explicit eligible size/species range and
finite input/output. Keep manual processing available for other catches and for a
different crew/equipment strategy. Do not force every species through an unsuitable
machine or conflate real filleting yield with free money per kg.

Deckhands work feeder/operator/unloader jobs as needed by the chosen machine; which
jobs require continuous attendance must be defined before Engineer automation skills.
High intake can starve output handling, and machinery competes with retrieval for
power and maintenance. Do not silently assume every machine runs unattended.

Add actual new processed-product states/byproducts only if Mo chooses that deeper
economy. An initial machine can perform the existing preparation transformation at
mechanical rates, preserving mass/value rules while we learn the throughput model.
Existing manual Batch Cutter/Bulk Processor remain alternative staffing solutions.

### Tier9 — Fishing-method specialization

Choose between modular automated longline gear and an expanded powered-cage setup;
retain jigging/rod/net paths. This is proposed new equipment, not current deep-line
gear. Longline gameplay needs an explicit fixed-position abstraction approved by Mo.

Give methods different arrival patterns: jigging supplies frequent individual catches,
longlines recover a sequence of hooked catches, nets land bursts, cages require timed
recovery. Do not merely multiply their prices. Different batches and worker demands
should favor different processors, carriers, power allocation and service schedules.

### Tier10 — Integrated machine boat

Allow two modular production routes sharing a constrained supply: e.g. cage/large-fish
manual processing on one route and net/small-fish machine processing on the other.
Offer upgraded generator/hydraulic capacity as a deck-space/fuel tradeoff, not the
mandatory largest version of every station. Power existed sinceTier6; now player
manages several concurrent loads and can choose how much generation to fit.

Optional freezer/packaging branch could support longer voyages if freshness/storage
rules are deliberately redesigned. Current prepared fish stop losing freshness, so
a compulsory ice machine would otherwise have little meaningful purpose. Keep it
optional/unapproved; do not create a useless new resource chore. A refrigeration
decision must cover freeze rate, cold storage and what happens to prepared freshness.

None of these tiers implies a giant factory ship or exact dimensions. First define
station footprints, route clearance and a worthwhile module/crew budget, then size
each hull modestly. Earlier machines can remain useful across later hulls.

## The machine contract that makes the ecosystem work

Before implementing a machine, define and expose:

1. Its eligible input, physical input point and finite queue.
2. Its output point and finite output queue.
3. Normal rate and which actual workers are occupied during which stages.
4. Active/idle power use and behavior when supply is insufficient.
5. Condition lost by productive workload/cycles and required service time.
6. What blocks it, what the engineer repairs and ordinary manual alternatives.

Machines must obey actual cargo identity/mass and current whole-fish overshoot rules.
Oversized or ineligible fish follow an explicit manual route; no infinite rejection
buffer or hidden loss. Normal intelligent routing is not a rarity-gated skill.
The captain can help with ordinary carrying/service and choose modules/duties/power
priorities. These decisions are distinct from manually triggering crew abilities.

Automation should remove a chosen repeated job while shifting the limiting factor.
Avoid artificially adding identical chore bars to every machine: queue, worker,
power and condition limits are enough to test first. More output only earns more
if the rest of the production route can accommodate it.

## What this gives the two Gold Engineers

These are direction examples to revisit AFTER the machine contract is chosen;
neither is a selected card or final skill package. Normal maintenance still starts
below80%, ordinary broken equipment needs full100%repair, with selectedRare5B as
the explicitly chosen halfway-resume exception. Do not sell that baseline as gold.

### Support gold — machine automation/control specialist

A promising new operating-mode ability is enabling **one properly fed machine to
run without its usual continuously assigned operator**, if that machine normally
requires one. Operator duties must be physically automatable; input/output carriers
remain necessary. Extra operating wear/limited safe run makes engineer support a
real cost. Frees a worker to support a different bottleneck, not every job at once.

This only makes sense if the selected machine's normal operator has a meaningful
job and its unattended mode is a genuine additional mechanism. If normal machine
operation is already unattended, discard this idea instead of inventing a fake
operator tax to make the card relevant. Power priorities/routing remain available
normally to all players. Alternative support abilities can follow the actual chosen
machines; do not lock this because it is written here.

### Technical gold — preventive machine-care specialist

Make actual servicing earn a finite reduced-wear allowance on that machine, consumed
by productive workload, or let the engineer spend real work to bank one future
upkeep action. A fixed productive-work/processed-kg budget is worth evaluating
alongside use counts so one giant batch cannot get unlimited protection. No free
global low-wear aura and no automatic condition creation from simply being aboard.

The normal engineer already visits below80. The gold distinction would be doing
extra preventive work earlier to preserve availability while they are busy at other
machines later. How reserve/protection is earned and consumed remains unselected.

## Decisions for Mo, not an implementation queue

- Does the powered handling→sorting→processing→specialized gear→integrated boat
  progression fit the game? All tiers/machines remain proposed.
- First new fishing method candidate: jigging; longlines require a separate design
  decision. No moving-school chase or travel-based trawling assumed.
- How deep should power management be: one visible capacity bar and priorities is
  a reasonable first proposal, rather than detailed circuits and plumbing.
- Cooling is conditional on making preservation a meaningful system; no automatic
  freshness/economy rewrite authorized.
- Decide machinery roles first, then finish GoldEngineer7/8 and shelvedPurple6.
  Existing selected crew remain; do not repeat all earlier card questions.

No gameplay source, boats, saves, builds or installs changed by this document.


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

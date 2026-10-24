# Catchline blueprint — tiers 0 to 5

Status: design authority for the rework, agreed with Mo on 2026-10-23. Where this
file and `docs/GAMEPLAY.md` disagree, this file states the intended direction and
GAMEPLAY records what the current code does until it is migrated. Numbers marked
*provisional* are starting values for the simulator, not promises.

Everything here is scoped to tiers 0–5. Tiers 6+ are deliberately not designed yet.

## 1. The game in one paragraph

Catchline is a labour-chain game with fish as the material. The player starts
doing every job by hand, then delegates one job at a time; every delegation
moves the bottleneck somewhere new. Fish flow through five stages — catch, sort,
table, hold, sell — and each stage is limited by a *different kind* of thing, so
different crews and gear hit different walls. The captain's job is to keep the
chain moving: set a few rules, assign duties, answer events, decide when to
relocate and when to go home. Fishing is the flavour; management is the game.

## 2. Stages and their limiters

| Stage | Done by | Limiter kind | What actually caps it |
|---|---|---|---|
| Catch | fishers (captain early) | supply, attention | ground richness per species drains as you fish; quota; night light; captain strike on "big one" bites; one fisher per rod |
| Sort | deckhand (Sort) | decision | the keep rule; undersize auto-throwback; throughput only matters on net bulk |
| Table | deckhand (Table) | choice | one table, several products; table-minutes are the scarce mid-game resource |
| Hold | — | capacity, composition | kg; what is in it versus contracts |
| Sell | buyers | demand | which buyer wants what; **no price drop for volume** |

Design rule: hauling is a *rate* limit and must only be the wall on bulk (net)
strategies. Fisher baskets are large enough that a full basket is rare outside
nets. If a playtest shows hauling as the bottleneck on a rod boat, fix basket
size or carry speed — do not add haulers.

## 3. Fish

### 3.1 Classes
Existing `CatchTier` maps to the six colours used everywhere in UI:

| Colour | Tier | Bait yield at table | Table behaviour |
|---|---|---|---|
| White | Common | 1 | generic products or pass through |
| Green | BigCommon | 2 | generic products or pass through |
| Blue | Rare | 3 | generic products or pass through |
| Purple | BigRare | — | always becomes its species' special product |
| Gold | Legendary | — | always special product |
| Red | Mythical | — | always special product |

### 3.2 Size rule (enforced, not optional)
A fish in the bottom 25% of its species weight range is **undersize** and is
always thrown back at the sort table. It never reaches the hold. It counts
against nothing. This is the one sorting rule the player does not control.

### 3.3 Value
Price per kg by species, with the existing specimen premium for large
individuals. **Remove market saturation**: selling many of one species never
lowers its price. Prices may drift a few percent per harbour day for flavour only.

Small fish are never worthless: the Bait shop (see §9) buys white/green at a
floor price, and every white/green/blue fish is worth 1/2/3 chum at the table.

## 4. Roles

| Role | Does | Never does |
|---|---|---|
| Captain | strike on rods (T0–T4), keep/throw at T0, sets rules, assigns duties, relocates, answers events, decides return | — |
| Navigator | **fixed slot from T1, cannot be swapped out.** Reads ground richness per species, calls relocation, early-warns events, radio (market and rush contracts at sea) | deck work |
| Fisher | one gear family end to end: baits, deploys, tends, hauls into **their own basket**. Rods, nets, cages, deep lines, jigs | sort, table, carry |
| Deckhand | **Haul · Sort · Table** as primary + secondary duty. Haul moves fish between baskets and the hold | catch gear |
| Engineer (T5) | generator, power allocation, electrical faults | catching, carrying |

"Processor" is not a role: it is a deckhand whose speciality is Table.

Every crew card has one speciality (fisher: a gear family; deckhand: one of the
three duties). Speciality work runs at 100; the rest of the role's work at the
rarity baseline (provisional 50 white, 65 purple, 80 gold).

### 4.1 Deckhand duty model
Each deckhand has a **primary** and a **secondary** duty from {Haul, Sort, Table}.
Primary first; secondary when primary has no work. Changing duties applies after
the current job. Bigger boats need a second sort table and a second processing
table (T5) because fishers outnumber deck capacity — that is intended.

## 5. Boat ladder

Berths: tier N = N hires + navigator + captain. The navigator slot is not a
hire choice; she is always aboard from T1.

| Tier | Hull (saved ID) | Hires | New on this boat | New limit |
|---|---|---|---|---|
| 0 | Rowboat (0) | 0 | 1 rod, basket; captain sorts by tap (keep / throw) | your hands |
| 1 | Rowboat (0) | 1 | navigator joins; sort table at the gunwale; first deckhand (Sort primary, Haul secondary) | one hand: sort versus carry |
| 2 | Skiff (1) | 2 | first fisher; 2 rods; bait bin; lantern → night voyages with jigs | which rods, what bait, day or night |
| 3 | Compact fisher (2) | 3 | first net (fisher sets/tends/hauls; deckhand sorts the pile); hold frozen from here | sort throughput versus rod carrying |
| 4 | Prep fisher (3) | 4 | processing table: chum, products, special products; second net module | table-minutes versus hold kg |
| 5 | Buoy fisher (4) | 5 | engineer, generator, deck lights, cages, deep lines; second sort table; relocation calls | power; bait for lines; two tables to feed |

T5 crew = 5 hires + navigator = 6, matching the current hull's six.

## 6. Gear

| Gear | Fisher side | Deck side | Output |
|---|---|---|---|
| Rod | bait, cast, strike, reel, drop in rod basket. Unmanned rods catch nothing | haul from rod basket to sort | one fish |
| Jig (night, T2) | jig, no bait, fast cycle | haul | squid |
| Net (T3) | set, tend while soaking, haul into net basket | **sort the pile** (undersize and bycatch back), haul keepers | many small fish |
| Cage (T5) | bait, drop, raise when ready | empty basket, sort by size | crab |
| Deep line (T5) | bait with chum, drop; **catches on its own**; fisher raises when ready | empty the line basket | few large fish, purple-heavy |

Existing timings (rod cycle, net 40/60 s soak, deep line 60 s, cage 65 s) stay
as starting values.

## 7. Bait

Bait never stops fishing. Scraps are free and unlimited. Bait decides **what**
bites, never **whether**.

| Bait | Source | Can reach |
|---|---|---|
| Scraps | free | white only |
| Worms | shop | white, green |
| Squid | shop, or jigged at night | white, green, blue; occasional purple, never a large one |
| Chum | made at the table from white/green/blue (1/2/3 each) | purple, gold, red |

Gold and red are chum-only. Deep lines take only chum. Fishers bait their own
gear from the shared bait bin; nobody delivers bait.

## 8. Sort and table rules (the captain's two rules)

**Keep rule** (sort table): undersize is always thrown back (§3.2). The player
toggles classes to throw back, e.g. "no whites". That is the whole rule; no kg
thresholds, no species lists.

**Table orders** (processing table, T4+): a short list of products. Each order is
a count: **1 · 5 · 10 · ∞**. The table works orders top to bottom; when an order
is satisfied (or no eligible input exists) it moves on; with no order left,
common fish pass through untouched to the hold. Purple and above always become
their special product and skip the list. Prepared/fillet forms are removed: a
common fish is either a fish or a product.

Initial products (provisional):

| Product | Input | Time per unit | Buyer |
|---|---|---|---|
| Chum | white 1, green 2, blue 3 | 3.5 s | not sold; feeds lines, cages, rods |
| Fish oil | any white/green | 4.5 s | Cannery |
| Special product | each purple+ species has one (marlin bill, shark tooth, ray skin, roe) | 6 s | Collector; contracts |

Add products only when a buyer or contract needs them.

## 9. Buyers and contracts — the reward axes

Each gear family leads to a species family, a product and a buyer. Reputation
with a buyer unlocks their next contract tier and shop items. This replaces
"bigger fish" as the only reward.

| Buyer | Wants | Reputation unlocks |
|---|---|---|
| Market | any fish, flat price | — |
| Bait shop | white/green fish, squid, at a floor price | bulk bait packs |
| Restaurant | named species, blue+ | squid lights, premium contracts |
| Cannery | kg of fish oil / bulk common | heavy net system |
| Collector | special products | deep-line rigs, cage sets |

Contract types: N of species · N kg of a class · N special products · a night
species. Contracts never ask for processed forms of common fish.

## 10. Stakes — a voyage can lose money

There is no fail state, but there is loss:

- **Running cost** paid at departure: wages per deployed crew (by rarity and
  level), fuel, bait bought, lantern oil at night. Shown on the departure sheet
  as one number: *This trip costs 420*.
- **Lost gear**: a snag can cost a rig; a net left out in a squall is lost. Spare
  rigs are a shop consumable.
- **Lost fish**: deck fish slide overboard in a squall, gulls raid open baskets,
  a seal empties a line.
- **Fines**: the inspector checks undersize and quota; over quota closes that
  ground for three voyages.
- **Reputation**: a failed contract drops that buyer one step.
- **Night** doubles event frequency and adds dark-deck slowness without lights.

Result: a sloppy night trip with a gold crew can end in the red. That is the
challenge the game currently lacks.

## 11. Night voyages (from T2)

Chosen on the chart. Each ground has a night species pool (squid, conger,
dogfish and later night-only species). Jigs need no bait. Lantern (T2) burns oil
bought at Supplies and lights one station; deck lights (T5, power) light the
deck. Without deck light, sorting and hauling run at 70%. Night is for products
and night species, not bigger fish.

## 12. Relocation within a map

A map has 3–5 **grounds** a few boat-lengths apart (shallows, drop-off, reef,
open water). Each has richness per species that drains as you catch and
recovers between voyages. Relocating: all gear in, 30 s move, re-set — one haul
cycle lost. The navigator says why: "Shallows thinning. Drop-off rich in cod."
Before T5 she only reads richness; from T5 she forecasts. The boat never moves
during fishing and never between maps.

Quota is per map per species per voyage; throwbacks are exempt.

## 13. Events

Navigator warns early (her level sets how early). Answers are only five verbs:
tap · reassign · change a rule · spend a consumable · accept. D = day, N = night,
T = minimum tier.

| Stage | Event | Effect → answer |
|---|---|---|
| Catch | School passes (D, T2) | rods and nets 3x for 90 s → have deck ready |
| Catch | Flying fish (D/N, T3) | fish land on deck unsorted → sorter |
| Catch | Jellyfish bloom (D, T3) | nets half jelly → sort table clogs |
| Catch | Seal (D/N, T5) | empties a deep line → raise early or accept |
| Catch | Dolphins (D, T2) | rods dead 60 s, nets fine → move fishers to nets |
| Catch | Snag (D/N, T1) | fisher frees it (20 s) or cuts → spend a rig |
| Catch | Shark takes the hook (D/N, T4) | half fish, special product only |
| Catch | Crossed lines (D, T2) | two rods tangled → fisher untangles |
| Catch | Tide turn (D/N, T3) | species mix flips → change keep rule / bait |
| Catch | Fog (D, T3) | no net tending → yield down |
| Catch | Squall (D/N, T2) | fishing stops 30 s, loose deck fish lost unless stowed |
| Catch | Birds working (D, T2) | relocate opportunity |
| Catch | Big one (D/N, T0) | captain strike, long window, loses rig on miss |
| Catch | Current shift (N, T5) | lines drift → re-drop |
| Sort | Gull raid (D, T1) | open baskets lose fish → tap to shoo, or basket covers |
| Sort | Spilled basket (D/N, T2) | re-sort |
| Sort | Crab pinch (D, T5) | sorter out 30 s |
| Sort | Undersize run (D/N, T3) | half the net is throwbacks |
| Sort | Protected species (D, T3) | two hands to release; ignoring it is remembered |
| Sort | Inspector boat (D, T3) | checks undersize and quota → fine |
| Sort | Rival anchors nearby (D, T4) | richness drains faster → relocate |
| Table | Eel wraps the board (D/N, T4) | needs two hands |
| Table | Dull blade (D/N, T4) | hone 20 s |
| Table | Oversized fish (D/N, T4) | cut in two first |
| Table | Roe found (D/N, T4) | bonus special product |
| Table | Offal pile (D, T4) | gulls, slippery deck → wash |
| Hold | Hatch jam (D/N, T3) | engineer or captain 20 s |
| Hold | Cargo shift (D/N, T3) | re-stow |
| Crew | Hook in hand (D/N, T1) | 60 s out, anyone first-aids |
| Crew | Seasick (D/N, T2) | one person at 50% → reassign |
| Crew | Won't work adjacent (D/N, T3) | two named crew refuse neighbouring stations |
| Crew | Man overboard (D/N, T2) | everything stops, lifebuoy tap |
| Radio | Price spike (D/N, T1) | species X pays more this trip |
| Radio | Rush order (D/N, T2) | contract with a this-voyage deadline |
| Radio | Weather warning (D/N, T2) | return by T or risk a squall |
| Radio | Cannery closed (D, T4) | fish oil unsellable today |
| Power | Breaker trip (D/N, T5) | machines stop → engineer, or allocate less |
| Power | Fuel leak (D/N, T5) | fuel drains → return early |
| Power | Light out (N, T5) | deck dark → engineer |

## 14. Roster and abilities, tiers 1–5

Card structure (Mo, 2026-10-23): **blue = small passive · purple = teamwork ·
gold = signature**. Level comes from kg landed by that crew member. Wages per
voyage scale with rarity and level. Roster should be about twice the berths.

Unlock order is gated by tier so no card is useful before its gear exists.

| Tier | Card | Role · speciality | Blue | Purple | Gold |
|---|---|---|---|---|---|
| 1 | Mira | Navigator (fixed) | richness readout 30 s earlier | crew stow gear 2x faster on a relocation call | **Radio**: price spikes and rush contracts at sea |
| 1 | Noor | Deckhand · Sort | +10% sort | pre-stacks for the hauler on her route (+20% his walk) | **Bucket brigade**: sorts a whole net basket as one job |
| 2 | Dirk | Fisher · Rods | strike window +15% | neighbouring unmanned rods self-hook for 5 s after his bite | **Two rods** |
| 2 | Sam | Deckhand · Haul | carries +1 fish | two haulers on one route both +30% | **Power lifter**: carries any single fish alone |
| 3 | Kofi | Fisher · Nets | sets 20% faster | tends a second fisher's net while his soaks (+15% both) | **Back-to-back**: haul and reset in one job |
| 3 | Ana | Deckhand · Haul | +10% walk | her deliveries arm one half-time sort job | **Clear deck**: clears every loose fish on deck in one sweep |
| 4 | Mats | Deckhand · Table | +10% table | **Offcuts**: every product job yields one chum | **Batch cut**: processes a basket as one job |
| 4 | Lise | Fisher · Jigs (night) | **Lamp eye**: jig cycle +10% | **Shares the light**: the neighbouring station counts as lit at night | **Ink run**: her jig pulls two squid per cycle |
| 5 | Olaf | Engineer | faults 20% rarer | lights also raise night sort speed to 100% | **Overclock**: +50% power 30 s, breaker risk |
| 5 | Pim | Fisher · Cages/Lines | baits 30% faster | his raised line arms a free cage rebait | **Double drop**: baits two lines with one chum |
| 5 | Tove | Deckhand · Sort | +10% sort | crab pinches never take her out | **Grader**: her sorted purple+ fish yield 2 special products |

Reconcile with `docs/CREW-CARDS-DESIGN.md`: Power lifter, Bulk/Batch processor,
Back-to-back netter and the count-based commons are already selected there;
keep their effects, re-slot them into this blue/purple/gold structure.

## 15. Management screen semantics

Four stage cards — Fishing · Hauling · Sorting/Table · To hold — each with one
number (fish/min), a traffic light (Steady / Busy / Backed up) and the queue
drawn as fish icons. One recommendation line and one primary action
(**Assign crew**). No costs per minute, no charts, no efficiency ring. Tap a
stage for its detail page. The rule for the light stays the one in
`docs/MANAGEMENT078.md`.

## 16. Migration from current code

Remove: market saturation; prepared/fillet premium (`Prepared`, 25%/150%);
remaining food fields; legacy engineer condition on rods/nets/cages; fisher
task tickboxes (replaced by speciality + boat gear). Keep: kg hold and overflow
rule; frozen hold from T3; net and deep-line minigames and timers; chum code
(re-pointed at table orders); catch cards and class colours; saved species and
hull IDs (append only). Navigator is a new `CrewRole`; deckhand `DeckhandWork`
becomes primary/secondary over {Haul, Sort, Table}.

## 17. Open decisions

1. Wage numbers per rarity and level.
2. Which special product each purple+ species yields.
3. Night species pools per ground.
4. Whether the inspector fines coins or closes the ground (or both).

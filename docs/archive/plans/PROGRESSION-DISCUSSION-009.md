# Progression discussion 009 — 16 October 2026

Design proposal from Codex 1, not an implementation specification or tuned balance.
Mo's latest numbering in this conversation supersedes older notes for discussion:
0 solo tutorial;1 first deckhand boat;2 two hired crew/two rods;3 three hired crew
and the compact net-fisher model currently finished by Codex2. Saved Hull IDs and
runtime test overrides have NOT changed. TODO and artist handoffs retain older
labels; do not infer a migration or rewrite their scope from this proposal.

## What the early ladder teaches

| Tier | Hired crew, excluding captain | Stations | New experience |
|---|---|---|---|
|0|0|1 rod|Learn cast/strike/carry/stow/return/sell in a short voyage|
|1|1, deckhand only at this stage|1 rod|Delegate bait/carrying while captain keeps fishing|
|2|2, freely mixed|2 rods|Choose fishing output versus handling; captain fills the gap|
|3|3, freely mixed|3 rods +1 small stationary net|Coordinate methods and intermittent handling pressure|

Tier1 role restriction is a staged unlock, not a permanent rule forcing role
quotas on later hulls. First automation needs to arrive early. Recommend starting
near250coins rather than500, with the first short deckhand contract included and
provisions ready. Tune for roughly10–15minutes from a fresh start (prefer earlier
if the manual loop drags), not a mandatory price. If measured NET progress takes
longer, lower the cost or give an explicit tutorial trade-in credit. Historical
49coins/2.63min fixture is not production net-income proof. Boat price alone omits
bait/provisions/hiring and optional upgrades. No16-fish/big-cooler prerequisite
before first automation. Keep early upgrades sparse and avoid selling an upgrade
that costs as much as the first helper boat before the player understands it.

Tutorial should teach the essential labour through a few catches, not withhold
crew until a long grind is finished. Introduce crew/provisions at tier1, fisher
hiring and two-rod decisions at tier2; do not front-load nets/repair/assignment UI.

## Flexible crews should create consequences, not artificial parity

Tier2: two fishers occupy both rods and the captain handles catch. One fisher+
one deckhand lets the captain fish the second rod. Two hands are allowed but
likely overstaffed with only the captain producing fish. Show missing-work and
idle-capacity consequences; do not forbid a mix or invent work to make it optimal.
Captain uses one of the physical rods, never an invisible bonus station.

Tier3: three fishers on three rods leaves captain handling/net work. Two fishers+
one hand is flexible but one hand is not guaranteed to service three busy rods
AND the net. One fisher+two hands trades a rod's output for net/handling capacity.
Three hands remain legal; at this scale it may be a niche or weak choice. No need
to promise that every mix is equally efficient. Show actual workload before
encouraging more hires. Higher output, hold capacity and crew throughput must
be tuned together; a bigger hull should not just amplify backlog punishment.

## Keep two professions; put net handling under deck work

Fishers work their assigned rod. Deckhands carry/stow, prepare gear and set/haul
nets. The captain can do either manually. Net handling is shared deck work, not
a new profession. During soak, no worker stays reserved at the net. At haul,
one worker uses the winch; then catch still needs handling into the hold.

Use a contained landing basket for the net batch, not several instant loose
fish all on the existing25second escape timer. Basket fish remain a backlog and
freshness/capacity issue, not instant secured/sold cargo. A full basket blocks
the next cycle visibly; no silent loss. Rod catches can retain their urgent
individual carrying behaviour. This avoids punishing the player for discovering
a batch-catch system before hiring optimal automation.

TODO's2–5fish(mean3.3)/90second soak/5second haul is a starting test, not tuned.
Its illustrative16gross coins/haul depends on the locality and excludes actual
handling/crew opportunity cost. Balance net return relative to time taken away
from rods/carrying. Favour small local schooling fish; keep squid/rod fishing
useful for valuable specimens. Start with one net and a limited landing basket.
Prototype the useful loop before adding wear. If retained, repair should be
minor clear harbour maintenance, not a new mandatory job/mid-trip chore or random
net destruction. Do not port the much more generous old prototype yield as if it
were this new net design. Returning should recover it or explain forfeiture.

## Task orders before a management simulator

At tier1 the lone hand simply helps. Tier2 can stay automatic; tier3 introduces
three clear preferences per deckhand: Deck first, Net first, Flexible. Preferences
select work queues, not rigid occupations; sensible defaults protect fish about
to be lost. Workers finish or safely hand off tasks before switching. An explicit
player command takes precedence; do not commandeer the captain through an AI list.

Later, assign a desired headcount to a work area, e.g. three processing/carrying,
one net work. Respect physical station capacity: one winch cannot employ three
simultaneous haulers. Extra hands can unload/sort/carry its batch; otherwise show
idle/no available work rather than pretending throughput tripled. Default routing
and priorities must work without requiring player rules to repair bad crew AI.

## Later progression worth prototyping

After tier3, consider specialization rather than a long compulsory ladder:
- Pot/creel boat: baited traps, placement and collection route. Four hires only
  if enough simultaneous work exists. Different trip decisions from stationary nets.
- Purpose-built small trawler: captain steers through schools/manages tow while
  hands haul/handle and fishers work rods when practical. Active captain job;
  a larger net standing still would not be enough of a new tier.
- Larger offshore/processing boat much later: handling, chilling/sorting and trip
  planning can justify more workers. Add a profession only when there is a real
  independent activity/choice, not a new name for another deckhand station.

Do not promise a profession/minigame on every upgrade or solve later content by
only increasing capacity. Next useful prototype is the0→1→2 labour transition;
measure first-helper timing and manual satisfaction, then add the tier3 net/task
pressure. Prices, yields, tier2/3 capacities, wear, later hulls and final station
allocation UI remain proposals needing playtests and Mo's decisions.

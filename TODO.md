# Catchline — next boat and small net

Mo's current scope, 2026-10-16: **3D first; V1 size approved, finished model delivered in ART-022.**
The rowboat is tier 1; the new compact motor fisher is tier 2 in Mo's latest
wording. These display tiers do not renumber saved `Hull` IDs. Earlier zero-based
planning remains history; do not migrate progression from names alone.

## First model / ART-021

- [x] Mo reviewed/approved V1 hull size, helm roof and four-person deck against the rowboat.
- [x] ART-022 finishes the approved silhouette without enlargement: 5.4m hull,
  2.8m beam, compared with the 4.2m/2.4m rowboat; open sides, roof over helm only,
  small rear net. Real hold opening, independent lid/drum/crank and fittings added.
  Source/actual FBX/static access checked; native gameplay integration remains below.
  See [finished 3D handoff](docs/CLI-COMPACT-FISHER-022.md).
- [ ] Codex 1 checks native import axes/materials, camera framing, four crew routes,
  rod access, helm/hold access, net handling and travel/docking clearances before
  selecting this model in gameplay. V1 is a separate asset, not a Skiff replacement.
- [ ] Settle whether this tier carries captain + three hired crew immediately, and
  how flexible roles/coverage warnings are presented. Four-person model capacity
  does not itself change hiring rules or introduce a net-operator role.

## Proposed small-net loop — NOT IMPLEMENTED / values to playtest

Use a **small stationary set net**, not a giant trawl: set it off the stern,
fish with the rods while it soaks, haul it, then carry/stow its catch. No bait is
required. The tradeoffs are time, handling work, shared hold space and **net wear**.
Keeping this first net stationary leaves steering/tow management for a later boat.

- [ ] Start tuning at 2 seconds setting + 90 seconds soaking + 5 seconds hauling,
  plus walking/carrying. One active net; no idle/offline earnings. Pause freezes it.
- [ ] Try **2–5 fish per completed haul**, probabilities 20%/40%/30%/10% (mean3.3).
  Prioritize local small schooling fish, with limited local bycatch; do not make
  this tiny net an easy source of trophy fish. Final per-location tables need tests.
- [ ] Keep bait relevance: rods using squid should remain the route to valuable
  large fish. Net catches must not inherit the captain's paid-bait multiplier.
- [ ] Prototype **100% condition, 12 percentage points wear per completed haul**.
  Eight full hauls leave4%; require at least12% to set again. Show the condition
  and repair cost before departure/setting. Never randomly destroy a net/catch.
- [ ] Try repair at the existing Chandlery: `ceil(16 * damage / 100)` coins to
  restore to100%. Eight hauls cost16 coins to restore96% damage, effectively2/haul.
  No extra currency or separate repair screen. Do not implement these prices yet.
- [ ] Keep it recoverable: no coins/condition means net unavailable with a clear
  repair reason; free unlimited scraps and ordinary rod fishing remain available.
  Net repair is optional, not a departure requirement or a new soft lock.
- [ ] Charge wear once on successful haul; save/load or canceled walks must not
  duplicate catch, refund an already delivered haul, or charge twice. Decide and
  explain returning with a soaking/ready net; recommend recover it before departure,
  with an explicit forfeiture confirmation if leaving early, never silent loss.
- [ ] Capacity preview: show expected catch range and remaining hold space before
  setting. At haul, use existing deck backlog/carrying/freshness rules; no instant
  sale and no silent overflow deletion. Catch age starts when the haul lands.
- [ ] Native tests: empty/full hold, full deck, no deckhand, two fishers/no hand,
  paused soak, save/reload, canceled set/haul, low condition/zero money, departure
  during soak, sale preview/payout equality, and deterministic yield across seeds.

### Starting economics, not a measured balance result

Example harbour table60% herring/40% mackerel at current mean weights/prices:
`0.6*(0.21*17) + 0.4*(0.5*14) = 4.942 coins/fish` before freshness/market effects.
Expected haul `3.3*4.942 = 16.3086` gross coins. Ignoring walking/carrying,97seconds
is about10.09 gross coins/min; subtract2 coins wear reserve per haul for about
8.85 coins/min. These are illustrative proposals, not actual runtime yield.
Native balance must include deckhand throughput, provision/fuel costs, location
depletion, market changes and opportunity cost of the captain's handling time.

The existing `VoyageNet.cs` is much more generous: first catch after4seconds,
then every3–4.5seconds scaled by richness during a60–90second soak, with30% spot
bycatch and no wear. Do not mistake that old prototype for this proposed tiny-net
balance; replace it in a separate scoped systems pass after the model review.

## Keep later boats interesting — suggestions, not approved expansion

- [ ] Explore crab/lobster pots: bait, placement decisions and collection routes.
- [ ] Explore a later purpose-built trawler: steer through schools, manage tow speed
  and load. This is different work, not simply a bigger version of the first net.
- [ ] Decide later activities before escalating hull size. No cabin, industrial
  gantry, cargo-scale hold or new fishing system is required for this V1.

## Gameplay ideas — journal and deep nets

Ideas Mo asked to keep for later design work. Weight capacity and the deep-net
failure rule are now approved direction in docs/GAMEPLAY.md (2026-10-16), not
implemented. Other proposals and all example balance values remain unsettled.

### Fish journal and massive-catch achievements

- [ ] Add a fish journal that records catches by species, including personal size
  records and notable milestones.
- [ ] Explore species-specific achievements or special rewards for massive
  catches. Define what counts as massive separately for each fish type; thresholds
  and repeat rewards are undecided.
- [ ] Consider collection rewards such as journal marks, harbour trophies or boat
  cosmetics, so records have value beyond ordinary sale income. Exact rewards and
  whether any reward is repeatable remain undecided.

### Deep nets

- [x] WEIGHT020 implements approved weight-based storage/net direction: kg capacity upgrades,
  higher value per kg for large specimens, and one final whole fish accepted
  while the hold is below capacity. A failed deep haul loses catch and one use,
  keeping remaining uses; carry reserve deep nets. Current values,5000seed native
  mass/value sample and remaining play-balance limits are in docs/WEIGHT020.md.

- [ ] Explore a costly, limited-use deep net that shifts catch odds toward the
  better fish available in the selected map. It must not introduce fish from
  outside that map's species pool.
- [x] WEIGHT020 starts at100coins per net and3uses, including failed hauls.
  The prior4–5fish/2greatfish hypothesis is superseded by local weight budgets and
  larger-specimen bias; rare species are not guaranteed. Future tuning stays open.
- [ ] Make the net clearly worthwhile after its purchase cost, time and handling
  work. Compare its expected sale value and journal/record value with ordinary
  nets and rods across maps, including depleted grounds and market effects.
- [ ] Work out how skill affects the limited uses, what happens when a haul is
  interrupted or the hold is full, and how much the better-fish odds improve.
  Preserve fair, predictable results; do not promise a positive payout until the
  balance is tested.

## Deferred — modular chum station (Mo, 2026-10-17)

**To do for a larger tier 4 or 5 boat; not for implementation now.** Exact
unlock tier remains undecided. This is a future production link between catches,
crew and rod fishing, rather than another shop-bought bait upgrade.

- [ ] Fit a chum-making station into a modular boat slot. It trades equipment
  space and crew time for top-tier bait; larger boats must have room/personnel
  to support it. Exact footprint and slot compatibility remain to be designed.
- [ ] Let the player assign a specific hand to chum production instead of net
  work or collecting fishermen's catches, using a simple RimWorld-like work order.
- [ ] Support a bounded order such as **make 10 chum**, then stop. Avoid requiring
  a tap for every portion. Whether a later repeat/maintain-stock option is useful
  remains open; it is not required for this first version.
- [ ] Require caught fish as input, consuming eligible fish to produce chum.
  Fish-to-chum yield and processing time are undecided.
- [ ] Let the player choose an input limit by fish value or weight: for example,
  **only fish worth under 10 coins** or **only fish under 1 kg**. These are example
  player settings, not fixed balance values. Define the value basis and whether
  both filters can be combined before implementation; protect ineligible fish.
- [ ] Chum is the top-tier bait for attracting the biggest fish. It cannot be
  purchased: earn it from the voyage's catch and processing work each run.
  Exact attraction/size effects and consumption per cast remain untuned.
- [ ] Chum spoils and does not carry over into the next voyage. Exact spoil timing
  within a voyage remains open; do not silently choose a timer now.
- [ ] Keep the first interaction compact: assign worker, set quantity, choose fish
  limit, see progress and why production is waiting. Define input pickup/storage,
  rod bait selection and worker behaviour after completion before building.

No current boat, crew role, bait, save or economy change is authorized by this
backlog entry. Revisit alongside tier 4/5 modular-boat design.

## Tier 4 prep/chum station — current direction (2026-10-17)

See [BOAT032 design and model comparison](docs/TIER4-BLOCKOUT032.md). This refines
and supersedes the earlier tier4/5 chum-only station proposal above. Both rough
model variants are rendered and ready for Mo's review; no gameplay system is implemented.

- [ ] One dual-purpose table, up to two assigned ordinary deckhands, plus optional
  captain help through a quick green-zone head-cutting minigame.
- [ ] Drag job priorities; maintain10chum in stock, then prepare eligible fish;
  replenish chum when consumed if suitable input fish exists. Fish input limits
  by value/weight and preparation species/minimum-weight selection remain part
  of the design. Chum remains earned per voyage and unpurchasable.
- [ ] Local flow: raw front buckets -> table -> prepared freezer storage directly
  behind each hand. Minimal depositing travel and only representative visible fill.
- [ ] Prepared fish NEVER spoils. Untreated fish in ordinary front buckets still
  spoils. Upgrade front buckets to ice coolers to protect untreated fish as well.
- [ ] Aim for quick processing alongside catching; fuel limits optional waiting
  at voyage end. Approximately25%prepared sale premium remains to be tuned.
- [ ] Review compact larger hull before production modelling: initial6.2x3.1m
  candidate was too small for Mo; current comparison6.8x3.5m against actual
  tier3 5.4x2.8m, identical crew scale. Final size/crew cap not approved yet.

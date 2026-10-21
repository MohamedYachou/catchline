# Catchline — next boat and small net

## Active gameplay — DEEP104, 21 October 2026

Mo's latest choices and source/check details: [DEEP104](docs/DEEP104.md). Read latest `comms.md` before pickup.

- [x] A–C: saved preferences and deep-line core, bait/deploy/60s/automatic landing/backpressure.
- [x] D: fisher-operated nets, independent hand basket collection, no manual maintenance/Engineer requirement; paid legacy Engineers preserved inactive. Six hired berths plus captain.
- [x] E: Management third Crew page, independent task/bait tickboxes, deckhand hauling/basket/table duties and existing station chum controls.
- [x] F: shared four-method forecasts, local deep class distribution, finite worker time, actual chum/preparation work and downstream accounting.
- [x] D2/E2: two standard deep rigs plus optional3500coin third; actual third access/geometry/soaks/bait/landing/save checked. Existing Tier5 table produces white1/green2/blue3 chum; purple+protected.
- [x] G isolated broad regression: final expanded source passed both layouts, all pipelines/saves/UI controls,60000chum-baited deep rolls and older regression suites.
- [x] G native final review:46actual frames, standard/upgraded/net layouts, desktop/landscape, Crew/chum/input, cloned Real load/departure/return/save; actual save unchanged.
- [x] H final Test/Real installed; all five launcher modes preserved; installed native smokes passed and real save unchanged. Receipt: docs/screens/deep104/installed-build.json.
- [ ] GitHub commit/push verification — in progress.

Deep lines require self-made chum. Deep catches: one fish per rod, with5%white/5%green/10%blue/75%purple/3%gold/2%red where local classes exist; missing classes redistribute locally. No nonlocal species. Third rig sits between cage and normal rod, hidden with the entire deep module in side-net layout. Chum uses existing timing/stock targets/voyage expiry; table and150%Tier5preparation preserved. Astra remains parked.

## Parked research / finished art — TIER5-103, 20 October 2026

- [ ] **Return to Astra: Tier5 deep-line balance and 30 crew-card proposals.** Research is already finished; do not restart it. Read [Astra research](docs/TIER5-102/ASTRA-RESEARCH.md), then answer the [three preliminary questions](docs/TIER5-102/ASTRA-QUESTIONS.md) and give the balance/card phase its greenlight. Questions: catch3/upgraded5 per whole module or per physical rig; bought/own-fish bait versus required onboard supply; self-sustaining good crew versus essential full-time captain. Proposed roster:15Fishers+15Deckhands, each7blue/4purple/4gold. Six hired berths preferred; no Tier5Engineer. Fishers work rods/nets/cages/deep lines, hands haul/process. Full card proposals and simulations **have not started**. Resume existing Astra child `/root/astra_crew_research` if available, or give a new session these saved files plus latest canonical crew decisions and comms. No separate chat URL was returned by the delegation interface.
- [ ] **Later gameplay/UI integration:** new deep lines, fisher net operation, remove legacy manual-gear Engineer requirement, and Management third page for per-crew method/bait/duty preferences. Keep gameplay/forecast numbers shared using [integration handoff](docs/CREW-MANAGEMENT-INTEGRATION.md). Model approval does not approve unresolved catch/bait/card numbers.
- **3D priority now:** Mo approved Sol's two-tall-rod early preview. Production source and full-boat/separate-rig FBXs are finished and export/reimport verified; see [final art handoff](Art/Models/Tier5DeepLines103/REPORT.md). Runtime integration remains pending; the old playable model is still active. The approved preview remains [here](Art/Models/Tier5DeepLines102/REPORT.md). See [brief](docs/TIER5-102/BRIEF.md) and [lead review](docs/TIER5-102/REVIEW.md). Always fixed2rods+2cages+rear net; optional2rods+deep lines OR side net.

## Current status / future crew pickup — CREW096, 18 October 2026

Tier 5, the actual processing pipeline, accepted Management tabs and all five
Real/Test launchers are delivered; see [DASH087](docs/DASH087.md) and
[DASH092](docs/DASH092.md). The older compact-fisher/net checklist below is
historical and must not restart superseded work. Read current comms first.

Next crew implementation, when Mo requests it, follows
[CREW-MANAGEMENT-INTEGRATION.md](docs/CREW-MANAGEMENT-INTEGRATION.md) and latest
[canonical crew decisions](docs/CREW-CARDS-DESIGN.md). Cards are not implemented.
Shared gameplay/forecast effects, processing batches, per-fish telemetry, effect
cache invalidation, hauling relearning, card payroll and electrical-only upkeep
are explicit integration work, not presumed automatic support. Do not invent
unselected levels/wages/stacking or future machine tiers.

## Historical compact-fisher checklist

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


## Complete fish model + UI portrait roster — FISH043, Mo17October2026

Mo prefers our existing authored fish style, rejects Gemini fish models, and likes the new glow/cards. Every fish gets an authored3D model and a transparent UI portrait rendered from that SAME model. Preserve IDs0–9, and preserve interimIDs10–15.25total includes the24listed fish plus supplied gold-tip shark. Big green/purple threshold remains >=75%of that species maximum weight. Existing10deliveries were verified against their authored sources; next pass removes ivory eye rims and corrects the10-point bass spine to the exact brief. The3D/UI checks mean exported-source/FBX/matching-portrait verification; native/game checks and Mo play acceptance are separate.

| Fish | Saved ID | Presentation | Model/portrait requirements |3D pass|UI pass|Native/game verified|
|---|---|---|---|---|---|---|
|Herring|0|Common / green big|0.26m silver-steel body, fork tail, black bead eye|[x]|[x]|[ ]|
|Mackerel|1|Common / green big|0.34m teal back,7navy dorsal stripes,2dorsal fins|[x]|[x]|[ ]|
|Pollock|2|Common / green big|0.48m kelp green,3dorsals,shallow fork|[x]|[x]|[ ]|
|Sea bass|3|Rare / purple big|0.50m hull-blue/steel,10-point spiny dorsal|[x]|[x]|[ ]|
|Conger eel|4|Rare / purple big|0.80m sinusoidal navy body,continuous dorsal ribbon|[x]|[x]|[ ]|
|Plaice|5|Common / green big|0.36m flat wood/rope body,orange spots,fan tail,both eyes upper side|[x]|[x]|[ ]|
|Cod|6|Common / green big|0.70m olive heavy body,3dorsals,fan tail,one chin barbel|[x]|[x]|[ ]|
|Whiting|7|Common / green big|0.38m steel/ivory,3dorsals|[x]|[x]|[ ]|
|Red mullet|8|Common / green big|0.34m coral-orange,twin ivory barbels,gold lateral line|[x]|[x]|[ ]|
|Turbot|9|Rare / purple big|0.58m wide diamond,stone spots,fan tail|[x]|[x]|[ ]|
|Crown pufferfish|10|Rare blue|Rope/ivory inflated body,conical spines,wood spots,fan tail,black bead eyes; light jackpot|[x]|[x]|[ ]|
|Spotted eagle ray|11|Giant rare purple|Wide navy/blue diamond,ivory ocelli rings,snout,whip tail|[x]|[x]|[ ]|
|Sun-gilded reef shark|12|Legendary gold|Bronze/gold dorsal,ivory belly,5gill slits,swept fins,black shark eyes|[x]|[x]|[ ]|
|Gold-tip shark (supplied extra)|13|Legendary gold|Retain supplied shark,coherent authored bronze/gold-tipped model|[x]|[x]|[ ]|
|Scarred great white shark|14|Mythic red|Heavy slate-grey body,countershaded ivory belly,serrated jaw,scars,black eyes|[x]|[x]|[ ]|
|Abyssal killer whale / orca|15|Mythic red|Jet-black/ivory,tall dorsal,paddle pectorals,horizontal flukes,white patch BEHIND normal black eye|[x]|[x]|[ ]|
|Blue-spotted stingray|16|Rare blue|Smooth rope/wood disc,bright teal/blue spot domes,whip tail,top-mounted eyes|[x]|[x]|[ ]|
|Flying fish|17|Rare blue|Blue/silver torpedo,oversized swept teal/silver pectoral wings|[x]|[x]|[ ]|
|Lionfish|18|Rare blue|Orange/ivory banding,fanned dorsal spines,splayed pectoral plumes|[x]|[x]|[ ]|
|Giant devil manta|19|Giant rare purple|Rubber/navy wings,white shoulder patches,forward cephalic horns,lateral black eyes|[x]|[x]|[ ]|
|Atlantic swordfish|20|Giant rare purple|Muscular blue/silver body,long flattened steel bill,tall crescent dorsal|[x]|[x]|[ ]|
|Ocean sunfish / mola mola|21|Giant rare purple|Steel/silver compressed disc,tall dorsal/anal fins,scalloped clavus|[x]|[x]|[ ]|
|Scalloped hammerhead|22|Legendary gold|Wet-stone/steel,T-shaped cephalofoil,eyes at outer tips,tall falcate dorsal|[x]|[x]|[ ]|
|Pelagic thresher shark|23|Legendary gold|Blue/silver shark,upper caudal scythe as long as body|[x]|[x]|[ ]|
|Giant Architeuthis squid|24|Mythic red|Orange/crimson torpedo mantle,arrow fins,8arms+2long feeding clubs,black abyssal eyes|[x]|[x]|[ ]|

- [ ] Audit and deliver ALL25entries; no missing flying fish/lionfish/sunfish/squid or supplied extra shark.
- [ ] Use canonical named palette, coherent real mesh silhouettes, natural black eyes and no Gemini illustration/model substitutions.
- [ ] Verify FBX geometry/materials/scale/finite vertices, alpha margins, matching portraits, data IDs/save/log/market/catch pools and native six-card/HUD integration.
- [ ] Keep new species balance provisional and glows/cards independent of arbitrary sale prices.

## Signature Big Common expansion — FISH050, Mo18October2026

Mo approves four visually distinct additions alongside existing large common specimens.
Each new species stays green/Big Common at every weight; IDs25–28append without renumbering.

| Fish | Saved ID | Recognition cues |3D source/FBX|Matching2D portrait|Native/game verified|
|---|---|---|---|---|---|
|Yellowfin tuna|25|Navy/silver torpedo, yellow sickle fins/finlets, crescent tail|[x]|[x]|[x]|
|Barracuda|26|Long narrow body, projecting toothed jaw, separated dorsals|[x]|[x]|[x]|
|Mahi-mahi|27|Square forehead, long sail, teal/gold body, blue spots|[x]|[x]|[x]|
|Monkfish|28|Broad mouth/head, teeth, raised eyes/lure, tapering tail|[x]|[x]|[x]|

Source/export/alpha/hash checks and model contact-sheet review passed. Runtime
checks and the verified Tier4Test installation passed (docs/FISH050.md); no new player acceptance is
claimed for the older25entries by this checklist.

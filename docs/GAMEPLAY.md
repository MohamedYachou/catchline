# Catchline: gameplay design

Single source of truth for how the game plays. Numbers are starting values for tuning, not promises.

**Build priority, confirmed by Mo 2026-10-15:** the core loop works. Finish the
small playable slice's visual and interaction quality before expanding systems.
Closely match the goal renders, with fishing as the reference standard. Every
later mechanic ships using that finished visual language from its first pass.
See PRODUCT.md, DESIGN.md and docs/plans/PLAYABILITY-PLAN.md.

## Current tier3/net progression — NET023,16October2026

Tier3 Compact fisher now has100kg hold,150kg with the existing big-cooler upgrade.
Both nets have a10kg hard capacity; Heavy net system costs5000coins and raises both
to15kg. Normal nets favour many small fish; deep nets fewer larger local specimens.
Tier3 upgrade prices scale to1500–3500coins for ordinary equipment. Depletion is
weight-based and market saturation softer on tier3. Real progression can buy the
Compact fisher from an owned skiff for4000coins. See [NET023.md](NET023.md) for
pricing, measured native distributions, save compatibility and launcher separation.
This supersedes WEIGHT020's24/36kg hold and unequal net budgets. Starter prices
and saved owned upgrades are preserved.

## Current crew rules — CREW026, 2026-10-16

Crew remain temporary contracts: hands last2 voyages, experienced crew3 and
veterans5, then leave. The player pays the existing grade/role fee each time they
hire. Every hull's Crew Office keeps enough candidates of both roles to fill all
its berths, even after hiring one; board rolls, hull changes and old-save loads
also restore those choices. Players can fill all three tier3 berths with
fishermen, deckhands or any mix in both Real and Test.

The Test shortcut starts at a tier3 harbour with no hired crew and1000 isolated
coins, opening Crew Office so any three can be chosen. `-deep-net-trial` remains a
separate opt-in at-sea test. Real continues to load and save the player's progress.
Full crew does not remove the captain's interactive work. The empty-roster Test
setup lets players hire their own mix using normal contract fees. See
[CREW026.md](CREW026.md).

## Current fuel/preparation rules — FUEL021,16October2026

Food is inactive on early boats. Crew works at the former70%pace as its normal
baseline. Powered boats carry10minutes of fuel,20with the extra tank (the old lunch
upgrade ID). Fuel burns with voyage time, costs1coin/missing minute to refill and
forces a return at10%. Docks do not refill it automatically; rowboats use oars.
Set sail opens a polished departure manifest with quick bait/fuel purchases before
explicit Let's go. See [FUEL021.md](FUEL021.md). These rules supersede older food and
round-trip fuel descriptions below. A later cook/food bonus remains future work.

## Approved weight-capacity direction — 2026-10-16

Implemented in WEIGHT020 after Mo's approval. Current capacities, pricing, net
uses, migration and evidence are in [WEIGHT020.md](WEIGHT020.md). Earlier numbers
elsewhere in this document are historical starting targets where they conflict.

- Boat storage and its capacity upgrades use kilograms instead of fish slots.
  Ten kilograms was an example, not a required starting capacity. Tune capacities
  to voyage length and crew throughput rather than relabelling existing counts.
- Large specimens should earn more for the same total weight than small fish.
  WEIGHT020 implements a capped species-relative premium from1x to1.5x; current
  rates are first-pass tuning for playtesting, not permanent balance promises.
- If stored weight is below capacity, accept one more whole fish regardless of
  its weight. That fish may exceed capacity, then storage is full. Apply this
  per fish, including concurrent crew deliveries and net unloading, never to an
  entire net batch. Do not silently delete remaining basket fish.
- Balance net yields primarily around catch weight, while preserving individual
  fish, local species pools and specimen records. Deep nets are costly limited-use
  equipment; reserve deep nets remain part of preparation.
- A failed deep-net haul loses that haul's catch and consumes one use, preserving
  all remaining uses. It does not destroy the entire remaining deep net. When its
  last use is consumed, another net is needed. WEIGHT020 starts at100coins/3uses,
  30ssoak and roughly twice shallow target mass, with larger local specimens.
  Worker recovery is80%safe; failure spends one use and loses that haul only.

Saved fish weights and purchased upgrades are preserved; storage HUD/shop wording,
fullness, sale preview/payout and simultaneous deliveries are verified in isolated
native checks. Conditions, rank progression and journal expansion remain
design proposals; these decisions do not approve every pasted expansion detail.

## Current boat progression steering — 2026-10-16

Mo's latest direction uses zero-based numbering: **Boat 0** is a solo tutorial
boat; **Boat 1** introduces hired crew, probably one or two; **Boat 2** has three
hired crew, with net fishing conditional on compelling later boat additions.
The captain is additional to hired crew. Exact Boat 1 capacity and later mechanics
are not finalized. Flexible role composition and uncovered-work warnings remain
the prior intent. CREW026 guarantees role availability without changing the
existing crew cap, fees or expiring contracts; future boat-cap changes still
follow this direction. The
big-fish-fight/fish-finder proposal was rejected.

This is production direction; its boat ladder remains unfinalized. CREW026 keeps
role choices guaranteed without changing those hull-capacity decisions or the
existing temporary contracts.
See [CLI-SKIFF-DIRECTION-020.md](CLI-SKIFF-DIRECTION-020.md). ART-020 authoring remains
paused after baseline inspection; no revised Skiff model has been delivered.

## Current urgent playtest slice — 2026-10-15

Mo's 2026-10-16 direction supersedes the one-candidate-per-role testing override:
enough role contracts to fill the boat now apply to both Real and Test. Contract
durations and expiry remain unchanged. See
[PLAYTEST-OVERRIDES.md](PLAYTEST-OVERRIDES.md) and [CREW026.md](CREW026.md).

Free unlimited scraps automatically replace exhausted paid bait and catch only
small herring/mackerel. Returning to port preserves/saves the haul. The captain
presses **Sell haul +N coins**, with a preview matching market impact and contract
rewards, before the next departure. Haul value and oldest-fish freshness are shown
while fishing: 60 seconds at full value, then 7% loss/min down to 60%, unless iced.
Harbour storage holds value until sale. With a deckhand the captain stays in
fishing mode after a catch and can **Throw again** or **Leave**.

## Pillars

1. **Automation is the game, fishing is the accent.** You start doing every job by hand and slowly build a boat that runs itself, but it never becomes cosy.
2. **Slow, not frantic.** Think Factorio and Satisfactory, not Overcooked. You are rate-limited: by hand you are at best as fast as yourself. Mistakes cost time (a fish gets off, bait is lost), never a game over.
3. **Your hands are the scarcest resource.** Every automation frees your hands from one job and the game hands them a new, bigger one. Events and crew gaps keep pulling you back to the real fishing.
4. **People management never stops.** Crew contracts expire and need replacing,
   but both worker roles stay available to hire. Crew assignment and the captain's
   own active tasks keep the player engaged without random role scarcity.
5. **Fully active.** No idle income. A daily login reward is fine.

## The voyage loop

1. **Harbour:** sell the catch, take contracts, hire crew, buy provisions and bait, buy upgrades.
2. **Map:** pick a fishing spot. Spots differ in species, distance and how depleted they are.
3. **Sail out:** a short animation. The boat view stays fixed; only the surroundings change (harbour quay, open sea, kelp, rocks, deep water, later islands and tropical shallows).
4. **Fish:** until the storage is full, provisions run out or you choose to go home. There is **no voyage timer**: storage size and provisions decide how long you stay.
5. **Sail home** and repeat.

**The voyage is the unit of time** for crew and harbour contracts, spot recovery and market recovery. Day and night can be purely visual inside a voyage.

Target voyage lengths:

| Boat | Cheap crew | Experienced crew |
|---|---|---|
| Rowboat (tier 1-2) | 4-7 min | 3-5 min |
| Skiff (tier 3-4) | 10-15 min | 7-10 min |
| Day boat (tier 5+) | about 20 min | 10-15 min |

Small boats go home often, big boats stay out longer.

## Tier ladder (location 1: the fish harbour)

| Tier | Boat | Runs by itself | What your hands do |
|---|---|---|---|
| 1 | Rowboat | nothing | One rod: bait, cast, watch the bobber, strike on time, pick the fish up, carry it to the cooler |
| 2 | Rowboat | Deckhand baits hooks and carries fish to the cooler | Run 2 rods (rod holder). You are still the only one who strikes on time |
| 3 | Skiff | Fisherman works the rods (worse than a perfect you) | First small net: set it and haul it with a hand winch |
| 4 | Skiff | Net winch; deckhands pick fish out of the net | Sort table (species and size, undersize and bycatch go back), ice the hold |
| 5 | Day boat | Sorting chute, conveyors | Layout and repairs; fish finder to chase schools |
| 6+ | Bigger | Gutting/fillet station, freezer hold, trawl | Processing chains and contracts |

Every tier creates its own bottleneck. Example: the tier 3 fisherman lands fish faster than one deckhand can carry them, so fish pile up on deck until you hire or automate.

### What keeps you close to the fishing

- **Captain's work remains active.** Crew automate their assigned jobs, but a full
  roster does not remove the captain's interactive responsibilities.
- **Sickness and injury.** Seasickness in storms, a hook or pinch injury mid-work, a hangover after a port night. A crew member is out for part of a voyage and you cover.
- **Things break, and you are always needed.** A maintenance crew member fixes things alone, slowly; with you helping it goes fast.
  - Electrical fault: the deck goes dark and the machines stop. Fuse and wiring minigames in the engine room.
  - Leak: pump the bilge while the mechanic patches.
  - Net snagged on a rock: cut it (lose the net) or dive to free it.
  - Rope in the propeller: dive.
  - Storm: secure the cargo, or a rogue wave takes crates.
  - Engine fire: extinguisher minigame.
  - Ice on deck (North Pole): chip it off.

  An event never ends a run; it costs time.
- **Expeditions: the captain fishes for real.**
  - Dinghy runs: the big boat drops you in a rowboat, because shy exotic fish avoid engines. Tier 1 rod play with endgame gear.
  - Big game chair: marlin, tuna, shark. A long tension fight, and the base for the weigh-off.
  - Scuba: spearfishing, lobsters by hand, pearls, wreck salvage.
  - Submarine (late): deep-sea species.
  - Night fishing for squid under lights.
  - One legend fish per location: a multi-step hunt with clues, bait and weather.

## Crew

- **Temporary contracts.** Pay the listed fee at the Crew Office; crew leave after their grade-based contract ends. Both roles remain available, and each hire is replaced by a new candidate.
- **Three grades:**

| Grade | Speed | Contract | Hire fee | Where |
|---|---|---|---|---|
| Hand | 1.0x | 2 voyages | base | Usually on the board |
| Experienced | 1.5x, +1 trait | 3 voyages | 2x base | Often on the board |
| Veteran | 2.0x, +2 traits, also raises catch quality | 5 voyages | 5x base | Rare |

Fishermen cost twice the same-grade deckhand fee. The board always offers enough
of both roles to fill every berth on the current hull, including tier3's three
fishermen, three deckhands or any mix. Hiring a candidate removes that individual
and replenishes the role; candidate names/grades can change, role availability
does not. This applies in both Real and Test.

- **Hands must feel fine, not bad.** No penalty systems that only hit cheap crew. Every gap between grades is a bonus, never a punishment.
- **Prestige:** crew carry-over between locations is not decided yet; contracts still expire within a location.

### Why experienced crew are worth it (cargo-capped voyages)

Since there is no idle income, **coins per real minute** still matters. Experienced
crew cost twice a hand's fee for1.5x speed and3 voyages; veterans cost5x for2x
speed,5 voyages, extra traits and higher catch quality. The premium is paid per
contract, so it only pays where the worker is a bottleneck.

## Provisions, fuel and the cook

- **Food** drains per crew member per minute. Out of food: everyone works at 70% until home. It never stops the boat.
- **Fuel** drains while sailing (distance to the spot and back). Rowboats are rowed: no fuel, but rowing takes time.
- **Cook** (from the day boat): a normal cook has no downside. A good cook uses less food and gives a morale bonus (+10% work speed). Food poisoning comes only from the cheapest provisions or a rare event, never from a normal cook.
- **Comfort:** bunks, galley and heating raise morale, which raises productivity on long voyages.

## Fishing spots, market and contracts

- **Spots deplete:** every catch lowers a spot's richness (bites come slower). Every voyage, all spots recover a bit. Seasons and migration change a spot's species over time.
- **The market reacts:** each fish sold lowers that species' price a little, and prices recover over a few voyages. Dumping one species is punished; variety pays.
- **Harbour contracts:** a board with 3 offers ("Deliver 8 mackerel within 2 voyages, reward 90"). Take up to 2. A missed deadline means the contract is gone and a new one appears. Contracts are the main pull toward specific spots and species.
- **Rivals:** AI captains on the harbour scoreboard. They also take contracts from the board, so waiting can cost you the good one. A weekly weigh-off ranks you against them.
- **Fish log:** an encyclopedia of every species, size record and location. Collection drives exploration.

## What money buys

- **Coins (earned by playing):** ship upgrades that add **features**, never a bare stat bump. Examples:
  - a cooler, then an ice box (fish keep full value)
  - storage size
  - a rod holder (second rod)
  - net winch speed
  - a fuel-efficient engine
  - bunks (comfort)
  - a galley
  - a fish finder

  Coins also pay crew contracts, provisions, bait and hull licences.
- **Gems (premium, also earned slowly):** cards and chests for **gear**: rods, lines, bait types, nets and tools, with small percentage improvements and visual variety. Also cosmetics, ship pets (dog: crew level faster; cat: scares off thieving gulls and gives +10% income), a season pass and remove-ads.
- **Never sold for premium currency:** crew contracts or hull progress.

## Hull progress

You never buy a ship. Each hull has a **refit licence**: a skill or throughput goal plus a fee. Example rowboat → skiff: fill the big cooler (16 fish) in one voyage, then pay 1,500. The boat is refitted into the next hull model. Run 1 caps at hull 3.

## Locations and prestige

1. **Location 1: fish harbour** (rod → nets, tiers by species: herring, mackerel, pollock, sea bass, cod...).
2. **Location 2: Crab Coast** (pots, tiers by crab species).
3. Later: Tropical Islands, Miami, North Pole.

Unlocking a location's whole map enables prestige: sell the company and start at the next location. Each reset costs more and adds a tier. Rewards: head starts, your veteran on the new board, cautious multipliers, trophies and rank. Free roam back to old locations.

## Build 1: tier 1-2 vertical slice (current)

Rowboat 3x2, the captain, one rod, a cooler. The camera stays on the boat.

**Interaction model: one tap per action.** Speech bubbles float above whatever needs you; there is no walking around by hand.

**First-voyage pass (2026-10-15):** start with an optional goal of three fish
safely stowed. Hints follow the real state (cast, wait, strike, carry, return)
and can be disabled in Settings. For the first three landed fish, including
saved fish-log progress, bite waits are clamped to 4–6 seconds and the strike
window is at least 1.5 seconds. Normal timings resume afterward. Early strikes
still lose bait. There is no forced return at the three-fish goal.

Catches show their supplied portrait, weight, approximate current sale value
and new-species/record feedback. Stowing shows +1; returning shows sale coins.
The market recommends the next useful upgrade and links to the Chandlery.
The big cooler now costs **60 coins**, carrying 16 instead of 10 fish, so a full
first trip can fund storage and replacement bait. Rod holder and later prices
remain as listed in GameData. Existing owners and saves retain their upgrades.

- **Rod cycle:**
  1. Tap the **Fish** bubble above a rod. The captain walks there, baits the hook (1.2 s; skipped when the deckhand already baited it) and casts by himself.
  2. The **strike minigame** opens: a close-up of the bobber with a fish circling closer. Fish shadows also swim in the water around the boat.
  3. Wait 6-14 s through 1-3 nibbles (the bobber twitches and the fish darts in).
  4. When the bobber goes fully under, **tap anywhere once** inside the bite window (0.9 s). Tapping on a nibble spooks the fish, and missing the window lets it get away; both cost the bait.
  5. Reel (1-2.5 s by weight). The captain tosses the fish onto the deck next to him.
  6. **Solo:** tap the fish's **Carry** bubble and the captain takes it to the cooler. **With a deckhand (tier 2+):** they fetch it and bait the hook; stay in fishing mode and choose Throw again or Leave.

  A fish left on deck flops back overboard after 25 s. A rod nobody is standing at shows a **Watch** bubble (and **!** on a bite): tap it to go there.
- **Cooler:** 10 fish. Without the ice box, fish lose value the longer they sit (down to 60%).
- **Food:** bought at Supplies before sailing, in minutes. Out of food means 70% speed.
- **Bait:** worms (1 per hook) and squid (draws bigger fish and bigger species; used first when you have it).
- **Rod holder:** a second rod. A rod nobody is holding hooks a biting fish by itself 35% of the time; otherwise the fish usually keeps nibbling, and sometimes steals the bait.
- **Deckhand (tier 2):** baits hooks and carries fish to the cooler.

### Gull Harbour, the first world

The harbour is a quay with five shops. Tap a building's bubble to open it:

| Shop | What it does |
|---|---|
| Fish Market | Your last sale and today's prices (the market reacts to what you sell). Start a new game |
| Harbour Master | The sea chart (pick a sea, buy charts for new seas) and the contract board (3 offers) |
| Crew Office | Deckhand and fisherman contracts. Both roles remain available after hiring; choose any mix up to the hull's crew cap. |
| Chandlery | Rod holder, big cooler (16 fish), ice box, fibreglass rods (1.15 s strike window, faster reel), carbon rods (1.4 s, self-hook 45%), and the skiff refit goal |
| Supplies | Worms, squid, food, lunch tin |

Five seas, each with its own look and fish. Stocks drop as you fish a sea and recover every voyage.

| Sea | Chart | Row | Fish |
|---|---|---|---|
| Harbour mouth | free | 5 s | herring, mackerel |
| Kelp bank | free | 9 s | mackerel, pollock, some herring and sea bass |
| Sandbar | 120 | 11 s | plaice, mackerel, sea bass |
| Rocky point | 220 | 14 s | pollock, sea bass, mackerel, conger |
| Deep channel | 500 | 20 s | cod, conger, pollock (slow bites, bring food) |

Progress saves in the harbour (after selling and after every purchase). A voyage in progress is not saved.

Bot balance run (30 voyages):
- Sandbar chart at about 30 min
- Rocky point at about 50 min
- all gear by about 90 min
- Deep channel at about 100 min
- skiff money at about 2.5-3 hours

Earnings climb from about 25 to 40 coins per minute as seas unlock.

- **Skiff refit:** bring home 16 fish in one voyage, then pay 1,500 coins at the Chandlery. This survives saving and loading; older saves remain rowboats.

## Build 2: skiff foundation (2026-10-15)

The refit replaces the boat with the supplied skiff model and changes the walkable deck from 3×2 to 5×3. The console, hold and winch block walking; crew route around them. The skiff has three rod sockets, a 40-fish hold and an outboard that halves travel times. Crew caps are currently two on the rowboat and three on the skiff, plus the captain.

Supplies sells 10 fuel for 10 coins. A round trip consumes `ceil(spot.RowSeconds / 5)` fuel, reserved at launch, including the return. The shipyard includes the first 10 fuel in the refit price. Food capacity grows fourfold on the skiff (24 minutes, or 48 with the lunch tin), still shared by everyone aboard. The ice-box upgrade continues to preserve fish in the hold.

The rowboat, skiff and compact fisher always offer fisherman and deckhand contracts, even after hiring a worker of that role. Fishermen occupy one rod each, bait/cast autonomously, and strike 80%/85%/90% of bites by grade. Fishermen cost twice a deckhand at the same grade. They leave landed fish for deckhands. Up to three hires can be any role mix; workers leave when their 2/3/5-voyage contracts expire.

**Gill net:** tap Set net with the captain's hands free. The captain walks to the winch and sets it; it soaks for 60–90 seconds while rods keep fishing. Floats bob and the catch count rises. Tap Haul net when ready: the captain cranks for five working seconds, dropping fish onto the deck for carrying. Nets mainly catch herring/mackerel with local bycatch. Fish on deck still flop away after 25 seconds, making transport capacity matter. Returning home clears the deployed net; net fish are only sold after hauling and stowing.

The captain, deckhands and fishermen now use the delivered skinned crew and role outfits. Eleven clips cover idle, walk, carry, bait, cast, wait, strike, reel, row, cheer and stow, sampled using the simulation clock.

The bot buys, hires, fuels, sets and hauls through the same actions as the player. The final seed 7 30-voyage run reached the skiff at voyage 28; its first three voyages earned 86/133/73 gross coins per minute, versus late rowboat voyages around 30–54. Skiff voyages took 6.0/6.0/5.3 minutes, with two deck fish lost on the first haul voyage. The average meets the initial throughput improvement goal; longer voyage pacing and more seeds remain future tuning work.

Verification runs on `Catchline-sim`, never batchmode on the open main project. `docs/tools/check.ps1` syncs assets to that scratch project; use `-Method Catchline.EditorTools.SkiffChecks.Run` for refit/save/fuel/rig checks, `-Method Catchline.EditorTools.SkiffChecks.Automation` for crew/net tests, or its default method for a 30-voyage balance run. The automated checks use a separate temporary save file.

## Zero-coin contract sale fix — 2026-10-15

Every fish in a sold haul earns its normal market value immediately, including
fish matching an unfinished contract. Those fish also advance one matching
contract; completion pays the listed reward as an additional bonus. Partial or
expired contracts never consume unpaid fish. The live haul/port quote uses this
same calculation. Historical zero-payout behaviour was a bug, not intended design.

Fisherman feedback (Mo, 2026-10-15): basic/expert/veteran strike80/85/90% of bites. Automatic catches, misses, bite badges, lost-fish and stow popups stay silent; captain feedback remains visible. Aggregate haul and crew status still update.

## Mo fish/content tuning — 2026-10-16

Ten species now share the five existing grounds: whiting joins Harbour mouth and
Kelp bank, red mullet joins Sandbar and Rocky point, turbot joins Sandbar and Deep
channel. Existing species IDs are append-only for save compatibility. New
contracts use the same voyage board and known-ground pool. Pollock/bass/cod/conger
prices rise about20–29%; herring/mackerel/plaice prices stay unchanged.

Squid still adds0.4 cast power, now also suppresses herring/mackerel table weight
to4% and biases toward substantial species. Its specimen roll uses the upper65%
of each species' weight range. This improves expected landed value; missed
strikes, fish availability, freshness and market saturation still matter. No
guaranteed profit per cast. Scraps remain unlimited and restricted to small
herring/mackerel. Worms remain the everyday low-cost option.

Supplies also offers30 worms for24 coins and15 squid for36, alongside existing
10-for10 and5-for15 packs. The existing Use squid first toggle remains a preference;
when worms run out, remaining squid is used. Fishing HUD now names the next bait.
Catch portraits are rendered from distinct authored fish models; rewards retain
nonblocking captain-only feedback. Native Unity art/HUD/audio review is pending.
See CLI-FISH-CONTENT-REVIEW.md for measured checks and integration notes.

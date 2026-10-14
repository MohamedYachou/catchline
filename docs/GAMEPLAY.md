# Catchline: gameplay design

Single source of truth for how the game plays. Numbers are starting values for tuning, not promises.

## Pillars

1. **Automation is the game, fishing is the accent.** You start doing every job by hand and slowly build a boat that runs itself, but it never becomes cosy.
2. **Slow, not frantic.** Think Factorio and Satisfactory, not Overcooked. You are rate-limited: by hand you are at best as fast as yourself. Mistakes cost time (a fish gets off, bait is lost), never a game over.
3. **Your hands are the scarcest resource.** Every automation frees your hands from one job and the game hands them a new, bigger one. Events and crew gaps keep pulling you back to the real fishing.
4. **People management never stops.** No permanent crew. Everyone is on a contract, everyone can get sick, and the hiring board is never guaranteed.
5. **Fully active.** No idle income. A daily login reward is fine.

## The voyage loop

1. **Harbour:** sell the catch, take contracts, hire crew, buy provisions and bait, buy upgrades.
2. **Map:** pick a fishing spot. Spots differ in species, distance and how depleted they are.
3. **Sail out:** a short animation. The boat view stays fixed; only the surroundings change (harbour quay, open sea, kelp, rocks, deep water, later islands and tropical shallows).
4. **Fish:** until the storage is full, provisions run out or you choose to go home. There is **no voyage timer**: storage size and provisions decide how long you stay.
5. **Sail home** and repeat.

**The voyage is the unit of time** for everything: crew contracts, harbour contracts, spot recovery and market recovery. Day and night can be purely visual inside a voyage.

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

- **Crew gaps.** The hiring board is random. Some voyages nobody is available for a job, so you do it yourself.
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

- **Everyone is on a contract** for a number of voyages, with a fee paid up front. When it runs out they leave, or you re-sign them at the current board price if they are on it.
- **Three grades:**

| Grade | Speed | Contract | Fee | Where |
|---|---|---|---|---|
| Hand | 1.0x | 2 voyages | base | Usually on the board |
| Experienced | 1.5x, +1 trait | 3 voyages | 2x base | Often on the board |
| Veteran | 2.0x, +2 traits, also raises catch quality | 5 voyages | 5x base | Rare, a few times per location |

- **Hands must feel fine, not bad.** No penalty systems that only hit cheap crew. Every gap between grades is a bonus, never a punishment.
- **Prestige:** your best veteran comes back on the new location's board, keeping their level, on a normal paid contract. Nothing is permanent.

### Why experienced crew are worth it (cargo-capped voyages)

The cargo is the same either way, but you finish it faster, and since there is no idle income, **coins per real minute** is what counts. Example, skiff with 2 crew and a cargo worth 2,000:

| | Voyage | Crew cost per voyage | Profit per voyage | Profit per minute |
|---|---|---|---|---|
| 2 hands (400 for 2 voyages each) | 20 min | 400 | 1,600 | **80** |
| 2 experienced (800 for 3 voyages each) | 13 min | 533 | 1,467 | **113 (+41%)** |

Experienced crew earn a little less per voyage and a lot more per hour. It only pays where they are the bottleneck, so placing your one experienced hand is a real decision. Veterans also raise catch quality, so the same hold sells for more.

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
- **Never sold:** crew contracts, permanent crew or hull progress.

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

- **Rod cycle:**
  1. Tap the **Fish** bubble above a rod. The captain walks there, baits the hook (1.2 s; skipped when the deckhand already baited it) and casts by himself.
  2. The **strike minigame** opens: a close-up of the bobber with a fish circling closer. Fish shadows also swim in the water around the boat.
  3. Wait 6-14 s through 1-3 nibbles (the bobber twitches and the fish darts in).
  4. When the bobber goes fully under, **tap anywhere once** inside the bite window (0.9 s). Tapping on a nibble spooks the fish, and missing the window lets it get away; both cost the bait.
  5. Reel (1-2.5 s by weight). The captain tosses the fish onto the deck next to him.
  6. **Solo:** tap the fish's **Carry** bubble and the captain takes it to the cooler. **With a deckhand (tier 2+):** they fetch it and bait the hook, and the rod's Fish bubble comes back for your next cast.

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
| Crew Office | Deckhand contracts: hands, sometimes experienced, rarely a veteran. Nobody signs on for good |
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

- **Skiff licence goal** visible (16 fish in one voyage + 1,500 coins), refit coming in build 2.

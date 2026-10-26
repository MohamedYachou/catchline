# Catchline master plan — from the current build to v1 (tiers 0–5)

Status: the execution plan for everything that is not 3D art or images. Owner:
the local Claude Code session(s). Art and images are in `docs/ART-PLAN.md` and
belong to Codex. Agreed with Mo on 2026-10-23. Where this plan and an older
document disagree, this plan wins; `docs/BLUEPRINT.md` (design),
`docs/CARDS-AND-SPEEDS.md` (numbers) and `docs/UI-SYSTEM.md` (interface) are
its reference specs and are updated when this plan changes them.

The plan is written so that a session with no prior context can pick any
milestone, read its section, build it, prove it, and move on without asking.

---

## Part A — Decision register

Every decision Mo made in the 2026-10-23 design session, in one place. "Default"
marks a call made by the lead where Mo gave no ruling; it stands until Mo
overrides it.

### A1. Product and scope
1. Mobile F2P first, PC second. Revenue from selling things, not ads. Battle
   pass later, not now. Nothing pay-to-win: crew cards are never sold.
2. A voyage is a 10–20 minute mobile session: go out, fill the hold, come back,
   sell. Bigger boats hold more, catch more, and cost more to run and upgrade.
3. The game is management of a labour chain. Fishing is flavour. What Mo
   wants: start manual, delegate, the bottleneck moves, repeat with more
   complexity. Each boat has its own limit; the next boat fixes it and adds a
   new one. Models: Factorio, Satisfactory, RimWorld, Timberborn.
4. v1 is tiers 0–5. Tiers 6–10 are not designed now ("fix the base game").
   Recorded for later: crane + scuba diver who spears sharks (fishers never
   spear); a raft the captain takes out for spear mini-bosses with its own
   minigame (Black Flag whaling); squid specialisation at a late tier even
   though night fishing starts at tier 2. Rejected for ever: pots on a string
   worked by a moving boat; a freezer boat; conveyors or any machine that
   replaces crew; fish finder; income-only multipliers.
5. World 2 / prestige after tier 10: start over on a new map with new cards to
   collect, keep all old cards, receive wildcards, small boats cannot carry
   everyone, a maxed late-tier card may sail on a tier-1 boat. Recorded, not
   scheduled.

### A2. Camera, boat, map
6. Fixed camera. The boat never moves while fishing.
7. Relocation inside one map only, a few boat-lengths: tap the wheel, enter
   move mode, move to another ground, tap off, back to management. Never
   between maps, never open world, never multi-stop.
8. Maps become at least 3× bigger with several grounds each. The navigator
   tells the captain when the current ground is poor and when a better one
   appears, roughly every 3–5 minutes.

### A3. The chain
9. Stages: catch → sort → table → hold → sell. Every station has baskets that
   deckhands haul between. Only the hold is "unlimited" up to its kg.
10. Sorting exists from the first boat. Tier 0: the captain taps keep or throw
    for each fish. Tier 1: a deckhand sorter whose primary job is sorting and
    whose backup job is hauling.
11. Undersize rule: any fish in the bottom 25% of its species' weight range is
    always thrown back. Not optional.
12. Keep rule: the player may toggle whole classes to throw back ("no
    whites"). No kg thresholds, no species lists.
13. Classes: white, green, blue, purple, gold, red (the existing six tiers).
    White/green/blue yield 1/2/3 chum at the table. Purple and above are always
    turned into their species' special product (shark tooth, marlin bill, ray
    skin...). Common fish are either fish or a generic product; fillets and the
    "prepare" premium are removed.
14. Table orders: a short list of products with counts 1 · 5 · 10 · ∞. Done or
    starved orders are skipped; with nothing ordered, fish pass through to the
    hold.
15. No market saturation. Catching many of one fish never lowers its price.
16. Hold: kg based (kept). Tiers 0–2 lose up to 40% value over time; from tier
    3 the hold is frozen automatically and nothing degrades. No icing chores.
17. Hauling must not be the only bottleneck. Fisher baskets are large, hauling
    is fast; only net bulk is allowed to stress haulers. Each stage is limited
    by a different kind of thing (see BLUEPRINT §2).

### A4. Crew and jobs
18. Roles: Captain, Navigator (fixed slot from tier 1, cannot be swapped),
    Fisher, Deckhand, Engineer (tier 5). Diver later. "Processor" is a deckhand
    with the Table speciality.
19. Fishers do their gear end to end: fetch bait from the shared bin, bait,
    cast or set, strike, reel or haul, drop into their own basket. Nobody
    delivers bait. Unmanned rods catch nothing. Deep lines and cages catch on
    their own once a fisher has baited and dropped them; the fisher raises
    them; a deckhand empties the basket.
20. Deckhands: Haul · Sort · Table, as a **primary and a secondary** duty.
    No priority tables. Bigger boats get a second sort table and a second
    processing table because fishers outnumber deck capacity.
21. Berths: tier N = N hires + navigator + captain. Roster about 2× berths so
    there is always someone left ashore and a real team choice per map.
22. Crew are permanent named cards, the same for every player, unlocked in a
    fixed order by tier. Rarity blue → purple → gold via wildcards. Level from
    XP = kg landed while deployed. Wages per voyage by rarity and level. Hire
    fees and expiring contracts are removed.
23. Abilities: blue = small passive, purple = teamwork, gold = signature (two
    rods at once, bucket brigade, batch cut...). Abilities must be great and
    pair up: two complementary cards are worth 3× one. Rejected: "chain
    strike".
24. Speed: speciality skill 100 at every rarity; other jobs in the role at
    50/65/80 by rarity; level adds up to +43.5% (default, from today's chat;
    overrides the older "equal base speed" note).
25. Captain: skill 100 at every deck job, no wage. His pickup/stow slowness on
    the compact boat is a bug in the speed model and is fixed first.

### A5. Fishing
26. Bait never blocks fishing: scraps are free and infinite. Bait decides what
    bites, never whether. Shop bait may luckily reach purple but never a large
    one and never gold/red; those are chum-only, and chum is only made aboard.
27. Rods: fisher-side only; the player strikes for the captain's rod.
28. Nets: fisher sets, tends, hauls; the pile goes to a basket; the deckhand
    sorts it. Rejected: gear "readiness" chores (re-rig, mend) every cycle.
29. Night voyages from tier 2 with a lantern, later deck lights. Night must
    carry real danger. Night rewards are different species and products, not
    bigger fish. "Bigger fish" is not allowed to be the only reward axis of
    anything.
30. Grounds drain per species as you fish; quota per map stops farming one
    expensive ground; undersize throwbacks are exempt.

### A6. Risk and events
31. There must be a way to do badly: a voyage can lose money through wages,
    fuel, bait, lost gear, lost fish, fines and failed contracts.
32. Events in the dozens, with chaos at every stage of the chain (jellyfish in
    the nets, flying fish on deck, gulls on open baskets...). Answers are only:
    tap, reassign, change a rule, spend a consumable, accept.
33. Rotating "+10% rods when cloudy" style map modifiers are rejected as
    lacklustre. Conditions must change what the deck has to do.
34. Engineer: no raw multipliers. Machines enable new ways to fish (lights,
    haulers, compressor) and need power; the engineer keeps power up.

### A7. Interface
35. Every screen, button and element is rebuilt in one language that matches
    the four concept images (Clash Royale / BTD6 physicality). The right-hand
    crew rail stays. Management is full screen; duties are tap-to-cycle.
36. Casual: no rule simulator, no maths to play, no charts, costs per minute
    or efficiency rings. Status is a word.

### A8. Working method
37. Lead designs and specifies; the local Claude Code session(s) build
    everything that is not art; Codex builds 3D art and images only. Two local
    sessions may run in parallel (UI and gameplay) because gameplay and UI are
    separated by read-models (Part B).
38. comms.md stays but with one START and one DONE per task, five lines each.
39. Legacy test suites a milestone breaks are replaced by that milestone's
    suite, not kept green at any cost (default).
40. Saves: v2 starts fresh; migration is best-effort for coins, hull and owned
    upgrades (default).
41. Chests are earned only for now: contracts, tier milestones, daily streak.
    Purchasing arrives with the shop later (default).
42. Grounds per map: three, distinct (default).
43. The five hull models stay; stations are added as props with anchors
    (default).

---

## Part B — Architecture

### B1. Why
Today the game is ~15k lines of partial classes with a special case per hull
(`VoyageCompactFisher`, `VoyagePrepFisher`, `VoyageTier5`, `VoyageDeepLines`,
`VoyageNetUnload`, `VoyagePrepOrders`, `VoyageBalance*`), three UI skins and
hard-coded crew behaviour. Every new boat or job costs another file. The
rework replaces that with four pillars so the content from tier 6 onward is
data plus art, not code.

### B2. Pillar 1 — the deck graph is data
A hull is: a `HullDef` (grid, cell size, capacity) plus a **station file**
delivered by Codex with the model:

```
Assets/Art/Models/Boats/<Hull>.stations.json
{
  "hull": "CompactFisherV1",
  "stations": [
    { "id": "rod1", "kind": "Rod", "pos": [x,y,z], "yaw": 0, "workTile": [gx,gy], "basketOut": [x,y,z] },
    { "id": "net1", "kind": "Net", ... , "basketOut": [...] },
    { "id": "sort1", "kind": "SortTable", ..., "basketIn": [...], "basketOut": [...] },
    { "id": "table1", "kind": "ProcessTable", ..., "basketIn": [...], "basketOut": [...], "places": 2 },
    { "id": "hold", "kind": "HoldHatch", ..., "workTile": [...] },
    { "id": "bait", "kind": "BaitBin", ... },
    { "id": "nav", "kind": "NavPost", ... },
    { "id": "lantern", "kind": "Lantern", ... },
    { "id": "gen", "kind": "Generator", ... }
  ],
  "blocked": [[gx,gy], ...]
}
```

Runtime types (new folder `Assets/Scripts/Game/Deck/`):

- `Station` — id, kind, anchor, work tile, facing, `In`/`Out` baskets,
  current worker, power draw, enabled flag.
- `Basket` — id, kind, `CapacityCount`, `CapacityKg`, `List<CaughtFish>`,
  claims. Fish objects keep their identity through the whole chain.
- `DeckGraph` — grid, stations, walkable tiles, path cache; built from
  `HullDef` + station file by `DeckGraph.Load(hull)`.

Basket capacities (default): RodOut 6 · JigOut 8 · NetOut 16 · CageOut 6 ·
LineOut 4 · SortIn 12 · SortOut 12 · TableIn 10 · TableOut 8. Bait bin: scraps
∞, worms 30, squid 30, chum 20. A fish over 5 kg does not fit a basket: it
lands loose on the deck tile beside its station and blocks that tile until
carried; over 15 kg needs two carriers (or Power lifter).

### B3. Pillar 2 — one job system
- `Worker` wraps `Person`: role, speciality, duties (primary, secondary), card
  reference, `Skill(JobKind)`, `LevelMult`, carrying (≤ 3 fish or 6 kg), claims.
- `Job` — kind (Haul, Sort, TableWork, RodCycle, NetCycle, CageCycle,
  LineCycle, JigCycle, Relocate, EventResponse), source, target, phases
  (walk → act → walk → act), durations from the speed model, cancel semantics
  (claims released, fish stay where they are, nothing duplicated).
- `Scheduler.Tick` — for every idle worker: fishers run their station's cycle;
  deckhands take the highest-pressure job of their primary duty (fullest
  basket ratio, then nearest), else their secondary; the captain takes only
  what the player taps. One claim per fish and per basket slot.
- Speed model and all base durations: `docs/CARDS-AND-SPEEDS.md` §1 and §4.
- Abilities hook into this system through `IAbility` (B5), never through
  special cases in jobs.

Routing after sort: undersize → thrown (counted for the log, exempt from
quota); class in the throw list → thrown; purple+ or matching an open table
order → `SortOut` flagged `NeedsTable` → hauled to `TableIn`; otherwise
`SortOut` → hauled to the hold. Table output: chum → bait bin; products and
special products → hold.

### B4. Pillar 3 — gameplay never draws, UI never mutates
Gameplay exposes immutable read-models, rebuilt at most every 0.25 s:

- `HudReport` — day/time, coins, ground, hold kg/cap, fuel, bait counts, goal,
  bubbles (world position, label, icon, command id).
- `StageReport[4]` — rate, capacity, status (Steady/Busy/BackedUp), queue
  count, cause text, recommendation, suggested command.
- `CrewReport[]` — card id, name, role, speciality, duties, status word,
  progress (0–1 or none), ability flags.
- `GroundReport` — current ground, per-species richness band, other grounds
  with bands, relocation allowed and why not.
- `EventReport` — active events, lead warnings, allowed responses.
- `RosterReport`, `ShopReport`, `ContractReport`, `SaleReport`, `PowerReport`.

UI sends `Command`s (`AssignDuty`, `SetKeepRule`, `SetOrder`, `Relocate`,
`RespondEvent`, `Deploy`, `Buy`, `Sell`, `SetBaitPermission`, `TogglePower`...)
through one `GameCommands` entry point. This boundary is what lets the UI
session and the gameplay session work at the same time: UI owns
`CoastalCanvas`, `Skin`, `VoyageInterface*`, `VoyageManagement*` (presentation
half) and reads reports; gameplay owns everything else and never touches UGUI.

### B5. Pillar 4 — content as tables
Static data lives in `Assets/Scripts/Game/Data/` as C# tables (same style as
`GameData`), one file each: `Cards`, `Abilities`, `Products`, `Buyers`,
`Contracts`, `Events`, `Grounds`, `Bait`, `Quota`, `Chests`. Art plugs in by
id (portrait id, icon id, model id). Nothing here needs a code branch to add
a row.

`IAbility` hooks: `ModifyDuration(JobKind, ref float)`,
`ModifyCapacity(BasketKind, ref int)`, `ModifyChance(ChanceKind, ref float)`,
`OnFishLanded`, `OnNetHauled`, `OnSortDone`, `OnTableDone`, `OnRelocate`,
`OnEvent`. Teamwork abilities read neighbouring workers through the scheduler.

### B6. Save model v2
`SaveV2 { Version=2, Coins, Hull, Owned upgrades, Cards[] {Id, Rarity, Level,
Xp}, Wildcards per role, Deployment[], BuyerRep[], Contracts[], Quota state,
Ground richness[], Chest pity, Day, Settings }`. A v1 save is read once for
coins, hull and upgrades, then written as v2. No other v1 field is kept.

---

## Part C — Milestones

Each milestone: scope · data · code · acceptance. Captures are native
1440×900 and 844×390 from `Catchline-sim` through `docs/tools/check.ps1`.
Every milestone adds its own `Assets/Editor/<Milestone>Checks.cs` and may
delete legacy suites it invalidates. Commit per milestone on `proto/deck-sim`.

### M0 — Speed model and cleanup (1 session)
- Implement CARDS-AND-SPEEDS §1 and §4: one formula, delete `CrewWorkSpeed`,
  `DeckhandHandlingSpeed`, `CompactPickupTime`, `CompactStowTime`; captain
  skill 100. Pickup 0.5 s, stow 0.6 s everywhere.
- Delete market saturation (`MarketDropPerFish`, `MarketRecovery`, market
  arrays). Delete prepare/fillet (`Prepared`, `PreparedBonus`,
  `PreparedQuality`, the 25%/150% premium); keep chum code for M3.
- Delete the legacy tier-5 condition arrays and engineer servicing of manual
  gear.
- Acceptance: `M0Checks`: captain pickup < 1 s and stow < 1 s on the compact
  boat; a hand and the captain take the same time for the same job; selling 50
  herring does not change the herring price; a save with prepared fish loads
  and sells them at raw value.

### M1 — Deck graph and the job system (core, 3–4 sessions)
- B2 + B3 in full. Station files for all five hulls: until Codex delivers
  props, generate interim station files from current hard-coded positions
  (rods, net basket, hold, prep anchors) plus primitive placeholders for sort
  table, baskets and bait bin, so gameplay never waits on art.
- Sort table with undersize and keep rule. Rod/net/cage/line baskets.
  Deckhand duties primary/secondary with tap-to-cycle commands. Tier 0 captain
  keep/throw as a two-button bubble at the sort table.
- Migrate hulls in order: rowboat → skiff → compact → prep → buoy, deleting
  the hull-specific worker code as each migrates.
- Loose big fish rule; hand capacity; two-carrier rule.
- Read-models `HudReport`, `StageReport`, `CrewReport` and the `GameCommands`
  entry point (B4), with the existing UI wired to them so the game stays
  playable through the migration.
- Acceptance: `M1Checks` per hull: every station reachable; a rod fish
  travels rod → RodOut → SortIn → SortOut → hold with one claim at a time;
  undersize never reaches the hold; keep rule honoured; a 14-fish net pile is
  sorted and stowed by one sorter and one hauler in under 60 s on the compact
  boat; duties switch after the current job; cancelling mid-carry loses no
  fish; 120 s trace on each hull with 0 lost fish and no stuck worker. Bot
  plays 10 voyages per hull.

### M2 — Cards (2–3 sessions)
- Data: `Cards` table from BLUEPRINT §14 with this correction: **Lise** is
  Fisher · Jigs (night), blue "Lamp eye" +10% jig cycle, purple "Shares the
  light" (neighbouring station counts as lit at night), gold "Ink run" (her
  jig pulls two squid per cycle). All other cards as listed. Tier grants: on
  reaching tier N the player receives all tier-N cards at blue level 1.
- `CardState`, roster, deployment (≤ berths, navigator forced), wages at
  departure (CARDS-AND-SPEEDS §2.3), XP at sale (§2.2), rarity upgrade with
  wildcards (§2.1), speciality/skill matrix (§3), strike chance by rarity and
  level.
- Delete `Grade`, `Fee`, `ContractVoyages`, `VoyagesLeft`, the candidate board
  and hire flow. Crew Office = roster + deployment.
- Abilities: `IAbility` (B5) and all 11 cards' blue abilities; then purple;
  then gold. Each ability is one small class with a unit check.
- Save v2 (B6) with the v1 import.
- Read-models `RosterReport`, wages on the departure report.
- Acceptance: `M2Checks`: level table and XP table reproduce CARDS-AND-SPEEDS
  §2.2 exactly; wages for the three examples in §2.3; a gold Sam carries a
  20 kg fish alone and a blue Sam cannot; Noor's Bucket brigade sorts a basket
  as one job; two haulers on one route both get Sam's purple bonus; deploying
  six cards on a tier-5 boat is refused; the navigator cannot be undeployed;
  v1 save imports coins/hull/upgrades and nothing else.

### M3 — Table v2 and bait (1–2 sessions)
- `Products` table: Chum (white 1 / green 2 / blue 3, 3.0 s), Fish oil (white
  or green, 4.0 s, 0.25 kg per unit, Cannery), Special product per purple+
  species (6.0 s, kg of the fish, Collector). Orders `{Product, Target 1/5/10/∞}`
  worked top to bottom; starved orders skipped; purple+ bypass the list.
- `Bait` table: scraps / worms / squid / chum with the class ceilings and bait
  factors of CARDS-AND-SPEEDS §5 and the class weights: scraps {W100};
  worms {W85 G15}; squid {W55 G30 B13 P2, purple capped at the species' lower
  half}; chum {W10 G20 B30 P30 Go7 R3}. Deep lines keep the DEEP104 weights
  with chum. Fishers take the best bait their permissions allow; scraps when
  nothing else.
- Bait bin station; chum from table output lands in it; shop bait lands in it
  at departure.
- Read-models for orders and bait.
- Acceptance: `M3Checks`: an order "Fish oil 5" consumes exactly five eligible
  fish then stops; ∞ keeps going; a purple fish always becomes its special
  product even with an empty order list; chum yields 1/2/3 by class; a
  fisher with only scraps allowed never consumes chum; 20,000 chum rolls at
  Deep channel reproduce the class weights within 1%; the hold never exceeds
  its kg with products included.

### M4 — Grounds, relocation and the navigator (2 sessions; needs ART-PLAN A1)
- `Grounds` table: per map three grounds with kind, boat anchor, day pool,
  night pool, richness per species (start 1.0, drain rods −0.02 per catch,
  nets −0.004 per kg, floor 0.3, recover +0.35 per voyage). Current map tables
  split across the three grounds so no species is lost.
- Relocation state machine: Fishing → MoveMode (all gear in; if a net or line
  is out, a modal "Haul it first / Forfeit and go") → travel 30 s along the
  map path with the camera following at fixed framing → Anchored → Fishing.
  Command `Relocate(groundId)`; the navigator post is where the wheel bubble
  lives.
- Navigator role: `GroundReport` with bands Rich ≥ 0.8 / Thinning / Poor
  < 0.5 per species; a "move" suggestion when the best other ground beats the
  current by 0.3 on the player's targeted classes; warning lead time for
  events = 8 s + 0.5 s per level. Gold Radio enables M5 radio events.
- Interim art: until Codex's 3× maps land, place the three grounds on the
  existing diorama with offsets so the mechanics are testable.
- Acceptance: `M4Checks`: richness drains and recovers per the formula; a
  move with a soaking net requires the modal; travel takes 30 s and no worker
  acts during it; the navigator cannot be removed from deployment; the report
  bands match the numbers; bot relocates when suggested and earns more than a
  bot that never moves over 20 voyages at Kelp bank.

### M5 — Buyers, contracts v2, quota, stakes (2 sessions)
- `Buyers` table: Market (everything at base), Bait shop (white/green at a
  floor of 3/6 coins per fish, squid at 8), Restaurant (blue+ of the map's
  named species at ×1.3), Cannery (fish oil 8 per unit; bulk kg contracts),
  Collector (special products at their table price). Sale auto-splits the
  haul to the best buyer per item; the sale screen shows the split. Reputation
  per buyer = coins sold to them ÷ 100; tiers at 1,000 / 5,000 / 20,000 unlock
  that buyer's contract tier and shop items (bulk bait packs, squid lights,
  heavy net system, deep-line rigs, cage sets move behind these).
- `Contracts` table: types Species×N, Class×kg, Special×N, NightSpecies×N;
  giver = buyer; deadline in voyages; reward coins + rep + chest; board of 3,
  max 2 active; rush orders at sea through the radio (M6). Delete fillet-style
  contracts.
- `Quota`: per map per voyage, by class: blue 30 kg, purple 20 kg, gold 10 kg,
  red 5 kg; white/green unlimited; throwbacks exempt. Inspector event (M6)
  fines 2× the excess value and closes the ground for three voyages.
- Stakes: departure sheet shows "This trip costs N" = wages + fuel + bait +
  lantern oil, paid on Let's go. Spare rigs consumable (5 coins); a snag cut
  spends one; with none left the rod fishes "frayed" at −20% strike window,
  never unusable. A net left out through a squall is lost (existing
  replacement cost). Failed contract: −500 rep with that buyer.
- Read-models `SaleReport`, `ContractReport`, departure cost.
- Acceptance: `M5Checks`: split sale totals equal item sums; a white herring
  sells to the Bait shop when the floor beats base; rep tiers unlock exactly
  the listed items; quota excess triggers the fine and closure; a voyage with
  five gold cards and no catch ends with negative net and the result screen
  says so; frayed rig never blocks fishing.

### M6 — Events (2 sessions, then content batches)
- `Events` table with the schema `{Id, Stage, MinTier, Day/Night, Weight,
  LeadSeconds, DurationSeconds, Effects[], Responses[], Icon}`. Scheduler: a
  voyage rolls events at random times with ≥ 45 s spacing, at most one active
  per stage, rate ×2 at night, none in the first 60 s of tier-0/1 voyages.
  Effects are modifiers on baskets, grounds, stations, workers or the hold.
  Responses are the five verbs; the UI shows one slab with one primary.
- Batch 1 (15): school passes, flying fish, jellyfish bloom, dolphins, snag,
  crossed lines, squall, big one, gull raid, spilled basket, undersize run,
  hook in hand, seasick, price spike, weather warning.
- Batch 2 (15): seal, shark takes the hook, tide turn, fog, birds working,
  drifting float, protected species, inspector boat, rival anchors, eel wraps,
  dull blade, oversized fish, roe found, man overboard, rush order.
- Batch 3 (15+): crab pinch, offal pile, hatch jam, cargo shift, won't work
  adjacent, cannery closed, breaker trip, fuel leak, light out, current
  shift, plus new ones proposed by the session in the same schema (target 60
  total by v1).
- Exact effects for batch 1 (numbers are starting values): school passes —
  rod bite wait ×0.4 and net yield ×2 for 90 s; flying fish — 6–10 white fish
  spawn loose on free deck tiles; jellyfish — next net haul yields 50%
  throwbacks and sort time ×1.5 for 60 s; dolphins — rod bite wait ×3 for
  60 s; snag — one rod stuck, fisher 20 s or Cut (−1 rig); crossed lines — two
  rods paused until a fisher untangles (10 s); squall — all fishing paused
  30 s, loose fish on deck lost; big one — a purple+ bite on the captain's
  rod with a 2 s window, miss costs a rig; gull raid — every 10 s one fish
  leaves an uncovered SortIn/RodOut basket until Shoo (tap) or 45 s; spilled
  basket — one basket's fish go loose on adjacent tiles; undersize run — next
  net haul 70% undersize; hook in hand — one deckhand paused 60 s, or 20 s if
  anyone first-aids (tap); seasick — one worker at skill ×0.5 for 120 s;
  price spike — one species ×1.5 at sale this voyage; weather warning —
  squall in 120 s unless home.
- Acceptance: `M6Checks`: scheduler spacing and night rate; each batch-1
  event applies and reverts its effect; each response verb works; navigator
  lead time by level; no event fires during travel or in harbour.

### M7 — Night (1 session; needs ART-PLAN A1 night variants)
- Chart toggle day/night per voyage. Night pools per ground (M4 data).
  Jig station and `JigCycle` (6 s per squid at skill 100, no bait, no strike).
  Lantern upgrade (Supplies, 60 coins) + lantern oil (10 coins per night
  voyage) lights one station; deck lights at tier 5 (M8). Unlit sort/haul at
  skill ×0.7. Night event rate ×2 and night-only events.
- Night species at v1: squid (jig only, 0.3–1.2 kg, bait + Restaurant),
  conger, dogfish (new white species, append-only ID), plus the existing
  night-biased rares per ground.
- Acceptance: `M7Checks`: night pool rolls only at night; jig cycle time;
  unlit penalties; oil consumed; lantern lights exactly one station; squid
  lands in the bait bin as squid bait when the keep rule throws it.

### M8 — Tier 5 power and machines (2 sessions)
- Generator 10 kW burning 1% fuel per minute while any draw is on. Draws:
  winch 4 (required by the deep net), line hauler 3 (required by the third
  rig), deck lights 3, compressor 4 (reserved). Draw over capacity trips the
  breaker: powered stations stop until the engineer resets (5 s). Power panel
  toggles per station.
- Faults: each powered station rolls 2% per cycle; a faulted station stops
  until the engineer repairs (15 s). Engineer with nothing to do hauls at
  skill 50.
- Cages and deep lines re-fitted onto the deck graph (fisher baits/drops/
  raises; `CageOut`/`LineOut` baskets; deckhand empties). Second sort table and
  second processing table from the tier-5 station file.
- Acceptance: `M8Checks`: breaker trips at 11 kW and resets; faults stop and
  resume; the deep net cannot be set without the winch powered; both tables
  and both sort tables take jobs concurrently; tier-5 bot 30 voyages with the
  intended wall per CARDS-AND-SPEEDS §7.

### M9 — Meta: chests, wildcards, roster screens (1–2 sessions)
- `Chests` table: Wooden (contract completion; 2–4 wildcards role-weighted
  to the giver's needs, 50 kg XP, 100–300 coins), Iron (tier milestone; 8–12
  wildcards, 200 kg XP, 1,000 coins), Gold (7-day streak; 20 wildcards, 500 kg
  XP). Pity: every third Wooden has at least one wildcard of the role you own
  fewest of. Open animation is UI's.
- Card detail screen data: level, XP to next, rarity upgrade cost, ability
  texts, wage.
- Acceptance: `M9Checks`: chest contents within ranges; pity rule; upgrade
  consumes wildcards and coins; XP boost applies to deployed cards only.

### M10 — Tutorial tier 0 and bot acceptance (1–2 sessions)
- Scripted first voyage: cast → strike → reel → keep/throw at the sort table
  (an undersize fish shows why it is thrown) → carry → stow → return → sell →
  buy the Rod holder → tier 1 introduces the navigator and the first deckhand
  card. Hints are commands the UI renders; skippable.
- Bot: drives duties, orders, relocation and event responses. Run 30 voyages
  per tier with the default crew of BLUEPRINT §5; report per stage
  utilisation, longest queue and most-backed-up stage; pass when the wall is
  the one intended in CARDS-AND-SPEEDS §7 and no stage idles over 50%.
- Acceptance: tutorial completes with no input other than the hinted taps;
  bot reports committed to `docs/screens/bot-v1/`.

### UI v2 — parallel track (see `docs/UI-SYSTEM.md` and `docs/archive/PROMPT-OPUS-UI.md`)
Screens in order: voyage HUD → operations → crew (duties, bait permissions)
→ harbour hub and shops → chart (with day/night and grounds) → departure
(with trip cost) → sale result (buyer split) → title and pause → catch card →
roster and card detail → chest open → event slab → relocation mode → keep
rule and table orders slabs → navigator readout → power panel → tutorial
hints. The UI session binds to read-models as each milestone lands; until
then it binds to the current state with `// TODO(BLUEPRINT)`.

---

## Part D — Sessions, ownership, order

| Session | Owns | Never touches |
|---|---|---|
| Gameplay (local Claude Code) | everything under `Assets/Scripts/Game/` except the UI files below; `Assets/Editor/*Checks.cs`; `docs/tools/`; data tables | `Art/`, `Assets/Art/`, UGUI code |
| UI (local Claude Code) | `CoastalCanvas.cs`, `Skin.cs`, `VoyageInterface*.cs`, `VoyageMenus.cs`, `VoyageHud.cs` presentation half, `VoyageManagement*.cs` presentation half, `Assets/Art/UI/` sprites built from SVG | gameplay state, saves, art models |
| Codex (art) | `Art/`, `Assets/Art/Models/`, station files, portraits, illustrations, map models | any `.cs` |

Order: M0 first (one session, no dependencies). Then M1 → M2 → M3 in the
gameplay session while UI v2 does voyage HUD → operations → crew. M4 and M7
wait for ART-PLAN A1 (maps); M8 waits for A2 (tier-5 stations). M5, M6, M9,
M10 need only code. Both local sessions merge to `proto/deck-sim` daily; the
lead reviews captures and bot reports, not diffs.

Done is: every milestone's suite green, every screen captured at both sizes
matching the concepts, bot reports showing the intended wall per tier, and Mo
playing tier 0 → 5 on his phone without opening a doc.

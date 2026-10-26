# Restaurant: fish by day, serve at night (design v1)

Written 2026-10-26 by Claude 2 from Mo's decisions in chat. This is the plan the restaurant is built from; it wins
over older docs where they disagree (MASTER-PLAN economy, BLUEPRINT buyers). Numbers marked *(tune)* are first
guesses for the pacing sim, not decisions.

## 0. Mo's decisions (10-26)

- Catchline becomes **a restaurant game with a fishing outing**. The restaurant part must be very well done.
- **One day:** set up the restaurant in the harbour by day → sail to any ground → plan the night with Mira on the way
  out → fish → prepare fillets, stock and the rest on the way home → sell what isn't needed at the market → the
  evening and night in the restaurant, where the crew cook and serve.
- **Guests order whatever the chosen ground gives.** There is no menu to pick: where you sail decides tonight's food.
  Bigger fish are harder to catch and more work, and pay more.
- **The restaurant is the money maker.** Selling fish at the market pays little. Crew cards and their upgrades stay;
  every card gets a restaurant counterpart.
- **What the boat prepares is not finished food.** Fillets, fish stock, cleaned whole fish, crab and so on still get
  cooked and plated in the restaurant kitchen.
- **The plan must show semi-reliable numbers:** how many guests and what they'll eat.
- **During fishing Mira can change the order on the fly. Once you leave the ground nothing changes**, apart from a
  few walk-ins. So you keep a little extra, nothing crazy.
- **Fish is sold before service. Whatever prepared food is left after service goes to the alley cats** (lost value),
  so you neither prep too much nor too little.
- **The captain manages, not frantic:** a few taps and decisions, moving crew to put one job before another.
- **PlateUp-like evening:** guests come in from early evening into the night. By day you buy tables and appliances and
  choose where they go. A clear kitchen area and a clear guest area. Mobile first: placement, shop and UI must be easy.
- **The restaurant opens with Mira.** Many more Mira messages through the whole game.
- Crew keep their ship models and clothes for now; restaurant outfits (2D and 3D) come later. Passive restaurant
  income: later, not now.

## 1. The day

| Phase | Where | What the player does | About |
|---|---|---|---|
| Morning | Harbour | Mira's morning note (weekday, weather, bookings). Arrange the restaurant, shop, crew, chart. | free |
| Choose the ground | Chart | Each pin shows what tonight's guests would eat if you fish there. | seconds |
| Trip out | Sea lane | Mira's plan card: guests, dishes, the catch list, special requests to accept. | 0.5-1 min |
| Fishing | Ground | Fish as now. The catch list ticks off on screen. Mira may call with a change. | 3-5 min |
| Trip home | Sea lane | The prep plan: what gets prepared for tonight, what stays whole for the market. Crew prepare it; you may fillet the special fish yourself. | 0.5-1 min |
| Arrival | Harbour, dusk | Whole fish sell at the market automatically (a short tally). | seconds |
| Service | Restaurant, 18:00-23:00 | Guests arrive, crew cook and serve, you manage. | 4-5 min |
| Closing | Restaurant | Till, reviews, popularity, leftovers to the cats, crew of the night. Sleep. | 30 s |

A full day is about 10-13 minutes, a good phone session. The rowboat days before Mira (tier 0) stay as they are now:
fish, sell everything at the market. The closed restaurant is already visible on the quay, shutters down.

## 2. Guests and what they order

**How many.** Tonight's guest count is rolled at departure from popularity × weekday × weather *(tune)*:
Monday quiet (×0.8), Friday and Saturday busy (×1.3), Sunday more families (groups of 4); rain ×0.85 and no terrace,
sun fills the terrace. Groups of 1-4 (later 6 for booths).

**What they order.** Each guest wants one fish dish, drawn from the chosen ground's fish (weighted like the catch
pool, so common fish are asked for most), filtered to dishes your kitchen can cook. Most also want a drink; some want
coffee after. A few ask for a **special**: a big or rare fish from that ground (a purple, a big specimen). Specials pay
much more and are harder to catch.

**The forecast is semi-reliable.** The guest list is rolled when you leave, but the plan card shows ranges:
"18-22 guests", "Mackerel 6-8, Pollock 4-6, Soup 3-5, plenty of coffee". The real numbers land inside the ranges.

**Changes.**
- While fishing, Mira calls 0-2 times per trip: "+3 guests, the Peeters are bringing the kids (fish and chips)", "the
  Janssens cancelled", "someone asks for sea bass if you see one". Each call changes the real list and the ranges, at
  most +20% in total.
- When you leave the ground the list is **locked**.
- At the door, walk-ins add 0-10% *(tune)*. The plan card says "plus a few walk-ins".

**Special requests** appear on the plan card with **Accept / Not tonight**. Accepted and served: big pay and
popularity. Accepted and not caught: the guest takes another dish; no bonus, no penalty beyond that.

## 3. From fish to portions

The game always shows portions, never asks the player to do kg sums.

| Prepared form (on the boat) | From | Portions *(tune)* | Cooked on |
|---|---|---|---|
| Cleaned whole fish | fish up to 0.8 kg (mackerel, red mullet, small whiting, plaice; 2 herring = 1) | 1 per fish | Grill |
| Fillets | fish over 0.8 kg (pollock, bass, cod, turbot...) | 1 per 0.4 kg of fish | Stove (pan-fried) or Fryer (fish and chips) |
| Fish stock | offcuts of every filleted fish, plus any fish you put in the pot | 4 bowls per kg | Soup kettle (batches of 8) |
| Big fish for the oven | a specimen of 4 kg or more | one platter for a whole table | Oven |
| Crab, squid | crab pots, squid | 1 per crab / 0.3 kg squid | Steamer pot / Fryer (calamari) |

Big fish feed many guests: a 4.5 kg cod is about 11 fillet portions plus soup. Fish size matters again.

**Staples** are always there and need no fish: coffee and tea (coffee machine), lemonade and beer (drinks fridge),
fries and bread. They cost a little per serving (bought automatically), earn a little, and a drink resets a waiting
guest's patience a bit.

## 4. The trip home: preparing for tonight

When the boat leaves the ground, the **prep plan** opens (Mira's card, section 9):
- Left: the catch, grouped by fish.
- Right: per dish, the portions to prepare, set by the crew from the forecast, with a marker showing the forecast range
  and +/- steppers (one fish per step).
- A margin choice: **Tight / +10% / +20%**. The default is +10%.
- Bottom line: "Restaurant: 24 portions (forecast 20-24) · Market: 11 whole fish → 96 coins".
- Forms the kitchen can't cook are greyed with the reason ("needs a grill").
- **Fridge space** caps tonight's stock ("Fridge: 30 portions"); more fridges mean more stock (section 5).

The crew prepare it during the trip and always finish by arrival; the trip length never blocks the plan. **Captain's
cut (optional):** fillet the special fish yourself with one knife swipe along a guide line; a clean cut gives one
extra portion.

On arrival everything not prepared sells **whole** at the market. Market prices are well below restaurant value
*(tune: the market pays about half of today's prices; a dish about 3× its raw fish)*. After service, prepared
portions that were not sold go to the alley cats: a cute scene, but the value is gone (shown on the closing card).

Why this works: prep too little and guests get soup or a substitute (less pay, less popularity growth); prep too much
and the cats eat the profit. The forecast ranges and the +10% margin make the right call easy, never exact.

## 5. The restaurant

**Where.** Mira's family's old restaurant, a corner house at the end of the quay's house row with its terrace side to
the water (exact spot fitted into the harbour layout; HARBOUR-PLAN appendix). Closed on tier 0, it opens when Mira
joins. Tap it in the harbour to go inside. The player can rename it (default "Mira's").

**The view.** One fixed camera from the front looking down (about 50°), the front wall cut away like a doll's house.
Landscape. The kitchen sits at the back/left behind the **pass** (a counter with a serving hatch), the guest area at
the front/right, the door to the quay at the front with Mira's reception desk, and a back door from the kitchen to the
alley where the cats wait. Exact pitch, FOV and the largest room that stays touchable come from Codex 1's study
(`docs/screens/restaurant-scale-1/`).

**The grid.** 1 m tiles. Every item fills 1×1 or 2×1 tiles. Kitchen items only go in the kitchen; guest items only in
the guest area; bar items in the guest area; decor on the guest floor or the walls. The zones never mix, so the
layout always reads.

**Stages** (grid sizes final after the scale study):

| Stage | Name | Floor | Opens |
|---|---|---|---|
| 1 | Café | 8×5 (kitchen 3×5) | Mira joins (Skiff) |
| 2 | Bistro | 10×5 + terrace 4×2 | popularity 3 + coins *(tune)* |
| 3 | Restaurant | 12×6 + terrace 5×2, knocked through into the next house | popularity 5 + coins |
| 4 | Seafood house | 14×7 + terrace 6×2 | popularity 8 + coins |

Each stage also changes the building outside (Codex 2's exterior sheet), so the harbour shows your progress.

**Starting kit (stage 1, free):** stove, soup kettle, prep counter, fridge, coffee machine, reception desk, two tables
for 2.

**Items** *(prices tune)*:

| Area | Item | Size | What it does |
|---|---|---|---|
| Kitchen | Prep counter | 1×1 | Plating; a cook needs one nearby |
| | Stove | 1×1 | Pan-fried fillets |
| | Soup kettle | 1×1 | Soup, 8 bowls a batch: the safety net |
| | Grill | 1×1 | Grilled whole fish |
| | Fryer | 1×1 | Fish and chips, calamari, fries |
| | Oven | 1×1 | Big-fish platters for a whole table |
| | Steamer pot | 1×1 | Crab (later mussels) |
| | Fridge | 1×1 | Holds tonight's stock, 15 portions each |
| | Sink and dish rack | 2×1 | Clean plates (from R4) |
| Bar | Coffee machine | 1×1 | Coffee, tea |
| | Drinks fridge | 1×1 | Lemonade, beer |
| | Bar counter with stools | 2×1 | Seats solo guests and drinkers |
| Guests | Table for 2 / for 4 | 1×1 / 2×1 | Seats |
| | Booth for 6 | 2×1 | Big groups (stage 3) |
| | Terrace table | 1×1 | Outside seats (stage 2), empty in rain |
| | Reception desk | 1×1 | Mira's spot, next to the door |
| Decor | Trophy mount | wall | One of YOUR record fish, from the catch records |
| | Net with floats, lamp, plant, framed chart | 1×1 / wall | Ambience |
| | Jukebox | 1×1 | Ambience, more patience |

Ambience (decor and trophies) raises patience and tips. A chalkboard by the door shows tonight's catch automatically.

**Layout matters, gently.** Staff walk on the grid, so a stove far from the pass or tables far from the hatch costs
time. After each night Mira may give one tip ("Our waiters walked 900 m tonight. Tables nearer the hatch would help").

## 6. The night service

Service runs from 18:00 to 23:00 game time, about 4 minutes at normal speed *(tune)*, with pause, ×1 and ×2. Guests
arrive in a curve: a trickle at six, the rush from seven to nine, a tail until half past ten, when the door closes.
Service ends when the last table leaves.

**A guest's evening:** arrives → waits at the door (patience ring) → Mira seats the group at a free table that fits →
a waiter takes the order → drinks from the bar → the ticket goes to the kitchen → a cook takes stock from the fridge,
cooks it on the right appliance, plates it at the pass → a waiter carries it out → they eat → they pay (dishes,
drinks, tip by satisfaction) → the waiter clears the table. From R4 the plates go to the sink and need washing
(PlateUp's dish bottleneck).

**Satisfaction** (1-3 stars per table): waiting times, got what they asked for, quality (fresh today, cook level,
captain's cut, special served), ambience. Groups that run out of patience at the door leave; at the table they still
pay, with no tip and a bad review.

### The crew at night

Tonight's staff are the crew who sailed today, plus Mira.

| On the boat | In the restaurant | What their card does |
|---|---|---|
| Fisher | Cook | Cooking speed; higher rarity, better dishes |
| Deckhand | Waiter | Walking and order speed, tips |
| Engineer | Handyman | Fixes breakdowns, fewer of them; washes plates when idle (R4) |
| Navigator | Barista | Drinks and coffee; serves drinks to waiting guests |
| Mira | Reception | Seats guests, patience at the door, popularity bonus |
| Captain (you) | Manager | The manager's actions below |

Any crew member can take any job; in their own role they work at full speed, in another at 70% *(tune)*. Level and
rarity use the one work-speed model from `docs/CARDS-AND-SPEEDS.md`. Each card shows a second line, e.g. "Restaurant:
cook, +10% cooking speed". Card abilities get restaurant twins later (R6); v1 uses level and rarity only. Crew who
stayed ashore don't work in v1 (later: a few "shore staff" slots for bench cards).

### What the manager does (a few taps)

1. **Move crew between jobs.** Tap a portrait on the staff rail, pick a job. "Two fishers on waiting tonight, the
   kitchen is quiet": that is the core decision.
2. **Serve this first.** Tap a table to pin it; staff handle it before others. One pin at a time.
3. **Seat a group yourself** (optional): drag a waiting group onto a table. Otherwise Mira seats them.
4. **Sold out?** A small card: offer soup (they pay less) / another fish if one is spare / sorry and a free coffee.
   Picks soup by itself after a few seconds.
5. **Fix things.** A broken item (a smoking fryer, the stove flame out, the fridge door, a wobbly table, a flickering
   light) stops working. Tap it and the handyman goes; with no handyman free, hold it to fix it yourself.
6. **Captain's moments.** Carry the catch of the day or a special to its table (tap when it's at the pass: big tip and
   popularity); shoo the cat that sneaks in; greet a VIP with Mira.
7. **Close the door** early when the fridge is empty.

**Events** (light, a few per night, from R4): a birthday table (offer a cake for a big tip), the alley cat sneaks in
(shoo it or it eats a portion), a tour group of 6 (needs a booth or two tables), a regular with a favourite dish, rain
moving terrace guests inside, and later the food critic.

## 7. Closing

A closing card: guests served (and any who left), coins from dishes, drinks and tips, the total; three review cards
with stars and a funny line ("The mackerel was so fresh it winked at me"); the popularity bar filling; leftovers
("3 portions went to the alley cats", the cats eating out back, the lost value greyed); crew of the night (a small
token bonus *(tune)*); Mira's personal line. Then **Sleep** → next morning.

**Popularity** only grows; a bad night just grows it less *(Mo to confirm)*. Its levels raise the guest count, bring
new guest types (tourists, fishermen's groups, the critic) and open the stages. Later: critic stars, up to three, as
the long-term goal.

## 8. Economy

- Restaurant income becomes the main income; the market pays less. The pacing sim (`docs/plans/CARDS-PACING.md`) is
  rerun with the restaurant before numbers are fixed; boat, chart and crew prices are rebalanced against it.
- Restaurant items and stages are a new coin sink.
- **Watch:** the restaurant's guests per night must grow with the boat tiers (stages, popularity, more crew as staff,
  pricier Outer coast fish), or a bigger hold stops mattering. The surplus that doesn't fit tonight still sells at
  the market, so big hauls are never worthless.
- No paid currency, no timers to wait out.

## 9. Mira

Mira becomes the voice of the restaurant, using the tutorial bubble with her talking frames and Heart's voice:
morning note; the plan card; calls while fishing; "we have enough for 22" when you leave the ground; the prep card;
"selling the rest" on arrival; seating, sold-out and event calls during service; her closing line; story beats (the
reopening, each new stage, the first critic); layout tips. Text carries the numbers; the voice uses short fixed lines
("Captain, change of plans!") so every line can be voiced ahead of time.

The reopening is her story: her family's restaurant, closed for years; when she joins (Skiff) she asks you to
reopen it with her. The first night is a short tutorial service with four guests.

## 10. Screens (mobile first, 844×390; desktop 1440×900)

All in the existing UI kit (docs/UI-SYSTEM.md, Fredoka), big touch targets (at least 44 px), one thumb.

**S1 Arrange mode** (harbour, by day). The room fills the screen between a top bar (back, "Arrange", coins, undo) and
a bottom drawer (84 px): category tabs on the left (Kitchen, Guests, Bar, Decor, Expand), item cards scrolling
sideways (picture, name, price, footprint dots, "new" badge). Tap a card: the item appears as a ghost on the nearest
free valid tile in its zone; drag it (it floats above the finger and snaps to tiles); rotate and ✓/✗ float next to it;
you pay on ✓. Tap a placed item to lift it: drag, rotate, store, or sell back. Invalid spots show red with one short
reason ("Kitchen items go in the kitchen", "Leave a way to the door"). A path check keeps door → every table and pass →
every appliance open. Dragging on empty floor pans when the room is wider than the screen.

**S2 Service HUD.** Top: the evening clock (18:00-23:00) as a strip with the arrival curve and a now-marker, coins
tonight, popularity, speed (pause, ×1, ×2). Left: tonight's stock, one plate icon per dish with its count, red when
low. Bottom: the staff rail, crew portraits with a job icon (pan, tray, wrench, cup, desk) and a busy ring; tap to
change job. In the room: guests' bubbles (order icon and patience ring), broken items flashing, event cards sliding in
from the right with Mira's face and two or three buttons.

**S3 Mira's plan card** (trip out). Mira on the left. "Tonight: Friday, 18-22 guests (plus a few walk-ins)". The
dishes they'll want as icons with ranges. The catch list in fish ("about 8 mackerel, 3 kg pollock"). Special request
cards with Accept / Not tonight. "Got it". While fishing, the catch list shrinks to a ticket pinned at the screen edge
("Mackerel 5/8").

**S4 Prep plan** (trip home). Section 4: catch on the left, portions per dish with steppers and forecast markers on
the right, margin choice, fridge space, the restaurant/market totals, "Prepare", and the optional captain's cut.

**S5 Closing card.** Section 7.

## 11. Not in v1 (TODO)

Restaurant outfits for the crew (2D and 3D), passive restaurant income, card abilities' restaurant twins, shore staff
slots, critic stars, smoker, live tank, more dishes per fish (a recipe book), night fishing (see below).

**Night fishing** is half built and never reachable: `GameState.NightVoyage`, night fish pools in `Data/Grounds.cs`,
the Jig boat's lamps and night abilities exist, but nothing in the game starts a night trip. With nights in the
restaurant, it stays parked. A later option: "closed tonight, gone fishing" for special night trips.

## 12. Build order

| Slice | Content | Who |
|---|---|---|
| R0 | Concepts: look options, exterior stages, interiors, item kit, service moment, UI mockups (Codex 2); camera and room-size study (Codex 1). Mo picks the look. | now |
| R1 | The restaurant in the harbour: building (closed → café), go in and out, interior view with grid and zones, arrange mode with shop and placement, layout saved. No service yet. | |
| R2 | Service core: guests, arrival curve, Mira seating, waiters, cooks, appliances, dishes from stock, pay, closing card; staff = today's crew; the staff rail. | |
| R3 | The day plan: forecast, chart pins, Mira's plan card, the ticket and her calls while fishing, the prep plan, market sale of the rest, leftovers to the cats. | |
| R4 | Manager moments and events, plates and sink, popularity levels, stages 2-4, the rest of the items. | |
| R5 | Economy rebalance with the pacing sim, the first-night tutorial and Mira's story, the Mira message pass. | |
| R6 | Later list (section 11). | |

Technical shape: the service is a pure logic simulation (`RestaurantSim`, tickable headless, with editor checks and a
pacing-sim hook) and the 3D room follows it, like the deck simulation. Tile pathfinding on a grid of at most 14×9.
Staff reuse the crew rigs and animations (walk, carry, the prep table's work loop). Layout, stage, popularity and the
day counter live in a new save block.

## 13. Open questions for Mo

1. Tonight's staff: only the crew who sailed today (my pick for v1), or can crew who stayed ashore work too?
2. Popularity only grows, a bad night just grows it less: OK?
3. Fridge space caps how much you prepare: OK?
4. Special requests with Accept / Not tonight: OK?
5. The player can rename the restaurant (default "Mira's"): OK?
6. Night fishing stays parked: OK?

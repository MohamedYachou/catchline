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

Mo, later on 10-26:
- **Jobs are fixed per card**: fishers cook, deckhands are haulers (serving, clearing and cleaning tables, washing
  plates, emptying trash cans into an outside container), the engineer is the handyman (things break quite
  regularly), Mira is the navigator and so the host who seats guests and takes payment, and two baristas (a girl and a
  boy: Ines and one more) come at higher tiers. The captain walks around helping.
- **Who you take fishing by day works the night**, so spread the right crew.
- **A dashboard like the boat's** shows who does what and the bottlenecks: how fast groups are seated, how long the
  food takes, how long it waits before it's served.
- **Food served more than about 30 s after it's ready is cold**; the guests are a bit less happy.
- **The night is about 10 minutes**: four game hours of guests, spread out ("about 4 an hour", so about 4 tables),
  each group about 2 to 2.5 minutes from sitting down to leaving. Then close.
- Money, hold weight and catch are rethought around the restaurant; the rest of the catch sells.
- Answers: the crew who sailed work the night; popularity goes up and down, with stars that bring more guests and
  higher prices; the fridge caps the prep but is upgradeable per tier; special requests yes; renaming yes; night
  fishing not now.
- **Mo, on the concept sheets: the game must look exactly like them** (UI, 3D, styling, movement). They are the visual
  target now, alongside the fishing view.

## 1. The day

| Phase | Where | What the player does | About |
|---|---|---|---|
| Morning | Harbour | Mira's morning note (weekday, weather, bookings). Arrange the restaurant, shop, crew, chart. | free |
| Choose the ground | Chart | Each pin shows what tonight's guests would eat if you fish there. | seconds |
| Trip out | Sea lane | Mira's plan card: guests, dishes, the catch list, special requests to accept. | 0.5-1 min |
| Fishing | Ground | Fish as now. The catch list ticks off on screen. Mira may call with a change. | 3-5 min |
| Trip home | Sea lane | The prep plan: what gets prepared for tonight, what stays whole for the market. Crew prepare it; you may fillet the special fish yourself. | 0.5-1 min |
| Arrival | Harbour, dusk | Whole fish sell at the market automatically (a short tally). | seconds |
| Service | Restaurant, 18:00-22:00 arrivals | Groups arrive spread out, the crew work their fixed jobs, you help and manage. | about 10 min |
| Closing | Restaurant | Till, reviews, popularity, leftovers to the cats, crew of the night. Sleep. | 30 s |

A full day is about 16-20 minutes. The rowboat days before Mira (tier 0) stay as they are now:
fish, sell everything at the market. The closed restaurant is already visible on the quay, shutters down.

## 2. Guests and what they order

**How many.** Tonight's guest count is rolled at departure from popularity × weekday × weather *(tune)*:
Monday quiet (×0.8), Friday and Saturday busy (×1.3), Sunday more families (groups of 4); rain ×0.85 and no terrace,
sun fills the terrace. Groups of 1-4 (later 6 for booths). The plan shows it as a rate, "about 4 groups an hour", so
you can see how many tables you need.

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

**The view** (from Codex 1's study, `docs/screens/restaurant-scale-1/`, 10-26). One orthographic camera straight
on from the front, pitched 52°, the front wall cut away like a doll's house. The study showed that on a wide phone
screen the room's depth, not its width, decides the tile size, and that a deep whole-room view never reaches 44 px
tiles. So:
- Rooms are **5 tiles deep** at every stage and grow **sideways**.
- **Low cut-away walls** (about 1 m, like PlateUp) instead of full-height walls, so the floor gets the screen.
- **Kitchen on the left, guests on the right**, with the pass as the counter between them running front to back, so it
  never hides the kitchen. The door to the quay is on the right with Mira's desk beside it; the kitchen's back door
  opens to the alley where the cats wait.
- **One view for service and for arranging.** A tile is then about 56×44 px on a phone; rooms up to 14 tiles wide need
  no pan, wider ones pan sideways only.
- Crew and guests are small on a phone (about 30-40 px), so taps go to tables, stations and bubbles, never to crew
  bodies; the staff rail handles crew.

**The grid.** 1 m tiles. Every item fills 1×1 or 2×1 tiles. Kitchen items only go in the kitchen; guest items only in
the guest area; bar items in the guest area; decor on the guest floor or the walls. The zones never mix, so the
layout always reads.

**Stages:**

| Stage | Name | Floor (kitchen part) | Opens |
|---|---|---|---|
| 1 | Café | 8×5 (3×5) | Mira joins (Skiff) |
| 2 | Bistro | 10×5 (4×5) + terrace 3×5 on the quay side | popularity 3 + coins *(tune)* |
| 3 | Restaurant | 12×5 (4×5) + terrace, knocked through into the next house | popularity 5 + coins |
| 4 | Seafood house | 14×5 (5×5) + terrace (pans sideways) | popularity 8 + coins |

Each stage also changes the building outside (Codex 2's exterior sheet), so the harbour shows your progress.

**Starting kit (stage 1, free):** stove, soup kettle, prep counter, fridge, sink, trash can, coffee machine, reception
desk with the till, two tables for 2.

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
| | Fridge | 1×1 | Holds tonight's stock, 15 portions each, upgradeable |
| | Sink and dish rack | 2×1 | Haulers wash plates here; holds the clean stack |
| | Trash can | 1×1 | Scraps; a hauler empties it into the outside container in the alley |
| Bar | Coffee machine | 1×1 | Coffee, tea (baristas, or you) |
| | Drinks fridge | 1×1 | Lemonade, beer |
| | Bar counter with stools | 2×1 | Seats solo guests and drinkers |
| Guests | Table for 2 / for 4 | 1×1 / 2×1 | Seats |
| | Booth for 6 | 2×1 | Big groups (stage 3) |
| | Terrace table | 1×1 | Outside seats (stage 2), empty in rain |
| | Reception desk with till | 1×1 | Mira's spot by the door; guests pay here (the till can break) |
| Decor | Trophy mount | wall | One of YOUR record fish, from the catch records |
| | Net with floats, lamp, plant, framed chart | 1×1 / wall | Ambience |
| | Jukebox | 1×1 | Ambience, more patience |

Ambience (decor and trophies) raises patience and tips. A chalkboard by the door shows tonight's catch automatically.

**Layout matters, gently.** Staff walk on the grid, so a stove far from the pass or tables far from the hatch costs
time. After each night Mira may give one tip ("Our waiters walked 900 m tonight. Tables nearer the hatch would help").

## 6. The night service

**Length and rhythm.** Guests arrive for four game hours, 18:00 to 22:00, about **10 minutes at ×1** (a game hour is
about 2.5 minutes) *(tune)*, with pause, ×1 and ×2. Then the door closes and service ends when the last group leaves.
Groups come **spread out, never all at once**: the plan and the clock show the rate, "about 4 groups an hour", and
because a visit takes about one game hour, that also says how many tables you need (4 an hour ≈ 4 tables in use).

**A group's visit** (about 2 to 2.5 minutes from sitting down to leaving *(tune)*):
1. They arrive and wait at the door (patience ring).
2. Mira seats them at a free, **clean** table that fits and takes their order.
3. The ticket goes to the kitchen. A cook takes the prepared fish from the fridge, finishes it (cutting, portioning),
   cooks it on the right appliance, and plates it at the pass on a clean plate.
4. A hauler carries it to the table. **Serve it within about 30 seconds** of it being plated, or it goes cold and the
   group is a little less happy (the dish is never lost).
5. They eat.
6. A hauler clears the plates: dirty plates to the sink, scraps into the nearest trash can.
7. Some want a coffee or a drink afterwards, made by a barista.
8. They pay at the till, to Mira or to you, tip by how happy they are, and leave.
9. A hauler wipes the table. Only then can the next group sit there.

**The supply lines that can jam** (PlateUp-style, all visible in the room and on the dashboard):
- **Plates.** A stack of clean plates; dirty plates pile up at the sink until a hauler washes them. No clean plates,
  no plating.
- **Trash.** Trash cans fill with scraps from the kitchen and the tables. A full can takes no more; a hauler carries
  the bag out the back door to the **outside container** in the alley (fixed, not placeable).
- **Breakdowns.** Things break quite regularly *(tune: about one every two or three minutes at stage 1, more with
  more machines)*: the oven, stove, grill, fryer, coffee machine, the till, the fridge, the sink, the lights. A broken
  item stops until the handyman fixes it, or until you hold it to fix it yourself. Upgraded machines break less.

**Satisfaction** (1-5 stars per group): wait at the door, time until the food comes, food still hot, got what they
asked for, quality (fresh today, cook level, captain's cut, special served), ambience, wait at the till. Groups that
run out of patience at the door leave; at the table they still pay, with no tip and a bad review.

### The crew at night: fixed jobs

**Who sails today works tonight**, and every card has one fixed night job. So the crew you pick in the morning has to
work for both: good fishers by day are your cooks at night, deckhands are your haulers.

| By day | At night | Does |
|---|---|---|
| Fisher | **Cook** | Finishes the prep (cutting, portioning), cooks, plates at the pass, throws kitchen scraps away |
| Deckhand | **Hauler** | Serves plates, clears and wipes tables, washes plates, empties full trash cans into the outside container |
| Engineer | **Handyman** | Repairs whatever breaks |
| Navigator (Mira) | **Host** | The face of the restaurant: seats groups, takes payment at the till |
| Ines (engineer) and Mats (deckhand), tier 4 | **Barista** | Coffee and drinks after the meal, and for guests waiting at the door |
| Captain (you) | **Helps anywhere** | Tap a task and you walk over and do it |

- Level and rarity use the one work-speed model (`docs/CARDS-AND-SPEEDS.md`); each card shows a second line, e.g.
  "Night: cook, +10% cooking speed". Card abilities get night twins later (R6).
- Before the baristas join (tier 4), after-meal drinks only happen if you make them yourself (a cup bubble on the
  coffee machine).
- The arc: at the café you do a lot yourself (Mira, one crew member and you); with every bigger boat you bring more
  crew, so the night runs itself more and you become the manager. The same automation idea as on the boat.
- Crew who stayed ashore don't work in v1.

### What the manager does

1. **Pick the crew in the morning** with the night in mind. The biggest decision of the day.
2. **Set priorities on the dashboard** (section 10, S6), like the boat's: each hauler's order of jobs (serve, clear,
   wash, trash), each cook's order (oldest ticket first or the biggest table first), Mira's (seat first or the till
   first). "Sam on dishes and trash first, Ana on serving" is the core management decision.
3. **Help where it hurts.** Tap a task (a plate waiting at the pass, a dirty table, a full trash can, a broken
   machine, a group at the till, a cup bubble) and the captain goes. A short queue of up to three taps.
4. **Decide:** a late group at the door (seat them / not tonight), a sold-out dish (offer soup / another fish / a free
   coffee; soup by itself after a few seconds), a special or a VIP.
5. **Close the door** early when the fridge is empty.

**Events** (light, a few per night, from R4): a birthday table, the alley cat sneaking in, a tour group of 6, a
regular with a favourite dish, rain moving terrace guests inside, and later the food critic.

## 7. Closing

A closing card: groups served (and any who left), coins from dishes, drinks and tips, the total; three review cards
with stars and a funny line ("The mackerel was so fresh it winked at me"); popularity and stars; leftovers
("3 portions went to the alley cats", the cats eating out back, the lost value greyed); crew of the night; Mira's
personal line. Then **Sleep** → next morning.

**Popularity goes up and down** with how happy the guests were. The restaurant's **stars (1 to 5)** follow popularity
with a buffer, so one bad night doesn't cost a star. Each star brings more guests an hour **and higher prices**
*(tune: about +10% per star)*, brings new guest types (tourists, fishermen's groups, the critic) and opens the stages.

## 8. Economy

Direction (numbers come from the pacing sim, `docs/plans/CARDS-PACING.md`, rerun with the restaurant):
- **The restaurant is the money maker.** A dish earns about 3× its raw fish *(tune)*, plus drinks, tips and the star
  bonus. The market pays about half of today's prices for whole fish.
- **The day's target is tonight's catch list, not a full hold.** When the list is complete, "Head home" lights up.
  Whatever else you catch sells at the market, so staying out longer still pays a little.
- **Bigger boats still matter:** more berths mean more crew at night (the restaurant's capacity), new grounds bring
  pricier fish and specials, and a bigger hold carries more for the market and for bigger nights.
- **Fridges are upgradeable** so each tier's night always fits; the fridge never becomes a chore.
- Restaurant items, stages and machine upgrades are a new coin sink; boat, chart and crew prices are rebalanced.
- Crew tokens (today: tier × crew × fill, +15% for a full hold) should follow the night instead: tier × crew × how
  well the night went, +15% for a full house *(to confirm with Mo)*.
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
free valid tile in its zone; drag it (it floats about 60 px above the finger, its footprint lit on the floor, and snaps to tiles); rotate and ✓/✗ float next to it;
you pay on ✓. Tap a placed item to lift it: drag, rotate, store, or sell back. Invalid spots show red with one short
reason ("Kitchen items go in the kitchen", "Leave a way to the door"). A path check keeps door → every table and pass →
every appliance open. Dragging on empty floor pans sideways when the room is wider than the screen (stage 4 with its terrace).

**S2 Service HUD.** Top: the evening clock (18:00-22:00) as a strip with the arrival curve, "about 4 an hour" and a
now-marker, coins tonight, stars, speed (pause, ×1, ×2), a dashboard button. Left: tonight's stock, one plate icon per
dish with its count, red when low. Bottom: the staff rail, crew portraits with their fixed job (Cook, Hauler, Fix,
Barista, Host), their current task and a busy ring; tap one for its priorities. In the room: guests' bubbles (order
icon and patience ring), plates at the pass with a 30-second ring, dirty tables, full trash cans and broken items
marked as tap targets for the captain, event cards sliding in from the right with Mira's face and two buttons.

**S6 Dashboard** (like the boat's management screen; the game pauses or slows while it's open). The guest journey as
a row of steps with live average times: door → seated, seated → food out, pass → table, eating, waiting to pay, table
dirty → clean. The slowest step glows, with the job behind it and a hint ("Plates are piling up at the sink: put Sam
on dishes first"). Per crew: busy %, current task, and their priority list to reorder.

**S3 Mira's plan card** (trip out). Mira on the left. "Tonight: Friday, 18-22 guests (plus a few walk-ins)". The
dishes they'll want as icons with ranges. The catch list in fish ("about 8 mackerel, 3 kg pollock"). Special request
cards with Accept / Not tonight. "Got it". While fishing, the catch list shrinks to a ticket pinned at the screen edge
("Mackerel 5/8").

**S4 Prep plan** (trip home). Section 4: catch on the left, portions per dish with steppers and forecast markers on
the right, margin choice, fridge space, the restaurant/market totals, "Prepare", and the optional captain's cut.

**S5 Closing card.** Section 7.

## 11. Not in v1 (TODO)

Restaurant outfits for the crew (2D and 3D), passive restaurant income (later idea: the restaurant runs on its own
at night with the crew who stayed ashore while the captain goes night fishing with others), card abilities' restaurant twins, shore staff
slots, critic stars, smoker, live tank, more dishes per fish (a recipe book), night fishing (see below).

**Night fishing** is half built and never reachable: `GameState.NightVoyage`, night fish pools in `Data/Grounds.cs`,
the Jig boat's lamps and night abilities exist, but nothing in the game starts a night trip. With nights in the
restaurant, it stays parked. A later option: "closed tonight, gone fishing" for special night trips.

## 12. Build order

| Slice | Content | Who |
|---|---|---|
| R0 | Concepts: look options, exterior stages, interiors, item kit, service moment, UI mockups (Codex 2); camera and room-size study (Codex 1). Mo picks the look. | now |
| R1 | The restaurant in the harbour: building (closed → café), go in and out, interior view with grid and zones, arrange mode with shop and placement, layout saved. No service yet. | |
| R2 | Service core: groups spread over the night, Mira seating and the till, cooks, haulers (serve, clear, wipe, plates, trash), handyman and breakdowns, the 30-second rule, the captain helping, closing card; staff = today's crew with fixed jobs; staff rail and dashboard. | |
| R3 | The day plan: forecast, chart pins, Mira's plan card, the ticket and her calls while fishing, the prep plan, market sale of the rest, leftovers to the cats. | |
| R4 | Events, stars, stages 2-4, baristas, machine upgrades, the rest of the items. | |
| R5 | Economy rebalance with the pacing sim, the first-night tutorial and Mira's story, the Mira message pass. | |
| R6 | Later list (section 11). | |

Technical shape: the service is a pure logic simulation (`RestaurantSim`, tickable headless, with editor checks and a
pacing-sim hook) and the 3D room follows it, like the deck simulation. Tile pathfinding on a grid of at most 17×5.
Staff reuse the crew rigs and animations (walk, carry, the prep table's work loop). Layout, stage, popularity and the
day counter live in a new save block.

## 13. Decided (Mo, 10-26 evening)

1. The second barista is Mats (tier 4 deckhand), with Ines.
2. Economy direction of section 8 approved (tonight's list is the target, the rest sells, tokens from the night).
3. Exterior look 01, whitewashed stone with blue shutters.
4. The UI must match the concept mockups; the 3D as close as possible to the sheets, with animation and the same
   cosiness. Claude builds the UI; Codex 2 leads the Blender work; Codex 1 the logic.
5. The night runs 18:00-23:00 (as the mockups), still about 10 real minutes.
6. Temporary UI pieces may be cut from the mockups until Codex's clean art lands (list: Art/Source/Restaurant/ui-TEMP-CROPS.md).
7. Staff rail: one card per person cannot fit 5-8 crew plus Mira and the baristas. Mo leans to small portrait chips grouped
   by job; three variants (per job / per person scrolling / chips) are captured for him to choose
   (docs/screens/restaurant-ui/r6/restaurant-service-{jobs,scroll,chips}-*.png).

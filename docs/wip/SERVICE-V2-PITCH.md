# Service v2: a night you play, not watch (pitch, 10-28)

Mo: "rethink the damn system, this is so slow... we must serve a lot more customers... unplanned ones all over...
nothing happens, there's nothing we can do in the meantime... this is a mobile game, no point in waiting 2 minutes
for something to happen, we need to do magnitudes better."

## Why tonight's service is boring (measured from RestaurantSim/RestaurantTuning)

- A night is 600 s with about 18 guests (BaseGuests 18), all booked in advance: one arrival every ~30 s.
- A group sits for 95 s eating (EatSeconds) and may wait 180 s for food (TablePatience). Most of the screen is still.
- The staff do every task themselves. The player can only seat, pin a table, pick a swap dish, or fix a station.
- The 1x/2x speed buttons are the tell: when a player wants to skip your gameplay, it is waiting.

## What the genre teaches

- **PlateUp**: you are the hands (carry, cook, plate, serve, wash); a day is a few minutes with 20-30 customers
  early and 80+ late; each customer phase has its own patience bar; between days you pick upgrade/customer cards
  that make the next day harder and richer; automation is something you build, so there is always a gap you fill.
- **Arcade idle (Burger Please!, Pizza Ready!, My Perfect Hotel)**: the avatar runs between stations carrying a
  stack; every hire automates one lane (cashier, carrier, cleaner) but is slower than you; cleaning a table and
  serving both pay at once, so every second of walking is rewarded.
- **Cooking Fever / Diner Dash**: food cooks in seconds; tap-tap-tap queues actions the character performs in order;
  serving several things in one trip and matching the right order give combo tips; things burn if you ignore them.
- **Eatventure**: helpers come for short bursts; upgrades visibly halve cook times; nothing takes long.

## The pitch

1. **A night is about 3 minutes of nonstop play** (door open 180 s, then last orders): think 3 s, order 2 s,
   cook 4-8 s, eat 10-12 s, pay 2 s. Patience: door 20 s, order 15 s, food 35 s, all visible as rings.
2. **Walk-ins all night.** Mira's bookings are the big fish tables (her plan, the catch, the money). On top, walk-ins
   stream in from the pier every 4-8 s, more as the night's stars climb (a good night snowballs). Walk-ins mostly
   order the quick menu (fries, bread, soup from the offcuts, drinks), so the kitchen is never idle even when the
   fish runs out, and the catch stays the premium. Target: 25-35 guests on night 1, 80-120 at the Seafood house.
3. **The captain is your hands.** Tap a table, the pass, a station, the sink: he runs there and does it. Taps queue
   up (three ahead) so you plan a route. He carries 2 plates (upgrades to 4). Serving two tables in one trip, or
   clearing and seating in one go, is a combo with a tip burst.
4. **Crew are automation, and slower than you.** Each hire takes one lane (Mira seats and takes orders, a waiter
   carries, a cook cooks, a pot-washer washes). Early nights it is you and Mira; later the crew run the floor and
   you jump on whatever is about to blow (a VIP, a burning grill, a gull on the terrace).
5. **Always something to do between the big jobs**: dirty plates go to the sink and clean plates run out if nobody
   washes; a gull lands on a terrace plate (tap it away); drinks, coffee and dessert bubbles pop over tables for a
   few seconds (tap for a quick sale); a spill to mop; a grill the captain cooks has a perfect window (tap on the
   glow: better plate, bigger tip; ignore it and it burns).
6. **Harbour moments** Mira calls on the radio: the ferry docks and twelve walk-ins arrive at once; a food critic
   (one table, triple stars); fishermen asking for tonight's catch of the day (your rarest fish, a huge tip).
7. **Stars, not failure.** A walkout cracks one of three stars; lose all three and the night closes early with what
   you earned. The night's tips fill a "Full house" bar that pays a bonus.
8. **Between nights: pick 1 of 3 cards** (our flavour of PlateUp's): a dish, a gadget (plate rack, warming lamp, a
   second grill), or a night modifier with a payout (Ferry night +40% guests, Critics' week, Rain: indoor only).
9. **No speed buttons.** The night is already fast; pause stays.

## Order of work

- A (Claude, now): retime the sim and add the walk-in stream; captain direct control with the tap queue, carry
  stack and combos; per-phase patience rings in the room. Codex 2 is making the missing dishes, plate stacks,
  sink piles, gull and spill (SERVICE-PROPS-1). Codex 1 is building the pier and harbour around the room
  (RESTAURANT-PIER-1).
- B: sink and plates, gulls, upsell bubbles, perfect-grill timing.
- C: night cards, ferry rush, critic, catch of the day.

## Status (10-28, playable)

- Done (A): 240 s night, door shuts at 180 s; walk-ins every ~6 s (gentler on the first night); four tables, ten seats
  on the starter cafe; cook "load and leave" with dishes visible on the stations and plates at the pass; the captain
  as the player's hands (tap queue of three, numbered badges); 2-plate combo tips. Codex 1's pier, quay and harbour
  around the room. The 1x/2x buttons became the night clock.
- Done (B): upsell bubbles (tap a waving table to sell a round on the spot); gulls (tap to shoo, ignored they steal
  and the table loses a star).
- Headless proof, ServiceV2Checks (starter cafe, Mira + captain): a quick tapper serves 30 of 44 guests for ~480
  coins with 10 upsells; with no taps nobody is served.
- Next: SERVICE-PROPS-2 (Codex 2: food cooking on each station, tip coins, catch board, ferry) and SERVICE-UI-KIT-4
  (Codex 1: v3 service icons) to wire in; then perfect-grill timing, tip coins collected on clearing, night cards.

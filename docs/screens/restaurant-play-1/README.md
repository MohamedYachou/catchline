# Restaurant core: headless service reports

Provisional tuning; no production wiring. Fixed 0.25 s ticks; random breakdowns disabled in pacing comparisons (separate repair checks). Each scenario uses its declared seed.

| Scenario | Seed | Guests | Served | Left | Dishes | Drinks | Tips | Staple cost | Net | Stars | Cats | Seconds | Metres |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Stage 1 / Skiff | 100 | 28 | 8 | 20 | 106 | 28 | 10 | 9 | 135 | 1.93 | 7 | 600.00 | mira 12.0; captain 237.0 |
| Stage 2 / Compact fisher | 101 | 32 | 16 | 16 | 204 | 137 | 14 | 36 | 319 | 2.13 | 20 | 600.00 | mira 70.0; cook0 88.0; waiter0 108.0; waiter1 58.0; barista 166.0 |
| Stage 3 / Prep fisher | 102 | 34 | 20 | 14 | 277 | 131 | 22 | 40 | 390 | 2.65 | 18 | 600.00 | mira 130.0; cook0 120.0; cook1 28.0; waiter0 196.0; waiter1 65.0; waiter2 39.0; barista 234.0 |
| Stage 4 / Buoy fisher | 103 | 46 | 24 | 22 | 305 | 148 | 24 | 38 | 439 | 2.35 | 27 | 600.00 | mira 142.0; cook0 150.0; cook1 16.0; cook2 0.0; waiter0 261.0; waiter1 118.0; waiter2 14.0; barista 321.0; engineer 0.0 |
| Under-prepped (stage3) | 102 | 34 | 6 | 28 | 96 | 131 | 4 | 58 | 173 | 1.24 | 0 | 600.00 | mira 146.0; cook0 60.0; cook1 14.0; waiter0 104.0; waiter1 40.0; waiter2 10.0; barista 236.0 |
| Over-prepped (stage3) | 102 | 34 | 27 | 7 | 359 | 131 | 36 | 33 | 493 | 3.59 | 33 | 600.00 | mira 130.0; cook0 132.0; cook1 28.0; waiter0 222.0; waiter1 71.0; waiter2 39.0; barista 234.0 |

PLAY-1 rules: 600 seconds, 18-22 arrivals and 23 closing; stage1 Mira + one captain helper. Fixed card roles; cold after 30s, payment at till, repairable breakdowns and 1-5 stars. Plates/sink/trash are simplified to clearing, not finite supply lines. Other report stages use specialists at their native jobs. No player-save/UI integration claimed.

Integration API: standalone RestaurantState + RestaurantLayout; forecast takes ground weighted (Species, weight) pairs, exposes copied guests and ranges, supports MiraChange/SpecialRequest/Lock. RestaurantPortions.Suggest produces fridge stock and untouched market fish. RestaurantSim.Tick accepts elapsed seconds, fixed steps internally; SetJob, Pin, Seat, CloseDoor, ChooseSubstitute, Break, CaptainHoldFix are manager commands. Busy staff finish their accepted task before taking the new role. RunToClose is the headless runner. Result includes gross/net split and each staff distance.

Layout expansion inserts kitchen columns at the pass and shifts guest-side items together, preserving every UID and relative guest positions. Existing items are never sold or lost. Terrace width is3 at stages2-4. Access tiles are the nearest reachable cardinal neighbours of footprints; table access represents all chairs (no separate chair occupancy in v1). Wall fixtures share floor tiles; the vertical pass has a front aisle crossing. Layout must remain fixed during service.

Tuning defaults live only in RestaurantTuning. Plan-defined values: 600s night, 8 soup/batch, 15 portions/fridge, fixed jobs, half-price market, dish3x raw, growth20%, walk-ins10%, portion yields. Unspecified timings, prices, forecast slack, stock offcut mass20%, base guests/popularity, stars/tips and failure probability are provisional and require lead/pacing review. No finite plates/sink/trash, events, critic, ability twins, live save integration or UI.

[View evidence](view/README.md), [check details](checks.txt), [machine reports](nights.json). Existing regression status is in regression-passed.txt only after that suite completes.

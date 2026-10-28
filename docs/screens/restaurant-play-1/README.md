# Restaurant core: headless service reports

Provisional tuning; no production wiring. Fixed 0.25 s ticks; random breakdowns disabled in pacing comparisons (separate repair checks). Each scenario uses its declared seed.

| Scenario | Seed | Guests | Served | Left | Dishes | Drinks | Tips | Staple cost | Net | Stars | Cats | Seconds | Metres |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Stage 1 / Skiff | 100 | 28 | 17 | 11 | 126 | 68 | 15 | 30 | 179 | 3.36 | 7 | 240.00 | mira 12.0; captain 517.0 |
| Stage 2 / Compact fisher | 101 | 50 | 36 | 14 | 234 | 174 | 31 | 73 | 366 | 3.88 | 5 | 240.00 | mira 192.0; cook0 58.0; waiter0 232.0; waiter1 117.0; barista 286.0 |
| Stage 3 / Prep fisher | 102 | 54 | 40 | 14 | 336 | 165 | 31 | 77 | 455 | 3.44 | 0 | 240.00 | mira 266.0; cook0 66.0; cook1 35.0; waiter0 286.0; waiter1 192.0; waiter2 51.0; barista 434.0 |
| Stage 4 / Buoy fisher | 103 | 61 | 44 | 17 | 424 | 177 | 41 | 73 | 569 | 3.46 | 1 | 240.00 | mira 326.0; cook0 85.0; cook1 31.0; cook2 14.0; waiter0 313.0; waiter1 168.0; waiter2 136.0; barista 467.0; engineer 0.0 |
| Under-prepped (stage3) | 102 | 56 | 42 | 14 | 189 | 184 | 15 | 96 | 292 | 3.29 | 1 | 240.00 | mira 286.0; cook0 36.0; cook1 2.0; waiter0 340.0; waiter1 202.0; waiter2 93.0; barista 410.0 |
| Over-prepped (stage3) | 102 | 50 | 46 | 4 | 546 | 161 | 59 | 51 | 715 | 4.52 | 24 | 240.00 | mira 266.0; cook0 132.0; cook1 29.0; waiter0 338.0; waiter1 185.0; waiter2 93.0; barista 422.0 |

PLAY-1 rules: 600 seconds, 18-22 arrivals and 23 closing; stage1 Mira + one captain helper. Fixed card roles; cold after 30s, payment at till, repairable breakdowns and 1-5 stars. Plates/sink/trash are simplified to clearing, not finite supply lines. Other report stages use specialists at their native jobs. No player-save/UI integration claimed.

Integration API: standalone RestaurantState + RestaurantLayout; forecast takes ground weighted (Species, weight) pairs, exposes copied guests and ranges, supports MiraChange/SpecialRequest/Lock. RestaurantPortions.Suggest produces fridge stock and untouched market fish. RestaurantSim.Tick accepts elapsed seconds, fixed steps internally; SetJob, Pin, Seat, CloseDoor, ChooseSubstitute, Break, CaptainHoldFix are manager commands. Busy staff finish their accepted task before taking the new role. RunToClose is the headless runner. Result includes gross/net split and each staff distance.

Layout expansion inserts kitchen columns at the pass and shifts guest-side items together, preserving every UID and relative guest positions. Existing items are never sold or lost. Terrace width is3 at stages2-4. Access tiles are the nearest reachable cardinal neighbours of footprints; table access represents all chairs (no separate chair occupancy in v1). Wall fixtures share floor tiles; the vertical pass has a front aisle crossing. Layout must remain fixed during service.

Tuning defaults live only in RestaurantTuning. Plan-defined values: 600s night, 8 soup/batch, 15 portions/fridge, fixed jobs, half-price market, dish3x raw, growth20%, walk-ins10%, portion yields. Unspecified timings, prices, forecast slack, stock offcut mass20%, base guests/popularity, stars/tips and failure probability are provisional and require lead/pacing review. No finite plates/sink/trash, events, critic, ability twins, live save integration or UI.

[View evidence](view/README.md), [check details](checks.txt), [machine reports](nights.json). Existing regression status is in regression-passed.txt only after that suite completes.

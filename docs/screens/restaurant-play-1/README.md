# Restaurant core: headless service reports

Provisional tuning; no production wiring. Fixed 0.25 s ticks; random breakdowns disabled in pacing comparisons (separate repair checks). Each scenario uses its declared seed.

| Scenario | Seed | Guests | Served | Left | Dishes | Drinks | Tips | Staple cost | Net | Stars | Cats | Seconds | Metres |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Stage 1 / Skiff | 100 | 21 | 15 | 6 | 173 | 68 | 23 | 27 | 237 | 3.86 | 4 | 240.00 | mira 16.0; captain 523.0 |
| Stage 2 / Compact fisher | 101 | 42 | 34 | 8 | 260 | 183 | 24 | 75 | 392 | 3.81 | 3 | 240.00 | mira 158.0; cook0 76.0; waiter0 218.0; waiter1 118.0; barista 292.0 |
| Stage 3 / Prep fisher | 102 | 53 | 39 | 14 | 273 | 190 | 27 | 89 | 401 | 3.53 | 4 | 240.00 | mira 306.0; cook0 58.0; cook1 16.0; waiter0 290.0; waiter1 152.0; waiter2 56.0; barista 402.0 |
| Stage 4 / Buoy fisher | 103 | 49 | 33 | 16 | 348 | 180 | 27 | 67 | 488 | 3.12 | 4 | 240.00 | mira 268.0; cook0 73.0; cook1 31.0; cook2 8.0; waiter0 267.0; waiter1 115.0; waiter2 47.0; barista 422.0; engineer 0.0 |
| Under-prepped (stage3) | 102 | 51 | 40 | 11 | 183 | 198 | 14 | 97 | 298 | 3.59 | 1 | 240.00 | mira 260.0; cook0 36.0; cook1 2.0; waiter0 306.0; waiter1 163.0; waiter2 66.0; barista 420.0 |
| Over-prepped (stage3) | 102 | 45 | 45 | 0 | 475 | 188 | 49 | 59 | 653 | 4.64 | 27 | 240.00 | mira 264.0; cook0 84.0; cook1 34.0; waiter0 300.0; waiter1 179.0; waiter2 118.0; barista 376.0 |

PLAY-1 rules: 600 seconds, 18-22 arrivals and 23 closing; stage1 Mira + one captain helper. Fixed card roles; cold after 30s, payment at till, repairable breakdowns and 1-5 stars. Plates/sink/trash are simplified to clearing, not finite supply lines. Other report stages use specialists at their native jobs. No player-save/UI integration claimed.

Integration API: standalone RestaurantState + RestaurantLayout; forecast takes ground weighted (Species, weight) pairs, exposes copied guests and ranges, supports MiraChange/SpecialRequest/Lock. RestaurantPortions.Suggest produces fridge stock and untouched market fish. RestaurantSim.Tick accepts elapsed seconds, fixed steps internally; SetJob, Pin, Seat, CloseDoor, ChooseSubstitute, Break, CaptainHoldFix are manager commands. Busy staff finish their accepted task before taking the new role. RunToClose is the headless runner. Result includes gross/net split and each staff distance.

Layout expansion inserts kitchen columns at the pass and shifts guest-side items together, preserving every UID and relative guest positions. Existing items are never sold or lost. Terrace width is3 at stages2-4. Access tiles are the nearest reachable cardinal neighbours of footprints; table access represents all chairs (no separate chair occupancy in v1). Wall fixtures share floor tiles; the vertical pass has a front aisle crossing. Layout must remain fixed during service.

Tuning defaults live only in RestaurantTuning. Plan-defined values: 600s night, 8 soup/batch, 15 portions/fridge, fixed jobs, half-price market, dish3x raw, growth20%, walk-ins10%, portion yields. Unspecified timings, prices, forecast slack, stock offcut mass20%, base guests/popularity, stars/tips and failure probability are provisional and require lead/pacing review. No finite plates/sink/trash, events, critic, ability twins, live save integration or UI.

[View evidence](view/README.md), [check details](checks.txt), [machine reports](nights.json). Existing regression status is in regression-passed.txt only after that suite completes.

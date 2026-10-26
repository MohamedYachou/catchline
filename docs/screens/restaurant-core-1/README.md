# Restaurant core: headless service reports

Provisional tuning; no production wiring. Fixed 0.25 s ticks; random breakdowns disabled in pacing comparisons (separate repair checks). Each scenario uses its declared seed.

| Scenario | Seed | Guests | Served | Left | Dishes | Drinks | Tips | Staple cost | Net | Stars | Cats | Seconds | Metres |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Stage 1 / Skiff | 100 | 13 | 5 | 8 | 59 | 20 | 7 | 5 | 81 | 1.69 | 10 | 248.75 | mira 21.0; noor 14.0; sam 83.0 |
| Stage 2 / Compact fisher | 101 | 20 | 9 | 11 | 111 | 106 | 7 | 32 | 192 | 1.45 | 14 | 240.00 | mira 53.0; cook0 44.0; waiter0 86.0; waiter1 35.0; barista 108.0 |
| Stage 3 / Prep fisher | 102 | 27 | 16 | 11 | 224 | 94 | 15 | 32 | 301 | 1.67 | 14 | 247.00 | mira 98.0; cook0 60.0; cook1 56.0; waiter0 124.0; waiter1 96.0; waiter2 52.0; barista 175.0 |
| Stage 4 / Buoy fisher | 103 | 41 | 18 | 23 | 227 | 81 | 11 | 22 | 297 | 1.34 | 28 | 240.00 | mira 116.0; cook0 54.0; cook1 30.0; cook2 14.0; waiter0 149.0; waiter1 84.0; waiter2 55.0; barista 226.0; engineer 0.0 |
| Under-prepped (stage3) | 102 | 27 | 6 | 21 | 96 | 94 | 4 | 42 | 152 | 1.15 | 0 | 245.00 | mira 98.0; cook0 44.0; cook1 30.0; waiter0 118.0; waiter1 66.0; waiter2 19.0; barista 175.0 |
| Over-prepped (stage3) | 102 | 27 | 22 | 5 | 280 | 86 | 20 | 22 | 364 | 1.93 | 38 | 246.50 | mira 104.0; cook0 72.0; cook1 42.0; waiter0 138.0; waiter1 102.0; waiter2 102.0; barista 157.0 |

Staff counts including Mira: 3 / 5 / 7 / 9. Stages 2-4 use 4 / 6 / 8 sailed crew plus Mira per brief's stage-1 convention. Generic crew are White level1; Mira Gold level1. Boat capacities are not changed. Stage1 has two seats per table: groups of3/4 may leave; table combining is R4. Soup uses prepared stock, never infinite free fish. One platter is one prepared unit for the table.

Design revision notice: this delivery follows the explicit RESTAURANT-CORE-1 brief baseline (240s night, assignable jobs, no plates/sink). The plan changed during work: 600s / 18-22 arrivals, fixed card jobs, haulers, plates/trash, cold food, till tasks, captain task queue and dashboard priorities are newer requirements and are NOT implemented here. Do not wire this baseline into the current design without a follow-up. No existing C# integration edits are needed for this standalone delivery.

Integration API: standalone RestaurantState + RestaurantLayout; forecast takes ground weighted (Species, weight) pairs, exposes copied guests and ranges, supports MiraChange/SpecialRequest/Lock. RestaurantPortions.Suggest produces fridge stock and untouched market fish. RestaurantSim.Tick accepts elapsed seconds, fixed steps internally; SetJob, Pin, Seat, CloseDoor, ChooseSubstitute, Break, CaptainHoldFix are manager commands. Busy staff finish their accepted task before taking the new role. RunToClose is the headless runner. Result includes gross/net split and each staff distance.

Layout expansion inserts kitchen columns at the pass and shifts guest-side items together, preserving every UID and relative guest positions. Existing items are never sold or lost. Terrace width is3 at stages2-4. Access tiles are the nearest reachable cardinal neighbours of footprints; table access represents all chairs (no separate chair occupancy in v1). Wall fixtures share floor tiles; the vertical pass has a front aisle crossing. Layout must remain fixed during service.

Tuning defaults live only in RestaurantTuning. Plan-defined values: 240s night, 8 soup/batch, 15 portions/fridge, 70% other job, half-price market, dish3x raw, growth20%, walk-ins10%, portion yields. Unspecified timings, prices, forecast slack, stock offcut mass20%, base guests/popularity, stars/tips and failure probability are provisional and require lead/pacing review. No R4 dishes/sink, events, critic, ability twins, live save integration or UI.

[View evidence](view/README.md), [check details](checks.txt), [machine reports](nights.json). Existing regression status is in regression-passed.txt only after that suite completes.

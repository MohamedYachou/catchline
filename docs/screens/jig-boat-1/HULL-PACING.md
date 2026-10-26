# Hull pacing with the inserted Jig step

Skiff is the experiment starting hull (day1), not a measured purchase. Values are median [p10,p90] over200 seeds; >180 is right-censored. The retained chest-first spending policy and full free deployment are specified in [the full report](cards-pacing-generated.md). No economy constants were changed.

| Chest price | Trips/day | Compact | Jig | Prep | Buoy |
|---:|---:|---|---|---|---|
| 400 | 2 | >180 [>180, >180] | >180 [>180, >180] | >180 [>180, >180] | >180 [>180, >180] |
| 400 | 5 | >180 [>180, >180] | >180 [>180, >180] | >180 [>180, >180] | >180 [>180, >180] |
| 400 | 10 | >180 [>180, >180] | >180 [>180, >180] | >180 [>180, >180] | >180 [>180, >180] |
| 2000 | 2 | 4 [4, 4] | 7 [6, 7] | 8 [8, 9] | >180 [>180, >180] |
| 2000 | 5 | 2 [2, 2] | 3 [3, 3] | 4 [3, 4] | >180 [>180, >180] |
| 2000 | 10 | 1 [1, 1] | 2 [2, 2] | 2 [2, 2] | >180 [>180, >180] |
| 3000 | 2 | 4 [4, 4] | 7 [6, 7] | 8 [8, 9] | >180 [>180, >180] |
| 3000 | 5 | 2 [2, 2] | 3 [3, 3] | 4 [3, 4] | >180 [>180, >180] |
| 3000 | 10 | 1 [1, 1] | 2 [2, 2] | 2 [2, 2] | >180 [>180, >180] |
| 6000 | 2 | 4 [4, 4] | 7 [6, 7] | 8 [8, 9] | 11 [10, 11] |
| 6000 | 5 | 2 [2, 2] | 3 [3, 3] | 4 [3, 4] | 4 [4, 5] |
| 6000 | 10 | 1 [1, 1] | 2 [2, 2] | 2 [2, 2] | 2 [2, 3] |

At baseline400, the simulator buys sea chests while cash exceeds3xprice. That drains savings before the4000-coin Compact threshold; no baseline seed leaves Skiff. At2000/3000/6000 the reserve grows and hulls become reachable. These are conditional policy results, not a claim that normal play cannot progress. The real refit sequence independently passed focused checks. Lead question: should a future pacing policy protect hull savings? This delivery does not alter economy or the established spending policy.

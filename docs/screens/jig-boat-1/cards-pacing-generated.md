# Crew card pacing — measured real API

200 seeds (1..200) per profile, 180 days, 2/5/10 trips daily. Focus Noor from White level 1; Mira excluded from focus progression. GrantTrialCards at every hull fills the unlocked roster for free (welcome reward removed); this isolates progression with full deployments and DOES NOT measure recruitment time or cost. All rarity/level/star costs and reward rolls use GameState APIs. No save is read or written. No game data source is edited.

Start already owning tier-1 Skiff, default StartCoins, no other equipment. Refit costs come from live constants (Compact 4000, Jig 6500, Prep 9500, Buoy 18000). Retain the prior experiment's optional BigCooler purchase at tier2 (3000); it persists on later hulls. Jig's130kg hold can clear the100kg Prep gate without it. The real CardTier path is 1/2/3/4/5, with saved Jig ID5 mapped to tier3. Hull days below emerge from actual cash, not invented unlock dates.

Income assumption: each trip's target fill is uniform[0.6,1.0); fill each hold with equal draws of eligible Herring/Mackerel/Pollock/SeaBass/Cod, weight uniform within real species limits. Last fish is clipped to remaining target kg (synthetic haul approximation). Sell at time0 (fresh), with real specimen prices; no rare jackpot, depletion, catch-time, ability productivity, gear upgrades or contract cash. Deduct real wages and an assumed10coins/trip fuel/bait reserve. These are conditional economy estimates, not a one-hour gameplay measurement.

Working capital: level spending keeps departure wages +20coins; hull purchases retain the next deployment wages +10coins. Policy per return: real Sell; AwardHaulTokens using departure deployment; daily crate deduplicated by simulated date; one contract crate every third day. Open all chests, focus-level before rank/stars, claim renown immediately to Noor (after maxing, unused choices go to another eligible card), repeat to convergence. Then buy the next affordable hull/cooler, then repeatedly buy sea chests while coins exceed3xprice, settling after each. Other cards stay at starting rarity/level; deploy navigator then roster order to all real berths. No prestige. Separate seeded fill/income and chest RNG streams; same seeds per scenario, but hull timing can change with costs/rewards.

## Baseline

Days are median [p10, p90], nearest-rank over all 200 seeds; >180 is right censored, never omitted.
| Profile | Purple | Gold | Mythic level 30 | Mythic 5 stars | Mythic reached by 180 |
|---|---:|---:|---:|---:|---:|
| casual | 20 [11, 33] | 39 [29, 58] | 71 [56, 95] | >180 [154, >180] | 200/200 |
| regular | 9 [5, 15] | 19 [13, 26] | 33 [26, 41] | 86 [73, 101] | 200/200 |
| heavy | 6 [3, 8] | 10 [7, 14] | 18 [13, 23] | 45 [39, 54] | 200/200 |

| Profile | Road milestone day 30 / 60 / 180 (median) | Renown day 30 / 60 / 180 (median) | Tier 2 / 3 / 4 / 5 days (median [p10,p90]) |
|---|---|---|---|
| casual | 4 / 5 / 7 | 37 / 52 / 97 | >180 [>180, >180] / >180 [>180, >180] / >180 [>180, >180] / >180 [>180, >180] |
| regular | 5 / 7 / 8 | 52 / 87 / 107 | >180 [>180, >180] / >180 [>180, >180] / >180 [>180, >180] / >180 [>180, >180] |
| heavy | 7 / 8 / 8 | 87 / 107 / 107 | >180 [>180, >180] / >180 [>180, >180] / >180 [>180, >180] / >180 [>180, >180] |

180-day means (tokens earned and spent are exact per-run reconciled ledgers):
| Profile | Haul tokens | Chest tokens | Road tokens | Total earned | Spent | Banked | Chests / sea chests | Dropped BP / focused BP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| casual | 405.8 | 10521.6 | 80.0 | 11007.4 | 2579.0 | 8428.4 | 528.2 / 286.2 | 33.7 / 26.6 |
| regular | 1013.2 | 25205.8 | 80.0 | 26299.0 | 2579.0 | 23720.0 | 1017.7 / 775.7 | 76.7 / 29.0 |
| heavy | 2024.0 | 49630.0 | 80.0 | 51734.0 | 2579.0 | 49155.0 | 1831.8 / 1589.8 | 147.3 / 29.0 |

| Profile | Gross sale coins | Wages | Operating reserve | Hulls + cooler | Levels | Sea chests | Ending coins |
|---|---:|---:|---:|---:|---:|---:|---:|
| casual | 247238.4 | 14215.4 | 3600.0 | 0.0 | 28355.0 | 199342.5 | 1765.6 |
| regular | 617880.8 | 37262.8 | 9000.0 | 0.0 | 28355.0 | 541562.0 | 1741.0 |
| heavy | 1235399.8 | 75884.5 | 18000.0 | 0.0 | 28355.0 | 1111460.0 | 1740.3 |

Blocked post-spend trip observations by current rank, pooled across seeds. Coin/token counters can overlap; blueprint waits count only at level cap. These identify the next progression gate, not a causal economic elasticity test.
| Profile | Current rank -> next | Coin | Tokens | Blueprints | Dominant gate |
|---|---|---:|---:|---:|---|
| casual | White -> Green | 0 | 586 | 0 | tokens |
| casual | Green -> Blue | 0 | 775 | 1615 | blueprints |
| casual | Blue -> Purple | 244 | 1094 | 4063 | blueprints |
| casual | Purple -> Gold | 1120 | 740 | 6513 | blueprints |
| casual | Gold -> Mythic | 7502 | 3091 | 4508 | coins |
| casual | Mythic -> 5 stars | 0 | 0 | 40178 | blueprints |
| regular | White -> Green | 0 | 564 | 0 | tokens |
| regular | Green -> Blue | 0 | 797 | 2149 | blueprints |
| regular | Blue -> Purple | 351 | 1073 | 4551 | blueprints |
| regular | Purple -> Gold | 1167 | 696 | 7837 | blueprints |
| regular | Gold -> Mythic | 7623 | 3071 | 6019 | coins |
| regular | Mythic -> 5 stars | 0 | 0 | 53336 | blueprints |
| heavy | White -> Green | 0 | 564 | 0 | tokens |
| heavy | Green -> Blue | 0 | 1018 | 1824 | blueprints |
| heavy | Blue -> Purple | 321 | 1132 | 5402 | blueprints |
| heavy | Purple -> Gold | 1181 | 649 | 8196 | blueprints |
| heavy | Gold -> Mythic | 7627 | 2957 | 6848 | coins |
| heavy | Mythic -> 5 stars | 0 | 0 | 56533 | blueprints |

## Sensitivity: Chests.All SeaChest.PriceBase 400 -> 2000

Days are median [p10, p90], nearest-rank over all 200 seeds; >180 is right censored, never omitted.
| Profile | Purple | Gold | Mythic level 30 | Mythic 5 stars | Mythic reached by 180 |
|---|---:|---:|---:|---:|---:|
| casual | 22 [14, 33] | 31 [21, 45] | 54 [42, 71] | 151 [126, 176] | 200/200 |
| regular | 9 [6, 14] | 14 [10, 20] | 24 [17, 34] | 67 [55, 81] | 200/200 |
| heavy | 5 [3, 7] | 8 [6, 10] | 13 [9, 17] | 36 [29, 42] | 200/200 |

| Profile | Road milestone day 30 / 60 / 180 (median) | Renown day 30 / 60 / 180 (median) | Tier 2 / 3 / 4 / 5 days (median [p10,p90]) |
|---|---|---|---|
| casual | 5 / 6 / 8 | 46 / 66 / 116 | 4 [4, 4] / 7 [6, 7] / 8 [8, 9] / >180 [>180, >180] |
| regular | 6 / 8 / 8 | 76 / 106 / 116 | 2 [2, 2] / 3 [3, 3] / 4 [3, 4] / >180 [>180, >180] |
| heavy | 8 / 8 / 8 | 106 / 116 / 116 | 1 [1, 1] / 2 [2, 2] / 2 [2, 2] / >180 [>180, >180] |

180-day means (tokens earned and spent are exact per-run reconciled ledgers):
| Profile | Haul tokens | Chest tokens | Road tokens | Total earned | Spent | Banked | Chests / sea chests | Dropped BP / focused BP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| casual | 6659.5 | 58591.2 | 80.0 | 65330.7 | 2579.0 | 62751.7 | 667.7 / 425.7 | 45.7 / 28.9 |
| regular | 17011.2 | 140560.0 | 80.0 | 157651.2 | 2579.0 | 155072.2 | 1349.7 / 1107.7 | 104.7 / 29.0 |
| heavy | 34242.1 | 276866.2 | 80.0 | 311188.3 | 2579.0 | 308609.3 | 2485.2 / 2243.2 | 204.7 / 29.0 |

| Profile | Gross sale coins | Wages | Operating reserve | Hulls + cooler | Levels | Sea chests | Ending coins |
|---|---:|---:|---:|---:|---:|---:|---:|
| casual | 1454706.8 | 36033.0 | 3600.0 | 23000.0 | 28355.0 | 1355728.5 | 8030.3 |
| regular | 3699032.2 | 92673.3 | 9000.0 | 23000.0 | 28355.0 | 3538110.0 | 7933.8 |
| heavy | 7436177.1 | 187149.6 | 18000.0 | 23000.0 | 28355.0 | 7171700.0 | 8012.5 |

Blocked post-spend trip observations by current rank, pooled across seeds. Coin/token counters can overlap; blueprint waits count only at level cap. These identify the next progression gate, not a causal economic elasticity test.
| Profile | Current rank -> next | Coin | Tokens | Blueprints | Dominant gate |
|---|---|---:|---:|---:|---|
| casual | White -> Green | 0 | 799 | 0 | tokens |
| casual | Green -> Blue | 197 | 1253 | 2522 | blueprints |
| casual | Blue -> Purple | 28 | 296 | 3875 | blueprints |
| casual | Purple -> Gold | 0 | 10 | 3937 | blueprints |
| casual | Gold -> Mythic | 553 | 0 | 8555 | blueprints |
| casual | Mythic -> 5 stars | 0 | 0 | 37628 | blueprints |
| regular | White -> Green | 3 | 1088 | 0 | tokens |
| regular | Green -> Blue | 172 | 1347 | 2487 | blueprints |
| regular | Blue -> Purple | 18 | 157 | 4253 | blueprints |
| regular | Purple -> Gold | 0 | 9 | 4880 | blueprints |
| regular | Gold -> Mythic | 565 | 12 | 8967 | blueprints |
| regular | Mythic -> 5 stars | 0 | 0 | 43584 | blueprints |
| heavy | White -> Green | 39 | 1531 | 0 | tokens |
| heavy | Green -> Blue | 110 | 1223 | 2369 | blueprints |
| heavy | Blue -> Purple | 15 | 72 | 4608 | blueprints |
| heavy | Purple -> Gold | 0 | 2 | 4761 | blueprints |
| heavy | Gold -> Mythic | 578 | 2 | 9483 | blueprints |
| heavy | Mythic -> 5 stars | 0 | 0 | 45355 | blueprints |

## Sensitivity: Chests.All SeaChest.PriceBase 400 -> 3000

Days are median [p10, p90], nearest-rank over all 200 seeds; >180 is right censored, never omitted.
| Profile | Purple | Gold | Mythic level 30 | Mythic 5 stars | Mythic reached by 180 |
|---|---:|---:|---:|---:|---:|
| casual | 25 [17, 37] | 38 [27, 54] | 65 [48, 88] | >180 [152, >180] | 200/200 |
| regular | 11 [7, 18] | 17 [11, 25] | 29 [21, 40] | 84 [69, 101] | 200/200 |
| heavy | 6 [4, 8] | 9 [6, 13] | 16 [11, 20] | 44 [36, 52] | 200/200 |

| Profile | Road milestone day 30 / 60 / 180 (median) | Renown day 30 / 60 / 180 (median) | Tier 2 / 3 / 4 / 5 days (median [p10,p90]) |
|---|---|---|---|
| casual | 5 / 6 / 8 | 46 / 61 / 106 | 4 [4, 4] / 7 [6, 7] / 8 [8, 9] / >180 [>180, >180] |
| regular | 6 / 7 / 8 | 66 / 96 / 116 | 2 [2, 2] / 3 [3, 3] / 4 [3, 4] / >180 [>180, >180] |
| heavy | 7 / 8 / 8 | 96 / 116 / 116 | 1 [1, 1] / 2 [2, 2] / 2 [2, 2] / >180 [>180, >180] |

180-day means (tokens earned and spent are exact per-run reconciled ledgers):
| Profile | Haul tokens | Chest tokens | Road tokens | Total earned | Spent | Banked | Chests / sea chests | Dropped BP / focused BP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| casual | 6662.5 | 46429.4 | 80.0 | 53171.9 | 2579.0 | 50592.9 | 566.2 / 324.2 | 36.6 / 26.7 |
| regular | 17014.3 | 108928.2 | 80.0 | 126022.4 | 2579.0 | 123443.4 | 1086.0 / 844.0 | 82.2 / 29.0 |
| heavy | 34245.9 | 212794.0 | 80.0 | 247119.9 | 2579.0 | 244540.9 | 1951.2 / 1709.2 | 159.4 / 29.0 |

| Profile | Gross sale coins | Wages | Operating reserve | Hulls + cooler | Levels | Sea chests | Ending coins |
|---|---:|---:|---:|---:|---:|---:|---:|
| casual | 1454944.3 | 35849.0 | 3600.0 | 23000.0 | 28355.0 | 1353744.0 | 10436.3 |
| regular | 3699449.1 | 92471.3 | 9000.0 | 23000.0 | 28355.0 | 3536295.0 | 10367.8 |
| heavy | 7436692.9 | 186926.0 | 18000.0 | 23000.0 | 28355.0 | 7170030.0 | 10421.9 |

Blocked post-spend trip observations by current rank, pooled across seeds. Coin/token counters can overlap; blueprint waits count only at level cap. These identify the next progression gate, not a causal economic elasticity test.
| Profile | Current rank -> next | Coin | Tokens | Blueprints | Dominant gate |
|---|---|---:|---:|---:|---|
| casual | White -> Green | 0 | 799 | 0 | tokens |
| casual | Green -> Blue | 197 | 1253 | 2942 | blueprints |
| casual | Blue -> Purple | 28 | 331 | 4818 | blueprints |
| casual | Purple -> Gold | 0 | 11 | 5348 | blueprints |
| casual | Gold -> Mythic | 459 | 0 | 10093 | blueprints |
| casual | Mythic -> 5 stars | 0 | 0 | 42689 | blueprints |
| regular | White -> Green | 3 | 1088 | 0 | tokens |
| regular | Green -> Blue | 172 | 1347 | 3017 | blueprints |
| regular | Blue -> Purple | 17 | 181 | 5545 | blueprints |
| regular | Purple -> Gold | 0 | 10 | 5469 | blueprints |
| regular | Gold -> Mythic | 483 | 0 | 11677 | blueprints |
| regular | Mythic -> 5 stars | 0 | 0 | 55467 | blueprints |
| heavy | White -> Green | 39 | 1531 | 0 | tokens |
| heavy | Green -> Blue | 110 | 1225 | 2823 | blueprints |
| heavy | Blue -> Purple | 10 | 70 | 5579 | blueprints |
| heavy | Purple -> Gold | 0 | 2 | 6282 | blueprints |
| heavy | Gold -> Mythic | 469 | 0 | 12577 | blueprints |
| heavy | Mythic -> 5 stars | 0 | 0 | 57061 | blueprints |

## Sensitivity: Chests.All SeaChest.PriceBase 400 -> 6000

Days are median [p10, p90], nearest-rank over all 200 seeds; >180 is right censored, never omitted.
| Profile | Purple | Gold | Mythic level 30 | Mythic 5 stars | Mythic reached by 180 |
|---|---:|---:|---:|---:|---:|
| casual | 30 [18, 41] | 43 [28, 59] | 75 [54, 94] | >180 [171, >180] | 200/200 |
| regular | 13 [8, 21] | 20 [12, 29] | 33 [24, 44] | 99 [80, 119] | 200/200 |
| heavy | 8 [5, 11] | 11 [7, 16] | 19 [14, 25] | 52 [44, 63] | 200/200 |

| Profile | Road milestone day 30 / 60 / 180 (median) | Renown day 30 / 60 / 180 (median) | Tier 2 / 3 / 4 / 5 days (median [p10,p90]) |
|---|---|---|---|
| casual | 5 / 6 / 8 | 48 / 63 / 108 | 4 [4, 4] / 7 [6, 7] / 8 [8, 9] / 11 [10, 11] |
| regular | 6 / 7 / 8 | 63 / 88 / 118 | 2 [2, 2] / 3 [3, 3] / 4 [3, 4] / 4 [4, 5] |
| heavy | 7 / 8 / 8 | 88 / 118 / 118 | 1 [1, 1] / 2 [2, 2] / 2 [2, 2] / 2 [2, 3] |

180-day means (tokens earned and spent are exact per-run reconciled ledgers):
| Profile | Haul tokens | Chest tokens | Road tokens | Total earned | Spent | Banked | Chests / sea chests | Dropped BP / focused BP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| casual | 11097.1 | 49626.8 | 80.0 | 60803.9 | 2579.0 | 58224.9 | 510.7 / 268.7 | 31.9 / 24.1 |
| regular | 28522.3 | 115019.8 | 80.0 | 143622.1 | 2579.0 | 141043.1 | 945.3 / 703.3 | 69.9 / 29.0 |
| heavy | 57528.2 | 223570.6 | 80.0 | 281178.8 | 2579.0 | 278599.8 | 1668.5 / 1426.5 | 132.9 / 29.0 |

| Profile | Gross sale coins | Wages | Operating reserve | Hulls + cooler | Levels | Sea chests | Ending coins |
|---|---:|---:|---:|---:|---:|---:|---:|
| casual | 2159557.7 | 65533.1 | 3600.0 | 41000.0 | 28355.0 | 2002312.5 | 18797.1 |
| regular | 5525922.5 | 169657.6 | 9000.0 | 41000.0 | 28355.0 | 5259450.0 | 18499.9 |
| heavy | 11132610.8 | 343219.2 | 18000.0 | 41000.0 | 28355.0 | 10683562.5 | 18514.1 |

Blocked post-spend trip observations by current rank, pooled across seeds. Coin/token counters can overlap; blueprint waits count only at level cap. These identify the next progression gate, not a causal economic elasticity test.
| Profile | Current rank -> next | Coin | Tokens | Blueprints | Dominant gate |
|---|---|---:|---:|---:|---|
| casual | White -> Green | 0 | 799 | 0 | tokens |
| casual | Green -> Blue | 197 | 1253 | 3447 | blueprints |
| casual | Blue -> Purple | 28 | 331 | 5677 | blueprints |
| casual | Purple -> Gold | 0 | 20 | 5766 | blueprints |
| casual | Gold -> Mythic | 87 | 3 | 11938 | blueprints |
| casual | Mythic -> 5 stars | 0 | 0 | 41693 | blueprints |
| regular | White -> Green | 3 | 1088 | 0 | tokens |
| regular | Green -> Blue | 172 | 1347 | 4371 | blueprints |
| regular | Blue -> Purple | 18 | 213 | 6302 | blueprints |
| regular | Purple -> Gold | 0 | 6 | 6065 | blueprints |
| regular | Gold -> Mythic | 98 | 0 | 13714 | blueprints |
| regular | Mythic -> 5 stars | 0 | 0 | 65943 | blueprints |
| heavy | White -> Green | 39 | 1531 | 0 | tokens |
| heavy | Green -> Blue | 110 | 1225 | 4470 | blueprints |
| heavy | Blue -> Purple | 11 | 107 | 7396 | blueprints |
| heavy | Purple -> Gold | 0 | 0 | 6865 | blueprints |
| heavy | Gold -> Mythic | 117 | 0 | 15743 | blueprints |
| heavy | Mythic -> 5 stars | 0 | 0 | 67977 | blueprints |


# Crew card pacing: findings and tuning decision

> The original findings below predate CREW-TIERS. See the final CREW-TIERS rerun section for the current conditional progression measurement.

CARDS-PACING-1, Codex 1 (Windows app), 2026-10-25. Analysis only; no runtime, Data, UI, or save changes.

The baseline regular player reaches **Gold on median day 19**, **Mythic level 30 on day 32**, and **Mythic five stars on day 84**. Mythic's p10/p90 is 25/41 days. The brief's regular-player median target of 30–60 days is already met. Five stars takes longer than two months; calling Mythic “fully maxed” would hide that distinction. The spec's narrower five-to-seven-week aspiration is also a little slower than this baseline median.

The 30–60-day result describes the median: 128 of 200 regular seeds reach Mythic within that interval; the faster seeds also count toward the reported percentiles. All 200 regular seeds reach five stars by day 180.

The binding gate changes with rank: tokens for White→Green; blueprints for Green→Blue, Blue→Purple and Purple→Gold; coins for Gold's expensive levels before Mythic; blueprints for stars. Blueprint waits dominate the pre-Mythic journey overall. The rank-by-rank counters below support this; simultaneous coin/token shortages are counted separately rather than forced into one cause.

**Recommendation: retain current card rewards and costs for now (zero data constants changed).** Increasing rewards is not supported by this model. First address the chest-buying policy's hull savings assumption: the literal repeat-buy rule leaves every baseline seed on the Skiff for all 180 days. At tier 1 the sea chest costs 700; purchases drain the wallet below the 2,100 purchase trigger after each return, preventing the 4,000-plus-wages Compact refit. This is a simulated spend-policy trap, not proof that a human player cannot save for a hull. No free hulls or invented tier-3 boat were injected to conceal it.

Typical baseline gross income is about 687 coins per trip, from the real sale valuation of the explicitly assumed fresh common-fish hauls. Each refit date in the tables is derived from actual sampled sales, wages, level spending and the current 4,000/9,500/18,000 hull prices, plus the required 3,000 cooler. A `>180` hull date means that purchase never became affordable under this policy. These results condition on completing 2/5/10 filled-hold trips daily; they do not establish that five trips fit an hour. The entire-roster eight-to-nine-month target is not tested by a single-focus policy that leaves all other cards at their starting levels.

## Measured constant sensitivities

Each candidate changes only `Chests.All`'s SeaChest `PriceBase` in memory, and restores it in `finally`; `PricePerTier = 300` and all card/token/blueprint odds stay unchanged. Each is rerun for 200 seeds per profile over 180 days. These are conditional alternatives for Claude's review, not instructions to change Data or recommendations to raise chest prices merely to repair a bot's spending policy. The counterintuitive speed-up when some prices rise comes from unlocking higher-income hulls and more tokens per chest/haul. The smallest tuning needed to meet the brief's **baseline** 30–60-day median is **no change**. If Claude also requires this exact bot to finance every real hull without changing its spend policy, the one-constant 6,000 case is a measured alternative that meets the day target and the tier path; it is not a claim that 6,000 is the globally smallest possible price.

| Candidate constant (SeaChest.PriceBase) | Expected mechanism | Re-measured regular Gold / Mythic / 5 stars, median [p10,p90] | Outcome |
|---|---|---|---|
| 400 → 2,000 | Larger cash buffer allows higher-income hulls, accelerating rewards despite a higher chest price | 14 [10,20] / 25 [18,32] / 69 [56,81] | Too fast for Mythic target; tier 5 still stalls |
| 400 → 3,000 | Higher chest cost slows blueprint acquisition after early hull upgrades | 16 [11,25] / 30 [20,39] / 88 [71,106] | Median meets target; tier 5 still stalls |
| 400 → 6,000 | Wallet buffer allows all refits; chest purchases remain slower per coin | 20 [13,30] / 36 [23,48] / 102 [84,122] | Median meets target with full real hull path; five stars remains over two months |

The 6,000 case's actual hull days (tier 1 is day 1 in every profile) are casual 4/7/10, regular 2/3/4, heavy 1/2/2 for tiers 2/4/5. Regular Gold→Mythic then becomes overwhelmingly blueprint-limited (14,725 blocked trip observations versus 83 coin and zero token observations). Do not transfer the baseline's coin bottleneck to the higher-tier economy. Raising price also reduces chest/tool volume; this sim does not measure the resulting equipment progression or player enjoyment. All candidates are proposals only and none has been applied.

Full remeasured tables follow the evidence notes.

## Reproduction and evidence

Run from the main checkout:

```powershell
powershell -NoProfile -File docs/tools/check.ps1 -Name cards-pacing -Method Catchline.EditorTools.CardPacingSim.Run
```

This copies source to **Catchline-sim** and runs Unity there. The tool never calls save/load or PlayerPrefs, never opens a gameplay scene and never writes game-data source. Its only game-data mutation is a temporary chest-definition field in that separate editor process. The 10-coin operating reserve and common-fish mix are assumptions, not duplicated economic formulas. Every level, rank, star, wage, token, chest and renown result comes from the real API. Working capital is retained before spending; the first development run caught the bankruptcy that otherwise resulted from spending every last coin on levels.

Final evidence is in the sibling scratch project's `Logs` directory:

- [Unity execution log](../../../Catchline-sim/Logs/cards-pacing-pretiers/check-cards-pacing.log)
- [Per-seed results, including censored day 181](../../../Catchline-sim/Logs/cards-pacing-pretiers/cards-pacing-results.csv)
- [Machine-generated tables](../../../Catchline-sim/Logs/cards-pacing-pretiers/cards-pacing-generated.md)
- [SHA256 manifest of the tested tool and ten economic source files](../../../Catchline-sim/Logs/cards-pacing-pretiers/cards-pacing-sources.sha256)
- [Independent CSV and source-hash verification receipt](../../../Catchline-sim/Logs/cards-pacing-pretiers/cards-pacing-verification.json)

The CSV uses `181` for “not reached in 180 days”; table quantiles include those runs. Nearest-rank p10/median/p90 over 200 seeds uses positions 20/100/180. Road milestone entries are *claimed milestone indices*, with renown totals shown separately. Dropped blueprint totals exclude renown choices; focused blueprint totals exclude free blueprints banked after Noor reaches five stars. Other crew can receive renown choices only once Noor cannot use them, allowing immediate claims without inventing additional focus progression.


## Simulation assumptions and full tables

200 seeds (1..200) per profile, 180 days, 2/5/10 trips daily. Focus Noor from White level 1; Mira excluded. All rarity/level/star costs and reward rolls use GameState APIs. No save is read or written. No game data source is edited.

Start already owning tier-1 Skiff, default StartCoins, no other equipment. Refit costs come from live constants (Compact 4000, Prep 9500, Buoy 18000). Buy BigCooler at tier2 (3000) to clear Prep's100kg gate; it persists on later hulls. The real CardTier path is 1/2/4/5: future tier3 is unavailable. Hull days below emerge from actual cash, not invented unlock dates.

Income assumption: each trip's target fill is uniform[0.6,1.0); fill each hold with equal draws of eligible Herring/Mackerel/Pollock/SeaBass/Cod, weight uniform within real species limits. Last fish is clipped to remaining target kg (synthetic haul approximation). Sell at time0 (fresh), with real specimen prices; no rare jackpot, depletion, catch-time, ability productivity, gear upgrades or contract cash. Deduct real wages and an assumed10coins/trip fuel/bait reserve. These are conditional economy estimates, not a one-hour gameplay measurement.

Working capital: level spending keeps departure wages +20coins; hull purchases retain the next deployment wages +10coins. Policy per return: real Sell; AwardHaulTokens using departure deployment; daily crate deduplicated by simulated date; one contract crate every third day. Open all chests, focus-level before rank/stars, claim renown immediately to Noor (after maxing, unused choices go to another eligible card), repeat to convergence. Then buy the next affordable hull/cooler, then repeatedly buy sea chests while coins exceed3xprice, settling after each. Other cards stay at starting rarity/level; deploy navigator then roster order to all real berths. No prestige. Separate seeded fill/income and chest RNG streams; same seeds per scenario, but hull timing can change with costs/rewards.

## Baseline

Days are median [p10, p90], nearest-rank over all 200 seeds; >180 is right censored, never omitted.
| Profile | Purple | Gold | Mythic level 30 | Mythic 5 stars | Mythic reached by 180 |
|---|---:|---:|---:|---:|---:|
| casual | 19 [11, 31] | 38 [27, 57] | 68 [56, 88] | 180 [149, >180] | 200/200 |
| regular | 10 [6, 15] | 19 [13, 28] | 32 [25, 41] | 84 [70, 103] | 200/200 |
| heavy | 5 [3, 8] | 10 [6, 13] | 17 [14, 22] | 46 [36, 55] | 200/200 |

| Profile | Road milestone day 30 / 60 / 180 (median) | Renown day 30 / 60 / 180 (median) | Tier 2 / 4 / 5 days (median [p10,p90]) |
|---|---|---|---|
| casual | 4 / 5 / 8 | 36 / 51 / 106 | >180 [>180, >180] / >180 [>180, >180] / >180 [>180, >180] |
| regular | 5 / 7 / 8 | 51 / 86 / 106 | >180 [>180, >180] / >180 [>180, >180] / >180 [>180, >180] |
| heavy | 7 / 8 / 8 | 86 / 106 / 106 | >180 [>180, >180] / >180 [>180, >180] / >180 [>180, >180] |

180-day means (tokens earned and spent are exact per-run reconciled ledgers):
| Profile | Haul tokens | Chest tokens | Road tokens | Total earned | Spent | Banked | Chests / sea chests | Dropped BP / focused BP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| casual | 405.8 | 10522.7 | 80.0 | 11008.5 | 2579.0 | 8429.5 | 528.2 / 286.2 | 33.1 / 27.1 |
| regular | 1013.2 | 25205.2 | 80.0 | 26298.4 | 2579.0 | 23719.4 | 1017.6 / 775.6 | 73.3 / 29.0 |
| heavy | 2024.0 | 49627.3 | 80.0 | 51731.3 | 2579.0 | 49152.3 | 1831.7 / 1589.7 | 141.7 / 29.0 |

| Profile | Gross sale coins | Wages | Operating reserve | Hulls + cooler | Levels | Sea chests | Ending coins |
|---|---:|---:|---:|---:|---:|---:|---:|
| casual | 247238.4 | 14260.7 | 3600.0 | 0.0 | 28355.0 | 199304.0 | 1758.7 |
| regular | 617880.8 | 37269.0 | 9000.0 | 0.0 | 28355.0 | 541548.0 | 1748.8 |
| heavy | 1235399.8 | 75934.2 | 18000.0 | 0.0 | 28355.0 | 1111397.0 | 1753.6 |

Blocked post-spend trip observations by current rank, pooled across seeds. Coin/token counters can overlap; blueprint waits count only at level cap. These identify the next progression gate, not a causal economic elasticity test.
| Profile | Current rank -> next | Coin | Tokens | Blueprints | Dominant gate |
|---|---|---:|---:|---:|---|
| casual | White -> Green | 0 | 586 | 0 | tokens |
| casual | Green -> Blue | 0 | 775 | 1496 | blueprints |
| casual | Blue -> Purple | 259 | 1055 | 3892 | blueprints |
| casual | Purple -> Gold | 1119 | 795 | 6147 | blueprints |
| casual | Gold -> Mythic | 7750 | 3383 | 3783 | coins |
| casual | Mythic -> 5 stars | 0 | 0 | 40446 | blueprints |
| regular | White -> Green | 0 | 564 | 0 | tokens |
| regular | Green -> Blue | 0 | 797 | 2154 | blueprints |
| regular | Blue -> Purple | 331 | 1061 | 4615 | blueprints |
| regular | Purple -> Gold | 1163 | 666 | 7781 | blueprints |
| regular | Gold -> Mythic | 7716 | 3142 | 5649 | coins |
| regular | Mythic -> 5 stars | 0 | 0 | 53310 | blueprints |
| heavy | White -> Green | 0 | 564 | 0 | tokens |
| heavy | Green -> Blue | 0 | 1018 | 2261 | blueprints |
| heavy | Blue -> Purple | 336 | 1015 | 4296 | blueprints |
| heavy | Purple -> Gold | 1154 | 1100 | 7512 | blueprints |
| heavy | Gold -> Mythic | 7947 | 3425 | 6695 | coins |
| heavy | Mythic -> 5 stars | 0 | 0 | 56499 | blueprints |

## Sensitivity: Chests.All SeaChest.PriceBase 400 -> 2000

Days are median [p10, p90], nearest-rank over all 200 seeds; >180 is right censored, never omitted.
| Profile | Purple | Gold | Mythic level 30 | Mythic 5 stars | Mythic reached by 180 |
|---|---:|---:|---:|---:|---:|
| casual | 22 [13, 31] | 32 [21, 44] | 54 [38, 70] | 149 [125, >180] | 200/200 |
| regular | 9 [6, 14] | 14 [10, 20] | 25 [18, 32] | 69 [56, 81] | 200/200 |
| heavy | 5 [3, 8] | 8 [5, 11] | 13 [9, 17] | 36 [30, 42] | 200/200 |

| Profile | Road milestone day 30 / 60 / 180 (median) | Renown day 30 / 60 / 180 (median) | Tier 2 / 4 / 5 days (median [p10,p90]) |
|---|---|---|---|
| casual | 5 / 6 / 8 | 45 / 65 / 115 | 4 [4, 4] / 9 [7, 14] / >180 [>180, >180] |
| regular | 6 / 8 / 8 | 75 / 105 / 115 | 2 [2, 2] / 4 [3, 5] / >180 [>180, >180] |
| heavy | 8 / 8 / 8 | 105 / 115 / 115 | 1 [1, 1] / 2 [2, 3] / >180 [>180, >180] |

180-day means (tokens earned and spent are exact per-run reconciled ledgers):
| Profile | Haul tokens | Chest tokens | Road tokens | Total earned | Spent | Banked | Chests / sea chests | Dropped BP / focused BP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| casual | 5463.2 | 58460.5 | 80.0 | 64003.7 | 2579.0 | 61424.7 | 669.1 / 427.1 | 44.1 / 28.7 |
| regular | 14041.1 | 140614.8 | 80.0 | 154735.9 | 2579.0 | 152156.9 | 1352.4 / 1110.4 | 100.9 / 29.0 |
| heavy | 28336.3 | 277329.9 | 80.0 | 305746.3 | 2579.0 | 303167.3 | 2490.7 / 2248.7 | 196.9 / 29.0 |

| Profile | Gross sale coins | Wages | Operating reserve | Hulls + cooler | Levels | Sea chests | Ending coins |
|---|---:|---:|---:|---:|---:|---:|---:|
| casual | 1447135.2 | 33081.0 | 3600.0 | 16500.0 | 28355.0 | 1357633.0 | 8006.2 |
| regular | 3691409.1 | 85386.6 | 9000.0 | 16500.0 | 28355.0 | 3544245.0 | 7962.5 |
| heavy | 7430851.6 | 172700.2 | 18000.0 | 16500.0 | 28355.0 | 7187364.0 | 7972.4 |

Blocked post-spend trip observations by current rank, pooled across seeds. Coin/token counters can overlap; blueprint waits count only at level cap. These identify the next progression gate, not a causal economic elasticity test.
| Profile | Current rank -> next | Coin | Tokens | Blueprints | Dominant gate |
|---|---|---:|---:|---:|---|
| casual | White -> Green | 0 | 799 | 0 | tokens |
| casual | Green -> Blue | 171 | 1401 | 2050 | blueprints |
| casual | Blue -> Purple | 24 | 246 | 3913 | blueprints |
| casual | Purple -> Gold | 6 | 36 | 4002 | blueprints |
| casual | Gold -> Mythic | 562 | 22 | 8298 | blueprints |
| casual | Mythic -> 5 stars | 0 | 0 | 38859 | blueprints |
| regular | White -> Green | 5 | 1088 | 0 | tokens |
| regular | Green -> Blue | 158 | 1315 | 2147 | blueprints |
| regular | Blue -> Purple | 34 | 175 | 4301 | blueprints |
| regular | Purple -> Gold | 1 | 16 | 4953 | blueprints |
| regular | Gold -> Mythic | 582 | 3 | 9317 | blueprints |
| regular | Mythic -> 5 stars | 0 | 0 | 44211 | blueprints |
| heavy | White -> Green | 43 | 1600 | 0 | tokens |
| heavy | Green -> Blue | 96 | 813 | 2384 | blueprints |
| heavy | Blue -> Purple | 17 | 117 | 4772 | blueprints |
| heavy | Purple -> Gold | 2 | 1 | 4949 | blueprints |
| heavy | Gold -> Mythic | 589 | 16 | 9382 | blueprints |
| heavy | Mythic -> 5 stars | 0 | 0 | 46523 | blueprints |

## Sensitivity: Chests.All SeaChest.PriceBase 400 -> 3000

Days are median [p10, p90], nearest-rank over all 200 seeds; >180 is right censored, never omitted.
| Profile | Purple | Gold | Mythic level 30 | Mythic 5 stars | Mythic reached by 180 |
|---|---:|---:|---:|---:|---:|
| casual | 23 [13, 36] | 35 [22, 54] | 61 [44, 83] | >180 [152, >180] | 200/200 |
| regular | 11 [6, 17] | 16 [11, 25] | 30 [20, 39] | 88 [71, 106] | 200/200 |
| heavy | 6 [4, 9] | 9 [6, 13] | 16 [11, 21] | 45 [37, 53] | 200/200 |

| Profile | Road milestone day 30 / 60 / 180 (median) | Renown day 30 / 60 / 180 (median) | Tier 2 / 4 / 5 days (median [p10,p90]) |
|---|---|---|---|
| casual | 5 / 6 / 8 | 45 / 60 / 105 | 4 [4, 4] / 7 [7, 8] / >180 [>180, >180] |
| regular | 6 / 7 / 8 | 65 / 95 / 115 | 2 [2, 2] / 3 [3, 3] / >180 [>180, >180] |
| heavy | 7 / 8 / 8 | 95 / 115 / 115 | 1 [1, 1] / 2 [2, 2] / >180 [>180, >180] |

180-day means (tokens earned and spent are exact per-run reconciled ledgers):
| Profile | Haul tokens | Chest tokens | Road tokens | Total earned | Spent | Banked | Chests / sea chests | Dropped BP / focused BP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| casual | 5518.2 | 46698.4 | 80.0 | 52296.6 | 2579.0 | 49717.6 | 568.2 / 326.2 | 36.4 / 26.6 |
| regular | 14094.2 | 109292.6 | 80.0 | 123466.8 | 2579.0 | 120887.8 | 1088.9 / 846.9 | 78.8 / 29.0 |
| heavy | 28377.1 | 213379.8 | 80.0 | 241836.9 | 2579.0 | 239257.9 | 1956.0 / 1714.0 | 153.7 / 29.0 |

| Profile | Gross sale coins | Wages | Operating reserve | Hulls + cooler | Levels | Sea chests | Ending coins |
|---|---:|---:|---:|---:|---:|---:|---:|
| casual | 1454362.0 | 33111.1 | 3600.0 | 16500.0 | 28355.0 | 1362312.0 | 10524.0 |
| regular | 3698238.9 | 85334.6 | 9000.0 | 16500.0 | 28355.0 | 3548601.0 | 10488.3 |
| heavy | 7436117.5 | 172605.0 | 18000.0 | 16500.0 | 28355.0 | 7190253.0 | 10444.5 |

Blocked post-spend trip observations by current rank, pooled across seeds. Coin/token counters can overlap; blueprint waits count only at level cap. These identify the next progression gate, not a causal economic elasticity test.
| Profile | Current rank -> next | Coin | Tokens | Blueprints | Dominant gate |
|---|---|---:|---:|---:|---|
| casual | White -> Green | 0 | 799 | 0 | tokens |
| casual | Green -> Blue | 171 | 1401 | 2435 | blueprints |
| casual | Blue -> Purple | 36 | 228 | 4687 | blueprints |
| casual | Purple -> Gold | 0 | 13 | 4776 | blueprints |
| casual | Gold -> Mythic | 450 | 20 | 10220 | blueprints |
| casual | Mythic -> 5 stars | 0 | 0 | 43390 | blueprints |
| regular | White -> Green | 5 | 1088 | 0 | tokens |
| regular | Green -> Blue | 162 | 1469 | 2798 | blueprints |
| regular | Blue -> Purple | 14 | 85 | 5412 | blueprints |
| regular | Purple -> Gold | 0 | 0 | 6009 | blueprints |
| regular | Gold -> Mythic | 482 | 3 | 11958 | blueprints |
| regular | Mythic -> 5 stars | 0 | 0 | 58376 | blueprints |
| heavy | White -> Green | 43 | 1600 | 0 | tokens |
| heavy | Green -> Blue | 111 | 1205 | 2628 | blueprints |
| heavy | Blue -> Purple | 0 | 24 | 5852 | blueprints |
| heavy | Purple -> Gold | 0 | 2 | 6109 | blueprints |
| heavy | Gold -> Mythic | 482 | 5 | 12586 | blueprints |
| heavy | Mythic -> 5 stars | 0 | 0 | 58692 | blueprints |

## Sensitivity: Chests.All SeaChest.PriceBase 400 -> 6000

Days are median [p10, p90], nearest-rank over all 200 seeds; >180 is right censored, never omitted.
| Profile | Purple | Gold | Mythic level 30 | Mythic 5 stars | Mythic reached by 180 |
|---|---:|---:|---:|---:|---:|
| casual | 28 [18, 41] | 42 [28, 60] | 70 [52, 96] | >180 [173, >180] | 200/200 |
| regular | 14 [8, 20] | 20 [13, 30] | 36 [23, 48] | 102 [84, 122] | 200/200 |
| heavy | 7 [4, 11] | 11 [7, 15] | 18 [14, 25] | 55 [45, 67] | 200/200 |

| Profile | Road milestone day 30 / 60 / 180 (median) | Renown day 30 / 60 / 180 (median) | Tier 2 / 4 / 5 days (median [p10,p90]) |
|---|---|---|---|
| casual | 5 / 6 / 8 | 48 / 63 / 108 | 4 [4, 4] / 7 [7, 8] / 10 [9, 10] |
| regular | 6 / 7 / 8 | 63 / 88 / 118 | 2 [2, 2] / 3 [3, 3] / 4 [4, 4] |
| heavy | 7 / 8 / 8 | 88 / 118 / 118 | 1 [1, 1] / 2 [2, 2] / 2 [2, 2] |

180-day means (tokens earned and spent are exact per-run reconciled ledgers):
| Profile | Haul tokens | Chest tokens | Road tokens | Total earned | Spent | Banked | Chests / sea chests | Dropped BP / focused BP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| casual | 8309.7 | 50204.8 | 80.0 | 58594.4 | 2579.0 | 56015.4 | 514.3 / 272.3 | 32.0 / 24.3 |
| regular | 21326.2 | 116171.9 | 80.0 | 137578.1 | 2579.0 | 134999.1 | 952.8 / 710.8 | 67.3 / 29.0 |
| heavy | 43002.0 | 225704.7 | 80.0 | 268786.7 | 2579.0 | 266207.7 | 1682.6 / 1440.6 | 128.1 / 29.0 |

| Profile | Gross sale coins | Wages | Operating reserve | Hulls + cooler | Levels | Sea chests | Ending coins |
|---|---:|---:|---:|---:|---:|---:|---:|
| casual | 2162325.5 | 47918.7 | 3600.0 | 34500.0 | 28355.0 | 2029237.5 | 18754.3 |
| regular | 5530396.9 | 123859.4 | 9000.0 | 34500.0 | 28355.0 | 5316187.5 | 18535.0 |
| heavy | 11140035.9 | 250714.1 | 18000.0 | 34500.0 | 28355.0 | 10789500.0 | 19006.7 |

Blocked post-spend trip observations by current rank, pooled across seeds. Coin/token counters can overlap; blueprint waits count only at level cap. These identify the next progression gate, not a causal economic elasticity test.
| Profile | Current rank -> next | Coin | Tokens | Blueprints | Dominant gate |
|---|---|---:|---:|---:|---|
| casual | White -> Green | 0 | 799 | 0 | tokens |
| casual | Green -> Blue | 171 | 1401 | 3024 | blueprints |
| casual | Blue -> Purple | 36 | 228 | 5689 | blueprints |
| casual | Purple -> Gold | 0 | 15 | 5793 | blueprints |
| casual | Gold -> Mythic | 88 | 6 | 12024 | blueprints |
| casual | Mythic -> 5 stars | 0 | 0 | 41894 | blueprints |
| regular | White -> Green | 5 | 1088 | 0 | tokens |
| regular | Green -> Blue | 162 | 1469 | 4060 | blueprints |
| regular | Blue -> Purple | 19 | 156 | 6485 | blueprints |
| regular | Purple -> Gold | 0 | 3 | 6788 | blueprints |
| regular | Gold -> Mythic | 83 | 0 | 14725 | blueprints |
| regular | Mythic -> 5 stars | 0 | 0 | 66913 | blueprints |
| heavy | White -> Green | 43 | 1600 | 0 | tokens |
| heavy | Green -> Blue | 111 | 1205 | 4082 | blueprints |
| heavy | Blue -> Purple | 1 | 52 | 6790 | blueprints |
| heavy | Purple -> Gold | 0 | 0 | 7504 | blueprints |
| heavy | Gold -> Mythic | 100 | 0 | 15438 | blueprints |
| heavy | Mythic -> 5 stars | 0 | 0 | 72590 | blueprints |



## CREW-TIERS rerun after DECK-BERTHS-1

Codex 1 (Windows app), after Claude's CREW-TIERS READY (f920e4a). Hulls now fit 2/4/6/8 card crew including Mira; tier 3 has five berths but no hull. **Recruitment assumption:** `GrantTrialCards` supplies all unlocked crew at the start and each refit, removes the welcome chest, and fills deployment at starting rarity/level. Noor is the sole progression focus. Recruiting time, crew-chest spending and welcome rewards are excluded; this is a conditional full-roster progression experiment, not a new-player acquisition forecast. Other haul, spending and operating assumptions remain as above.

The scratch rerun passed **2,400 runs / 432,000 simulated days**, including exact per-run coin/token conservation, no missed departures, daily deduplication, all pending chests opened, settlement convergence and restoration of temporary chest prices. Independent verification found twelve groups of 200 unique seeds and all eleven tested source hashes still matching main at verification.

| Sea chest PriceBase | Regular Gold | Regular Mythic level 30 | Regular five stars |
|---|---:|---:|---:|
| 400 | 19 [13, 26] | 33 [26, 41] | 86 [73, 101] |
| 2000 | 15 [10, 20] | 25 [18, 32] | 68 [54, 80] |
| 3000 | 17 [12, 27] | 30 [21, 39] | 84 [68, 101] |
| 6000 | 19 [13, 28] | 34 [23, 44] | 99 [81, 120] |

Baseline regular Mythic moves from day32 to33 and five stars from84 to86; Gold remains19. The baseline still meets the 30-60 day median Mythic target under these assumptions. All 600 baseline runs remain on the Skiff through day180: the repeat chest-buying policy still prevents hull savings, so that baseline does not exercise larger deployments. All 600 runs at each higher price reach Compact and Prep; only the 6000 scenario reaches Buoy (all 600 runs). These scenarios exercise the corresponding full trial-granted deployments. Blueprint waits remain the main overall progression gate, with tokens early and coins for Gold levels. No runtime or Data constants changed; retain the earlier recommendation and resolve savings/recruitment policy before treating these as player forecasts.

Current evidence: [Unity log](../../../Catchline-sim/Logs/cards-pacing-tiers/check-cards-pacing-tiers.log), [2,400 per-seed rows](../../../Catchline-sim/Logs/cards-pacing-tiers/cards-pacing-results.csv), [complete tables](../../../Catchline-sim/Logs/cards-pacing-tiers/cards-pacing-generated.md), [tested source hashes](../../../Catchline-sim/Logs/cards-pacing-tiers/cards-pacing-sources.sha256), [independent receipt](../../../Catchline-sim/Logs/cards-pacing-tiers/verification.json). Earlier accepted evidence is preserved separately in `Logs/cards-pacing-pretiers/`.

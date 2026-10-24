# Cards, work speeds and throughput — implementation numbers

Status: implementation specification for Codex, derived from `docs/BLUEPRINT.md`
and the current constants in `GameData.cs`, `DeckActors.cs`, `VoyageGame.cs`,
`VoyageNet.cs`, `DeepLineRules.cs`, `VoyageTier5.cs` and `VoyagePrepOrders.cs`.
Every number is a starting value; §8 says how to prove them in the simulator.

## 1. One work-speed model for everyone

Every timed action on the boat uses one formula:

```
duration = base / (skill / 100) / levelMult
walk     = 2.2 m/s * (skill / 100) * levelMult        (skill = the Haul skill)
```

- `base` is the action's base duration from §4, in seconds.
- `skill` is the person's skill for that job (§3): 100 for a speciality.
- `levelMult` is the card's level multiplier (§2.2). The captain is level 1
  forever and skill 100 at every deck job.

**Remove**: `GameData.CrewWorkSpeed` (0.7 global drag), `DeckhandHandlingSpeed`
(the deckhand-only ÷3), `CompactPickupTime`/`CompactStowTime` (1.4 s / 3 s),
`Speed(Grade)` and the whole `Grade` enum. Today the captain picks up at
1.4/0.7 = 2.0 s and stows at 3/0.7 = 4.3 s on the compact boat while a hand
takes 0.67/1.43 s — that is the slowness Mo feels. After this change the captain
picks up in 0.5 s and stows in 0.6 s on every hull.

## 2. Crew cards

### 2.1 Rarity

| Rarity | Non-speciality skill | Abilities | Strike chance (fishers) |
|---|---|---|---|
| Blue | 50 | passive | 80% |
| Purple | 65 | passive + teamwork | 85% |
| Gold | 80 | passive + teamwork + signature | 90% |

Speciality skill is 100 at every rarity. Rarity never changes speciality speed;
it widens what the card is good at and unlocks abilities.

Upgrading rarity costs role wildcards (from chests, contracts and milestones)
plus coins scaled by the card's unlock tier `T` (1–5):

| Step | Wildcards | Coins |
|---|---|---|
| Blue → Purple | 10 | 300 × T |
| Purple → Gold | 25 | 1000 × T |

### 2.2 Level

Levels 1–30. `levelMult = 1 + 0.015 × (level − 1)`. Fishers also gain
+0.25 percentage points strike chance per level above 1, capped at 97%.

XP is kilograms landed by the boat while the card is deployed; every deployed
card gains the same XP per voyage. Cumulative XP to reach a level:
`xp(L) = round(40 × (L − 1)^1.5)`.

| Level | levelMult | Cumulative kg | Level | levelMult | Cumulative kg |
|---|---|---|---|---|---|
| 1 | 1.000 | 0 | 16 | 1.225 | 2,324 |
| 2 | 1.015 | 40 | 17 | 1.240 | 2,560 |
| 3 | 1.030 | 113 | 18 | 1.255 | 2,804 |
| 4 | 1.045 | 208 | 19 | 1.270 | 3,055 |
| 5 | 1.060 | 320 | 20 | 1.285 | 3,313 |
| 6 | 1.075 | 447 | 21 | 1.300 | 3,578 |
| 7 | 1.090 | 588 | 22 | 1.315 | 3,849 |
| 8 | 1.105 | 741 | 23 | 1.330 | 4,127 |
| 9 | 1.120 | 905 | 24 | 1.345 | 4,412 |
| 10 | 1.135 | 1,080 | 25 | 1.360 | 4,703 |
| 11 | 1.150 | 1,265 | 26 | 1.375 | 5,000 |
| 12 | 1.165 | 1,459 | 27 | 1.390 | 5,303 |
| 13 | 1.180 | 1,663 | 28 | 1.405 | 5,612 |
| 14 | 1.195 | 1,875 | 29 | 1.420 | 5,927 |
| 15 | 1.210 | 2,095 | 30 | 1.435 | 6,247 |

A tier-1 boat lands about 20 kg a voyage, so a card reaches level 3 after six
early trips; a tier-5 boat lands about 240 kg, so a card maxes after roughly 26
tier-5 voyages. Chest XP boosts add to the same pool.

### 2.3 Wages — paid per voyage at departure

```
wage = tierBase[T] × rarityMult × (1 + 0.01 × (level − 1))
tierBase = { T1: 8, T2: 15, T3: 30, T4: 60, T5: 120 }
rarityMult = { Blue: 1.0, Purple: 1.6, Gold: 2.5 }
```

Examples: Noor (T1) blue level 1 = 8; Dirk (T2) purple level 10 = 26; Olaf
(T5) gold level 30 = 387. A tier-5 crew of five gold level-30 cards costs about
1,500 a trip against roughly 4,800 of catch value — profitable only when the
boat is actually running well. The navigator is paid like any card.

Cards are owned permanently. **Remove** hire fees (`Fee`), contract expiry
(`ContractVoyages`, `VoyagesLeft`) and the Crew Office candidate board; the
Crew Office becomes the roster where you pick who sails.

### 2.4 Captain

Skill 100 at rods, sort, haul and table; level 1; no wage. His strike is the
player's tap. From tier 5 he keeps these skills but the design stops relying
on them.

## 3. Skill matrix by role

| Role | Speciality (100) | Other jobs in role (by rarity 50/65/80) | Cannot do |
|---|---|---|---|
| Fisher | one of Rods, Nets, Cages/Lines, Jigs | the other gear families | sort, haul, table |
| Deckhand | one of Haul, Sort, Table | the other two | gear |
| Navigator | reading grounds, warnings, radio | — | deck work, gear |
| Engineer (T5) | power and faults | haul at 50 | gear, sort, table |

## 4. Base durations (seconds, at skill 100, level 1)

| Action | Current effective (Hand) | New base | Note |
|---|---|---|---|
| Bait rod | 1.2 / 0.7 = 1.71 | **1.0** | fisher or captain, from the shared bait bin |
| Cast | 0.64 | **0.5** | |
| Line flight | 0.6 | **0.6** | unchanged |
| Bite wait | see §5 | see §5 | the main fishing limiter |
| Strike window | 0.9 / 1.15 / 1.4 by rod | same | unchanged |
| Reel | 0.8 + 0.3 kg, 0.8–2.5, ÷ rod reel speed | same | unchanged |
| Drop into rod basket | walk + 0.5 pickup + walk + 0.57 stow | **0.3** | no walking; rod basket holds 6 fish |
| Pick up one fish | 0.71 rowboat / 2.0 compact (captain) | **0.5** | every hull, every person |
| Hand capacity | 1 fish | **3 fish or 6 kg** | fish over 15 kg need two people |
| Walk | 1.54 m/s | **2.2 m/s** | loitering 0.55 unchanged |
| Sort one fish, keep | — (did not exist) | **1.5** | at the sort table |
| Sort one fish, throw back | — | **2.0** | includes the toss |
| Stow one fish at the hold | 0.57 / 4.3 compact (captain) | **0.6** | |
| Gather from net basket | 1.2 ÷ 3 ÷ 0.7 = 0.57 | **0.5** | same as pick up |
| Set net | 2.9 | **2.0** | fisher |
| Net soak shallow / deep | 40 / 60 | **40 / 60** | unchanged |
| Haul net (crank game) | 7.1 | **5.0** | fisher |
| Deep line bait / drop / soak / raise | 2 / 1 / 60 / 2 | same | fisher; line catches alone |
| Cage soak / recover | 65 / 2 | same | fisher recovers; deckhand empties the basket |
| Table: take / place | 0.15 / 0.15 | **0.2 / 0.2** | |
| Table: chum unit | 3.5 | **3.0** | white 1, green 2, blue 3 units per fish |
| Table: fish oil unit | 4.5 (prepare) | **4.0** | replaces "prepare" |
| Table: special product | — | **6.0** | purple and above, automatic |
| Loose deck fish lifetime | 25 | **25** | only loose fish; baskets never lose fish |

## 5. Bite wait

Current: `(5 + rand·4 + power·5) × spotBiteWait / max(0.3, richness)`, capped at
15 s, richness −0.035 per catch. At a drained ground this sits at the 15 s cap
for most of the voyage, which reads as "nothing happens".

New:

```
wait = clamp(6 × spotBiteWait × baitFactor / richness + 2 × power, 4, 12)
baitFactor = { scraps 1.0, worms 0.9, squid 0.85, chum 0.8 }
richness per catch: rods −0.02; nets −0.004 per kg; floor 0.3; +0.35 per voyage
```

Harbour mouth (0.85) with scraps at full richness: 5.1 + ~1 = about 6 s. At the
floor it hits the 12 s cap. Grounds drain over about 35 rod catches, which is
the relocation signal the navigator reads. Keep the first-voyage clamp 4–6 s.

## 6. Net yield

```
fish per haul = clamp(round(10 × richness × tend) + rand(−2..+2), 4, 16)
tend = 1.0 untended, 1.15 with a fisher tending during the soak
```

Species from the ground's small-school pool; the hull's kg cap still applies.
Undersize share is rolled per fish like rods. A 14-fish haul takes a sorter
about 14 × 1.6 = 22 s and a hauler about 14 × 2.0 = 28 s on the compact boat.

## 7. Throughput by tier — the intended bottleneck

Rates at level 1, speciality skill, richness 1, Harbour-mouth-class ground.
Rod rate per manned rod: `60 × strike / (4.6 + wait)`; with wait 8 s that is
3.8 fish/min for a blue fisher and about 4.3 for the captain.

Deck cost per fish: pickup 0.5 + sort 1.6 + stow 0.6 + walk (round trip ÷ 3
fish). Walk round trips: rowboat 1 m, skiff 2 m, compact 3 m, prep 4 m, buoy 5 m.

| Tier | Intake (fish/min) | Sort capacity | Haul capacity | Table | Intended wall |
|---|---|---|---|---|---|
| 1 | captain, 1–2 rods: 4–8 | 1 sorter: 37 | same hand: 24 | — | captain's attention on two rods |
| 2 | fisher 3.8 + captain 4–8: 8–12 | 1 sorter: 37 | 1 hauler: 28 | — | richness drain → bait, ground, day/night |
| 3 | 2 rods 8 + net 14 per 47 s ≈ 18: **26 peak** | 1 sorter: 33 | 1 hauler: 25 | — | sort/haul near parity; net bursts back up |
| 4 | 3 rods 12 + net 18: 30 | 1 sorter: 30 | 1 hauler: 22 | 1 hand: chum 19/min, oil 14/min, special 10/min | table-minutes when orders are set |
| 5 | rods 8 + net 18 + lines 2.8 + cages 1.8: 31 + big | 2 sorters: 56 | 1–2 haulers: 20–40 | 2 hands | power; chum supply for lines; two tables to staff |

The numbers are deliberately within 20% of each other at tiers 3–5 so that the
duty choice and the events move the wall. If the simulator shows one stage
below 60% utilisation on every voyage of a tier, change that stage's base
durations, not the crew count.

## 8. Acceptance in the simulator

Per tier, run the existing bot for 30 voyages with the default crew from
BLUEPRINT §5 and report, per stage: average utilisation, longest queue, and
the stage that was "Backed up" most. Pass when the most-backed-up stage is the
intended wall in §7 and no voyage has a stage idle more than 50% of its time.
Also report captain pickup and stow durations on the compact boat: both must
be under 1 s.

## 9. Codex implementation checklist

1. `GameData`: delete `CrewWorkSpeed`, `DeckhandHandlingSpeed`,
   `CompactPickupTime`, `CompactStowTime`, `Grade`, `Speed`, `Fee`,
   `ContractVoyages`, `StrikeChance(Grade)`. Add the §4 constants and §5/§6
   formulas. Keep `BiteWindow`, reel, soak, deep-line and cage constants.
2. `Person`: replace `Speed` with `Skill(job)` and `LevelMult`; `Tick` and
   `Do` use §1. Captain: skill 100, level 1.
3. `GameState`: crew entries become card references (card id, rarity, level,
   xp); add wages at departure, XP at sale; remove `VoyagesLeft`, hire fees and
   the candidate board. Save migration: existing crew map to blue cards of the
   same role at level 1.
4. Rod baskets, sort table and deck baskets per BLUEPRINT §4/§6; sorting
   durations from §4; undersize rule from BLUEPRINT §3.2.
5. Bite wait and richness from §5; net yield from §6.
6. Table orders replace prepare/chum orders: chum 3.0, oil 4.0, special 6.0.
7. Run §8 and append the results to this file.

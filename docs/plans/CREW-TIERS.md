# Crew tiers, recruiting and pity

Decided by Mo on 2026-10-25 (night). This replaces section 7 of CREW-CARDS-V2.md, where reaching a tier gave every
crew member of that tier for free.

## Berths

Berths count the crew cards aboard, Mira's navigator seat included. The captain is not a card.

| Tier | Boat | Berths | Hires besides Mira |
|---|---|---|---|
| 0 | Rowboat | 0 | captain alone |
| 1 | Skiff | 2 | 1 |
| 2 | Compact fisher | 4 | 3 |
| 3 | Jig boat (not built yet) | 5 | 4 |
| 4 | Prep fisher | 6 | 5 |
| 5 | Buoy fisher | 8 | 7 |

The decks still need room for these counts. That is Codex 1's job, DECK-BERTHS-1.

## Who joins at which tier

Each crew member comes from the tier that unlocks the gear their abilities work on. Higher tiers start at a higher
rarity.

| Tier | Gear it adds | Crew | Starts at |
|---|---|---|---|
| 1 | rods, first crab pot | Mira (navigator, from the welcome chest), Noor (sorting), Sam (carrying) | Mira Gold, others White |
| 2 | stern net, second pot | Dirk (rods), Kofi (setting nets), Rosa (hauling nets) | Green |
| 3 | jigs (boat to come) | Tess (rods, feathers), Ana (walking, hand-offs), Lise (night rods) | Blue |
| 4 | prep table, second net, big hold | Mats (table), Ines (freshness, night), Tove (grading, top-price fish) | Purple |
| 5 | deep lines, buoy pots, engine room | Olaf (engine, winches), Pim (deep lines, pots) | Legendary |

Tier 3 has no boat yet, so the game skips from tier 2 to tier 4. Until the jig boat exists, tier-3 crew join from
the prep fisher.

## Power creep

1. **Starting rarity.** A crew member from a higher tier joins with more of their abilities already unlocked.
2. **Tier multiplier.** Work speed is multiplied by 1.00 at tier 1, rising by 0.05 per tier to 1.20 at tier 5. Mira
   stays at 1.00.

| Crew member | Work speed |
|---|---|
| Tier-1, maxed (Mythic, level 30, 5 stars) | 2.33x |
| Tier-5, just joined (Legendary, level 1) | 1.63x |
| Tier-5, maxed | 2.79x |

A maxed tier-1 crew member still outworks a newcomer from the top tier, so the work already put into them isn't
wasted. Higher-tier crew have a higher ceiling and work on gear that lower tiers never touch, which gives players a
reason to move up.

## How crew join

- **Tutorial.** The rowboat (tier 0) sails alone. Buying the skiff brings a free **welcome chest**: Mira, 20 tokens
  and one Green-or-better tool.
- **Blueprints recruit.** A blueprint that drops for someone who hasn't joined yet recruits them at their starting
  rarity. Chest blueprints go to the focus crew member 75% of the time. The other 25% go to anyone who can still use
  one: owned crew short of Mythic with 5 stars, or crew the boat's tier has unlocked who haven't joined yet.
- **Pity on normal chests.** A blueprint is guaranteed after 50 crates, 30 sea chests or 10 captain's chests. The
  captain's chest stands in for the future gem chest. Each kind keeps its own counter.
- **Crew chests.** Every crew member the tier unlocks has an offer of 10 chests centred on them, paid in coins:
  - Each chest holds tokens, 2 tools (one Green or better) and a 15% chance of that crew member's blueprint.
  - The 10th chest always holds their blueprint, whatever dropped before.
  - Price: 1,200 + 900 × the crew member's tier, so 2,100 coins at tier 1 and 5,700 at tier 5 (three sea chests'
    worth).
  - The offer closes after 10 chests.
- **Renown road.** "Blueprint of choice" milestones can also recruit an unlocked crew member who hasn't joined.

Existing saves keep the crew they already have. The test-tier trials still give the whole tier, so testing stays
quick.

## Open numbers (to tune later)

The crew chest price and 15% chance, the welcome chest contents, the tier multipliers and the pacing. Codex 1
re-runs CardPacingSim once this lands.

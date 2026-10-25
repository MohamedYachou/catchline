# Crew cards v2: rarities, levels, blueprints, tools, chests and abilities

Agreed with Mo in chat on 2026-10-25. It replaces the Blue/Purple/Gold + role-wildcard system, the kg
experience levels and the CREW-CHESTS-1 / CHEST-ART-1 briefs. Old saves are wiped (SaveV2 version 3);
nothing migrates. The model is Hot Slide's garage (rank, level per rank, type tokens, blueprints, parts).

## 1. Rarity ladder

| Rarity | Level cap | Blueprints to reach it | Unlocks | Work speed base |
|---|---|---|---|---|
| White | 5 | start | 1 tool slot | 1.00 |
| Green | 10 | 1 | passive ability | 1.08 |
| Blue | 15 | 1 | 2nd tool slot | 1.16 |
| Purple | 20 | 2 | auto ability | 1.26 |
| Gold | 30 | 3 | 3rd tool slot, signature outfit | 1.36 |
| Mythic | 30 | 4 | strong auto ability, red premium frame | 1.50 |

- A card must be at its level cap to rank up. Ranking up keeps the level and raises the cap.
- A crew member at Mythic level 30 works about 2x a fresh White, and about 10% faster than a level-30 Gold.
  The limit on money sits in the fishing ground (fish per minute), so a strong crew stops waiting on the
  early maps and earns its keep on the later, richer ones; a weak crew can't fill the hold there in time.

Work speed = rarity base x (1 + 0.012 x (level - 1)) x (1 + 0.03 x stars) x (1 + tool bonus for that job).
Off-speciality skill by rarity: 45 / 50 / 55 / 62 / 70 / 80. Strike chance: 78 / 80 / 82 / 85 / 88 / 90%,
+0.25 points per level, cap 97%. Wage multiplier by rarity: 1.0 / 1.2 / 1.45 / 1.75 / 2.1 / 2.5.

## 2. Levels: universal upgrade tokens plus coins

- One token type for every crew member (Mo: fairer than per-role tokens, Mira would starve alone).
- Level L to L+1 costs round(L^1.6) + 1 tokens and round(15 x L^1.5) coins.
  Level 1 to 5: 23 tokens. Level 1 to 30: about 2,600 tokens and 28,000 coins per crew member.
- Tokens per sold haul: boat tier x crew on board x hold fill (0..1), +15% when the hold is full, rounded
  down. Tier 5, six crew, full hold: 34 tokens. A half hold pays half.
- Chests and the renown road add tokens.

## 3. Blueprints and stars

- Blueprints only ever belong to a crew member you already own. Spare ones are banked on the card.
- Rank-up costs 1 / 1 / 2 / 3 / 4 (White to Mythic, 11 in all from White).
- Focus: the player marks one crew member. When a chest blueprint drops, it is the focus crew's 75% of
  the time, otherwise a random owned crew member who is not yet at 5 stars.
- Pity: a blueprint is guaranteed within 40 chests opened (counter shared by every chest kind).
- Target pace: one focused crew member from White to Mythic level 30 in about 5 to 7 weeks at an hour a
  day; the whole roster in 8 to 9 months.
- Stars (Mobile Legends Adventure's enlightened stars): blueprints for a Mythic card buy stars 1 to 5,
  costing 2 / 3 / 4 / 5 / 6. Each star is +3% work speed and a star on the card. A starred crew member keeps
  everything through a prestige and is available from tier 1 again; unstarred crew unlock at their tier.
- A blueprint for a 5-star card converts into one blueprint of another owned crew member of the player's
  choice. There are no wildcards.

## 4. Tools (crew equipment cards)

- Tools come from chests, have a rarity (White to Mythic) and merge 2 into 1 of the next rarity.
- A tool belongs to a class: fisher, deckhand, engineer or navigator. Any rarity fits any crew member of
  that class. The captain can use fisher, deckhand and engineer tools (not navigator). Slots: section 1;
  the captain has 3.
- Bonus per tool by rarity: 3 / 5 / 7 / 10 / 13 / 17% to its job. Bonuses add up, capped at +50% per
  crew member. Percent bonuses suit strong crew best, which is intended.
- A fisher with a rod and a reel is a rod specialist; a rod and a net makes an all-rounder.

| Class | Tools and the job they speed up |
|---|---|
| Fisher | Rod (strike window and reel), Reel (reeling), Net needle (net set and haul), Bait knife (baiting pots and lines) |
| Deckhand | Gloves (sorting), Gaff (carrying), Fillet knife (table work), Boots (walking) |
| Engineer | Winch handle (net and pot winching), Oil can (fuel use, down), Toolbelt (repairs and engine work) |
| Navigator | Compass (ground thinning, down), Binoculars (bite speed, half rate), Charts (travel speed) |

- The market keeps only boat upgrades: hold, ice box, cooler, fuel tank, rod holder, net system, deep-line
  rig, crab pots, hulls, supplies. Fibreglass and Carbon rods leave the market; the captain's rod tool
  replaces them (its rarity picks the rod model: Blue+ fibreglass, Gold+ carbon).

## 5. Chests

| Chest | Where from | Tokens | Tools | Blueprint |
|---|---|---|---|---|
| Crate | each completed contract, first sale of the day | 8 x tier (min 8) | 1 | 3% |
| Sea chest | market, 400 + 300 x tier coins | 30 x tier (min 30) | 2, one Green+ | 8% |
| Captain's chest | renown road only for now (gems later) | 80 x tier (min 80) | 3, one Purple+ | 20% |

- Tool rarity odds per draw: White 60, Green 25, Blue 10, Purple 4, Gold 1 (Captain's chest guarantee
  re-rolls below Purple). Mythic tools only come from merging.
- Odds are shown in the game for every chest. Paid chests are never offered in Belgium.

## 6. Renown road (account progression; survives prestige)

- Renown = sum of all crew levels + 5 per rank-up gained + 10 per star.
- Milestones at 5, 10, 20, 30, 45, 60, 80, 100, 125, 150, then the gap grows by 5 every two milestones.
- Rewards: milestone 1 a blueprint of choice (the first Green rank-up comes in the first hour); every 5th a
  blueprint of choice; every 10th a Captain's chest; the rest alternate tokens (20 + 5 x index), a crate and
  a sea chest.
- Later rounds: battle-pass track, monthly challenges, crew tasks, fish album, captain level, harbour that
  grows, prestige seas.

## 7. Crew, tiers and starting rarity

| Crew | Role | Speciality | Tier | Starts |
|---|---|---|---|---|
| Mira | Navigator, first mate | Navigation | 1 | Gold |
| Noor | Deckhand | Sort | 1 | White |
| Dirk | Fisher | Rods (big fish) | 2 | Green |
| Tess | Fisher | Rods (shoal fish) | 2 | Green |
| Sam | Deckhand | Haul | 2 | Green |
| Kofi | Fisher | Nets (setting) | 3 | Blue |
| Rosa | Fisher | Nets (hauling) | 3 | Blue |
| Ana | Deckhand | Haul | 3 | Blue |
| Mats | Deckhand | Table | 4 | Purple |
| Lise | Fisher | Rods at night (jigs when the jig boat lands) | 4 | Purple |
| Ines | Engineer | Power (night, ice) | 4 | Purple |
| Olaf | Engineer | Power (engine, winches) | 5 | Gold |
| Pim | Fisher | Pots and lines | 5 | Gold |
| Tove | Deckhand | Sort (crabs, big fish) | 5 | Gold |

Mira is fixed aboard from tier 1 (the skiff) onward and never stands down. Berths stay navigator + tier.

## 8. Abilities

All abilities trigger by themselves: tiny passives, or automatic triggers on a condition or a timer. No
buttons, no combos. Green unlocks the passive, Purple the automatic ability, Mythic the strong one; Blue
and Gold add tool slots instead. Big multipliers only where the scope is narrow (one catch, one basket).

Builds the abilities support:
- Rod line, big fish: Dirk, Sam, Tove, Mira. Rod line, shoal fish: Tess, Noor, Ana.
- Net crew: Kofi sets, Rosa hauls, Noor and Ana clear the baskets, Olaf speeds the winch.
- Pots and lines: Pim baits, Mats makes the chum, Tove handles crabs, Olaf winches.
- Night shift: Lise, Ines, Dirk for the big night predators, Sam to carry them.

| Crew | Green, passive | Purple, automatic | Mythic, automatic |
|---|---|---|---|
| Mira | Chart reader: grounds thin out 15% slower | Shoal call: every 2 min, bites come 30% sooner at every rod and line for 20 s | Mate's eye: every 4 min, for 30 s every fish caught rolls its weight twice and keeps the heavier |
| Noor | Quick sort: sorts 10% faster | Same again: sorting the same species twice in a row makes her next sort 30% faster | Bucket brigade: when a net basket lands, she sorts its first 5 fish instantly |
| Dirk | Steady strike: strike window 15% longer | Rod line: when he lands a fish, the other rods bite 20% sooner for 15 s | Trophy hunter: every 3rd fish he lands is in the top quarter of its weight range |
| Tess | Quick reel: reels 15% faster | Feathers: 20% of her herring, mackerel and whiting catches bring up a second fish | String of feathers: every 2 min, her next herring, mackerel or whiting catch brings up 3 fish |
| Sam | Extra fish: carries 1 more fish per trip | Heavy lifter: fish over 3 kg don't slow him and he carries 2 of them | Shoulder load: every 2 min he carries a whole net basket in one trip |
| Kofi | Fast set: sets nets 15% faster | Good spot: when his net comes up over 80% full, the next soak is 25% shorter | Back-to-back: every 3rd net he hauls is reset instantly |
| Rosa | Strong back: hauls nets 15% faster | Full bag: every 3 min, the next net she hauls comes up 30% fuller | Shake out: when she hauls a net, its first 6 fish go straight to the hold, already sorted |
| Ana | Quick walk: walks 10% faster | Hand-off: each fish she brings to the sort table makes the next sort there 20% faster | Clear deck: once a minute, when 6 or more fish wait on deck, she takes them all in one sweep |
| Mats | Quick knife: table work 10% faster | Offcuts: every product job also makes 1 chum | Batch cut: every 3rd product job processes two fish at once |
| Lise | Night eyes: at night her bites come 20% sooner | Lamp lure: at night, every 2 min, every rod and line bites 25% sooner for 30 s | Deep night: at night every 4th fish she lands is a heavy predator in the top quarter of its weight |
| Ines | Headlamp: at night the whole crew works 5% faster | Ice watch: when the hold passes half full, the catch stops losing freshness for 3 min | Floodlights: at night, every 3 min, bites come 25% sooner and deck work is 15% faster for 40 s |
| Olaf | Tuned engine: 10% less fuel | Winch tune: every 2 min, nets and pots winch up 25% faster for 30 s | Full steam: trips out and home are 25% faster |
| Pim | Fast bait: baits pots and lines 25% faster | Chum saver: 30% of his baits don't use up the chum | Pot luck: every 5 min, the next pot or line he raises brings up an extra catch |
| Tove | Steady hands: crab pinches never stop her, crabs sort 20% faster | Grader: fish she sorts in the top quarter of their weight sell for 10% more | Keen eye: every 10th fish she sorts sells for double |

Mira's own trait, on top: First mate, every crew member aboard works 5% faster (8% once she is Mythic).

## 9. Build split (2026-10-25)

- Claude: data and rules (Cards, CardState, CardProgression, tools, chests, tokens, blueprints, focus,
  pity, stars, renown, save v3, market changes) with editor checks. Public API in section 10.
- Codex 1 (brief CREW-CARDS-UI-1): crew garage and card screens, chests in the market and the opening
  reveal, tool equip and merge, renown road, haul token toast; then the ability engine in the deck
  simulation and the 42 abilities, with checks.
- Codex 2 (brief CREW-FINAL-ART-1): Rosa, Ines and Tess portraits; White, Green and Mythic frames;
  chest, token, blueprint, star and tool icons.

## 10. Code API (Claude delivers; UI and abilities build on it)

- `CardRarity { White, Green, Blue, Purple, Gold, Mythic }`; `CardDef` gains `StartRarity` and three
  `AbilityDef { Id, Name, Text }` (Green, Purple, Mythic) plus Mira's `Trait`.
- `CardState { Id, Rarity, Level, Blueprints, Stars, ToolUids[3] }`; `ToolState { Uid, Kind, Rarity }`;
  `ToolKind` with `ToolInfo.Class(kind)` and `ToolInfo.Job(kind)`.
- `CardProgression`: `LevelCap`, `TokensForLevel`, `CoinsForLevel`, `BlueprintsToRankUp`,
  `BlueprintsForStar`, `ToolSlots`, `ToolBonus`, `WorkMult`, `OffSkill`, `StrikeChance`, `Wage`,
  `HasAbility(rarity, tier)`.
- `GameState`: `Tokens`, `Tools`, `FocusCard`, `ChestPity`, `Renown`, `RenownClaimed`;
  `LevelUpCard`, `LevelUpCardToCap`, `RankUpCard`, `SetFocus`, `EquipTool`, `UnequipTool`, `MergeTools`,
  `BuyChest`, `OpenChest(ChestKind) -> ChestResult`, `GrantChest`, `AwardHaulTokens(kgSold) -> int`,
  `ClaimRenown(index, choiceCardId)`, `PendingChests`.

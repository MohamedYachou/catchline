# Weight storage, specimen pricing and deep nets

Codex 1 (Windows app), 2026-10-16. Current implementation supersedes NET015's
count-based cargo/yield and 80-coin shallow replacement tuning. Pickup history,
ownership and exact verification boundaries are in `comms.md`, WEIGHT020 A–G.

## Player rules

| Hull | Base hold | With the existing Big cooler upgrade |
|---|---:|---:|
| Rowboat | 4 kg | 6 kg |
| Skiff | 18 kg | 27 kg |
| Compact fisher | 24 kg | 36 kg |

Big cooler still costs 60 coins, preserves its existing saved upgrade ID, and now
adds 50% capacity on every hull. Hull IDs and crew/grid layouts are unchanged.
Kilograms are fish cargo capacity, not total vessel displacement or crew weight.

Any whole fish can enter while the stored mass is strictly below capacity. That
fish may overfill the hold by any amount; further inserts are rejected. A net batch
is processed fish by fish, not treated as one fish. Captain/crew deliveries recheck
at their actual storage callback, so simultaneous animations never grant two final
spaces. Remaining basket fish are retained, even if the fitted net used its last
use. Returning warns about the same carried-first/deck-order overflow that the
actual departure will discard; there is no new automatic forced return.

HUD, chart, world hold label, shop and storage upgrade wording use kg. Individual
fish counts remain meaningful for the journal, contracts, haul receipts and the
existing sixteen-fish refit milestone; those are not hidden cargo slot caps.

## Specimen value and market

Each species has a base rate. Its relative specimen size in its authored min/max
range increases that rate smoothly from 1x at minimum size to 1.5x at maximum.
The premium is capped, including oversized fish from old saves. Thus the same
mass of larger specimens earns more than smaller specimens of that species.
Species identity still matters; not every large cheap species beats every small
premium species in every market.

Base coins/kg in saved species order: Herring12, Mackerel13, Pollock15, Sea bass19,
Conger18, Plaice16, Cod17, Whiting14, Red mullet18, Turbot22. Existing sale rounding,
freshness and contract rewards apply after specimen pricing. Quote and actual
sale/receipt paths share `ValueOf`; the market catalogue labels its base rate
explicitly and mentions the size bonus.

Market pressure now scales with sold kg: each half kilogram applies the previous
0.97 price multiplier. Existing market recovery and 50% floor remain. This avoids
charging much more saturation for the same weight of small fish. Stock depletion
still counts catches; journal and contract quantities retain individual fish.

## Net preparation and wear

Supplies on the compact fisher has two net product cards and a loadout selector
at the top. Selection is harbour-only. Inventory is saved independently:

| Method | Purchase | Lifetime | Soak | Catch direction |
|---|---:|---|---:|---|
| Shallow | 30 coins | Reusable; tear destroys one | 20 s | Local schooling species; smaller specimens |
| Deep | 100 coins | 3 uses per net | 30 s | Local full species pool; larger specimens |

Shallow stock still starts at three including the fitted net, rack limit four.
Deep stock starts at zero, rack limit three including fitted. Every deep-net entry
stores its remaining uses; exhausted fitted nets rotate to the next reserve.

A completed deep haul spends one use whether it succeeds or fails. Failure loses
that catch, not the other uses or reserves. A failed setting minigame also spends
one use. Clean setting and cancellation spend none. Abandoning a soaking/ready net
forfeits its unlanded catch through the existing departure confirmation; it awards
no fish and does not refund a previously spent use. No automatic net-type fallback.

Captain setting and hauling retain the existing tap-only skill games and two
cumulative mistakes. There is no random captain failure. A worker has exactly an
80% successful recovery chance, rolled once at completion; a failed shallow haul
destroys one shallow net, a failed deep haul spends one deep use. Existing Fish/Nets
duties, concurrent actor passage and automatic whole-batch unloading remain.

Catch rewards are mass budgets, not guaranteed fish counts. Ground-specific mass
uses the local species table's average weights; deep target mass is roughly twice
shallow. Depletion reduces the target. Only local species are rolled; deep weighting
favours heavier local species and sizes in the top35% of their range, shallow sizes
in the lower10–50%. Whole final fish can exceed a net's mass target. A 64-fish safety
limit bounds malformed future content; it is not the normal reward rule. No claim
that a deep net always gives twice the number of fish, or guarantees rare species.

## Balance evidence and limitations

Production code was sampled across 500 seeds per ground and method (5,000 hauls).
Values below are fresh, initially unsaturated sale quotes including within-haul
market impact. They exclude fuel, food, crew, travel/handling time and losses from
existing market saturation, freshness, hold overflow or player mistakes.

| Ground | Shallow mean kg / gross coins | Deep mean kg / gross coins |
|---|---:|---:|
| Harbour mouth | 1.81 / 26.74 | 3.56 / 64.18 |
| Kelp bank | 2.96 / 47.88 | 5.95 / 127.07 |
| Sandbar | 3.47 / 47.63 | 7.79 / 200.74 |
| Rocky point | 5.99 / 91.74 | 13.14 / 304.84 |
| Deep channel | 10.51 / 140.14 | 22.80 / 494.42 |

At Harbour mouth, a worker's expected contribution after net expense is about
15.40 coins per shallow attempt and 18.01 per deep attempt, before voyage costs.
Deep's longer cycle makes shallow competitive there. On later grounds deep nets
are substantial money makers; a deep-channel haul can fill the compact hold alone,
so running rods concurrently creates overflow rather than unlimited extra income.
These are first-pass balance targets, not measured human profit/minute or a claim
that every loadout/ground/market is profitable. See `docs/screens/weight020/balance.csv`.

## Source and migration

- `VoyageStorage`: actual mass/fullness/atomic insertion, no cached count budget.
- `GameState` / `GameData`: kg capacities, upgrade, specimen prices, market exponent,
  additive save fields with existing version1 and stable upgrade/species/hull IDs.
- `GameStateNetLoadout`: selected method, purchase, per-net uses and reserve rotation.
- `VoyageNetLoadout`: harbour preflight and local mass range; `VoyageNet` integrates
  cycle ownership/debits/yield, preserving authored stern float/rope visuals.
- `VoyageNetUnload` / `VoyageGame` / `VoyageHaul`: stow and departure order/capacity.
- Existing HUD/chart/shop/goal components show real state using supplied artwork.

Older saves retain each fish's actual weight, unsold cargo, owned cooler, money,
crew, charts and market state. Missing deep fields mean no deep stock and shallow
selection. Explicit exhausted zero remains zero; list entries are clamped/sanitized
on load. No existing cargo is truncated to the new limit. Saves happen at harbour
as before; this does not add in-voyage resume.

## Checks and preview

`WeightNetChecks.Regression` runs the focused migration/storage/pricing/deep-net
tests plus the full prior first-voyage, skiff, automation, UI, tap-net, inventory,
crew, catch reward, illustrated chart and all-map clearance regression suites.
Native captures include real world+Canvas at1440x900 and844x390, actual supplies
loadout and scrolled deep purchase. Physical touch and mobile GPU profiling remain
unverified. Existing secondary phone typography and broader content balance remain
separate work.

Separate SessionOnly preview: `Catchline-sim/Builds/Weight020/Catchline.exe`.
Explicit `-deep-net-trial` starts the compact boat/200coins/three hired crew with
two full deep nets and deep selected. These are isolated test supplies, not gifts
to normal saves. `-native-display` requests the laptop's borderless native display.
No foreground launch is part of this implementation task.

Conditions, seasons, ranks and journal expansion remain separate design work.

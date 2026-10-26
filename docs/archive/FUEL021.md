# Fuel and departure — FUEL021

Mo's16October update combines WEIGHT020 storage/pricing/deep nets, CATCH018 rewards,
CHART017 illustrated chart and CREW016 character polish with fuel and preparation.

## Rules

Early boats have no active food purchase, consumption or hunger penalty. Existing
crew/action work runs at the former70%pace as its baseline. A future cook/food bonus
is a future feature; no cook is sold or invented in this update. Powered travel keeps
its engine timing; manual rowing follows the crew baseline.

Powered boats have10minutes of fuel,20with the100coin extra-tank upgrade. The old
LunchTin enum/owned-save ID is deliberately retained and now grants tank capacity.
No player needs to repurchase an already owned upgrade. Existing legacy food fields
are dormant save/fixture data; FillFood cannot charge coins.

Fuel burns at1minute per actual simulated minute during outward travel, fishing and
return, independent of crew count. Pausing stops simulation. At10%fuel while fishing,
the boat immediately heads home, using the existing departure handling: carried/deck
fish are stowed individually as space permits, unstored overflow and deployed catch
are forfeited. The final10%is reserved for the home leg:1minute on the base tank,
2minutes with the upgrade. Existing return travel is shorter than either reserve.
There is no dock refill. Fuel persists as fractional minutes and is shown as percent.

Refilling costs1coin per missing minute, rounded up, matching the former provision
unit cost. Full/insufficient-funds purchases never charge. First shipyard refit includes
its first tank. The rowboat remains oar-powered and needs no fuel. Old numeric fuel
loads into the new minutes field and is clamped to the owned tank capacity after
loading upgrades. Empty fuel never silently refills on save/load.

## Ready to leave

Set sail opens a native coastal manifest; only Let's go starts the trip. The manifest
shows destination, live coins, fuel percent/tank, worms/squid, free scraps, actual crew
and contract voyages, selected net and stock/remaining uses. Refuel and bait controls
buy actual supplies at the same shop prices and save normal games. Disabled full,
unaffordable and no-fuel departure states are explicit. Back/Escape returns to port.
Crew hiring, upgrades and net purchases/loadout remain in the real harbour shops.

## Verification and release

Runner: docs/tools/check-fuel021.ps1. Uses independent Catchline-rewards-sim; never
batchmodes main. All native test fixtures/builds are SessionOnly and cannot read or
write the player's save. FuelDepartureChecks covers refill/persistence/thresholds,
actual simulation/time drain, harbour reserve and departure native control invocations.
WeightNetChecks includes Codex1's final exact-double storage/departure boundary test.
Full combined regression, native captures and exact build/startup evidence are logged
in comms.md. Screenshots are actual production Canvas/world captures with authored
inventory fixtures, not physical mouse/mobile acceptance or measured play balance.

Build: Catchline-rewards-sim/Builds/Fuel021/Catchline.exe. User explicitly requested
launch of the combined update; visible session uses isolated deep-net trial inventory.

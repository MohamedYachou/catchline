# PREP035 - Tier 4 working prep table

The approved Prep fisher has a real two-person deckhand station. This continues TIER033; the hull/art dimensions are unchanged.

## Play

Open **Catchline - Tier 4 Test** on the desktop after the updated build is installed. The isolated trial starts with two fishermen, one delivery hand and one Prep hand. Open **Prep table / chum** at bottom left to change orders and assign a second hand. **Crew duties** also offers Fish, Nets and Prep. No more than two deckhands can be assigned to Prep. Crew remain ordinary temporary contracts.

- Default priority: maintain 10 chum, then prepare eligible raw fish. Reserved/in-progress chum counts toward the target. When a hook uses chum, the order becomes eligible again. With no eligible small fish, the hand falls back to preparation.
- Priority swap changes which eligible order is chosen next; jobs already started finish. The first pass uses a swap control, not drag-and-drop.
- Target cycles 10 / 20 / off. Chum input weight cycles 1 / 2 / 0.5 kg; a 10-coin maximum input value also applies. One eligible whole raw fish yields one chum.
- Preparation minimum cycles all / 1 kg / 3 kg. Species filtering and arbitrary numeric text entry are deferred.
- Chum is earned at the table, cannot be bought or saved, and expires on returning to port, including chum left on ready hooks. It is consumed before squid/worms and strongly favours heavier local species and specimens in the top quarter of their species weight range. It does not import species from another map.
- Preparation keeps the same fish object, weight, species and contract eligibility; it grants one 25% market premium. It freezes current quality permanently. It does not restore quality already lost. Prepared fish never spoils, even without the IceBox upgrade. Front raw buckets continue normal freshness loss; ice coolers protect raw inputs too. Prepared boxes need no upgrade.
- Fish remain in cargo while reserved so two jobs cannot manufacture spare hold capacity. Each slot claims a distinct fish. Changing duty, cancellation and returning release claims without losing unfinished inputs. Work continues at full cargo capacity and uses normal crew pace and voyage fuel.

The captain cutting minigame, species filters, drag reordering and a final paid Tier 4 progression unlock are not in this pass. Tier 4 remains the save-isolated trial. With two hands assigned to Prep, arrange someone to deliver rod catches or carry them yourself.

## Implementation

`VoyagePrepOrders.cs` owns orders, reservations, station actions, actual table fish visuals and native UI. `CaughtFish.Prepared` and `PreparedQuality` survive port copy and JSON save/load. Saved `PrepOrderSettings` have legacy defaults; `Chum` is voyage-only. Baited rods remember chum separately from squid, and chum fish rolls stay in the current map pool. Existing work animation is reused for table actions.

## Verification

First isolated run: `docs/tools/check.ps1 -Name prep035 -Method Catchline.EditorTools.PrepOrdersChecks.Run` exit0; PREP035, TIER033 and COMPACT FISHER checks passed. Exact target with concurrent workers, eligibility/fallback/refill, cancellation, third worker rejection, no duplicate premium, spoilage/ice, port/save preservation, voyage-only stock, native UI callbacks and actual quote/payout covered. Source checks are not physical touch acceptance.

Final suite/build and native capture evidence will be appended after completion.

Final behaviour/build: `docs/tools/check.ps1 -Name prep035-final -Method Catchline.EditorTools.PrepOrdersChecks.ValidateAndBuild` exit0. PREP035, TIER033 and COMPACT FISHER suites passed; successful standalone build. Added regression proves already-deteriorated fish keeps its frozen quality after preparation. Native desktop first pass inspected: both station occupants and table fish visible, readable 2/2 work/order/stock controls. First landscape working capture retained the previous modal for one frame; capture hook now waits a frame after each modal state change and also captures Crew duties. Behaviour source unchanged by this capture-only fix; rebuild/recapture pending.

Final capture-only rebuild `prep035-capture` exit0. Final rendered Windows player `Logs/prep035-native-final.log` confirms TEST/no-save mode and PREP035 NATIVE CAPTURES COMPLETE, no native exceptions. Inspected all six final PNGs in `docs/screens/prep035`: working table, order modal and duties modal at1440x900 and844x390; both real station workers and fish visible, all controls contained/readable. Scripted native captures verify presentation, not physical touch acceptance. Captain mini-game/drag/species filters remain explicitly deferred.

Updated `Catchline-play/Tier033` from the verified build. Desktop **Catchline - Tier 4 Test** still targets that executable with `-prepboat-trial -native-display`; executable, game assembly and resources hashes match scratch build (`docs/screens/prep035/installed-build.json`). No real launcher/save changes and no capture process left running. Source UTF8/hash receipt: `verified-source.json`. Temporary PREP035 source backup successfully removed after verification; older task backup leftovers untouched. No commit or push.

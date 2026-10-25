# Deck berth verification - DECK-BERTHS-1

Codex 1 (Windows app). Completed native geometry review and required regression.

| Hull | Card crew (Mira included) | Captain | Card rest tiles |
|---|---:|---:|---|
| Rowboat | 0 | 1 | none |
| Skiff | 2 | 1 | (0,1), (3,1) |
| Compact fisher | 4 | 1 | (30,2), (9,20), (23,11), (6,2) |
| Prep fisher | 6 | 1 | (10,26), (37,26), (23,11), (45,2), (22,4), (15,21) |
| Buoy fisher | 8 | 1 | (39,28), (70,16), (30,7), (63,32), (60,2), (19,24), (30,24), (12,25) |

Tier 3 has five card berths in the card rules and no hull yet. Captain positions are unchanged except Skiff (3,0), moved away from its sort table.

## Method

The `.cs.txt` files are reproducible fixtures, copied as executable `.cs` files only into sibling `Catchline-sim`. The scene and executable exist only there. The native launch requires `SessionOnly=true` (no save reads or writes), grants trial cards, fills deployment, sails to Harbour mouth, then stops every person at the actual production indexed rest. This tests a full idle deployment, not dynamic crowd routing while working.

`<hull>.png` is the ordinary native 1440x900 HUD, `<hull>-phone.png` is 844x390, and `<hull>-deck.png` supplements them with a hull-relative steep camera and the canvas hidden. `<hull>-reverse.png` adds a lower reverse angle to expose canopy-covered crew. No crew or boat mesh is moved or hidden for either diagnostic view. Roofs can occlude crew beneath a canopy.

The graph checks require exact counts, unique captain and crew positions, walkable cells, routes to every station access, at least 0.55m between rest centres, and rests outside gear work cells (navigation and bait access are allowed). Graph checks do not establish mesh clearance: opened native views are required separately.

## Checks

- Final graph and native build: `Catchline-sim/Logs/check-berth-final-build.log`, Unity exit 0.
- The same final build passed M2 data, 286 crew ability assertions, M2 checks and CREW ABILITY INTEGRATION REGRESSION. Earlier stale tier-test failures were fixed by the lead and are superseded by this complete pass; Codex 1 did not edit tests.
- Final native recapture: `Catchline-sim/Logs/berths-native-final.log` completed with failures=0; exact card counts 2/4/6/8 plus captain.
- `build-sources.json` records 231 scratch source/station inputs. The lead's VoyageInterfaceCrew.cs and VoyageInterfaceVoyage.cs had advanced after scratch sync; the berth and card-core sources matched. These captures do not claim acceptance of that later UI work.
- CREW-TIERS READY is now logged; pacing follow-up begins after this handoff.

## Geometry review

The first clear Buoy overhead caught two rests inside existing ice coolers even though their graph cells were walkable. Those rests were moved to (39,28) and (30,7). The final graph and opened captures pass. Skiff has three distinct bodies, captain off the sort table, with hold/gear access clear. Compact has five bodies, Prep seven and Buoy nine across the overhead and reverse angles. All card rests are separate and clear of tables, baskets and coolers. Reverse views expose crew beneath the open canopies. All desktop, phone and diagnostic views were opened during review. These are static idle placement checks; moving crews and UI polish remain outside this acceptance.

Implementation is restricted to the Hulls block in GameData.cs and RestFor in VoyageGame.cs; VoyageDeck.cs is unchanged. No git operation or player-save access. This is a test-player evidence build, not installation or player acceptance.

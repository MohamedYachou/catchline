# Jig boat acceptance evidence

Status: technical delivery complete; Claude review and Mo player acceptance remain.

- [Implementation and limits](REPORT.md)
- [Hull comparison audit](COMPARISONS.md) and [full diff](current-comparison.diff)
- [Native FBX measurements](native-measure.txt)
- [Import byte receipt](import-receipt.json)
- [Full regression summary](jig-regression.txt), [log](check-jig-regression.log), [scratch source hashes](regression-source-hashes.json)

The route sweep passed 792 directed routes across all six hulls and eleven maps. Its legacy log denominator says11/5; the actual inventory is66 hull/map combinations. Timing warnings remain recorded: physical route times span2.15-34.65seconds and are not all within the old target. They are warnings, not a new timing acceptance claim.

Harbour checks passed33 sea lanes, five existing hull round trips, and the Jig Deep channel round trip (out28s/home29s). Ability286/tutorial217/M2/bite/cage checks passed. The source hashes record the exact scratch snapshot before the later hatch hinge/night-lighting focused build.

[Hull pacing](HULL-PACING.md), [full pacing experiment](cards-pacing-generated.md), [per-image review and hashes](visual-review.json), and [native player log](native-player.log) record the final outcomes. All10PNG frames were individually opened. Work/night captures show the normal deck; final player completed refit/crew/cast/home.

| View | Desktop | Landscape phone |
|---|---|---|
| refit-card | [1440x900](refit-card-1440.png) | [844x390](refit-card-844.png) |
| harbour | [1440x900](harbour-1440.png) | [844x390](harbour-844.png) |
| anchor-day | [1440x900](anchor-day-1440.png) | [844x390](anchor-day-844.png) |
| deck-working | [1440x900](deck-working-1440.png) | [844x390](deck-working-844.png) |
| anchor-night | [1440x900](anchor-night-1440.png) | [844x390](anchor-night-844.png) |

Baseline pacing never reaches Compact under the retained chest-buying policy; see the report for censored dates and higher-price sensitivity cases. Lamp spill is subtle at phone scale; no bloom or held UI changes were introduced. No installed player, shortcut or player save is changed. Claude owns review and commit; Mo owns player acceptance.

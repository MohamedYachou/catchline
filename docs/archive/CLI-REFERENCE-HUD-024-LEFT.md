# UI-024 left reference HUD

Owner: Codex 2 (WSL CLI) / reference-left, Mo-authorized Sol delegate.

`VoyageInterfaceGoals.cs` supplies `VoyageGame.InterfaceReferenceGoals()`.
The lead wires it into the fishing interface and owns all shared artwork,
fonts, colours, line work, corner treatments and primitives. No gameplay,
save or progression rules are changed. No Next Milestone is introduced.

## Layout contract

Every rectangle goes through the lead's `ReferenceRect(x,y,w,h)` using the
1672 × 941 reference and height scale `ih / 941`, anchored to the left.
Text sizes remain reference pixels; the shared label primitive scales them.

| Element | Reference x,y,w,h | Text size |
| --- | --- | --- |
| Status panel | 20,25,320,65 | — |
| Sun | 31,36,44,44 | — |
| Day | 91,35,80,23 | 18 |
| Elapsed | 91,58,80,24 | 20 bold |
| Coin | 194,37,38,41 | — |
| Balance | 237,36,96,38 | 29 bold |
| Goal panel | 20,130,220,104 | — |
| Target | 31,137,24,25 | — |
| Current Goal | 64,138,166,23 | 16 bold |
| Crate | 30,178,39,43 | — |
| Objective | 75,172,155,20 | 13 |
| Progress | 75,200,114,13 | — |
| Count | 197,198,34,20 | 13 bold centered |

The status separator at reference x177 and goal title rule belong to the
shared panel artwork. Both panels call `Block` to protect world clicks.
Icon rectangles now follow actual extractor `source_bounds`, preserving
original sizes and aspect ratios rather than squeezing the first measured
slots. The shared static Current Goal caption preserves its original
106 × 20 raster size inside the label slot. Review found that the initial
extractor cleared the original goal rule; restoration belongs to the lead.

## Real data

- Day is `State.Voyage`, the existing voyage unit. There is no calendar.
- The time line is elapsed `mm:ss` below 100 minutes, then `HhMM` below
  100 hours, then `DdHH` (days and remaining hours), floored from nonnegative
  `SimTime - voyageStart`; `SetSail` resets the start, simulation pause
  freezes it. The reference's 10:24 is not a fabricated game clock.
- Balance uses actual `State.Coins` with the existing `N0` convention below
  10,000 magnitude. Larger values use rounded conventional k/M/B units to
  fit the same slot; this is display rounding and does not change coins.
- First active contract wins: `Sell {contract.Title}`, actual
  `Delivered / Count`. Fish aboard are not yet sold, so the bar does not
  count them as delivered. This deliberately avoids the old projected count.
- Without a contract, rowboat shows the existing sold-haul record against
  `GameData.SkiffFishGoal` (currently 16). After that requirement is met,
  it shows actual coins toward `GameData.SkiffCost` (currently 1,500),
  using a percentage in the narrow counter. `CanRefit` changes the copy
  to “Skiff refit ready”; it does not execute a refit.
- An upgraded hull without a contract shows actual `Cooler.Count` against
  `State.CoolerCapacity`. Bar fill is clamped; denominators guard zero.

## Integration and retained instruments

Dependencies: `ReferenceRect`, shared `FishReferenceStyle.PanelKind.Status/Goal`,
`FishReferenceStyle.Icon.Sun/Coin/Target/Crate`, and
`CoastalCanvas.ReferencePanel/ReferenceIcon/ReferenceLabel/ReferenceBar`.
Call after `coastalUi.Begin` with `iw`/`ih` established. The delegate does
not wire or edit `VoyageInterface.cs`.

The old instrument at logical (18,18) overlaps these new panels and should
be moved by the lead. Suggested retained storage/supply strip: below the
goal at reference y252 with reference width320, keeping secured hold count,
quoted value, bait and food. Existing extra contract summaries can follow
it. This suggestion is not implemented; the lead must check phone fit and
boat/action occlusion. Keep the existing Head home/pause controls accessible
when moving the right-side HUD.

## Validation limits

Source-level checks cover exact agreed rectangle calls, shared-only style
usage, existing state fields, guarded/clamped progress and absence of save
mutations. These are not C# compilation or native visual/input acceptance.
The lead owns integration, native capture, long-text/numeric fit, same-resolution
overlay/difference and landscape-phone checks. No pixel-perfect or exact-font
claim is made. No Unity/scratch/foreground apps or commits are used here.

## Focused native state matrix — not yet run

Run through the integrated fishing HUD at the original 1672 × 941 and
landscape-phone viewport, including default and Larger type. Codex1 NET010
currently owns scratch/native execution; coordinate rather than launch
another process. These are acceptance scenarios, not source-coordinate tests.

| Setup / action | Expected left HUD | Check |
| --- | --- | --- |
| Day12, coins2845, elapsed624s | Day12, 10:24, localized full2,845 balance | Compare static contour/icon/caption to original; full balance stays inside card. |
| First contract herring5, delivered2;3 matching fish aboard | Sell5herring,2/5,40%bar | Pending aboard fish do not falsely count as sold; relocated hold/value remain visible. |
| Sell those3fish at harbour, return fishing | Completed contract removed; next active contract or fallback shown | No stale previous objective/count/bar after sale and next voyage. |
| Multiple active contracts, first partial | First list entry only | First-contract choice is deterministic; secondary contract summaries remain accessible if integrated. |
| No contract, Hull0, BestVoyageFish0; full10fish hold | Sell16in one haul,0/16 | Goal is sold-haul record; current hold is shown separately, not falsely counted as record. |
| No contract, Hull0, best15,1500coins | Sold-haul requirement15/16 | Coins alone do not bypass existing fish requirement. |
| No contract, Hull0, best16,750coins | Save1,500coins,50%,half bar | Existing refit requirement and current balance only. |
| Same with1499 then1500coins |99% then Skiff refit ready/100% | Goal transition is accurate; no refit triggered by drawing. |
| No contract, Hull1 then Hull2, empty/partial/full Cooler | Fill the hold; actual count/capacity | Uses hull's real capacity; fullbar clamps; actions/return remain visible. |
| Balance9999,10000,999999,1000000,int.MaxValue | Full9,999;10k;1000k;1M;2.15B (rounded) | Boundary rounding is readable, no overlap with icon/panel; save balance unchanged. |
| Elapsed5999,6000,359999,360000s |99:59;1h40;99h59;4d04 | Units are elapsed duration; strings fit clock slot. |
| Pause/unpause; next SetSail | Time stops/resumes; next voyage resets to00:00 | Display follows simulation clock; no time-of-day simulation introduced. |
| Longest current contract labels: Sell9mackerel, Sell3redmullet, Sell1congereel | One readable line in155px objective slot | Shared Nunito approximation may shrink within its allowed range; no clipping or spill. |
| Panel clicks and fishing clicks near panel edges | Left cards block world input; nearby world actions remain operable | Actual raycast/Block integration, not inferred from source. |

Spacing in matrix values is compact for scanability; rendered text contains
normal word spaces and fraction counters omit spaces. Shared Nunito500/800
dynamic fonts are approximations; native-sized raster static captions come
from the original. Full current labels already include the contract count
and species once (`Sell {contract.Title}`), so no duplicate wording was added.

# CHART-011 nautical chart handoff

Codex 1 (Windows app) / chart: finished source delivery under lead. No commit or native execution. New files only: `Assets/Scripts/Game/VoyageChart.cs`, `Assets/Editor/ChartChecks.cs`, this note. No added resources, downloaded artwork, shared Canvas/HUD/travel/map-data changes or existing backups overwritten.

## Integration

Replace the body of existing `InterfaceChart()` with `InterfaceNauticalChart();`. The new partial reads existing `catalog`, `catalogWidth`, `catalogY`, `chartFocus`, `State` and normal UI helpers. Root retains sole ownership of that hook and build/scratch. Copy both new scripts to scratch before compile; let Unity generate metadata using normal import.

The retained `NauticalChartGraphic : MaskableGraphic` is created as one child of CoastalCanvas's retained `chart/nautical/field` Box. It inherits catalogue masking/lifecycle; all interactive labels/buttons remain ordinary CoastalCanvas elements and InvokeInterface controls. Geometry only updates when focus/destination/known state or RectTransform size changes. No per-frame texture generation, no resource dependency. Mesh stays below Canvas vertex budget; checks assert actual vertex limits/bounds.

## Composition / behavior

Southern coast with a harbour inlet and breakwaters; layered coastal shoals and seabed contours; kelp/sand/rock/deep grounds; divided schematic scale/compass/neatline; five real location symbols/names and dashed routes. Gold marks selected sailing destination; navy ring marks inspected ground. Solid marks mean known chart, hollow marks mean purchase required. Geometry and hit targets share `NauticalChartPoint` and the actual RouteDirection X/Z bearing (north is -Z). Route lengths are explicitly schematic. Neither GameData.MapPos nor RouteDirection is changed.

The chart title/field/legend lead to a real focus detail below, then preserved active/available harbour contracts. Focus action displays actual fish table, hull-adjusted journey seconds, round-trip fuel, richness and correct lock/price/shortfall. Inspecting a ground leaves SelectedSpot unchanged; choosing an owned chart is free, purchase calls existing BuyChart and charges once before selection/save. Contract action verifies the offer still exists before taking it, preventing repeated stale callbacks from duplicating it.

Existing `chart/select`, `chart/focus/title`, `chart/fish`, `chart/stocks`, `chart/stocklabel`, `offer/{i}/take`, and contract IDs remain usable. Marker IDs are now `chart/nautical/pin/{i}`; root may need to update any older tests that addressed chart/pin/{i}. No gameplay/progression/fish/economy modifications.

## Checks / native next step

Source whitespace check clean. No compile, runtime render, physical input or visual acceptance claimed by this delegate. Lead native-render review is essential; source inspection alone does not prove this map attractive or readable.

Run `Catchline.EditorTools.ChartChecks.Run` in Catchline-sim for actual focus controls, inspection-vs-selected state, insufficient/exact funds purchase, no double charging, free selection, contract state/cap/stale callback, five true bearings, geometry bounds/finite vertices and vertex budget, marker44+logical targets, supplied fonts and 1920x1080 /1440x900 /844x390 layouts. `ChartChecks.Capture` first runs that fixture and writes real combined scene/Canvas pairs into `Logs/chart011` at those sizes, plus focused Sandbar. Captures reuse ReferenceHudChecks.Shot. No tests/build were run here under root ownership constraints.

Inspect top map at desktop/laptop and phone, scroll to destination details and contracts, verify actual name/state overlap and text fit, click/scroll behavior and unchanged reference HUD. Root owns any final integrated corrections. Map max400logical-height fits most desktop catalogue viewport; landscape phone scrolls through the chart and detail. Phone labels remain logical16px and follow existing Canvas scaling; native physical legibility is not claimed. Schematic scale intentionally contains no invented miles/depth measurements.

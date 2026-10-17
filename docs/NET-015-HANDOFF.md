# NET015 / SEA014 — 2026-10-16 — Codex 1 (Windows app)

Current preview: C:/Users/momoy/Projects/Catchline-sim/Builds/Net015/Catchline.exe
Flags: -netboat-trial -native-display. Isolated compact fisher, 200coins,
2fishers/1deckhand,60bait/full food,3usable nets. Real save untouched.

## Implemented

- Every fishing map goes through an all-mesh clearance pass. Piers/piles/props
  and clipped water-crossing triangle edges count. A permanent9.6m-wide open
  strip follows the boat's fore/aft axis, with unlimited length; wider hulls
  expand it with2m side clearance. Complete dioramas move together.
- Five environment FBXs retain Read/Write geometry in standalone builds.
  Earlier editor-only clearance evidence missed their stripped CPU meshes.
  Future unreadable assets use conservative bounds as a fail-safe.
- Setting: three timing taps inside a green sweep band. Hauling: single taps
  build tension/progress. Best gains/least decay near red; cold tension loses
  progress quickly and red loses it faster. Holding does not repeat input.
- Two cumulative mistakes across a cycle tear exactly one net and lose the
  unlanded batch. Captain failure is skill based. Cancellation retains wear
  and ready catch, without rerolling fish or consuming a spare.
- Worker recovery has one80%-safe/20%-tear roll at successful haul completion;
  setting does not also roll. Worker setting2s/haul5s, soak20s, yield3–5local
  schooling fish. Total cycle around30s including active work and delivery,
  depending on walking and player rhythm.
- Clean cycles reuse the fitted net. Start3total/cap4; replacements80coins
  through Supplies. New saves preserve zero; old saves migrate to default3.
- Automatic entire-batch unloading, capacity overflow safety and concurrent
  captain/deckhand deliveries remain. Existing starter/skiff paths retained.

## Evidence

check-net015-final.log exit0: full prior regression + economy/save/native-shop
checks +5maps x3hulls and14m-long/8m-beam future fixture + actual tap mechanics,
tears, lazy-input regression, tension-dependent progress loss, exact worker.8
boundary, automatic batch and concurrent deliveries. Source helper Sol6.1
completed inventory/shop/save and adapted compact fixtures; all released.
check-net015-visual-final.log exit0: focused behavior/capture/build after gauge
color fix. check-net015-release.log exit0: final build after source encoding fix.
Native world+Canvas images inspected: docs/screens/net015 and sea014.
Standalone headless startup passed with no mesh-read errors, then stopped.
Rendered Net015 startup reached trial and native2560x1440, alive PID30692,
unique Logs/net015-visible.log; no exceptions or mesh-read errors at startup.
Compilation/headless/captures do not prove physical touch feel or Mo acceptance.

## Limits / pickup

80coin replacement cost and two-mistake tolerance are first-pass tuning.
At Harbour mouth, average small-school batch gross is only about17coins before
freshness/market effects. With20% worker tears,80coin replacements can make
net-only automation unprofitable there; captain skill or richer grounds changes
this. Do not silently call the worker economy balanced: tune price/grade/yield
with Mo before treating this as finished production progression.
Existing seabed rectangular edges and kelp art remain visually rough. Main
harbour shop berth geometry is separate; this reserve applies to fishing maps.
Readable-map CPU memory/startup cost has not been separately profiled on mobile.
No commit/stage/reset/push. Existing unrelated dirty work preserved.

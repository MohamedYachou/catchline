# Harbour and travel plan (decided 2026-10-24)

Mo: "the base upgrades with tiers", "tier 5 is too big for the harbour", the map trip "just stays still and boom
youre there", Codex's earlier trip "drives trough islands", and a beeline out of the harbour is "really barebones and
boring". Mo approved ideas 1-5 below; idea 6 is a to-do.

## 1. One growing harbour

Gull Harbour stays one place and grows with the boat. The camera frames the current boat's berth and the buildings
that serve it. Shops keep their tap bubbles, and every shop is also in the tab bar, so nothing is lost when a
building isn't on screen.

### Berths, shore to open water (hull index -> berth)

| Berth | Where | Boats |
|---|---|---|
| Beach slipway | west end, sand ramp into the water | Rowboat (tiers 1-2), bow up the ramp |
| Pontoon | floating pontoon out from the west quay | Skiff (tiers 3-4), alongside |
| Fish quay | the stone quay in front of the market, with a crane | Compact and Prep fisher, alongside |
| Outer wharf | inner face of the east breakwater, near the lighthouse | Buoy fisher (tier 5+), alongside |

Each berth has two to three slots. The player's boat takes slot 0 of its berth.

### Old boats stay, other fishermen fill the rest

- Every hull the player has owned before stays moored at its own berth, in the player's colours.
- Empty slots hold other fishermen's boats (colour variants). Bigger berths show bigger boats, so the next tier is
  always visible across the water.

### Buildings arrive with the tiers

| Hull | New on the quay | Shop tab it hosts |
|---|---|---|
| Rowboat | Market stall, harbour master hut with a notice board, supplies shed | Market, Harbour master, Crew (notice board), Supplies + Chandlery (shed) |
| Skiff | Crew office, chandlery, fuel dock on the pontoon, boatyard | Crew, Chandlery, Supplies (fuel) |
| Compact | Fish quay crane, net loft | |
| Prep | Fish market hall replaces the stall, harbour master office replaces the hut, ice house | Market, Harbour master |
| Buoy | Outer wharf with bollards and lights | |

During a refit the new hull sits on the boatyard cradle until it is ready.

## 2. Leaving and coming home

One continuous trip in three legs. There are no cuts: the camera moves and the chart fades in and out.

1. **Harbour lane (3D, about 6-8 s).**
   - The boat casts off from its berth and goes dead slow through the basin.
   - It passes the lighthouse and the breakwater head, opens up to full speed and turns toward the ground's bearing.
   - The lane is an authored spline per berth, so it never crosses the pontoon, moored boats or the breakwater.
2. **Chart leg (3-7 s, tap to speed up).**
   - The camera lifts and widens while the illustrated Gull coast chart fades in, zoomed in on the harbour, and
     settles to full view. It reads as zooming out to the map.
   - A boat token sails a dotted route to the ground with a wake behind it.
   - Two landmarks per route pop up as the boat passes.
   - One quiet crew line says what the crew are doing.
3. **Sea lane (3D, on the sea map).**
   - The chart zooms into the ground's pin and fades out as the 3D sea map appears, the camera high and wide, easing
     down to sailing height.
   - The boat enters from the map edge facing Gull Harbour and follows the sea lane to the ground.

Coming home is the reverse:

1. The boat sails the sea lane back to the edge, then the chart leg runs.
2. The boat enters past the lighthouse and slows to dead slow in the basin.
3. It docks at its berth with a short final glide.
4. Crates of the catch are carried up to the market stall, one after another.
5. The Sell button follows.

The crew keeps working through every leg: the deck schedule runs as it does at sea today.

## 3. Sea lanes: the rules (fixes "drives through islands")

1. **Entry faces home.** Each sea map's entry point lies on the map edge in the direction of Gull Harbour, as drawn
   on the chart and turned into the sea camera's screen frame. Example: Rocky point lies west of the harbour on the
   chart, so its entry is on the east (screen right) edge.
2. **Lanes have width.** The route from the entry to each ground is planned with a clearance of twice the biggest
   hull's radius plus 2 m, then smoothed. Every smoothed sample must still clear that width, or the raw lane is used.
3. **Nothing in the lane.** No island, shallows, rock or prop may sit inside a lane corridor. A check proves this
   for every map and ground: `Assets/Editor/SeaLaneChecks.cs`, which also runs as a plain .NET test.
4. **Landmarks line the lane.** Each lane has two to three things to remember, placed just outside the corridor:
   channel markers, a bell buoy, a wreck, seal rocks.
5. A relocation inside the map (tap to sail) still uses the existing path planner.

## 4. Moments on the way (rare, never a pop-up you must answer)

Each sea lane can roll one moment, at most one per trip, from these four:

- **Gulls diving:** a school marker just off the lane. Tap it to detour and fish there.
- **Floating crate:** sail through it for a few coins or bait.
- **Fog bank:** the fog thickens and the boat slows for a stretch.
- **Dolphins:** dolphins ride the bow wave for a while.

## 5. To-do (not in this round)

6. A choice of route: a safe lane or a faster shortcut through the rocks that needs a better hull or a navigator
   crew member.
- Townsfolk walking, boats coming and going, day/night in the harbour.
- Walking the captain around the quay instead of tap bubbles.

## Decisions taken without Mo (change any of them)

- One growing harbour, no move to a bigger port.
- Tap bubbles and tabs stay.
- Travel is the chart fly-over, not a loading screen.

## Work split

- **Claude:**
  - harbour layout and berths
  - moored boats
  - building unlocks
  - the three-leg trip, chart leg and arrival crates
  - sea lanes and their check
  - moments
  - then the rod minigame polish
- **Codex 2:** the 3D harbour kit and the sea-lane art (HARBOUR-ART-1), then the rod arms (FISH-ARMS-2).
- **Codex 1:**
  - imports the kit into Unity and registers it in ArtLibrary
  - fixes map entry art if the lane check fails
  - builds, installs and makes native captures (HARBOUR-IMPORT-1)
- Code falls back to simple blocks for any model that hasn't landed, so the art can arrive in any order.

## Appendix: harbour layout (metres, harbour frame)

x runs along the shore, z < 2.3 is water, the quay top is y 0.35 and the waterline is y -0.32. Yaw is in degrees
about +Y; a boat at yaw 0 points its bow to -x, and at yaw 90 its bow points to +z (toward land).

| Thing | Position (x, z) | Yaw | From hull |
|---|---|---|---|
| Quay4m row | x -18..26 every 4, z 3.3 | 0 | 0 |
| Beach (sand) | x -42..-29 (cut out at the slipway) | | 0 |
| Slipway | (-25, 2.4), sunk to y -0.05 (quay top - 0.4) | 0 | 0 |
| Boatyard shed + cradle | shed (-34, 6.5), cradle (-34, 2.5) | 180 | 1 |
| Supplies shed | (-29, 6.0) | 180 | 0 |
| Market stall | (-21.5, 5.0) | 180 | 0 |
| Harbour master hut + notice board | (-17.5, 6.0), board (-15.6, 4.6) | 180 | 0 |
| Pontoon gangway, segments, fuel dock | gangway (-13, 2.4), segments (-13, -1.5) and (-13, -5.5), fuel dock (-13, -8.6) | 0 | 1 |
| Crew office (HouseA + ShopFront_CrewOffice) | (-10.4, 6.6) | 180 | 1 |
| Chandlery (HouseB + ShopFront_Chandlery) | (-6.8, 6.6) | 180 | 1 |
| Fish market hall (HouseA + ShopFront_FishMarket) | (-2.6, 6.6) | 180 | 3 |
| Harbour master office (HouseB + ShopFront_HarbourMaster) | (1.0, 6.6) | 180 | 3 |
| Ice house | (5.0, 6.4) | 180 | 3 |
| Net loft | (9.0, 6.6) | 180 | 2 |
| Quay crane | (16.5, 4.2) | 180 | 2 |
| East breakwater | wall x 28 from z 0 to -8, then z -12 from x 26 to 10; BreakwaterEnd (6.5, -12), Lighthouse (5.6, -12.3) yaw 200 | | 0 |
| Outer wharf + lights | segments x 12..24 at z -10.6 | 0 | 4 |
| West headland (BreakwaterRock) | bezier (-40, 1) → (-34, -16) → (-19, -14); MouthBeacon at (-18.6, -14) | | 0 |

### Berth slots (hull centre)

| Berth | Slot 0 | Slot 1 | Slot 2 | Yaw |
|---|---|---|---|---|
| Slipway | (-27.35, -1.8) | (-22.65, -1.8) | | 90 |
| Pontoon | (-10.25, -6.5) | (-15.75, -1.6) | | 90 |
| Fish quay | (1.5, 2.0 - beam/2) | (12.5, 2.0 - beam/2) | | 0 |
| Outer wharf | (12.4, -9.15 + beam/2) | (24.2, -9.15 + beam/2) | | 0 |

### Harbour lane

1. The boat moves from its berth to a pull-out point.
2. It passes through the basin at (-2.5, -7.5) and the mouth at (-6.5, -13.5).
3. It reaches outside at (-6.5, -25).
4. It runs 14 m along the bearing of the ground.

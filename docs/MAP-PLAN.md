# Map plan: bigger seas, placed islands, sailing with collision, a border that feels natural

Status: proposal by Claude (lead), 2026-10-24, for Mo's approval. Supersedes the "travel 30 s along a
fixed path" part of MASTER-PLAN M4 and the 3× size target of ART-PLAN A1. Everything else in M4 (richness,
navigator, relocation rules) stays.

## 1. Where we are

- Codex 1 delivered `GroundsV1` for all five maps (Art/Models/Maps/, REPORT.md): 9× the old footprint, but that
  is only about 73 × 73 m. The extra space is mostly empty sea; the original island sits next to ground 1, the
  other two grounds have a few rocks or buoys. Grounds are ~22 m apart, joined by L-shaped polylines.
- In the game the boat does not move at sea: "sailing out" is a timed transition, then the boat is placed at
  the spot. Nothing collides with anything.
- So "bigger maps, move the islands, collision so the boat can sail" is a new layer: a navigable sea.

## 2. Player-facing design

**How the boat moves: tap to sail.** The player taps a ground marker (or any open water) on the sea; the
navigator plots a route around islands and shallows and the boat sails it, camera following. No joystick:
Catchline is a crew-management game played on phones, and the crew keep working (the deck graph keeps
ticking) while the boat is under way only for jobs that make sense moving (sorting, stowing; no gear out).
This replaces the fixed 30 s path. Travel time comes from distance and hull speed (rowboat slow, later hulls
faster), targeted at 15–40 s between grounds.

**Size.** Playable water per map, sized for 15–40 s trips at hull speed:

| Map | Playable sea | Character |
|---|---|---|
| Harbour mouth | 220 × 160 m | Mainland coast along one long side, harbour wall, two small islets, a channel between them |
| Kelp bank | 260 × 180 m | A chain of three low islands sheltering the kelp; open water on the far side |
| Sandbar | 260 × 200 m | One long sandbar that splits the map; gullies at both ends; you must sail round it |
| Rocky point | 280 × 200 m | A headland with scattered reefs; the reef field is the hazard and the prize |
| Deep channel | 320 × 240 m | Two big islands with the dark trench running between them; a distant ship lane outside |

**Islands are placed for play, not decoration.** Each island does a job: it shelters a ground, forces a
route choice, or frames the view at anchor. Each map keeps its three grounds (ART-PLAN A1 names), but a ground
becomes a zone (circle, 12–20 m radius) rather than a point; anchoring anywhere inside it fishes that ground.
At least one ground per map should not be reachable in a straight line, so the island layout matters.

**Shallows.** Every island has a shallow ring (sand or rock colour in the water). The boat slows to half
speed there and cannot anchor; the route planner avoids it unless it is the only way. Later hulls with deeper
draft get a wider ring (fits the hull progression).

## 3. The border (recommendation)

Layered, so it never feels like an invisible wall:

1. **Diegetic edge.** A ring of outer marker buoys (red/white spar buoys, 25–30 m apart) marks the fishing
   area. Players understand buoys; they explain why you stop.
2. **Fog bank.** From 30 m inside the edge, sea fog thickens and the water darkens and swells a little. At
   the edge you see grey haze, not the end of the world.
3. **Route planner refuses beyond the buoys.** Tapping outside snaps the target to the nearest point inside
   and the navigator says a short line ("Fog's thick past the buoys, skipper."). The captain never sails out.
4. **Hard clamp** on the boat position at the border polygon as a safety net (slide along it, no bounce).
5. **Camera clamp** so the view never reaches the edge of the water mesh.

**Beyond the border:** the sea continues to the horizon (an infinite water plane with the same shader,
fading into fog), with low, unreachable silhouettes: mainland headlands, far islands, a lighthouse, the odd
ship crossing on the lane. Cheap (a few low-poly cards and meshes per map), and the world feels bigger than
the area you sail. Rejected: invisible walls (feel cheap), wrap-around (breaks geography), storm walls
everywhere (too dramatic; kept as a Deep channel event idea).

## 4. Technical design

**Data, not physics.** Navigation is deterministic data the game reads, like the deck graph, so it is
testable in EditMode checks. No Unity NavMesh or rigidbodies.

Per map, Codex exports `Art/Models/Maps/<Map>/navigation.json` from the .blend:
- `islands`: polygons from slicing the terrain at the waterline (Y = 0), simplified to ≤ 64 vertices each.
- `shallows`: polygons from slicing at −1.0 m (the shallow ring).
- `border`: the fishing-area polygon (inside the buoys).
- `grounds`: id, name, centre, radius, nominal depth, pool id (extends grounds.json).
- `harbour`: the spot where a voyage starts and ends.
- `cameraBounds`: rectangle the camera target may use.

**Runtime (`Assets/Scripts/Game/Sea/`)**
- `SeaNav`: loads navigation.json; inflates island/shallow polygons by the hull's radius (half beam + 0.5 m);
  plans routes with A* over a visibility graph of inflated vertices (exact, cheap for < 300 vertices);
  shallows cost ×2; `Plan(from, to) → polyline` or null; `Snap(point)` to inside the border.
- `BoatSailor`: follows the route with turn-rate-limited steering (no sliding sideways), slows in shallows and
  near the end, slides along edges if it ever touches an inflated polygon, hard clamp at the border.
- Hull speed and turn rate come from HullDef (new fields).
- `VoyageGame`: SailingOut / SailingHome / relocation use real routes; arrival = inside the ground zone.
- Fog/border dressing, outer buoys and horizon silhouettes are scenery driven by the same file.

**Checks (`MapNavChecks`, EditMode, scratch editor only):** for every map and every hull: harbour → each
ground and ground → ground routes exist; no route point inside an inflated island; route length within 1.6×
straight-line distance unless an island is in the way; travel time per hull within 15–40 s; a target outside
the border snaps inside; a boat pushed into an island ends outside it. Plus native captures at 1440 × 900
and 844 × 390 of sailing, the border fog and an anchored ground.

## 5. Work split

| Who | What | Depends on |
|---|---|---|
| Mo | Approve this plan and the decisions below | — |
| Codex 1 (art, high) | Rebuild the five maps at the new sizes with placed islands, shallows, outer buoys and horizon silhouettes; export navigation.json; top-down plates with routes; day/night renders | Plan approved |
| Sol 6.1 medium (code) | SeaNav, BoatSailor, VoyageGame integration, MapNavChecks, using interim navigation.json files hand-made from the current maps until Codex delivers | Plan approved; can start in parallel |
| Claude (lead) | Briefs, acceptance of both, native captures, final say on feel | — |

Order: Harbour mouth and Kelp bank first (the first two maps players see), then the other three.

## 6. Decisions for Mo

1. Tap to sail with auto-route (recommended) vs. manual steering.
2. Grounds as zones you can anchor anywhere inside (recommended) vs. fixed anchor points.
3. Map sizes in the table above (recommended) or bigger/smaller.
4. Border: buoys + fog + horizon silhouettes (recommended).
5. May the crew sort and stow while sailing (recommended) or does all work stop under way?

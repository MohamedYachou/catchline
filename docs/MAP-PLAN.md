# Map plan: bigger seas, placed islands, sailing with collision, a border that feels natural

Status: APPROVED by Mo 2026-10-24 (sizes, border, beyond, collision, tap-to-sail). Travel time is 10–20 s for now;
Mo is exploring with Fable whether the trip becomes its own gameplay half (preparation on the way). Build travel so its
duration is one tunable number per hull and nothing else depends on it. Supersedes the "travel 30 s along a
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
faster), targeted at 10–20 s between grounds (Mo: longer is boring unless the trip gets its own gameplay).

**Size.** Playable water per map, sized for 10–20 s trips at hull speed (hull speeds are tuned to fit):

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
straight-line distance unless an island is in the way; travel time per hull within 10–20 s; a target outside
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

## 7. Sailing feel and where the fish are (Claude's design calls, 2026-10-24)

Built so far: SeaNav (routes), BoatSailor (steering), VoyageSea (voyages sail real routes, Relocate, deck work keeps
ticking), MapNavChecks; Codex 1's SeaV2 maps and navigation.json for all five. Not yet: the maps in the scene, the
border/horizon, the tap input, the camera, and fish richness. This section decides how those feel.

### 7.1 Moving the boat

- **Input (Mo, 2026-10-24): an explicit Sail mode.** Fishing is the default mode; taps on the water do nothing
  there. A Sail button with a ship's-wheel icon enters Sail mode (gear must be in: if a net/line/cage is soaking,
  the "Haul it first / Forfeit and go" modal comes first). In Sail mode: tap open water or a ground ring → dotted
  route line + end ring and the boat sets off; tap again to re-route; tap the boat to stop; tap an island → nearest
  reachable water; beyond the buoys → snapped inside + navigator line. A "Fish here" button (fishing icon) leaves
  Sail mode back to Fishing; it is enabled only when stopped inside a ground zone (otherwise it reads "No ground
  here" and stays in Sail mode). Both buttons are UI v2 components (docs/UI-SYSTEM.md).
- **Feel.** Ease in over ~1.5 s, cruise, ease out over the last boat-length; turns limited per hull (rowboat nimble,
  big hulls wide); a slight bank into turns and a wake trail behind (white foam ribbon, fades in ~4 s). Shallows:
  half speed, lighter water, a soft scrape sound if a hull edge enters. Never a hard stop against an island: slide.
- **Camera.** Anchored = today's framing. Sailing = eases (1 s) to a higher, slightly wider follow camera, boat a bit
  below centre so the destination is ahead; clamped to cameraBounds; eases back to the anchored framing on arrival.
- **Arrival.** The boat stops at the tapped point. Pressing "Fish here" inside a zone = anchored (anchor-drop sound +
  small splash) and back to Fishing mode. Anywhere in the zone works; the ring shows its edge.
- **Time.** One cruise speed per hull, tuned so harbour → first ground is 10–20 s (Mo). Nothing else depends on it.

### 7.2 Where the fish are rich

Two layers, both visible to the player so moving is a decision, not a guess:

1. **Ground richness (MASTER-PLAN M4, unchanged numbers).** Per ground per species 0.3–1.0: rods −0.02 per catch,
   nets −0.004 per kg, floor 0.3, +0.35 recovery per voyage. Bite rate × richness. This is what pushes you to other
   grounds over a session.
2. **A school inside each ground (new, small).** Each ground has one moving hotspot (radius 6–8 m) that drifts slowly
   (0.2–0.4 m/s) inside the zone and jumps to a new spot every 3–5 minutes or when its richness drops below 0.5.
   Fishing with the boat inside the hotspot: bite rate ×1.3; at the zone edge ×1.0 (linear in between). This makes
   "nudge the boat 10 m" worth a tap without punishing anyone who ignores it.

**How the player sees it (no numbers on the water):**
- Gulls circle above a rich school (3–6 gulls at ≥ 0.8, 1–2 when thinning, none when poor); occasional surface boils
  and jumping fish at the hotspot.
- The ground ring's colour: warm when rich, neutral when thinning, grey when poor (same bands as the navigator).
- The navigator (when deployed) gives the numbers and suggestions: "Herring thinning here. Kelp edge is richer."
  Tier-0 players without a navigator still get the gulls and ring colour.
- Night: schools sit closer to the surface near light; lantern stations attract (M7 ties in later).

**Not doing:** a fish-finder minigame, invisible random hotspots, or richness that changes mid-cast. Fish quality and
species mix stay per ground as in MASTER-PLAN; the school only changes how often they bite.

### 7.3 Order of work

- Codex 2 (now): the sea in the scene: SeaV2 maps loaded per map, border buoys + fog + infinite water + horizon
  silhouettes, tap input with route line, follow camera, wake, arrival; native captures. (brief: SEA-SCENE-1)
- Codex 1 (from 21:20): grounds and fish: M4 grounds table, richness, schools, gulls/ring colour cues, navigator
  report and suggestion, M4Checks. (brief: GROUNDS-1). Then the rest of SOL-CODE-1 if any remains.

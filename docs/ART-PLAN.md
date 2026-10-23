# Catchline art plan — 3D and images (Codex)

Status: the complete art backlog for v1 (tiers 0–5), owned by Codex. Agreed
with Mo on 2026-10-23. Everything that is code is in `docs/MASTER-PLAN.md` and
belongs to the local Claude Code sessions. Codex never edits `.cs` files; the
code sessions never edit `Art/` or `Assets/Art/Models/`.

Style authority: `Art/STYLE.md` for models and palette; the four concept
images in `docs/screens/ui-concept/` for interface and illustration; existing
goal renders for scene framing. Hull dimensions, pivots, names and axes of the
five existing hulls are frozen — stations are added as props, hulls are not
remodelled.

Every delivery: source (`.blend` or `.svg`), export (`.fbx` or `.png`), a
report with validation (round-trip, bounds, pivots, triangle counts), copied
into the main checkout paths named below with existing GUIDs preserved, one
START and one DONE entry in `comms.md` of five lines each.

---

## A1. Maps — five maps at 3× with three grounds each (M4, M7)

Each map becomes at least three times its current footprint and contains
three visually distinct grounds, each a place the boat can anchor with the
same camera framing as today. Grounds are a few boat-lengths apart; the boat
travels between them along a short path. Deliver per map:

| Map | Ground 1 | Ground 2 | Ground 3 |
|---|---|---|---|
| Harbour mouth | Quay shallows (sand, moorings) | Channel (dark, buoys) | Mouth flats (weed, posts) |
| Kelp bank | Kelp shallows (dense blades) | Kelp edge (broken kelp, rock) | Open (deep blue, few features) |
| Sandbar | The bar (pale sand, ripples) | Gully (dark channel beside the bar) | Open |
| Rocky point | Reef (boulders, breaking colour) | Drop-off (shelf to dark) | Open |
| Deep channel | Drop-off | Trench (darkest water, no bed) | Open (distant ship, buoys) |

Per map: `Art/Models/Maps/<Map>/<Map>.blend` and `.fbx`, a `grounds.json`
with each ground's boat anchor (position, heading) and the travel path between
grounds (polyline), seabed depth per ground for water colour, and a night
lighting variant (lantern-coloured warm key, cool fill, visible deck light
pools) delivered as a second lighting preset, not a second model. Keep the
authored waterline at local 0, world Y −0.32, identity placement, no
recentring. Runtime paths: `Assets/Art/Models/Environment/<Map>/`.

Acceptance: a render from the gameplay camera at each ground, day and night,
plus a top-down plate showing the three anchors and the path. 15 ground
renders by day, 15 by night, 5 plates.

## A2. Stations and baskets on all five hulls (M1, M8)

Props added to each existing hull, delivered with a station file the code
reads directly:

```
Assets/Art/Models/Boats/<Hull>.stations.json
{ "hull": "...", "stations": [ { "id", "kind", "pos", "yaw", "workTile", "basketIn", "basketOut", "places" } ], "blocked": [...] }
```

Positions are hull-local metres; `workTile` is the deck grid cell the worker
stands on (grid per `GameData.Hulls`); `basketIn`/`basketOut` are the basket
prop positions; `places` only for the processing table.

| Hull | Stations to add |
|---|---|
| Rowboat (0) | sort table clamped to the gunwale (small cutting board on the rail), rod basket, bait bucket (exists), navigator seat at the bow |
| Skiff (1) | sort table, two rod baskets, bait bin, lantern mount, navigator post |
| Compact fisher (2) | sort table, sort-out basket, three rod baskets, net basket (exists, restyle), bait bin, hold hatch marker, navigator post |
| Prep fisher (3) | as compact plus processing table with two places (exists), table in/out baskets |
| Buoy fisher (4) | as prep plus a second sort table, second processing table, cage baskets ×2, line baskets ×3, generator box, deck light masts ×2, winch (exists), line hauler, navigator post at the helm |

Prop kit (shared, honey timber / ivory / navy per STYLE.md): sort table (two
sizes), wooden basket (two sizes, empty and three fill states), bait bin,
hatch ring, lantern, deck light mast, generator box, line hauler, cutting
board. Baskets need three fill states so the code can show pressure without
spawning sixty fish.

Acceptance: per hull a top plan with all stations labelled, a gameplay-camera
render with props in place, and the station file validated by the code
session's `M1Checks` (every work tile walkable and reachable).

## A3. Characters (M2)

- Navigator: one rigged character on the existing crew rig, with a distinct
  outfit (navy jacket, cap) and a bow/helm idle pose with binoculars; animation
  clips: idle, point, warn.
- Card portraits: illustrated busts in the concept style, 240×240 with
  transparent background, for Mira, Noor, Dirk, Sam, Kofi, Ana, Mats, Lise,
  Olaf, Pim, Tove. Same bust used at 56, 96 and 240 px, so the silhouette must
  read at 56.
- Card frames: blue, purple, gold, 480×640 with a portrait window, name band
  and three ability slots; plus a locked variant.
- Runtime paths: `Assets/Art/UI/Portraits/`, `Assets/Art/UI/Cards/`.

## A4. Interface imagery (UI v2 — see `docs/UI-SYSTEM.md` §6)

Slabs, buttons, bars, chips and tabs are vector and are built by the UI
session from SVG. Codex delivers the image-generated set:

- `plank-tile` (tileable navy planks), `rope-h`, `rope-v`, `nail`.
- Stage illustrations ×5 (fishing, hauling, sorting, table, hold) at 96×96.
- Shop item illustrations at 160×120 for every item in `GameData.Upgrades`
  and the Supplies list (bait packs, fuel, lantern, oil, spare rigs).
- Event icons ×60 at 64×64 (list in MASTER-PLAN M6; deliver per batch).
- Buyer shopfronts and portraits ×5 (Market, Bait shop, Restaurant, Cannery,
  Collector), 320×200 and 120×120.
- Product icons: chum, fish oil, and one per special product (species list
  from the code session's `Products` table).
- Night species portraits: squid, dogfish (new), and night variants are not
  needed for existing species.
- Chest art ×3 (wooden, iron, gold) closed and open.
- Title illustration refresh in the concept style if the current one clashes.

Delivery: `Assets/Art/UI/v2/` with a manifest listing each file's logical size.

## A5. Gear and props (M7, M8)

- Jig rig (night squid): small rail-mounted rod with jig line and a lamp.
- Spare rig prop (for the Snag event cut), lantern oil can.
- Deck light pool decal (for night lighting of a single station).

## A6. Events art (M6)

Visible world pieces the events need beyond icons: jellyfish clump in the
net, flying fish (model exists), gull (exists) swoop pose, seal head at the
surface, dolphin fin, inspector launch (small navy boat), rival boat (exists),
squall overlay (rain streaks sprite), offal pile, eel on the table.

## A7. Order of delivery

1. A2 stations for rowboat, skiff and compact (unblocks M1 captures).
2. A3 portraits and frames (unblocks M2 and the UI roster screens).
3. A4 interface imagery (unblocks UI v2 beyond the voyage HUD).
4. A1 maps, Harbour mouth and Kelp bank first (unblocks M4), then the rest.
5. A2 stations for prep and buoy (unblocks M8).
6. A5, A6, then A1 night variants (unblocks M7).

Anything blocked on a decision from the code side (a product list, an event
batch) is answered in `comms.md` by the lead within the day; do not invent
species, products or events.

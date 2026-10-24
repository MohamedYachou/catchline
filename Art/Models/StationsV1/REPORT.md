# ART108 — five hull station deliveries

23 October 2026. Art-side delivery against Fable's `docs/ART-PLAN.md` A2,
first priority in A7. Source hulls, existing GUIDs and all C# are untouched.

## Contents

Thirty-three shared authored props, each with editable `.blend`, source `.fbx` and
matching runtime `.fbx` under `Assets/Art/Models/StationsV1/`. Exact bounds,
triangle totals, SHA256 and independent Blender FBX readback results are in
`kit-manifest.json`. All thirty-three round trips match triangle totals and bounds
within 0.1 mm. Honey timber, ivory rims, navy steelwork and restrained teal
match `Art/STYLE.md`. BasketSmall and BasketLarge each have four variants:
empty, low, medium and full. The fish are illustrative fill geometry, not
individual simulated fish. Switch whole variants; do not show all four.

Each of `Rowboat/`, `Skiff/`, `CompactFisherV1/`, `PrepFisherV1/` and `Tier5DeepLines103/` contains a `.blend` review
scene, an additive prop-overlay FBX, gameplay-angle render, labelled top plan,
station JSON and validation receipt. The canonical machine-readable station
files are copied to `Assets/Art/Models/Boats/<Hull>.stations.json`.

## Coordinate contract

`pos`, `basketIn` and `basketOut` are **runtime Boat-local metres**, Y up,
bow toward negative X, before Boat travel/bob. They are not the imported FBX
child's coordinates. `workTile` is the existing `GameData.Hulls` integer
grid, converted by multiplying both axes by `cellSize` (tile Y means world
Z). The manifest records grid dimensions and the model spawn centre.

The old Rowboat/Skiff FBXs and the compact FBX use different baked source
axis conventions. `layout_stations.py` documents the actual source-to-review
mapping; never copy the Blender scene object locations directly into a
Unity model-child transform. Individual kit sources have Z up and their
operator-facing side toward source -Y. Unity integration must verify the
importer's root conversion once before placing props. Overlay FBXs are
review aids in the review scene basis, not automatically bound prefabs.

`existing: true` refers to the station or gear already aboard. A `model`
on such a row is an additive trim/bracket, not a replacement hull. Replace
the old runtime net basket when enabling the wooden one. Do not duplicate
the existing bait bucket/cooler/rods/net/console. The Skiff's third rod
shares rod2's output basket; it has no separate basketOut entry.

SortBoardRail's origin is the clamp's rail-contact plane, not the lowest
clamp tip. Its clamp extends 0.1125 m below the origin; Rowboat places that
origin at 0.40 m. NavigatorHelmBracket is a low console attachment, avoiding
the Compact canopy. The navigator sits on the Rowboat seat; that seat is
not classified as a standing body obstacle.

## Access validation

All declared station work tiles are reachable in four-neighbour BFS from
the receipt's seed. Existing legacy blocked cells remain blocked. New prop
meshes are sliced at 0.20/0.55/0.95 m with 0.28 m body clearance on all
five grids; basket footprints also have 0.28 m clearance. Compact also
rasterizes the original hull meshes and preserves the hatch opening even
with its lid raised. Review receipts record any station approach moved
away from a basket or obstacle.

The initial Compact sort-table location was hidden by the canopy. It now
sits along the open aft rail, yaw 90, and leaves a narrow but connected
approach beside the original hatch. This is explicitly an art-side check;
the code owner must run native M1Checks, concurrent-worker traces and both
screen sizes. There is no claim that runtime currently consumes this JSON.

## Rebuild and review

Run Blender in the background with `Art/Source/Art108/build_stations.py`,
then `layout_stations.py`. Use `-- Rowboat Skiff CompactFisherV1` to choose
layouts. Rebuild only these new output directories. The original hull
files are read-only inputs; hashes are recorded in each validation receipt.
The review water, labels, lights and cameras are excluded from kit exports.

The `.blend` review scene is saved before technical labels are added; its
camera starts at the gameplay angle. The PNG top plan is bow-right. These
are authored renders, not native gameplay screenshots or player acceptance.
Rowboat review omits its existing runtime-spawned cooler and bait bucket;
their station rows and blocked hold tile are retained. The unchanged
centre thwart/oars and all original boat geometry remain in the render.

No commit or installed-game update is included in this art handoff.

## Final large-hull delivery and runtime names

24 October: Prep and Tier5 gameplay renders and labelled plans reviewed. Prep has469 reachable cells; Tier5 has870. Both processing-table work places are distinct and reachable. The manifests describe suppression of existing RawBuckets, RawIceCoolers and NetModule2 prop groups in the default rod/deep-line configuration; the hull geometry remains unchanged. Tier5 includes an optional third deep-line review clone and its explicit source/offset contract. Alternate side-net configuration is not validated. Canopy occlusion and concurrent worker access need native checks.

The runtime FBX files and internal roots are Art108_<LogicalName>.fbx. Use runtimeModelId/runtimeFile from kit-manifest.json and station JSON; model is the logical source name. This avoids filename-key collisions with existing Lantern and other imported models. No original GUID was changed.

A5 gear and A6 events share the same manifest: JigRig, SpareRig, LanternOilCan, CuttingBoard, JellyfishClump, FlyingFishEvent, GullSwoop, SealHead, DolphinFin, InspectorLaunch, OffalPile and TableEel. Flying fish/gull are separate derivatives of existing authored sources; originals untouched. Event motion and hooks remain code work. Rival boat can use existing Harbour/Rowboat_VariantRed.fbx. DeckLightPool and SquallOverlay have editable SVGs and effects-manifest.json. Review plates show revised visible basket fill states and a flying gull with tucked feet.

Publication update (24 October 2026): Mo authorized GitHub publication of this delivery. See Art/ART-PLAN-PROGRESS.md and comms.md for the commit/push receipt. Earlier no-commit wording describes the original pre-publication handoff. Native acceptance remains pending.

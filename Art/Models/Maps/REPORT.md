# ART108 - expanded fishing maps

24 October 2026. Five editable derived .blend models and matching FBX exports; runtime files are Environment/<Map>/<Map>GroundsV1.fbx. Original environment files, GUIDs and artist-worktree .blends are untouched. Each directory contains grounds.json, lighting-presets.json, validation.json, six gameplay-angle PNGs, one three-grounds top plate and an updated review-sheet.png. All35 images were opened after the landmark revision.

Each map has3 distinct anchors/grounds and three travel polylines. Footprint is9x its source footprint (3x each axis). Independent Blender FBX import matches triangle counts and vertices within0.1mm; worst observed error3.44 micrometres. Reports retain baseline source path/hash, bounds, exact exported hash and centreline checks sampled every0.5m. The original visible coast/shallow shelf is retained. Deep skirt vertices below-2.3m are lowered to join a new connected closed seabed; these are derived maps, not unchanged originals.

Ground anchors are WORLD DECK-CENTRE positions, deckY=0 above waterY=-0.32. Runtime Boat translation = anchor minus rotated HullDef.Center. Never add map-rootY to the boat. The existing import X compensation is retained in exports. Heading0 is a starting value. Each ground has nominal depth for the water-colour preset plus measured physicalAnchorDepth; nominal preset depth is not a bathymetric claim.

Day/night share one model. Presets give warm day key/cool ambient and cool night ambient with two warm deck pools. Blender review uses a Rowboat reference, glass/volume water approximation and static lights. It omits the native HUD, crew and runtime water; images are art-side framing evidence, not game screenshots. Original-world land is intentionally local to ground1; outer grounds use sparse kelp, marker buoys, rocks or distant ship silhouettes.

## Pending code-owner acceptance

M4 must bind isolated model keys, translate anchors correctly, sweep finite hulls/turning envelopes along paths and check all5 hulls at both screen sizes in native runtime. Centreline clearance does not prove hull clearance. Depth presets must be reconciled with live water and fish pools. Light intensity values are integration starting values, not Blender lumen equivalence. No scene, C#, save, build, install, commit or push was changed by this art task.

Builder: Art/Source/Art108/build_maps.py -- <Map> build or review. Sources: Catchline-art-style HarbourMouth11 and Locations12 paths recorded in each receipt. Maps: GullHarbourMouth, GullKelpBank, GullSandbar, GullRockyPoint, GullDeepChannel.

Publication update (24 October 2026): Mo authorized GitHub publication of this delivery. See Art/ART-PLAN-PROGRESS.md and comms.md for the commit/push receipt. Earlier no-commit wording describes the original pre-publication handoff. Native acceptance remains pending.

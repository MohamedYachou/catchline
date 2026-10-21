# TIER5-102 early deep-line model preview

**Awaiting Mo's visual greenlight. Preview only; no production export or installation.**

Authored by Sol under Codex 2 (WSL CLI), from the actual approved `Tier5Production071/Tier5FisherV1.blend`. The production scene, exporter and FBX are unchanged. Open `Tier5DeepLines102-preview.blend` for the primary rod/deep-line arrangement. The reproducible source is `Art/Source/tier5_deeplines102_preview.py`.

- `01-rod-deepline-beauty.png`: two tall deep-line fishing rods alongside two optional normal rods; two fixed normal rods, two fixed buoy/cage proxies and one rear net retained.
- `02-rod-deepline-plan.png`: same geometry from directly above; bow right, optional +X side at the top of the sheet.
- `03-side-net-beauty.png` / `04-side-net-plan.png`: optional normal rods, holders and all deep-line parts hidden; one optional side net shown. Fixed equipment remains.

## Placement and dimensions

Source Blender coordinates are X across deck, **-Y bow / +Y stern**, Z above deck. These axes are confirmed by actual helm/bow-locker/outboard geometry, not inferred from anchor labels. Hull remains 8.50m long by 4.20m wide; no new crew or berth geometry. Crew contract stays six hired plus captain, at existing 0.95m bare-scalp scale.

| Element | Source placement / measure |
|---|---|
| Fixed normal rods | X±1.90, Y-0.35; sockets unchanged |
| Optional normal rods | X1.90, Y1.10 and2.55; sockets unchanged |
| Deep-line rod bases | X1.87, Y0.40 and1.82, Z0.46 |
| Deep-line tips | X3.34, same Y, Z3.14 |
| Tall rod base separation | 1.42m fore/aft |
| Clamp envelope | 0.22m across ×0.30m fore/aft ×0.30m high; centred X1.86,Z0.44 |
| Manual reel | Centre X1.94,Z0.74; flange diameter0.41m |
| Inboard crank extreme | X≈1.65; no new central deck pedestal |
| Canopy maximum | about1.50m; rod tip1.64m taller |
| Main hull side / tip | X2.10 / X3.34; tip extends1.24m beyond hull |
| Fixed buoy centres | X±2.80,Y-2.05; separate cages shown below waterline |

The smallest lateral geometric gap from the inboard deep-line crank to the prep station's X≈0.74 edge is about0.91m. The clamp's inboard edge X1.75 leaves about1.01m against that same prep envelope. This is a static geometric gap, **not a reserved or verified crew route**. Mounts interleave between the normal rods rather than replacing them. Deep lines are0.70/0.73m fore/aft from the neighbouring normal sockets, and the forward deep-line base is2.45m behind the buoy-service line. The entire deep-line module is aft of the canopy footprint (its rear edge Y≈-0.90).

Two rigs give a clear tall fishing-pole silhouette without a gantry or electrical cabinet. Visible reel, hand crank, grip and hanging line establish a human-operated fishing rig. Catch batch3/upgraded5 is not a rod count. Fishers still operate this equipment; deckhands still haul/process. No powered catch mechanism or replacement crew is implied.

A third rod is **not included or approved**. A midpoint Y1.11 would coincide with the existing optional normal rod. A rear extension nearY3.2 would approach rear net work/access and the second optional rod. A third upgrade therefore needs a deliberate layout change; adding it to this first version would obscure the compact two-rig decision.

## Existing geometry versus preview additions

The approved source contains rod holders but relies on runtime fishing rods/buoys/cages; this preview adds clearly simplified normal-rod and buoy/cage geometry to make the full equipment count legible. These are preview props, not replacements for runtime assets. No crew silhouettes are baked into the scene.

The existing source's `NetModule2` is also stern-mounted. For Mo's new side-net requirement, this copied group is rotated -90° and translated to the optional +X rail (preview only). The original fixed rear net remains unchanged. The side-net comparison is a physical layout proposal, not a claim that current runtime already switches to this placement. Legacy Engineer control/hatch/status visuals are hidden in the copied review scene because this pass has no Engineer.

The sea floor is a neutral review stage below the cages, not game water. Orthographic three-quarter view is approximately45° down and40° off stern, close to the source game's45°/35° camera convention (`VoyageGame.cs`). Actual hull rotation/camera framing in Unity is not reproduced or verified here.

## Checks and limits

Actual source mesh bounds were inspected with Blender before authoring. Beauty and plan PNGs were rendered from the authored scene and visually inspected for canopy/table/normal-rod/net conflicts. The second layout hides every new optional rod/deep-line part and the original optional holders. The saved scene retains the primary rod/deep-line layout. Existing palette materials are reused; review-stage sea is presentation only.

No Unity import, runtime, route, animation, mobile readability, balance, production topology/export or Mo acceptance is claimed. WSL Blender5.0.1 reads this5.2 source with a newer-file warning; it is used only to save this separate preview copy. Production must remain sourced from the original approved5.2 asset if a later production stage is approved.

Next: Mo reviews the actual images and chooses whether to keep/refine the two tall poles before any production work.

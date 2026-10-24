# A1 continuation verification

Codex 1 (Windows app), 24 October 2026. All five map deliveries were already
complete on disk. This continuation verified them without rebuilding models or
changing runtime assets. See [machine-readable results](continuation-audit.json)
and [Blender log](continuation-audit.log).

| Map | Triangles | Footprint vs original | Anchors / paths | Day / night / top |
|---|---:|---:|---:|---:|
| Harbour mouth | 45,544 | 9× | 3 / 3 | 3 / 3 / 1 |
| Kelp bank | 28,396 | 9× | 3 / 3 | 3 / 3 / 1 |
| Sandbar | 24,614 | 9× | 3 / 3 | 3 / 3 / 1 |
| Rocky point | 25,596 | 9× | 3 / 3 | 3 / 3 / 1 |
| Deep channel | 24,446 | 9× | 3 / 3 | 3 / 3 / 1 |

The five six-view review sheets and five top plates were opened. The day/night
views show the ground dressing, water-colour differences and warm night deck
pools. Source models, FBX exports, JSON files, individual 1440×900 ground renders
and top plates are present in each named directory. Day and night share one
model and use separate lighting presets.

The focused audit reopened each source and its immutable original baseline,
recomputed bounds, and confirmed the retained visible coastal vertices above
the intentionally lowered deep skirt. Each expanded seabed is closed with no
nonmanifold edges. Roots are identity transforms; units are metres; declared
waterline is local zero and world Y −0.32. Ground anchors are world deck-centre
positions at Y zero, with headings and distinct pool IDs.

All 15 physical anchor depths match freshly sampled terrain. All 15 travel
polylines connect their declared anchors and pass downward surface checks at
intervals no greater than 0.5 m. Actual FBX imports match every mesh triangle
count and bidirectional nearest-vertex positions after the documented ART108 X
compensation. Maximum error is 0.000003439 m. Runtime FBX/JSON copies match the
art delivery byte for byte. Original baseline hashes and original flat
Environment model, placement and metadata files were checked. Hashes of all
protected inputs are identical before and after the audit.

The derived `GroundsV1` runtime keys have not yet acquired Unity `.meta` files.
Existing original model GUIDs remain untouched. Native import/binding is still
the code owner's step; this audit did not create metadata, scenes or C#.

These are Blender art-camera reviews with a reference Rowboat and approximate
water/static lighting. Native HUD, live water, all five hulls, mobile framing,
finite-hull/turning clearance and player acceptance remain unverified. Centreline
sampling does not establish hull clearance. Nominal `seabedDepth` is a water
colour preset; `physicalAnchorDepth` is the separately measured terrain depth.

Re-run from the project root:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Art/Source/Art108/audit_maps.py
```

The audit writes only its JSON receipt. No model, runtime asset, original GUID,
Unity scene, C#, git operation or commit was changed by this continuation.

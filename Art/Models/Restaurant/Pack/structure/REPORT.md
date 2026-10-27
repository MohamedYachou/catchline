# PACK-STRUCTURE-1 — overhead anchors

Source delivery by Codex 2 (WSL CLI). Four drop-in, atlas-coloured models; no Assets, runtime code or git changes. Native Unity placement and acceptance remain with Claude/Mo.

| Stem / file (`Restaurant_<stem>.fbx`) | Size W × D × H (metres) | Mount | Pack recipe and authored additions |
|---|---|---|---|
| Pergola | 3.000 × 1.000 × 2.550 | floor | KayKit shelf_A_small four rafter mounting brackets; authored solid bevelled timbers, squared posts, diagonal knee braces, navy foot/collar shoes and brass bolts. Open rafter frame, no roof. |
| CeilingBeam | 2.000 × 0.204 × 0.250 | ceiling | Authored solid bevelled timber beam with two KayKit shelf_A_small end brackets, navy straps and brass pendant eyes. |
| TerraceAwning | 1.510 × 0.889 × 0.400 | wall | KayKit shelf_A_small pair of wall brackets; authored wood batten, navy/cream solid striped fabric with scalloped valance, brass support stays. |
| HangingBasket | 0.442 × 0.442 × 0.745 | ceiling | Kenney pottedPlant leaf-only crown; authored honey wicker basket with woven ribs, three brass suspension chains and top eye. |

## Placement

Unity Y-up, metres, baked axis conversion, identity root transforms. Source Blender coordinates map to FBX `[x,z,-y]`; importer handedness/placement is Claude-owned.

- **Pergola:** floor-footprint-centre origin, four feet at Y=0; 3 × 1 m overall, nominal clear post span 2.59 × 0.67 m; knee braces begin at about 1.90 m. Open rafters, no opaque canopy.
- **CeilingBeam:** top-centre mount Y=0; hangs 0.25 m below the mount. Two end brackets and two brass pendant eyes; place the origin at the chosen ceiling height.
- **TerraceAwning:** origin at wall-contact/top edge of the batten, front faces -Z. All geometry hangs below origin; projects 0.889 m from the wall. Navy/cream solid stripes, scalloped valance and brass stays. Use about 2.6 m wall mount height as in proofs.
- **HangingBasket:** top chain-eye mount Y=0, basket hangs 0.745 m below. Three short interlocking brass chains, dark soil, warm wicker and Kenney foliage; no glow.

`footprint_tiles` are conservative placement envelopes, not runtime seat/layout reservations. `size_unity_m` is W,H,D; exact bounds and meshes are in manifest.json. Overhead proof origins are 2.6 m high. The awning is rotated only in proof displays to face the camera; its exported root remains identity. Grey mounting pads / proof wall / ground grid / cameras / lights are excluded from every export.

## Source and materials

CC0 KayKit Restaurant/Furniture Bits (`shelf_A_small` brackets) and Kenney furniture (`pottedPlant`, foliage material faces only); original downloads and accepted Pack assemblies remain read-only. Main timbers, posts, braces, awning cloth, basket and chains are authored geometry using the supplied atlas colours. No false claim that new timber/fabric/wicker geometry is an unmodified pack model.

Three adjacent accepted atlas PNGs are byte-identical to Pack root: restaurantbits_texture-catchline.png, furniturebits_texture-catchline.png, food-colormap-catchline.png. No new shader/emission dependency, transparent materials or `_Glow` elements. Warm wood, navy, cream, green foliage and brass; no diner-orange.

## Export and reproducibility

Editable .blend per FBX. `build.py` reads accepted light/decor helper modules without editing them. Exact accepted FBX call:

```python
bpy.ops.export_scene.fbx(filepath=..., use_selection=True, object_types={'MESH'},
    axis_forward='-Z', axis_up='Y', apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS', bake_space_transform=True,
    bake_anim=False, path_mode='COPY', embed_textures=True, colors_type='LINEAR')
```

Run Blender 5.2 with build.py `-- 0:4`; then audit_raw.py and review.py `-- audit`, `-- individual`, `-- grid`. Package/seal via Python + Pillow. Rebuild only owned structure folder. Windows Blender 5.2.1 produced this delivery. `review.py` fresh-imports FBXs, rather than rendering unexported scene state.

## Evidence and checks

- `structure-contact.jpg`: all four at game camera pitch 38° / yaw 2°, shared 1 m grid and scale; `structure-contact-844.jpg`: 844-wide overview. `structure-detail-contact.jpg`: individual views at useful detail scale.
- `renders/<Stem>.png`: four fresh-import individual proofs; `renders/grid.png`: shared-scale overview. `visual-review.json` records reviewed final proof hashes.
- `fbx-transform-audit.json`: binary FBX identity roots, units, axes and mesh-only export.
- `geometry-audit.json`: independent binary vertices/bounds, finite coordinates, triangle counts and mount pivots.
- `mesh-audit.json`: fresh-import exact names/mesh counts, valid UVs, decoded atlas images, bounds/pivots, triangle and manifest hash agreement, no glow.
- `preservation-audit.json`: immutable Pack/downloads hash comparison; active Codex 1 terrace and new structure folder excluded. `audit.json`: final package/check seal.

Visual corrections before sealing: replaced notched shelf-plank timber subsets with solid bevelled atlas timbers while retaining pack brackets; reduced proof mounting pads to expose the ceiling beam; connected basket chain links and added visible dark soil; moved pendant eyes into the beam underside to remove a small side gap.

These are isolated source proof renders. Native Unity import, lighting, actual scene fit and performance have not been claimed as verified.

Total geometry: **10,496 triangles**, one body mesh per FBX. Individual counts: Pergola 2,084, CeilingBeam 1,084, TerraceAwning 920, HangingBasket 6,408.

Final source seal: **PASS**, exact4 FBXs /4 editable blends /3 byte-identical atlases /8 decoded proofs; all4 raw-transform, geometry and fresh-import audits PASS. Preservation **4,313/4,313 unchanged**, zero exceptions. Final8proof SHA256s match visual-review.json; all4 grid projected bounds remain in frame. Removed 3 own temporary .blend1 backups after verification. Native acceptance remains pending Claude/Mo.

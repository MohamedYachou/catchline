# Crab Coast — 3D pipeline test

Created with the installed **Blender 5.2.1 LTS** in headless mode from WSL. These are actual editable meshes, not raster render substitutes. Six `.blend` sources, six binary FBX exports, six Blender-rendered previews and a comparison contact sheet are included. No Unity editor was opened.

## Geometry, budgets and scale

Dimensions below are world bounding boxes in metres: **width × depth × height**. In the exported Unity-oriented mesh basis, that is **X × Z × Y**. Counts include every exported mesh, all closed faces, bands and cargo; preview cameras, lights and floor are excluded.

| Prop | Exported triangles | Limit | Bounds, W × D × H (m) | Structure |
| --- | ---: | ---: | --- | --- |
| Crab | **672** | 800 | **0.280000 × 0.247660 × 0.086101** | `Catchline_Crab` → `CrabBody` |
| Banded crab | **800** | 800 | **0.280000 × 0.247660 × 0.086101** | `Catchline_BandedCrab` → identical `CrabBody` + separate `ClawBands` (128 tris) |
| Empty pot | **1064** | 1500 | **0.700000 × 0.550000 × 0.350000** | `Catchline_EmptyPot` → `PotBody` |
| Full pot | **1496** | 1500 | **0.700000 × 0.550000 × 0.350000** | `Catchline_FullPot` → identical `PotBody` + separate `CrabLoad` (432 tris) |
| Crate | **396** | 400 | **0.450000 × 0.320000 × 0.250000** | `Catchline_Crate` → `CrateBody` |
| Buoy | **256** | 300 | **0.250000 × 0.250000 × 0.380000** | `Catchline_Buoy` → `BuoyBody` |

The crab's STYLE.md measurement of **0.18 m is the shell/body length**, not the total envelope including forward claws and legs. The shell is 0.18 m fore-aft and the complete animal is exactly 0.28 m across the legs. Its total depth/height are reported above rather than silently substituting them for body length.

`CrabBody` geometry is identical between crab and banded crab, verified by mesh hash. `PotBody` is likewise identical between empty and full pot. `CrabLoad` contains three simplified cargo crabs at **144 triangles each**; it can be disabled as one child. The cargo deliberately uses simpler geometry than the standalone crab so the full pot, including its catch, remains below 1500 triangles. All state parts are siblings under an identity asset root, avoiding nested mesh-parent axis-bake errors.

All asset roots and mesh objects have applied transforms: location zero, rotation zero, scale one. Geometry is positioned in mesh data. Roots sit at the horizontal bounds centre, with the lowest point at ground zero. Bands and cargo share their parent asset's origin. There are no unapplied modifiers or armatures.

## Materials

No image textures, texture files or embedded textures are used. Mesh faces use flat palette materials with opaque Principled surfaces, zero metallic value and 0.72 roughness. Materials are named for later shared URP remapping; this pass does not create or assign Unity URP `.mat` assets.

| Material | Canonical sRGB base colour | Use |
| --- | --- | --- |
| `M_HullNavy` | `#173F57` | Pot frame, crate, buoy eye |
| `M_SafetyOrange` | `#E36A35` | Crab, cargo crabs, buoy |
| `M_RailIvory` | `#F3F0DC` | Crate rim, buoy stripe |
| `M_Rope` | `#D1AF76` | Pot lashings, buoy rope stub |
| `M_Steel` | `#8FA6AC` | Coarse solid pot lattice |
| `M_Rubber` | `#28343B` | Crab eyes, latch recess |
| `M_SeaTeal` | `#168F9F` | Pot latch and hinges |
| `M_BandIvory` | `#F3DEA1` | Claw bands and crab underside |

Blender shader values are converted from these sRGB colours into linear values. Rendered pixels are affected by lighting and should not be sampled to recreate the palette. `M_PreviewCream` is used only by the preview floor and is excluded from exports.

## Export basis and verification

Sources use normal Blender axes: **Z up, -Y forward, X right**, with metric unit scale 1. FBX export uses `axis_forward='-Z'`, `axis_up='Y'`, `use_space_transform=True`, `bake_space_transform=True`, global scale 1, `apply_unit_scale=True`, and `apply_scale_options='FBX_SCALE_UNITS'`. Only selected asset mesh/empty objects are exported; triangulation is enabled, animation disabled, textures not embedded.

The actual binary FBX mesh data was inspected: **X right, Y up, +Z facing**, with Blender `(X, Y, Z)` converted to FBX `(X, Z, -Y)`. Every exported node has identity local translation/rotation/scale; the conversion is baked into vertex data. FBX's `UnitScaleFactor=100` records one stored coordinate unit as one metre, rather than placing a 100× scale on a mesh node.

Every FBX was imported into a fresh empty Blender scene. The imported bounds match the source bounds within 0.00001 m, triangle counts match exactly, and variant children retain the intended root hierarchy. Camera/light attributes and texture/video objects are absent from all six FBXs. Source `.blend` files retain a clearly separated `PREVIEW_ONLY_NOT_EXPORTED` collection for reproducible renders.

Saved checks: [build metrics](build-metrics.json), [validation results](validation.json). The validator also checks source transforms, no modifiers/image textures, palette names, cargo containment and identical shared base geometry. The [Blender export API reference](https://docs.blender.org/api/5.0/bpy.ops.export_scene.html) documents the export switches; the installed 5.2.1 runtime and binary/round-trip checks are the evidence for these specific files.

**Unity import/runtime validation remains unperformed**, as requested. Shared URP remapping and initial Unity-generated `.meta`/importer settings belong to the later integration pass. No files under `Assets/Scripts` or `Assets/Scenes` were changed.

## Files and visual review

- Sources: `Art/Models/Props/{Crab,BandedCrab,EmptyPot,FullPot,Crate,Buoy}.blend`
- Exports: `Assets/Art/Models/Props/{Crab,BandedCrab,EmptyPot,FullPot,Crate,Buoy}.fbx`
- Previews: `Art/Models/Props/Previews/<prop>.png`, 768 × 768.
- [Contact sheet](Previews/ContactSheet.png): all six actual rendered meshes beside [the approved prop concept](../../Concepts/13-crab-coast-props.png).

Previews use an **orthographic camera 45° down, 35° yaw from the front**, cream floor/background, broad area lights, a neutral Standard view transform and Cycles CPU rendering at 32 samples with denoising. Each prop is framed individually; the contact sheet is a visual comparison, not a common-scale lineup. Actual size comes from the table and meshes.

The updated pots use 0.036 m chunky rails/posts, four closed solid rope lashings and a broad teal latch over a dark recess. Both state variants share the updated frame. The shapes deliberately use fewer lattice bars, simpler rope, broader faces and less surface detail than the concept illustration to meet the explicit triangle budgets without textures. The material families, claw/band states, rectangular pot, slotted navy/ivory crate and orange/ivory buoy follow the reference. These are a first small-prop pipeline pass, with the starting boat and crew now supplied separately in the Gull Harbour batch. Crab Coast is location 2.

## Rebuild from WSL

Run from the `Catchline-art-style` worktree. These commands regenerate the six assets and their render previews, validate exports and compose the contact sheet:

```bash
"/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" \
  --background --factory-startup --python-exit-code 1 \
  --python 'C:\Users\momoy\Projects\Catchline-art-style\Art\Source\build_crab_coast_props.py'

"/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" \
  --background --factory-startup --python-exit-code 1 \
  --python 'C:\Users\momoy\Projects\Catchline-art-style\Art\Source\validate_crab_coast_props.py'

python3 Art/Source/make_prop_contact_sheet.py
```

The builder also accepts a subset after `--`, such as `-- EmptyPot FullPot`. It is self-contained and requires Blender's bundled Python; the contact-sheet script uses WSL's ffmpeg and DejaVu Sans. Generation scripts are source controls for this art pass and do not execute in the Unity project.

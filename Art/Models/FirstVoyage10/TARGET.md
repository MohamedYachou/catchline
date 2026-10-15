# ART-010 — first-voyage reproduction target

These are Blender reference renders, not screenshots of implemented Unity effects. Windows Codex owns runtime camera, water, contact, lighting and UI integration. The supplied current screenshot is retained as `Unity-before.jpg`; the comparison explicitly labels it and the generated target. Background harbour rocks, UI and bobbing are omitted from the clean render to isolate the boat and contact treatment.

## Exact gameplay camera and layout

Unity camera: orthographic, Euler **(45°, 35°, 0°)**, size **3.2** (6.4 m vertical span), target **(1, 0, -0.7)**, distance **40 m**, near **0.1**, far **120**. Desktop 1440×900; landscape phone 844×390. Keep the same vertical span on the phone; do not zoom the boat to fill its wider frame. Blender's landscape ortho scale is the horizontal span: **10.24** desktop, **13.85025641** phone. No perspective, DOF, lens changes or individually fitted comparison cameras.

**POLISH-002 framing update received during this pass:** Windows retained the angle/zoom and moved the fishing target to `HullDef.Center + (0.35,0,-0.30)`, i.e. rowboat **(1.35,0,0.20)**. `refined-desktop.png` / `refined-phone.png` and `refined-desktop.blend` reproduce that updated framing exactly. Use those for current runtime integration. The before/after comparison and supplied screenshot keep the original target above, making their model comparison consistent. `Quiet-area-guide.png` documents the original comparison frame; review actual HUD placement in the updated runtime frame. Both targets are independently projection-validated. Model roots and placement are identical in both; this is a deliberate camera difference.

The reference generator handles Unity's handedness explicitly. Reference world mapping is `(Unity x, Unity z, Unity y)` into Blender; model roots use a local Y reflection and the opposite Z-yaw. These negative scales exist **only in the source-only demonstration scene**. The exported Rowboat root and all model parts retain positive unit scales and zero rotations. Validation projects four boat landmarks through independent Unity equations and Blender's camera, then compares their normalized image coordinates. This avoids mistaking a mirrored asset preview for the gameplay view.

Actual runtime placements reproduced in Unity metres:

| Object | Position | Yaw | Scale |
| --- | --- | ---: | ---: |
| Rowboat | (1, 0, 0.5) | -90° | 1 |
| Cooler | (1, 0, 1) | 180° | 1 |
| BaitBucket | (0.25, 0, 1.25) | 0° | 1 |
| LunchTin | (1.75, 0, 1.3) | 20° | 1 |
| RopeCoil | (-0.38, 0.01, 0.45) | 30° | 0.8 |
| SmallAnchor | (-0.42, 0.02, 0.95) | 90° | 0.6 |
| TackleBox | (2.32, 0, 1.32) | 90° | 0.8 |
| Lantern | (2.4, 0, 0.55) | 0° | 0.8 |
| Captain rig | (1, 0, -0.05) | 0° | 1 |
| Rod 1 butt | (0, 0.44, -0.615) | aimed below | 1.25 |

Captain is the existing CrewRig with Body, Outfit_Captain and Hat_CaptainCap, sampled from existing **Wait frame 12** and frozen. No rig or animation source changed. Rod is the actual 1.6 m source scaled uniformly to runtime length **2 m**, aimed along normalized **(0.05, 1.6, -0.6)**. The butt coincides with the unchanged port-bow socket. Cooler/bucket minimum height meets the original deck plane; no hovering presentation offsets are added. Oars remain at their original bind pose/pivots. Upper-left status and lower-centre strike areas remain quiet water; `Quiet-area-guide.png` is an annotated reference, not new UI artwork.

## Light, materials and colour management

Canonical model colours are unchanged. All geometry uses the existing `M_*` palette. Timber roughness **0.72**, paint **0.72**, metal response **0** in the existing simplified material setup. Keep the navy blue in shadow; avoid crushed dark paint and yellowed ivory.

Measured Blender reference setup (metres, watts):

| Light | Blender position | Unity position equivalent | Energy | Size | Colour |
| --- | --- | --- | ---: | ---: | --- |
| WarmKey / disk area | (-4, 0, 7) | (-4, 7, 0) | 1100 W | 4.5 m | #FFF2DC |
| CoolFill / disk area | (5, 4, 6) | (5, 6, 4) | 260 W | 6 m | #C6E0EB |

Both aim at the boat centre: Blender (1, 0.5, 0), Unity (1, 0, 0.5). Cool environment **#BCD6DF**, background strength **0.45**. Key arrives from upper-left in the gameplay frame. To approximate its direction with a Unity directional light, forward toward the target is normalized **(5, -7, 0.5)**, approximately Euler **(54.33°, 84.29°, 0°)**. These area-light wattages do **not** translate numerically to Unity directional intensity. Windows should match shadow softness, ivory highlight and navy visibility against the image while choosing the runtime lighting mechanism.

Cycles CPU, **24 samples**, denoising on; **Standard**, look **None**, exposure **0**, gamma **1**, RGB PNG. Hex inputs are decoded from sRGB to linear before shading. No added AO multiplier, bloom, vignette, grain, tonemap contrast boost or baked world lightmap. Soft contact comes from the real geometry and this lighting; avoid stacking heavy SSAO over it in Unity.

## Water, contact and rowing wake

These effects are **reference-only material nodes and geometry** in saved Blender scenes. They do not create or modify runtime water textures or shaders. `REF_ONLY_*` material names and intermediate render tints are demonstration data, not new canonical `M_*` palette entries.

- Water surface: Unity **Y=-0.32 m**, source-only opaque plane, zero displacement. Base **#168F9F**, matte roughness **0.88**, specular weight **0.12**. Broad colour variation runs between base and subdued intermediate **#279DA8**; this is an illustrative low-contrast mix toward the existing **#64C7C4** highlight family, not a proposed new asset material. Use sparse broad patterns rather than white bars or glitter.
- Reproduction node: Object coordinates → Vector Add → Noise Texture, scale **1.7**, detail **0**, roughness **0.25** → colour ramp positions **0.22 / 0.78**. Typical pattern size about **0.6 m**. No bump or displacement. The node vector offset moves from **(0,0,0)** at frame 1 to **(0.36,0.18,0) m** at frame 145 (24 fps / 6 s). Blender's default keyframe easing applies; the second phase is a movement-intent reference, not a runtime animation claim.
- Hull contact: narrow **0.04 m** broken bands, tinted **#CBE4DB**, at Unity **Y=-0.312 m** (8 mm above water for this demonstration). Bands follow the hull section at water level, not the full beam at the gunwale. Skip multiple segments and leave gaps; no continuous bright outline around the whole boat. Relative radial offsets **0.025–0.065 m** from the interpolated waterline. The hull's sloping side naturally hides some sections at this camera angle.
- Rowing wake: only while travelling, illustrative **0.4–0.6 m/s**. Two **0.045 m** ribbons spread from source `(±0.67, 1.94)` to `(±1.20, 3.35)` behind the stern, about **1.4 m** long. Match the short faint V, fade when stopped, and avoid motorboat spray. The example is static geometry; runtime speed/alpha modulation belongs to Windows.
- Stationary: broken contact only, no trailing V. `target-flat`, `target-contact`, `target-rowing`, `target-drift-6s` retain identical camera, model scale and light. The last pair freezes the crew pose to isolate the water offset.

## Model change and integration

Only Rowboat is rebuilt: broader rail bevels (22 mm chamfer), a narrow outer hull shoulder/inner lip, quieter 8-plank timber variation, four broad fastening plates on the existing gunwale and timber end soles outside the walking rectangle. Original part set and all root/oar/socket pivots remain unchanged. Hull shell is **4.2×2.4 m**; authoritative PlankDeck remains **3×2 m**, top at zero. The existing oars and rope already extend outside the hull envelope; total assembled bounds are reported separately rather than incorrectly calling them the hull beam. Triangles **1790 → 2054**; final measurements are in `validation.json`. No new palette names, rig, clips, textures or loose props fused into the model.

Windows integration: import the updated `Assets/Art/Models/Boats/Rowboat.fbx`, retain canonical material remapping and existing oar/socket bindings, and compare the updated fishing view against `refined-desktop.png` and `refined-phone.png`. `after-*` matches the original supplied capture frame for the before/after comparison. Treat the Blender scenes as target documentation, never runtime scenes. ART-009 is a separate prior delivery on the same art branch; merge deliberately rather than assuming it has already been accepted. Keep existing gameplay and save layouts.

## Rebuild and evidence

Use Windows Blender 5.2.1 with `--background --factory-startup --python-exit-code 1 --python <script> -- <mode>`:

1. `Art/Source/render_first_voyage10.py -- before` uses retained Rowboat-before.blend.
2. `Art/Source/build_gull_harbour.py -- Rowboat` rebuilds only Rowboat.
3. `Art/Source/render_first_voyage10.py -- after`, `-- refined` and `-- targets` create original-frame desktop/phone, updated runtime-frame desktop/phone and water variants.
4. `Art/Source/validate_first_voyage10.py` validates the source, actual FBX binary/reimport, old contracts, exact camera projection and protected assets.
5. Python/Pillow `Art/Source/sheets_first_voyage10.py` creates labelled comparisons, identical close crops, quiet-area guide and target sheet.

`baseline-contract.json` and `Rowboat-before.blend` are retained comparison evidence. `protected-hashes.json` tracks unrelated assets, crew source and runtime textures; only the targeted Rowboat FBX may differ. `validation.json` records the actual checks, dimensions, triangles, parts, palette and camera matrices. Original thin stripe shells and assembled/intersecting components are retained intentionally; topology is recorded without pretending the full assembled model is one watertight manifold.

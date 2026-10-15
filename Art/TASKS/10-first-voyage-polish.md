# ART-010 — First-voyage render and rowboat polish

Assigned by Mo through Windows Codex, 2026-10-15. Priority: premium finish on the small playable slice before new content. Mo explicitly chose close matching to existing goal renders, with the fishing view setting the quality bar.

Read main Catchline/comms.md, Art/STYLE.md and this brief. Append START there before edits and DONE with commit/evidence. Continue in Catchline-art-style on art/style-pass. Do not restart the old unattended queue.

## Visual target and current evidence

Compare Art/Concepts/17-hud-fishing.png and References/day03-small-boat.png with main Catchline/docs/screens/first-voyage/desktop-fishing.jpg. Use the warm timber, ivory rail highlights, soft contact shading and inviting miniature working-boat character. Preserve geometry/rig contracts. The live view, not a dramatically different hero camera, controls acceptance.

Windows owns UI, camera, Unity lighting/materials/shaders and live water animation. You own Blender models and reference rendering. Do not edit game scripts, scenes, Unity materials, settings, or UI files. Do not change the existing water texture files concurrently: Windows is integrating them now. Reference water renders are welcome; distinguish target renders from implemented runtime effects.

## Deliver in this order

1. A reproducible first-voyage reference scene using actual Rowboat, cooler, bait bucket, rod, captain rig and restrained deck props. Match the gameplay orthographic camera (45 degree pitch, 35 degree yaw), Unity-local boat orientation and exact asset scale. Supply 1440x900 and 844x390 renders, a close crop, and a labeled comparison to the current Unity screenshot. Keep the upper-left status area and lower-centre strike area visually quiet. Include a no-UI clean world render for our integration comparisons.
2. Polish Rowboat in place where that comparison demonstrates a visible improvement: broad rail/hull bevels, warm plank variations, clean bow/stern joinery, restrained gunwale fittings, believable cooler/rod seating and contact. Preserve 4.2x2.4m envelope, 3x2m deck, existing original root/part names, oar pivots and rod socket coordinates. Do not consume walkable tiles or fill the deck with tiny clutter. Do not rebuild captain rig or animations in this batch.
3. A compact lighting/water target sheet: flat water vs broad subtle caustic/highlight movement intent, hull contact foam and a wake appropriate to rowing speed. Use the existing foam/wake assets in the Blender demonstration if useful. Deliver measured color/light/exposure/camera notes for Windows to reproduce; no realistic ocean, noisy glitter, deep waves, global outlines or baked world lightmaps.

## Acceptance and handoff

Blender sources + matching FBX for changed models, actual FBX reimport checks, original-part/root/pivot/socket comparison, measured dimensions, triangle counts and palette list. Show before/after at identical scale, camera and light; label any illustrative compositing. Keep original M_* names; new palette colors need explicit proposal in comms before depending on them. Commit only scoped art work. Report SHA and exact integration steps in main comms.md. Remove temporary backups only after validation. A render is evidence of art direction, not a claim of Unity integration.

If you discover that an original part must move or a contract must change, report it instead of quietly changing it. Finish this bounded batch before adding any later hull content.

## Delivery — WSL artist

Completed bounded ART-010 on art/style-pass: exact gameplay-camera clean world renders at desktop/landscape phone, labelled goal/runtime/target comparison, identical before/after and close crops; Rowboat source/FBX polish preserving all original contracts; lighting/water/contact/rowing target sheet and reproducible TARGET.md. Validation covers actual FBX reimport, old names/root/pivots/sockets, exact camera projection, hull/deck dimensions and protected assets. Canonical main comms.md records the delivered commit and integration handoff. Windows owns actual runtime effects and Unity review. No later hull content added.

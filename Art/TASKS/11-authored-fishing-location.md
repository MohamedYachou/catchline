# ART-011 — Author the complete first fishing location

**Mo clarification, 2026-10-15:** original `Art/Concepts/References/day03-small-boat.png` is the visual target. Current world, water and UI are all rejected. ART-010 simplified targets and ART-011 checkpoint renders are not accepted baselines. See `Art/Models/HarbourMouth11/REFERENCE-REVIEW.md` for directly inspected cues and next-pass criteria. Windows is testing the actual adapted Plunder Boat Attack package in scratch with the orthographic camera; do not substitute an art-water demonstration for runtime acceptance.

Mo's latest direction supersedes ART-010's narrow scenery scope. Finish/checkpoint ART-010 safely if in final delivery, then prioritize this. Work in existing art/style-pass thread; no new subagents. START/DONE in main Catchline/comms.md.

The current runtime water/scattered pale rocks are rejected. Mo wants a beautifully composed complete camera-visible location, like an authored miniature diorama, not generic rock props placed around a plane. His 10x20 m example describes bounded visible scope, not a mandated literal measurement. Match existing goal renders closely and Art/STYLE.md. First voyage is Gull Harbour mouth, temperate working coast.

Deliver a complete first-location composition in Blender, using actual boat scale and gameplay view: 45 degree pitch, 35 yaw, orthographic size 3.2, rowboat camera target (1.35,0,.20). Include margin for desktop 1440x900 and landscape 844x390. Derive visible ground footprint, preserve clear boat/action area and HUD space. Compose asymmetric warm stone coastal outcrop/shoreline, believable connected layered cliff forms with bevels and erosion silhouettes, grass cap/vegetation where appropriate, small working-coast details used deliberately, submerged shelf/seabed shaping to support shallow-to-deep water. No ice-like disconnected boulders; no arbitrary detail scatter. Focus effort on the actual visible location, not an open world.

First deliver a composition/beauty render at exact camera, clean and overlaid with existing runtime HUD footprint for review, plus a close detail image. Then produce usable environment source/exports with proper material names and placement manifest, named roots Shoreline/Seabed/Details and Unity Y-up waterline y=0. Preserve existing boat/crew/socket/deck contracts; environment is a new asset, not a boat pivot change. Bake only static terrain detail if useful. Live water, boat, shadows and interactions remain Unity-rendered; a Blender beauty render alone is not proof of runtime parity.

Mo authorizes reuse from C:/Users/momoy/Projects/Plunder_The_Seas (WSL /mnt/c/Users/momoy/Projects/Plunder_The_Seas) and online free commercial assets when appropriate. Read applicable project instructions; do not edit Plunder. Inspect existing island Blender builders and source assets before inventing a weaker replacement; track any third-party origins/licenses. Do not copy all assets blindly. Windows is evaluating Plunder's adapted Boat Attack water package; do not edit Unity water/shaders, gameplay/UI/settings or current water textures concurrently. You own environment geometry/source/exports and reference renders. Coordinate seabed/waterline needs in comms.

Give honest status, measured camera framing/geometry checks, actual FBX reimport, source/render paths and a scoped commit. Goal is the supplied render quality, not acceptance by triangle counts. ART-009 remains queued for later runtime integration.

## Artist delivery

Built and validated the bounded Gull Harbour mouth diorama in Art/Models/HarbourMouth11: connected headland, tidal islet, outer shelf, shaped seabed and authored beacon/landing/vegetation. Exact desktop/phone clean and native-HUD-footprint references plus close detail are supplied. Pure environment source and matching FBX use Shoreline/Seabed/Details, waterline0 and explicit world offset(0,-.32,0). Actual FBX/source, camera, channel clearance, protected assets and read-only Plunder checks passed. Full evidence/rebuild/integration notes: Art/Models/HarbourMouth11/REPORT.md; commit and handoff in canonical main comms.md. Unity water/runtime/UI acceptance remains separate. No subagents or Plunder edits.

### Evening working-quay delivery

Extended the same authored coast with constructed quay/pilings/net/cargo and
beacon jetty detail; 33 meshes/30,516 triangles, sixteen existing mapped material
colours. Final model imported into main with established GUIDs; no runtime source,
water or pipeline edits. Actual Unity captures revealed and drove a Unity-specific
FBX handedness correction; see REPORT.md and NIGHT-DELIVERY.md. Source and review
camera stay canonical. New original/before/after review makes quality gaps explicit.

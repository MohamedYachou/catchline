# Restaurant harbour exteriors

Four complete exterior-only models express the Cafe → Bistro → Restaurant → Seafood house progression. Shared footprint-centre origin, floor contact Z0, one-metre tiles, facade toward Blender +Y / Unity -Z. The restaurant keeps pale warm masonry, navy/blue tiled roofs, ivory window trim, timber, brass and warm window/lantern light. Each stage adds frontage and terrace depth; the final house has three joined gables, a sculpted fish crest, five outdoor tables and twelve string bulbs. Cafe has two outdoor tables, Bistro three, Restaurant four. Upper-floor shutters, flower boxes, entrance pots and later-stage vines retain the concept sheet's harbour house language.

| Stage | Name | FBX | Room footprint (m) | Triangles |
|---|---|---|---|---|
| 1 | Cafe | `RestaurantExterior_Cafe.fbx` | 8 × 5 | 17,972 |
| 2 | Bistro | `RestaurantExterior_Bistro.fbx` | 10 × 5 | 24,924 |
| 3 | Restaurant | `RestaurantExterior_Restaurant.fbx` | 12 × 5 | 31,820 |
| 4 | SeafoodHouse | `RestaurantExterior_SeafoodHouse.fbx` | 14 × 5 | 35,713 |

## Placement and scale

Every FBX has the same local footprint-centre origin at floor Z0, so stage replacement preserves the anchor. Footprints grow symmetrically from8 to14m; do not offset the prefab by half its width. Each matching *.footprint.json records room and terrace bounds, tile dimensions, facade orientation, practical-light positions and a placement example; lighting.json lists the corresponding warm point-light recipe. Roof eaves extend0.22m past walls; terrace rails and plants extend slightly beyond room width. Terrace decks extend1.65/2.5/3/3.5m toward the water and include piles down toZ-1. These overhangs are excluded from the room footprint deliberately. See manifest.json and validation.json for every exported mesh's actual full bounds.

VoyageHarbour.cs places quay top at UnityY0.35 and its water edge aroundZ2.3; row store fronts useZ4.95. With the restaurant centre at Unity[x,0.35,4.95], local facade at+2.5 BlenderY lands at UnityZ2.45; the terrace projects toward negativeZ over the water. Use yaw0 for these assets (existing HouseA fronts-Y and is placed yaw180). Choose a free end-of-row slot wide enough for the14m final building; the example is a coordinate recipe, not a request to overlap occupied buildings. The first cafe spans multiple3m harbour-house bays, consistent with its8×5 interior. Height5.3m is a modest second storey above accepted HouseA3.6m/HouseB3.9m. Scene review includes an unchanged HouseA at real scale beside each stage.

## Atlas, materials and export

textures/* are byte-identical to the accepted Stage1V4 restaurant atlas, preserving its painted navy/blue/ivory/timber palette beside the older harbour kit's flat material colours. That older HouseA kit has no bitmap atlas to reuse. This package introduces no crew-remapped M_SeaTeal/M_Skin names. BaseColor sRGB; Surface linear R roughness/G metallic/B emission; emission = base colour × mask ×2.5. FBX embeds BaseColor, while Surface must be bound by the runtime shader. Production meshes have UV0, separate positive-area UV1 charts, LocalAO vertex colours and one atlas material per mesh. Only model geometry is exported: no sea, neighbouring house, camera, light or presentation floor. Packed source blends contain editable production geometry only.

## Proof and checks

Fresh independent FBX reimport checks exact name inventory, triangle counts, finite bounds matching source within0.00001m, valid material indices, exactly two UVs and positive UV1 areas. Counts are below the self-imposed60k budget per exterior. The converted sign's default extra UVMap was removed before final export. The first camera proof exposed a source-neighbour Preview_Ground plane; final proof appends only HouseWalls, HouseRoof and DoorsWindowsTrim. The sign was moved to the awning front for visibility. No production floor or water plane is present in any FBX.

Four1440×900 harbour views use exactly45° pitch/35° yaw, orthographic framing with Unity size7.5 (Blender horizontal scale24). Position/focus and conversion recorded in harbour-cameras.json. All four use the same framing for an honest growth comparison. Each *-Harbour-check.blend includes review-only quay, painted water, accepted neighbouring HouseA and lights. exteriors-review.jpg is the four-stage contact sheet. visual-review.json records the final images actually opened, not an automated visual acceptance claim.

No Assets, runtime code, metas or git edits; no commit. Claude owns native import, placement at a free harbour corner, stage swapping, Surface binding and practical lights. These are Blender harbour-camera checks, not native runtime acceptance.

## E seal / 2026-10-27 scale correction

All four FBXs re-exported with the Stage1V4 flags: apply_unit_scale=True, apply_scale_options=FBX_SCALE_UNITS, axis_forward=-Z, axis_up=Y, colors_type=LINEAR, mesh-only selection, bake_anim=False, path_mode=RELATIVE. Fresh imports pass every original node/triangle/world-bound/UV check. Geometry unchanged; existing harbour proof hashes remain current and contact sheet reopened. final-audit.json seals source/export/atlas/report/proofs. Native Unity scale/placement acceptance remains Claude. No commit.

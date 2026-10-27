# Restaurant arrange props and effects

Delivered by Codex 2 (WSL CLI). Art only; no Assets, production code, metas or git changes.

Six table assemblies include matching chairs: two seats use 1x1 tiles, four seats use 2x1. Three separate Chair_Tier* FBXs support individual placement. Tier1 is plain plank wood, tier2 teal cloth/ivory runner/candle, tier3 white linen/navy-and-brass chairs/brass linen-shade lamp. Tables have inward-facing chairs and recorded seat sockets.

All16 FBXs have matching `.footprint.json` files: metres, tile1m, footprint-centre local X/Y, contact Z0, identity object origins/scales. Unity receives Y-up via FBX axis conversion. Wall pieces use their bottom contact at0; raise the complete object to `recommended_base_height_m` when mounting. Wall faces point Blender -Y. Four-seat tables occupy 2x1 tiles including tucked chairs. The separate tabletop candle reserves1x1 for metadata consistency but has a .11m-wide base; place its origin on a table, not the floor. Tables include their own candle/lamp.

| FBX | Tiles | Tris |
|---|---|---|
| Dining2_Tier1 | 1x1 | 2044 |
| Dining4_Tier1 | 2x1 | 3908 |
| Chair_Tier1 | 1x1 | 824 |
| Dining2_Tier2 | 1x1 | 2804 |
| Dining4_Tier2 | 2x1 | 4580 |
| Chair_Tier2 | 1x1 | 780 |
| Dining2_Tier3 | 1x1 | 3702 |
| Dining4_Tier3 | 2x1 | 6302 |
| Chair_Tier3 | 1x1 | 1192 |
| WallNetFloats | 1x1 | 1672 |
| WallFishTrophy | 1x1 | 779 |
| WallMenuBoard | 1x1 | 1085 |
| StringLights | 2x1 | 2388 |
| PlantPot_Herbs | 1x1 | 1644 |
| PlantPot_Flowering | 1x1 | 6004 |
| TableCandle | 1x1 | 576 |

Atlas: byte-identical Stage1V4 BaseColor + Surface and atlas.json, supplied in textures/. Base sRGB; Surface linear R roughness/G metal/B emission. All polygon UVs stay within one inset atlas cell, including bevels. Export embeds BaseColor; bind the supplied Surface to the game's existing V4 atlas shader for roughness/metal/emission. Packed RestaurantUpgrades.blend is editable source; Upgrades-V4-check.blend is presentation only. No presentation floor/lights/camera exist in any FBX.

TableCandle.fbx contains TableCandle and independently toggleable TableCandle_Flame meshes. Glow cell19 emits warm ivory; suggested multiplier2.5. The shader must use Surface.B for emission; a plain FBX material importer does not reproduce this custom node network. No point light is baked into the prop.

Steam/steam-sheet.png is2048x256,8frames of256x256 left-to-right, RGBA transparent,8fps looping. Steam/steam.json and validation.json provide rects, pivot, suggested.38m world height and alpha bounds. Use normal alpha blend and billboard orientation over soup/coffee. Native coherent Blender wisps, not stock. Eight PNGs, source Steam.blend, checker review and GIF are included.

Validation: validate.py fresh-imports all16 FBXs and checks exact mesh-only inventories, identity origins/scales, contact0, footprint containment, bounds roundtrip<1e-5m, triangle counts, one atlas material, inset UV cells, loaded embedded base texture and current hashes. All pass. Steam checks all8frames unique256RGBA, nonempty translucent alpha and zero edge clipping. See validation.json and Steam/validation.json.

Visual review: final16closeups and unscaled1440x900/844x390 lineups use the saved V4 camera orientation; the lineups preserve exact position/rotation/lens. Studio floor/lighting differ from room lighting. Three-tier/props contact and steam checker reviewed; details and native placement remain subject to lead import/game acceptance. No Unity runtime acceptance claimed.

from pathlib import Path
from PIL import Image,ImageDraw,ImageStat
import json,hashlib
O=Path(__file__).resolve().parent;W=O.parent/'Stage1V4';rows=json.loads((O/'manifest.json').read_text())['assets']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
contact=Image.new('RGB',(1280,1376),'#15283b');d=ImageDraw.Draw(contact)
for i,r in enumerate(rows):
 im=Image.open(O/'renders'/(r['name']+'.png')).convert('RGBA');im.thumbnail((320,320));x=(i%4)*320;y=(i//4)*344;contact.paste(im,(x,y),im);d.text((x+8,y+323),r['name'],fill='white')
contact.save(O/'upgrades-review.jpg',quality=95)
proof=Image.new('RGB',(1440,936),'#15283b');d=ImageDraw.Draw(proof)
for i,v in enumerate(['before','after']):
 im=Image.open(W/'backwall-renders'/(v+'-room-1440x900.png'));im.thumbnail((720,450));proof.paste(im,(i*720,18));d.text((i*720+8,2),v.upper()+' / V4 camera',fill='white')
 # Rear wall crop at original resolution to expose paint, shelf and coping.
 im=Image.open(W/'backwall-renders'/(v+'-room-1440x900.png')).crop((290,125,1130,260));im.thumbnail((700,300));proof.paste(im,(i*720+10,495));d.text((i*720+10,476),'Upper-wall detail',fill='white')
proof=proof.crop((0,0,1440,650));proof.save(W/'backwall-review.jpg',quality=95)
text='''# Restaurant arrange props and effects

Delivered by Codex 2 (WSL CLI). Art only; no Assets, production code, metas or git changes.

Six table assemblies include matching chairs: two seats use 1x1 tiles, four seats use 2x1. Three separate Chair_Tier* FBXs support individual placement. Tier1 is plain plank wood, tier2 teal cloth/ivory runner/candle, tier3 white linen/navy-and-brass chairs/brass linen-shade lamp. Tables have inward-facing chairs and recorded seat sockets.

All16 FBXs have matching `.footprint.json` files: metres, tile1m, footprint-centre local X/Y, contact Z0, identity object origins/scales. Unity receives Y-up via FBX axis conversion. Wall pieces use their bottom contact at0; raise the complete object to `recommended_base_height_m` when mounting. Wall faces point Blender -Y. Four-seat tables occupy 2x1 tiles including tucked chairs. The separate tabletop candle reserves1x1 for metadata consistency but has a .11m-wide base; place its origin on a table, not the floor. Tables include their own candle/lamp.

| FBX | Tiles | Tris |
|---|---|---|
'''
for r in rows:text+=f"| {r['name']} | {r['tiles_w']}x{r['tiles_d']} | {r['triangles']} |\n"
text+='''
Atlas: byte-identical Stage1V4 BaseColor + Surface and atlas.json, supplied in textures/. Base sRGB; Surface linear R roughness/G metal/B emission. All polygon UVs stay within one inset atlas cell, including bevels. Export embeds BaseColor; bind the supplied Surface to the game's existing V4 atlas shader for roughness/metal/emission. Packed RestaurantUpgrades.blend is editable source; Upgrades-V4-check.blend is presentation only. No presentation floor/lights/camera exist in any FBX.

TableCandle.fbx contains TableCandle and independently toggleable TableCandle_Flame meshes. Glow cell19 emits warm ivory; suggested multiplier2.5. The shader must use Surface.B for emission; a plain FBX material importer does not reproduce this custom node network. No point light is baked into the prop.

Steam/steam-sheet.png is2048x256,8frames of256x256 left-to-right, RGBA transparent,8fps looping. Steam/steam.json and validation.json provide rects, pivot, suggested.38m world height and alpha bounds. Use normal alpha blend and billboard orientation over soup/coffee. Native coherent Blender wisps, not stock. Eight PNGs, source Steam.blend, checker review and GIF are included.

Validation: validate.py fresh-imports all16 FBXs and checks exact mesh-only inventories, identity origins/scales, contact0, footprint containment, bounds roundtrip<1e-5m, triangle counts, one atlas material, inset UV cells, loaded embedded base texture and current hashes. All pass. Steam checks all8frames unique256RGBA, nonempty translucent alpha and zero edge clipping. See validation.json and Steam/validation.json.

Visual review: final16closeups and unscaled1440x900/844x390 lineups use the saved V4 camera orientation; the lineups preserve exact position/rotation/lens. Studio floor/lighting differ from room lighting. Three-tier/props contact and steam checker reviewed; details and native placement remain subject to lead import/game acceptance. No Unity runtime acceptance claimed.
'''
(O/'REPORT.md').write_text(text)
(W/'backwall-REPORT.md').write_text('''# V4 north-wall paint repair

Stage1V4.blend and Stage1V4.fbx redelivered; all239 exported node names unchanged,152488triangles unchanged. Geometry, transforms and secondary UV coordinates match the accepted source. No layout pieces renamed; EXPORT_* naming preserved for the lead's hide-by-name flow.

Changed50meshes only:48RearMasonry_* to atlas stonecool, RearCoping to navy, HighKitchenShelf to wooddark. Added neutral LocalAO=.85 to these formerly plain-material meshes, assigned the existing V4 atlas shader, and named their primary UV layer UV0 to match that shader. Each face samples one inset cell. Original atlas textures unchanged. Source colour/UV repairs avoid the game's former bright striped sampling.

validation.json fresh-import check passes239meshes, original bounds/topology/triangles and secondary UVs. backwall-changes.json records source geometry/transform/UV1 signatures and current export hash. backwall-final-audit confirms texture files resolve in Stage1V4/textures; FBX relative base path is textures/Restaurant_BaseColor.png.

Opened before/after1440x900+844x390 saved V4 camera renders. Final proof shows quieter slate wall, navy top coping and dark shelf beneath warm lanterns. backwall-review.jpg combines before/after plus upper-wall crops. Proof inherits accepted LookProof populated scene and light rig; the runtime r41 appearance is the lead's import check, not claimed here. Existing LookProof.blend is untouched.

Source editable with Blender5.2.1. Backwall helpers regenerate source/audit/proof; backwall-fix.py uses a temporary pre-change backup when present and otherwise repeats the paint repair on the production source; the temporary backup is removed after verification per standing instruction. Production source/export and saved before renders remain. No Assets/code/git changes.
''')
print('REPORTS/CONTACTS PACKAGED')

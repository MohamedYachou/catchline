"""Review sheets and handoff text; no image generation/retouching of source proof."""
from pathlib import Path
import json,math,hashlib
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parent;R=O.parents[3];G=O.parent/'Guests';P=O/'renders'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
def compare(ref,actual,label):
 a=Image.open(R/ref).convert('RGB');b=Image.open(P/actual).convert('RGB');assert a.size==b.size;w,h=a.size;out=Image.new('RGB',(w*2,h+54),'#102732');out.paste(a,(0,54));out.paste(b,(w,54));d=ImageDraw.Draw(out);d.text((18,16),'ACCEPTED LOOK / reference illustration',font=font,fill='#f5e7c5');d.text((w+18,16),'STAGE 1 V3 / actual Blender geometry, no HUD',font=font,fill='#f5e7c5');out.save(P/label)
compare('Art/Source/Restaurant/concepts/ui-service-desktop.png','room-1440x900.png','compare-service-desktop.png')
compare('Art/Source/Restaurant/concepts/ui-2-service.png','room-844x390.png','compare-service-phone.png')
out=Image.new('RGB',(1440,508),'#102732');d=ImageDraw.Draw(out)
for i,(f,label) in enumerate([('camera-persp.png','38deg perspective / 58mm horizontal FOV34.48deg'),('camera-ortho.png','38deg orthographic / horizontal span12.4m')]):
 im=Image.open(P/f);im.thumbnail((720,450));out.paste(im,(i*720,58));d.text((i*720+14,18),label,font=small,fill='#f5e7c5')
out.save(P/'camera-comparison.png')
for pose in ['idle','eat']:
 sheet=Image.new('RGB',(1080,932),'#102732');draw=ImageDraw.Draw(sheet)
 for i,name in enumerate(['Ada','Ben','Cora','Dan','Edda','Finn']):
  im=Image.open(G/'renders'/('Guest_'+name+'-'+pose+'.png'));x=i%3*360;y=i//3*466;sheet.paste(im,(x,y+26));draw.text((x+12,y+3),name+' / '+pose,font=small,fill='#f5e7c5')
 sheet.save(G/'renders'/('guests-'+pose+'-sheet.png'))
M=json.loads((O/'build-metrics.json').read_text());A=json.loads((O/'validation.json').read_text());D=json.loads((G/'validation.json').read_text());C=json.loads((O/'final-cameras.json').read_text());L=json.loads((O/'lighting.json').read_text())
# Assign explicit URP light recipe values, authored starting settings rather than watt conversion claims.
for row in L['lights']:
 n=row['name'];typ=row['type'];p=row['blender_power']
 row['URP_range_m']=0 if typ=='SUN' else (2.2 if 'Candle' in n else (3.5 if typ=='POINT' else 5))
 row['URP_intensity_lumens_or_lux']=.12 if typ=='SUN' else (30 if 'Candle' in n else (260 if 'WallLantern' in n or 'JettyLamp' in n else (110 if typ=='POINT' else (750 if 'Kitchen' in n else 500))))
 row['URP_mode']='Mixed realtime direct + baked indirect' if typ=='POINT' else ('Baked area indirect' if typ=='AREA' else 'Realtime directional')
L['URP']={'colour_space':'Linear','HDR':True,'ambient_srgb':'#5579A6','ambient_intensity':.12,'tone_mapping':'ACES','post_exposure_ev':.4,'white_balance_temperature':6,'saturation':-4,'contrast':12,'bloom_threshold':1.8,'bloom_intensity':.12,'bloom_scatter':.55,'emission_lantern_srgb':'#FFB943','emission_lantern_HDR_multiplier':5,'emission_existing_atlas':'Keep V2 texture/vertex-AO shader; windows use V2 authored material emission recipe','SSAO_intensity':.35,'SSAO_radius_m':.16,'DOF':False,'vignette':0,'grain':0,'lightmaps':'Bake additive wall UV1 with referenced V2 UV1; 20 texels/m starting density, pad4px. Light probes at staff/diner/queue head and torso heights; reflection probe box room+quay. Areas are bake-only.'}
(O/'lighting.json').write_text(json.dumps(L,indent=2))
cam=C[0];phone=C[1]
text='''# RESTAURANT-LOOK-DETAIL-3 — room look handoff

Codex 2 (WSL CLI). Source/proof delivery; lead/Mo visual acceptance and native Unity parity remain separate.

## A — camera

Opened both accepted illustrations and both actual camera studies. The illustration has no recoverable physical camera metadata: **38° elevation, -2° Blender yaw is a measured visual fit**, not a claim of exact reconstruction. Perspective is selected: visible furniture fronts and faces, mild depth enlargement at the quay. Orthographic is supplied for comparison; its more diagrammatic equal sizing is less close.

Coordinate contract: Blender `(X,Y,Z)` -> Unity `(X,Z,-Y)` in metres. Unity camera forward is +Z, so its yaw is **178°**, not -2°. Set scale1, roll0, near0.1, far250, perspective sensor36mm horizontal; disable physical-camera gate-fit overrides and set vertical FOV explicitly below. Aim target Unity(-0.02,0.43,0.55).

'''
text+=f"| Setting | Desktop | Phone landscape |\n|---|---|---|\n| Output |1440×900|844×390|\n| Camera position Unity |{[round(v,6) for v in cam['position_unity_m']]}|same|\n| Euler XYZ Unity |38°,178°,0°|same|\n| Vertical FOV |{cam['vertical_fov_deg']:.6f}°|{phone['vertical_fov_deg']:.6f}°|\n| Horizontal FOV |{cam['horizontal_fov_deg']:.6f}°|{phone['horizontal_fov_deg']:.6f}°|\n| Lens / horizontal sensor |58mm /36mm|47mm /36mm|\n\nAlternative ortho uses the same transform with Unity orthographicSize3.875 (horizontal span12.4m at16:10). Wider phone lens is intentional whole-quay framing, not an unnoticed crop. [Exact cameras](final-cameras.json), [perspective/ortho comparison](renders/camera-comparison.png).\n"
text+='''
## B — night and URP handoff

Blue-hour ambient with opaque honey lantern emission, five table candles, illuminated windows, kitchen/dining warm bounce and quay lamp pool. Cycles OPTIX40 samples, denoised, AgX Medium High Contrast, exposure+0.4EV. Fog-glow threshold1.8, strength0.07,size0.35; no DOF, outlines or transparency tricks. [lighting.json](lighting.json) is the complete list with per-light position in both coordinate systems, sRGB colour, Blender energy, source radius, authored URP intensity, range and bake mode.

URP recipe: Linear colour/HDR, ACES, post exposure+0.4, contrast+12,saturation-4,temperature+6; Bloom threshold1.8,intensity0.12,scatter0.55. Ambient sRGB#5579A6,intensity0.12; directional0.12lux/cool blue, soft shadows. Lantern emission sRGB#FFB943×5. Point lights mixed: wall/quay260lm range3.5m, existing/window110lm range3.5m, candles30lm range2.2m. Area bounce bake only: kitchen750lm, dining/terrace500lm, positions/sizes in list. These are explicit authored starting values, **not a numerical watt-to-lumen conversion or demonstrated engine match**. Bake with room UV1 at20texels/m starting density/padding4px, light probes at diners/staff/queue, box-projected reflection probe. SSAO0.35/radius0.16m. Match exposure before increasing practical intensities; check skin and pale masonry for clipping. Native bake/URP appearance untested.

## C — dressed room and production boundaries

8×5 room and3×5 left kitchen retained. All accepted V2 item mesh data are **linked by reference** from `../Stage1V2/Stage1V2.blend`; V2 source remains untouched. Three freestanding tables: two complete1×1 two-seat kits and one2×1 four-seat kit, plus2×1 booth and2×1 pass. Plates/candles/glasses, pass stacks/cloche/fish, existing rear hood/trophy/shelves/cups/pots, additional cup shelf/wall lanterns/raised warm masonry, plants, front-left terrace table/parasol/paving, rope/posts/quay barrel/crates/lamp and right door jetty. [Placements and complete mesh bounds](build-metrics.json).

`Stage1V3.blend` is the room scene with linked kit, lighting and camera. `Stage1V3.fbx` is flattened production geometry only: no water plane, people, cameras, lights or presentation floor. Export-only duplicate meshes avoid shared FBX material-index ambiguity. `EXPORT_` prefix identifies the production mesh in the bounds audit. Linked UV0/UV1 and AO retained; additive geometry has two UV channels and positive-area independent UV1 charts. New masonry/metal uses six named flat palette materials alongside the accepted atlas shader; it is not claimed to share V2's single material. FBX cannot encode the atlas node graph: reuse the V2 atlas/material recipe on meshes whose audited material is Restaurant_Atlas_URP. Keep relative V2 directory available for linked blend/textures. Water is dark review scenery and is excluded from FBX and budget.

'''
text+=f"Production **{M['room_triangles']:,} triangles /180,000**, {A['mesh_count']} meshes; fresh FBX import passes per-mesh triangle/material/UV1/world-bounds audit; largest bounds error{max(r['bounds_max_delta_m'] for r in A['meshes']):.3g}m. No extra oversized plane. [Independent audit](validation.json). This is visual dressing, not a validated runtime navigation/service-anchor layout.\n"
text+='''
## D — six civilian guests

Three adult women (Ada/Cora/Edda) and three adult men (Ben/Dan/Finn); varied skin, hair, shirts and trousers, bob/long/bun/short hair. Compact head/body language follows existing crew. Each FBX has exactly the original20 bones/rest matrices/parents at original scale, no added bones, normalized weights, original11 clips plus49-frame Sit/Eat (24fps,2s loop span). Sit lifts hips to the kit cushion and bends knees; Eat brings the right hand up towards the face. Bare-hand gesture, no spoon/food attached. Original Idle/Walk sampled matrices match the original crew FBX within audit tolerance. Unity Humanoid/Generic avatar import and runtime clip blending still need integration checks.

'''
text+='| Guest | Triangles | Rest matrix max difference | Idle/Walk max difference | Eat hand travel |\n|---|---:|---:|---:|---:|\n'
for r in D['guests']:text+=f"|{r['name']}|{r['triangles']}|{r['bone_names_parents_rest_max_delta_m']:.3g}|{max(r['original_idle_walk_sampled_matrix_delta'].values()):.3g}|{r['eat_hand_travel_m']:.3f}m|\n"
text+='''
[Guest validation](../Guests/validation.json), [idle sheet](../Guests/renders/guests-idle-sheet.png), [meal gesture sheet](../Guests/renders/guests-eat-sheet.png). Each of the24 individual guest images was opened, including side-on seated poses. Guest source blends save neutral/rest; FBX contains all13 clips. Individual source palettes/rig contract in build-metrics.json. Bodies use original proportions, not six unique body sculpts.

## E — actual proof and remaining differences

[Desktop1440×900](renders/room-1440x900.png), [phone844×390](renders/room-844x390.png), [desktop side by side](renders/compare-service-desktop.png), [phone side by side](renders/compare-service-phone.png), [populated ortho alternative](renders/room-ortho-1440x900.png). `LookProof.blend` reproduces populated scene. Original cook/waiter rig outfits and Mira are unchanged; six unique guest assets instantiate eight diners plus three queue guests (deliberate repeats). Mira is behind reception, queue on right jetty. Character placements/clips/source hashes in [characters.json](characters.json). These are rendered Blender scene proofs, not Unity/HUD screenshots. Every final PNG opened; final hashes and findings in visual-review.json.

| Remaining gap | Honest limit / implication |
|---|---|
| Painterly detail | Accepted illustration has more irregular painted surfaces, tiny crockery, foliage and atmospheric brush detail; real V2 kit retains cleaner faceted geometry/palette. This does not establish an exact pixel match. |
| Proportions/layout | Fixed8×5 room and reusable footprints constrain paths and guest density; perspective fit differs from the illustration's inconsistent object scales. |
| Faces/animation | Civilians share crew proportions; no bespoke facial animation. Eat is a simple hand-to-face gesture without cutlery. Repeated guest instances are visible. |
| Framing | Full-quay phone proof makes restaurant smaller than a cropped UI composition; source reference contains HUD and this scene does not. |
| Lighting/water | Blender indirect light/glow and smooth reflective review water are not the runtime water/URP bake. URP recipe needs an actual engine comparison. |
| Function | Queued and seated poses are authored proof, not validated navigation, chair occupancy, service reach, animations driven by gameplay, or player-save state. |

No Assets/.cs/.meta/git/player save operations, installs, subagents or watchdog changes. Temporary backups removed only after final validation and image opens. Acceptance belongs to lead/Mo; this report records source checks and observed proof only.

Rebuild with existing Windows Blender: `python3 run.py build validate review`; from Guests `python3 run.py build validate` first. Review sheets/report: `/home/mo/.venvs/catchline-ui/bin/python pack.py`. Audit: `/home/mo/.venvs/catchline-ui/bin/python audit.py` (existing Pillow environment; no install). No main Unity batchmode involved.
'''
(O/'REPORT.md').write_text(text)
(G/'REPORT.md').write_text('# Restaurant civilian guests\n\nSix FBX/blend pairs, same original CrewRig20-bone skeleton, original11 actions plus Sit/Eat. Each below12k tris. [Full handoff](../Stage1V3/REPORT.md), [independent reimport audit](validation.json), [source contracts/palettes](build-metrics.json). 24fps; Sit/Eat49-frame clips including endpoints, 2s loop span; no root travel. Native avatar/clip blend acceptance pending.\n')
print('SHEETS/REPORT PACKED')

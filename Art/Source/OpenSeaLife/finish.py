"""Seal only after manual image review inventory is complete."""
from pathlib import Path
import json,hashlib,ast
from PIL import Image,ImageDraw,ImageFont
S=Path(__file__).resolve().parent;R=S.parents[2];O=R/'Art/Models/OpenSeaLife'
N=['Dolphin','DolphinPod','GannetDive','DiveSplash','BaskingFin','FloatingCrate','DriftNetBuoy','DriftLog','DistantSail']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
A={n:json.loads((O/'metrics'/(n+'-audit.json')).read_text()) for n in N}
for n,a in A.items():
 assert a['result']=='PASS'
 for ext in ('blend','fbx'):assert a['sha256'][ext]==sha(O/(n+'.'+ext))
images=sorted((O/'renders').rglob('*.png'));images=[p for p in images if p.name not in ('review-sheet.png','clip-sheet.png')];assert len(images)==82,len(images)
review=json.loads((S/'opened-images.json').read_text());assert set(review['opened'])=={p.relative_to(O).as_posix() for p in images}
for p in images:Image.open(p).verify()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18)
# All studio views at useful contact-sheet sizes; exact fullsize files remain alongside.
studio=[p for p in images if p.parent.name!='Assembly' and not p.name.startswith('action-')]
sheet=Image.new('RGB',(1500,9*270),'#E9E3D8');d=ImageDraw.Draw(sheet)
for i,n in enumerate(N):
 for j,v in enumerate(['three-quarter','front','right','back','top']):
  im=Image.open(O/'renders'/n/(v+'.png')).convert('RGB');im.thumbnail((296,240));x=j*300;y=i*270;sheet.paste(im,(x+(300-im.width)//2,y+27));d.text((x+5,y+4),n+' / '+v,font=font,fill='#173F57')
sheet.save(O/'renders'/'review-sheet.png')
clips=[(n,c) for n in N for c in A[n]['animation']];sheet=Image.new('RGB',(1500,len(clips)*250),'#E9E3D8');d=ImageDraw.Draw(sheet)
for i,(n,c) in enumerate(clips):
 for j in range(5):
  im=Image.open(O/'renders'/n/('action-'+c+'-'+str(j)+'.png')).convert('RGB');im.thumbnail((296,222));x=j*300;y=i*250;sheet.paste(im,(x+(300-im.width)//2,y+25));d.text((x+5,y+3),n+' '+c+' '+str(j),font=font,fill='#173F57')
sheet.save(O/'renders'/'clip-sheet.png')
text='''# OPEN-SEA-LIFE-ART-1 — sailing-leg wildlife and flotsam

Codex 2 (WSL CLI), 2026-10-26. Nine independent metre-scale FBXs and editable blends; integration assets only, no event mechanics. No Unity, Assets, meta, C# or git operations. Five views per item, five samples per clip, and paired1440x900/844x390 sailing45 assemblies are in renders/. Every82required image opened individually; contact sheets are additional quick-reference evidence.

## Coordinates, pivots, import

Blender X right, -Y forward, Z up; Unity X right, Y up, +Z forward. Scene scale1 metre, FBX UnitScaleFactor100. All object scales1. Each top-level asset root stays fixed at its waterline/contact origin. Underwater geometry is intentional; do not move the root to the mesh bottom. No presentation floor, shadow catcher, lights, cameras or water is exported. Opaque flat house-palette materials, no textures or two-sided skins. Normals follow authored facets. Production URP material binding remains the integrating lead's responsibility.

For animated assets set the Unity importer Animation Type to **Legacy**, enable animations, disable root motion, and explicitly configure clip names, frame ranges and wrap modes below. FBX action metadata carries `legacy` and `loop` hints but cannot set Unity's importer settings. FBX take names may be prefixed with the armature name and a pipe; use the final suffix as the public clip name. Use Animation.Play/CrossFade on the corresponding imported animation component; loops need Loop, once clips need Once/Clamp as appropriate. The world root never translates; animal body bones move relative to the fixed waterline pivot.

| Asset | Triangles / cap | Rest size Unity XYZ, m | Clips (30 fps; inclusive frame range) |
|---|---:|---|---|
'''
for n,a in A.items():
 cap=json.loads((O/'metrics'/(n+'-build.json')).read_text())['limit'];clips='; '.join(f"{c}:1–{v['source']['sample_frames'][-1]}, {v['source']['seconds']:g}s, "+('loop' if v['source']['loop'] else 'once') for c,v in a['animation'].items()) or 'static'
 text+=f"| {n} | {a['source']['triangles']} / {cap} | "+' × '.join(f'{x:.3f}' for x in a['dimensions_unity_xyz_m'])+' | '+clips+' |\n'
text+='''
## Item contracts and placement

- **Dolphin**: root `Dolphin`, child `DolphinRig`, skin `DolphinSkin`. Five bones Root/Body/Tail/Flipper.L/Flipper.R. Grey back, silvery sides and pale belly, curved swept dorsal, horizontal notched flukes, elongated beak and small eyes. Rest body intersects waterline: show with production water. Swim1.2s closes exactly, with body heave/pitch, fluke beat and flipper motion; translate/rotate the world instance in code to travel. Leap1.4s is a complete local up-and-back arc, peak body rise1.65m and whole animal above water, ending at its surface starting pose. It has a small fore-aft excursion but no net root drift. Keep ~4m local clearance for the full arc.
- **DolphinPod**: root `DolphinPod`, immediate children `Dolphin_1`, `Dolphin_2`, `Dolphin_3`; each owns its identically named Rig and Skin. Child waterline pivots in Unity are(-1.10,0,-0.50),(0,0,0.60),(1.10,0,-0.20). Three distinct rigged dolphins in a loose staggered line, each380tri. Swim/Leap exported for each rig (six FBX takes total); choose each child animation independently for phase offsets. The authored preview is synchronized; runtime may stagger Swim start times and Leap triggers. Do not play every take on the pod root and assume it targets all three imported animation components. Maintain the child placements or detach with world transform preserved.
- **GannetDive**: root `GannetDive`, four-bone `GannetDiveRig`, `GannetDiveSkin`. Wingspan2.07m, ivory body, black tips, buff crown and long pale bill. Geometry starts gliding1.1m above its waterline pivot. Glide2s gently heaves at altitude. Dive0.9s pitches the bird nose-down, folds both wings aft, then plunges entirely below water. End body descent2.25m relative to glide; never loop Dive. Position the root at desired sea contact level. After Dive, hide/reset/reposition the instance explicitly; do not leave it below the water until another animation unintentionally resurfaces it.
- **DiveSplash**: root `DiveSplash`, `DiveSplashCrown` mesh; open hollow ivory crown with six alternating tall spikes and four raised droplets, waterline origin. Static128tri. Scale/fade briefly at the gannet's contact point in code; no particle system, transparency shader or timing mechanics supplied. It is a small authored splash, not persistent foam or a change to shared water.
- **BaskingFin**: root `BaskingFin`, `BaskingFinRig`, `BaskingFinSkin`, three bones Root/Body/Tail. Rounded grey-brown dorsal and smaller tail tip, separated1.7m fore-aft; unseen body intentionally omitted. Cruise3s gently sways dorsal and tail independently, fixed root. Friendly smooth silhouette, no mouth, teeth, attack cue or threat mechanic. Translate in code at a calm speed.
- **FloatingCrate**: root `FloatingCrate`, `BrokenFishCrate`. About0.64m wide with open top, floor slats and one visibly broken upper slat in two ragged pieces. Lower timber extends below water. Static; whole-root bob/roll in code. Honey timber and dark corner battens match existing working-coast props.
- **DriftNetBuoy**: root `DriftNetBuoy`, `OrangeNetFloat`, `TangledNet`. Orange float, top neck and open green net lattice draped below the waterline. Root is waterline centre, not buoy bottom. Static lattice and float move together; mild whole-root bob only unless a future runtime deformer is supplied. This is scenery, not an interactive fishing station.
- **DriftLog**: root `DriftLog`, `WeatheredLog`; child contact pivot `GullSeat` at source(0,-.23,.19), Unity(0,.19,.23), containing static `PerchedGull`. Weathered1.835m log with pale cut ends, branch stub, two restrained bark ridges. Gull is included; replace/hide it under GullSeat if runtime wants its shared animated gull. Do not add a duplicate on top without hiding the included bird. Mild roll/bob keeps feet attached.
- **DistantSail**: root `DistantSail`, `DistantDinghy`,100tri. Ivory main/jib, navy hull/deck and warm wood mast,1.54m long and1.87m total height including underwater hull depth. Static; use as a far-off silhouette, no crew or rig animation. Small hull at horizon distance, without giant scaling or a navigational promise.

## Suggested sparse sailing-leg spacing

These are art-composition suggestions, not tested navigation positions. Place wildlife off the boat's projected route and outside the HUD's top-centre destination plate and upper-right coin/home cluster (reference opened: docs/screens/map10-seal-cliffs-1/sail-out-1440.png). Let water stay quiet. Use one family at a time near camera: pod12–20m from route, other pods at least50–80m apart; individual gannet15–30m off route and separate dive splashes by20m; basking fin20–35m off route, no repeated fins within60m; flotsam6–12m off route, roughly15–30m apart; distant sails60–120m from route, at least80m between sails. Adjust all distances to actual camera visibility/map scale and never obstruct casts, lanes or shore approaches. Dense Assembly is an evidence inventory, not a proposed simultaneous spawn layout. No sea-event rules or collision/nav data delivered.

## Palette and review

The existing sailing capture has restrained muted blue-teal water. Dolphin grey/ivory, gannet ivory/black/buff, warm grey-brown fins, honey/weathered timber, green net, orange buoy and navy sail hull remain distinct without neon accents or outlines. Isolated assembly water uses #1C6E7E, matching accepted life-art evidence; this is a matte review plane, not an imitation or replacement of the live water shader. Warm key/cool fill, no bloom/DOF/global outline. Five-view studio floors sit below lowest geometry to reveal submerged portions. Animation frames hide the floor to show the complete local motion, including submerged endpoints. All action frames share one fitted camera per item so movement and disappearance are not hidden by per-frame recentering.

## Actual-FBX evidence and limits

All nine independent Blender5.2FBX reimport audits passed: finite nonzero faces, used vertices, triangle caps, every-mesh physical bounds, source/import ordered polygon surfaces, hierarchy, material colours, scale1/metres and no exported presentation geometry. Every animated vertex has normalized skin weights; roots fixed at every integer frame; all five sample surfaces per clip match source within20micrometres; all looping clips close within20micrometres. Leap wholly airborne at mid-clip and back at waterline at its end; Dive wholly submerged at end. Three pod rigs tested individually. Initial diagnostics found unbound shared pod action slots and insufficient gannet terminal descent; both corrected and final independent audits PASS. No defect waived.

Detailed metrics and exact FBX hashes: metrics/*-audit.json. Each includes everymesh bounds/palette, source/import geometry and deformed sample comparisons. renders/<item>/ contains45studio images total and35sampledclip frames; renders/Assembly/ has1440x900 and844x390 sailing45 images at equal horizontal world span. review-sheet.png and clip-sheet.png are additional contacts. visual-validation.json records actual opened-image inventory and observations. These prove source-art technical/visual checks only; production water, Unity Legacy clip import/binding, HUD, native rendering and navigation placement remain lead scope.

## Reproduce

`python3 Art/Source/OpenSeaLife/run.py build <asset...>`, then `audit <asset...>`, then `render <asset...> Assembly`, using installed Windows Blender5.2. Render independent work batches without overlapping output names. finish.py uses /home/mo/.venvs/catchline-ui/bin/python after opened-images.json records the actual review. Existing helper imports are read-only: build_crab_coast_props.py, HarbourV2/audit.py, Skerries/render.py. No browser/HTML checks apply to these 3D assets; no formal Impeccable UI audit or native acceptance claimed. No subagents, commits, background daemon, player save operations, temporary backups or changes outside the brief's art paths and canonical diary.

## Every actual exported mesh bound (source X/-Y forward/Z up, metres)

| Asset / mesh | Minimum | Maximum | Triangles |
|---|---|---|---:|
'''
for n,a in A.items():
 for mn,row in a['imported']['mesh_bounds'].items():text+=f"| {n} / {mn} | {tuple(round(x,5) for x in row['world_min_m'])} | {tuple(round(x,5) for x in row['world_max_m'])} | {row['triangles']} |\n"
text+='\n## Exact sRGB material palette\n\n| Material | Hex |\n|---|---|\n'
pal=json.loads((O/'metrics'/'Dolphin-build.json').read_text())['palette']
for n,c in pal.items():text+=f'| {n} | {c} |\n'
(O/'REPORT.md').write_text(text)
visual={'task':'OPEN-SEA-LIFE-ART-1','result':'PASS source-art manual visual review','opened_images':review['opened'],'observations':review['observations'],'additional_opened':review.get('additional_opened',[]),'contact_sheet_observation':review.get('contact_sheet_observation',''),'native_acceptance':False,'limits':['Isolated Blender evidence, no production water/HUD/nav acceptance.','Clip importer must be explicitly Legacy, wraps configured by integrating lead.','Assembly density is review inventory only.'],'review_sheets':['renders/review-sheet.png','renders/clip-sheet.png']};(O/'visual-validation.json').write_text(json.dumps(visual,indent=2)+'\n')
for p in S.glob('*.py'):ast.parse(p.read_text())
paths=sorted([p for p in O.rglob('*') if p.is_file() and p.name!='delivery-receipt.json']+[p for p in S.rglob('*') if p.is_file() and '__pycache__' not in str(p)])
receipt={'task':'OPEN-SEA-LIFE-ART-1','owner':'Codex 2 (WSL CLI)','result':'PASS source art, native acceptance false','audit_results':{n:a['result'] for n,a in A.items()},'required_images':82,'sha256':{p.relative_to(R).as_posix():sha(p) for p in paths}}
(O/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert all(sha(R/n)==h for n,h in receipt['sha256'].items());print('OPEN SEA SEALED',len(paths),'hashes',len(images),'required images')

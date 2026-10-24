"""Compose real render evidence and report after independent validation.
Uses Pillow only for layout; does not paint or alter model evidence.
"""
import argparse,json,os
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--owner',default='Codex 1 (Windows app), continuing Codex 2');a=p.parse_args()
R=Path(__file__).resolve().parents[2];name=a.name;out=R/'Art/Models/CrewV2'/name
m=json.loads((out/'build-manifest.json').read_text());v=json.loads((out/'validation.json').read_text())
hair=json.loads((out/'hair-coverage-hits.json').read_text())
assert hair['revision']==m['revision'] and hair['skin_first_hits']==0
assert v['all_passed'] and v.get('revision',m['revision'])==m['revision']
pre=out/'iterations'/m['revision'];W,H=2400,2880
sheet=Image.new('RGB',(W,H),'#F4F0E5');d=ImageDraw.Draw(sheet)
fonts=Path('C:/Windows/Fonts') if os.name=='nt' else Path('/mnt/c/Windows/Fonts')
def font(s,b=False):return ImageFont.truetype(str(fonts/('segoeuib.ttf' if b else 'segoeui.ttf')),s)
def label(x,y,t,s=25,b=True):d.text((x,y),t,fill='#243946',font=font(s,b))
def cell(source,rect,title):
    x,y,w,h=rect
    im=source.copy() if isinstance(source,Image.Image) else Image.open(source).convert('RGB')
    im=ImageOps.contain(im,(w,h-45),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(w-im.width)//2,y+(h-45-im.height)//2));label(x+12,y+h-38,title)
d.rectangle((0,0,W,115),fill='#183E58');d.text((30,14),f'{name} / {m["role"]}',fill='#F4F0E5',font=font(44,True))
d.text((30,74),f'CREW3D-WOMEN | {m["revision"]} | {m["triangles"]:,} triangles | original 20-bone CrewRig / 11 actions',fill='#F4F0E5',font=font(23))
for i,k in enumerate(('front','three-quarter','side','back')):cell(pre/(k+'.png'),(i*600,130,600,640),k.replace('-',' ').title())
ref=R/'Art/Source/UIv2/crew-styles'/('portrait-'+name.lower()+'.png')
if name=='CaptainF':ref=Image.open(R/'docs/screens/crew-styles/lineup-2d.png').crop((1410,92,1765,540))
cell(ref,(10,790,590,655),'2D reference — face / hair target')
cell(pre/'face.png',(605,790,590,655),'3D face — actual render')
cell(pre/'back-hair.png',(1205,790,590,655),'Back hair — actual close-up')
cell(pre/'idle.png',(1805,790,585,655),'Idle — original action / frame 13')
cell(pre/'same-scale.png',(10,1465,1450,650),'Same scale: original crew / Mira / '+name)
cell(pre/'walk.png',(1480,1465,900,650),'Walk — original action / frame 7')
cell(pre/'carry.png',(10,2140,580,680),'Carry — frame 7')
cell(pre/'cast.png',(605,2140,580,680),'Cast — frame 17')
y=2185
for t in [f'{m["triangles"]:,} triangles / 20,000 maximum','512px face + 256px colour-only hair atlas','0.95m scalp; floor pivot; -Y forward','Shared female shape: waist / hips / chest','Original hierarchy, rest pose and actions','Normalized explicit skin weights','Independent source + actual FBX audit PASS','No Unity or Mo acceptance claim']:
    label(1240,y,t,28,False);y+=65
label(30,2840,'Rendered geometry, original animation poses; reference shown unaltered. Studio excluded from export.',23,False)
sheet.save(out/(name+'-review.png'))
# Open every individual PNG and provide an additional contact sheet for visual inspection.
files=sorted(pre.glob('*.png'));contact=Image.new('RGB',(1800,((len(files)+3)//4)*550),'#F4F0E5');cd=ImageDraw.Draw(contact)
for i,path in enumerate(files):
    with Image.open(path) as im:im.load();thumb=ImageOps.contain(im.convert('RGB'),(440,505))
    x=(i%4)*450;y=(i//4)*550;contact.paste(thumb,(x+(450-thumb.width)//2,y));cd.text((x+8,y+510),path.stem,fill='#243946',font=font(24))
contact.save(pre/'contact-sheet.jpg')
fb=v['actual_fbx_roundtrip'];cfg=m['settings']
gaps={
'Lise':'The red curls are overlapping shallow wavy clumps with fine colour fibres. The painted reference has softer, more irregular curls and a fuller swept fringe; the geometry remains an approximation at close range.',
'Tess':'The side braid uses interwoven flattened leaves. The illustration has richer loose wisps and subtler braid transitions; opaque strand tips remain visible at extreme close range.',
'Ines':'The platinum braids are interwoven geometry with fine strand colour. Her adult calm expression is adapted to the fixed chibi face; painted eyelids, lips and translucent flyaways are simplified.',
'Noor':'The blunt bob is layered geometry. The illustration has smoother painted locks and hair ends; rigid Head weighting gives no hair dynamics.',
'Ana':'The high bun uses a continuous support volume covered by swept layered locks. Individual flyaway hairs and the illustration\'s painted curl shading are simplified.',
'Rosa':'The short pixie is layered opaque locks. The eyebrow scar is shallow pale geometry. Fine painted edge wisps and skin detail are approximate.',
'Tove':'Age lines are shallow facial geometry, with silver layered short hair. Painted wrinkles and soft hair edges are simplified; the fixed expression cannot convey every portrait feature.',
'CaptainF':'The auburn low bun and white cap follow the approved lineup. This full-body illustration is the available identity reference; no separate portrait was supplied.'}
report=f'''# {name} — detailed female crew

CREW3D-WOMEN / {a.owner}, 2026-10-24. Revision **{m['revision']}**, **{m['triangles']:,} triangles**. Delivered for Claude/Mo review; native integration and likeness acceptance remain separate.

Files: `{name}.blend`, `{name}.fbx`, `{name}_Face.png` (512² RGB), `{name}_Hair.png` (256² RGB), `{name}-review.png`, `build-manifest.json`, `validation.json`, and individual rendered views under `iterations/{m['revision']}/`. Combined texture area 327,680 pixels, below 2048²; colour-only skin/blush/fibres, no baked lighting.

The role is **{m['role']}**. Hair design: **{cfg['style']}**, base colour `{cfg['hair']}`. Reference is the approved {('lineup top-right captain' if name=='CaptainF' else 'portrait-'+name.lower()+'.png')}. Outfit follows the fixed role palette, including hat, garment and role accessories. Hair uses thin flattened layered clumps with tapered ends and continuous UVs, not round rope strands. All hair is rigidly Head weighted; no particles, simulation or image-to-3D credits.

## Reusable female body

`Art/Source/build_crew_female.py` reads per-character settings from `crew_female_settings.json` and uses the same `crew_female_shape.py` / CrewV2-female-1 deformation field as approved Mira r16. It narrows the waist, widens/deepens the hips slightly and adds a modest chest form under clothes. The builder applies the field exactly once to torso/hip vertices and garment details, by original weight region. Head, limb attachments, height, bone positions and weights remain unchanged. All eight women share this path; men never receive this field. `crew_female_hair.py` provides the per-style layered hair construction.

## Verification

Independent validator reopened the saved Blend, then imported the actual delivered FBX into a fresh scene. PASS: <=20k triangles, identical original 20 bones/hierarchy/rest matrices, all 11 unchanged source action digests, normalized weights, floor pivot, 0.95m bare scalp, metre scale, 24fps, valid texture paths/UVs and source/export geometry. Across 44 pose samples, maximum FBX bone position error {fb['max_bone_position_error_m']:.8f}m and mesh bounds error {fb['max_mesh_bounds_error_m']:.8f}m. Details and delivery hashes are in `validation.json`.

Source axes X right, -Y forward, Z up. FBX uses original axis settings (-Z forward/Y up), metre scale, all actions and no leaf bones. Review studio is excluded. The Blend opens in Idle frame 1.

Review sheet contains front/three-quarter/side/back, rear hair close-up, face beside reference, same-scale original crew/Mira/{name}, Walk/Idle and Carry/Cast frames. Visual likeness and clothing clearance are checked from these selected rendered poses; the numerical pose audit is a rig/roundtrip check, not an exhaustive collision test.

## Hair coverage review

`hair-coverage-hits.json` records {hair['rays']} radial rays at 10-degree intervals over eleven heights (0.705–0.905m), with {hair['scalp_samples']} anatomical scalp samples and **zero skin-first hits**. Every ray and exposed-face/hairline exclusion is listed. Ears, nose and neck are excluded from the scalp by connected-mesh identity. `{name}-hair-review.png` shows six actual headshots from the supplied review script, including both sides and the nape. This is sampled coverage evidence, supplemented by the rendered views, not a continuous mathematical guarantee.

## Honest gaps

{gaps[name]}

Fixed facial expression; no face bones, hair physics, cloth simulation or finger articulation beyond the existing mitten design. No Unity playback, mobile performance or Mo acceptance is claimed.

Reproduce from project root with Blender 5.2:

```text
blender --background --factory-startup --python Art/Source/build_crew_female.py -- --name {name} --revision {m['revision']} --render all --samples 32
blender --background --factory-startup --python Art/Source/validate_crew_female.py -- --name {name}
python Art/Source/compose_crew_female.py --name {name}
```

No Assets, game source, Unity, male outputs, original CrewRig or git changes by this task.
'''
(out/'REPORT.md').write_text(report,encoding='utf-8');print(out/(name+'-review.png'))

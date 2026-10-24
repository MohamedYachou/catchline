"""Layout actual Mira hair-rework evidence after source/FBX validation."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

R = Path(__file__).resolve().parents[2]
O = R / 'Art/Models/CrewV2/Mira-sol'
m = json.loads((O/'build-manifest.json').read_text())
v = json.loads((O/'validation.json').read_text())
h = json.loads((O/'hair-coverage-hits.json').read_text())
assert v['revision'] == h['revision'] == m['revision']
assert v['r20_nonhair_exact'] and v['r20_face_texture_exact'] and h['skin_first_hits'] == 0
P = O/'iterations'/m['revision']
for name, digest in v['delivery_sha256'].items():
    import hashlib
    assert hashlib.sha256((O/name).read_bytes()).hexdigest() == digest
fontpath = Path('/mnt/c/Windows/Fonts/segoeui.ttf')
f = lambda s: ImageFont.truetype(str(fontpath), s)
sheet = Image.new('RGB', (2400, 2890), '#F4F0E5')
d = ImageDraw.Draw(sheet)
d.rectangle((0,0,2400,110), fill='#183E58')
d.text((25,12), f'Mira / {m["revision"]} / full hair rework', font=f(40), fill='#F4F0E5')
d.text((25,66), f'{m["triangles"]:,} triangles | original 20 bones / 11 actions | five r20 nonhair meshes exact', font=f(25), fill='#F4F0E5')
def cell(path, x, y, w, height, label):
    with Image.open(path) as im:
        thumb = ImageOps.contain(im.convert('RGB'), (w, height-48), Image.Resampling.LANCZOS)
    sheet.paste(thumb, (x+(w-thumb.width)//2,y+(height-48-thumb.height)//2))
    d.text((x+12,y+height-41), label, font=f(24), fill='#183E58')
for i,key in enumerate(('front','three-quarter','side','back')):
    cell(P/(key+'.png'),i*600,125,600,620,key.replace('-',' ').title())
for i,(path,label) in enumerate([
    (R/'Art/Source/UIv2/crew-styles/portrait-mira.png','2D portrait target'),
    (P/'face.png','New face / hair'), (P/'back-hair.png','New rear hair'),
    (P/'idle.png','Idle / frame 13')]):
    cell(path,i*600,770,600,640,label)
cell(O/'iterations/r20/temple-left.png',0,1440,600,650,'Archived r20 / side comparison')
cell(P/'temple-left.png',600,1440,600,650,'New side / layered waves')
cell(P/'same-scale.png',1200,1440,1200,650,'Original crew / Mira at original scale')
for i,key in enumerate(('walk','carry','cast','cast-side')):
    cell(P/(key+'.png'),i*600,2120,600,700,key.replace('-',' ').title())
d.text((25,2842),'Actual unretouched renders. Sampled source/FBX proof is separate from Mo likeness and Unity acceptance.',font=f(25),fill='#183E58')
sheet.save(O/'Mira-review.png')
files=sorted(P.glob('*.png'))
contact=Image.new('RGB',(1800,550*((len(files)+3)//4)),'#F4F0E5');cd=ImageDraw.Draw(contact)
for i,path in enumerate(files):
    with Image.open(path) as im: thumb=ImageOps.contain(im.convert('RGB'),(440,505))
    x=i%4*450;y=i//4*550;contact.paste(thumb,(x+(450-thumb.width)//2,y));cd.text((x+8,y+510),path.stem,font=f(24),fill='#183E58')
contact.save(P/'contact-sheet.jpg')
hair=Image.new('RGB',(2240,470),'#F4F0E5');hd=ImageDraw.Draw(hair)
hd.text((15,8),f'Mira | {m["revision"]} | {h["scalp_samples"]} scalp samples / zero skin-first hits',font=f(27),fill='#183E58')
views=[(R/'Art/Source/UIv2/crew-styles/portrait-mira.png','2D reference')]+[(P/'headshots'/('Mira_'+key+'.png'),label) for key,label in [('front','Front'),('q_left','Three-quarter'),('left','Their left'),('back','Back'),('right','Their right'),('q_back','Rear three-quarter')]]
for i,(path,label) in enumerate(views):
    with Image.open(path) as im: thumb=ImageOps.contain(im.convert('RGB'),(310,355))
    hair.paste(thumb,(i*320+(320-thumb.width)//2,55+(355-thumb.height)//2));hd.text((i*320+10,420),label,font=f(22),fill='#183E58')
hair.save(O/'Mira-hair-review.png')
fb=v['actual_fbx_roundtrip']
(O/'REPORT.md').write_text(f'''# Mira — full hair rework

Codex 2 (WSL CLI), 2026-10-24. Revision **{m['revision']}**, **{m['triangles']:,} triangles**. For Claude/Mo review; no new likeness approval or native Unity acceptance is claimed.

Authority: Mo's UPDATE16:55 in `Art/Source/UIv2/FIX-CREW3D-HAIR.txt` unlocks the entire hair, including the front. The old r20 front-only lock is superseded for this work. Immutable `iterations/r20/` retains its original source, FBX, textures, manifest and renders for comparison. All five new nonhair meshes (face, eyes/expression, cap, body/clothes and accessories) have exactly the same coordinates, topology, material slots, smoothing, UVs and skin weights as archived r20. Face texture bytes are unchanged; independent fingerprints and archive SHA256 values are recorded.

New dark-brown hair uses individually curved shallow elliptical locks, colour-only fine fibres, continuous fitted temple/nape coverage, and a full-depth gathered ponytail with outer and inner rings of wavy locks. Both sides and the back are modeled, with hooked ends and roots tucked beneath the cap. Hair is rigid Head-weighted. It has no simulation. Compared with the painted portrait the silhouette, curls and flyaways remain simplified; strand intersections and opaque pointed tips can be seen in close-up. Hair/face likeness is subject to Mo's review.

Delivered: `Mira.blend`, `Mira.fbx`, unchanged 512² `Mira_Face.png`, new 512² colour-only `Mira_Hair.png`, manifest, `validation.json`, `hair-coverage-hits.json`, `Mira-review.png`, `Mira-hair-review.png`, and seventeen individual render views plus six supplied-script headshots under `iterations/{m['revision']}/`. Texture area 524,288 pixels, below 2048²; no baked illumination.

Independent validation reopens saved source and actual exported FBX: original 20 bones/hierarchy/rest matrices, eleven exact source action digests, 44 sampled animation poses, normalized weights, original metre scale/floor pivot/0.95m scalp and valid face/hair UVs with resolved texture hashes. Maximum sampled FBX bone position error {fb['max_bone_position_error_m']:.8f}m; bounds error {fb['max_mesh_bounds_error_m']:.8f}m. Source axes X right/-Y forward/Z up, original FBX -Z forward/Y up. Studio excluded. Saved source opens in Idle frame1. This proves rig/export integrity rather than exhaustive pose collision freedom.

Scalp coverage: {h['rays']} radial rays, every10degrees at eleven heights0.705–0.905m, {h['scalp_samples']} anatomical scalp samples, zero skin-first hits. Every distance and natural exposed-face/hairline exclusion is saved. Ears/nose/neck separated by connected component. Six supplied-script views include both sides and nape. Sampled coverage plus selected renders is not a continuous mathematical guarantee.

Reproduce using Blender5.2:
```
blender --background --factory-startup --python Art/Source/build_mira_hair_v2.py -- --revision {m['revision']} --render all --samples 32
blender --background --factory-startup --python Art/Source/validate_mira_hair_v2.py
blender --background Art/Models/CrewV2/Mira-sol/Mira.blend --python docs/screens/crew-review/headshots.py -- C:/Users/momoy/Projects/Catchline/Art/Models/CrewV2/Mira-sol/iterations/{m['revision']}/headshots/Mira
uv run --with pillow python Art/Source/compose_mira_hair_v2.py
```

No Unity, game source, male folders, original CrewRig, Assets crew exports or git operations.
''',encoding='utf-8')
print(O/'Mira-review.png')

"""Compose only rendered review evidence; never synthesizes or repaints a face.
python Art/Source/compose_crew_male.py --name Pim
"""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
p=argparse.ArgumentParser();p.add_argument('--name',required=True)
p.add_argument('--report-only',action='store_true');args=p.parse_args()
ROOT=Path(__file__).resolve().parents[2];name=args.name
out=ROOT/'Art/Models/CrewV2'/name
m=json.loads((out/'build-manifest.json').read_text());pre=out/'iterations'/m['revision']
validation=json.loads((out/'validation.json').read_text())
assert validation['all_passed'] and validation.get('revision',m['revision'])==m['revision']
assert all(hashlib.sha256((out/filename).read_bytes()).hexdigest()==digest
           for filename,digest in validation['delivery_sha256'].items())
band=json.loads((out/'hair-band-audit.json').read_text())
assert band['all_passed'] and band['revision']==m['revision']
assert band['source_sha256']==hashlib.sha256((out/(name+'.blend')).read_bytes()).hexdigest()
navy='#183E58';cream='#F4F0E5';ink='#243946';muted='#63737C'
sheet=Image.new('RGB',(2400,2120),cream);d=ImageDraw.Draw(sheet)
fontpath=Path('C:/Windows/Fonts/segoeui.ttf');boldpath=Path('C:/Windows/Fonts/segoeuib.ttf')
def font(s,b=False):return ImageFont.truetype(str(boldpath if b else fontpath),s)
d.rectangle((0,0,2400,110),fill=navy)
d.text((34,15),name+' / '+m['role'],fill=cream,font=font(43,True))
d.text((34,71),'CREW3D-MEN  |  '+m['revision']+'  |  Blender 5.2  |  original CrewRig 20 bones / 11 actions',fill=cream,font=font(23))
def cell(path,rect,label,cover=False):
    x,y,w,h=rect
    im=Image.open(path).convert('RGB')
    if cover:im=ImageOps.fit(im,(w,h-43),centering=(.5,.5))
    else:im=ImageOps.contain(im,(w,h-43),Image.Resampling.LANCZOS)
    sheet.paste(im,(x+(w-im.width)//2,y+(h-43-im.height)//2))
    d.text((x+15,y+h-36),label,fill=ink,font=font(24,True))
for i,k in enumerate(['front','three-quarter','side','back']):
    cell(pre/(k+'.png'),(i*600,128,600,648),k.replace('-',' ').title())
cell(ROOT/'Art/Source/UIv2/crew-styles'/('portrait-'+name.lower()+'.png'),(15,800,550,575),'2D portrait — face / hair target')
cell(pre/'face.png',(575,800,550,575),'Authored 3D face')
cell(pre/'same-scale.png',(1145,800,1240,575),'Same scale: original crew / Mira / '+name)
cell(pre/'idle.png',(15,1410,510,650),'Idle — original action, frame 13')
cell(pre/'walk.png',(535,1410,510,650),'Walk — original action, frame 7')
# Rear close-up is an explicitly labelled crop of the actual back render.
im=Image.open(pre/'back.png');im=im.crop((75,30,690,455))
im=ImageOps.contain(im.convert('RGB'),(580,430));sheet.paste(im,(1070,1460))
d.text((1085,1915),'Rear hair / hat detail (render crop)',fill=ink,font=font(23,True))
x=1700;y=1430
checks=[f"{m['triangles']:,} triangles / 20,000 maximum",'512px face + 256px curl textures' if name=='Kofi' else '512px face + 512px beard textures' if name=='Olaf' else '512 × 512 authored face colour texture',
        '0.95 m bare scalp; floor pivot at zero','Original 20-bone hierarchy; 24 fps',
        'All 11 original actions included in FBX','Source + real FBX validation: see JSON',
        'No Unity integration / Mo acceptance claim']
for t in checks:d.text((x,y),t,fill=ink,font=font(23));y+=48
d.text((35,2080),'Rendered geometry and original animation poses. Portrait shown only as reference. Studio excluded from export.',fill=muted,font=font(22))
if not args.report_only:sheet.save(out/(name+'-review.png'))
print(out/(name+'-review.png'))
headviews=['front','q_left','left','back','right','q_back']
if all((pre/('head_'+view+'.png')).exists() for view in headviews):
    heads=Image.new('RGB',(2100,1160),cream)
    hd=ImageDraw.Draw(heads)
    hd.rectangle((0,0,2100,100),fill=navy)
    hd.text((25,20),name+' / hair continuity / '+m['revision'],fill=cream,font=font(38,True))
    reference=ImageOps.contain(Image.open(ROOT/'Art/Source/UIv2/crew-styles'/('portrait-'+name.lower()+'.png')).convert('RGB'),(500,970))
    heads.paste(reference,(10,110))
    hd.text((20,1060),'Unaltered portrait reference',fill=ink,font=font(23,True))
    for index,view in enumerate(headviews):
        xx=530+index%3*520;yy=110+index//3*520
        render=ImageOps.contain(Image.open(pre/('head_'+view+'.png')).convert('RGB'),(510,465))
        heads.paste(render,(xx,yy))
        hd.text((xx+10,yy+470),{'left':'Own left','right':'Own right','q_left':'Front left','q_back':'Rear left'}.get(view,view.title()),fill=ink,font=font(24,True))
    hd.text((20,1120),'Saved-source headshots.py renders; no repainting. Thin layers / temples / ears / nape / hat clearance.',fill=muted,font=font(23))
    if not args.report_only:heads.save(out/(name+'-hair-review.png'))

# The report is only emitted after the independent validator has passed.
gaps={
 'Pim':'The painted fringe outline is interpreted as overlapping sculpted planes. Knit detail is simplified at this topology budget; the portrait has richer painted hair shading.',
 'Dirk':'The grey moustache and temple waves are sculpted layered clumps; the portrait has softer painted transitions and more irregular grey flyaways. Facial age lines are intentionally shallow geometry.',
 'Kofi':'The tight curls are compact overlapping opaque clumps with an authored colour-only curl strand atlas. Individual micro-curls and the portrait\'s painted edge texture are simplified.',
 'Sam':'The swept fringe is interpreted as overlapping sculpted planes. The rubber apron is a skinned surface with no cloth simulation; hand/finger detail uses the shared mitten style.',
 'Mats':'The moustache curls and brown hair use layered opaque clumps. The portrait\'s soft painted strand edges and nose blush are approximate; the apron has no cloth simulation.',
 'Olaf':'The full white beard is opaque layered geometry with fine ridges rather than simulated individual hairs. Painted wisps, skin wrinkles and beard translucency are simplified.',
 'Captain':'The portrait\'s face and cap are adapted to the fixed chibi head/rig dimensions. Gold trim and anchor are geometry; embroidered microtexture and fine cloth weave are simplified.'}
fb=validation['actual_fbx_roundtrip']
texture_detail='An additional `Kofi_Hair.png` 256 × 256 RGB atlas supplies fine colour-only curl strands. Total texture pixels: 327,680.' if name=='Kofi' else 'An additional `Olaf_Hair.png` 512 × 512 RGB atlas supplies fine colour-only beard strands. Total texture pixels: 524,288.' if name=='Olaf' else 'Total texture pixels: 262,144.'
baseline_checks=validation.get('nonhair_baseline_surface_checks',{})
baseline_note=('The optional pre-correction baseline comparison passes bidirectional nonhair surface distances below 1 mm; maximum observed '+
               f"{max(check['max_bidirectional_surface_error_m'] for check in baseline_checks.values())*1000:.3f} mm. "+
               (f'All {len(baseline_checks)} checked nonhair topology/weight/material fingerprints match exactly. ' if
                all(check['exact_topology_fingerprint'] for check in baseline_checks.values()) else
                'Topology indexing/decimation differs; per-part results are in validation.json. ')) if baseline_checks else ''
text=f'''# {name} — detailed male crew

CREW3D-MEN / Codex 1 (Windows app), 2026-10-24. Revision **{m['revision']}**. Art delivery for Claude/Mo review; no Unity integration or Mo likeness acceptance claimed.

- **{m['triangles']:,} triangles** including hair, hat, clothing and props; budget 20,000. Exact per-mesh counts: `build-manifest.json`.
- Texture: `{name}_Face.png`, 512 × 512 RGB, authored skin colour/blush without baked lighting. {texture_detail} Below 2048². Hair, eyes, knit and outfit detail use opaque skinned geometry, palette materials and the listed colour textures.
- Files: `{name}.blend`, `{name}.fbx`, `{name}_Face.png`, `{name}-review.png`; individual orthographic views in `iterations/{m['revision']}/`.
- Reference: `Art/Source/UIv2/crew-styles/portrait-{name.lower()}.png`; role clothes follow the approved lineup and current assignment.

The male body uses the current flat male proportions and original limb attachment positions, with smoother authored garment surfaces. The original CrewRig was loaded from its source, not rebuilt: 20 bones, unchanged names/hierarchy/rest matrices and all 11 original source actions. All mesh vertices have normalized explicit skin weights. No new rig, face bones, cloth simulation or particles.

Independent verification reopened the saved `.blend`, then imported the actual delivered FBX into a fresh empty scene. `validation.json` and `validation.log` record exact source rig/action comparison, 0.95 m scalp, floor pivot, metre scale, normalized weights, relative face texture/UV resolution, identical source/export triangle counts and 44 animation-pose samples across all 11 actions. Maximum FBX bone-position error: {fb['max_bone_position_error_m']:.8f} m; maximum mesh-bounds error: {fb['max_mesh_bounds_error_m']:.8f} m. Original rig SHA256: `{validation['original_crewrig_sha256']}`.

Source axes: X right, −Y forward, Z up. FBX follows the original CrewRig settings (`axis_forward=-Z`, `axis_up=Y`, metre scale, no leaf bones, all original actions, 24 fps). The review studio is excluded from FBX. The `.blend` opens in the original Idle pose, frame 1.

The review sheet contains front, three-quarter, side, back, face beside the unaltered portrait, same-camera/same-scale original crew and Mira, plus Idle frame 13 and Walk frame 7. The rear detail is a labelled crop of the actual back render. Visual review is separate from the technical JSON checks.

The hair correction is integrated in the original male builder: overlapping temple-to-ear layers (curls for Kofi), a continuous fitted original hair volume, irregular tucked nape boundaries, and character-specific side flow. The supplementary `{name}-hair-review.png` shows six saved-source head angles beside the unaltered portrait. No rejected recovery-chat overlay helper is used. {baseline_note}
{validation.get('intentional_hat_change','')}

`hair-band-audit.json` records 324 outside-in rays: every 10 degrees around the entire head, nine heights from a fixed anatomical hairline up to 0.895 m, including the lower rear band down to 0.700 m. All pass with zero skin-first hits. The explicit hairline rises to 0.800 m above exposed ears and 0.885 m at the forehead; intended face/ear skin below it is excluded. This complements the denser 325-ray temple/crown audit in `hair-coverage-hits.json` (649 samples total). Both lists save actual skin/hair/hat hit distances; the full-band receipt includes the current source SHA256. Discrete ray checks complement the six head views and do not prove every surface point.

## Honest gaps / integration limits

{gaps[name]}

Shared original animations are preserved, including their broad elbow/shoulder articulation. These previews do not establish Unity playback, mobile performance, hand-to-equipment contact, collision/IK, animation acceptance or player acceptance. The face is a fixed expression; there is no facial animation.

Rebuild from the project root:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Art/Source/build_crew_male.py -- --name {name} --render all --samples 32 --revision {m['revision']}
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Art/Source/validate_crew_male.py -- --name {name}
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python Art/Source/audit_crew_male_hair.py -- --name {name}
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' -b Art/Models/CrewV2/{name}/{name}.blend -P docs/screens/crew-review/headshots.py -- C:/Users/momoy/Projects/Catchline/Art/Models/CrewV2/{name}/iterations/{m['revision']}/head
python Art/Source/compose_crew_male.py --name {name}
```

No Assets, Unity scenes, gameplay code, female models or original CrewRig changes; no git operations or commit by this task.
'''
(out/'REPORT.md').write_text(text,encoding='utf-8')

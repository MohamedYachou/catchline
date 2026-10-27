"""Review sheets/report from real Blender views or original effect PNG. Pillow."""
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
out=ROOT/'Art/Models/PropsV2'/a.name
m=json.loads((out/'build-manifest.json').read_text());v=json.loads((out/'validation.json').read_text())
assert v['pass'] and v['revision']==m['revision']
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
for file,digest in m['delivery_sha256'].items():assert sha(out/file)==digest
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title=ImageFont.truetype(font,28);body=ImageFont.truetype(font,17);small=ImageFont.truetype(font,14)
W=1440;tile=480;header=104;rows=3 if a.name=='JigRig' else 2
sheet=Image.new('RGB',(W,header+rows*510+90),'#F4EFE3');d=ImageDraw.Draw(sheet)
d.text((24,14),f'{a.name} / PropsV2 / {m["revision"]}',font=title,fill='#173F57')
metric=f'{v["triangles"]:,} triangles · {v["mesh_count"]} mesh parts · metres' if m['kind']=='mesh' else f'{m["logical_size"][0]} × {m["logical_size"][1]} RGBA · alpha {v["alpha_max"]:.3f}'
d.text((24,54),metric+' · saved-source / actual-export audit PASS',font=body,fill='#173F57')
d.text((24,80),'Art evidence only. Native lighting, import and event behaviour require integration review.',font=small,fill='#52636A')
if m['kind']=='mesh':
    files=m['render_files'];files=sorted(files,key=lambda f:['three-quarter','front','left','back','right','top','night-context'].index(Path(f).stem))
    for i,f in enumerate(files):
        im=Image.open(ROOT/f).convert('RGB');im.thumbnail((tile,tile))
        x=(i%3)*tile;y=header+(i//3)*510;sheet.paste(im,(x,y));d.text((x+18,y+480),Path(f).stem,font=body,fill='#173F57')
    if a.name=='JigRig':
        d.text((510,header+2*510+80),'Night panel: review-only warm point light.',font=body,fill='#173F57')
        d.text((510,header+2*510+112),'Export contains mesh only; bind native lamp separately.',font=body,fill='#173F57')
else:
    im=Image.open(out/(a.name+'.png')).convert('RGBA')
    for i,(label,colour) in enumerate([('ivory', '#F4EFE3'),('navy','#173F57'),('checkerboard',None),('ivory / 120px','#F4EFE3'),('navy / 120px','#173F57'),('checkerboard / 120px',None)]):
        bg=Image.new('RGBA',(480,480),colour or '#CCCCCC');bd=ImageDraw.Draw(bg)
        if colour is None:
            for yy in range(0,480,24):
                for xx in range(0,480,24):
                    if (xx//24+yy//24)%2:bd.rectangle((xx,yy,xx+23,yy+23),fill='#F0F0F0')
        view=im.copy();view.thumbnail((min(420,im.width),min(420,im.height)) if i<3 else (120,120))
        bg.alpha_composite(view,((480-view.width)//2,(480-view.height)//2))
        x=(i%3)*480;y=header+(i//3)*510;sheet.paste(bg.convert('RGB'),(x,y));d.text((x+18,y+480),label,font=body,fill='#173F57')
d.text((24,sheet.height-66),'StationsV1 palette · no global outlines · clean silhouette · original references preserved',font=body,fill='#173F57')
d.text((24,sheet.height-37),'Review sheet composed from delivered geometry/effect; no painted model corrections.',font=small,fill='#52636A')
sheet.save(out/'review-sheet.png');pre=out/'iterations'/m['revision'];pre.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'review-sheet.png',pre/'review-sheet.png')
sources=pre/'source';sources.mkdir(exist_ok=True)
for f in ['build_props_v2.py','validate_props_v2.py','compose_props_v2.py']:shutil.copyfile(ROOT/'Art/Source'/f,sources/f)
snapshot={'revision':m['revision'],'source_sha256':{f.name:sha(f) for f in sources.iterdir() if f.is_file()},'delivery_sha256':m['delivery_sha256'],'review_sha256':sha(out/'review-sheet.png')}
(pre/'delivery-snapshot.json').write_text(json.dumps(snapshot,indent=2))
use=m.get('use',m.get('pivot_use'))
provenance='\n'.join(f'- `{x["file"]}` — {x["purpose"]}; SHA256 `{x["sha256"]}`.' for x in m['provenance'])
report=f'''# {a.name} — PropsV2 {m['revision']}

{m.get('origin',m.get('use'))}

Delivery: {metric}. Pivot/use: {use}. Runtime: `{m['runtime_file']}`.

Saved source and actual runtime export independently audited in `validation.json`.
Current delivery hashes, material assignment/colours, mesh counts, finite bounds,
metre scale and protected reference hashes checked. Review: `review-sheet.png`;
source/tool snapshots and individual angle renders under `iterations/{m['revision']}/`.

{('Maximum actual FBX bounds error: '+str(v['max_bounds_error_m'])+' m. Source Z-up / -Y front; FBX -Z forward / Y up.') if m['kind']=='mesh' else ('Transparent corners and finite RGBA checked; painted pixel fraction '+str(v['painted_pixel_fraction'])+'. SVG retained as editable vector source.')}

Read-only provenance:
{provenance}

The existing kit is preserved. Derivative geometry is declared rather than claimed
as a new sculpt. Native Unity import, materials/alpha mode, placement and event or
lamp behaviour remain untested; no scenes or game code changed. Final visual
inspection status is recorded separately in canonical `comms.md`. No Mo acceptance claimed.
'''
(out/'REPORT.md').write_text(report)
print('PROPSV2 SHEET READY',a.name,m['revision'],flush=True)

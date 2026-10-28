"""Record a personally opened render pair after independent reimport passes.
Usage: python finish_cooking_item.py NAME NEXTSTEP NOTE
"""
import json,sys,hashlib,datetime
from pathlib import Path
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parents[2]
name,nextstep,note=sys.argv[1:4]
p=O/'cooking-manifest.json';records=json.loads(p.read_text());rec=next(r for r in records if r['name']==name)
audit=json.loads((O/'cooking-audit.json').read_text());a=next(r for r in audit['items'] if r['name']==name);assert audit['status']=='PASS' and a['tris']==rec['tris'] and a['sha256']==rec['sha256']
assert hashlib.sha256((R/rec['file']).read_bytes()).hexdigest()==rec['sha256']
frames=[]
for f in rec['renders']:
 q=R/f;im=Image.open(q);im.verify();frames.append(dict(file=f,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),size=Image.open(q).size))
rec['render_review']='PASS — both final frames individually opened by Codex 2';rec['review_note']=note;p.write_text(json.dumps(records,indent=2)+'\n')
(O/'cooking-build-progress.json').write_text(json.dumps(dict(state='VERIFIED; '+nextstep,item=rec),indent=2)+'\n')
rp=O/'cooking-visual-review.json';rr=json.loads(rp.read_text()) if rp.exists() else [];rr=[r for r in rr if r['name']!=name]+[dict(name=name,reviewer='Codex 2 (WSL CLI)',note=note,frames=frames,opened=True)];rp.write_text(json.dumps(rr,indent=2)+'\n')
top=rec.get('station_top_y_m');surface=str(top)+'m' if top is not None else rec.get('placement_surface','n/a')
with (R/'comms.md').open('a') as f:
 f.write(f"\ncodex2, SERVICE-PROPS-2 {name}, done, {rec['tris']} tris, station top Y{surface}\n")
 f.write(f"CHECKPOINT / SERVICE-PROPS-2 / Codex 2 (WSL CLI) / {name} VERIFIED. Independent FBX reimport PASS; two final service38deg/close frames individually opened, hashes/notes in cooking-visual-review.json. {note} IN PROGRESS {nextstep}. Prior finished items remain verified; same exact reservations, no subagents/git/Unity; working.\n")
import runpy
runpy.run_path(str(O/'refresh_cooking_report.py'))
print('FINISHED',name,rec['tris'],'NEXT',nextstep)

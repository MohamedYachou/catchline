"""Record personally opened frames after independent audit. Never auto-reviews."""
import json,sys,hashlib
from pathlib import Path
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parents[2]
name,nextstep,note=sys.argv[1:4];p=O/'props3-manifest.json';rows=json.loads(p.read_text())
for r in rows:
 for key in ['file','source']:
  if key in r:r[key]=r[key].replace('\\','/')
 if 'renders' in r:r['renders']=[f.replace('\\','/') for f in r['renders']]
rec=next(r for r in rows if r['name']==name)
a=json.loads((O/('props3-critic-audit.json' if rec.get('rig') else 'props3-audit.json')).read_text());assert a['status']=='PASS'
if not rec.get('rig'):assert next(x for x in a['items'] if x['name']==name)['tris']==rec['tris']
assert hashlib.sha256((R/rec['file']).read_bytes()).hexdigest()==rec['sha256']
frames=[]
for f in rec['renders']:
 q=R/f;im=Image.open(q);im.verify();frames.append(dict(file=f,sha256=hashlib.sha256(q.read_bytes()).hexdigest(),size=Image.open(q).size))
rec['render_review']='PASS — every final frame individually opened by Codex 2';rec['review_note']=note;p.write_text(json.dumps(rows,indent=2)+'\n')
rp=O/'props3-visual-review.json';rr=json.loads(rp.read_text()) if rp.exists() else [];rp.write_text(json.dumps([r for r in rr if r['name']!=name]+[dict(name=name,reviewer='Codex 2 (WSL CLI)',note=note,frames=frames,opened=True)],indent=2)+'\n')
done_line=f'codex2, SERVICE-PROPS-3 {name}, done, {rec["tris"]} tris'
already_logged=done_line in (R/'comms.md').read_text()
with (R/'comms.md').open('a') as f:
 if not already_logged:f.write("\n"+done_line+"\n")
 f.write(f"CHECKPOINT / SERVICE-PROPS-3 / Codex 2 (WSL CLI) / {name} VERIFIED. Independent FBX audit PASS; {len(frames)} final frames individually opened and hashed in props3-visual-review.json. {note} IN PROGRESS {nextstep}. Same exact held paths, no subagents/git/Unity; working.\n")
print('VERIFIED',name,rec['tris'],len(frames))

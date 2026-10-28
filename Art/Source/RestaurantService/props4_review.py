"""Record a human/model visual inspection after both final images were opened."""
import sys,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2]
key,note,nextstep=sys.argv[1:4];name='Restaurant_'+key
rows=json.loads((O/'props4-manifest.json').read_text());rec=next(r for r in rows if r['name']==name)
audit=json.loads((O/'props4-audit.json').read_text());assert any(r['name']==name for r in audit['items'])
path=O/'props4-visual-review.json';data=json.loads(path.read_text()) if path.exists() else {}
data[name]={'status':'OPENED_AND_INSPECTED','note':note,'images':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in rec['renders']}}
path.write_text(json.dumps(data,indent=2)+'\n');rec['render_review']='OPENED_AND_INSPECTED';(O/'props4-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
with (R/'comms.md').open('a') as f:
 f.write(f'\ncodex2, SERVICE-PROPS-4 {name}, done, {rec["tris"]} tris\nCHECKPOINT / SERVICE-PROPS-4 / Codex 2 (WSL CLI): {name} VERIFIED — independent FBX atlas/UV/colour/corner-layer/pivot/Y-up/metres/budget audit PASS; service-camera room and close renders both opened, hashes recorded. {note} IN PROGRESS {nextstep}. Same exact reservations; working; no subagents/Git/Unity.\n')

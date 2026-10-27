"""Source preservation + delivered manifest/proof checks; no game mutations."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
O=Path(__file__).resolve().parent;R=O.parents[4];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if '--reuse-preservation' not in sys.argv:
 baseline=json.loads((O/'preservation-baseline.json').read_text());changed=[n for n,h in baseline.items() if not (R/n).is_file() or sha(R/n)!=h]
 (O/'preservation-audit.json').write_text(json.dumps(dict(pass_all=not changed,files_checked=len(baseline),unchanged=len(baseline)-len(changed),changed=changed,excluded='generated __pycache__ files and new lights directory'),indent=2));print('PRESERVATION',len(baseline),len(changed),flush=True)
if '--preservation-only' in sys.argv:sys.exit(0)
pres=json.loads((O/'preservation-audit.json').read_text());M=json.loads((O/'manifest.json').read_text())['items'];names='PendantLamp WallSconce HangingLantern StringLightsLong TableLamp Brazier'.split()
proofs={}
for p in list((O/'renders').glob('*.png'))+list(O.glob('lights-*.jpg')):
 with Image.open(p) as im:im.load();proofs[p.relative_to(O).as_posix()]=dict(size=list(im.size),sha256=sha(p))
atlases={p.name:sha(p)==sha(O.parent/p.name) for p in O.glob('*.png')}
checks=dict(exact_names={p.name for p in O.glob('*.fbx')}=={'Restaurant_'+n+'.fbx' for n in names},exact6=len(M)==6,editable_blends=all((O/(r['name']+'.blend')).is_file() for r in M),manifest_hashes=all(sha(O/(r['name']+'.fbx'))==r['fbx_sha256'] for r in M),accepted_atlases=len(atlases)==3 and all(atlases.values()),decoded_proofs=len(proofs)==10,source_preservation=pres['pass_all'],phone844=proofs.get('lights-contact-844.jpg',{}).get('size',[0])[0]==844)
for n in ['fbx-transform-audit.json','geometry-audit.json','mesh-audit.json','visibility-audit.json']:checks[n]=json.loads((O/n).read_text())['pass_all']
(O/'audit.json').write_text(json.dumps(dict(pass_all=all(checks.values()),checks=checks,triangle_total=sum(r['triangles'] for r in M),atlases=atlases,proofs=proofs,source_files_checked=pres['files_checked']),indent=2));print('FINAL_AUDIT',all(checks.values()),checks,flush=True)

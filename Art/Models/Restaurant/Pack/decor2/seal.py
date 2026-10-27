"""Final source preservation, delivered-name, atlas and proof-image audit."""
from pathlib import Path
from PIL import Image
import json,hashlib,sys
O=Path(__file__).resolve().parent;R=O.parents[4]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
baseline=json.loads((O/'preservation-baseline.json').read_text());changed=[]
if '--reuse-preservation' in sys.argv:
 changed=json.loads((O/'preservation-audit.json').read_text())['changed']
else:
 for n,h in baseline.items():
  p=R/n
  if not p.exists() or sha(p)!=h:changed.append(n)
cache_changes=[n for n in changed if '/__pycache__/' in n and n.endswith('.pyc')]
source_changes=[n for n in changed if n not in cache_changes]
(O/'preservation-audit.json').write_text(json.dumps(dict(pass_all=not changed,pass_source=not source_changes,files_checked=len(baseline),unchanged=len(baseline)-len(changed),changed=changed,source_changes=source_changes,generated_cache_changes=cache_changes,note='Baseline excludes active lights and generated caches. All listed pre-existing source files are checked byte for byte; later folders are outside the baseline.'),indent=2))
print('PRESERVATION',len(baseline),'source changes',len(source_changes),'generated caches',len(cache_changes),flush=True)
M=json.loads((O/'manifest.json').read_text())['items'];names='ShipWheel PortholeMirror LifeRing WindowFlowerBox WelcomeMat HangingHerbs BarBottleShelf ReedVase'.split()
expected={'Restaurant_'+n+'.fbx' for n in names};atlases={p.name:sha(p)==sha(O.parent/p.name) for p in O.glob('*.png')};proofs={}
for p in list((O/'renders').glob('*.png'))+list(O.glob('decor2-*.jpg')):
 with Image.open(p) as im:im.load();proofs[p.relative_to(O).as_posix()]=dict(size=list(im.size),sha256=sha(p))
checks=dict(exact_names={p.name for p in O.glob('*.fbx')}==expected,exact8=len(M)==8,editable_blends=all((O/(r['name']+'.blend')).exists() for r in M),manifest_hashes=all(sha(O/(r['name']+'.fbx'))==r['fbx_sha256'] for r in M),accepted_atlases=len(atlases)==3 and all(atlases.values()),all_proofs=len(proofs)==12,source_preservation=not source_changes)
for n in ['fbx-transform-audit.json','mesh-audit.json','geometry-audit.json']:checks[n]=json.loads((O/n).read_text())['pass_all']
(O/'audit.json').write_text(json.dumps(dict(pass_all=all(checks.values()),checks=checks,triangle_total=sum(r['triangles'] for r in M),atlases=atlases,proofs=proofs,source_files_checked=len(baseline),generated_cache_changes=cache_changes),indent=2))
print('AUDIT',all(checks.values()),checks,flush=True)

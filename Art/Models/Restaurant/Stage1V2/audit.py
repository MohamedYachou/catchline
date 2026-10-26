"""Seal final, actually-opened evidence. Does not infer Unity acceptance."""
from pathlib import Path
from PIL import Image
import json,hashlib,ast,re
O=Path(__file__).resolve().parent;R=O.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((O/'build-metrics.json').read_text());v=json.loads((O/'validation.json').read_text());opened=json.loads((O/'visual-review.json').read_text());review={r['file']:r for r in opened['images']}
assert v['pass'] and v['unique_library_plus_shell_triangles']<=150000
images=[]
for p in sorted(O.rglob('*.png')):
 if '_before-final' in p.parts:continue
 with Image.open(p) as im:im.load();dims=list(im.size)
 rel=p.relative_to(O).as_posix();assert rel in review,('not actually opened',rel);assert review[rel]['sha256']==sha(p),('changed after open',rel)
 images.append({'file':rel,'size':dims,'sha256':sha(p),'opened':True})
assert len(list((O/'textures').glob('*.png')))==2
for p in (O/'textures').glob('*.png'):
 with Image.open(p) as im:assert im.size==(2048,2048)
for dim in [(1440,900),(844,390)]:
 with Image.open(O/'renders'/f'room-{dim[0]}x{dim[1]}.png') as im:assert im.size==dim
expected={r['file'] for r in v['items']}|{'Stage1V2.fbx'};actual={p.relative_to(O).as_posix() for p in O.rglob('*.fbx') if '_before-final' not in p.parts};assert expected==actual,(expected-actual,actual-expected)
for r in v['items']+[v['assembly']]:assert sha(O/r['file'])==r['sha256']
for row in m['roots']:
 data=next(r for r in v['items'] if r['file']==row['fbx'])['rows'][0]
 if row['footprint_tiles']:
  assert all(data['max_m'][i]-data['min_m'][i]<=row['footprint_tiles'][i]+1e-4 for i in [0,1])
 if row['root']!='RoomShell':assert abs(data['min_m'][2])<1e-5
for r in json.loads((O/'character-scale.json').read_text()):assert sha(R/r['source'])==r['source_sha256']
scripts=[]
for p in sorted(O.glob('*.py')):ast.parse(p.read_text());scripts.append(p.name)
links=[]
for link in re.findall(r'\]\(([^)]+)\)',(O/'REPORT.md').read_text()):
 if link.startswith('https:'):continue
 assert (O/link).is_file(),link;links.append(link)
for r in json.loads((O/'render-manifest.json').read_text()):
 assert (O/'renders'/r['file']).exists()
 if r['file'].startswith('room-'):assert r['pitch_deg']==52 and r['yaw_deg']==0
result={'pass':True,'images':images,'FBX_exports':len(expected),'footprint_roots':sum(bool(r['footprint_tiles']) for r in m['roots']),'python_AST_checks':scripts,'report_local_links':len(links),'characters_original_hashes_match':True,'no_extra_FBX':True,'native_Unity_verified':False,'limits':'UV1 finite/area/range checks are not exhaustive intersection or Unity bake validation; no native UI/runtime acceptance.'}
(O/'independent-audit.json').write_text(json.dumps(result,indent=2))
receipt={p.relative_to(O).as_posix():sha(p) for p in sorted(O.rglob('*')) if p.is_file() and '_before-final' not in p.parts and p.name!='delivery-receipt.json' and not p.name.endswith('.blend1')}
(O/'delivery-receipt.json').write_text(json.dumps({'files':receipt,'git_commit':None,'native_Unity_verified':False,'subagents':[]},indent=2))
print('INDEPENDENT AUDIT PASS',len(images),'opened PNGs',len(expected),'FBX',len(scripts),'scripts')

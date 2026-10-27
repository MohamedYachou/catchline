"""Read-only delivery seal for this art-only task. Run with system Python."""
from pathlib import Path
import json,hashlib,ast
O=Path(__file__).resolve().parent;R=O.parents[3];C=O.parent/'Clothes';G=O.parent/'Guests'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
formal=read(C/'formal-validation.json');assert formal['pass'] and formal['fbx_sha256']==sha(C/'CrewRig_Restaurant.fbx');assert formal['source_sha256']==sha(R/'Assets/Art/Models/Crew/CrewRig.fbx');assert formal['bone_count']==20 and len(formal['clips'])==11;assert len(formal['original_mesh_preservation'])==17 and all(all(r.values()) for r in formal['original_mesh_preservation'].values())
g=read(G/'validation-extra.json');motion=read(G/'audit-extra-clips.json');assert g['pass'] and motion['pass'] and len(g['guests'])==6
for r in g['guests']:
 assert r['fbx_sha256']==sha(G/(r['name']+'.fbx'));assert len(r['clips'])==13;assert all(not m['name'].startswith('M_') for m in r['materials']);m=next(x for x in motion['guests'] if x['name']==r['name']);assert m['fbx_sha256']==r['fbx_sha256'] and len(m['all_original_clip_sample_deltas'])==11
v=read(O/'validation.json');assert v['pass'] and len(v['dishes'])==5
for r in v['dishes']:assert r['fbx_sha256']==sha(O/(r['name']+'.fbx'))
for name in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:assert sha(O/'textures'/name)==sha(O.parent/'Stage1V4/textures'/name)
files=[C/'CrewRig_Restaurant.blend',C/'CrewRig_Restaurant.fbx',C/'formal-validation.json',C/'formal-REPORT.md',C/'formal-visual-review.json',G/'validation-extra.json',G/'audit-extra-clips.json',G/'REPORT-extra.md',G/'visual-review-extra.json',O/'RestaurantDishes.blend',O/'Dishes-V4-check.blend',O/'validation.json',O/'REPORT.md',O/'visual-review.json']
files += [G/(r['name']+ext) for r in g['guests'] for ext in ['.blend','.fbx']]+[O/(r['name']+'.fbx') for r in v['dishes']]
for p in [C/'formal-build.py',C/'formal-validate.py',C/'formal-game-lineup.py',G/'build-extra.py',G/'validate-extra.py',G/'audit-extra-clips.py',O/'build.py',O/'validate.py']:ast.parse(p.read_text())
for p in [C/'formal-visual-review.json',G/'visual-review-extra.json',O/'visual-review.json']:
 for row in read(p)['opened_images']:assert sha(R/row['path'])==row['sha256']
(O/'final-audit.json').write_text(json.dumps({'pass':True,'scope':'HostFormal + six additional guests + five dishes','artifact_count':len(files),'files':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size} for p in files],'no_native_unity_acceptance_claim':True},indent=2));print('FINAL ART DELIVERY PASS',len(files))

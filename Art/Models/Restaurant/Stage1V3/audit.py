"""Seal consistency of observed deliverables. Does not replace manual image review."""
from pathlib import Path
import json,hashlib,ast,re
from PIL import Image
O=Path(__file__).resolve().parent;G=O.parent/'Guests';R=O.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
V=json.loads((O/'validation.json').read_text());D=json.loads((G/'validation.json').read_text());M=json.loads((O/'build-metrics.json').read_text());B=json.loads((G/'build-metrics.json').read_text());C=json.loads((O/'final-cameras.json').read_text())
assert V['pass'] and D['pass'];assert V['FBX_sha256']==sha(O/'Stage1V3.fbx');assert V['triangles']==M['room_triangles']<=180000;assert len(V['meshes'])==len(M['production_meshes'])==166
assert M['V2_blend_sha256']==sha(O.parent/'Stage1V2/Stage1V2.blend');assert D['reference_fbx_sha256']==sha(R/'Assets/Art/Models/Crew/CrewRig.fbx');assert B['original_crew_blend_sha256']==sha(R/'Art/Models/CrewRig/CrewRig.blend');assert B['source_helper_sha256']==sha(R/'Art/Source/Townsfolk/build.py')
for a,b in zip(B['guests'],D['guests']):
 assert a['name']==b['name'];assert a['fbx_sha256']==b['fbx_sha256']==sha(G/(a['name']+'.fbx'));assert a['blend_sha256']==sha(G/(a['name']+'.blend'));assert b['triangles']<=12000 and len(b['clips'])==13
for c in C:
 assert c['rotation_unity_euler_deg']==[38,178,0];assert c['elevation_deg']==38
 if c['projection']=='PERSP':assert 34<c['horizontal_fov_deg']<43
for c in json.loads((O/'characters.json').read_text()):assert c['sha256']==sha(R/c['source'])
chars={r['name']:r for r in json.loads((O/'characters.json').read_text())};assert chars['Diner_E']['position_blender_m']==[.99,.80,.04] and chars['Diner_F']['position_blender_m']==[1.71,.16,.04]
reviews=[]
for root in [O,G]:
 for p in (root/'renders').glob('*.png'):
  with Image.open(p) as im:im.verify()
  with Image.open(p) as im:res=list(im.size)
  reviews.append({'path':str(p.relative_to(O.parent)),'sha256':sha(p),'resolution':res})
manual=json.loads((O/'visual-review.json').read_text());assert manual['all_listed_images_actually_opened'];seen={r['path']:r['sha256'] for r in manual['images']};assert len(seen)==len(reviews)==34,(len(seen),len(reviews))
for r in reviews:assert seen[r['path']]==r['sha256'],r['path']
for f,res in [('room-1440x900.png',[1440,900]),('room-844x390.png',[844,390]),('compare-service-desktop.png',[2880,954]),('compare-service-phone.png',[1688,444])]:
 with Image.open(O/'renders'/f) as im:assert list(im.size)==res
helpers=[]
for root in [O,G]:
 for p in root.glob('*.py'):ast.parse(p.read_text());helpers.append(str(p.relative_to(O.parent)))
links=[]
for root in [O,G]:
 for href in re.findall(r'\]\(([^)]+)\)',(root/'REPORT.md').read_text()):
  assert (root/href).exists(),href;links.append(str((root/href).relative_to(O.parent)))
receipt={'pass':True,'source_only_native_unverified':True,'opened_PNGs':len(reviews),'helpers_AST_valid':helpers,'room_triangles':V['triangles'],'guests':len(D['guests']),'original_dependency_hashes_pass':True,'reports_local_links_pass':links,'max_room_bounds_delta_m':max(r['bounds_max_delta_m'] for r in V['meshes']),'remaining_limits':'REPORT.md E; native URP/nav/clip blend and lead visual acceptance unverified'}
(O/'independent-audit.json').write_text(json.dumps(receipt,indent=2))
sealed=[]
for root in [O,G]:
 for p in sorted(root.rglob('*')):
  if p.is_file() and '_before-final' not in p.parts and p.name!='delivery-receipt.json' and p.suffix not in ['.log','.blend1','.blend2']:
   sealed.append({'path':str(p.relative_to(O.parent)),'bytes':p.stat().st_size,'sha256':sha(p)})
(O/'delivery-receipt.json').write_text(json.dumps({'owner':'Codex 2 (WSL CLI)','task':'RESTAURANT-LOOK-DETAIL-3','files':sealed,'scope':['Stage1V3/**','Guests/**'],'no_native_acceptance_claim':True},indent=2));print('AUDIT PASS',len(reviews),'opened PNGs',len(sealed),'sealed files')

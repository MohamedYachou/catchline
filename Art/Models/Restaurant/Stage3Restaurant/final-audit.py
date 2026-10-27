"""Seal current exports, dependency hashes, coverage and actually opened proofs."""
from pathlib import Path
import json,hashlib,re,ast
O=Path(__file__).resolve().parent;P=O.parent;K=P/'KitchenKit2';R=O.parents[3]
def j(p):return json.loads(p.read_text())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seal(folder,files,extra):
 for f in folder.glob('*.py'):ast.parse(f.read_text())
 reviewed=j(folder/'visual-review.json')['opened']
 for f,digest in reviewed.items():assert h(folder/f)==digest,('review changed',f)
 out={'pass':True,'files_sha256':{f:h(folder/f) for f in files},'opened_visuals_sha256':reviewed,'native_unity_acceptance':False,**extra}
 (folder/'final-audit.json').write_text(json.dumps(out,indent=2));return out
kv=j(K/'validation.json');assert kv['pass'] and len(kv['assets'])==10
km=j(K/'manifest.json');assert len(km['assets'])==10
files=['RestaurantKitchenKit2.blend','manifest.json','validation.json','id-to-file.json','REPORT.md','lineup-camera.json','visual-review.json']
for a in km['assets']:
 name=a['name'];fp=K/(name+'.footprint.json');assert j(fp)==a;assert h(K/(name+'.fbx'))==a['fbx_sha256'];assert a['floor_contact_z_m']==0 and a['origin_blender_m']==[0,0,0]
 files.extend([name+'.fbx',name+'.footprint.json'])
ids=j(K/'id-to-file.json');text=(R/'Assets/Scripts/Game/Restaurant/RestaurantData.cs').read_text();block=text.split('public static readonly ItemDef[] Items = {')[1].split('};')[0];expected=set(re.findall(r'I\(ItemId\.(\w+)',block));assert {r['ItemId'] for r in ids}==expected and len(ids)==23
for row in ids:assert (R/row['file']).is_file(),row
for folder in [K,O]:
 for f in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:assert h(folder/'textures'/f)==h(P/'Stage1V4/textures'/f)
ko=seal(K,files,{'ItemIds_covered':23,'new_semantic_replacements':7,'S8_variants':3,'FBX_models':10,'V4_atlas_byte_identical':True})
v=j(O/'validation.json');m=j(O/'build-metrics.json');assert v['pass'] and v['FBX_sha256']==h(O/'Stage3Restaurant.fbx');assert v['triangles']==m['room_triangles'] and v['mesh_count']==len(m['production_meshes'])
assert m['source_V4_sha256']==h(P/'Stage1V4/Stage1V4.blend');assert m['source_Bistro_sha256']==h(P/'Stage2Bistro/Stage2Bistro.blend')
assert all(r['export_name']=='EXPORT_'+r['name'] for r in m['production_meshes'])
l=j(O/'layout.json');assert l['room_tiles']==[12,6] and len(l['dining_tables'])==6 and len(l['terrace_tables'])==5
assert sum(t['seats'] for t in l['dining_tables']+l['terrace_tables'])==38
for t in l['dining_tables']+l['terrace_tables']:assert len(t['seat_sockets'])==t['seats']
for actual,source in zip(j(O/'final-cameras.json'),j(P/'Stage1V4/final-cameras.json')):
 for key in ['rotation_blender_rad','lens_mm','resolution']:assert actual[key]==source[key],key
so=seal(O,['Stage3Restaurant.blend','Stage3Restaurant.fbx','layout.json','lighting.json','build-metrics.json','validation.json','final-cameras.json','REPORT.md','visual-review.json'],{'mesh_count':v['mesh_count'],'triangles':v['triangles'],'unchanged_dependencies':['Stage1V4.blend','Stage2Bistro.blend'],'V4_atlas_byte_identical':True,'room_tiles':[12,6],'table_seats':38,'bar_stools':3,'V4_lenses_orientation_resolutions_preserved':True})
print('FINAL AUDIT PASS',len(ko['files_sha256']),len(so['files_sha256']),'sealed files')

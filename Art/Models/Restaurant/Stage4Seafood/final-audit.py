"""Seal both deliveries after fresh FBX checks and human-agent visual opens."""
from pathlib import Path
import json,hashlib,ast,math
O=Path(__file__).resolve().parent;P=O.parent;X=P/'Exteriors'
def j(p):return json.loads(p.read_text())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seal(d,claims):
 for p in d.glob('*.py'):ast.parse(p.read_text())
 for f,digest in j(d/'visual-review.json')['opened'].items():assert h(d/f)==digest,('opened image changed',d/f)
 for f in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:assert h(d/'textures'/f)==h(P/'Stage1V4/textures'/f)
 assert not list(d.rglob('*.blend1')) and not list(d.rglob('*.bak'))
 files=[p for p in d.rglob('*') if p.is_file() and p.suffix in {'.fbx','.blend','.json','.md','.png','.jpg','.py'} and p.name!='final-audit.json']
 data={'pass':True,'files_sha256':{p.relative_to(d).as_posix():h(p) for p in sorted(files)},'claims':claims,'actually_opened_images':j(d/'visual-review.json')['opened'],'native_unity_acceptance':False}
 (d/'final-audit.json').write_text(json.dumps(data,indent=2));return len(files)
v=j(O/'validation.json');m=j(O/'build-metrics.json');l=j(O/'layout.json');assert v['pass'] and v['FBX_sha256']==h(O/'Stage4Seafood.fbx');assert v['triangles']==m['room_triangles']<220000 and v['mesh_count']==len(m['production_meshes'])==170
assert m['source_V4_sha256']==h(P/'Stage1V4/Stage1V4.blend') and m['source_Stage3_sha256']==h(P/'Stage3Restaurant/Stage3Restaurant.blend')
assert l['room_tiles']==[14,5] and l['kitchen_tiles']==[5,5];assert len(l['dining_tables'])==2 and len(l['booths'])==2 and len(l['terrace_tables'])==6
assert sum(r['seats'] for r in l['dining_tables']+l['booths']+l['terrace_tables'])==44;assert len(l['bar_counter']['stool_centres_blender_m'])==5
for row in l['dining_tables']+l['booths']+l['terrace_tables']:assert len(row['seat_sockets'])==row['seats']
for r in m['production_meshes']:
 assert r['export_name']=='EXPORT_'+r['name'];assert all(math.isfinite(x) for x in r['world_min_m']+r['world_max_m']);assert -5<r['world_min_m'][0] and r['world_max_m'][0]<11 and r['world_min_m'][1]>-8.5 and r['world_max_m'][1]<3 and -1.2<r['world_min_m'][2] and r['world_max_m'][2]<3.1,('unexpected oversized mesh',r['name'])
for a,b in zip(j(O/'final-cameras.json'),j(P/'Stage1V4/final-cameras.json')):
 for k in ['rotation_blender_rad','lens_mm','resolution']:assert a[k]==b[k],k
assert len(j(O/'visual-review.json')['opened'])==3
n=seal(O,{'fresh_FBX':True,'meshes':v['mesh_count'],'triangles':v['triangles'],'room_tiles':[14,5],'kitchen_tiles':[5,5],'table_seats':44,'bar_stools':5,'unchanged_sources':['Stage1V4.blend','Stage3Restaurant.blend'],'V4_atlas_byte_identical':True,'V4_orientation_lenses_resolutions_preserved':True,'no_oversized_or_presentation_mesh':True})
xm=j(X/'manifest.json');xv=j(X/'validation.json');assert xv['pass'] and len(xv['stages'])==len(xm['stages'])==4
for s,a in zip(xm['stages'],xv['stages']):
 assert a['pass'] and h(X/s['file'])==a['FBX_sha256'] and s['triangles']==a['triangles']<60000;f=j(X/s['footprint']);W=6+2*s['stage'];assert f['tiles']==[W,5] and f['facade_unity_direction']==[0,0,-1]
 for r in s['meshes']:
  assert r['min_m'][0]>-W/2-.55 and r['max_m'][0]<W/2+.55 and r['min_m'][1]>-2.8 and r['max_m'][1]<6.3 and r['min_m'][2]>-1.2 and r['max_m'][2]<5.6,('oversized exterior mesh',s['name'],r['name'])
for c in j(X/'harbour-cameras.json'):assert c['unity_rotation_euler']==[45,35,0] and c['resolution']==[1440,900] and c['unity_orthographic_size']==7.5
assert len(j(X/'visual-review.json')['opened'])==5
nx=seal(X,{'four_fresh_FBX':True,'stage_triangles':{s['name']:s['triangles'] for s in xm['stages']},'footprints_tiles':[[8,5],[10,5],[12,5],[14,5]],'shared_floor0_footprint_centre':True,'facade_Unity_negativeZ':True,'V4_atlas_byte_identical':True,'harbour_camera_pitch45_yaw35_common_ortho7_5':True,'presentation_context_excluded_from_FBX':True,'no_oversized_mesh':True})
print('FINAL DELIVERY AUDIT PASS',n,'Stage4 files;',nx,'Exterior files;8 actually-opened visual hashes')

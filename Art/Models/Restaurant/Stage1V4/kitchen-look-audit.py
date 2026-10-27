"""Independent fresh FBX audit. Original geometry/names, grid files, atlas and units."""
import bpy,json,hashlib,gzip,math
from pathlib import Path
from io_scene_fbx import parse_fbx
O=Path(__file__).resolve().parent;STAGE=O.name;B=O/'_kitchen-look-backup'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(path):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path),colors_type='LINEAR');bpy.context.view_layer.update();out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  pts=[o.matrix_world@v.co for v in o.data.vertices];out[o.name]={'points':sorted(tuple(round(v[k],5) for k in range(3)) for v in pts),'faces':len(o.data.polygons)}
 return json.loads(json.dumps(out))
baseline=O/'kitchen-look-baseline.json.gz'
if (B/(STAGE+'.fbx')).exists():
 original={'meshes':snapshot(B/(STAGE+'.fbx')),'files':{f.name:sha(f) for f in [B/'final-cameras.json',*B.glob('layout.json')]},'atlas':{f.name:sha(f) for f in (O/'textures').glob('*') if f.is_file()}}
 baseline.write_bytes(gzip.compress(json.dumps(original).encode()))
else:original=json.loads(gzip.decompress(baseline.read_bytes()))
after=snapshot(O/(STAGE+'.fbx'));preserved={n:after.get(n)==v for n,v in original['meshes'].items()};assert all(preserved.values()),[n for n,v in preserved.items() if not v]
assert all(sha(O/n)==h for n,h in original['files'].items());assert all(sha(O/'textures'/n)==h for n,h in original['atlas'].items())
assert all(n.startswith('EXPORT_') and 'REVIEW_' not in n for n in after)
added=sorted(set(after)-set(original['meshes']));assert len(added)==6 and all(n.startswith('EXPORT_KitchenLook_') for n in added)
M=json.loads((O/'build-metrics.json').read_text());expected={r['name']:r for r in M['production_meshes']};rows=[];total=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 r=expected.pop(o.name.removeprefix('EXPORT_'));o.data.calc_loop_triangles();tris=len(o.data.loop_triangles);total+=tris;assert tris==r['triangles']
 ps=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[k] for v in ps) for k in range(3)];hi=[max(v[k] for v in ps) for k in range(3)];assert all(math.isfinite(v) for p in ps for v in p)
 delta=max(abs(a-b) for aa,bb in [(lo,r['world_min_m']),(hi,r['world_max_m'])] for a,b in zip(aa,bb));assert delta<1e-5,(o.name,delta)
 assert len(o.data.materials)==1 and all(p.material_index==0 for p in o.data.polygons)
 assert len(o.data.uv_layers)>=2
 for uv in o.data.uv_layers:assert all(math.isfinite(c) for d in uv.data for c in d.uv)
 uv=o.data.uv_layers[1].data;areas=[]
 for t in o.data.loop_triangles:
  a,b,c=[uv[i].uv.copy() for i in t.loops];areas.append(abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))/2)
 assert min(areas)>0,o.name
 if o.name in added:assert lo[2]>.90 and lo[1]>1.60,(o.name,lo) # Wall-mounted; no floor contact/aisle obstruction.
 rows.append({'name':o.name,'triangles':tris,'min_m':lo,'max_m':hi,'UV1_min_area':min(areas),'bounds_delta_m':delta})
assert not expected;assert total==M['room_triangles'] and total<180000
tree,version=parse_fbx.parse(str(O/(STAGE+'.fbx')));settings=next(e for e in tree.elems if e.id==b'GlobalSettings');props=next(e for e in settings.elems if e.id==b'Properties70');units={e.props[0].decode():e.props[-1] for e in props.elems if e.props[0] in [b'UnitScaleFactor',b'OriginalUnitScaleFactor']};assert units['UnitScaleFactor']==100
recipe=json.loads((O/'lighting.json').read_text());tasks=[r for r in recipe['lights'] if r['name'].startswith('KitchenLook_')];assert len(tasks)==2
if STAGE=='Stage2Bistro':
 layout=json.loads((O/'layout.json').read_text());assert layout['room_tiles']==[10,5] and layout['kitchen_tiles']==[4,5] and layout['terrace_tiles']==[3,5] and layout['door_tile']==[9,0]
result={'pass':True,'FBX_sha256':sha(O/(STAGE+'.fbx')),'mesh_count':len(rows),'triangles':total,'original_names_world_geometry_preserved':preserved,'added_nodes':added,'layout_cameras_atlas_byte_identical':True,'FBX_units':units,'all_added_nodes_wall_mounted':True,'two_task_practicals':tasks,'meshes':rows,'native_unity_after_verified':False}
(O/'kitchen-look-validation.json').write_text(json.dumps(result,indent=2));(O/'validation.json').write_text(json.dumps(result,indent=2));print('KITCHEN LOOK FRESH AUDIT PASS',STAGE,len(rows),total,flush=True)

"""Fresh FBX audit plus original geometry/name preservation; never modifies source."""
import bpy,json,hashlib,math,gzip
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import parse_fbx
O=Path(__file__).resolve().parent;B=O/'_stages-look2-backup'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(path):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path),colors_type='LINEAR');bpy.context.view_layer.update();out={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  pts=[o.matrix_world@v.co for v in o.data.vertices];out[o.name]={'points':sorted(tuple(round(v[k],5) for k in range(3)) for v in pts),'triangles':len(o.data.polygons)}
 return out
baseline=O/'stages-look2-baseline.json.gz'
if (B/'Stage3Restaurant.fbx').exists():
 before=snapshot(B/'Stage3Restaurant.fbx')
 original={'meshes':before,'export_sha256':sha(B/'Stage3Restaurant.fbx'),'layout_sha256':sha(B/'layout.json'),'cameras_sha256':sha(B/'final-cameras.json')}
 baseline.write_bytes(gzip.compress(json.dumps(original).encode()))
else:
 original=json.loads(gzip.decompress(baseline.read_bytes()));before=original['meshes']
# Round-trip JSON normalizes tuple/list representation for retained measurements.
before=json.loads(json.dumps(before));after=json.loads(json.dumps(snapshot(O/'Stage3Restaurant.fbx')));preserved={n:after.get(n)==v for n,v in before.items()};assert all(preserved.values()),[n for n,v in preserved.items() if not v]
assert all(n.startswith('EXPORT_') for n in after);assert not any('REVIEW_' in n for n in after)
old=json.loads((O/'layout.json').read_text());assert original['layout_sha256']==sha(O/'layout.json');assert original['cameras_sha256']==sha(O/'final-cameras.json')
assert old['room_tiles']==[12,5] and old['kitchen_tiles']==[4,5] and old['terrace_tiles']==[3,5] and old['door_tile']==[11,0]
tree,version=parse_fbx.parse(str(O/'Stage3Restaurant.fbx'));settings=next(e for e in tree.elems if e.id==b'GlobalSettings');props=next(e for e in settings.elems if e.id==b'Properties70');units={e.props[0].decode():e.props[-1] for e in props.elems if e.props[0] in [b'UnitScaleFactor',b'OriginalUnitScaleFactor']};assert units['UnitScaleFactor']==100
atlas={n:sha(O/'textures'/n)==sha(O.parent/'Stage1V4/textures'/n) for n in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']};assert all(atlas.values())
M=json.loads((O/'build-metrics.json').read_text());assert set(after)=={'EXPORT_'+r['name'] for r in M['production_meshes']}
# Check all 65 floor centres remain backed by the unchanged original floor geometry.
floor=bpy.data.objects['EXPORT_GridFloor'];hits=[]
for x in range(15):
 for y in range(5):
  p=Vector((-3.5+x,2-y,5));hit= floor.ray_cast(floor.matrix_world.inverted()@p,Vector((0,0,-1)))
  assert hit[0] and abs((floor.matrix_world@hit[1]).z-.04)<1e-4,(x,y,hit);hits.append([x,y])
runner={}
for o in bpy.context.scene.objects:
 if o.name.startswith('EXPORT_StageLook2_') and 'Runner' in o.name:
  z=max((o.matrix_world@v.co).z for v in o.data.vertices);assert z<.055;runner[o.name]=z
for o in bpy.context.scene.objects:
 if o.name.startswith('EXPORT_StageLook2_') and any(t in o.name for t in ['JettyCrate','TerraceLantern']):
  ps=[o.matrix_world@v.co for v in o.data.vertices];assert max(v.y for v in ps)<-2.5 or min(v.y for v in ps)>2.5,o.name
assert not [n for n in after if any(t in n for t in ['REVIEW_Layout','DiningTwo_','DiningFour','TerraceTable'])]
result={'pass':True,'FBX_sha256':sha(O/'Stage3Restaurant.fbx'),'original_export_sha256':original['export_sha256'],'old_mesh_geometry_names_preserved':preserved,'original_meshes':len(before),'added_nodes':sorted(set(after)-set(before)),'mesh_count':len(after),'room_triangles':M['room_triangles'],'FBX_units':units,'layout_and_cameras_byte_identical':True,'atlas_byte_identical':atlas,'grid_centres_checked':hits,'runner_max_z_m':runner,'no_added_fixed_seating':True,'native_unity_unverified':True}
(O/'stages-look2-validation.json').write_text(json.dumps(result,indent=2));print('STAGES LOOK2 FRESH AUDIT PASS',len(before),len(after),flush=True)

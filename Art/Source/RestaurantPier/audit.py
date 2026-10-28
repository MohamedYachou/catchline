"""Independent exported-FBX audit. Does not load Unity or modify room assets."""
import bpy,json,math,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2];P=R/'Assets/Resources/Restaurant'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(P/'RestaurantPier.fbx'),use_anim=False)
expected=json.loads((O/'phase3-metrics.json').read_text());rows=[];errors=[]
objects=bpy.context.scene.objects
for name in ['RestaurantPier','Pier_S1','Pier_S2','Pier_S3','Pier_S4','Quay','Boats','Clutter']:
 if name not in objects:errors.append('Missing '+name)
for ob in objects:
 if ob.type!='MESH':continue
 me=ob.data;me.calc_loop_triangles();points=[ob.matrix_world@v.co for v in me.vertices]
 lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
 row=dict(name=ob.name,group=ob.parent.name,triangles=len(me.loop_triangles),bounds_blender=[lo,hi],materials=[m.name for m in me.materials],uv_layers=len(me.uv_layers),colors=[a.name for a in me.color_attributes]);rows.append(row)
 original=next((r for r in expected['objects'] if r['name']==ob.name),None)
 if not original:errors.append('Unexpected mesh '+ob.name);continue
 if row['triangles']!=original['triangles']:errors.append('Triangle mismatch '+ob.name)
 if max(abs(a-b) for aa,bb in zip(row['bounds_blender'],original['bounds_blender']) for a,b in zip(aa,bb))>.0001:errors.append('Bounds mismatch '+ob.name)
 if row['materials']!=['Restaurant_Atlas_URP_V4']:errors.append('Material '+ob.name)
 if not me.uv_layers or any(not math.isfinite(n) or n<0 or n>1 for v in me.uv_layers.active.data for n in v.uv):errors.append('UV '+ob.name)
 if 'Color' not in row['colors']:errors.append('Vertex colors '+ob.name)
 if any(not math.isfinite(n) for p in points for n in p):errors.append('Nonfinite '+ob.name)
 if ob.parent.name.startswith('Pier_S'):
  stage=int(ob.parent.name[-1]);end=[4.85,9,11,13][stage-1]
  interior=[p for p in points if -4<=p.x<=end and -2.5<=p.y<=2.5]
  if interior and max(p.z for p in interior)>.0001:errors.append('Pier enters room '+ob.name)
  if not (lo[2]<-.57<hi[2]):errors.append('Pilings miss sea '+ob.name)
 if ob.name.startswith('Boat_') and not ob.name.endswith('Mooring') and not(lo[2]<-.57<hi[2]):errors.append('Boat floats above sea '+ob.name)
total=sum(r['triangles'] for r in rows)
if total>25000:errors.append('Budget '+str(total))
source=json.loads((O/'room-inspection.json').read_text());hashes={}
for name,data in source.items():
 h=hashlib.sha256((P/(name+'.fbx')).read_bytes()).hexdigest();hashes[name]=dict(sha256=h,unchanged=h==data['sha256'])
 if not hashes[name]['unchanged']:errors.append('ROOM CHANGED '+name)
result=dict(passed=not errors,errors=errors,total_triangles=total,objects=rows,rooms=hashes,fbx_sha256=hashlib.sha256((P/'RestaurantPier.fbx').read_bytes()).hexdigest())
(O/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('PIER AUDIT',result['passed'],'TRIS',total,'ERRORS',errors,flush=True)
assert not errors,errors

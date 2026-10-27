"""Independent actual-FBX top-face roof-occlusion and unchanged-node audit."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
S=Path(__file__).resolve().parent;R=S.parents[3];O=R/'Art/Models/BoatsV2/Tier6V1'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/'Tier6V1.fbx'));bpy.context.view_layer.update()
obs={o.name:o for o in bpy.context.scene.objects}
roofnames=['WheelhouseRoof','RoofTimberLip'];verts=[];polys=[]
for name in roofnames:
 o=obs[name];offset=len(verts);verts += [o.matrix_world@v.co for v in o.data.vertices];polys += [tuple(offset+i for i in p.vertices) for p in o.data.polygons]
roof=BVHTree.FromPolygons(verts,polys)
direction=Vector((-math.cos(math.radians(35))*math.cos(math.radians(45)),-math.sin(math.radians(35))*math.cos(math.radians(45)),math.sin(math.radians(45)))).normalized()
def descendants(n):
 o=obs[n];return [o]+list(o.children_recursive)
def surface_tree(objects):
 v=[];p=[]
 for o in objects:
  if o.type!='MESH':continue
  off=len(v);v += [o.matrix_world@a.co for a in o.data.vertices];p += [tuple(off+i for i in f.vertices) for f in o.data.polygons]
 return BVHTree.FromPolygons(v,p)
stations=['PrepStation','PreparedHold','RawIceCoolers','RawBuckets','DeepLineRig_1','DeepLineRig_2','NetModule1','NetModule2','BuoyRig_1','BuoyRig_2','SortingTray','FishHold','HoldLid','TwoShortLampMasts','LampCable']
stations += ['RodHolder_%d'%i for i in range(1,5)]+['JigReel_%02d'%i for i in range(1,4)]+['SquidLamp_%02d'%i for i in range(1,9)]
rows=[]
for name in stations:
 objects=[o for o in descendants(name) if o.type=='MESH'];tree=surface_tree(objects);samples=[]
 for o in objects:
  mat=o.matrix_world;normalmat=mat.to_3x3().inverted().transposed()
  for f in o.data.polygons:
   n=(normalmat@f.normal).normalized()
   if n.z<.45:continue
   # Every upward face centroid plus inset vertices: sample only top faces exposed to sky.
   centre=mat@f.center
   points=[centre]+[centre*.2+(mat@o.data.vertices[i].co)*.8 for i in f.vertices]
   for p in points:
    start=p+Vector((0,0,.0001))
    if tree.ray_cast(start,Vector((0,0,1)),20)[0] is not None:continue
    hit=roof.ray_cast(p+direction*.0001,direction,30)
    samples.append({'mesh':o.name,'face':f.index,'xyz':list(p),'roof_blocked':hit[0] is not None})
 assert samples,('NO UPWARD TOP SAMPLES',name)
 blocked=[p for p in samples if p['roof_blocked']]
 rows.append({'station':name,'upward_exposed_top_samples':len(samples),'roof_occluded_samples':len(blocked),'blocked':blocked,'pass':not blocked})
# All ten fixed crew-point transforms and all pre-existing station nodes must stay exact.
old=json.loads((S/'roof-backup/Tier6V1/build-metrics.json').read_text())['objects'];changed=[]
expected_changes=('WheelhouseRoof','RoofTimberLip','ShelterRoofAftPosts')
for name,d in old.items():
 o=obs[name]
 if name in expected_changes:continue
 err=max(abs(o.matrix_world[i][j]-d['world'][i][j]) for i in range(4) for j in range(4))
 assert err<1e-5,(name,err)
 if name.startswith('CrewStand_'):changed.append({'node':name,'max_world_matrix_delta':err})
rooflo=[min(v[i] for v in verts) for i in range(3)];roofhi=[max(v[i] for v in verts) for i in range(3)]
# Body extents exact from actual FBX, not intended box dimensions.
body=[obs['WheelhouseBody'].matrix_world@v.co for v in obs['WheelhouseBody'].data.vertices]
bodylo=[min(v[i] for v in body) for i in range(3)];bodyhi=[max(v[i] for v in body) for i in range(3)]
overhang=max(bodylo[i]-rooflo[i] for i in range(2));overhang=max(overhang,max(roofhi[i]-bodyhi[i] for i in range(2)));assert overhang<=.4
record={'pass':all(r['pass'] for r in rows),'method':'Actual FBX: every sky-exposed upward polygon centroid and inset vertices of every named station, BVH rays parallel to exact orthographic game45 camera; roofs tested separately from other occluders. No claim of zero self/equipment occlusion.','camera_direction':list(direction),'roof_meshes':roofnames,'roof_min':rooflo,'roof_max':roofhi,'cabin_min':bodylo,'cabin_max':bodyhi,'max_roof_overhang_m':overhang,'other_canopies':0,'stations':rows,'unchanged_preexisting_transforms':True,'crew_points':changed,'fbx_sha256':hashlib.sha256((O/'Tier6V1.fbx').read_bytes()).hexdigest()}
(O/'roof-visibility.json').write_text(json.dumps(record,indent=2)+'\n')
v=json.loads((O/'validation.json').read_text());v['station_roof_visibility_game_exact_45']=record;(O/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print('ROOF VISIBILITY',record['pass'],len(rows),'stations',sum(r['upward_exposed_top_samples'] for r in rows),'top samples',sum(r['roof_occluded_samples'] for r in rows),'blocked',flush=True)
assert record['pass'],[(r['station'],r['roof_occluded_samples']) for r in rows if not r['pass']]

import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent;O=R/'Art/Models/Maps/GullKelpForest';B=R.parent/'Catchline-sim/Backups/codex2-sand-edges-before'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def snap(path,fbx=False):
 if fbx:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path))
 else:bpy.ops.wm.open_mainfile(filepath=str(path))
 bpy.context.view_layer.update();rows={}
 for o in bpy.context.scene.objects:
  r={'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(v) for v in o.matrix_world]}
  if o.type=='MESH':
   o.data.calc_loop_triangles();r.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],triangles=[list(p.vertices) for p in o.data.loop_triangles],material_indices=[p.material_index for p in o.data.polygons],materials=[m.name for m in o.data.materials],bounds=[[min((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)],[max((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)]])
  rows[o.name]=r
 return rows,bpy.context.scene.unit_settings.scale_length
old,unit0=snap(B/'GullKelpForestSeaV2.blend');new,unit1=snap(O/'GullKelpForestSeaV2.blend');assert set(old)==set(new);assert unit0==unit1==1
checks={};bed='ConnectedBathymetry'
for n,r in old.items():
 if n!=bed:assert r==new[n],n
 else:
  for k in ['type','parent','matrix','bounds']:assert r[k]==new[n][k],(n,k)
checks['other_source_objects_exact']=len(old)-1;checks['names_hierarchy_units_bounds_preserved']=True
# Both direction surface samples: original and new vertices and triangle centres.
def surface(a,b):
 tree=BVHTree.FromPolygons([Vector(v) for v in b['vertices']],b['triangles'],all_triangles=True)
 vkeys={tuple(v) for v in b['vertices']}
 def tkey(r,t):return tuple(sorted(tuple(r['vertices'][i]) for i in t))
 tkeys={tkey(b,t) for t in b['triangles']}
 pts=[Vector(v) for v in a['vertices'] if tuple(v) not in vkeys]+[sum((Vector(a['vertices'][i]) for i in t),Vector())/3 for t in a['triangles'] if tkey(a,t) not in tkeys]
 # Identical vertices/triangles prove their own parity; BVH only the recut patch.
 worst=max(pts,key=lambda v:tree.find_nearest(v)[3]);print('WORST RECUT',list(worst),tree.find_nearest(worst),flush=True)
 return tree.find_nearest(worst)[3],len(pts)
checks['new_to_old_surface_max_m'],checks['new_surface_samples']=surface(new[bed],old[bed]);checks['old_to_new_surface_max_m'],checks['old_surface_samples']=surface(old[bed],new[bed]);print('SURFACE',checks,flush=True);assert max(checks['new_to_old_surface_max_m'],checks['old_to_new_surface_max_m'])<.0001
nav=sha(O/'navigation.json');assert nav==sha(B/'navigation.json')
a,u0=snap(B/'GullKelpForestSeaV2.fbx',True);b,u1=snap(O/'GullKelpForestSeaV2.fbx',True);assert set(a)==set(b);assert u0==u1
for n,r in a.items():
 if n!=bed:assert r==b[n],('FBX changed',n)
 else:
  for k in ['type','parent','matrix','bounds']:assert r[k]==b[n][k],('FBX',n,k)
checks['unchanged_fbx_objects_exact']=len(a)-1;checks['actual_fbx_units_match_accepted']=u1
bounds=[{'name':n,'before':a[n]['bounds'],'after':r['bounds'],'triangles_before':len(a[n]['triangles']),'triangles_after':len(r['triangles'])} for n,r in b.items() if r['type']=='MESH']
checks['source_to_fbx_vertex_max_m']=0
for n,r in new.items():
 if r['type']!='MESH':continue
 kd=KDTree(len(b[n]['vertices']));o=bpy.data.objects[n]
 for i,v in enumerate(o.data.vertices):p=o.matrix_world@v.co;kd.insert(Vector((-p.x,p.y,p.z)),i)
 kd.balance()
 err=max(kd.find(Vector(v))[2] for v in r['vertices']);checks['source_to_fbx_vertex_max_m']=max(err,checks['source_to_fbx_vertex_max_m'])
assert checks['source_to_fbx_vertex_max_m']<.0001
count=sum(len(r['triangles']) for r in b.values() if r['type']=='MESH');assert count<=75000
plan=json.loads((S/'sand-edges-plan.json').read_text())
result={'all_passed':True,'checks':checks,'mesh_count':len(bounds),'triangles':count,'triangles_before':sum(len(r['triangles']) for r in a.values() if r['type']=='MESH'),'bounds_table':bounds,'anchors_empties':[{'name':n,'matrix':r['matrix'],'exact_match':True} for n,r in b.items() if r['type']=='EMPTY'],'patches':plan['patches'],'footprint_measure':'Bounding extents and centroid shift <=0.5m. Individual staircase-notch boundary displacement separately reported, not constrained to0.5m.','navigation_sha256_unchanged':nav,'sha256':{e:sha(O/('GullKelpForestSeaV2.'+e)) for e in ('blend','fbx')}}
(O/'SeaV2-sand-edges-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('SAND EDGES INDEPENDENT AUDIT PASS',count,checks,flush=True)

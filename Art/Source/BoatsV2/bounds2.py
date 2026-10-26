"""Independent all-mesh original/exported world and mesh-local bounds; no mutations."""
import bpy,json,sys,hashlib
from pathlib import Path
from io_scene_fbx import parse_fbx
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[3]
def raw(p):
 root,_=parse_fbx.parse(str(p))
 child=lambda e,n:next(c for c in e.elems if c.id==n)
 props=lambda e:[[p.decode(errors='replace') if isinstance(p,bytes) else p for p in c.props] for c in e.elems]
 settings=props(child(child(root,b'GlobalSettings'),b'Properties70'))
 models={}
 for e in child(root,b'Objects').elems:
  if e.id==b'Model':
   name=e.props[1].decode().split('\x00')[0];models[name]=props(child(e,b'Properties70'))
 return {'unit_scale_factor':next(p[-1] for p in settings if p[0]=='UnitScaleFactor'),'models':models}
def scan(p):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(p));bpy.context.view_layer.update();rows={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  local=[v.co for v in o.data.vertices];world=[o.matrix_world@v for v in local]
  bounds=lambda vs:[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]]
  rows[o.name]={'world_bounds':bounds(world),'mesh_local_bounds':bounds(local),'local_scale':list(o.scale),'world_matrix':[list(r) for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'materials':[m.name for m in o.data.materials]}
 return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'raw_fbx':raw(p),'meshes':rows}
for name in sys.argv[sys.argv.index('--')+1:]:
 out=R/'Art/Models/BoatsV2'/name;old=scan(R/f'Assets/Art/Models/Boats/{name}.fbx');new=scan(out/(name+'.fbx'));rows=[]
 for n,d in new['meshes'].items():
  bounds=d['world_bounds'];span=max(bounds[1][i]-bounds[0][i] for i in range(3));rows.append({'name':n,'original':old['meshes'].get(n),'exported':d,'world_span_max_m':span})
 record={'original_sha256':old['sha256'],'exported_sha256':new['sha256'],'rows':rows,'world_bounds_within_30m':all(r['world_span_max_m']<30 for r in rows),'review_meshes': [r['name'] for r in rows if 'REVIEW' in r['name'].upper()]}
 record['original_raw_fbx']=old['raw_fbx'];record['exported_raw_fbx']=new['raw_fbx']
 record['unit_convention_preserved']=old['raw_fbx']['unit_scale_factor']==new['raw_fbx']['unit_scale_factor']
 assert record['unit_convention_preserved'], 'FBX unit convention differs from original'
 prior=R/'Art/Source/BoatsV2/_before-unit-fix2'/name/(name+'.fbx')
 if prior.exists():
  previous=scan(prior);current=scan(out/(name+'.fbx'));maxerr=0
  def vertices(path):
   bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path));bpy.context.view_layer.update()
   return {o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in bpy.context.scene.objects if o.type=='MESH'}
  a=vertices(prior);b=vertices(out/(name+'.fbx'));assert set(a)==set(b)
  for n in a:
   assert len(a[n])==len(b[n]);tree=KDTree(len(a[n]))
   for i,v in enumerate(a[n]):tree.insert(v,i)
   tree.balance();maxerr=max(maxerr,max(tree.find(v)[2] for v in b[n]))
  assert maxerr<.0001
  record['prior_rejected_export_sha256']=previous['sha256'];record['prior_unit_scale_factor']=previous['raw_fbx']['unit_scale_factor'];record['max_world_vertex_delta_from_prior_rendered_export_m']=maxerr;record['existing_renders_geometry_equivalent']=True
 (out/'bounds-audit.json').write_text(json.dumps(record,indent=2))
 for r in rows:print(name,r['name'],'world',r['exported']['world_bounds'],'local',r['exported']['mesh_local_bounds'],'scale',r['exported']['local_scale'])
 print('BOUNDS',name,record['world_bounds_within_30m'],record['review_meshes'],flush=True)

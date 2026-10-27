"""Independent fresh-GLB audit, including subset position/UV triangle equivalence."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];sys.path.insert(0,str(O))
from inspect_pack import reset,load,bounds,source
def triangles(obs,predicate=lambda ob,poly:True):
 rows=[]
 for ob in obs:
  if ob.type!='MESH':continue
  mesh=ob.data;mesh.calc_loop_triangles();uv=mesh.uv_layers.active
  for tri in mesh.loop_triangles:
   poly=mesh.polygons[tri.polygon_index]
   if not predicate(ob,poly):continue
   corners=[]
   for vi,li in zip(tri.vertices,tri.loops):
    pos=ob.matrix_world@mesh.vertices[vi].co
    corners.append(tuple(round(float(x),5) for x in (*pos,*(uv.data[li].uv if uv else (0,0)))))
   rows.append(tuple(sorted(corners)))
 return sorted(rows)
checks=[]
for name,base,predicate in [('salmon-fillet','sushi-salmon',lambda o,p:all(i>=48 for i in p.vertices)),('fries-loose','fries',lambda o,p:o.name=='fries.001')]:
 reset();a=triangles(load(source('food',base)),predicate)
 reset();b=triangles(load(O/'derived'/(name+'.glb')))
 assert a==b,(name,len(a),len(b))
 checks.append(dict(name=name,triangles=len(b),source_triangle_positions_uv_identical=True))
dm=json.loads((O/'dish-map.json').read_text());de=json.loads((O/'decor-map.json').read_text())
assert len(dm['dishes'])==13 and len({r['dish'] for r in dm['dishes']})==13
models=[]
for rec in dm['dishes']+de['decor']:
 name=rec.get('dish',rec.get('model'));p=O/rec.get('composite_glb',rec.get('variant_glb',''))
 reset();obs=load(p);lo,hi=bounds(obs);size=hi-lo
 assert all(math.isfinite(v) and v>0 for v in size),(name,list(size))
 assert abs(lo.z)<.0001,(name,'bad bottom pivot',list(lo))
 meshes=[o for o in obs if o.type=='MESH'];assert meshes
 missing=[]
 for ob in meshes:
  for m in ob.data.materials:
   if m and m.use_nodes:
    for n in m.node_tree.nodes:
     if n.type=='TEX_IMAGE':
      if not n.image or min(n.image.size)<1:missing.append(m.name)
 assert not missing,(name,missing)
 if 'components' in rec:
  # Match the exported meal's union to recipe component bounds.
  expected_min=[min(c['verified_bounds_blender_m']['min'][i] for c in rec['components']) for i in range(3)]
  expected_max=[max(c['verified_bounds_blender_m']['max'][i] for c in rec['components']) for i in range(3)]
  error=max(abs(lo[i]-expected_min[i]) for i in range(3))+max(abs(hi[i]-expected_max[i]) for i in range(3))
  assert error<.0001,(name,error)
 else:
  error=max(abs(size[i]-rec['display_size_m'][i]) for i in range(3));assert error<.0001,(name,error)
 models.append(dict(name=name,path=str(p.relative_to(O)),bounds_min=list(lo),bounds_max=list(hi),meshes=len(meshes),triangles=sum(len(o.data.polygons) for o in meshes),uv_layers=[len(o.data.uv_layers) for o in meshes],max_bounds_error_m=error,missing_images=missing))
(O/'mesh-audit.json').write_text(json.dumps(dict(status='PASS',subset_equivalence=checks,models=models),indent=2))
print('MESH_AUDIT_PASS',len(models),'composites/decor',checks)

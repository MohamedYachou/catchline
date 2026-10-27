import bpy,json,sys,hashlib,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[4]
sys.path.insert(0,str(R/'Art/Source/Restaurant/kenney'))
from inspect_pack import load,reset,bounds
rows=[]
manifest=json.loads((O/'manifest.json').read_text())
for rec in manifest['items']:
 reset();p=O/(rec['name']+'.fbx');obs=load(p);meshes=[o for o in obs if o.type=='MESH'];lo,hi=bounds(meshes)
 expected=rec['bounds_blender'];error=max(abs([lo,hi][j][i]-expected[j][i]) for j in range(2) for i in range(3))
 images=[n.image for o in meshes for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
 rotations=[list(o.rotation_euler) for o in meshes if o.parent is None]
 scales=[list(o.scale) for o in meshes if o.parent is None]
 checks=dict(single_mesh=len(meshes)==1,floor_pivot=abs(lo.z)<1e-5,bounds_roundtrip=error<1e-4,finite=all(math.isfinite(v) for a in [lo,hi] for v in a),uvs=all(o.data.uv_layers.active is not None for o in meshes),images_valid=all(i.size[0]>0 and i.size[1]>0 for i in images),blender_axis_restore=all(abs(x[0]-math.pi/2)<1e-5 and max(abs(x[1]),abs(x[2]))<1e-5 for x in rotations),identity_scale=all(max(abs(v-1) for v in x)<1e-5 for x in scales),hash_matches=hashlib.sha256(p.read_bytes()).hexdigest()==rec['fbx_sha256'])
 row=dict(name=rec['name'],checks=checks,root_rotation_blender=rotations,root_scale=scales,max_bounds_error=error,bounds_blender=[list(lo),list(hi)],triangles=sum(len(f.vertices)-2 for ob in meshes for f in ob.data.polygons),images=[dict(name=i.name,size=list(i.size),packed=bool(i.packed_file)) for i in set(images)])
 rows.append(row)
(O/'mesh-audit.json').write_text(json.dumps(dict(pass_all=all(all(r['checks'].values()) for r in rows),models=len(rows),items=rows),indent=2))
print('FRESH_FBX',len(rows),'PASS',all(all(r['checks'].values()) for r in rows))
for r in rows:
 if not all(r['checks'].values()):print(r['name'],r['checks'],r['root_rotation_blender'],r['root_scale'])

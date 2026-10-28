"""Read-only delivery-blend verification; no Unity or runtime context."""
import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2]
rows=json.loads((O/'props4-manifest.json').read_text());results=[]
assert len(rows)==10
for rec in rows:
 path=R/rec['source'];bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False)
 obs=list(bpy.context.scene.objects);expected=13 if rec['name']=='Restaurant_PaperLanterns' else 1
 assert len(obs)==expected and all(o.type=='MESH' for o in obs)
 roots=[o for o in obs if not o.parent];assert len(roots)==1 and roots[0].name==rec['name']
 assert roots[0].get('service_props_task')=='SERVICE-PROPS-4'
 count=0
 for o in obs:
  assert o.matrix_basis.is_identity,(rec['name'],o.name)
  o.data.calc_loop_triangles();count+=len(o.data.loop_triangles)
  assert len(o.data.materials)==1 and o.data.materials[0].name=='RestaurantAtlas'
  assert len(o.data.uv_layers)==1 and o.data.color_attributes.get('Color')
 mat=roots[0].data.materials[0];images=[n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE']
 assert len(images)==2 and all(i.packed_file for i in images)
 assert count==rec['tris']
 if expected==13:
  glows=[o for o in obs if o.name.split('.')[0]=='Glow'];assert len(glows)==6
  assert all(o.parent and o.parent.name.startswith('Lantern_') for o in glows)
 results.append(dict(name=rec['name'],source=rec['source'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),tris=count,mesh_objects=expected,packed_atlas_images=2,identity_authoring_transforms=True,production_meshes_only=True))
 print('SOURCE_PASS',rec['name'],count,flush=True)
(O/'props4-source-audit.json').write_text(json.dumps(dict(status='PASS',items=results),indent=2)+'\n')
print('SOURCE_ALL_PASS',len(results))

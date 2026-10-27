"""Fresh-FBX audit. Presentation assets must never enter the exported inventories."""
import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;manifest=json.loads((O/'manifest.json').read_text());cells=json.loads((O/'textures/atlas.json').read_text())['cells'];rows=[]
for row in manifest['assets']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/(row['name']+'.fbx')));obs=list(bpy.context.scene.objects);assert {o.name for o in obs}==set(row['export_meshes']);assert all(o.type=='MESH' for o in obs)
 pts=[o.matrix_world@v.co for o in obs for v in o.data.vertices];lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)];delta=max(abs(a-b) for p,q in zip([lo,hi],row['bounds_blender_m']) for a,b in zip(p,q));assert delta<1e-5;assert abs(lo[2])<1e-5;assert hi[0]-lo[0]<=row['tiles_w']+1e-5 and hi[1]-lo[1]<=row['tiles_d']+1e-5
 used=set();tri=0
 for ob in obs:
  assert ob.location.length<1e-5 and max(abs(v-1) for v in ob.scale)<1e-5;assert len(ob.data.materials)==1 and len(ob.data.uv_layers)==1
  ob.data.calc_loop_triangles();tri+=len(ob.data.loop_triangles)
  for poly in ob.data.polygons:
   uvs=[ob.data.uv_layers[0].data[i].uv for i in poly.loop_indices];valid=[]
   for c in cells:
    x,y,w,h=c['pixel_cell'];u0,u1=(x+16)/2048,(x+w-16)/2048;v0,v1=1-(y+h-16)/2048,1-(y+16)/2048
    if all(u0-1e-6<=uv.x<=u1+1e-6 and v0-1e-6<=uv.y<=v1+1e-6 for uv in uvs):valid.append(c['name'])
   assert len(valid)==1,(row['name'],poly.index,valid);used.add(valid[0])
  images=[n.image for n in ob.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image];assert images and all(i.has_data and min(i.size)>0 for i in images)
 assert used==set(row['atlas_cells']);assert tri==row['triangles'];sha=hashlib.sha256((O/(row['name']+'.fbx')).read_bytes()).hexdigest();assert sha==row['fbx_sha256']
 rows.append({'name':row['name'],'pass':True,'bounds_blender_m':[lo,hi],'bounds_delta_m':delta,'meshes':[o.name for o in obs],'triangles':tri,'fbx_sha256':sha,'floor_contact_and_footprint':True,'identity_origin_scale':True,'UV_faces_in_single_inset_cell':True,'atlas_cells':sorted(used),'embedded_base_image_loaded':True})
for name,sha in manifest['atlas_hashes'].items():assert hashlib.sha256((O/'textures'/name).read_bytes()).hexdigest()==sha==hashlib.sha256((O.parent/'Stage1V4/textures'/name).read_bytes()).hexdigest()
(O/'validation.json').write_text(json.dumps({'pass':True,'assets':rows,'atlas_byte_identical_to_V4':True,'native_unity_unverified':True},indent=2));print('UPGRADES IMPORT AUDIT PASS',len(rows),flush=True)

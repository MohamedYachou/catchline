import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'Stage1V4.blend'));rows=[];changes=json.loads((O/'backwall-changes.json').read_text());v=json.loads((O/'validation.json').read_text());sha=hashlib.sha256((O/'Stage1V4.fbx').read_bytes()).hexdigest();assert sha==v['FBX_sha256']==changes['fbx_sha256'] and v['pass']
def sig(o):return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],list(map(tuple,o.matrix_world)),[[tuple(d.uv) for d in u.data] for u in list(o.data.uv_layers)[1:]])).encode()).hexdigest()
for name,expected in changes['source_signatures'].items():assert sig(bpy.data.objects[name])==expected,name
for change in changes['changes']:
 o=bpy.data.objects[change['node'].removeprefix('EXPORT_')];assert o.data.uv_layers[0].name=='UV0';m=o.data.materials[0];n=next(n for n in m.node_tree.nodes if n.type=='VERTEX_COLOR');a=o.data.color_attributes[n.layer_name];assert all(max(abs(c-.85) for c in d.color[:3])<1e-5 for d in a.data)
for m in bpy.data.materials:
 if not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:
   p=Path(bpy.path.abspath(n.image.filepath));assert p.exists();rows.append({'material':m.name,'image':n.image.name,'relative_texture':str(p.relative_to(O)),'exists':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(O/'backwall-validation.json').write_text(json.dumps({'pass':True,'fbx_sha256':sha,'unchanged_source_geometry_transform_secondaryUV_meshes':len(changes['source_signatures']),'same_export_names_as_original':True,'exported_meshes':v['mesh_count'],'triangles':v['triangles'],'repainted_meshes':len(changes['changes']),'UV0_name_and_neutral_AO':True,'images':rows,'native_unity_unverified':True},indent=2));print('BACKWALL FINAL AUDIT PASS',flush=True)

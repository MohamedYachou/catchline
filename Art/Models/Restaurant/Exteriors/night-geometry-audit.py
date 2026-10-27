import bpy,json,hashlib,gzip
from pathlib import Path
O=Path(__file__).resolve().parent;M=json.loads((O/'manifest.json').read_text());rows=[]
def meshes(p):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(p),colors_type='LINEAR');bpy.context.view_layer.update();out={}
 for o in bpy.context.scene.objects:
  assert o.type=='MESH';me=o.data;out[o.name]={'v':[[round(x,6) for x in v.co] for v in me.vertices],'f':[list(p.vertices) for p in me.polygons],'uv':[[[round(x,7) for x in l.uv] for l in uv.data] for uv in me.uv_layers],'matrix':[[round(x,6) for x in row] for row in o.matrix_world],'colors':[[[round(x,6) for x in d.color] for d in attr.data] for attr in me.color_attributes]}
 return out
for item in M['stages']:
 baseline=O/'_night-backup'/item['file'];snapshot=O/(Path(item['file']).stem+'-day-geometry.json.gz')
 if baseline.exists():
  a=meshes(baseline);snapshot.write_bytes(gzip.compress(json.dumps(a,separators=(',',':')).encode()))
 else:a=json.loads(gzip.decompress(snapshot.read_bytes()))
 b=meshes(O/item['file']);assert a==b,item['file'];rows.append({'name':item['name'],'unchanged_meshes':sorted(a),'unchanged_vertices_faces_UVs_colors_transforms':True,'fbx_sha256':hashlib.sha256((O/item['file']).read_bytes()).hexdigest()})
(O/'night-geometry-audit.json').write_text(json.dumps({'pass':True,'stages':rows},indent=2));print('NIGHT GEOMETRY PRESERVATION PASS')

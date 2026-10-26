import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3]; O=R/'Art/Models/BoatsV2'; rows={}
for name in ['Rowboat','Skiff']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 p=R/f'Assets/Art/Models/Boats/{name}.fbx'; bpy.ops.import_scene.fbx(filepath=str(p)); bpy.context.view_layer.update()
 rows[name]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':[]}
 for o in bpy.context.scene.objects:
  d={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world],'local':[list(r) for r in o.matrix_local]}
  if o.type=='MESH':
   ps=[o.matrix_world@v.co for v in o.data.vertices];d.update(tris=sum(len(p.vertices)-2 for p in o.data.polygons),bounds=[[min(v[i] for v in ps) for i in range(3)],[max(v[i] for v in ps) for i in range(3)]],materials=[m.name for m in o.data.materials])
  rows[name]['objects'].append(d)
(O/'baseline.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=1))

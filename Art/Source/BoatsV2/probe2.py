import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];rows={}
for name in ['DayBoat','CompactFisherV1','PrepFisherV1','Tier5FisherV1']:
 bpy.ops.wm.read_factory_settings(use_empty=True);p=R/f'Assets/Art/Models/Boats/{name}.fbx';bpy.ops.import_scene.fbx(filepath=str(p));bpy.context.view_layer.update();d={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'objects':[]}
 for o in bpy.context.scene.objects:
  q={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world],'local':[list(r) for r in o.matrix_local]}
  if o.type=='MESH':
   vs=[o.matrix_world@v.co for v in o.data.vertices];q.update(triangles=sum(len(p.vertices)-2 for p in o.data.polygons),bounds=[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],materials=[m.name for m in o.data.materials]);q['vertices']=[list(v) for v in vs] if o.name in ['Hull','IvoryGunwale'] else []
  d['objects'].append(q)
 rows[name]=d
(R/'Art/Source/BoatsV2/baseline2.json').write_text(json.dumps(rows,indent=2))
for n,d in rows.items():
 print(n,sum(q.get('triangles',0) for q in d['objects']))
 for q in d['objects']:print(q['name'],q.get('triangles'),q.get('bounds'))

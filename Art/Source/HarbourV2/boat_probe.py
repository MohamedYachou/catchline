"""Read-only released-hull material/geometry probe for paint-only variants."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/GullHarbour/HarbourV2'
rows={}
for name in ['CompactFisherV1','PrepFisherV1','Tier5DeepLines103','Skiff']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 src=R/'Assets/Art/Models/Boats'/(name+'.fbx');before=hashlib.sha256(src.read_bytes()).hexdigest()
 bpy.ops.import_scene.fbx(filepath=str(src));bpy.context.view_layer.update()
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 rows[name]={'source':str(src.relative_to(R)),'sha256':before,'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'roots':[{'name':o.name,'type':o.type,'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale)} for o in bpy.context.scene.objects if o.parent is None],'parts':[]}
 for o in meshes:
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  rows[name]['parts'].append({'name':o.name,'tris':sum(len(p.vertices)-2 for p in o.data.polygons),'materials':sorted({o.data.materials[p.material_index].name for p in o.data.polygons}),'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]})
 assert before==hashlib.sha256(src.read_bytes()).hexdigest()
(O/'boat-probe.json').write_text(json.dumps(rows,indent=2))

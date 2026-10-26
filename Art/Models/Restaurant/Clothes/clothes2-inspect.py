import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(R/'Assets/Art/Models/Crew/CrewRig.fbx'))
rows=[]
for o in bpy.context.scene.objects:
 rows.append({'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale),'matrix':[list(r) for r in o.matrix_world],'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else [],'vertices':len(o.data.vertices) if o.type=='MESH' else None,'groups':[g.name for g in o.vertex_groups] if o.type=='MESH' else [],'bones':[b.name for b in o.data.bones] if o.type=='ARMATURE' else []})
(O/'clothes2-source-inventory.json').write_text(json.dumps({'objects':rows,'actions':{a.name:list(a.frame_range) for a in bpy.data.actions}},indent=2));print(json.dumps(rows,indent=2))

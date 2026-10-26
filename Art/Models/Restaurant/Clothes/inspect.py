import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[3];rows={}
for name,folder in [('Mira','Mira-sol'),('Ana','Ana'),('Dirk','Dirk'),('Ines','Ines'),('Olaf','Olaf'),('Captain','Captain')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'Art/Models/CrewV2'/folder/(name+'.blend')))
 rows[name]=[{'name':o.name,'type':o.type,'vertices':len(o.data.vertices) if o.type=='MESH' else None,'materials':[m.name for m in o.data.materials] if o.type=='MESH' else [],'groups':[g.name for g in o.vertex_groups] if o.type=='MESH' else [],'bounds':[list(o.matrix_world@__import__('mathutils').Vector(v)) for v in o.bound_box] if o.type=='MESH' else []} for o in bpy.context.scene.objects if o.type in ['MESH','ARMATURE']]
(O/'source-inventory.json').write_text(json.dumps(rows,indent=2))
print('INSPECT PASS')

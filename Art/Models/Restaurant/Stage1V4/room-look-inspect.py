import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(O/'Stage1V4.blend'));sc=bpy.context.scene
rows=[]
for o in sc.objects:
 if o.type=='MESH' and not o.name.startswith('REVIEW_'):
  pts=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'lo':[min(v[k] for v in pts) for k in range(3)],'hi':[max(v[k] for v in pts) for k in range(3)],'materials':[m.name for m in o.data.materials],'colour_attributes':[a.name for a in o.data.color_attributes]})
(O/'room-look-inventory.json').write_text(json.dumps({'meshes':rows,'lights':[{'name':o.name,'type':o.data.type,'energy':o.data.energy} for o in sc.objects if o.type=='LIGHT']},indent=2));print('ROOM INSPECT PASS')

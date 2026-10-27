import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O.parent/'Stage2Bistro/Stage2Bistro.blend'))
rows=[]
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  rows.append({'name':o.name,'location':list(o.location),'min':[min(v[k] for v in pts) for k in range(3)],'max':[max(v[k] for v in pts) for k in range(3)]})
(O/'source-inventory.json').write_text(json.dumps(rows,indent=2))

import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3]
paths=['Art/Models/Fishing/CageKit/SortingBoard.blend','Art/Models/DayBoatKit/Stations/GuttingTable.blend','Art/Models/Fish043/Mackerel/Mackerel.blend','Art/Models/Skerries/Seal.blend']
rows={}
for rel in paths:
    bpy.ops.wm.open_mainfile(filepath=str(R/rel))
    rows[rel]={'sha256':hashlib.sha256((R/rel).read_bytes()).hexdigest(),'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'dimensions':list(o.dimensions),'bounds':[list(o.matrix_world@__import__('mathutils').Vector(c)) for c in o.bound_box] if o.type=='MESH' else []} for o in bpy.context.scene.objects if not o.name.startswith('Preview')],'materials':{m.name:list(m.diffuse_color) for m in bpy.data.materials}}
    print('REFERENCE',rel,json.dumps(rows[rel]),flush=True)
(R/'Art/Models/GutKit/metrics/references.json').write_text(json.dumps(rows,indent=2)+'\n')

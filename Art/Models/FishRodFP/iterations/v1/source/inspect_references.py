import bpy,json
from pathlib import Path
root=Path('/mnt/c/Users/momoy/Projects/Catchline')
for rel in ['Art/Models/CrewV2/Captain/Captain.blend','Art/Models/GullHarbour/Fishing/FishingRod.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(root/rel))
 print('REFERENCE',rel)
 print('MATERIALS',[(m.name, list(m.diffuse_color)) for m in bpy.data.materials])
 print('MESHES',[(o.name, list(o.dimensions)) for o in bpy.context.scene.objects if o.type=='MESH'][:20])

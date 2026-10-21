import bpy
from pathlib import Path
from mathutils import Vector
p=Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(p/'Tier5FisherV1.blend'))
for o in bpy.data.objects:
 if o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
 if lo[1]<-.5 and hi[2]>.2 and lo[2]<.95:print(o.name,[round(v,2) for v in lo],[round(v,2) for v in hi])

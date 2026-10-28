import bpy,sys,json,math
from pathlib import Path
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent));import build_service as b
bpy.ops.wm.read_factory_settings(use_empty=True)
obs=b.load_fbx(b.PACK/'Restaurant_SinkDishRack.fbx');out=[]
for o in obs:
 if o.type!='MESH':continue
 mx=Matrix.Rotation(math.pi/2,4,'X')@o.matrix_world
 for p in o.data.polygons:
  vs=[mx@o.data.vertices[i].co for i in p.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
  if hi[0]>.1 and hi[2]>.35 and p.area>.012:out.append(dict(area=p.area,lo=lo,hi=hi))
(b.O/'basin-faces.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))

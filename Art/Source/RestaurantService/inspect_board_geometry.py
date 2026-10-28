import bpy,sys
from pathlib import Path
from io_scene_fbx import import_fbx
class Op:
 def report(self,*a):pass
bpy.ops.wm.read_factory_settings(use_empty=True)
import_fbx.load(Op(),bpy.context,filepath=str(Path(__file__).resolve().parents[3]/'Assets/Art/Models/Restaurant/Pack/service/Restaurant_CatchBoard.fbx'),use_anim=False)
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  o.data.calc_loop_triangles()
  for t in o.data.loop_triangles:
   if t.area<1e-12:print('DEGENERATE',t.index,t.area,[list(o.data.vertices[i].co) for i in t.vertices])

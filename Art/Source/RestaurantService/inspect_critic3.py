import bpy,sys,json
from pathlib import Path
from io_scene_fbx import import_fbx
O=Path(__file__).resolve().parent;R=O.parents[2]
class Op:
 def report(self,*x):print(*x)
bpy.ops.wm.read_factory_settings(use_empty=True);import_fbx.load(Op(),bpy.context,filepath=str(R/'Assets/Art/Models/Restaurant/Guests/Restaurant_Guest_Critic.fbx'),use_anim=False)
for o in bpy.data.objects:
 if o.type=='MESH':
  print(o.name,'UV',sorted(set(tuple(d.uv) for d in o.data.uv_layers.active.data))[:30]);print('COL',sorted(set(tuple(d.color) for d in o.data.color_attributes.active_color.data))[:5])

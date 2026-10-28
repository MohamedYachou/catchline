import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parents[3]/'Assets/Resources/Restaurant/Stage1V4.fbx'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(p))
for o in bpy.context.scene.objects:
 if o.type=='MESH' and ('RoomShell' in o.name or 'PrepCounter' in o.name or 'DiningTwo' in o.name):
  print('COLOR',o.name,[(a.name,a.domain,len(a.data),[tuple(x.color) for x in list(a.data)[:3]]) for a in o.data.color_attributes],flush=True)
  print('NORMALS',[(tuple(p.normal),p.area) for p in sorted(o.data.polygons,key=lambda p:p.area,reverse=True)[:3]],flush=True)

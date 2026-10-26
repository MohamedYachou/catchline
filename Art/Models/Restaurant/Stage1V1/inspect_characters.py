import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[4]
for path in ['Assets/Art/Models/Crew/CrewRig.fbx','Art/Models/CrewV2/Mira-sol/Mira.fbx']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(R/path));bpy.context.view_layer.update()
 print('SOURCE',path)
 for o in bpy.context.scene.objects:
  if o.type=='MESH':
   vs=[o.matrix_world@v.co for v in o.data.vertices];print(o.name,len(o.data.polygons),'MIN',[round(min(v[i] for v in vs),3) for i in range(3)],'MAX',[round(max(v[i] for v in vs),3) for i in range(3)])
  if o.type=='ARMATURE':print('BONES',[b.name for b in o.pose.bones])
 print('ACTIONS',[(a.name,a.frame_range[:]) for a in bpy.data.actions])

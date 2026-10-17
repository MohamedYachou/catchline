import bpy,json
from mathutils import Vector
from pathlib import Path
P=Path('C:/Users/momoy/Projects/Catchline')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(P/'Assets/Art/Models/Boats/CompactFisherV1.fbx'))
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  print('BOAT',o.name,[(round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)) for i in range(3)])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(P/'Assets/Art/Models/Crew/CrewRig.fbx'),use_anim=True)
for o in bpy.context.scene.objects:
 print('CREW',o.name,o.type,tuple(round(x,3) for x in o.dimensions))
 if o.type=='ARMATURE':print('BONES',[b.name for b in o.pose.bones])
print('ACTIONS',[a.name for a in bpy.data.actions])

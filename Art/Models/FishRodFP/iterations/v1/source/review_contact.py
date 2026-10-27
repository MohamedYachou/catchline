"""Refresh the contact evidence camera without rebuilding or changing the asset."""
from pathlib import Path
import bpy
from mathutils import Vector

out = Path(__file__).resolve().parents[3] / 'Art/Models/FishRodFP'
bpy.ops.wm.open_mainfile(filepath=str(out / 'FishRodFP.blend'))
scene = bpy.context.scene
rig = bpy.data.objects['FishRodFP_Rig']
rig.animation_data.action = bpy.data.actions['Idle']
scene.frame_set(0)
camera = scene.camera
camera.data.type = 'PERSP'
camera.data.lens = 32
camera.location = (.34, .60, .18)
camera.rotation_euler = (Vector((0, -.02, -.07)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
scene.render.filepath = str(out / 'renders/hands-detail.png')
bpy.ops.render.render(write_still=True)
print('CONTACT REVIEW RENDER COMPLETE; saved source and export unchanged')

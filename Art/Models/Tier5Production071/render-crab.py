import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Art/Models/Tier5Production071'
# Matching portrait of the existing authored crab; transparent pixels, no invented image.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/Art/Models/Props/Crab.fbx'))
meshes=[o for o in bpy.data.objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
lo=Vector(tuple(min(v[i] for v in points) for i in range(3)));hi=Vector(tuple(max(v[i] for v in points) for i in range(3)));center=(lo+hi)/2
bpy.ops.object.camera_add(location=center+Vector((.35,-.45,.50)));cam=bpy.context.object;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(hi-lo)*1.50
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.film_transparent=True
scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.world=bpy.data.worlds.new("Crab portrait world");scene.world.color=(.6,.6,.6)
bpy.ops.object.light_add(type='AREA',location=center+Vector((.2,-.3,.7)));lamp=bpy.context.object;lamp.data.energy=35;lamp.data.size=.6;lamp.rotation_euler=(center-lamp.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ROOT/'Assets/Art/UI/fish-crab.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'crab-portrait.blend'));bpy.ops.render.render(write_still=True)
print('TIER071 CRAB PORTRAIT COMPLETE')

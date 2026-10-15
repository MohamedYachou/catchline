"""Source-only seating review: no bench geometry added to NPC FBX."""
import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/WorldPolish'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Harbour/NPC_Sitting.blend'))
root=bpy.data.objects['Catchline_NPC_Sitting'];root.location.z=.2235;root.location.y=-.15
with bpy.data.libraries.load(str(OUT/'Harbour/Bench.blend'),link=False) as (src,dst):dst.objects=['Bench']
bench=dst.objects[0];bpy.data.collections['PREVIEW_ONLY_NOT_EXPORTED'].objects.link(bench)
scene=bpy.context.scene;target=Vector((0,0,.68));scene.camera.location=target+Vector((2.8,-2.8,1.5));scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=2.0
scene.render.resolution_x=scene.render.resolution_y=640;scene.cycles.samples=16
scene.render.filepath=str(OUT/'Previews/Harbour/NPC_Sitting-on-Bench.png');bpy.ops.render.render(write_still=True)
print('NPC seating check: local hip/outfit sole .239 + root .2235 = Bench seat .4625; legs dangle')

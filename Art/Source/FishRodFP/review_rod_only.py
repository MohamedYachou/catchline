"""STEP0 evidence only; no original/v1 edits."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/FishRodFP';D=O/'rod-only';(D/'frames').mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'FishRodFP_RodOnly.blend'))
sc=bpy.context.scene;rig=bpy.data.objects['FishRodFP_Rig'];mesh=bpy.data.objects['FishRodFP_Mesh'];cam=sc.camera
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:sc.cycles.device='CPU'
sc.cycles.samples=16;sc.render.resolution_percentage=100
sc.render.threads_mode='FIXED';sc.render.threads=6
M=json.loads((O/'build-manifest.json').read_text())
def player():
 c=M['camera_source'];cam.location=c['location'];cam.rotation_euler=(Vector(c['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=c['lens_mm'];cam.data.sensor_width=c['sensor_width_mm']
def view(d):
 e=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();pts=[e.matrix_world@v.co for v in me.vertices];e.to_mesh_clear()
 c=Vector(tuple((min(p[i] for p in pts)+max(p[i] for p in pts))*.5 for i in range(3)));cam.data.type='ORTHO';cam.location=c+Vector(d).normalized()*5;cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler();basis=cam.rotation_euler.to_matrix();u=basis@Vector((1,0,0));v=basis@Vector((0,1,0));w=max(p.dot(u) for p in pts)-min(p.dot(u) for p in pts);h=max(p.dot(v) for p in pts)-min(p.dot(v) for p in pts);cam.data.ortho_scale=max(w,h*sc.render.resolution_x/sc.render.resolution_y)*1.14

def render(p):sc.render.filepath=str(p);bpy.ops.render.render(write_still=True)
sc.render.resolution_x=sc.render.resolution_y=600
for n,d in [('front',(0,-3,1)),('back',(0,3,1)),('left',(-3,0,.6)),('right',(3,0,.6)),('top',(0,0,3))]:view(d);render(D/f'{n}.png')
player();sc.render.resolution_x=1440;sc.render.resolution_y=900;render(D/'player-idle-1440.png')
frames=[];sc.render.resolution_x=480;sc.render.resolution_y=300
for n,clip in M['clips'].items():
 end=clip['frames'][1]
 for f in [0,end//2,end]:
  rig.animation_data.action=bpy.data.actions[n];sc.frame_set(f);view((3,2,1.3));p=D/'frames'/f'{n}-{f:02d}.png';render(p);frames.append({'action':n,'frame':f,'file':p.relative_to(D).as_posix()})
(D/'playback-frames.json').write_text(json.dumps(frames,indent=2)+'\n')
print('ROD ONLY RENDERS COMPLETE')

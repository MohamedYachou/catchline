"""Exact inherited player camera plus full side/top, hand contacts and v1 comparator."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/FishRodFP';V=O/'arms-v2';D=V/'renders';D.mkdir(exist_ok=True)
preview='--preview' in sys.argv
contacts='--contacts' in sys.argv
bpy.ops.wm.open_mainfile(filepath=str(O/'FishRodFP_ArmsV2.blend'))
sc=bpy.context.scene;rig=bpy.data.objects['FishRodFP_ArmsV2_Rig'];body=bpy.data.objects['FishRodFP_ArmsV2_Mesh'];cam=sc.camera
M=json.loads((V/'build-manifest.json').read_text());frames={'Idle':[0],'Cast':[18,25],'Hold':[20],'Twitch':[4],'Strike':[6],'Reel':[0,8,16,24],'Lift':[48]}
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 sc.cycles.device='GPU'
except Exception:sc.cycles.device='CPU'
sc.cycles.samples=24;sc.render.resolution_percentage=100;sc.render.threads_mode='FIXED';sc.render.threads=6
def player():
 c=M['camera_source'];cam.location=c['location'];cam.rotation_euler=(Vector(c['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=c['lens_mm'];cam.data.sensor_width=c['sensor_width_mm'];sc.render.resolution_x=1440;sc.render.resolution_y=900
def look(c,d,scale):
 cam.location=Vector(c)+Vector(d).normalized()*5;cam.rotation_euler=(Vector(c)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
def fit(direction):
 e=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();pts=[e.matrix_world@v.co for v in me.vertices];e.to_mesh_clear();c=Vector(tuple((min(p[i] for p in pts)+max(p[i] for p in pts))*.5 for i in range(3)))
 look(c,direction,3);basis=cam.rotation_euler.to_matrix();u=basis@Vector((1,0,0));v=basis@Vector((0,1,0));w=max(p.dot(u) for p in pts)-min(p.dot(u) for p in pts);h=max(p.dot(v) for p in pts)-min(p.dot(v) for p in pts);cam.data.ortho_scale=max(w,h*sc.render.resolution_x/sc.render.resolution_y)*1.12
renders=[]
def render(name,action,frame,view):
 p=D/f'{name}.png';sc.render.filepath=str(p);bpy.ops.render.render(write_still=True);renders.append({'file':p.relative_to(V).as_posix(),'action':action,'frame':frame,'view':view,'size':[sc.render.resolution_x,sc.render.resolution_y]})
for name,fs in ([] if contacts else frames.items()):
 if preview and name!='Idle':continue
 rig.animation_data.action=bpy.data.actions[name]
 for f in fs:
  sc.frame_set(f);player();render(f'{name}-{f:02d}-player',name,f,'exact v1 camera')
  for vn,d in [('side',(1,0,0)),('top',(0,0,1))]:
   sc.render.resolution_x=900;sc.render.resolution_y=700;fit(d);render(f'{name}-{f:02d}-{vn}',name,f,vn)
rig.animation_data.action=bpy.data.actions['Idle'];sc.frame_set(0)
for side,c,d,scale in [('right-grip',(-.025,-.065,.008),(-1,1,.7),.29),('left-crank',M['crank_knob_source'],(1,1,.8),.32)]:
 sc.render.resolution_x=900;sc.render.resolution_y=700;look(c,d,scale);render(side,'Idle',0,'grip closeup')
player();sc.render.resolution_x=844;sc.render.resolution_y=390;render('Idle-00-phone','Idle',0,'exact v1 camera / landscape phone')
if not preview and not contacts:
 # Render v1 freshly from identical inherited camera and lighting settings.
 bpy.ops.wm.open_mainfile(filepath=str(O/'FishRodFP.blend'));sc=bpy.context.scene;cam=sc.camera;rig=bpy.data.objects['FishRodFP_Rig'];sc.cycles.samples=24;sc.cycles.device='GPU';sc.render.resolution_percentage=100
 rig.animation_data.action=bpy.data.actions['Idle'];sc.frame_set(0);player();render('v1-Idle-00-player','Idle',0,'v1 identical exact camera')
(V/('contacts-renders.json' if contacts else ('preview-renders.json' if preview else 'renders.json'))).write_text(json.dumps(renders,indent=2)+'\n');print('ARMS REVIEW RENDERS COMPLETE',len(renders))

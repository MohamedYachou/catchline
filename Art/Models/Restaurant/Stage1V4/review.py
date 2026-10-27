"""Populated review scene; production linked kit remains a separate deliverable."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders';G=O.parent/'Guests'
bpy.ops.wm.open_mainfile(filepath=str(O/'Stage1V4.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;records=[]
sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
def character(src,name,loc,clip='Idle',yaw=0,outfit=None,hat=None):
 before=set(sc.objects);actions=set(bpy.data.actions);bpy.ops.import_scene.fbx(filepath=str(R/src));new=list(set(sc.objects)-before);aa=list(set(bpy.data.actions)-actions);rig=next(o for o in new if o.type=='ARMATURE')
 action=next(a for a in aa if a.name.split('|')[-1].split('.')[0]==clip);rig.animation_data_create();rig.animation_data.action=action
 if action.slots:rig.animation_data.action_slot=action.slots[0]
 for unused in aa:
  if unused!=action:bpy.data.actions.remove(unused)
 if outfit:
  for o in new:
   if o.type=='MESH' and (o.name.startswith('Outfit_') or o.name.startswith('Hat_')):o.hide_render=o.name.split('.')[0] not in [outfit,hat];o.hide_viewport=o.hide_render
 wrapper=bpy.data.objects.new(name+'_placement',None);sc.collection.objects.link(wrapper)
 for o in new:
  if not o.parent:o.parent=wrapper
 wrapper.location=loc;wrapper.rotation_euler.z=math.radians(yaw)
 records.append({'name':name,'source':src,'sha256':hashlib.sha256((R/src).read_bytes()).hexdigest(),'position_blender_m':list(loc),'yaw_deg':yaw,'clip':clip,'scale':1,'original_character_geometry':True});print('PLACED',name,clip,flush=True);return rig
# Eight diners: all six adults, two repeated for the booth/terrace. Two further repeats queue on right jetty.
for n,person,loc,yaw,clip in [
 ('Diner_A','Ada',(.32,-1.35,.04),90,'Eat'),('Diner_B','Ben',(.98,-1.35,.04),-90,'Sit'),
 ('Diner_C','Cora',(1.92,-1.35,.04),90,'Eat'),('Diner_D','Dan',(2.58,-1.35,.04),-90,'Sit'),
 ('Diner_E','Edda',(.99,.80,.04),0,'Eat'),('Diner_F','Finn',(1.71,.16,.04),180,'Sit'),
 ('TerraceDiner','Ben',(-3.18,-3.48,-.04),90,'Sit'),('TerraceDiner2','Ada',(-2.52,-3.48,-.04),-90,'Eat'),('BoothDiner','Ada',(2.15,2.02,.04),0,'Eat'),
 ('Queue1','Cora',(3.16,-2.93,-.03),180,'Idle'),('Queue2','Finn',(3.25,-3.65,-.03),180,'Idle'),('Queue3','Edda',(3.13,-4.32,-.03),180,'Idle')]:
 character('Art/Models/Restaurant/Guests/Guest_'+person+'_v2.fbx',n,loc,clip,yaw)
character('Assets/Art/Models/Crew/CrewRig.fbx','Cook',(-2.4,.84,.04),'Idle',90,'Outfit_Deckhand','Hat_Beanie')
character('Assets/Art/Models/Crew/CrewRig.fbx','Waiter',(-.02,-.55,.04),'Carry',-20,'Outfit_Captain','Hat_CaptainCap')
character('Art/Models/CrewV2/Mira-sol/Mira.fbx','Mira',(3.02,-1.25,.04),'Idle',0)
sc.frame_set(13);bpy.context.view_layer.update();cam=sc.camera;camrows=[]
for kind,res,label in [('PERSP',(1440,900),'room-1440x900'),('PERSP',(844,390),'room-844x390')]:
 sc.render.resolution_x,sc.render.resolution_y=res;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';cam.data.type=kind;cam.data.lens=58 if res[0]==1440 else 47;cam.data.ortho_scale=12.4
 camrows.append({'file':label+'.png','projection':kind,'resolution':res,'position_blender_m':list(cam.location),'rotation_blender_rad':list(cam.rotation_euler),'position_unity_m':[cam.location.x,cam.location.z,-cam.location.y],'rotation_unity_euler_deg':[38,178,0],'elevation_deg':38,'yaw_blender_deg':-2,'distance_m':21,'lens_mm':cam.data.lens,'horizontal_fov_deg':math.degrees(2*math.atan(36/(2*cam.data.lens))),'vertical_fov_deg':math.degrees(2*math.atan(36/res[0]*res[1]/(2*cam.data.lens))),'unity_orthographic_size_m':cam.data.ortho_scale/(res[0]/res[1])/2,'frame':13})
 sc.render.filepath=str(P/(label+'.png'));bpy.ops.render.render(write_still=True);print('POPULATED PROOF',label,flush=True)
cam.data.type='PERSP';cam.data.lens=58;sc.render.resolution_x=1440;sc.render.resolution_y=900;bpy.ops.wm.save_as_mainfile(filepath=str(O/'LookProof.blend'))
(O/'characters.json').write_text(json.dumps(records,indent=2));(O/'final-cameras.json').write_text(json.dumps(camrows,indent=2));print('V4 REVIEW PASS')

"""V4-angle studio lineup. Front exact-size face pairing composed separately."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
names=[r['name'] for r in json.loads((O/'guests3-metrics.json').read_text())['guests']]
for i,n in enumerate(names):
 before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(O/(n+'.fbx')));new=set(bpy.data.objects)-before;rig=next(o for o in new if o.type=='ARMATURE');a=rig.animation_data.action
 idle=next(a for a in bpy.data.actions if a.name.split('|')[-1].split('.')[0]=='Idle');rig.animation_data.action=idle
 if idle.slots:rig.animation_data.action_slot=idle.slots[0]
 offset=bpy.data.objects.new('REVIEW_Offset_'+n,None);sc.collection.objects.link(offset);offset.location.x=(i-3.5)*.78;rig.parent=offset
sc.frame_set(12)
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.world=bpy.data.worlds.new('Studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.22,.27,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size in [((-3,-4,6),450,5),((3,-1,4),220,4)]:
 data=bpy.data.lights.new('Softbox','AREA');data.energy=power;data.size=size;light=bpy.data.objects.new('Softbox',data);sc.collection.objects.link(light);light.location=loc;light.rotation_euler=(Vector((0,0,.5))-light.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=7.0
cam.rotation_euler=json.loads((O.parent/'Stage1V4/final-cameras.json').read_text())[0]['rotation_blender_rad'];cam.location=Vector((0,0,.48))+cam.rotation_euler.to_matrix()@Vector((0,0,12))
sc.render.resolution_x=844;sc.render.resolution_y=390;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.render.filepath=str(O/'renders-guests3/guests3-v4-angle-844x390.png');bpy.ops.render.render(write_still=True)
(O/'guests3-camera.json').write_text(json.dumps({'orientation_source':'Stage1V4/final-cameras.json desktop saved camera','rotation_rad':list(cam.rotation_euler),'projection':'ORTHO studio review, not full-room perspective','resolution':[844,390],'idle_frame':12,'names_left_to_right':names},indent=2))

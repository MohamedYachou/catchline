"""Read-only lit V4 proof + labelled diagnostic head views; original cameras retained."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V4';P=O/'mira-match-renders';P.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(V/'RoomLook3-Check.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
names={r['name'] for r in json.loads((V/'build-metrics.json').read_text())['production_meshes']}
for o in list(sc.objects):
 if o.type in ['MESH','ARMATURE','EMPTY'] and (o.name not in names or o.name.startswith(('DiningTwo','DiningFour','TerraceTable','PlaceSetting_','Glass_','Candle_','V4_Plate_','V4_Glass_'))):bpy.data.objects.remove(o,do_unlink=True)
sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
before=set(sc.objects);bpy.ops.import_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'));added=set(sc.objects)-before;rig=next(o for o in added if o.type=='ARMATURE');rig.animation_data_clear()
for ob in list(added):
 if ob.type=='MESH' and ob.name.split('.')[0] not in ['Body','Outfit_HostFormal','Hat_HairUpClip']:bpy.data.objects.remove(ob,do_unlink=True)
root=bpy.data.objects.new('REVIEW_MiraRoot',None);sc.collection.objects.link(root);root.location=(1.8,-1.05,.045);rig.parent=root;rig.data.pose_position='POSE'
a=next(a for a in bpy.data.actions if a.name.split('|')[-1]=='Idle');rig.animation_data_create();rig.animation_data.action=a
if a.slots:rig.animation_data.action_slot=a.slots[0]
sc.frame_set(13);cams=json.loads((V/'final-cameras.json').read_text());cam=sc.camera
# Fast diagnostic first, uses the actual V4 angle and room light.
cam.rotation_euler=cams[0]['rotation_blender_rad'];cam.location=Vector((1.8,-1.05,.57))+cam.rotation_euler.to_matrix()@Vector((0,0,2.6));cam.data.lens=58;sc.render.resolution_x=500;sc.render.resolution_y=650;sc.render.filepath=str(P/'mira-v4-detail.png');bpy.ops.render.render(write_still=True)
for c in cams:
 cam.location=c['position_blender_m'];cam.rotation_euler=c['rotation_blender_rad'];cam.data.lens=c['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=c['resolution'];sc.render.filepath=str(P/('mira-room-'+str(c['resolution'][0])+'.png'));bpy.ops.render.render(write_still=True)
# Neutral front + rear three-quarter studio proofs of silhouette and face.
for o in list(sc.objects):
 if o not in added and o!=root and o.type not in ['CAMERA']:bpy.data.objects.remove(o,do_unlink=True)
root.location=(0,0,0);sc.world=bpy.data.worlds.new('MiraStudio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.14,.19,.23,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size in [((-3,-4,5),350,4),((3,-2,4),240,4),((0,3,4),260,3)]:
 data=bpy.data.lights.new('Softbox','AREA');data.energy=power;data.size=size;light=bpy.data.objects.new('Softbox',data);sc.collection.objects.link(light);light.location=loc;light.rotation_euler=(Vector((0,0,.6))-light.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';cam.data.ortho_scale=1.23;sc.render.resolution_x=500;sc.render.resolution_y=650
for name,loc,target in [('front',(0,-4,.70),(0,0,.52)),('threequarter',(2,-4,1.4),(0,0,.53)),('back',(2,4,1.4),(0,0,.53))]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/('mira-'+name+'.png'));bpy.ops.render.render(write_still=True)
(O/'mira-match-cameras.json').write_text(json.dumps({'game_camera_source':'Stage1V4/final-cameras.json','game_camera_rows':cams,'diagnostics':'Front/threequarter/back orthographic studio; detail V4 angle translated closer','native_Unity_unverified':True},indent=2));print('MIRA MATCH RENDER PASS',flush=True)

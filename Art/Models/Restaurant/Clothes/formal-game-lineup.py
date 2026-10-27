import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene
for i,outfit in enumerate(['Outfit_HostFormal','Outfit_WaiterSkirt','Outfit_CookWhites']):
 before=set(sc.objects);bpy.ops.import_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'));added=set(sc.objects)-before;rig=next(o for o in added if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST';keep=['Body',outfit]+(['Hat_HairUpClip'] if i==0 else ['Hat_Toque'] if i==2 else [])
 for ob in list(added):
  if ob.type=='MESH' and ob.name.split('.')[0] not in keep:bpy.data.objects.remove(ob,do_unlink=True)
 offset=bpy.data.objects.new('REVIEW_Offset',None);sc.collection.objects.link(offset);offset.location.x=(i-4)*.95;rig.parent=offset;rig.data.pose_position='POSE';a=next(a for a in bpy.data.actions if a.name.split('|')[-1]=='Idle');rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
for i,n in enumerate(['Gus','Hazel','Ivo','Jonas','Kai','Lena']):
 before=set(sc.objects);bpy.ops.import_scene.fbx(filepath=str(O.parent/'Guests'/('Guest_'+n+'.fbx')));rig=next(o for o in set(sc.objects)-before if o.type=='ARMATURE');rig.animation_data_clear();offset=bpy.data.objects.new('REVIEW_Offset',None);sc.collection.objects.link(offset);offset.location.x=(i-1)*.95;rig.parent=offset;rig.data.pose_position='POSE';a=next(a for a in bpy.data.actions if a.name.split('|')[-1]=='Idle');rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
sc.frame_set(13);sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.world=bpy.data.worlds.new('Night');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.19,.27,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
for loc,power,size,col in [((-3,-4,5),650,7,(1,.82,.63)),((3,-2,4),450,6,(.65,.82,1))]:
 data=bpy.data.lights.new('Studio','AREA');data.energy=power;data.color=col;data.shape='DISK';data.size=size;ob=bpy.data.objects.new('Studio',data);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200);ground=bpy.context.object;ground.location.z=-.01;mat=bpy.data.materials.new('REVIEW_Slate');mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.028,.055,.075,1);ground.data.materials.append(mat)
cam=bpy.data.objects.new('Exact V4 camera',bpy.data.cameras.new('Exact V4 camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.lens=58
cams=json.loads((O.parent/'Stage1V4/final-cameras.json').read_text());proof=[]
for c in cams:
 cam.location=c['position_blender_m'];cam.rotation_euler=c['rotation_blender_rad'];sc.render.resolution_x=c['resolution'][0];sc.render.resolution_y=c['resolution'][1];sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX';sc.render.filepath=str(O/('formal-game-'+str(c['resolution'][0])+'.png'));bpy.ops.render.render(write_still=True);proof.append({'file':Path(sc.render.filepath).name,'camera_source':c,'note':'Exact saved camera position/rotation/lens/resolution; neutral studio floor and lighting, not room/native integration.'})
(O/'formal-game-cameras.json').write_text(json.dumps(proof,indent=2));print('EXACT V4 LINEUP PASS',flush=True)

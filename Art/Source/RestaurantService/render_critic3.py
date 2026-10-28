"""Pose evidence from actual exported critic with Ada-compatible unchanged takes."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import import_fbx
O=Path(__file__).resolve().parent;R=O.parents[2];sys.path.insert(0,str(O))
import build_props3 as p
import props3_scene
bpy.ops.wm.read_factory_settings(use_empty=True)
rec=next(r for r in json.loads((O/'props3-manifest.json').read_text()) if r.get('rig')=='CrewRig')
import_fbx.load(p.b.OP,bpy.context,filepath=str(R/rec['file']),use_anim=True)
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');meshes=[o for o in bpy.data.objects if o.type=='MESH'];p.b.MAT=p.material()
for o in meshes:o.data.materials.clear();o.data.materials.append(p.b.MAT)
scene,cam,room=props3_scene.scene_setup(rig,rec,'Critic')
anchor=bpy.data.objects.new('REVIEW_placement_unanimated',None);scene.collection.objects.link(anchor);rig.parent=anchor;rig.location=(0,0,0)
# Print actual chair world bounds so placement is inspectable and measured.
bpy.context.view_layer.update()
for o in room:
 if o.type=='MESH' and ('Dining' in o.name):
  vs=[o.matrix_world@Vector(v) for v in o.bound_box];print('ROOM_SUPPORT',o.name,[round(min(v[i] for v in vs),3) for i in range(3)],[round(max(v[i] for v in vs),3) for i in range(3)],flush=True)
def bind(key,f):
 a=next(a for a in bpy.data.actions if a.name.split('|')[-1]==key);rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
 rig.data.pose_position='POSE';scene.frame_set(f);bpy.context.view_layer.update()
def render(suffix):
 if '--' in sys.argv and suffix not in sys.argv[sys.argv.index('--')+1:]:return (O/'renders'/('props3-Restaurant_Guest_Critic-'+suffix+'.png')).relative_to(R).as_posix()
 scene.render.filepath=str(O/'renders'/('props3-Restaurant_Guest_Critic-'+suffix+'.png'));bpy.ops.render.render(write_still=True);return Path(scene.render.filepath).relative_to(R).as_posix()
frames=[];bind('Walk',7);anchor.location=(-.1,0,.04);p.b.place_camera(cam,Vector((-.1,0,.54)),2.65,38);frames.append(render('walk-service'))
# Ada Sit raises hips 0.17m; place on the near existing table chair.
for key,f in [('Sit',13),('Eat',25)]:
 bind(key,f);anchor.location=(.80,.25,.24);anchor.rotation_euler.z=math.pi/2;bpy.context.view_layer.update();target=Vector((1.15,.32,.60));pitch=math.radians(38);yaw=math.radians(-15);cam.location=target+Vector((math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)))*4;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=2.5;frames.append(render(key.lower()+'-service'))
bind('Idle',1);anchor.location=(0,0,0);anchor.rotation_euler.z=0;bpy.context.view_layer.update()
# Close-ups use an uncluttered evidence stage; service poses above retain actual room.
for ob in room:ob.hide_render=True
for ob in scene.objects:
 if ob.type=='LIGHT':ob.hide_render=True
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002));floor=bpy.context.object;floor.data.materials.append(p.b.flat_material('Review navy floor',(.028,.044,.063)))
for loc,power,col,size in [((-2,-3,4),260,(1,.82,.64),3),((2,1,3),180,(.54,.72,1),2)]:
 d=bpy.data.lights.new('Close review softbox','AREA');d.energy=power;d.color=col;d.size=size;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
scene.view_settings.exposure=0
for name,yaw in [('front',0),('side',90),('back',180)]:
 target=anchor.location+Vector((0,0,.54));angle=math.radians(yaw);cam.location=target+Vector((math.sin(angle)*3,-math.cos(angle)*3,.55));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.9;frames.append(render(name+'-close'))
rec['renders']=frames;rec['render_review']='PENDING';rec['service_camera_pitch_deg']=38;rec['pose_frames']={'Walk':7,'Sit':13,'Eat':25,'Idle':1};rec['pose_review_note']='Exported bones/actions unchanged. Walk root floor0.04; Sit/Eat evidence root0.24m aligns Ada seated hips with V4 chair. Runtime seating offset needs native verification.';p.save_manifest(rec);print('CRITIC RENDERED',flush=True)

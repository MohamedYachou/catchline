import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders-v2';P.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def init():bpy.ops.wm.read_factory_settings(use_empty=True)
def bind(rig,suffix):
 a=next(a for a in bpy.data.actions if a.name.split('|')[-1]==suffix);rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
 return a
def bones(rig):return {b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(r) for r in b.matrix_local]} for b in rig.data.bones}
def motions(rig,clip):
 a=bind(rig,clip);out=[]
 for f in [1,7,13,19,25]:
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update();out.append({b.name:[list(r) for r in b.matrix] for b in rig.pose.bones})
 return out
init();bpy.ops.import_scene.fbx(filepath=str(R/'Assets/Art/Models/Crew/CrewRig.fbx'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');ref=bones(rig);refmotion={n:motions(rig,n) for n in ['Idle','Walk']};rows=[]
for record in json.loads((O/'build-metrics-v2.json').read_text())['guests']:
 init();sc=bpy.context.scene;name=record['name'];bpy.ops.import_scene.fbx(filepath=str(O/(name+'.fbx')));rig=next(o for o in sc.objects if o.type=='ARMATURE');mesh=next(o for o in sc.objects if o.type=='MESH');bb=bones(rig);assert bb.keys()==ref.keys();delta=max(abs(bb[n]['matrix'][i][j]-ref[n]['matrix'][i][j]) for n in bb for i in range(4) for j in range(4));assert delta<1e-5,delta
 assert all(bb[n]['parent']==ref[n]['parent'] for n in bb)
 mesh.data.calc_loop_triangles();tri=len(mesh.data.loop_triangles);assert tri<=12000
 assert all(v.groups and abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in mesh.data.vertices)
 clips={a.name.split('|')[-1]:list(a.frame_range) for a in bpy.data.actions};assert all(n in clips for n in ['Idle','Walk','Sit','Eat'])
 motiondelta={}
 for clip in ['Idle','Walk']:
  mm=motions(rig,clip);dd=max(abs(mm[f][n][i][j]-refmotion[clip][f][n][i][j]) for f in range(5) for n in bb for i in range(4) for j in range(4));assert dd<1e-4,(name,clip,dd);motiondelta[clip]=dd
 em=motions(rig,'Eat');handtravel=max((Vector([em[f]['RightHand'][i][3] for i in range(3)])-Vector([em[0]['RightHand'][i][3] for i in range(3)])).length for f in range(5));assert handtravel>.02,handtravel
 # Per-character visual evidence rendered from the independently imported FBX.
 sc.render.engine='CYCLES';sc.cycles.samples=20;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 sc.world=bpy.data.worlds.new('Studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.19,.24,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
 for loc,power,size in [((-2,-3,4),180,3),((2,-1,2.5),90,2)]:
  data=bpy.data.lights.new('Softbox','AREA');data.energy=power;data.shape='DISK';data.size=size;ob=bpy.data.objects.new('Softbox',data);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.5))-ob.location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.3;sc.render.resolution_x=360;sc.render.resolution_y=440;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
 for label,clip,frame,yaw in [('idle','Idle',12,0),('sit','Sit',1,0),('sit-side','Sit',1,90),('eat','Eat',25,0)]:
  bind(rig,clip);sc.frame_set(frame);bpy.context.view_layer.update();a=math.radians(yaw);target=Vector((0,-.03,.54));cam.location=target+Vector((math.sin(a)*3,-math.cos(a)*3,1.3));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/(name+'-'+label+'.png'));bpy.ops.render.render(write_still=True)
 rows.append({'name':name,'fbx_sha256':sha(O/(name+'.fbx')),'triangles':tri,'bone_names_parents_rest_max_delta_m':delta,'original_idle_walk_sampled_matrix_delta':motiondelta,'clips':clips,'eat_hand_travel_m':handtravel,'normalized_nonempty_weights':True,'images':[name+'-'+s+'.png' for s in ['idle','sit','sit-side','eat']]});print('GUEST VALIDATED',name,tri,handtravel,flush=True)
(O/'validation-v2.json').write_text(json.dumps({'pass':True,'reference_fbx_sha256':sha(R/'Assets/Art/Models/Crew/CrewRig.fbx'),'guests':rows,'native_unity_unverified':True},indent=2));print('GUEST VALIDATION PASS')

import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;P=O/'renders-guests3';P.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(rig,n):
 a=next(a for a in bpy.data.actions if a.name.split('|')[-1]==n);rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
 return a
def bones(rig):return {b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(r) for r in b.matrix_local]} for b in rig.data.bones}
def sample(rig,n):
 a=bind(rig,n);lo,hi=a.frame_range;out=[]
 for t in [0,.25,.5,.75,1]:
  bpy.context.scene.frame_set(round(lo+(hi-lo)*t));bpy.context.view_layer.update();out.append({b.name:[list(r) for r in b.matrix] for b in rig.pose.bones})
 return out
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O.parent/'Clothes/CrewRig_Restaurant.fbx'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');ref=bones(rig);clips={a.name.split('|')[-1]:list(a.frame_range) for a in bpy.data.actions};refposes={n:sample(rig,n) for n in clips};assert len(clips)==20
rows=[]
for record in json.loads((O/'guests3-metrics.json').read_text())['guests']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/(record['name']+'.fbx')));sc=bpy.context.scene;rig=next(o for o in sc.objects if o.type=='ARMATURE');ob=next(o for o in sc.objects if o.type=='MESH');bb=bones(rig);assert bb.keys()==ref.keys() and len(bb)==20
 delta=max(abs(bb[n]['matrix'][i][j]-ref[n]['matrix'][i][j]) for n in bb for i in range(4) for j in range(4));assert delta<1e-5
 assert all(bb[n]['parent']==ref[n]['parent'] for n in bb)
 actions={a.name.split('|')[-1]:list(a.frame_range) for a in bpy.data.actions};assert set(actions)==set(clips)|{'Sit','Eat'}
 md={}
 for n in clips:
  assert actions[n]==clips[n];poses=sample(rig,n);d=max(abs(poses[f][b][i][j]-refposes[n][f][b][i][j]) for f in range(5) for b in bb for i in range(4) for j in range(4));assert d<1e-4,(n,d);md[n]=d
 assert all(v.groups and abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in ob.data.vertices)
 assert all(m.name.startswith(record['name']+'_') for m in ob.data.materials);assert len(ob.data.uv_layers)>=1
 ob.data.calc_loop_triangles();tri=len(ob.data.loop_triangles);assert tri<12000
 rig.data.pose_position='REST';pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)];assert max(hi[i]-lo[i] for i in range(3))<1.5;rig.data.pose_position='POSE'
 sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 sc.world=bpy.data.worlds.new('Studio');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.22,.27,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 for loc,power in [((-2,-3,4),170),((2,-1,3),90)]:
  data=bpy.data.lights.new('Softbox','AREA');data.energy=power;data.size=3;light=bpy.data.objects.new('Softbox',data);sc.collection.objects.link(light);light.location=loc;light.rotation_euler=(Vector((0,0,.5))-light.location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.19;sc.render.resolution_x=288;sc.render.resolution_y=390;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='AgX'
 for label,clip,frame in [('front','Idle',12),('sit','Sit',1),('eat','Eat',25)]:
  bind(rig,clip);sc.frame_set(frame);cam.location=(0,-3,.53);cam.rotation_euler=(Vector((0,0,.53))-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/(record['name']+'-'+label+'.png'));bpy.ops.render.render(write_still=True)
 rows.append({'name':record['name'],'face':record['face'],'triangles':tri,'bounds_rest_m':[lo,hi],'bone_rest_delta':delta,'clip_sample_deltas':md,'clips':actions,'normalized_weights':True,'materials':[{'name':m.name,'linear_rgba':list(m.diffuse_color)} for m in ob.data.materials],'uv0':True,'fbx_sha256':sha(O/(record['name']+'.fbx'))});print('GUEST3 VALIDATED',record['name'],flush=True)
preserved=json.loads((O/'guests3-preserved.json').read_text());assert all(sha(O/n)==h for n,h in preserved.items())
(O/'guests3-validation.json').write_text(json.dumps({'pass':True,'guests':rows,'all_prior_guest_hashes_unchanged':True,'reference_sha256':sha(O.parent/'Clothes/CrewRig_Restaurant.fbx'),'native_unity_unverified':True},indent=2))

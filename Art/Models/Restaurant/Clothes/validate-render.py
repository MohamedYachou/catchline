import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders';P.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clear():bpy.ops.wm.read_factory_settings(use_empty=True)
def bind(rig,clip):
 a=next(a for a in bpy.data.actions if a.name.split('|')[-1]==clip);rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
def bones(rig):return {b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(r) for r in b.matrix_local]} for b in rig.data.bones}
def motion(rig,clip):
 bind(rig,clip);out=[]
 for f in [1,7,13,19,25]:
  bpy.context.scene.frame_set(f);bpy.context.view_layer.update();out.append({b.name:[list(r) for r in b.matrix] for b in rig.pose.bones})
 return out
clear();bpy.ops.import_scene.fbx(filepath=str(R/'Assets/Art/Models/Crew/CrewRig.fbx'));rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');ref=bones(rig);rm={n:motion(rig,n) for n in ['Idle','Walk']};rows=[]
for record in json.loads((O/'build-metrics.json').read_text())['assets']:
 clear();sc=bpy.context.scene;name=record['asset'];bpy.ops.import_scene.fbx(filepath=str(O/(name+'.fbx')));rig=next(o for o in sc.objects if o.type=='ARMATURE');meshes=[o for o in sc.objects if o.type=='MESH'];bb=bones(rig)
 assert bb.keys()==ref.keys();assert all(bb[n]['parent']==ref[n]['parent'] for n in bb)
 delta=max(abs(bb[n]['matrix'][i][j]-ref[n]['matrix'][i][j]) for n in bb for i in range(4) for j in range(4));assert delta<1e-5,delta
 assert len(meshes)==4
 textures=[]
 for im in bpy.data.images:
  if im.source!='FILE':continue
  path=Path(bpy.path.abspath(im.filepath));assert im.packed_file or path.is_file(),(name,im.name,str(path))
  if not im.has_data:im.reload()
  assert im.size[0]>0,(name,im.name,'empty texture')
  textures.append({'image':im.name,'path':str(path),'dimensions':list(im.size),'packed':bool(im.packed_file),'exists':path.is_file()})
 assert len(textures)==len(record['textures']),(name,len(textures),len(record['textures']))
 md={}
 for clip in ['Idle','Walk']:
  mm=motion(rig,clip);dd=max(abs(mm[f][n][i][j]-rm[clip][f][n][i][j]) for f in range(5) for n in bb for i in range(4) for j in range(4));assert dd<1e-4,(name,clip,dd);md[clip]=dd
 bounds=[]
 rig.data.pose_position='REST';bpy.context.view_layer.update()
 for ob in meshes:
  ob.data.calc_loop_triangles();assert all(v.groups and abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in ob.data.vertices),(name,ob.name,'weights')
  vs=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];assert max(hi[i]-lo[i] for i in range(3))<1.5,(ob.name,lo,hi)
  bounds.append({'mesh':ob.name,'world_bounds_rest': [lo,hi],'triangles':len(ob.data.loop_triangles),'normalized_weights':True})
 clips={a.name.split('|')[-1]:list(a.frame_range) for a in bpy.data.actions};assert len(clips)==len(record['actions']),(name,clips)
 rig.data.pose_position='POSE'
 sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 sc.world=bpy.data.worlds.new('Night ambient');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.22,.29,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 for loc,power,size,col in [((-2,-3,4),170,3,(1,.83,.64)),((2,-1,2.5),100,2,(.66,.83,1)),((0,2,3),180,2,(1,.72,.42))]:
  data=bpy.data.lights.new('Softbox','AREA');data.energy=power;data.color=col;data.shape='DISK';data.size=size;ob=bpy.data.objects.new('Softbox',data);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.5))-ob.location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=1.25;sc.render.resolution_x=480;sc.render.resolution_y=580;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.view_settings.view_transform='AgX'
 images=[]
 for label,clip,frame,yaw,elev in [('front','Idle',12,0,.05),('game45','Idle',12,35,1.7),('back','Idle',12,180,.3),('walk','Walk',7,-30,.3)]:
  bind(rig,clip);sc.frame_set(frame);bpy.context.view_layer.update();a=math.radians(yaw);target=Vector((0,0,.53));cam.location=target+Vector((math.sin(a)*3,-math.cos(a)*3,elev));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();sc.render.filepath=str(P/(name+'-'+label+'.png'));bpy.ops.render.render(write_still=True);images.append(name+'-'+label+'.png')
 rows.append({'asset':name,'fbx_sha256':sha(O/(name+'.fbx')),'textures':textures,'bone_rest_delta':delta,'original_idle_walk_motion_delta':md,'clips':clips,'meshes':bounds,'rendered_from_reimported_fbx':True,'images':images});(O/'validation.json').write_text(json.dumps({'pass':True,'reference':str(R/'Assets/Art/Models/Crew/CrewRig.fbx'),'native_unity_unverified':True,'assets':rows},indent=2));print('VALIDATED',name,flush=True)
print('CLOTHES VALIDATION PASS',flush=True)

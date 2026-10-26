import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders';P.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clear():bpy.ops.wm.read_factory_settings(use_empty=True)
def bind(rig,clip):
 a=next(a for a in bpy.data.actions if a.name.split('|')[-1]==clip);rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
def inventory():
 rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST';bpy.context.view_layer.update()
 bones={b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(r) for r in b.matrix_local]} for b in rig.data.bones};meshes={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  meshes[o.name]={'v':[[round(x,6) for x in v.co] for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'mat':[m.name for m in o.data.materials],'mi':[p.material_index for p in o.data.polygons],'w':[{o.vertex_groups[g.group].name:round(g.weight,5) for g in v.groups} for v in o.data.vertices],'uv':[[[round(x,6) for x in v.uv] for v in uv.data] for uv in o.data.uv_layers]}
 clips={a.name.split('|')[-1]:list(a.frame_range) for a in bpy.data.actions};motions={}
 rig.data.pose_position='POSE'
 for clip,frames in clips.items():
  bind(rig,clip);out=[]
  for f in [frames[0]+(frames[1]-frames[0])*t/4 for t in range(5)]:
   bpy.context.scene.frame_set(int(f));bpy.context.view_layer.update();out.append({b.name:[list(r) for r in b.matrix] for b in rig.pose.bones})
  motions[clip]=out
 return rig,bones,meshes,clips,motions
clear();bpy.ops.import_scene.fbx(filepath=str(R/'Assets/Art/Models/Crew/CrewRig.fbx'));_,rb,rm,rc,ra=inventory()
clear();bpy.ops.import_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'));rig,b,m,c,a=inventory()
assert b.keys()==rb.keys();assert all(b[n]['parent']==rb[n]['parent'] for n in b)
rest=max(abs(b[n]['matrix'][i][j]-rb[n]['matrix'][i][j]) for n in b for i in range(4) for j in range(4));assert rest<1e-5,rest
assert c==rc,(c,rc)
motion={clip:max(abs(a[clip][f][n][i][j]-ra[clip][f][n][i][j]) for f in range(5) for n in b for i in range(4) for j in range(4)) for clip in c};assert max(motion.values())<1e-4,motion
preservation={n:{k:m[n][k]==v for k,v in row.items()} for n,row in rm.items()};assert all(all(row.values()) for row in preservation.values()),preservation
expected=['Outfit_Host','Outfit_CookWhites','Outfit_WaiterSkirt','Outfit_WaiterSuit','Outfit_Barista','Outfit_Handyman','Outfit_HelperSuit','Outfit_Dishwasher','Hat_Toque'];assert set(m)==set(rm)|set(expected)
rig.data.pose_position='REST';bounds=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 if o.name in expected:assert all(v.groups and abs(sum(g.weight for g in v.groups)-1)<1e-4 for v in o.data.vertices),(o.name,'weights')
 assert all(mod.object==rig for mod in o.modifiers if mod.type=='ARMATURE')
 vs=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];assert max(hi[i]-lo[i] for i in range(3))<1.5,(o.name,lo,hi)
 bounds.append({'mesh':o.name,'bounds':[lo,hi],'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)})
(O/'clothes2-validation.json').write_text(json.dumps({'pass':True,'source_sha256':sha(R/'Assets/Art/Models/Crew/CrewRig.fbx'),'fbx_sha256':sha(O/'CrewRig_Restaurant.fbx'),'bone_count':len(b),'rest_max_delta':rest,'original_mesh_preservation':preservation,'clips':c,'all_clip_motion_max_deltas':motion,'meshes':bounds,'exact_added_names':expected,'normalized_weights':True,'native_unity_unverified':True},indent=2));print('CLOTHES2 VALIDATION PASS',flush=True)
# Render only original Body + selected job outfit, exactly how runtime toggles siblings.
rig.data.pose_position='POSE';sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.world=bpy.data.worlds.new('Restaurant night');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.22,.29,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size,col in [((-2,-3,4),170,3,(1,.83,.64)),((2,-1,2.5),100,2,(.66,.83,1)),((0,2,3),180,2,(1,.72,.42))]:
 data=bpy.data.lights.new('Softbox','AREA');data.energy=power;data.color=col;data.shape='DISK';data.size=size;ob=bpy.data.objects.new('Softbox',data);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.5))-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('V4 Camera',bpy.data.cameras.new('V4 Camera'));sc.collection.objects.link(cam);sc.camera=cam
v4=json.loads((O.parent/'Stage1V4/final-cameras.json').read_text())[0];cam.rotation_euler=v4['rotation_blender_rad'];cam.data.type='PERSP';cam.data.lens=58
# Same V4 camera orientation/lens; translated towards a single actor for wardrobe readability.
target=Vector((0,0,.53));cam.location=target+cam.rotation_euler.to_matrix()@Vector((0,0,3.0));sc.render.resolution_x=480;sc.render.resolution_y=580;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.view_settings.view_transform='AgX'
for outfit in expected[:-1]:
 for ob in sc.objects:
  if ob.type=='MESH':ob.hide_render=ob.name not in ['Body',outfit]+(['Hat_Toque'] if outfit=='Outfit_CookWhites' else [])
 for clip,frame in [('Idle',13),('Walk',7),('Carry',13)]:
  bind(rig,clip);sc.frame_set(frame);sc.render.filepath=str(P/('clothes2-'+outfit+'-'+clip+'.png'));bpy.ops.render.render(write_still=True)
 print('RENDERED',outfit,flush=True)
print('CLOTHES2 RENDER PASS',flush=True)

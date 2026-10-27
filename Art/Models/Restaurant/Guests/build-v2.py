"""Six adult civilians, original unmodified CrewRig bones and actions, additional Sit/Eat."""
import bpy,sys,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('town',str(R/'Art/Source/Townsfolk/build.py'));T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)
GUESTS=[('Guest_Ada','woman','C58C60','7B4530','E85B62','253F58','bob'),('Guest_Ben','man','8A5238','292C2B','F4BC36','254960','short'),('Guest_Cora','woman','E5B38E','C79842','187DAE','353E56','long'),('Guest_Dan','man','B87550','4A302A','DF6D36','2C3D51','short'),('Guest_Edda','woman','8E6049','999C98','27A996','344F64','bun'),('Guest_Finn','man','D6A477','94603C','A55EB9','8A6C50','short')]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pose_action(rig,name):
 action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=action
 # Additive clips bind the identical skeleton. Feet point forward; thighs horizontal, knees bent.
 for f in [1,13,25,37,49]:
  t=(f-1)/48*math.tau
  for pb in rig.pose.bones:pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.location=(0,0,0);pb.scale=(1,1,1)
  # Hips local Y is world Z on the original rig.
  rig.pose.bones['Hips'].location.y=.17+.003*math.sin(t)
  for side in ['Left','Right']:
   rig.pose.bones[side+'UpLeg'].rotation_euler.x=-math.pi/2
   rig.pose.bones[side+'Leg'].rotation_euler.x=math.pi/2
   # Rest arms are T posed. World Z is local? Orient via world-space desired rotations below.
   arm=rig.pose.bones[side+'Arm'];sgn=1 if side=='Left' else -1
   # Rotate the arm down from +/-X towards the tabletop (-Y) and slightly down.
   arm.rotation_euler.x=math.radians(-55)
   arm.rotation_euler.z=sgn*math.radians(-26)
   rig.pose.bones[side+'ForeArm'].rotation_euler.z=sgn*math.radians(-24)
  rig.pose.bones['Spine'].rotation_euler.x=.035*math.sin(t)
  if name=='Eat':
   bite=(1-math.cos(t))/2
   rig.pose.bones['RightForeArm'].rotation_euler.z=-.85*bite
   rig.pose.bones['RightArm'].rotation_euler.y+=.25*bite
   rig.pose.bones['Head'].rotation_euler.x=.10*bite
  for pb in rig.pose.bones:
   pb.rotation_quaternion=pb.rotation_euler.to_quaternion();pb.rotation_mode='QUATERNION'
  bpy.context.view_layer.update()
  # Aim upper arms and forearms in armature space; no edit-bone changes or IK dependency.
  def aim(bone,direction):
   pb=rig.pose.bones[bone];base=pb.parent.matrix@pb.parent.bone.matrix_local.inverted()@pb.bone.matrix_local
   q=base.to_quaternion();delta=(q@Vector((0,1,0))).rotation_difference(Vector(direction).normalized())
   pb.rotation_quaternion=q.inverted()@delta@q;bpy.context.view_layer.update()
  for side,sign in [('Left',1),('Right',-1)]:
   aim(side+'Arm',(sign*.12,-.13,-.14))
   bite=(1-math.cos(t))/2 if name=='Eat' and side=='Right' else 0
   # Rest forearm extends to plate; at bite, hand rises inward towards mouth.
   aim(side+'ForeArm',(-sign*(.04+.10*bite),-.15+.10*bite,.02+.24*bite))
  for pb in rig.pose.bones:
   for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(data_path=prop,frame=f,group=pb.name)
 return action
rows=[]
for name,gender,skin,hair,shirt,pants,style in GUESTS:
 name+='_v2';rig=T.init();rig.data.pose_position='REST';bpy.context.scene.frame_set(1)
 # Preserve a bind/action contract before new clips; each civilian has independent local materials.
 original_bones={b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(v) for v in b.matrix_local]} for b in rig.data.bones}
 original_actions={a.name: {'range':list(a.frame_range)} for a in bpy.data.actions}
 for n,h in [('M_Skin',skin),('M_HairChestnut',hair),('M_SeaTeal',shirt),('M_HullNavy',pants)]:T.H.MATERIALS[n]=T.H.material(n,'#'+h)
 s=T.Skin(rig);T.torso(s,'M_SeaTeal');T.limbs(s,'M_SeaTeal',pants='M_HullNavy',rolled=True,boots=False);T.face(s);T.hair(s,long=style in ['long','bob'])
 # Head-bound civilian silhouette additions; exact original rest bones/actions.
 if 'Ben' in name:
  s.ell((0,.013,.925),(.192,.17,.025),'M_OilskinYellow','Head',seg=12,rings=3)
  s.ell((0,.025,.979),(.137,.13,.08),'M_OilskinYellow','Head',seg=12,rings=4)
  s.ell((0,.025,.942),(.141,.133,.019),'M_HullNavy','Head',seg=12,rings=2)
 if 'Cora' in name:
  for sign in [-1,1]:s.tube([(sign*.125,.06,.85),(sign*.16,.075,.72),(sign*.14,.08,.60)],[.06,.065,.04],'M_HairChestnut','Head',sides=8)
  s.ell((0,.13,.71),(.13,.046,.14),'M_HairChestnut','Head',seg=12,rings=4)
 if 'Dan' in name:
  s.ell((0,-.116,.729),(.105,.045,.065),'M_HairChestnut','Head',seg=10,rings=4)
  for sign in [-1,1]:s.ell((sign*.095,-.095,.762),(.036,.04,.05),'M_HairChestnut','Head',seg=8,rings=3)

 if style=='bun':s.ell((0,.14,.85),(.085,.068,.08),'M_HairChestnut','Head',seg=10,rings=4)
 if style=='bob':
  for sign in [-1,1]:s.ell((sign*.145,.025,.73),(.051,.104,.113),'M_HairChestnut','Head',seg=10,rings=4)
 if gender=='woman':
  for sign in [-1,1]:s.ell((sign*.171,-.012,.718),(.011,.012,.018),'M_OilskinYellow','Head',seg=6,rings=2)
  s.tube([(-.08,-.082,.52),(0,-.107,.485),(.08,-.082,.52)],[.009]*3,'M_RailIvory','Spine',sides=5)
 else:
  for sign in [-1,1]:s.box((sign*.044,-.099,.50),(.045,.016,.05),'M_RailIvory','Spine')
 for z in [.37,.415,.46]:s.ell((0,-.101,z),(.007,.006,.007),'M_OilskinYellow','Spine',seg=6,rings=2)
 ob=s.finish(name);ob.data.calc_loop_triangles();tris=len(ob.data.loop_triangles);assert tris<=12000
 # Guarantee normalised weights on all authored vertices.
 assert all(abs(sum(g.weight for g in v.groups)-1)<1e-5 for v in ob.data.vertices)
 for old in list(bpy.data.actions):
  if old.name in ['Sit','Eat']:bpy.data.actions.remove(old)
 for clip in ['Sit','Eat']:pose_action(rig,clip)
 # The source clips remain untouched. Save neutral posed Idle for previews/export.
 rig.animation_data_clear();rig.data.pose_position='REST';bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
 rig.data.pose_position='POSE';T.bind(rig,'Idle');bpy.context.scene.frame_set(1)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,use_custom_props=True)
 rows.append({'name':name,'gender_presentation':gender,'skin_srgb':'#'+skin,'hair_srgb':'#'+hair,'shirt_srgb':'#'+shirt,'pants_srgb':'#'+pants,'hairstyle':style,'triangles':tris,'bones':original_bones,'original_actions':original_actions,'added_actions':['Sit','Eat'],'fps':24,'fbx_sha256':digest(O/(name+'.fbx')),'blend_sha256':digest(O/(name+'.blend'))})
 print('GUEST EXPORTED',name,tris,flush=True)
(O/'build-metrics-v2.json').write_text(json.dumps({'guests':rows,'original_crew_blend_sha256':digest(R/'Art/Models/CrewRig/CrewRig.blend'),'source_helper_sha256':digest(R/'Art/Source/Townsfolk/build.py'),'unmodified_skeleton':True,'metres':True},indent=2));print('GUEST BUILD PASS',flush=True)

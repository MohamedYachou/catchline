"""Additive restaurant animation. Never modifies a mesh or existing action."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Quaternion
O=Path(__file__).resolve().parent
baseline=O/'_workclips-backup/CrewRig_Restaurant.blend'
bpy.ops.wm.open_mainfile(filepath=str(baseline if baseline.exists() else O/'CrewRig_Restaurant.blend'))
bpy.context.preferences.filepaths.save_version=0
sc=bpy.context.scene;sc.render.fps=24;rig=bpy.data.objects['CrewRig'];rig.animation_data_clear();rig.animation_data_create();rig.data.pose_position='POSE'
CLIPS=[('Cook',49,True),('Chop',25,True),('Pour',49,True),('Wipe',49,True),('Wash',49,True),('Repair',49,True),('Greet',61,False),('CarryPlate',25,True),('TakeOrder',49,True)]
# Rebuild only this assignment's additive actions when rerun after temporary backup cleanup.
for a in list(bpy.data.actions):
 if a.name.split('|')[-1] in [x[0] for x in CLIPS]:bpy.data.actions.remove(a)
walk=next(a for a in bpy.data.actions if a.name.split('|')[-1]=='Walk')
def bind(a):
 rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
def reset():
 for p in rig.pose.bones:p.rotation_mode='QUATERNION';p.rotation_quaternion=Quaternion();p.location=(0,0,0);p.scale=(1,1,1)
 bpy.context.view_layer.update()
def orient(n,d):
 p=rig.pose.bones[n];desired=Vector(d).to_track_quat('Y','Z');parent=p.parent.matrix.to_quaternion() if p.parent else Quaternion();rest=(p.parent.bone.matrix_local.inverted()@p.bone.matrix_local).to_quaternion() if p.parent else p.bone.matrix_local.to_quaternion();p.rotation_quaternion=rest.inverted()@parent.inverted()@desired;bpy.context.view_layer.update()
def limb(upper,lower,target,pole):
 p=rig.pose.bones[upper];start=p.head.copy();end=Vector(target);v=end-start;dist=min(max(v.length,.015),p.length+rig.pose.bones[lower].length-.001);d=v.normalized();a=p.length;b=rig.pose.bones[lower].length;x=(a*a-b*b+dist*dist)/(2*dist);off=Vector(pole)-start;off-=d*off.dot(d)
 elbow=start+d*x+off.normalized()*math.sqrt(max(0,a*a-x*x));orient(upper,elbow-start);orient(lower,end-rig.pose.bones[lower].head)
def hand(side,target,pole,aim=(0,-1,0)):
 limb(side+'Arm',side+'ForeArm',target,pole);orient(side+'Hand',aim)
walkposes=[]
bind(walk)
for frame in range(1,26):
 sc.frame_set(frame);walkposes.append({p.name:(p.location.copy(),p.rotation_quaternion.copy(),p.scale.copy()) for p in rig.pose.bones})
rig.animation_data.action=None
metrics=[]
for name,end,loop in CLIPS:
 action=bpy.data.actions.new(name);action.use_fake_user=True;action['loop']=loop;action['fps']=24;bind(action)
 for frame in range(1,end+1):
  t=(frame-1)/(end-1);w=math.sin(t*math.tau);c=math.cos(t*math.tau);fast=math.sin(t*math.tau*2);pulse=math.sin(t*math.pi)**2
  reset()
  # Work happens at chest/waist height, all workers face source -Y.
  left=(.13,-.18,.48);right=(-.13,-.19,.48);la=(0,-1,0);ra=(0,-1,0)
  if name=='Cook':
   left=(.13,-.19,.46);right=(-.06+.045*c,-.205+.03*w,.49+.012*fast);ra=(.15*c,-1,-.2)
  elif name=='Chop':
   left=(.095,-.215,.445);right=(-.09,-.215,.46+.085*(.5+.5*fast));ra=(0,-1,-.20)
  elif name=='Pour':
   lift=.5-.5*c;left=(.08,-.21,.46);right=(-.07-.055*lift,-.18,.47+.17*lift);ra=(.3*lift,-.6,-.8*lift)
  elif name=='Wipe':
   rig.pose.bones['Spine'].rotation_quaternion=Quaternion((1,0,0),.12);left=(.13,-.10,.38);right=(-.08+.105*w,-.23+.025*c,.425);ra=(0,-1,-.2)
  elif name=='Wash':
   left=(.065+.015*c,-.22,.43+.018*w);right=(-.065-.015*c,-.22,.43-.018*w);la=(0,-1,-.3);ra=(0,-1,-.3)
  elif name=='Repair':
   rig.pose.bones['Hips'].location.z=-.095;rig.pose.bones['Spine'].rotation_quaternion=Quaternion((1,0,0),.23);bpy.context.view_layer.update()
   for side,s in [('Left',1),('Right',-1)]:
    limb(side+'UpLeg',side+'Leg',(s*.085,0,.075),(s*.1,-.3,.17));orient(side+'Foot',(0,-.10,-.02))
   left=(.12,-.18,.30);right=(-.12,-.17,.32+.105*(.5+.5*w));ra=(0,-1,-.25)
  elif name=='Greet':
   bow=math.sin(min(t/.48,1)*math.pi)**2 if t<.48 else 0;opening=math.sin(max(0,(t-.35)/.65)*math.pi)**2
   rig.pose.bones['Spine'].rotation_quaternion=Quaternion((1,0,0),.24*bow);rig.pose.bones['Head'].rotation_quaternion=Quaternion((1,0,0),.10*bow)
   left=(.19+.13*opening,-.06-.09*opening,.31+.18*opening);right=(-.13,-.05-.12*bow,.31+.13*bow);la=(.8*opening,-.35,-.7+opening);ra=(0,-1,-.2)
  elif name=='CarryPlate':
   for p in rig.pose.bones:p.location,p.rotation_quaternion,p.scale=walkposes[frame-1][p.name]
   left=(.10,-.22,.515);right=(-.10,-.22,.515);la=ra=(0,-1,0)
  elif name=='TakeOrder':
   left=(.095,-.21,.495);right=(-.015+.014*fast,-.20+.01*c,.515+.008*w);la=(0,-1,.1);ra=(.5,-1,-.4);rig.pose.bones['Head'].rotation_quaternion=Quaternion((1,0,0),.08)
  bpy.context.view_layer.update()
  hand('Left',left,(.30,-.03,.29),la);hand('Right',right,(-.30,-.03,.29),ra)
  for p in rig.pose.bones:
   for prop in ['rotation_quaternion','location','scale']:p.keyframe_insert(prop,frame=frame,group=p.name)
 action.use_frame_range=True;action.frame_start=1;action.frame_end=end;metrics.append({'name':name,'frames':[1,end],'duration_s':(end-1)/24,'fps':24,'loop':loop})
rig.animation_data.action=None;reset();bind(next(a for a in bpy.data.actions if a.name.split('|')[-1]=='Idle'));sc.frame_set(13)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CrewRig_Restaurant.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
 if ob.type in ['MESH','ARMATURE']:ob.hide_set(False);ob.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True,use_custom_props=True)
(O/'workclips-manifest.json').write_text(json.dumps({'clips':metrics,'fbx_sha256':hashlib.sha256((O/'CrewRig_Restaurant.fbx').read_bytes()).hexdigest(),'prop_contract':'External props attach to unchanged LeftHand/RightHand; no new meshes in rig.'},indent=2));print('WORKCLIPS BUILD PASS',flush=True)

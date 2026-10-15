"""Task06: deterministic chibi rig, outfits, rigid hats and 24fps animation library.
Windows Blender 5.2 --background --factory-startup --python this-file.
Source axes X right,-Y forward,Z up. No Unity APIs; previous crew untouched.
"""
import bpy, math, json, sys, importlib.util
from pathlib import Path
from mathutils import Vector, Quaternion
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/CrewRig'; PRE=OUT/'Previews'; FBX=ROOT/'Assets/Art/Models/Crew/CrewRig.fbx'
for p in (OUT,PRE,FBX.parent):p.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('helpers',Path(__file__).with_name('build_crab_coast_props.py'))
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.render.fps=24
B.PALETTE.update({'M_Skin':'#B9784B','M_OilskinYellow':'#E6AD38','M_HairChestnut':'#50392E','M_HairSilver':'#ADB6AF'})
B.MATERIALS.update({k:B.material(k,v) for k,v in B.PALETTE.items()})
COL=bpy.data.collections.new('CREW_EXPORT');scene.collection.children.link(COL)
arm=bpy.data.objects.new('CrewRig',bpy.data.armatures.new('CrewSkeleton'));COL.objects.link(arm)
bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
def bone(n,a,b,parent=None):
 e=arm.data.edit_bones.new(n);e.head=a;e.tail=b
 if parent:e.parent=arm.data.edit_bones[parent]
 return e
bone('Hips',(0,0,.29),(0,0,.37))
bone('Spine',(0,0,.37),(0,0,.45),'Hips');bone('Spine1',(0,0,.45),(0,0,.53),'Spine')
bone('Neck',(0,0,.53),(0,0,.60),'Spine1');bone('Head',(0,0,.60),(0,0,.89),'Neck');bone('HatMount',(0,0,.90),(0,0,.97),'Head')
for side,s in [('Left',1),('Right',-1)]:
 bone(side+'Shoulder',(s*.045,0,.51),(s*.15,0,.51),'Spine1')
 bone(side+'Arm',(s*.15,0,.51),(s*.28,0,.51),side+'Shoulder')
 bone(side+'ForeArm',(s*.28,0,.51),(s*.39,0,.51),side+'Arm')
 bone(side+'Hand',(s*.39,0,.51),(s*.46,0,.51),side+'ForeArm')
 bone(side+'UpLeg',(s*.085,0,.31),(s*.085,0,.18),'Hips')
 bone(side+'Leg',(s*.085,0,.18),(s*.085,0,.075),side+'UpLeg')
 bone(side+'Foot',(s*.085,0,.075),(s*.085,-.10,.055),side+'Leg')
bpy.ops.object.mode_set(mode='OBJECT')
class Skin:
 def __init__(self):self.g=B.Geometry();self.w=[]
 def add(self,bone,method,*args):
  a=len(self.g.vertices);getattr(self.g,method)(*args);self.w.extend([{bone:1} for _ in self.g.vertices[a:]])
 def ell(self,b,c,r,m,seg=20,rings=10):self.add(b,'ellipsoid',c,r,seg,rings,m)
 def tube(self,b,path,r,m):self.add(b,'tube',path,r,16,m)
 def mesh(self,n):
  ob=self.g.object(n,arm,COL)
  for bn in arm.data.bones:ob.vertex_groups.new(name=bn.name)
  for i,w in enumerate(self.w):
   for bn,v in w.items():ob.vertex_groups[bn].add([i],v,'REPLACE')
  mod=ob.modifiers.new('SharedRig','ARMATURE');mod.object=arm
  for f in ob.data.polygons:f.use_smooth=True
  return ob
body=Skin()
body.ell('Head',(0,0,.76),(.173,.151,.19),'M_Skin',28,16)
body.ell('Neck',(0,0,.565),(.055,.05,.065),'M_Skin')
body.ell('Spine',(0,0,.427),(.14,.095,.14),'M_HullNavy')
body.ell('Hips',(0,0,.31),(.135,.092,.07),'M_HullNavy')
body.ell('Head',(0,-.15,.745),(.023,.030,.026),'M_Skin')
body.tube('Head',[(-.029,-.148,.707),(0,-.158,.698),(.029,-.148,.707)],[.004,.004,.004],'M_Rubber')
for s,side in [(1,'Left'),(-1,'Right')]:
 body.ell('Head',(s*.166,0,.745),(.030,.025,.043),'M_Skin')
 body.ell('Head',(s*.061,-.141,.774),(.013,.009,.022),'M_Rubber',16,8)
 body.ell('Head',(s*.066,-.137,.805),(.025,.009,.008),'M_HairChestnut',16,6)
 body.ell('Head',(s*.066,-.150,.783),(.004,.003,.005),'M_RailIvory',12,6)
 body.tube(side+'Arm',[(s*.143,0,.51),(s*.21,0,.51),(s*.28,0,.51)],[.061,.055,.049],'M_HullNavy')
 body.tube(side+'ForeArm',[(s*.28,0,.51),(s*.34,0,.51),(s*.39,0,.51)],[.049,.044,.037],'M_HullNavy')
 body.ell(side+'Hand',(s*.422,0,.51),(.047,.043,.041),'M_Skin')
 body.ell(side+'Hand',(s*.408,-.036,.486),(.022,.025,.022),'M_Skin')
 body.tube(side+'UpLeg',[(s*.085,0,.32),(s*.085,0,.25),(s*.085,0,.18)],[.066,.06,.052],'M_HullNavy')
 body.tube(side+'Leg',[(s*.085,0,.18),(s*.085,0,.10)],[.052,.047],'M_HullNavy')
 body.ell(side+'Foot',(s*.085,-.031,.052),(.065,.101,.052),'M_Rubber')
 # broad soft hair locks around scalp, leaving readable face
for i in range(11):
 a=math.tau*i/11
 body.ell('Head',(.139*math.cos(a),.115*math.sin(a),.874+(.014 if i%2 else 0)),(.059,.052,.061),'M_HairChestnut',16,8)
body.ell('Head',(0,.012,.906),(.112,.104,.043),'M_HairChestnut')
Body=body.mesh('Body')
# Clamp top hair to the same 0.95m sole-to-scalp reference.
for v in Body.data.vertices:v.co.z=min(v.co.z,.95)
# Two-bone blended sleeve seam: smooth articulation without automatic-weight ambiguity.
for ob in [Body]:
 for v in ob.data.vertices:
  if .25<abs(v.co.x)<.31 and .45<v.co.z<.57:
   side='Left' if v.co.x>0 else 'Right';w=max(0,min(1,(abs(v.co.x)-.25)/.06))
   for group in ob.vertex_groups:group.remove([v.index])
   ob.vertex_groups[side+'Arm'].add([v.index],1-w,'REPLACE');ob.vertex_groups[side+'ForeArm'].add([v.index],w,'REPLACE')
outfits=[]
for role,col in [('Captain','M_HullNavy'),('Deckhand','M_OilskinYellow'),('Fisherman','M_SafetyOrange'),('Veteran','M_HullNavy')]:
 sk=Skin();sk.ell('Spine',(0,0,.423),(.147,.102,.138),col)
 sk.ell('Hips',(0,0,.31),(.141,.099,.071),col)
 for s,side in [(1,'Left'),(-1,'Right')]:
  sk.tube(side+'UpLeg',[(s*.085,0,.31),(s*.085,0,.245),(s*.085,0,.171)],[.069,.064,.055],col)
 if role in ('Deckhand','Fisherman'):
  sk.add('Spine1','box',(0,-.102,.459),(.19,.014,.13),col)
  for s in (-1,1):
   sk.add('Spine1','beam',(s*.086,-.079,.515),(s*.074,-.109,.431),.023,.012,col)
   sk.ell('Spine1',(s*.074,-.119,.443),(.009,.005,.009),'M_Steel',12,6)
  sk.add('Spine','box',(0,-.111,.378),(.085,.009,.047),col)
 if role=='Captain':
  for s in (-1,1):
   sk.add('Spine1','beam',(s*.024,-.099,.51),(s*.053,-.109,.455),.03,.009,'M_RailIvory')
   for z in (.386,.429,.469):sk.ell('Spine',(s*.047,-.108,z),(.008,.005,.008),'M_OilskinYellow',12,6)
 if role=='Fisherman':
  sk.ell('Neck',(0,.054,.548),(.101,.055,.043),'M_SafetyOrange')
 if role=='Veteran':
  for x in (-.09,-.045,0,.045,.09):
   for i in range(5):sk.ell('Spine',(x+(.006 if i%2 else -.006),-.102,.35+i*.031),(.009,.006,.019),'M_HullBlue' if 'M_HullBlue' in B.MATERIALS else 'M_HullNavy',12,6)
  sk.ell('Head',(0,-.123,.639),(.113,.052,.07),'M_HairSilver')
  for s in (-1,1):sk.ell('Head',(s*.041,-.165,.710),(.046,.020,.018),'M_HairSilver')
 outfits.append(sk.mesh('Outfit_'+role))
# Rigid HatMount children maintain common local seat across outfit choices.
hats=[]
for n in ('CaptainCap','Beanie','Hood'):
 sk=Skin()
 if n=='CaptainCap':
  sk.ell('HatMount',(0,0,.952),(.183,.155,.068),'M_RailIvory')
  sk.ell('HatMount',(0,0,.915),(.173,.15,.027),'M_HullNavy')
  sk.ell('HatMount',(0,-.126,.913),(.145,.093,.018),'M_HullNavy')
  sk.ell('HatMount',(0,-.153,.955),(.018,.006,.023),'M_OilskinYellow',12,6)
 elif n=='Beanie':
  sk.ell('HatMount',(0,0,.948),(.176,.15,.088),'M_SafetyOrange')
  sk.ell('HatMount',(0,0,.914),(.182,.157,.029),'M_SafetyOrange')
  sk.ell('HatMount',(0,0,1.043),(.032,.032,.032),'M_SafetyOrange')
 else:
  # Editable double-sided open-front hood shell; back half of head only.
  rows=[(.69,.17,.145),(.76,.212,.208),(.87,.224,.220),(.96,.188,.182),(1.008,.083,.083)]
  verts=[]
  for inner in (False,True):
   for z,rx,ry in rows:
    for i in range(17):
     a=math.pi*i/16
     verts.append(((rx-(.014 if inner else 0))*math.cos(a),-.012+(ry-(.014 if inner else 0))*math.sin(a),z))
  faces=[];offset=len(rows)*17
  for k in (0,offset):
   for row in range(len(rows)-1):
    for i in range(16):
     a=k+row*17+i;f=(a,a+1,a+18,a+17)
     faces.append(f if k==0 else tuple(reversed(f)))
  for i in range(16):
   faces.append((i,i+offset,i+offset+1,i+1))
   a=(len(rows)-1)*17+i;faces.append((a,a+1,a+offset+1,a+offset))
  for i in (0,16):
   for row in range(len(rows)-1):
    a=row*17+i;faces.append((a,a+17,a+17+offset,a+offset))
  sk.g.add(verts,faces,'M_OilskinYellow')
 ob=sk.g.object('Hat_'+n,None,COL)
 for p in ob.data.polygons:p.use_smooth=True
 world=ob.matrix_world.copy();ob.parent=arm;ob.parent_type='BONE';ob.parent_bone='HatMount';ob.matrix_world=world
 hats.append(ob)
# Authored exaggerated in-place animation; all bones are keyed every frame.
CLIPS=[('Idle',49,True),('Walk',25,True),('Carry',25,True),('Bait',49,True),('Cast',33,False),('Wait',49,True),('Strike',19,False),('Reel',25,True),('Row',49,True),('Cheer',49,False),('Stow',49,False)]
def orient(n,d):
 p=arm.pose.bones[n]; desired=Vector(d).to_track_quat('Y','Z')
 parent=p.parent.matrix.to_quaternion() if p.parent else Quaternion()
 rest=(p.parent.bone.matrix_local.inverted()@p.bone.matrix_local).to_quaternion() if p.parent else p.bone.matrix_local.to_quaternion()
 p.rotation_quaternion=rest.inverted()@parent.inverted()@desired
 bpy.context.view_layer.update()
def pose(name,t):
 for p in arm.pose.bones:p.rotation_mode='QUATERNION';p.rotation_quaternion=Quaternion();p.location=(0,0,0);p.scale=(1,1,1)
 wave=math.sin(t*math.tau);pulse=math.sin(t*math.pi)
 arm.pose.bones['Hips'].location.z=.005*wave
 if name in ('Walk','Carry'):arm.pose.bones['Hips'].location.z=.012*(1-math.cos(t*math.tau*2))
 lean=0
 if name=='Stow':lean=.72*math.sin(math.pi*t)**2
 if name=='Cast':lean=-.20*math.sin(math.pi*t*2)
 if name=='Strike':lean=-.30*math.sin(math.pi*t)
 arm.pose.bones['Spine'].rotation_quaternion=Quaternion((1,0,0),lean)
 arm.pose.bones['Head'].rotation_quaternion=Quaternion((0,0,1),.025*wave)
 bpy.context.view_layer.update()
 for s,side in [(1,'Left'),(-1,'Right')]:
  upper=(s*.12,0,-.18);lower=(s*.025,-.015,-.11)
  if name=='Idle':upper=(s*.09,.008*wave,-.19)
  if name=='Walk':
   upper=(s*.07,s*.11*wave,-.17);lower=(0,-.02,-.11)
  if name=='Carry':upper=(s*.04,-.10,-.13);lower=(-s*.045,-.12,.045)
  if name in ('Bait','Wait','Reel','Strike'):
   upper=(s*.045,-.10,-.09);lower=(-s*.045,-.10,.07)
   if name=='Bait':lower=(-s*.05,-.09,.045+.024*wave*s)
   if name=='Wait':lower=(-s*.045,-.10,.07+.005*wave)
   if name=='Reel' and s==-1:lower=(.015+.025*math.cos(t*math.tau),-.10+.025*wave,.06+.035*wave)
   if name=='Strike':upper=(s*.04,-.09,-.09+.15*pulse);lower=(-s*.025,-.08,.08)
  if name=='Cast':
   q=(math.sin(math.pi*t*2-.5)+1)/2
   upper=(s*.03,-.08+.10*q,.14*q-.08);lower=(-s*.025,-.11+.12*q,.12)
  if name=='Row':
   upper=(s*.09,-.06+.08*wave,-.08);lower=(s*.05,-.11,.015+.025*wave)
   arm.pose.bones['Hips'].location.z=-.15
  if name=='Cheer':upper=(s*(.11-.045*pulse),0,-.18+.34*pulse);lower=(s*.03,0,-.1+.23*pulse)
  if name=='Stow':upper=(s*.04,-.10,-.12);lower=(-s*.035,-.11,-.02-.07*pulse)
  orient(side+'Arm',upper);orient(side+'ForeArm',lower);orient(side+'Hand',lower)
  leg=.48*s*wave if name in ('Walk','Carry') else 0
  if name=='Row':leg=-1.20
  arm.pose.bones[side+'UpLeg'].rotation_quaternion=Quaternion((1,0,0),leg)
  arm.pose.bones[side+'Leg'].rotation_quaternion=Quaternion((1,0,0),max(0,-s*wave)*.55 if name in ('Walk','Carry') else (1.05 if name=='Row' else 0))
 bpy.context.view_layer.update()
arm.animation_data_create()
for name,end,loop in CLIPS:
 action=bpy.data.actions.new(name);action.use_fake_user=True;arm.animation_data.action=action
 action['loop']=loop;action['fps']=24
 for frame in range(1,end+1):
  pose(name,(frame-1)/(end-1))
  for p in arm.pose.bones:
   p.keyframe_insert('rotation_quaternion',frame=frame,group=p.name);p.keyframe_insert('location',frame=frame,group=p.name);p.keyframe_insert('scale',frame=frame,group=p.name)
 action.use_frame_range=True;action.frame_start=1;action.frame_end=end
arm.animation_data.action=None;pose('Idle',0)
# Export every outfit/hat as requested; consumer chooses one combination.
bpy.ops.object.select_all(action='DESELECT')
for ob in COL.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,use_custom_props=True,mesh_smooth_type='FACE')
# Source saves include all variants; preview stage excluded from export.
for o in outfits+hats:o.hide_render=True
outfits[1].hide_render=False;hats[1].hide_render=False
B.preview_stage(scene,[Body,outfits[1],hats[1]])
scene.render.engine='CYCLES';scene.cycles.samples=12
scene.render.resolution_x=scene.render.resolution_y=400
scene.camera.data.ortho_scale=1.5
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CrewRig.blend'))
meta={'height_bare_scalp_m':.95,'fps':24,'bones':[b.name for b in arm.data.bones],'skinned_meshes':[Body.name]+[o.name for o in outfits],'hats':[o.name for o in hats],'new_materials':{'M_HairChestnut':'#50392E','M_HairSilver':'#ADB6AF'},'clips':[{'name':n,'start':1,'end':e,'loop':l} for n,e,l in CLIPS]}
(OUT/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
def render(path):scene.render.filepath=str(PRE/path);bpy.ops.render.render(write_still=True)
for i,ob in enumerate(outfits):
 for o in outfits+hats:o.hide_render=True
 ob.hide_render=False;hats[0 if i==0 else 1 if i in (1,3) else 2].hide_render=False
 arm.animation_data.action=None;pose('Idle',0)
 for angle,label in [(0,'front'),(90,'right'),(180,'back'),(270,'left')]:
  a=math.radians(angle);target=Vector((0,0,.52));scene.camera.location=target+Vector((3*math.sin(a),-3*math.cos(a),.65));scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler()
  render(ob.name+'-'+label+'.png')
for o in outfits+hats:o.hide_render=True
outfits[1].hide_render=False;hats[1].hide_render=False
scene.camera.location=(2.2,-3.14,3.52);target=Vector((0,0,.5));scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=1.55
for name,end,loop in CLIPS:
 arm.animation_data.action=bpy.data.actions[name]
 for j,f in enumerate([1,1+(end-1)//3,1+2*(end-1)//3]):
  scene.frame_set(f);render(name+'-'+str(j+1)+'.png')
print('CREW BUILD COMPLETE')

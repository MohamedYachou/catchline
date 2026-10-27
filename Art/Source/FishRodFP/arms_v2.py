"""Optional FISH-ARMS-2 authoring; never replaces v1 or rod-only.
Two-link IK is solved and baked per frame. Fixed shoulders, independent hand
targets follow rod/root and upright crank respectively. Source -Y forward/Z up.
"""
import bpy,math,json,hashlib
from mathutils import Vector,Matrix
from mathutils.kdtree import KDTree
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/FishRodFP';V=O/'arms-v2';V.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected={p.name:sha(p) for p in O.iterdir() if p.is_file() and p.suffix in ('.blend','.fbx','.png') and not p.name.startswith('FishRodFP_ArmsV2')}
M=json.loads((O/'build-manifest.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(O/'FishRodFP_RodOnly.blend'));bpy.context.preferences.filepaths.save_version=0
sc=bpy.context.scene;rig=bpy.data.objects['FishRodFP_Rig'];body=bpy.data.objects['FishRodFP_Mesh'];data=rig.data
rig.animation_data.action=None
for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4)
for v in body.data.vertices:v.co.x=-v.co.x
for p in body.data.polygons:p.flip()
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
for b in data.edit_bones:
 h=b.head.copy();t=b.tail.copy();h.x=-h.x;t.x=-t.x;b.head=h;b.tail=t
def bone(n,h,t,parent=None,deform=True):
 b=data.edit_bones.new(n);b.head=h;b.tail=t;b.use_deform=deform
 if parent:b.parent=data.edit_bones[parent]
 return b
bone('ArmRoot',(.34,.85,-.16),(.34,.85,-.04),deform=False)
KNOB=Vector((.160,.073,-.202));D=Vector((0,-.956304756,.292371705));UP=Vector((0,.292371705,.956304756))
W={'R':Vector((-.061,.002,-.025)),'L':KNOB+Vector((.015,.11,-.005))}
S={'R':Vector((.09,.70,-.16)),'L':Vector((.59,.70,-.16))}
lengths={'R':(.51,.48),'L':(.60,.56)}
poles={'R':Vector((-.62,.38,-.52)),'L':Vector((.97,.39,-.52))}
def elbow(side,w):
 s=S[side];a,b=lengths[side];d=w-s;r=d.length;assert abs(a-b)<r<a+b,(side,r,a+b)
 d.normalize();x=(a*a-b*b+r*r)/(2*r);h=math.sqrt(max(0,a*a-x*x))
 p=poles[side]-s;v=(p-d*p.dot(d)).normalized()
 return s+d*x+v*h
E={side:elbow(side,W[side]) for side in W}
for side in ['R','L']:
 bone('UpperArm.'+side,S[side],E[side],'ArmRoot')
 bone('Forearm.'+side,E[side],W[side],'UpperArm.'+side)
 palm=D*.10+Vector((-.045,.01,.005)) if side=='R' else KNOB+Vector((0,.045,.005))
 bone('Hand.'+side,W[side],palm,'ArmRoot')
 bone('WristTarget.'+side,W[side],W[side]+Vector((0,0,.07)),'ArmRoot',False)
 bone('ElbowPole.'+side,poles[side],poles[side]+Vector((0,0,.07)),'ArmRoot',False)
 for i in range(3):
  a=D*(.078+.029*i)+Vector((-.025,0,.022)) if side=='R' else KNOB+Vector((-.023+.023*i,.022,.026))
  bone('Fingers%d.%s'%(i+1,side),a,a+Vector((.035,0,-.018)),'Hand.'+side)
 a=D*.055+Vector((-.038,0,-.012)) if side=='R' else KNOB+Vector((-.045,.02,-.02))
 bone('Thumb.'+side,a,a+Vector((.025,-.02,0)),'Hand.'+side)
bpy.ops.object.mode_set(mode='OBJECT')
for side in ['R','L']:
 for n in ['UpperArm','Forearm','Hand','WristTarget']:
  rig.pose.bones[n+'.'+side].rotation_mode='QUATERNION'
rig['description']='Optional anatomical arms: right cork support / left crank; fixed shoulders, two-link IK baked at40fps'
rig['arm_solver']='Reproducible analytic two-link IK; WristTarget and ElbowPole bones retained for reauthoring; no runtime constraints needed'
mat=body.data.materials[0];parts=[body];metrics={}
def mesh(n,verts,faces,col,weights):
 me=bpy.data.meshes.new(n);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(n,me);sc.collection.objects.link(o)
 me.materials.append(mat);uv=me.uv_layers.new(name='AtlasUV');u=(col%4+.5)/4;v=(col//4+.5)/4
 for l in uv.data:l.uv=(u,v)
 for p in me.polygons:p.use_smooth=True
 o.parent=rig;groups={}
 for i,co in enumerate(verts):
  ws={weights:1} if isinstance(weights,str) else weights(i,Vector(co))
  assert abs(sum(ws.values())-1)<1e-6 and len(ws)<=4
  for name,w in ws.items():
   if w<1e-6:continue
   if name not in groups:groups[name]=o.vertex_groups.new(name=name)
   groups[name].add([i],w,'REPLACE')
 mod=o.modifiers.new('Anatomical skin','ARMATURE');mod.object=rig;parts.append(o)
 metrics[n]=sum(len(p.vertices)-2 for p in me.polygons);return o
def loft(n,points,radii,col,weights,sides=10):
 ps=[Vector(p) for p in points];vv=[];ff=[];prev=None;pd=None
 for i,p in enumerate(ps):
  d=(ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]).normalized()
  if prev is None:
   a=d.cross(Vector((1,0,0)))
   if a.length<.05:a=d.cross(Vector((0,1,0)))
   a.normalize()
  else:a=(pd.rotation_difference(d)@prev).normalized()
  a=(a-d*a.dot(d)).normalized();b=d.cross(a);prev=a;pd=d
  rx,ry=radii[i] if isinstance(radii[i],tuple) else (radii[i],radii[i])
  for j in range(sides):vv.append(p+a*math.cos(j*2*math.pi/sides)*rx+b*math.sin(j*2*math.pi/sides)*ry)
 for i in range(len(ps)-1):
  for j in range(sides):k=i*sides+j;q=i*sides+(j+1)%sides;ff.append((k,q,q+sides,k+sides))
 ff.append(tuple(reversed(range(sides))));ff.append(tuple((len(ps)-1)*sides+j for j in range(sides)))
 return mesh(n,vv,ff,col,weights)
def tube(n,a,b,r,col,w,r2=None,sides=10):return loft(n,[a,b],[r,r if r2 is None else r2],col,w,sides)
def ell(n,c,rs,col,w,seg=12,rings=6):
 vv=[];ff=[];c=Vector(c)
 for i in range(1,rings):
  th=math.pi*i/rings
  for j in range(seg):
   ph=2*math.pi*j/seg;vv.append(c+Vector((rs[0]*math.sin(th)*math.cos(ph),rs[1]*math.sin(th)*math.sin(ph),rs[2]*math.cos(th))))
 for i in range(rings-2):
  for j in range(seg):a=i*seg+j;b=i*seg+(j+1)%seg;ff.append((a+seg,b+seg,b,a))
 top=len(vv);vv.append(c+Vector((0,0,rs[2])));bot=len(vv);vv.append(c-Vector((0,0,rs[2])))
 for j in range(seg):ff.append((top,j,(j+1)%seg));a=(rings-2)*seg+j;b=(rings-2)*seg+(j+1)%seg;ff.append((bot,b,a))
 return mesh(n,vv,ff,col,w)
for side in ['R','L']:
 s,e,w=S[side],E[side],W[side];f=(w-e).normalized();upper='UpperArm.'+side;fore='Forearm.'+side;hand='Hand.'+side
 points=[s,s.lerp(e,.25),s.lerp(e,.65),s.lerp(e,.9),e,e.lerp(w,.12),e.lerp(w,.28),e.lerp(w,.34),e.lerp(w,.4),e.lerp(w,.53),e.lerp(w,.59),e.lerp(w,.65),e.lerp(w,.78),w-f*.034]
 radii=[.095,.092,.086,.079,.077,.075,.071,.079,.067,.063,.070,.059,.053,.046]
 def ws(i,p):
  ring=i//10
  t={3:.15,4:.5,5:.85}.get(ring,0 if ring<4 else 1)
  return {upper:1-t,fore:t}
 loft('OilskinAnatomy.'+side,points,radii,0,ws)
 tube('RolledCuff.'+side,w-f*.054,w-f*.030,.052,1,fore,r2=.049)
 for j,dist in enumerate([.050,.039]):tube('CaptainStripe%d.%s'%(j,side),w-f*dist,w-f*(dist-.003),.0526 if j==0 else .0505,2,fore)
 tube('VisibleWrist.'+side,w-f*.032,w+f*.012,.034,6,hand,r2=.032)
 # Wrist and glove collar merge into palm, with a visible tan strip at cuff.
 palm=D*.10+Vector((-.045,.01,.005)) if side=='R' else KNOB+Vector((0,.045,.005))
 a=(palm-w).normalized();tube('GloveWelt.'+side,w+a*.011,w+a*.035,.035,3,hand,r2=.037)
 tube('GloveHeel.'+side,w+a*.032,palm,.034,2,hand,r2=.035)
 if side=='R':
  ell('Palm.R',palm,(.025,.047,.031),2,hand)
  ell('PalmSeam.R',palm+Vector((-.023,0,.003)),(.004,.033,.019),3,hand,10,4)
  for i in range(3):
   c=D*(.078+.029*i)
   ph=[math.pi,math.pi*.75,math.pi*.5,math.pi*.25,0,-math.pi*.22,-math.pi*.40]
   pts=[c+Vector((math.cos(p)*.031,0,0))+UP*(math.sin(p)*.031) for p in ph]
   loft('ClosedGripFingers%d.R'%(i+1),pts,[.011,.0115,.0115,.011,.0105,.010,.0075],2,'Fingers%d.R'%(i+1),8)
  pts=[D*.047+Vector((-.046,0,-.007)),D*.048+Vector((-.028,0,-.025)),D*.049+Vector((-.002,0,-.031)),D*.061+Vector((.015,0,-.024))]
  loft('OpposingThumb.R',pts,[.016,.015,.013,.010],2,'Thumb.R',8)
 else:
  ell('Palm.L',palm,(.042,.027,.034),2,hand)
  ell('PalmSeam.L',palm+Vector((0,.024,.005)),(.03,.004,.020),3,hand,10,4)
  for i in range(3):
   x=-.023+i*.023;pts=[KNOB+Vector((x,math.cos(p)*.027,math.sin(p)*.027)) for p in [0,math.pi*.28,math.pi*.55,math.pi*.82,math.pi,math.pi*1.2]]
   loft('ClosedCrankFingers%d.L'%(i+1),pts,[.011,.011,.011,.0105,.010,.0075],2,'Fingers%d.L'%(i+1),8)
  loft('OpposingThumb.L',[KNOB+Vector((-.041,.037,-.009)),KNOB+Vector((-.048,.012,-.025)),KNOB+Vector((-.030,-.007,-.031)),KNOB+Vector((-.010,-.011,-.025))],[.017,.016,.013,.009],2,'Thumb.L',8)
# Fuse overlapping glove shells into one continuous surface; nearest-source skin
# retains articulated finger groups. Welt remains a deliberately separate cuff.
for side in ['R','L']:
 glove=[p for p in parts if p.name.endswith('.'+side) and p.name.startswith(('GloveHeel','Palm','ClosedGrip','ClosedCrank','OpposingThumb'))]
 bpy.ops.object.select_all(action='DESELECT')
 for p in glove:p.select_set(True)
 bpy.context.view_layer.objects.active=glove[0];bpy.ops.object.join();o=bpy.context.object
 points=[v.co.copy() for v in o.data.vertices];skin=[{o.vertex_groups[g.group].name:g.weight for g in v.groups} for v in o.data.vertices]
 tree=KDTree(len(points))
 for i,p in enumerate(points):tree.insert(p,i)
 tree.balance()
 for mod in list(o.modifiers):o.modifiers.remove(mod)
 mod=o.modifiers.new('Continuous glove union','REMESH');mod.mode='VOXEL';mod.voxel_size=.002;mod.use_smooth_shade=True
 bpy.ops.object.modifier_apply(modifier=mod.name)
 o.data.calc_loop_triangles();count=len(o.data.loop_triangles)
 mod=o.modifiers.new('Deliberate low-poly glove','DECIMATE');mod.ratio=min(1,900/count)
 bpy.ops.object.modifier_apply(modifier=mod.name)
 for group in list(o.vertex_groups):o.vertex_groups.remove(group)
 for v in o.data.vertices:
  _,i,_=tree.find(v.co)
  for name,w in skin[i].items():
   group=o.vertex_groups.get(name) or o.vertex_groups.new(name=name);group.add([v.index],w,'REPLACE')
 uv=o.data.uv_layers.get('AtlasUV') or o.data.uv_layers.new(name='AtlasUV')
 for l in uv.data:l.uv=(.625,.125)
 for p in o.data.polygons:p.use_smooth=True
 mod=o.modifiers.new('Anatomical skin','ARMATURE');mod.object=rig
 parts=[body]+[p for p in sc.objects if p.type=='MESH' and p.parent==rig and p!=body]
 o.name='ContinuousGlove.'+side
# Bake authoring IK into existing actions. Source rig remains easy to re-solve.
def aim(name,h,t):
 b=data.bones[name];q=(b.tail_local-b.head_local).rotation_difference(t-h)@b.matrix_local.to_quaternion()
 rig.pose.bones[name].matrix=Matrix.Translation(h)@q.to_matrix().to_4x4()
maxerr=0;reach={side:[100,0] for side in W}
for name,clip in M['clips'].items():
 act=bpy.data.actions[name];rig.animation_data.action=act;previous={}
 for frame in range(clip['frames'][1]+1):
  sc.frame_set(frame);bpy.context.view_layer.update()
  root=rig.pose.bones['RodRoot'].matrix@data.bones['RodRoot'].matrix_local.inverted()
  crank=rig.pose.bones['ReelHandle'].matrix@data.bones['ReelHandle'].matrix_local.inverted()
  left=Matrix.Translation(crank@KNOB)@root.to_quaternion().to_matrix().to_4x4()@Matrix.Translation(-KNOB)
  for side,transform in [('R',root),('L',left)]:
   w=transform@W[side];e=elbow(side,w);reach[side]=[min(reach[side][0],(w-S[side]).length),max(reach[side][1],(w-S[side]).length)]
   aim('UpperArm.'+side,S[side],e);bpy.context.view_layer.update();aim('Forearm.'+side,e,w)
   rig.pose.bones['Hand.'+side].matrix=transform@data.bones['Hand.'+side].matrix_local
   rig.pose.bones['WristTarget.'+side].matrix=transform@data.bones['WristTarget.'+side].matrix_local
   bpy.context.view_layer.update();maxerr=max(maxerr,(rig.pose.bones['Forearm.'+side].tail-w).length)
   for stem in ['UpperArm','Forearm','Hand','WristTarget']:
    pb=rig.pose.bones[stem+'.'+side];q=pb.rotation_quaternion
    if pb.name in previous and previous[pb.name].dot(q)<0:q.negate()
    previous[pb.name]=q.copy()
    for prop in ['location','rotation_quaternion','scale']:pb.keyframe_insert(prop,frame=frame)
 assert maxerr<1e-5,maxerr
rig.animation_data.action=bpy.data.actions['Idle'];sc.frame_set(0)
metrics={}
for p in parts:
 p.data.calc_loop_triangles();metrics[p.name]=len(p.data.loop_triangles)
bpy.ops.object.select_all(action='DESELECT')
for p in parts:p.select_set(True)
bpy.context.view_layer.objects.active=body;bpy.ops.object.join();body=bpy.context.object;body.name='FishRodFP_ArmsV2_Mesh'
body.data.calc_loop_triangles();tri=len(body.data.loop_triangles);assert tri<8000,tri
assert len(body.data.materials)==1
rig.name='FishRodFP_ArmsV2_Rig'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'FishRodFP_ArmsV2.blend'))
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);body.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(O/'FishRodFP_ArmsV2.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,path_mode='RELATIVE',use_custom_props=True,mesh_smooth_type='FACE')
assert all(sha(O/n)==h for n,h in protected.items() if not n.startswith('FishRodFP_ArmsV2'))
manifest={'status':'AUTHORING PASS; FBX and visual review pending','triangles':tri,'new_arm_triangles':tri-3862,'bones':[b.name for b in data.bones],'clips':M['clips'],'fps':40,'atlas':M['atlas'],'camera_source':M['camera_source'],'shoulders_source':{s:list(p) for s,p in S.items()},'elbows_rest_source':{s:list(p) for s,p in E.items()},'wrists_source':{s:list(p) for s,p in W.items()},'arm_lengths_m':lengths,'sampled_reach_m':reach,'max_ik_wrist_error_m':maxerr,'crank_knob_source':list(KNOB),'handedness':'screen-right right hand cork; screen-left left hand crank; mirrored reel vs v1','per_part_triangles':metrics,'protected_original_hashes':protected,'authoring':'Analytic fixed-shoulder two-link IK baked each40fps frame; 3finger groups+thumb per hand. WristTarget and ElbowPole helper bones retained.'}
(V/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('ARMS V2 AUTHORING PASS',tri,maxerr)

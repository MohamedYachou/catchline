"""Reproducible first-person rod. Run from project root with Blender -b -P thisfile.
Source -Y forward, Z up (screen-right is -X in the review), metres.
FBX exporter axes: -Z forward / Y up; Unity import belongs to Codex 1.
Review stage is never selected for FBX export.
"""
import bpy, math, json, sys, argparse
from mathutils import Vector
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Art/Models/FishRodFP'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'renders').mkdir(exist_ok=True)
ap=argparse.ArgumentParser()
ap.add_argument('--render',default='preview',choices=['none','preview','all'])
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.unit_settings.system='METRIC'; sc.unit_settings.scale_length=1
sc.render.fps=40
sc.render.engine='CYCLES'; sc.cycles.samples=24
sc.cycles.use_denoising=True
sc.render.image_settings.file_format='PNG'
sc.view_settings.view_transform='AgX'
sc.world=bpy.data.worlds.new('Review sky'); sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.46,.64,.68,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.65

COLORS=['173F57','2A6685','E6AD38','C38C29','E36A35','C58B50','DFB77A','8C5A36',
        '28343B','8FA6AC','F3F0DC','64C7C4','168F9F','BAC9C6','F3DEA1','365563']
img=bpy.data.images.new('FishRodFP_Atlas',width=256,height=256,alpha=False)
pix=[]
for y in range(256):
 for x in range(256):
  h=COLORS[(y//64)*4+x//64]
  pix.extend([int(h[i:i+2],16)/255 for i in (0,2,4)]+[1])
img.pixels.foreach_set(pix)
img.filepath_raw=str(OUT/'FishRodFP_Atlas.png'); img.file_format='PNG'; img.save()
img.reload()
img.filepath='//FishRodFP_Atlas.png'
mat=bpy.data.materials.new('M_FishRodFP_Atlas'); mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.57
tex=mat.node_tree.nodes.new('ShaderNodeTexImage'); tex.image=img; tex.interpolation='Closest'
mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])

data=bpy.data.armatures.new('FishRodFP_Skeleton')
rig=bpy.data.objects.new('FishRodFP_Rig',data); sc.collection.objects.link(rig)
bpy.context.view_layer.objects.active=rig; rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
def bone(n,h,t,p=None):
 b=data.edit_bones.new(n); b.head=h; b.tail=t
 if p: b.parent=data.edit_bones[p]
 return b
bone('RodRoot',(0,0,0),(0,-.12,0))
D=Vector((0,-.956304756,.292371705))
def rodpos(s): return D*s
START=.16; END=1.82; SEG=(END-START)/8
for i in range(8):
 b=bone('Rod_%02d'%(i+1),rodpos(START+i*SEG),rodpos(START+(i+1)*SEG),
        'RodRoot' if i==0 else 'Rod_%02d'%i)
 if i: b.use_connect=True
bone('GripHand.L',(-.07,.02,-.02),(-.07,-.07,-.02),'RodRoot')
CRANK=Vector((.058,.025,-.16))
KNOB=CRANK+Vector((.102,.048,-.042))
bone('ReelHandle',CRANK,CRANK+Vector((.08,0,0)),'RodRoot')
bone('ReelSpool',(0,-.05,-.157),(0,-.12,-.157),'RodRoot')
bone('ReelHand.R',KNOB,KNOB+Vector((0,-.07,0)),'ReelHandle')
bone('LineTip',rodpos(END),rodpos(END)+Vector((0,-.035,0)),'Rod_08')
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front=True
for p in rig.pose.bones: p.rotation_mode='XYZ'
constraint=rig.pose.bones['ReelHand.R'].constraints.new('COPY_ROTATION')
constraint.name='Keep wrist upright while cranking'
constraint.target=rig;constraint.subtarget='RodRoot'
constraint.target_space='POSE';constraint.owner_space='POSE'
rig['description']='2.1m spinning rod; left cork support/right crank; eight progressive bend bones'
rig['bend_axis']='Rod_01..08 local X; positive bends tip downward'
rig['bend_radians_at_1']=json.dumps([.01,.035,.06,.09,.13,.17,.22,.26])
rig['reel_axis']='ReelHandle local Y, 0 to 2*pi per 0.8s; ReelSpool local Y'
PARTS=[]
def attach(o,col,weights='RodRoot',smooth=True):
 o.data.materials.clear(); o.data.materials.append(mat)
 uv=o.data.uv_layers.new(name='AtlasUV') if not o.data.uv_layers else o.data.uv_layers[0]
 u=(col%4+.5)/4; v=(col//4+.5)/4
 for l in uv.data: l.uv=(u,v)
 for p in o.data.polygons: p.use_smooth=smooth
 o.parent=rig
 groups={}
 for vert in o.data.vertices:
  ws={weights:1} if isinstance(weights,str) else weights(o.matrix_world@vert.co)
  for k,w in ws.items():
   if w<1e-7: continue
   if k not in groups: groups[k]=o.vertex_groups.new(name=k)
   groups[k].add([vert.index],w,'REPLACE')
 mod=o.modifiers.new('FishRodFP Skin','ARMATURE'); mod.object=rig
 PARTS.append(o)
 return o
def mesh(n,verts,faces,col,w='RodRoot',smooth=True):
 m=bpy.data.meshes.new(n); m.from_pydata(verts,[],faces); m.update()
 o=bpy.data.objects.new(n,m); sc.collection.objects.link(o)
 return attach(o,col,w,smooth)
def loft(n,points,radii,col,w='RodRoot',sides=10):
 ps=[Vector(p) for p in points]; vv=[]; ff=[];prev_d=None;prev_a=None
 for i,p in enumerate(ps):
  d=ps[min(i+1,len(ps)-1)]-ps[max(0,i-1)]
  d.normalize()
  if prev_d is None:
   a=d.cross(Vector((1,0,0)))
   if a.length<.05:a=d.cross(Vector((0,1,0)))
   a.normalize()
  else:
   a=prev_d.rotation_difference(d)@prev_a
   a=(a-d*a.dot(d)).normalized()
  b=d.cross(a).normalized();prev_d=d.copy();prev_a=a.copy()
  rad=radii[i]; rx,ry=rad if isinstance(rad,tuple) else (rad,rad)
  for j in range(sides): vv.append(p+a*math.cos(j*2*math.pi/sides)*rx+b*math.sin(j*2*math.pi/sides)*ry)
 for i in range(len(ps)-1):
  for j in range(sides):
   k=i*sides+j; q=i*sides+(j+1)%sides
   ff.append((k,q,q+sides,k+sides))
 ff.append(tuple(reversed(range(sides)))); ff.append(tuple((len(ps)-1)*sides+j for j in range(sides)))
 return mesh(n,vv,ff,col,w)
def tube(n,a,b,r,col,w='RodRoot',sides=10,r2=None):
 return loft(n,[a,b],[r,r if r2 is None else r2],col,w,sides)
def ell(n,loc,scale,col,w='RodRoot',segments=12,rings=6):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,location=loc)
 o=bpy.context.object; o.name=n; o.scale=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return attach(o,col,w)
def ring(n,center,r,wire,col,w='RodRoot',normal=(0,1,0),steps=16):
 c=Vector(center); d=Vector(normal).normalized(); a=d.cross(Vector((1,0,0)))
 if a.length<.1:a=d.cross(Vector((0,0,1)))
 a.normalize(); b=d.cross(a)
 ps=[c+r*(a*math.cos(j*2*math.pi/steps)+b*math.sin(j*2*math.pi/steps)) for j in range(steps+1)]
 return loft(n,ps,[wire]*len(ps),col,w,4)
def bendweights(p):
 # Cubic B-spline support makes weight derivatives continuous across bones.
 # Clamped endpoints keep the physical blank end exactly on LineTip.
 t=max(-1,min(8,(p.dot(D)-START)/(END-START)*9-1))
 i=math.floor(t);f=t-i
 ws=[(1-f)**3/6,(3*f**3-6*f*f+4)/6,
     (-3*f**3+3*f*f+3*f+1)/6,f**3/6]
 result={}
 for j,w in zip(range(i-1,i+3),ws):
  key='Rod_%02d'%(max(0,min(7,j))+1)
  result[key]=result.get(key,0)+w
 return result

# Continuous tapered blank, dense longitudinally, no hard weighting seams.
ss=[START+i*(END-START)/64 for i in range(65)]
loft('RodBlank',[rodpos(s) for s in ss],[.013*(1-(s-START)/(END-START))+.0025 for s in ss],0,bendweights,7)
for a,b,r,col,n in [(-.28,-.26,.023,8,'RubberButt'),(-.26,-.065,.022,5,'RearCork'),
                    (-.065,.07,.021,8,'ReelSeat'),(.07,.16,.020,5,'ForeCork'),
                    (-.071,-.06,.023,9,'RearSeatBand'),(.063,.073,.023,9,'ForeSeatBand'),
                    (.155,.17,.021,10,'ForeGripRing')]:
 tube(n,rodpos(a),rodpos(b),r,col)
# Broad cork variation: deliberate, sparse seams, no noise texture.
for j,s in enumerate([-.23,-.185,-.135,-.09,.10,.139]):
 tube('CorkRing_%d'%j,rodpos(s),rodpos(s+.002),.0222 if s<0 else .0203,6)
for j,s in enumerate([.24,.55,.86,1.17,1.48,1.80]):
 p=rodpos(s); radius=.041-(s/END)*.026
 up=Vector((0,-.292,-.956))
 c=p+up*(radius+.018)
 ring('Guide_%02d'%(j+1),c,radius,.0025,9,bendweights,D)
 tube('GuideFoot_%02d'%(j+1),p,c+Vector((radius,0,0)),.0035,9,bendweights,6)
 tube('GuideWrap_%02d'%(j+1),rodpos(s-.013),rodpos(s+.012),.014*(1-s/END)+.0045,4,bendweights,8)

# Open spinning reel, satin spool, ivory line pack, visible bail and crank.
tube('ReelStem',(0,0,-.005),(0,.04,-.10),.011,9,sides=8)
ell('ReelBody',(0,.025,-.14),(.044,.058,.045),0)
ell('ReelBodyPanel',(-.034,.027,-.14),(.012,.036,.028),1)
tube('SpoolAxle',(0,-.015,-.151),(0,-.14,-.151),.009,9)
for name,y1,y2,r,col in [('SpoolRimRear',-.065,-.075,.046,9),('SpoolLine',-.075,-.127,.038,10),('SpoolRimFront',-.127,-.138,.047,9),('SpoolCap',-.138,-.15,.022,4)]:
 tube(name,(0,y1,-.151),(0,y2,-.151),r,col,'ReelSpool',16)
for i in range(5):
 ring('SpoolLine_%d'%i,(0,-.082-i*.009,-.151),.0385,.0014,13,'ReelSpool',steps=14)
ps=[]
for j in range(15):
 t=-.15+math.pi*1.15*j/14
 ps.append((.057*math.cos(t),-.11-.015*math.sin(t),-.151+.057*math.sin(t)))
loft('ReelBail',ps,[.003]*len(ps),9,'ReelSpool',6)
tube('CrankAxle',CRANK,CRANK+Vector((.052,0,0)),.012,9,'ReelHandle')
tube('CrankArm',CRANK+Vector((.048,0,0)),CRANK+Vector((.057,.048,-.042)),.009,9,'ReelHandle',8)
tube('CrankKnob',KNOB-Vector((.027,0,0)),KNOB+Vector((.028,0,0)),.017,8,'ReelHandle',12)

# Sleeves widen toward elbow with a restrained seam and captain's gold cuffs.
LWR=Vector((-.082,.015,-.033))+D*.10; LEL=Vector((-.26,.40,-.24))
RWR=KNOB+Vector((.022,.058,.012)); REL=Vector((.30,.39,-.27))
def sleeve(side,el,wr,hand):
 d=wr-el
 def ws(p):
  t=max(0,min(1,(p-el).dot(d)/d.length_squared))
  return {'RodRoot':1-t,hand:t}
 # Extend behind the visible forearm so wind-up/lift never reveal cut elbows.
 points=[el-d.normalized()*.65,el-d.normalized()*.30,el,el+d*.2,el+d*.55,el+d*.82,wr]
 loft('OilskinSleeve.'+side,points,[(.080,.074),(.074,.069),(.066,.060),(.064,.060),(.057,.054),(.048,.047),(.043,.042)],0,ws,12)
 for j,t in enumerate([.86,.93]):
  tube('CaptainCuffStripe%d.%s'%(j,side),el+d*t,el+d*(t+.012),.046-(t-.86)*.02,2,ws,12)
 tube('GloveCuff.'+side,wr-d.normalized()*.008,wr+d.normalized()*.028,.043,4,hand,12,r2=.041)
 return ws
sleeve('L',LEL,LWR,'GripHand.L'); sleeve('R',REL,RWR,'ReelHand.R')

# Rounded mitten-like work gloves, articulated finger silhouette and an opposing thumb.
ell('GlovePalm.L',(-.054,-.005,-.006),(.035,.063,.040),2,'GripHand.L')
ell('GloveBackPanel.L',(-.080,-.006,.005),(.012,.047,.025),3,'GripHand.L')
for i,y in enumerate([-.060,-.026,.008,.040]):
 ps=[(-.065,y,.023),(-.038,y,.041),(-.004,y,.033),(.023,y,.012),(.020,y,-.018),(-.002,y,-.027)]
 loft('GripFinger%d.L'%i,ps,[.012,.013,.013,.012,.011,.0075],2,'GripHand.L',8)
 # Seam between broad palm and individual rounded knuckles.
ell('ThumbBase.L',(-.063,-.068,-.022),(.022,.028,.023),2,'GripHand.L')
loft('Thumb.L',[(-.073,-.065,-.018),(-.041,-.090,-.018),(-.012,-.086,-.013),(.004,-.070,-.008)],[.020,.019,.016,.010],2,'GripHand.L',10)
for o in PARTS:
 if o.name.startswith(('GlovePalm.L','GloveBackPanel.L','GripFinger','ThumbBase.L','Thumb.L')):
  o.location+=D*.10

# Cranking hand cups a knob on its X axis; its centre remains at the crank endpoint.
ell('GlovePalm.R',KNOB+Vector((.010,.038,.007)),(.048,.034,.038),2,'ReelHand.R')
ell('GloveBackPanel.R',KNOB+Vector((.011,.059,.016)),(.035,.010,.023),3,'ReelHand.R')
for i,xoff in enumerate([-.033,-.010,.013,.036]):
 ps=[KNOB+Vector((xoff,.044,.020)),KNOB+Vector((xoff,.012,.038)),KNOB+Vector((xoff,-.022,.023)),KNOB+Vector((xoff,-.026,-.007)),KNOB+Vector((xoff,-.009,-.019))]
 loft('CrankFinger%d.R'%i,ps,[.011,.012,.012,.011,.007],2,'ReelHand.R',8)
loft('Thumb.R',[KNOB+Vector((-.040,.037,-.010)),KNOB+Vector((-.053,.015,-.024)),KNOB+Vector((-.033,-.006,-.029)),KNOB+Vector((-.013,-.009,-.022))],[.019,.019,.015,.009],2,'ReelHand.R',10)

# Mirror the authoring assembly so the support is left and the crank is right
# in the forward-facing review. Blender -Y view has screen-right along -X.
# Apply the reflection to geometry and rest bones, preserving positive transforms.
for o in PARTS:
 mw=o.matrix_world.copy()
 for v in o.data.vertices:
  p=mw@v.co;p.x=-p.x;v.co=p
 o.location=(0,0,0);o.rotation_euler=(0,0,0);o.scale=(1,1,1)
 # Reflection reverses winding; restore outward normals.
 for p in o.data.polygons:p.flip()
bpy.context.view_layer.objects.active=rig
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for b in data.edit_bones:
 h=b.head.copy();t=b.tail.copy();h.x=-h.x;t.x=-t.x;b.head=h;b.tail=t
bpy.ops.object.mode_set(mode='OBJECT')
CRANK.x=-CRANK.x;KNOB.x=-KNOB.x

# All seven actions affect the common assembly; procedural bend remains additive.
CLIPS={'Idle':(80,True),'Cast':(36,False),'Hold':(40,True),'Twitch':(16,False),'Strike':(10,False),'Reel':(32,True),'Lift':(48,False)}
BEND=[.01,.035,.06,.09,.13,.17,.22,.26]
def reset():
 for p in rig.pose.bones: p.location=(0,0,0); p.rotation_euler=(0,0,0); p.scale=(1,1,1)
def pose(frame,root=(0,0,0),bend=0,reel=0,loc=(0,0,0),spool=0):
 reset()
 # RodRoot points along -Y: its local X points along world -X.
 # Author the first angle about world +X so a negative angle lifts the rod.
 rig.pose.bones['RodRoot'].rotation_euler=tuple(math.radians(x) for x in (-root[0],root[1],root[2]))
 rig.pose.bones['RodRoot'].location=loc
 for i,b in enumerate(BEND):rig.pose.bones['Rod_%02d'%(i+1)].rotation_euler.x=b*bend
 rig.pose.bones['ReelHandle'].rotation_euler.y=reel
 rig.pose.bones['ReelSpool'].rotation_euler.y=spool
 for p in rig.pose.bones:
  p.keyframe_insert('location',frame=frame); p.keyframe_insert('rotation_euler',frame=frame)
def act(name):
 a=bpy.data.actions.new(name); a.use_fake_user=True
 rig.animation_data_create(); rig.animation_data.action=a
 return a
for n,(end,loop) in CLIPS.items():
 a=act(n)
 if n=='Idle':
  for f,v in [(0,0),(20,1),(40,0),(60,-1),(80,0)]:pose(f,(v*.7,0,v*.6),.015,loc=(0,0,.003*v))
 elif n=='Cast':
  for f,rot,b,loc in [(0,(0,0,0),0,(0,0,0)),(12,(-58,0,-7),.13,(.025,.08,.04)),(18,(-63,0,-9),.22,(.03,.10,.06)),(25,(16,0,2),.52,(0,-.05,0)),(31,(3,0,0),.16,(0,0,0)),(36,(0,0,0),0,(0,0,0))]:pose(f,rot,b,loc=loc)
 elif n=='Hold':
  for f,v in [(0,0),(20,1),(40,0)]:pose(f,(v*.3,0,0),.03+v*.015)
 elif n=='Twitch':
  for f,v in [(0,0),(4,.22),(8,.06),(12,.12),(16,0)]:pose(f,(v*-2,0,0),v)
 elif n=='Strike':
  for f,r,b in [(0,0,.25),(3,-21,.8),(6,-29,1),(10,-24,.8)]:pose(f,(r,0,0),b)
 elif n=='Reel':
  for f in range(0,33,4):
   t=f/32; pose(f,(-10+math.sin(t*2*math.pi)*.6,0,0),.55+.035*math.sin(t*2*math.pi),t*2*math.pi,spool=-t*4*math.pi)
 elif n=='Lift':
  for f,r,b in [(0,-10,.55),(16,-25,.8),(32,-44,.45),(48,-52,.18)]:pose(f,(r,0,0),b,loc=(0,0,f/48*.08))
 a['loop']=loop; a['duration_seconds']=end/40; a['frames']='0..%d'%end
 # Linear reel angle avoids acceleration at loop seam.
 for slot in a.slots:
  for layer in a.layers:
   for strip in layer.strips:
    cb=strip.channelbag(slot)
    if cb:
     for fc in cb.fcurves:
      if 'ReelHandle' in fc.data_path or 'ReelSpool' in fc.data_path:
       for k in fc.keyframe_points:k.interpolation='LINEAR'
 a.pose_markers.new('Start').frame=0; a.pose_markers.new('End').frame=end

rig.animation_data.action=bpy.data.actions['Idle']; sc.frame_set(0)
# A single skinned mesh/material is one production draw, preserving bone groups.
PART_TRIANGLES={o.name:sum(len(p.vertices)-2 for p in o.data.polygons) for o in PARTS}
bpy.ops.object.select_all(action='DESELECT')
for o in PARTS:o.select_set(True)
bpy.context.view_layer.objects.active=PARTS[0]
bpy.ops.object.join()
combined=bpy.context.object;combined.name='FishRodFP_Mesh'
PARTS=[combined]
# Export only production rig and meshes, no stage/camera/light/helper geometry.
bpy.ops.object.select_all(action='DESELECT'); rig.select_set(True)
for o in PARTS:o.select_set(True)
bpy.context.view_layer.objects.active=rig
FBX=OUT/'FishRodFP.fbx'
bpy.ops.export_scene.fbx(filepath=str(FBX),use_selection=True,object_types={'MESH','ARMATURE'},
 axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',
 use_space_transform=True,bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,
 bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,
 bake_anim_simplify_factor=0,path_mode='RELATIVE',use_custom_props=True,mesh_smooth_type='FACE')

def simplemat(n,col,rough=1):
 m=bpy.data.materials.new(n); m.diffuse_color=(*col,1); m.use_nodes=True
 m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*col,1)
 m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=rough
 return m
stage=bpy.data.collections.new('REVIEW_ONLY'); sc.collection.children.link(stage)
def stageobj(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 stage.objects.link(o)
sea=simplemat('Review sea',(.035,.30,.34),.7)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,-15,-.65)); o=bpy.context.object; o.name='REVIEW_Water';o.data.materials.append(sea);stageobj(o)
def light(n,loc,power,size):
 l=bpy.data.lights.new(n,'AREA'); l.energy=power; l.shape='DISK'; l.size=size
 o=bpy.data.objects.new(n,l);stage.objects.link(o);o.location=loc
 o.rotation_euler=(Vector((0,-.4,0))-o.location).to_track_quat('-Z','Y').to_euler()
light('Review key',(-3,0,5),450,4); light('Review fill',(3,-2,3),180,3)
camdata=bpy.data.cameras.new('PlayerCamera');cam=bpy.data.objects.new('PlayerCamera',camdata);stage.objects.link(cam);sc.camera=cam
CAMLOC=(.34,1.15,.30); CAMTARGET=(.34,-4,-.75)
def playercam():
 cam.location=CAMLOC;cam.rotation_euler=(Vector(CAMTARGET)-cam.location).to_track_quat('-Z','Y').to_euler()
 camdata.type='PERSP';camdata.lens=24;camdata.sensor_width=36;camdata.clip_start=.025;camdata.clip_end=250
playercam();sc.render.resolution_x=1440;sc.render.resolution_y=900;sc.render.resolution_percentage=100
# Review line is separate, not an asset; integration draws tip -> actual bobber.
def render(name):
 sc.render.filepath=str(OUT/'renders'/('%s.png'%name)); bpy.ops.render.render(write_still=True)
def assetview(direction):
 # Fit actual deformed geometry, including sleeves, for complete inspection.
 ob=combined.evaluated_get(bpy.context.evaluated_depsgraph_get())
 me=ob.to_mesh();pts=[ob.matrix_world@v.co for v in me.vertices];ob.to_mesh_clear()
 center=Vector(tuple((min(p[i] for p in pts)+max(p[i] for p in pts))/2 for i in range(3)))
 camdata.type='ORTHO';cam.location=center+Vector(direction).normalized()*4
 cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
 basis=cam.rotation_euler.to_matrix();right=basis@Vector((1,0,0));up=basis@Vector((0,1,0))
 width=max(p.dot(right) for p in pts)-min(p.dot(right) for p in pts)
 height=max(p.dot(up) for p in pts)-min(p.dot(up) for p in pts)
 camdata.ortho_scale=max(width,height*sc.render.resolution_x/sc.render.resolution_y)*1.12
tri=sum(len(p.vertices)-2 for o in PARTS for p in o.data.polygons)
manifest={'triangles':tri,'meshes':len(PARTS),'bones':[b.name for b in data.bones],
 'rod_length_m':2.1,'fps':40,'clips':{n:{'frames':[0,e],'seconds':e/40,'loop':l} for n,(e,l) in CLIPS.items()},
 'atlas':'FishRodFP_Atlas.png','atlas_size':[256,256],'camera_source':{'location':CAMLOC,'target':CAMTARGET,'lens_mm':24,'sensor_width_mm':36},
 'bend_radians_at_1':BEND,'crank_pivot_source':list(CRANK),'crank_knob_source':list(KNOB),
 'source_axes':'-Y forward, Z up; player screen-right is -X',
 'fbx_export_axes':{'axis_forward':'-Z','axis_up':'Y','global_scale':1,'unit':'metre'},
 'unity_import':'Not performed; Codex 1 owns runtime placement and handedness acceptance.',
 'per_part_triangles':PART_TRIANGLES}
assert tri<6000,tri
(OUT/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'FishRodFP.blend'))
if args.render!='none':
 render('player-idle-1440')
 sc.render.resolution_x=844;sc.render.resolution_y=390;render('player-idle-844')
 sc.render.resolution_x=1440;sc.render.resolution_y=900
if args.render=='all':
 for n,frames in {'Idle':[20],'Cast':[12,25],'Hold':[20],'Twitch':[4],'Strike':[6],'Reel':[0,8,16,24],'Lift':[48]}.items():
  rig.animation_data.action=bpy.data.actions[n]
  for f in frames:sc.frame_set(f);render('action-%s-%02d'%(n,f))
 # Alternate angle keeps the entire wind-up and lift legible when outside player framing.
 for n,f in [('Cast',12),('Cast',25),('Strike',6),('Lift',48)]:
  rig.animation_data.action=bpy.data.actions[n];sc.frame_set(f)
  assetview((3,2,1.3))
  render('pose-%s-%02d'%(n,f))
 rig.animation_data.action=None;reset();bpy.context.view_layer.update()
 for amount in [0,.5,1]:
  for i,b in enumerate(BEND):rig.pose.bones['Rod_%02d'%(i+1)].rotation_euler.x=b*amount
  bpy.context.view_layer.update()
  assetview((3,0,.68))
  render('bend-%s'%str(amount).replace('.','_'))
  # Separate review-only chain: offset sideways toward the camera, never in the FBX.
  overlay=[]
  chainmat=simplemat('Review chain %.1f'%amount,(1,.65,.12))
  for i in range(1,9):
   b=rig.pose.bones['Rod_%02d'%i]
   a=b.head+Vector((.09,0,0));t=b.tail+Vector((.09,0,0))
   bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.014,location=a)
   o=bpy.context.object;o.data.materials.append(chainmat);stageobj(o);overlay.append(o)
   bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.004,depth=(t-a).length,location=(a+t)/2)
   o=bpy.context.object;o.rotation_euler=(t-a).to_track_quat('Z','Y').to_euler()
   o.data.materials.append(chainmat);stageobj(o);overlay.append(o)
  render('chain-%s'%str(amount).replace('.','_'))
  for o in overlay:bpy.data.objects.remove(o,do_unlink=True)
 reset();bpy.context.view_layer.update()
 for n,direction in [('side',(1,0,0)),('top',(0,0,1))]:
  assetview(direction);render(n)
 # Close evidence for gloves, support grip and crank-knob contact.
 playercam();camdata.lens=32;cam.location=(.34,.60,.18)
 cam.rotation_euler=(Vector((0,-.02,-.07))-cam.location).to_track_quat('-Z','Y').to_euler()
 render('hands-detail')
 rig.animation_data.action=bpy.data.actions['Idle'];sc.frame_set(0);playercam()
 sc.render.resolution_x=1440;sc.render.resolution_y=900
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'FishRodFP.blend'))
print('FISH ROD BUILD',json.dumps({'triangles':tri,'meshes':len(PARTS),'bones':len(data.bones)}))

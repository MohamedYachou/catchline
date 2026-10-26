"""Whale shelf life: deterministic metre-scale source and Legacy FBX delivery."""
import bpy,sys,math,json,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/WhaleShelfLife'
sp=importlib.util.spec_from_file_location('accepted_open_sea_helpers',str(R/'Art/Source/OpenSeaLife/build.py'));S=importlib.util.module_from_spec(sp);sp.loader.exec_module(S)
H=S.H;G=H.Geometry;empty=S.empty;mesh=S.mesh;fin=S.fin;sha=S.sha;snapshot=S.snapshot
P={'M_WhaleSlate':'#526B73','M_WhaleLit':'#70858A','M_WhaleBelly':'#D4D9CC','M_ThroatGroove':'#A3B4B1','M_Ivory':'#F3F0DC','M_VapourShade':'#D5E3DC','M_Wingtip':'#28343B','M_GullMantle':'#BAC9C6','M_YellowBill':'#E6AD38','M_Eye':'#17343D','M_BaitDark':'#31565E','M_BaitSilver':'#8FA6AC','M_BaitTeal':'#517F81'}
LIMITS={'Humpback':1400,'BlowSpout':200,'KittiwakeFlock':900,'BaitBall':400}
CLIPS={'Humpback':{'Surface':(91,False),'Blow':(46,False),'Fluke':(91,False)},'KittiwakeFlock':{'Circle':(121,True)},'BaitBall':{'Swirl':(61,True)}}

def whale():
 g=G();tags=[]
 def part(n,fn):
  a=len(g.vertices);fn();tags.append((a,len(g.vertices),n))
 def body():
  # Broad blunt rostrum, long throat, arched back and tapering caudal peduncle.
  sec=[(-4.25,.22,.13,-.45),(-4.03,.65,.28,-.43),(-3.62,.96,.49,-.48),(-3.05,1.08,.73,-.59),(-2.15,1.13,.92,-.66),(-1.05,1.03,.98,-.67),(.10,.88,.86,-.72),(1.25,.60,.63,-.78),(2.28,.32,.35,-.71),(3.25,.14,.19,-.53),(3.9,.095,.12,-.37)]
  n=16;v=[(rx*math.cos(math.tau*i/n),y,z+rz*math.sin(math.tau*i/n)) for y,rx,rz,z in sec for i in range(n)]
  faces=[tuple(reversed(range(n))),tuple(range((len(sec)-1)*n,len(sec)*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(sec)-1) for i in range(n)]
  a=len(g.faces);g.add(v,faces,'M_WhaleSlate')
  for k in range(a,len(g.faces)):
   p=[g.vertices[i] for i in g.faces[k]];z=sum(v[2] for v in p)/len(p);y=sum(v[1] for v in p)/len(p)
   if z<-.75 and y<.1:
    # Long alternating ventral lanes suggest throat pleats without wire-like grooves.
    i=(k-a-2)%n;g.colours[k]='M_ThroatGroove' if i%2 else 'M_WhaleBelly'
   elif z<-.45:g.colours[k]='M_WhaleLit'
  for s in (-1,1):
   g.ellipsoid((s*.91,-3.36,-.39),(.040,.062,.044),6,2,'M_Eye')
   for y,x,z in [(-3.95,.39,-.19),(-3.66,.62,-.03),(-3.25,.65,.08)]:g.ellipsoid((s*x,y,z),(.095,.12,.075),5,1,'M_WhaleLit')
   # Quiet jaw edge and paired blowholes; no teeth or exaggerated expression.
   g.beam((s*.21,-4.20,-.50),(s*.73,-3.87,-.53),.027,.025,'M_WhaleLit')
  for s in (-1,1):g.ellipsoid((s*.085,-2.60,.15),(.045,.13,.018),6,1,'M_Eye')
  fin(g,[(0,.9,-.12),(0,1.17,.18),(0,1.33,.40),(0,1.44,.43),(0,1.49,.37),(0,1.50,.17),(0,1.94,-.26)],.17,'M_WhaleSlate')
 part('Body',body)
 def tail():
  for s in (-1,1):
   poly=[(s*.03,3.74,-.35),(s*.56,3.64,-.28),(s*1.27,3.83,-.23),(s*1.64,4.15,-.19),(s*1.70,4.34,-.20),(s*1.53,4.40,-.21),(s*.83,4.24,-.31),(s*.18,4.14,-.39),(0,4.30,-.40)]
   # Broad, thick flukes with curved ends and a deep central notch.
   a=len(g.faces);fin(g,poly,.10,'M_WhaleSlate',2)
   g.colours[a]='M_WhaleBelly'
 part('Tail',tail)
 for s,n in [(-1,'L'),(1,'R')]:
  def pec(s=s):
   path=[(s*.80,-2.15,-.77),(s*1.36,-1.86,-.86),(s*2.05,-1.31,-1.01),(s*2.71,-.61,-1.12),(s*3.18,.03,-1.16)]
   widths=[.30,.34,.29,.20,.055];depths=[.10,.12,.10,.075,.035];v=[]
   for (x,y,z),w,d in zip(path,widths,depths):
    for i in range(8):v.append((x,y+w*math.cos(math.tau*i/8),z+d*math.sin(math.tau*i/8)))
   faces=[tuple(reversed(range(8))),tuple(range(32,40))]+[(j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i) for j in range(4) for i in range(8)]
   g.add(v,faces,'M_WhaleBelly')
   for j in range(1,4):
    x,y,z=path[j];g.ellipsoid((x,y-widths[j]*.91,z+.02),(.11,.10,.075),5,1,'M_Ivory')
  part('Pectoral.'+n,pec)
 # Gradually transfer the posterior body vertices to Tail for a continuous peduncle bend.
 return g,tags,[('Root',(0,0,0),None),('Body',(0,0,0),'Root'),('Tail',(0,2.7,-.65),'Body'),('Pectoral.L',(-.8,-2.15,-.77),'Body'),('Pectoral.R',(.8,-2.15,-.77),'Body')]

def bird_geometry():
 g=G();tags=[]
 def part(n,fn):
  a=len(g.vertices);fn();tags.append((a,len(g.vertices),n))
 def body():
  g.ellipsoid((0,0,0),(.095,.22,.095),8,2,'M_Ivory');g.ellipsoid((0,-.19,.065),(.066,.084,.066),6,2,'M_Ivory')
  g.tube([(0,-.245,.065),(0,-.365,.05)],[.025,.004],5,'M_YellowBill');g.tube([(0,.17,-.005),(0,.36,-.015)],[.069,.012],5,'M_Ivory')
  for s in (-1,1):g.ellipsoid((s*.059,-.21,.083),(.009,.014,.009),4,1,'M_Eye')
 part('Body',body)
 for s,n in [(-1,'L'),(1,'R')]:
  def wing(s=s):
   fin(g,[(s*.05,-.055,.02),(s*.34,-.12,.05),(s*.57,-.10,.07),(s*.58,.025,.07),(s*.34,.07,.04),(s*.08,.12,0)],.025,'M_GullMantle',2)
   fin(g,[(s*.52,-.10,.07),(s*.76,-.055,.075),(s*.84,.025,.06),(s*.78,.07,.06),(s*.69,.035,.07),(s*.61,.105,.05),(s*.54,.06,.055)],.025,'M_Wingtip',2)
  part('Wing.'+n,wing)
 return g,tags

def flock():
 g=G();tags=[];spec=[('Root',(0,0,0),None)]
 for i in range(3):
  a=math.tau*i/3;c=Vector((3*math.cos(a),3*math.sin(a),2.4+.55*i));theta=a+math.pi
  from mathutils import Matrix
  rot=Matrix.Rotation(theta,3,'Z');bird,bt=bird_geometry();start=len(g.vertices);bird.vertices=[tuple(c+rot@Vector(v)) for v in bird.vertices];g.merge(bird)
  n='Bird_'+str(i+1);spec.append((n,tuple(c),'Root'))
  for lo,hi,part in bt:tags.append((start+lo,start+hi,n if part=='Body' else n+'.'+part))
  for s,k in [(-1,'L'),(1,'R')]:spec.append((n+'.Wing.'+k,tuple(c+rot@Vector((s*.08,-.055,.02))),n))
 return g,tags,spec

def bait():
 g=G();tags=[];spec=[('Root',(0,0,0),None)]
 # Twenty-four tiny solid diamond fish form a dark disc, with sparse silver glints.
 for i in range(24):
  a=i*2.39996323;r=1.65*math.sqrt((i+.5)/24);cx,cy=r*math.cos(a),r*math.sin(a);z=-.16+.025*math.sin(i*1.7);theta=a+.6
  from mathutils import Matrix
  rot=Matrix.Rotation(theta,3,'Z');q=G();q.add([(0,-.19,0),(.055,0,0),(0,.14,0),(-.055,0,0),(0,0,.028),(0,0,-.022)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(1,0,5),(2,1,5),(3,2,5),(0,3,5)],'M_BaitDark' if i%4 else 'M_BaitSilver')
  fin(q,[(0,.10,0),(.09,.23,0),(-.09,.23,0)],.012,'M_BaitTeal',2)
  q.vertices=[tuple(Vector((cx,cy,z))+rot@Vector(v)) for v in q.vertices];start=len(g.vertices);g.merge(q);n='FishRing_'+str(i%3);tags.append((start,len(g.vertices),n))
 for i in range(3):spec.append(('FishRing_'+str(i),(0,0,-.16),'Root'))
 return g,tags,spec

def spout(root):
 g=G()
 # Four rounded triangulated lobes overlap into a split heart/V crown.
 # Decimated icospheres avoid the old box-shaped latitude-ring poles.
 g.tube([(0,0,0),(.01,0,.55),(0,.01,1.1),(0,0,1.66)],[.075,.12,.20,.30],7,'M_Ivory')
 for c,r,col in [((-.22,0,1.78),(.41,.36,.56),'M_VapourShade'),((.23,-.01,1.85),(.44,.39,.58),'M_Ivory'),((-.49,.02,2.44),(.57,.47,.59),'M_Ivory'),((.49,0,2.46),(.58,.47,.58),'M_Ivory')]:
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1)
  o=bpy.context.object;mod=o.modifiers.new('RoundedLowFacet','DECIMATE');mod.ratio=.4
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
  g.add([(c[0]+v.co.x*r[0],c[1]+v.co.y*r[1],c[2]+v.co.z*r[2]) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],col)
  data=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(data)
 mesh(g,'RoundedVapour',root)

def rig_asset(name,root):
 g,tags,spec={'Humpback':whale,'KittiwakeFlock':flock,'BaitBall':bait}[name]()
 ar=bpy.data.armatures.new(name+'Skeleton');rig=bpy.data.objects.new(name+'Rig',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=root
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 for n,h,par in spec:
  b=ar.edit_bones.new(n);b.head=h;b.tail=Vector(h)+Vector((0,.08,0))
  if par:b.parent=ar.edit_bones[par]
 bpy.ops.object.mode_set(mode='OBJECT');skin=mesh(g,name+'Skin',rig);mod=skin.modifiers.new('LegacySkin','ARMATURE');mod.object=rig
 for n,_,_ in spec:skin.vertex_groups.new(name=n);rig.pose.bones[n].rotation_mode='XYZ'
 for a,b,n in tags:skin.vertex_groups[n].add(list(range(a,b)),1,'REPLACE')
 if name=='Humpback':
  for v in skin.data.vertices:
   if v.co.y>2.28 and v.index<176:
    t=min(1,max(0,(v.co.y-2.28)/1.62));skin.vertex_groups['Body'].add([v.index],1-t,'REPLACE');skin.vertex_groups['Tail'].add([v.index],t,'REPLACE')
 for clip,(end,loop) in CLIPS[name].items():
  act=bpy.data.actions.new(clip);act.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=act
  for f in range(1,end+1):
   t=(f-1)/(end-1);wave=math.sin(math.tau*t)
   for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
   if name=='Humpback':
    b=rig.pose.bones['Body'];tail=rig.pose.bones['Tail']
    if clip=='Surface':
     rise=math.sin(math.pi*t)**2
     b.location.z=-1.35+1.80*rise
     b.rotation_euler.x=.14*math.sin(math.tau*t)
     b.rotation_euler.y=.10*math.sin(math.tau*t)
     # A single left pectoral breach at the crest, followed by a quiet return.
     rig.pose.bones['Pectoral.L'].rotation_euler.y=.64*rise
     rig.pose.bones['Pectoral.R'].rotation_euler.y=.04*rise
    elif clip=='Blow':
     b.location.z=.035*math.sin(math.pi*t);b.rotation_euler.x=.018*math.sin(math.pi*t)
    else:
     # 0.9s arch/lift, 0.6s held vertical tail, then straight vertical withdrawal.
     def ease(q):
      q=min(1,max(0,q));return q*q*(3-2*q)
     lift=ease(t/.30)
     b.location.z=-.90*lift
     b.rotation_euler.x=.20*lift
     tail.location.z=2.35*lift
     tail.rotation_euler.x=1.30*lift
     if t>.50:
      # Freeze arch and horizontal coordinates throughout the vertical descent.
      b.location.z-=4.40*ease((t-.50)/.50)
     for n in ('L','R'):rig.pose.bones['Pectoral.'+n].rotation_euler.y=.04*lift
   elif name=='KittiwakeFlock':
    for i in range(3):
     a=math.tau*i/3;theta=math.tau*t;pb=rig.pose.bones['Bird_'+str(i+1)];pb.location=(3*(math.cos(a+theta)-math.cos(a)),3*(math.sin(a+theta)-math.sin(a)),.12*math.sin(theta+i)-.12*math.sin(i));pb.rotation_euler.z=theta
     for s,k in [(-1,'L'),(1,'R')]:rig.pose.bones['Bird_'+str(i+1)+'.Wing.'+k].rotation_euler.y=s*.09*math.sin(2*theta+i)
   else:
    # Three interleaved fish groups: a slow18-degree swirl arc and asynchronous ripples.
    for i in range(3):pb=rig.pose.bones['FishRing_'+str(i)];pb.rotation_euler.z=.16*wave;pb.location.z=.025*(math.sin(math.tau*t+i*2)-math.sin(i*2));pb.rotation_euler.x=.018*wave
   for pb in rig.pose.bones:
    for prop in ('location','rotation_euler','scale'):pb.keyframe_insert(prop,frame=f,group=pb.name)
  for fc in act.layers[0].strips[0].channelbag(rig.animation_data.action_slot).fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
   if loop:fc.modifiers.new('CYCLES')
  act['legacy']=True;act['loop']=loop
 rig.animation_data.action=bpy.data.actions[next(iter(CLIPS[name]))];rig.animation_data.action_slot=rig.animation_data.action.slots[0];rig['legacy_import']=True
 return rig

def run(name):
 O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=30
 H.PALETTE=P;H.MATERIALS={n:H.material(n,c,.73) for n,c in P.items()};root=empty(name)
 if name=='BlowSpout':spout(root)
 else:rig_asset(name,root)
 sc.frame_set(1);row=snapshot();assert row['triangles']<=LIMITS[name],(name,row['triangles'],LIMITS[name])
 for m in list(bpy.data.materials):
  if m.users==0:bpy.data.materials.remove(m)
 sc.frame_start=1;sc.frame_end=max([e for e,l in CLIPS.get(name,{}).values()] or [1]);bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')));bpy.ops.object.select_all(action='SELECT')
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=name in CLIPS,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_step=1,bake_anim_simplify_factor=0,use_custom_props=True,colors_type='LINEAR')
 row.update(name=name,limit=LIMITS[name],clips={n:{'seconds':(e-1)/30,'loop':l,'frames':[1,e]} for n,(e,l) in CLIPS.get(name,{}).items()},sha256={e:sha(O/(name+'.'+e)) for e in ('blend','fbx')},palette=P);(O/'metrics'/(name+'-build.json')).write_text(json.dumps(row,indent=2)+'\n');print('WHALE SHELF BUILT',name,row['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])

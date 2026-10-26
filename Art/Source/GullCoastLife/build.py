"""Deterministic coastal wildlife. Windows Blender5.2; all output source-art only."""
import bpy,sys,math,json,hashlib,random,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/GullCoastLife'
sys.path.insert(0,str(R/'Art/Source'));import build_crab_coast_props as H
G=H.Geometry
P={'M_FeatherDark':'#25383C','M_FeatherGloss':'#344D4A','M_Ivory':'#F3F0DC','M_BillHorn':'#B7A179','M_BillOrange':'#E36A35','M_LegPink':'#C9857F','M_Eye':'#14262A','M_EyeTeal':'#70B4A0','M_Rock':'#8E8A80','M_RockShade':'#6F6A61','M_WetSand':'#A69775','M_SandShade':'#8F856F','M_Red':'#BF4F3D','M_Green':'#477A56','M_Rope':'#D1AF76','M_LampGlow':'#FFE7A3'}
LIMITS={'Cormorant':600,'CormorantRock':1800,'Oystercatcher':400,'OystercatcherGroup':1800,'ChannelMarkers':1600,'PotBuoyLine':1000}
CLIPS={'Cormorant':{'Idle':(91,True),'DryWings':(61,True),'Dive':(31,False)},'Oystercatcher':{'Walk':(31,True),'Probe':(46,True)}}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def empty(n,parent=None):
 o=bpy.data.objects.new(n,None);bpy.context.scene.collection.objects.link(o);o.parent=parent;return o
def mesh(g,n,parent):
 o=g.object(n,parent,bpy.context.scene.collection);used=sorted({p.material_index for p in o.data.polygons});mats=[o.data.materials[i] for i in used];ids=[used.index(p.material_index) for p in o.data.polygons];o.data.materials.clear()
 for m in mats:o.data.materials.append(m)
 for p,i in zip(o.data.polygons,ids):p.material_index=i
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();return o

def bird(kind):
 c=kind=='Cormorant';g=G();tags=[]
 def part(n,fn):
  a=len(g.vertices);fn();tags.append((a,len(g.vertices),n))
 def body():
  start=len(g.faces);g.ellipsoid((0,.03,.37 if c else .24),(.135,.225,.22) if c else (.12,.195,.105),10 if c else 8,3,'M_FeatherDark')
  for i in range(start,len(g.faces)):
   ctr=sum((Vector(g.vertices[j]) for j in g.faces[i]),Vector())/len(g.faces[i])
   if not c and ctr.z<.25:g.colours[i]='M_Ivory'
  g.tube([(0,.20,.32 if c else .22),(0,.43 if c else .31,.18 if c else .17)],[.075 if c else .055,.008],5,'M_FeatherDark')
 part('Body',body)
 def head():
  if c:
   g.tube([(0,-.10,.49),(0,-.13,.65),(0,-.19,.78)],[.071,.047,.055],7,'M_FeatherDark')
   g.ellipsoid((0,-.235,.79),(.071,.09,.073),8,3,'M_FeatherDark')
   g.ellipsoid((0,-.285,.75),(.052,.051,.04),6,2,'M_Ivory')
   # Long horn bill with unmistakable curved, downward hook at the end.
   g.tube([(0,-.291,.794),(0,-.395,.786),(0,-.435,.758),(0,-.430,.738)],[.025,.018,.012,.003],5,'M_BillHorn')
  else:
   g.tube([(0,-.10,.26),(0,-.155,.34)],[.063,.052],6,'M_FeatherDark')
   g.ellipsoid((0,-.18,.355),(.067,.082,.065),8,2,'M_FeatherDark')
   g.tube([(0,-.242,.35),(0,-.43,.342)],[.022,.002],5,'M_BillOrange')
  for s in (-1,1):
   g.ellipsoid((s*(.065 if c else .060),-.260 if c else -.202,.805 if c else .367),(.009,.012,.010),6,1,'M_EyeTeal' if c else 'M_BillOrange')
   g.ellipsoid((s*(.072 if c else .066),-.261 if c else -.203,.806 if c else .368),(.004,.006,.006),4,1,'M_Eye')
 part('Head',head)
 for s,n in [(-1,'L'),(1,'R')]:
  def wing(s=s):
   if c:
    # Low faceted folded wing, discrete feather scallops. Opens at shoulder.
    poly=[(.105,-.07,.49),(.17,.06,.52),(.175,.24,.43),(.15,.39,.30),(.12,.34,.32),(.09,.20,.37)]
   else:poly=[(.08,-.055,.285),(.13,.03,.30),(.13,.14,.275),(.075,.27,.20),(.055,.16,.245)]
   v=[(s*x,y,z+d) for d in (-.007,.007) for x,y,z in poly];k=len(poly)
   g.add(v,[tuple(reversed(range(k))),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)],'M_FeatherGloss' if c else 'M_FeatherDark')
   if not c:g.beam((s*.132,.045,.293),(s*.106,.155,.267),.024,.009,'M_Ivory')
  part('Wing.'+n,wing)
  def leg(s=s):
   x=s*(.065 if c else .057);col='M_FeatherDark' if c else 'M_LegPink'
   g.tube([(x,.035,.24 if c else .22),(x,.055,.11),(x,-.015,.018)],[.016 if c else .009,.011 if c else .007,.009 if c else .006],5 if c else 4,col)
   if c:g.add([(x-.04,-.018,.009),(x+.04,-.018,.009),(x+.04,-.10,.009),(x-.03,-.115,.009),(x-.04,-.018,.016),(x+.04,-.018,.016),(x+.04,-.10,.016),(x-.03,-.115,.016)],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],col)
   else:
    for t in (-1,1):g.beam((x,-.015,.012),(x+t*.025,-.062,.006),.008,.010,col)
  part('Leg.'+n,leg)
 return g,tags

def rig_bird(name,root):
 c=name=='Cormorant';g,tags=bird(name);skin=mesh(g,name+'Skin',root)
 ar=bpy.data.armatures.new(name+'Skeleton');rig=bpy.data.objects.new(name+'Rig',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=root
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 spec=[('Root',(0,0,0),None),('Body',(0,0,.3 if c else .23),'Root'),('Head',(0,-.10,.49 if c else .26),'Body'),('Wing.L',(-.105,-.07,.49) if c else (-.08,-.055,.285),'Body'),('Wing.R',(.105,-.07,.49) if c else (.08,-.055,.285),'Body'),('Leg.L',(-.065,.035,.24) if c else (-.057,.035,.22),'Body'),('Leg.R',(.065,.035,.24) if c else (.057,.035,.22),'Body')]
 for n,h,parent in spec:
  b=ar.edit_bones.new(n);b.head=h;b.tail=Vector(h)+Vector((0,.05,0))
  if parent:b.parent=ar.edit_bones[parent]
 bpy.ops.object.mode_set(mode='OBJECT');skin.parent=rig;mod=skin.modifiers.new('BirdSkinning','ARMATURE');mod.object=rig
 for n,_,_ in spec:skin.vertex_groups.new(name=n);rig.pose.bones[n].rotation_mode='XYZ'
 for a,b,n in tags:skin.vertex_groups[n].add(list(range(a,b)),1,'REPLACE')
 for action,(end,loop) in CLIPS[name].items():
  act=bpy.data.actions.new(action);act.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=act
  for f in range(1,end+1):
   t=(f-1)/(end-1);wave=math.sin(math.tau*t)
   for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
   if action=='Idle':rig.pose.bones['Head'].rotation_euler.z=.10*wave
   elif action=='DryWings':
    for s,n in [(-1,'L'),(1,'R')]:rig.pose.bones['Wing.'+n].rotation_euler=(0,s*(.34+.08*math.sin(2*math.tau*t)),-s*1.35)
    rig.pose.bones['Head'].rotation_euler.x=.04*wave
   elif action=='Dive':
    smooth=t*t*(3-2*t);rig.pose.bones['Body'].rotation_euler.x=1.25*smooth;rig.pose.bones['Body'].location.z=-1.3*smooth
   elif action=='Walk':
    for s,n in [(-1,'L'),(1,'R')]:
     pb=rig.pose.bones['Leg.'+n];pb.rotation_euler.x=s*.22*wave;pb.location.z=.018*max(0,s*wave)
    rig.pose.bones['Head'].rotation_euler.x=.04*wave
   elif action=='Probe':
    a=math.sin(math.pi*t)**2;rig.pose.bones['Body'].rotation_euler.x=.22*a;rig.pose.bones['Head'].rotation_euler.x=.72*a
   for pb in rig.pose.bones:
    for prop in ('location','rotation_euler','scale'):pb.keyframe_insert(prop,frame=f,group=pb.name)
  for fc in act.layers[0].strips[0].channelbag(rig.animation_data.action_slot).fcurves:
   for key in fc.keyframe_points:key.interpolation='LINEAR'
   if loop:fc.modifiers.new('CYCLES')
  act['loop']=loop
 rig.animation_data.action=bpy.data.actions['Idle' if c else 'Walk'];sc=bpy.context.scene;sc.frame_start=1;sc.frame_end=91 if c else 46;sc.frame_set(1)
 return {'rig':rig.name,'bones':[n for n,_,_ in spec],'clips':{n:{'frames':[1,e],'seconds':(e-1)/30,'loop':l} for n,(e,l) in CLIPS[name].items()},'root_motion':False,'pivot':'feet contact at origin','forward':'Blender -Y / Unity +Z'}

def transform(g,x,y,z,scale=1,a=0):
 g.vertices=[(x+scale*(u*math.cos(a)-v*math.sin(a)),y+scale*(u*math.sin(a)+v*math.cos(a)),z+scale*w) for u,v,w in g.vertices];return g

def rock(root):
 g=G();rng=random.Random(147);n=9;angles=[math.tau*i/n for i in range(n)];verts=[]
 for z,r in [(-.10,.43),(.10,.50),(.29,.36)]:
  verts.extend((r*math.cos(a)*(1+rng.uniform(-.12,.12)),r*math.sin(a)*(1+rng.uniform(-.12,.12)),z+(rng.uniform(-.04,.04) if z!=.29 else 0)) for a in angles)
 faces=[tuple(reversed(range(n))),tuple(range(2*n,3*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(2) for i in range(n)]
 g.add(verts,faces,'M_Rock');g.colours[0]='M_RockShade';mesh(g,'CormorantRockBase',root)
 for i,(x,y,a) in enumerate([(-.19,-.04,-.25),(.19,.07,.36)]):
  g,tags=bird('Cormorant');transform(g,x,y,.29,.78,a);mesh(g,'PerchedCormorant_'+str(i+1),root)
 return {'static':True,'birds':2,'rock_width_m':1,'pivot':'rock at waterline; birds feet on flat angular top','animation':'Static group; use Cormorant for animated independent birds'}

def sand(root):
 g=G();poly=[(-1,-.23),(-.77,-.49),(-.12,-.5),(.74,-.36),(1,-.08),(.84,.32),(.25,.50),(-.55,.39)]
 g.extrude_polygon(poly,-.06,.018,'M_WetSand');mesh(g,'WetSandBar',root)
 for i,(x,y,a) in enumerate([(-.66,-.04,-.28),(-.18,.10,.20),(.30,-.08,-.16),(.65,.16,.5)]):
  g,_=bird('Oystercatcher');transform(g,x,y,.018,1,a);mesh(g,'Forager_'+str(i+1),root)
 return {'static':True,'birds':4,'sand_footprint_m':[2,1],'pivot':'sandbar waterline; feet on top .018m','animation':'Static habitat group; use Oystercatcher for Walk/Probe'}

def markers(root):
 for i,(name,x,col) in enumerate([('RedCan',-1.15,'M_Red'),('GreenCone',1.15,'M_Green')]):
  node=empty(name,root);g=G()
  g.tube([(x,0,-.22),(x,0,-.03),(x,0,.11)],[.23,.32,.30],10,col)
  g.tube([(x,0,.12),(x,0,.33)],[.27,.27],10,col)
  g.tube([(x,0,.34),(x,0,.98)],[.11,.085],8,col)
  g.tube([(x,0,1.0),(x,0,1.36)],[.22,.22 if i==0 else .018],10,col)
  g.tube([(x,0,1.37),(x,0,1.44)],[.05,.05],6,'M_FeatherDark')
  g.tube([(x,0,1.44),(x,0,1.52)],[.055,.055],6,'M_LampGlow')
  g.tube([(x,0,1.525),(x,0,1.56)],[.07,.038],8,col)
  # White identity band on the float ring, no invented labels.
  g.tube([(x,0,.03),(x,0,.085)],[.315,.305],10,'M_Ivory');mesh(g,name+'Mesh',node)
  # Bake geometry offset into child-local data so each marker has its OWN waterline pivot.
  for v in bpy.data.objects[name+'Mesh'].data.vertices:v.co.x-=x
  node.location.x=x
 return {'static':True,'height_above_water_m':1.56,'children':{'RedCan':[-1.15,0,0],'GreenCone':[1.15,0,0]},'pivot':'pair centre at waterline; each child also waterline centred, independently placeable','light_material':'M_LampGlow only small top lens; emission runtime bind'}

def floats(root):
 g=G();path=[]
 for i in range(33):
  x=-1.5+3*i/32;y=.10*math.sin(math.tau*i/32);z=.007-.018*math.sin(2*math.pi*i/32)**2;path.append((x,y,z))
 g.tube(path,[.012]*len(path),5,'M_Rope');mesh(g,'SlackPotRope',root)
 for i,x in enumerate((-1.25,0,1.25)):
  y=.10*math.sin(math.tau*(x+1.5)/3);g=G();start=len(g.faces)
  g.ellipsoid((x,y,.015),(.16,.115,.11),10,3,'M_BillOrange')
  for j in range(start,len(g.faces)):
   cx=sum(g.vertices[v][0] for v in g.faces[j])/len(g.faces[j])
   if abs(cx-x)<.07:g.colours[j]='M_Ivory'
  g.tube([(x,y,.103),(x,y,.14)],[.025,.02],6,'M_BillOrange');mesh(g,'PotFloat_'+str(i+1),root)
 return {'static':True,'span_m':3,'floats':3,'pivot':'surface centre; floats cross waterline','rope':'3m gentle S slack on water; no hanging vertical legs'}
BUILD={'Cormorant':lambda r:rig_bird('Cormorant',r),'CormorantRock':rock,'Oystercatcher':lambda r:rig_bird('Oystercatcher',r),'OystercatcherGroup':sand,'ChannelMarkers':markers,'PotBuoyLine':floats}

def snapshot():
 bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 return {'triangles':sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),'vertices':sum(len(o.data.vertices) for o in meshes),'bounds_unity':[[min((v.x,v.z,-v.y)[i] for v in pts) for i in range(3)],[max((v.x,v.z,-v.y)[i] for v in pts) for i in range(3)]],'meshes':[o.name for o in meshes],'materials':sorted({m.name for o in meshes for m in o.data.materials}),'parents':{o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects},'mesh_bounds_unity':{o.name:[[min((v.x,v.z,-v.y)[i] for v in [o.matrix_world@v.co for v in o.data.vertices]) for i in range(3)],[max((v.x,v.z,-v.y)[i] for v in [o.matrix_world@v.co for v in o.data.vertices]) for i in range(3)]] for o in meshes}}
def run(name):
 O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=30
 H.PALETTE=P;H.MATERIALS={n:H.material(n,c,.32 if n in ('M_FeatherDark','M_FeatherGloss') and name in ('Cormorant','CormorantRock') else .80) for n,c in P.items()};root=empty(name);contract=BUILD[name](root);row=snapshot();assert row['triangles']<=LIMITS[name],(name,row['triangles'])
 for m in list(bpy.data.materials):
  if m.users==0:bpy.data.materials.remove(m)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')));bpy.ops.object.select_all(action='SELECT')
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_space_transform=name not in CLIPS and name!='ChannelMarkers',use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=name in CLIPS,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_step=1,bake_anim_simplify_factor=0,use_custom_props=True,colors_type='LINEAR')
 row.update(name=name,contract=contract,limit=LIMITS[name],sha256={e:sha(O/(name+'.'+e)) for e in ('blend','fbx')},palette=P);(O/'metrics'/(name+'-build.json')).write_text(json.dumps(row,indent=2)+'\n');print('GULL BUILT',name,row['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])

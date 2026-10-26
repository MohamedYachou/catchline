"""OPEN-SEA-LIFE-ART-1 deterministic metre-scale low-poly assets. No runtime writes."""
import bpy,sys,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/OpenSeaLife'
sys.path.insert(0,str(R/'Art/Source'));import build_crab_coast_props as H
G=H.Geometry
P={'M_DolphinBack':'#708887','M_DolphinSide':'#A2B5B0','M_PaleBelly':'#DCE0CF','M_Ivory':'#F3F0DC','M_Wingtip':'#28343B','M_BuffHead':'#D8BE79','M_Bill':'#A9B7AD','M_Eye':'#17343D','M_SharkWarm':'#817F70','M_SharkShade':'#686D64','M_Wood':'#C58B50','M_WoodLight':'#DFB77A','M_WoodDark':'#8C5A36','M_Log':'#9A8B70','M_LogEnd':'#C2AF8C','M_Net':'#477A56','M_NetDark':'#355B48','M_Orange':'#E36A35','M_Navy':'#173F57','M_Rope':'#D1AF76'}
LIMITS={'Dolphin':700,'DolphinPod':2100,'GannetDive':450,'DiveSplash':200,'BaskingFin':250,'FloatingCrate':650,'DriftNetBuoy':1100,'DriftLog':600,'DistantSail':300}
CLIPS={'Dolphin':{'Swim':(37,True),'Leap':(43,False)},'DolphinPod':{'Swim':(37,True),'Leap':(43,False)},'GannetDive':{'Glide':(61,True),'Dive':(28,False)},'BaskingFin':{'Cruise':(91,True)}}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def empty(n,parent=None):
 o=bpy.data.objects.new(n,None);bpy.context.scene.collection.objects.link(o);o.parent=parent;return o
def mesh(g,n,parent):
 o=g.object(n,parent,bpy.context.scene.collection);used=sorted({p.material_index for p in o.data.polygons});mats=[o.data.materials[i] for i in used];ids=[used.index(p.material_index) for p in o.data.polygons];o.data.materials.clear()
 for m in mats:o.data.materials.append(m)
 for p,i in zip(o.data.polygons,ids):p.material_index=i
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();return o
def fin(g,poly,thick,col,axis=0):
 k=len(poly);v=[tuple(p[j]+(d if j==axis else 0) for j in range(3)) for d in (-thick/2,thick/2) for p in poly];g.add(v,[tuple(reversed(range(k))),tuple(range(k,2*k))]+[(i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k)],col)
def dolphin():
 g=G();tags=[]
 def part(n,fn):
  a=len(g.vertices);fn();tags.append((a,len(g.vertices),n))
 def body():
  # Anatomical cross sections: rounded melon, broad chest, tapered peduncle, swept spine.
  sections=[(-1.03,.035,.035,.02),(-.91,.13,.115,.045),(-.68,.24,.21,.025),(-.31,.285,.265,-.015),(.13,.245,.22,-.04),(.53,.15,.135,-.08),(.88,.065,.065,-.10),(1.06,.038,.040,-.08)]
  n=10;v=[(rx*math.cos(math.tau*i/n),y,z+rz*math.sin(math.tau*i/n)) for y,rx,rz,z in sections for i in range(n)]
  faces=[tuple(reversed(range(n))),tuple(range((len(sections)-1)*n,len(sections)*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(sections)-1) for i in range(n)]
  a=len(g.faces);g.add(v,faces,'M_DolphinBack')
  for k in range(a,len(g.faces)):
   z=sum(g.vertices[i][2] for i in g.faces[k])/len(g.faces[k]);g.colours[k]='M_PaleBelly' if z<-.12 else 'M_DolphinSide' if z<.03 else 'M_DolphinBack'
  g.tube([(0,-.91,-.015),(0,-1.12,-.035),(0,-1.24,-.04)],[.073,.06,.035],8,'M_DolphinSide')
  # A small quiet mouth line follows the beak; no teeth or cartoon grin.
  for s in (-1,1):
   g.beam((s*.05,-1.20,-.055),(s*.068,-.99,-.055),.009,.008,'M_Eye')
   g.ellipsoid((s*.173,-.80,.056),(.013,.024,.018),6,2,'M_Eye')
  fin(g,[(0,-.12,.19),(0,-.025,.45),(0,.055,.53),(0,.10,.51),(0,.13,.36),(0,.30,.17)],.055,'M_DolphinBack')
 part('Body',body)
 def tail():
  # Horizontal paired flukes, shallow centre notch, rounded tips.
  for s in (-1,1):fin(g,[(0,.91,-.07),(s*.19,1.02,-.045),(s*.43,1.10,-.015),(s*.48,1.18,-.02),(s*.34,1.22,-.04),(s*.06,1.14,-.08),(0,1.17,-.085)],.027,'M_DolphinBack',2)
 part('Tail',tail)
 for s,n in [(-1,'L'),(1,'R')]:
  part('Flipper.'+n,lambda s=s:fin(g,[(s*.19,-.43,-.12),(s*.37,-.21,-.22),(s*.50,.04,-.26),(s*.47,.10,-.25),(s*.34,.03,-.18),(s*.16,-.19,-.16)],.035,'M_DolphinSide',2))
 return g,tags,[('Root',(0,0,0),None),('Body',(0,0,0),'Root'),('Tail',(0,.80,-.09),'Body'),('Flipper.L',(-.20,-.40,-.12),'Body'),('Flipper.R',(.20,-.40,-.12),'Body')]
def gannet():
 g=G();tags=[]
 def part(n,fn):
  a=len(g.vertices);fn();tags.append((a,len(g.vertices),n))
 def body():
  g.ellipsoid((0,0,1.1),(.10,.24,.10),8,3,'M_Ivory');g.tube([(0,.16,1.09),(0,.44,1.08)],[.075,.012],6,'M_Ivory')
  g.tube([(0,-.14,1.12),(0,-.30,1.16)],[.06,.044],6,'M_Ivory');g.ellipsoid((0,-.32,1.17),(.062,.086,.061),8,2,'M_BuffHead');g.tube([(0,-.38,1.165),(0,-.57,1.155)],[.027,.003],6,'M_Bill')
  for s in (-1,1):g.ellipsoid((s*.056,-.346,1.185),(.009,.014,.009),4,1,'M_Eye')
 part('Body',body)
 for s,n in [(-1,'L'),(1,'R')]:
  def wing(s=s):
   fin(g,[(s*.07,-.08,1.12),(s*.43,-.115,1.14),(s*.77,-.08,1.13),(s*.72,.025,1.12),(s*.44,.08,1.10),(s*.13,.14,1.08)],.018,'M_Ivory',2)
   fin(g,[(s*.73,-.08,1.13),(s*1.01,-.025,1.115),(s*1.035,.025,1.10),(s*.98,.052,1.10),(s*.89,.035,1.11),(s*.84,.09,1.10),(s*.73,.06,1.11),(s*.65,.08,1.10)],.018,'M_Wingtip',2)
  part('Wing.'+n,wing)
 return g,tags,[('Root',(0,0,0),None),('Body',(0,0,1.1),'Root'),('Wing.L',(-.08,-.08,1.12),'Body'),('Wing.R',(.08,-.08,1.12),'Body')]
def basking():
 g=G();tags=[]
 def rounded_fin(sections,col,bone):
  # Elliptical horizontal sections: broad fleshy base, swept rounded crown.
  a=len(g.vertices);n=8
  v=[(rx*math.cos(math.tau*i/n),cy+ry*math.sin(math.tau*i/n),z) for z,cy,rx,ry in sections for i in range(n)]
  faces=[tuple(reversed(range(n))),tuple(range((len(sections)-1)*n,len(sections)*n))]
  faces += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(sections)-1) for i in range(n)]
  g.add(v,faces,col);tags.append((a,len(g.vertices),bone))
 rounded_fin([(-.09,.025,.145,.285),(0,.025,.125,.265),(.16,.035,.100,.203),(.34,.075,.069,.128),(.49,.115,.039,.065),(.555,.135,.017,.027)],'M_SharkWarm','Body')
 rounded_fin([(-.10,1.675,.100,.185),(0,1.710,.083,.150),(.12,1.765,.065,.113),(.25,1.820,.043,.078),(.345,1.870,.026,.040),(.385,1.890,.012,.018)],'M_SharkShade','Tail')
 return g,tags,[('Root',(0,0,0),None),('Body',(0,0,0),'Root'),('Tail',(0,1.55,0),'Root')]
def rig_asset(kind,root,prefix=None):
 g,tags,spec={'Dolphin':dolphin,'GannetDive':gannet,'BaskingFin':basking}[kind]();prefix=prefix or kind
 ar=bpy.data.armatures.new(prefix+'Skeleton');rig=bpy.data.objects.new(prefix+'Rig',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=root
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 for n,h,par in spec:
  b=ar.edit_bones.new(n);b.head=h;b.tail=Vector(h)+Vector((0,.06,0))
  if par:b.parent=ar.edit_bones[par]
 bpy.ops.object.mode_set(mode='OBJECT');skin=mesh(g,prefix+'Skin',rig);mod=skin.modifiers.new('LegacySkin','ARMATURE');mod.object=rig
 for n,_,_ in spec:skin.vertex_groups.new(name=n);rig.pose.bones[n].rotation_mode='XYZ'
 for a,b,n in tags:skin.vertex_groups[n].add(list(range(a,b)),1,'REPLACE')
 for action,(end,loop) in CLIPS[kind].items():
  act=bpy.data.actions.get(action) or bpy.data.actions.new(action);act.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=act
  # Shared pod actions have identical local curves; physical placements remain independent.
  if prefix!='Dolphin_1' and prefix.startswith('Dolphin_'):
   rig.animation_data.action_slot=act.slots[0];continue
  for f in range(1,end+1):
   t=(f-1)/(end-1);wave=math.sin(math.tau*t)
   for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
   body=rig.pose.bones['Body']
   if kind=='Dolphin':
    if action=='Swim':body.location.z=.05*wave;body.rotation_euler.x=.065*wave;rig.pose.bones['Tail'].rotation_euler.x=.22*math.sin(math.tau*t+.5)
    else:
     body.location.z=1.65*math.sin(math.pi*t)**2;body.location.y=-1.5*(t-.5)*math.sin(math.pi*t)**2;body.rotation_euler.x=-.70*math.sin(math.tau*t);rig.pose.bones['Tail'].rotation_euler.x=.16*wave
    for s,n in [(-1,'L'),(1,'R')]:rig.pose.bones['Flipper.'+n].rotation_euler.y=s*.08*wave
   elif kind=='GannetDive':
    if action=='Glide':
     body.location.z=.035*wave
     for s,n in [(-1,'L'),(1,'R')]:rig.pose.bones['Wing.'+n].rotation_euler.y=s*.045*wave
    else:
     bend=min(1,t/.45);bend=bend*bend*(3-2*bend);body.rotation_euler.x=math.pi/2*bend;body.location.z=-2.25*t*t
     for s,n in [(-1,'L'),(1,'R')]:rig.pose.bones['Wing.'+n].rotation_euler.z=s*1.37*bend
   else:body.location.x=.055*wave;body.rotation_euler.y=.075*wave;rig.pose.bones['Tail'].location.x=.085*math.sin(math.tau*t+.4)
   for pb in rig.pose.bones:
    for prop in ('location','rotation_euler','scale'):pb.keyframe_insert(prop,frame=f,group=pb.name)
  for fc in act.layers[0].strips[0].channelbag(rig.animation_data.action_slot).fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
   if loop:fc.modifiers.new('CYCLES')
  act['loop']=loop;act['legacy']=True
 rig.animation_data.action=bpy.data.actions[next(iter(CLIPS[kind]))];rig.animation_data.action_slot=rig.animation_data.action.slots[0];rig['legacy_import']=True
 return rig

def pod(root):
 for i,(x,y) in enumerate([(-1.10,.50),(0,-.60),(1.1,.20)],1):
  n=empty('Dolphin_'+str(i),root);n.location=(x,y,0);rig_asset('Dolphin',n,'Dolphin_'+str(i))
def splash(root):
 g=G();n=12;v=[]
 for r,z in [(.34,-.025),(.29,.06),(.24,.24),(.18,.025)]:
  for i in range(n):
   a=math.tau*i/n;v.append((r*math.cos(a),r*math.sin(a),z+(.12 if z==.24 and i%2==0 else -.10 if z==.24 else 0)))
 faces=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)];faces += [(i,3*n+i,3*n+(i+1)%n,(i+1)%n) for i in range(n)];g.add(v,faces,'M_Ivory')
 for i in range(4):
  a=i*math.tau/4+.4;g.ellipsoid((.32*math.cos(a),.32*math.sin(a),.35),(.022,.022,.055),4,1,'M_Ivory')
 mesh(g,'DiveSplashCrown',root)
def crate(root):
 g=G()
 for i in range(5):g.box((-.24+i*.12,0,-.10),(.105,.58,.05),'M_Wood' if i%2 else 'M_WoodLight')
 for y in (-.29,.29):
  for j in range(3):
   z=-.06+j*.10
   if y<0 and j==2:
    # Two splintered pieces leave a broad real broken-slat gap.
    g.extrude_polygon([(-.31,y-.025),(-.07,y-.025),(-.12,y+.025),(-.31,y+.025)],z-.035,z+.035,'M_Wood')
    g.extrude_polygon([(.09,y-.025),(.31,y-.025),(.31,y+.025),(.05,y+.025)],z-.035,z+.035,'M_Wood')
   else:g.box((0,y,z),(.64,.05,.07),'M_Wood' if j!=2 else 'M_WoodLight')
 for x in (-.295,.295):
  for j in range(3):g.box((x,0,-.06+j*.10),(.05,.58,.07),'M_Wood')
  for y in (-.26,.26):g.box((x,y,.025),(.045,.05,.32),'M_WoodDark')
 mesh(g,'BrokenFishCrate',root)
def buoy(root):
 g=G();a=len(g.faces);g.ellipsoid((0,0,.055),(.22,.22,.25),10,4,'M_Orange')
 for i in range(a,len(g.faces)):
  z=sum(g.vertices[j][2] for j in g.faces[i])/len(g.faces[i])
  if .07<z<.18:g.colours[i]='M_Ivory'
 g.tube([(0,0,.27),(0,0,.35)],[.045,.032],6,'M_Orange');mesh(g,'OrangeNetFloat',root)
 g=G()
 # Loose open lattice draped through waterline; broad lines remain legible at sailing scale.
 for axis in (0,1):
  for k in range(5):
   q=-.29+k*.145;path=[]
   for j in range(6):
    t=-.36+j*.145;x,y=(q,t) if axis==0 else (t,q);path.append((x+.075*math.sin(4*y),y,-.08-.19*(x*x+y*y)/.20+.04*math.sin(8*x+4*y)))
   g.tube(path,[.012]*6,4,'M_Net' if k%2 else 'M_NetDark')
 g.tube([(-.35,-.25,-.13),(-.24,-.30,-.03),(-.12,-.23,.07),(0,-.10,.18),(.05,0,.24)],[.019]*5,5,'M_NetDark');mesh(g,'TangledNet',root)
def log(root):
 g=G();path=[(0,-.9,-.015),(.035,-.65,0),(-.01,-.10,.025),(.02,.48,.012),(0,.9,0)];g.tube(path,[.12,.16,.18,.15,.11],9,'M_Log')
 # End-grain disks and a broken branch, restrained geometric bark ridges.
 g.tube([(0,-.905,-.015),(0,-.92,-.015)],[.105,.10],9,'M_LogEnd');g.tube([(0,.90,0),(0,.915,0)],[.095,.09],9,'M_LogEnd')
 g.tube([(.10,.21,.08),(.25,.27,.20),(.31,.32,.22)],[.075,.048,.04],7,'M_Log')
 for s in (-1,1):g.beam((s*.12,-.58,.05),(s*.13,.61,.07),.023,.018,'M_WoodDark')
 mesh(g,'WeatheredLog',root);seat=empty('GullSeat',root);seat.location=(0,-.23,.19)
 # Included simple perched gull; seat is a stable contact pivot for replacement/animation.
 g=G();g.ellipsoid((0,0,.13),(.075,.14,.11),8,2,'M_Ivory');g.ellipsoid((0,-.11,.26),(.052,.062,.054),6,2,'M_Ivory');g.tube([(0,-.16,.25),(0,-.25,.24)],[.018,.004],5,'M_BuffHead')
 for s in (-1,1):
  g.ellipsoid((s*.065,.03,.14),(.022,.10,.045),6,2,'M_Bill');g.beam((s*.03,0,.06),(s*.03,-.02,.008),.012,.012,'M_BuffHead')
 g.tube([(0,.1,.12),(0,.23,.08)],[.045,.008],5,'M_Wingtip');mesh(g,'PerchedGull',seat)
def sail(root):
 g=G();n=8;v=[]
 for z,w,l in [(-.09,.18,.55),(.12,.31,.77)]:v.extend((w*math.sin(math.tau*i/n),l*math.cos(math.tau*i/n),z) for i in range(n))
 g.add(v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'M_Navy');g.box((0,0,.10),(.37,.99,.035),'M_Wood')
 g.tube([(0,-.10,.12),(0,-.10,1.78)],[.022,.014],6,'M_WoodDark');g.beam((0,-.10,.39),(.02,.66,.39),.025,.025,'M_WoodDark')
 fin(g,[(.008,-.07,1.69),(.008,.64,.43),(.008,-.07,.43)],.016,'M_Ivory');fin(g,[(0,-.14,1.57),(0,-.66,.42),(0,-.14,.42)],.016,'M_Ivory')
 g.beam((0,-.65,.16),(0,-.10,1.70),.009,.009,'M_Rope');mesh(g,'DistantDinghy',root)
BUILD={'Dolphin':lambda r:rig_asset('Dolphin',r),'DolphinPod':pod,'GannetDive':lambda r:rig_asset('GannetDive',r),'DiveSplash':splash,'BaskingFin':lambda r:rig_asset('BaskingFin',r),'FloatingCrate':crate,'DriftNetBuoy':buoy,'DriftLog':log,'DistantSail':sail}
def snapshot():
 bpy.context.view_layer.update();obs=list(bpy.context.scene.objects);rows={}
 for o in obs:
  if o.type!='MESH':continue
  pts=[o.matrix_world@v.co for v in o.data.vertices];rows[o.name]={'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'world_min_m':[min(p[i] for p in pts) for i in range(3)],'world_max_m':[max(p[i] for p in pts) for i in range(3)],'materials':[m.name for m in o.data.materials]}
 pts=[o.matrix_world@v.co for o in obs if o.type=='MESH' for v in o.data.vertices]
 return {'triangles':sum(v['triangles'] for v in rows.values()),'mesh_bounds':rows,'parents':{o.name:o.parent.name if o.parent else None for o in obs},'bounds_unity':[[min((p.x,p.z,-p.y)[i] for p in pts) for i in range(3)],[max((p.x,p.z,-p.y)[i] for p in pts) for i in range(3)]],'materials':sorted({m.name for o in obs if o.type=='MESH' for m in o.data.materials})}
def run(name):
 O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=30
 H.PALETTE=P;H.MATERIALS={n:H.material(n,c,.48 if n.startswith('M_Dolphin') else .78) for n,c in P.items()};root=empty(name);BUILD[name](root);sc.frame_set(1)
 row=snapshot();assert row['triangles']<=LIMITS[name],(name,row['triangles'],LIMITS[name])
 for m in list(bpy.data.materials):
  if m.users==0:bpy.data.materials.remove(m)
 sc.frame_start=1;sc.frame_end=max([e for e,l in CLIPS.get(name,{}).values()] or [1]);bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')));bpy.ops.object.select_all(action='SELECT')
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=name in CLIPS,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_step=1,bake_anim_simplify_factor=0,use_custom_props=True,colors_type='LINEAR')
 row.update(name=name,limit=LIMITS[name],clips={n:{'seconds':(e-1)/30,'loop':l,'frames':[1,e]} for n,(e,l) in CLIPS.get(name,{}).items()},sha256={e:sha(O/(name+'.'+e)) for e in ('blend','fbx')},palette=P);(O/'metrics'/(name+'-build.json')).write_text(json.dumps(row,indent=2)+'\n');print('OPEN SEA BUILT',name,row['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])

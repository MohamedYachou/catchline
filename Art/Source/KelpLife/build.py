"""KELP-LIFE-ART-1. Deterministic source geometry, rig and metre-scale FBX."""
import bpy,sys,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/KelpLife'
sys.path.insert(0,str(R/'Art/Source'));import build_crab_coast_props as H
G=H.Geometry
P={'M_OtterBrown':'#705040','M_OtterCream':'#C8C3AF','M_OtterPaw':'#50392E','M_Rubber':'#28343B','M_KelpGreen':'#3D573B','M_KelpGold':'#536D3D','M_KelpBulb':'#8C7949'}
LIMITS={'SeaOtter':700,'OtterRaft':2800,'KelpMat':700}
CLIPS={'Float':(121,True),'Groom':(61,True),'Dive':(37,False)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def empty(n,parent=None):
 o=bpy.data.objects.new(n,None);bpy.context.scene.collection.objects.link(o);o.parent=parent;return o
def mesh(g,n,parent):
 o=g.object(n,parent,bpy.context.scene.collection)
 used=sorted({p.material_index for p in o.data.polygons});mats=[o.data.materials[i] for i in used];ids=[used.index(p.material_index) for p in o.data.polygons];o.data.materials.clear()
 for m in mats:o.data.materials.append(m)
 for p,i in zip(o.data.polygons,ids):p.material_index=i
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 return o
def otter():
 g=G();tags=[]
 def tag(st,n):tags.append((st,len(g.vertices),n))
 st=0;start=len(g.faces)
 g.ellipsoid((0,.025,.012),(.172,.310,.143),10,3,'M_OtterBrown')
 # Face assignment on the actual body avoids floating cream overlay shells.
 for i in range(start,len(g.faces)):
  c=sum((Vector(g.vertices[v]) for v in g.faces[i]),Vector())/len(g.faces[i])
  if c.z>.08 and c.y<.06:g.colours[i]='M_OtterCream'
 for s in (-1,1):
  g.ellipsoid((s*.12,.279,.015),(.095,.115,.042),6,2,'M_OtterPaw')
 tag(st,'Body');st=len(g.vertices)
 g.tube([(0,.255,-.018),(0,.44,-.035),(0,.61,-.045)],[.073,.043,.008],6,'M_OtterBrown');tag(st,'Tail')
 st=len(g.vertices);head_start=st;face_start=len(g.faces)
 g.ellipsoid((0,-.322,.135),(.143,.158,.137),10,3,'M_OtterBrown')
 for i in range(face_start,len(g.faces)):
  c=sum((Vector(g.vertices[v]) for v in g.faces[i]),Vector())/len(g.faces[i])
  if c.z>.16:g.colours[i]='M_OtterCream'
 head_faces=g.faces[face_start:]
 def face_z(x,y):
  from mathutils.geometry import intersect_ray_tri
  hits=[]
  for f in head_faces:
   for j in range(1,len(f)-1):
    h=intersect_ray_tri(Vector(g.vertices[f[0]]),Vector(g.vertices[f[j]]),Vector(g.vertices[f[j+1]]),Vector((0,0,-1)),Vector((x,y,1)),True)
    if h is not None:hits.append(h.z)
  assert hits,(x,y)
  return max(hits)
 # Compact two-lobed muzzle, bead eyes and tiny round ears; no whisker noise.
 for s in (-1,1):
  g.ellipsoid((s*.035,-.410,.235),(.051,.057,.038),6,2,'M_OtterCream')
  x,y=s*.072,-.359;g.ellipsoid((x,y,face_z(x,y)+.003),(.012,.015,.008),6,1,'M_Rubber')
  g.ellipsoid((s*.130,-.267,.174),(.034,.032,.037),6,2,'M_OtterBrown')
 g.ellipsoid((0,-.444,.266),(.028,.021,.015),6,1,'M_Rubber')
 tag(st,'Head')
 for s,n in [(-1,'Paw.L'),(1,'Paw.R')]:
  st=len(g.vertices)
  g.tube([(s*.14,-.19,.075),(s*.14,-.115,.151),(s*.064,-.137,.205)],[.042,.039,.030],6,'M_OtterBrown')
  g.ellipsoid((s*.059,-.148,.210),(.043,.052,.030),6,2,'M_OtterPaw');tag(st,n)
 return g,tags
def sea(root):
 g,tags=otter();skin=mesh(g,'SeaOtterSkin',root)
 ar=bpy.data.armatures.new('SeaOtterSkeleton');rig=bpy.data.objects.new('SeaOtterRig',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=root
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 spec=[('Root',(0,0,0),None),('Body',(0,0,0),'Root'),('Head',(0,-.215,.1),'Body'),('Tail',(0,.255,-.018),'Body'),('Paw.L',(-.14,-.19,.075),'Body'),('Paw.R',(.14,-.19,.075),'Body')]
 for n,h,par in spec:
  b=ar.edit_bones.new(n);b.head=h;b.tail=Vector(h)+Vector((0,.05,0))
  if par:b.parent=ar.edit_bones[par]
 bpy.ops.object.mode_set(mode='OBJECT');skin.parent=rig;mod=skin.modifiers.new('SeaOtterSkinning','ARMATURE');mod.object=rig
 for n,_,_ in spec:skin.vertex_groups.new(name=n);rig.pose.bones[n].rotation_mode='XYZ'
 for a,b,n in tags:skin.vertex_groups[n].add(list(range(a,b)),1,'REPLACE')
 sc=bpy.context.scene;sc.render.fps=30
 for name,(end,loop) in CLIPS.items():
  act=bpy.data.actions.new(name);act.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=act
  for f in range(1,end+1):
   t=(f-1)/(end-1)
   for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
   body=rig.pose.bones['Body']
   if name=='Float':
    body.location.z=.012*math.sin(math.tau*t);body.rotation_euler.y=math.radians(5)*math.sin(math.tau*t)
    rig.pose.bones['Head'].rotation_euler.z=math.radians(5)*math.sin(math.tau*t)
   elif name=='Groom':
    # Both short forearms rotate at the shoulders into the face, then rub.
    a=math.radians(48)*(math.sin(math.pi*t)**2)
    for s,n in [(-1,'Paw.L'),(1,'Paw.R')]:
     rig.pose.bones[n].rotation_euler.x=a
     rig.pose.bones[n].rotation_euler.y=s*math.radians(10)*math.sin(4*math.tau*t)*math.sin(math.pi*t)**2
    rig.pose.bones['Head'].rotation_euler.x=-math.radians(5)*math.sin(math.pi*t)**2
   else:
    smooth=t*t*(3-2*t);body.rotation_euler.y=math.pi*smooth;body.location.z=-1.05*smooth
    rig.pose.bones['Tail'].rotation_euler.x=math.radians(20)*math.sin(math.pi*t)
   for pb in rig.pose.bones:
    for prop in ('location','rotation_euler','scale'):pb.keyframe_insert(prop,frame=f,group=pb.name)
  for fc in act.layers[0].strips[0].channelbag(rig.animation_data.action_slot).fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
   if loop:fc.modifiers.new('CYCLES')
  act['loop']=loop;act['seconds']=(end-1)/30
 rig.animation_data.action=bpy.data.actions['Float'];sc.frame_start=1;sc.frame_end=121;sc.frame_set(1)
 return {'pivot':'fixed waterline centre, through torso; body partly submerged','forward':'Blender -Y / Unity +Z (head)','rig':'SeaOtterRig','bones':[n for n,_,_ in spec],'clips':{n:{'frames':[1,e],'seconds':(e-1)/30,'loop':l} for n,(e,l) in CLIPS.items()},'root_motion':False,'dive':'Body rolls180deg longitudinally and sinks1.05m; root stays at waterline. Hide/reset after once clip.'}
def kelp(g,width,depth):
 rng=random.Random(11041)
 # Fifteen slender straps with three broad waves, rounded taper and gentle roll.
 # Nine samples resolve the soft curves rather than making broad folded cards.
 for j in range(15):
  a=(j%5)*.47+(.75 if j%2 else -.55);cx=rng.uniform(-.78,.78);cy=rng.uniform(-.40,.40);length=rng.uniform(.85,1.65);w=rng.uniform(.028,.047)
  phase=j*.71;verts=[]
  for k in range(10):
   t=k/9;u=(t-.5)*length;v=.08*math.sin(math.tau*t+phase)+.025*math.sin(2*math.tau*t+phase)
   half=w*(.18+.82*math.sin(math.pi*t)**.55)
   z=.009+.002*(j%4)+.009*math.sin(math.tau*t+phase)
   roll=.10*math.sin(math.tau*t+phase)
   for side in (-1,1):verts.append((cx+u*math.cos(a)-(v+side*half)*math.sin(a),cy+u*math.sin(a)+(v+side*half)*math.cos(a),z+side*half*roll))
  g.add(verts,[(2*k,2*k+1,2*k+3,2*k+2) for k in range(9)],'M_KelpGold' if j%3==0 else 'M_KelpGreen')
 # Preserve metre footprint and bulbs; overlapping slender straps leave water gaps.
 lo=[min(v[i] for v in g.vertices) for i in range(2)];hi=[max(v[i] for v in g.vertices) for i in range(2)]
 g.vertices=[((v[0]-lo[0])/(hi[0]-lo[0])*width-width/2,(v[1]-lo[1])/(hi[1]-lo[1])*depth-depth/2,v[2]) for v in g.vertices]
 for x,y in [(-width*.33,depth*.16),(width*.32,-depth*.20)]:
  g.ellipsoid((x,y,.033),(.105,.073,.065),8,2,'M_KelpBulb')
 return g
def mat_only(root):
 mesh(kelp(G(),2.5,1.6),'KelpMatMesh',root)
 return {'pivot':'waterline centre','footprint_m':[2.5,1.6],'static':True,'kelp_ribbons':15,'float_bulbs':2,'shader':'Opaque matte, TWO SIDED leaves. Very shallow noncoplanar ribbons, no texture.'}
def raft(root):
 mesh(kelp(G(),3,2),'RaftKelp',root)
 # Two adults and one pup, three total; pup rests on port adult chest.
 for n,scale,x,y,z,a in [('AdultA',1,-.43,-.01,.038,-.17),('AdultB',1,.48,.16,.036,.22),('Pup',.47,-.44,-.12,.258,-.48)]:
  g,_=otter();g.vertices=[(x+scale*(u*math.cos(a)-v*math.sin(a)),y+scale*(u*math.sin(a)+v*math.cos(a)),z+scale*w) for u,v,w in g.vertices];mesh(g,n,root)
 return {'pivot':'waterline centre','footprint_m':[3,2],'otters':3,'adults':2,'pups':1,'pup_scale':.47,'static':True,'animation':'Static raft pose. Runtime may gently bob/roll whole root; spawn animated SeaOtter separately for individual behaviours.','kelp_ribbons':15,'float_bulbs':2,'shader':'Opaque matte, TWO SIDED kelp leaves.'}
BUILD={'SeaOtter':sea,'OtterRaft':raft,'KelpMat':mat_only}
def snapshot():
 bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 return {'triangles':sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),'vertices':sum(len(o.data.vertices) for o in meshes),'bounds_unity':[[min((v.x,v.z,-v.y)[i] for v in pts) for i in range(3)],[max((v.x,v.z,-v.y)[i] for v in pts) for i in range(3)]],'meshes':[o.name for o in meshes],'materials':sorted({m.name for o in meshes for m in o.data.materials}),'parents':{o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects},'mesh_bounds_unity':{o.name:[[min((v.x,v.z,-v.y)[i] for v in [o.matrix_world@v.co for v in o.data.vertices]) for i in range(3)],[max((v.x,v.z,-v.y)[i] for v in [o.matrix_world@v.co for v in o.data.vertices]) for i in range(3)]] for o in meshes}}
def run(name):
 O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=30
 H.PALETTE=P;H.MATERIALS={n:H.material(n,c,.80) for n,c in P.items()};root=empty(name);contract=BUILD[name](root);row=snapshot();assert row['triangles']<=LIMITS[name],(name,row['triangles'])
 for m in list(bpy.data.materials):
  if m.users==0:bpy.data.materials.remove(m)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')));bpy.ops.object.select_all(action='SELECT')
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_space_transform=name!='SeaOtter',use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=name=='SeaOtter',bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_step=1,bake_anim_simplify_factor=0,use_custom_props=True,colors_type='LINEAR')
 row.update(name=name,contract=contract,limit=LIMITS[name],sha256={e:sha(O/(name+'.'+e)) for e in ('blend','fbx')},palette=P);(O/'metrics'/(name+'-build.json')).write_text(json.dumps(row,indent=2)+'\n');print('KELP BUILT',name,row['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])

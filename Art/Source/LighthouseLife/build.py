"""LIGHTHOUSE-LIFE-1: deterministic low-poly metre assets, owned trees only."""
import bpy,sys,math,json,hashlib,random
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/LighthouseLife'
sys.path.insert(0,str(R/'Art/Source'));import build_crab_coast_props as H
G=H.Geometry
P={'M_GullWhite':'#F1F0EA','M_Rubber':'#28343B','M_SafetyOrange':'#E36A35','M_CardinalYellow':'#F2C14E','M_Steel':'#8FA6AC','M_WaterTeal':'#2E8C8A','M_LampGlow':'#FFE7A3'}
LIMITS={'Puffin':600,'PuffinGroup':2000,'TideRace':400,'LighthouseGlow':160}
CLIPS={'Idle':(91,True),'Flap':(13,True)}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def empty(n,parent=None):
 o=bpy.data.objects.new(n,None);bpy.context.scene.collection.objects.link(o);o.parent=parent;return o

def mesh(g,n,parent):
 o=g.object(n,parent,bpy.context.scene.collection)
 used=sorted({p.material_index for p in o.data.polygons});mats=[o.data.materials[i] for i in used];ix=[used.index(p.material_index) for p in o.data.polygons];o.data.materials.clear()
 for m in mats:o.data.materials.append(m)
 for p,i in zip(o.data.polygons,ix):p.material_index=i
 import bmesh
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 return o

def loft(g,rows,col,cap=True):
 n=len(rows[0]);fs=[tuple(reversed(range(n)))] if cap else []
 fs += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rows)-1) for i in range(n)]
 if cap:fs.append(tuple(range((len(rows)-1)*n,len(rows)*n)))
 g.add(sum(rows,[]),fs,col)

def bird():
 g=G();tags=[]
 def tag(st,n):tags.append((st,len(g.vertices),n))
 # Fixed webbed feet keep the contact pivot on the rock during the body bob.
 for s in (-1,1):
  x=s*.032;g.beam((x,.005,.014),(x,.005,.049),.014,.014,'M_SafetyOrange')
  outline=[(-.018,-.044),(.003,-.049),(.023,-.039),(.020,-.013),(.012,.023),(-.012,.020)]
  loft(g,[[(x+u,v,z) for u,v in outline] for z in (0,.014)],'M_SafetyOrange')
 tag(0,'Root');st=len(g.vertices)
 g.ellipsoid((0,.007,.125),(.067,.059,.105),10,3,'M_Rubber')
 # Ivory belly follows the actual faceted body triangles rather than floating in front.
 # Use the front half of the same mesh as a material region.
 body_start=st
 for i,f in enumerate(g.faces):
  if all(v>=body_start for v in f):
   c=sum((Vector(g.vertices[v]) for v in f),Vector())/len(f)
   if c.y<-.016 and c.z<.190:g.colours[i]='M_GullWhite'
 loft(g,[[(-.027,.046,.055),(.027,.046,.055),(.023,.094,.040),(-.023,.094,.040)],[(-.026,.047,.064),(.026,.047,.064),(.020,.100,.046),(-.020,.100,.046)]],'M_Rubber');tag(st,'Body')
 st=len(g.vertices);head_start=st;g.ellipsoid((0,-.027,.244),(.057,.055,.056),10,3,'M_Rubber')
 for i,f in enumerate(g.faces):
  if all(v>=head_start for v in f):
   c=sum((Vector(g.vertices[v]) for v in f),Vector())/len(f)
   if c.y<.004 and c.z<.279:g.colours[i]='M_GullWhite'
 head_faces=[f for f in g.faces if all(v>=head_start for v in f)]
 def cheek_x(sign,y,z):
  from mathutils.geometry import intersect_ray_tri
  hits=[]
  for f in head_faces:
   for j in range(1,len(f)-1):
    h=intersect_ray_tri(Vector(g.vertices[f[0]]),Vector(g.vertices[f[j]]),Vector(g.vertices[f[j+1]]),Vector((-sign,0,0)),Vector((sign*.2,y,z)),True)
    if h is not None:hits.append(h.x)
  assert hits,(sign,y,z)
  return max(hits) if sign>0 else min(hits)
 # Five material bands cross the broad deep bill. No texture or tiny floating stripe cards.
 sections=[(-.071,.023,.221,.270),(-.080,.025,.221,.270),(-.086,.025,.222,.268),(-.112,.020,.227,.260),(-.118,.018,.229,.256),(-.152,.001,.237,.240)]
 for j,col in enumerate(['M_Steel','M_GullWhite','M_SafetyOrange','M_CardinalYellow','M_SafetyOrange']):
  loft(g,[[(-w,y,lo),(w,y,lo),(w,y,hi),(-w,y,hi)] for y,w,lo,hi in sections[j:j+2]],col,cap=j in [0,4])
 for s in (-1,1):
  g.ellipsoid((cheek_x(s,-.051,.257)-s*.0015,-.051,.257),(.0025,.0045,.005),6,1,'M_Rubber')
  g.add([(cheek_x(s,y,z)+s*.00025,y,z) for y,z in [(-.051,.250),(-.055,.242),(-.047,.246)]],[(0,1,2)],'M_SafetyOrange')
 tag(st,'Head')
 for s,n in [(-1,'Wing.L'),(1,'Wing.R')]:
  st=len(g.vertices);poly=[(s*.045,-.006,.198),(s*.070,-.023,.178),(s*.079,-.010,.132),(s*.070,.043,.064),(s*.060,.067,.085),(s*.045,.040,.163)]
  loft(g,[[(x-s*.003,y,z) for x,y,z in poly],[(x+s*.004,y,z) for x,y,z in poly]],'M_Rubber');tag(st,n)
 return g,tags

def puffin(root):
 g,tags=bird();skin=mesh(g,'PuffinSkin',root)
 ar=bpy.data.armatures.new('PuffinSkeleton');rig=bpy.data.objects.new('PuffinRig',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=root
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 spec=[('Root',(0,0,0),None),('Body',(0,0,.10),'Root'),('Head',(0,-.025,.216),'Body'),('Wing.L',(-.046,.005,.193),'Body'),('Wing.R',(.046,.005,.193),'Body')]
 for n,h,par in spec:
  b=ar.edit_bones.new(n);b.head=h;b.tail=Vector(h)+Vector((0,.04,0))
  if par:b.parent=ar.edit_bones[par]
 bpy.ops.object.mode_set(mode='OBJECT');skin.parent=rig;mod=skin.modifiers.new('PuffinSkinning','ARMATURE');mod.object=rig
 for n,_,_ in spec:skin.vertex_groups.new(name=n);rig.pose.bones[n].rotation_mode='XYZ'
 for a,b,n in tags:skin.vertex_groups[n].add(list(range(a,b)),1,'REPLACE')
 sc=bpy.context.scene;sc.render.fps=30
 for name,(end,loop) in CLIPS.items():
  act=bpy.data.actions.new(name);act.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=act
  for f in range(1,end+1):
   t=(f-1)/(end-1)
   for pb in rig.pose.bones:pb.location=(0,0,0);pb.rotation_euler=(0,0,0);pb.scale=(1,1,1)
   if name=='Idle':
    rig.pose.bones['Body'].location.z=.003*(1-math.cos(math.tau*t))*.5
    rig.pose.bones['Head'].rotation_euler.z=math.radians(18)*math.sin(math.tau*t)
    rig.pose.bones['Head'].rotation_euler.x=math.radians(3)*math.sin(2*math.tau*t)
   else:
    for s,n in [(-1,'Wing.L'),(1,'Wing.R')]:rig.pose.bones[n].rotation_euler.y=-s*math.radians(65+35*math.sin(math.tau*t))
   for pb in rig.pose.bones:
    for prop in ['location','rotation_euler','scale']:pb.keyframe_insert(prop,frame=f,group=pb.name)
  for fc in act.layers[0].strips[0].channelbag(rig.animation_data.action_slot).fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
   fc.modifiers.new('CYCLES')
  act['loop']=True;act['seconds']=(end-1)/30
 rig.animation_data.action=bpy.data.actions['Idle'];sc.frame_start=1;sc.frame_end=91;sc.frame_set(1)
 return {'pivot':'feet contact centre','height_m':.3,'rig':'PuffinRig','bones':[n for n,_,_ in spec],'clips':{n:{'frames':[1,e],'seconds':(e-1)/30,'loop':True} for n,(e,_) in CLIPS.items()},'root_motion':False}

def group(root):
 g=G();outline=[(-.60,-.23),(-.39,-.33),(.38,-.30),(.60,-.14),(.54,.23),(.26,.32),(-.42,.29),(-.58,.10)]
 loft(g,[[(x*.94,y*.94,0) for x,y in outline],[(x,y,.12+.03*x) for x,y in outline],[(x*.86,y*.80,.20+.02*x) for x,y in outline]],'M_Steel')
 for x,y,a in [(-.35,-.025,-.25),(.01,.12,.30),(.35,-.02,1.05)]:
  b,_=bird();b.vertices=[(x+u*math.cos(a)-v*math.sin(a),y+u*math.sin(a)+v*math.cos(a),z+.20+.02*x) for u,v,z in b.vertices];g.merge(b)
 mesh(g,'PuffinGroupMesh',root)
 return {'pivot':'ledge base centre','birds':3,'ledge_width_m':1.2,'static':True,'animation':'Individual animated Puffin is separate; group is a single static mesh for cheap perches.'}

def race(root):
 g=G();rng=random.Random(818)
 # Unequal, oblique broken wavelets: avoid a repeating row/column tile silhouette.
 # Every white crest is an inset copy of a sloping face, never an upright fin.
 pieces=[(-2.48,-.60,1.12,.46,-.18),(-1.19,-.79,.78,.31,.16),(.18,-.57,1.68,.49,-.11),(2.03,-.75,1.20,.34,.29),
         (-2.08,.05,1.65,.57,.14),(-.42,.12,.91,.35,-.26),(1.21,-.05,1.36,.50,.20),(2.63,.13,.64,.31,-.19),
         (-2.61,.72,.70,.34,-.21),(-1.16,.58,1.38,.54,.25),(.43,.77,1.05,.33,-.14),(1.91,.61,1.54,.48,.10)]
 for x,y,L,W,angle in pieces:
  h=rng.uniform(.12,.225)
  uv=[(-.50,-.03),(-.17,-.50),(.50,-.04),(.35,.12),(.07,.50),(-.36,.20)]
  def point(u,v,z):
   return (x+u*L*math.cos(angle)-v*W*math.sin(angle),y+u*L*math.sin(angle)+v*W*math.cos(angle),z)
  vs=[point(u,v,.004) for u,v in uv]
  vs += [point(-.38,.01,.035),point(.02,.11,h),point(.34,.04,.042)]
  g.add(vs,[(0,1,6),(1,7,6),(1,2,7),(2,8,7),(2,3,8),(3,4,8),(4,7,8),(4,5,7),(5,6,7),(5,0,6)],'M_WaterTeal')
  for a,b,c in [(6,7,5),(7,8,4)]:
   p,q,t=[Vector(vs[i]) for i in [a,b,c]];off=Vector((0,0,.0006))
   g.add([p+off,q+off,q*.82+t*.18+off,p*.82+t*.18+off],[(0,1,2),(0,2,3)],'M_GullWhite')
 # Fit exact brief footprint without shifting the waterline pivot or crest heights.
 lo=[min(v[i] for v in g.vertices) for i in range(2)];hi=[max(v[i] for v in g.vertices) for i in range(2)]
 g.vertices=[((v[0]-lo[0])/(hi[0]-lo[0])*6-3,(v[1]-lo[1])/(hi[1]-lo[1])*2-1,v[2]) for v in g.vertices]
 mesh(g,'TideRaceMesh',root)
 return {'pivot':'waterline centre','footprint_m':[6,2],'maximum_crest_m':max(v[2] for v in g.vertices),'animation':'Runtime scrolls local X; twelve unequal oblique low standing-wave fragments, opaque teal facets/white flush crest strips. Two-sided surface shader.'}

def glow(root):
 g=G();alphas=[]
 for plane in ['XZ','YZ']:
  st=len(g.vertices);vs=[]
  for j in range(3):
   for i in range(3):
    a=(i-1)*.45;z=(j-1)*.45;vs.append((a,0,z) if plane=='XZ' else (0,a,z));alphas.append(.48 if i==j==1 else 0.)
  g.add(vs,[(j*3+i,j*3+i+1,(j+1)*3+i+1,(j+1)*3+i) for j in range(2) for i in range(2)],'M_LampGlow')
 mesh(g,'LanternCross',root)
 g=G();levels=[(0,.045,.20),(1,.11,.12),(10.5,.64,.025),(12,.73,0.)];beam_alpha=[]
 rows=[]
 for x,r,a in levels:
  rows.append([(x,r*math.cos(i*math.tau/8),r*math.sin(i*math.tau/8)) for i in range(8)]);beam_alpha += [a]*8
 loft(g,rows,'M_LampGlow',False);mesh(g,'LanternBeam',root)
 mat=H.MATERIALS['M_LampGlow'];rgba=mat.diffuse_color;mat.diffuse_color=(*rgba[:3],1);mat.use_nodes=True
 nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');mix=nt.nodes.new('ShaderNodeMixShader');attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='GlowAlpha';tr=nt.nodes.new('ShaderNodeBsdfTransparent');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(*rgba[:3],1);em.inputs['Strength'].default_value=1.8
 nt.links.new(attr.outputs['Alpha'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
 for name,values in [('LanternCross',alphas),('LanternBeam',beam_alpha)]:
  o=bpy.data.objects[name];c=o.data.color_attributes.new(name='GlowAlpha',type='BYTE_COLOR',domain='POINT')
  for d,a in zip(c.data,values):d.color=(1,1,1,a)
  o['shader_contract']='Shared M_LampGlow #FFE7A3, unlit/additive, vertex alpha GlowAlpha, double-sided, depth write off; no texture.'
 return {'pivot':'lantern centre','beam_axis_blender':'+X','beam_length_m':12,'cross_span_m':.9,'beam_end_radius_m':.73,'vertex_alpha':'GlowAlpha','shader':'Unlit additive/two-sided/no depth write; vertex alpha falloff, no texture. Runtime rotates whole root; FBX cannot carry Blender node graph.'}
BUILD={'Puffin':puffin,'PuffinGroup':group,'TideRace':race,'LighthouseGlow':glow}
def snapshot():
 bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];p=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 return {'triangles':sum(len(f.vertices)-2 for o in meshes for f in o.data.polygons),'vertices':sum(len(o.data.vertices) for o in meshes),'bounds_unity':[[min((v.x,v.z,-v.y)[i] for v in p) for i in range(3)],[max((v.x,v.z,-v.y)[i] for v in p) for i in range(3)]],'meshes':[o.name for o in meshes],'materials':sorted({m.name for o in meshes for m in o.data.materials}),'parents':{o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects}}
def run(name):
 O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=30
 H.PALETTE=P;H.MATERIALS={n:H.material(n,c,.75) for n,c in P.items()};root=empty(name);root['axes']='Blender X,-Y,Z -> Unity X,Z,-Y; metres, logical contact pivot.'
 contract=BUILD[name](root);row=snapshot();assert row['triangles']<=LIMITS[name],(name,row['triangles'])
 for m in list(bpy.data.materials):
  if m.users==0:bpy.data.materials.remove(m)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
 if name=='LighthouseGlow':
  # Export understands Principled; source retains the texture-free soft emission graph.
  mat=H.MATERIALS['M_LampGlow'];rgba=mat.diffuse_color[:];nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Base Color'].default_value=(*rgba[:3],1);bs.inputs['Alpha'].default_value=.20;bs.inputs['Emission Color'].default_value=(*rgba[:3],1);bs.inputs['Emission Strength'].default_value=1.8;nt.links.new(bs.outputs[0],out.inputs[0])
 bpy.ops.object.select_all(action='SELECT')
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_space_transform=name!='Puffin',use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=name=='Puffin',bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_step=1,bake_anim_simplify_factor=0,use_custom_props=True,colors_type='LINEAR')
 row.update(name=name,contract=contract,limit=LIMITS[name],sha256={e:sha(O/(name+'.'+e)) for e in ['blend','fbx']},palette=P);(O/'metrics'/(name+'-build.json')).write_text(json.dumps(row,indent=2)+'\n');print('LIGHTHOUSE BUILT',name,row['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])

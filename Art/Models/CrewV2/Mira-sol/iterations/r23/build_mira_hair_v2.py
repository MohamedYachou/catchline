"""Mira's unlocked full-hair revision. Immutable r20 nonhair, original rig.
Blender5.2 --background --factory-startup --python this-file -- --revision r22 --render all
"""
import argparse,ast,bpy,bmesh,hashlib,json,math,random,struct,sys,zlib,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/CrewV2/Mira-sol';BASE=OUT/'iterations/r20'
sys.path.insert(0,str(ROOT/'Art/Source'))
p=argparse.ArgumentParser();p.add_argument('--revision',default='r22');p.add_argument('--render',choices=['none','quick','all'],default='all');p.add_argument('--samples',type=int,default=32)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);PRE=OUT/'iterations'/a.revision;PRE.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
base_hash={n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in ('Mira.blend','Mira.fbx','Mira_Face.png','Mira_Hair.png','build-manifest.json')}
bpy.ops.wm.open_mainfile(filepath=str(BASE/'Mira.blend'))
scene=bpy.context.scene;arm=bpy.data.objects['CrewRig'];col=arm.users_collection[0];mats={m.name:m for m in bpy.data.materials}
tree=ast.parse((OUT/'iterations/r09/build_mira_sol.py').read_text());nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ('Mesh','catmull','signature','curves')]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'original-mira-primitives','exec'),globals())
man=json.loads((BASE/'build-manifest.json').read_text());contract=signature(arm);assert contract==man['contract']
arm.animation_data.action=None
for bone in arm.pose.bones:bone.matrix_basis.identity()
scene.frame_set(1);bpy.context.view_layer.update()
def fingerprint(ob):
 me=ob.data
 payload=([tuple(v.co) for v in me.vertices],[(tuple(p.vertices),p.material_index,p.use_smooth) for p in me.polygons],
          [m.name for m in me.materials],[[ (ob.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in me.vertices],
          [[tuple(x.uv) for x in uv.data] for uv in me.uv_layers])
 return hashlib.sha256(repr(payload).encode()).hexdigest()
nonhair={n:fingerprint(bpy.data.objects[n]) for n in man['meshes'] if n!='Mira_HairSculpt'}
shutil.copy2(BASE/'Mira_Face.png',OUT/'Mira_Face.png')
# Authored colour-only fibres, without painted illumination.
def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)
raw=bytearray()
for y in range(512):
 raw.append(0);v=y/511
 for x in range(512):
  u=x/511;ph=u*12+.08*math.sin(v*11)+.025*math.sin(v*28)
  fibre=(.5+.5*math.cos(math.tau*ph))**8;groove=(.5+.5*math.sin(math.tau*(ph+.2)))**10
  tone=.95+.24*fibre-.10*groove
  raw.extend(round(c*tone) for c in (72,39,29))
hp=OUT/'Mira_Hair.png';hp.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',512,512,8,2,0,0,0))+chunk(b'sRGB',b'\0')+chunk(b'IDAT',zlib.compress(bytes(raw),9))+chunk(b'IEND',b''))
for im in list(bpy.data.images):
 if im.name.startswith('Mira_Hair'):bpy.data.images.remove(im)
tex=bpy.data.images.load(str(hp),check_existing=False);mat=bpy.data.materials.new('Mira_ThinWaveHair');mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.64
node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=tex;mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);mats[mat.name]=mat
hair=Mesh();hair.quality=1;uvs={};rng=random.Random(6102)
def lock(points,w=.015,d=.005,normal=(0,-1,0),steps=1,sides=6):
 pts=catmull(points,steps);vv=[];local=[]
 for j,pt in enumerate(pts):
  t=j/(len(pts)-1);tangent=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized()
  u=Vector(normal).cross(tangent).normalized()
  if u.length<.1:u=Vector((1,0,0)).cross(tangent).normalized()
  dep=tangent.cross(u).normalized();taper=min(1,.48+t*6,max(.045,(1-t)*5))
  for k in range(sides):
   angle=math.tau*k/sides;vv.append(pt+u*w*taper*math.cos(angle)+dep*d*taper*math.sin(angle));local.append((.02+.96*(.5+.5*math.cos(angle)),.02+.96*t))
 ff=[tuple(reversed(range(sides)))]+[(j*sides+k,j*sides+(k+1)%sides,(j+1)*sides+(k+1)%sides,(j+1)*sides+k) for j in range(len(pts)-1) for k in range(sides)]+[tuple((len(pts)-1)*sides+k for k in range(sides))]
 start=len(hair.v);hair.add(vv,ff,mat.name,'Head')
 for i,uv in enumerate(local):uvs[start+i]=uv
profile=[(.630,.122,.104,.102),(.672,.150,.132,.126),(.713,.169,.146,.142),(.755,.175,.152,.153),(.801,.173,.148,.157),(.842,.165,.138,.152),(.880,.146,.120,.135),(.914,.112,.089,.105),(.940,.063,.048,.059)]
def fitted(angle,z,lift=.008):
 lo,hi=next(((lo,hi) for lo,hi in zip(profile,profile[1:]) if lo[0]<=z<=hi[0]),(profile[-2],profile[-1]));t=max(0,min(1,(z-lo[0])/(hi[0]-lo[0])))
 rx,fr,bk=[lo[k]*(1-t)+hi[k]*t for k in (1,2,3)]
 return Vector(((rx+lift)*math.cos(angle),((fr if math.sin(angle)<0 else bk)+lift)*math.sin(angle),z))
# Thin continuous fitted scalp underneath visible layers: front corners through nape.
N=41;L=10;vv=[]
for j in range(L):
 t=j/(L-1)
 for i in range(N):
  angle=-1.16+(math.pi+2.32)*i/(N-1);bottom=.677+.193*max(0,-math.sin(angle))**2+.004*math.sin(angle*11)
  vv.append(fitted(angle,bottom+(.939-bottom)*t))
ff=[(j*N+i,j*N+i+1,(j+1)*N+i+1,(j+1)*N+i) for j in range(L-1) for i in range(N-1)]
start=len(hair.v);hair.add(vv,ff,mat.name,'Head')
for j in range(L):
 for i in range(N):uvs[start+j*N+i]=(i/(N-1)*6,j/(L-1))
# Each back lock is a narrow independent S curve, ending below its hidden support.
for j in range(22):
 angle=-.55+(math.pi+1.1)*j/21;phase=j*1.71;points=[]
 for k in range(9):
  t=k/8;z=.926-(.275+.025*math.sin(j*1.9))*t
  aa=angle+.13*math.sin(t*math.tau*.9+phase)*math.sin(math.pi*t)
  pt=fitted(aa,max(.633,z),.014+.010*math.sin(math.pi*t));pt.z=z
  pt+=Vector((math.cos(aa),math.sin(aa),0))*.010*math.sin(t*math.tau*1.15+phase)*math.sin(math.pi*t)
  points.append(pt)
 lock(points,.016,.0055,normal=(math.cos(angle),math.sin(angle),0),steps=2)
# Sweep under the visor, preserving an open forehead and the portrait's part.
for side in (-1,1):
 for j in range(4):
  lock([(side*(.006+j*.012),-.098,.928),(side*(.035+j*.014),-.136,.897),(side*(.074+j*.019),-.154,.870),
        (side*(.110+j*.018),-.142,.850-j*.006),(side*(.124+j*.015),-.122,.837-j*.009)],.020-j*.0018,.006,steps=2)
 # A wide shallow corner flow is overlaid with individual thin side waves.
 lock([(side*.063,-.105,.921),(side*.117,-.127,.883),(side*.154,-.111,.847),(side*.171,-.072,.801)],.019,.0055,normal=(side*.8,-.6,0),steps=2)
 for j in range(6):
  points=[]
  for k in range(8):
   t=k/7;z=.913-(.278+.020*math.sin(j*1.7))*t
   x=.127+.045*math.sin(math.pi*t*.86)+.015*math.sin(t*math.tau*1.05+j*.63)*math.sin(math.pi*t)
   y=-.091+j*.021-.013*math.sin(t*math.tau+j*.5)*math.sin(math.pi*t)
   points.append((side*x,y,z))
  lock(points,.013,.0045,normal=(side,0,0),steps=2)
# Full 3D gathered ponytail: outer ring plus staggered inner waves, no flat fan.
for j in range(20):
 angle=math.tau*(j%13)/13;inner=j>=13;radius=.038 if inner else .073
 length=.310+.035*math.sin(j*1.3);points=[]
 for k in range(12):
  t=k/11;grow=math.sin(min(1,t*2.5)*math.pi/2);bulge=math.sin(math.pi*(.12+.88*t))**.65
  cx=.073+.063*grow;cy=.146+.097*grow
  wave=.011*math.sin(t*math.tau*1.05+j*1.7)*math.sin(math.pi*t)
  rx=radius*bulge+wave;ry=radius*.85*bulge+wave*.6
  points.append((cx+rx*math.cos(angle)+.012*math.sin(t*math.tau*1.05+j*.7)*t,
                 cy+ry*math.sin(angle),.886-length*t+.018*max(0,(t-.8)/.2)**2))
 lock(points,.019 if not inner else .017,.0075,normal=(math.cos(angle),math.sin(angle),.05),steps=2)
# Tucked root sections lie within the cap; visible sections retain their volume.
for i,(x,y,z) in enumerate(hair.v):
 if z>.890:
  fit=math.sqrt((x/.163)**2+(y/.142)**2)
  if fit>1:hair.v[i]=(x/fit,y/fit,z)
bpy.data.objects.remove(bpy.data.objects['Mira_HairSculpt'],do_unlink=True)
ob=hair.object('Mira_HairSculpt');uv=ob.data.uv_layers.new(name='ThinWaveFibres')
for loop in ob.data.loops:uv.data[loop.index].uv=uvs.get(loop.vertex_index,(.5,.5))
bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.calc_loop_triangles()
if len(ob.data.loop_triangles)>6450:
 dec=ob.modifiers.new('HairOnlyBudget','DECIMATE');dec.ratio=6448/len(ob.data.loop_triangles);bpy.context.view_layer.objects.active=ob;bpy.ops.object.modifier_apply(modifier=dec.name)
 ob.data.calc_loop_triangles()
meshes=[bpy.data.objects[n] for n in man['meshes']];counts={o.name:len(o.data.loop_triangles) for o in meshes}
for o in meshes:o.data.calc_loop_triangles();counts[o.name]=len(o.data.loop_triangles)
assert sum(counts.values())<=20000,counts
assert {n:fingerprint(bpy.data.objects[n]) for n in nonhair}==nonhair,'r20 nonhair changed'
assert signature(arm)==contract
man.pop('r09_front_hair',None);man.update(revision=a.revision,triangles=sum(counts.values()),meshes=counts,
 r20_preservation={'archive_sha256':base_hash,'five_nonhair_fingerprints':nonhair,'all_nonhair_exact':True,'front_lock_overridden_by':'Mo UPDATE16:55 full hair rework'},
 textures=[{'file':'Mira_Face.png','size':[512,512],'use':'r20 face unchanged'},{'file':'Mira_Hair.png','size':[512,512],'use':'thin-wave authored fibre colour, no lighting'}],
 hair_design='thin layered dark brown waves, continuous temples, full-depth gathered ponytail')
(OUT/'build-manifest.json').write_text(json.dumps(man,indent=2)+'\n')
for im in bpy.data.images:
 if im.name.startswith('Mira_Face'):im.filepath='//Mira_Face.png'
tex.filepath='//Mira_Hair.png'
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1)
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True)
for o in meshes:o.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(OUT/'Mira.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,use_custom_props=True,mesh_smooth_type='FACE',path_mode='RELATIVE')
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1)
scene.cycles.samples=a.samples
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='OPTIX'
 if any(dev.use for dev in prefs.devices):scene.cycles.device='GPU'
except Exception as e:print('CPU fallback',e,flush=True)
camera=bpy.data.objects['ReviewCamera']
def shot(name,angle=0,target=(0,0,.535),scale=1.19,size=(768,896),action='Idle',frame=1,elevated=.12):
 arm.animation_data.action=bpy.data.actions[action];scene.frame_set(frame);target=Vector(target);angle=math.radians(angle)
 camera.location=target+Vector((math.sin(angle)*3.4,-math.cos(angle)*3.4,elevated));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
 scene.render.resolution_x,scene.render.resolution_y=size;scene.render.filepath=str(PRE/(name+'.png'));bpy.ops.render.render(write_still=True)
if a.render!='none':
 shot('face',18,(0,-.018,.818),.59,(1024,1024),elevated=.03);shot('temple-left',65,(0,-.018,.818),.59,(1024,1024),elevated=.03);shot('temple-right',-65,(0,-.018,.818),.59,(1024,1024),elevated=.03);shot('back-hair',155,(.035,.11,.773),.63,(1024,1024),elevated=.10)
if a.render=='all':
 for key,angle in [('front',0),('three-quarter',27),('side',90),('back',180)]:shot(key,angle)
 for key,action,frame in [('idle','Idle',13),('walk','Walk',7),('carry','Carry',7),('cast','Cast',17)]:
  shot(key,27,action=action,frame=frame);shot(key+'-side',90,action=action,frame=frame)
 # Side-by-side original rig, at exact original scale.
 studio=bpy.data.collections['REVIEW_STUDIO_not_exported'];original=ROOT/'Art/Models/CrewRig/CrewRig.blend'
 with bpy.data.libraries.load(str(original),link=False) as (src,dest):dest.objects=['CrewRig','Body','Outfit_Captain','Hat_CaptainCap']
 ref=[o for o in dest.objects if o];ref_arm=next(o for o in ref if o.type=='ARMATURE')
 for o in ref:studio.objects.link(o);o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
 ref_arm.location.x=-.48;arm.location.x=.38;ref_arm.animation_data.action=bpy.data.actions['Idle'];shot('same-scale',0,(-.03,0,.535),1.85,(1400,1000));arm.location.x=0
 for o in ref:bpy.data.objects.remove(o,do_unlink=True)
 for action in list(bpy.data.actions):
  if action.name not in contract['actions']:bpy.data.actions.remove(action)
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1);assert signature(arm)==contract
camera.location=(1.54,-3.03,.755);camera.rotation_euler=(Vector((0,0,.535))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.19;scene.render.resolution_x,scene.render.resolution_y=768,896
assert {n:fingerprint(bpy.data.objects[n]) for n in nonhair}==nonhair
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Mira.blend'),relative_remap=False)
for n in ('Mira.blend','Mira.fbx','Mira_Face.png','Mira_Hair.png','build-manifest.json'):shutil.copy2(OUT/n,PRE/n)
shutil.copy2(Path(__file__),PRE/Path(__file__).name)
assert {n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in base_hash}==base_hash
print('MIRA FULL HAIR COMPLETE',a.revision,sum(counts.values()),counts,'five nonhair exact; r20 archive unchanged',flush=True)

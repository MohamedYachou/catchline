"""FISH043 — exact Catchline authored style, matching editable models/FBX/UI portraits.
Reuses the approved FishPolish16 construction/palette. No Gemini fish geometry or illustrations.
Run blender -b -t 4 --python Art/Source/build_fish043.py -- [optional species names].
"""
import bpy,bmesh,math,json,sys,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
# Blender's distro Python3.14 lazily evaluates operator annotations, while the
# bundled orientation_helper replaces them. Eagerly materialize property declarations
# in-memory; installed Blender/addon files remain untouched.
if 'use_selection' not in bpy.ops.export_scene.fbx.get_rna_type().properties.keys():
 import ast,io_scene_fbx
 addon=Path(io_scene_fbx.__file__)
 try:io_scene_fbx.unregister()
 except Exception:pass
 tree=ast.parse(addon.read_text())
 for node in ast.walk(tree):
  if isinstance(node,ast.ClassDef):
   converted=[];found=False
   for item in node.body:
    if isinstance(item,ast.AnnAssign) and item.value is None and isinstance(item.target,ast.Name):
     converted.append(ast.Assign(targets=[ast.Subscript(value=ast.Name(id='__annotations__',ctx=ast.Load()),slice=ast.Constant(value=item.target.id),ctx=ast.Store())],value=item.annotation));found=True
    else:converted.append(item)
   if found:node.body=[ast.Assign(targets=[ast.Name(id='__annotations__',ctx=ast.Store())],value=ast.Dict(keys=[],values=[]))]+converted
 ast.fix_missing_locations(tree);exec(compile(tree,str(addon),'exec'),io_scene_fbx.__dict__);io_scene_fbx.register()
 assert 'use_selection' in bpy.ops.export_scene.fbx.get_rna_type().properties.keys(),'FBX compatibility registration'

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/Fish043';OUT.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('fishbase',ROOT/'Art/Source/build_fish_polish16.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
base.OUT=OUT;base.COLORS.update({'M_OilskinYellow':'E6AD38','M_SpotBlue':'38B6FF','M_Crimson':'A9433C'})
original_ball=base.ball;original_fin=base.fin
# Keep the approved models. Remove the ivory ring so every eye reads as a normal black bead.
def bead_ball(name,pos,size,color):
 if name=='EyeRim':return None
 return original_ball(name,pos,size,color)
base.ball=bead_ball

def refined_fin(name,poly,color,thick):
 if name=='SpinyDorsal':
  #20alternating edge vertices =10actual dorsal spines, same span/profile as the approved bass.
  L=thick/.007;H=.18
  poly=[(-.28*L,H*.75*L)]+[((-.26+i*.0225)*L,H*(1.52 if i%2==0 else 1.05)*L) for i in range(20)]+[(.19*L,H*.6*L)]
 return original_fin(name,poly,color,thick)
base.fin=refined_fin
ROWS=[
 ('GoldenPuffer',.32,'puffer','M_Rope','M_BandIvory'),
 ('SpottedEagleRay',.80,'eagle','M_HullNavy','M_HullBlue'),
 ('ApexReefShark',1.0,'reef','M_Rope','M_OilskinYellow'),
 ('GoldTipShark',1.1,'goldtip','M_Rope','M_OilskinYellow'),
 ('AbyssalGreatWhite',1.25,'white','M_CoastWet','M_Rubber'),
 ('AbyssalLeviathan',1.45,'orca','M_Rubber','M_RailIvory'),
 ('BlueSpottedStingray',.65,'stingray','M_Rope','M_WoodRecess'),
 ('FlyingFish',.4,'flying','M_HullBlue','M_SeaTeal'),
 ('Lionfish',.42,'lion','M_SafetyOrange','M_RailIvory'),
 ('GiantDevilManta',1.3,'manta','M_Rubber','M_HullNavy'),
 ('AtlanticSwordfish',1.15,'sword','M_HullBlue','M_FishSilver'),
 ('OceanSunfish',.85,'sunfish','M_Steel','M_FishSilver'),
 ('ScallopedHammerhead',1.15,'hammer','M_CoastWet','M_Steel'),
 ('PelagicThresherShark',1.1,'thresher','M_HullBlue','M_FishSilver'),
 ('GiantSquid',1.2,'squid','M_SafetyOrange','M_Crimson')]
FEATURES=[]
def mesh(name,verts,faces,color):
 ob=base.mesh(name,verts,faces,[color]*len(faces));FEATURES.append(name);return ob

def ball(name,pos,size,color):
 ob=base.ball(name,pos,size,color);FEATURES.append(name);return ob

def line(name,pts,r,color):
 ob=base.line(name,pts,r,color);FEATURES.append(name);return ob

def fin(name,poly,color,L,thick=.008):
 ob=base.fin(name,[(y*L,z*L) for y,z in poly],color,L*thick);FEATURES.append(name);return ob

def plate(name,poly,color,L,thick=.008):
 verts=[(x*L,y*L,z*L+side*thick*L) for side in [-1,1] for x,y,z in poly];n=len(poly)
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,verts,faces,color)

def cone(name,start,end,r,color):
 direction=Vector(end)-Vector(start);bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=r,radius2=0,depth=direction.length,location=(Vector(start)+Vector(end))/2)
 ob=bpy.context.object;ob.name=name;ob.rotation_euler=direction.to_track_quat('Z','Y').to_euler();ob.parent=base.GROUP;ob.data.materials.append(base.mat(color));FEATURES.append(name);return ob

def body(L,W,H,back,kind):
 profile=[(-.48,.2),(-.43,.62),(-.33,.88),(-.18,1),(0,1),(.18,.78),(.33,.38),(.43,.08)]
 if kind=='orca':profile=[(-.5,.3),(-.47,.76),(-.34,.99),(-.18,1),(0,.96),(.2,.7),(.4,.20),(.5,.05)]
 if kind=='puffer':profile=[(-.43,.18),(-.36,.68),(-.24,.93),(-.08,1),(.08,.98),(.25,.79),(.35,.4)]
 if kind=='sunfish':profile=[(-.4,.3),(-.36,.62),(-.22,.9),(0,1),(.2,.87),(.35,.56),(.39,.4)]
 if kind=='squid':profile=[(-.37,.20),(-.29,.65),(-.12,1),(.12,.85),(.32,.45),(.5,.03)]
 n=24;verts=[]
 for y,f in profile:
  for i in range(n):
   a=i*math.tau/n;verts.append((L*W*f*math.cos(a),L*y,L*H*f*math.sin(a)))
 faces=[tuple(reversed(range(n)))];colors=[back]
 for j in range(len(profile)-1):
  for i in range(n):
   faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i));a=(i+.5)*math.tau/n
   color=back if math.sin(a)>.1 else 'M_FishSilver' if math.sin(a)>-.5 else 'M_RailIvory'
   if kind=='puffer':color='M_Rope' if math.sin(a)>.35 else 'M_BandIvory'
   if kind=='lion':color='M_SafetyOrange' if j%2 else 'M_RailIvory'
   if kind=='squid':color='M_SafetyOrange' if math.sin(a)>.1 else 'M_Crimson'
   if kind=='orca':color='M_Rubber' if math.sin(a)>-.25 else 'M_RailIvory'
   colors.append(color)
 faces.append(tuple(range((len(profile)-1)*n,len(profile)*n)));colors.append(back)
 ob=base.mesh('Body',verts,faces,colors)
 for p in ob.data.polygons:p.use_smooth=True
 return ob

def eyes(L,W,kind):
 if kind in ['eagle','stingray','manta']:
  for side in [-1,1]:
   eye_pos=(side*(.115 if kind=='manta' else .075)*L,-.30*L,(.012 if kind=='manta' else .055)*L)
   ball('Eye',eye_pos,(.024*L,.026*L,.021*L),'M_Rubber')
   ball('EyeGlint',(eye_pos[0],eye_pos[1]-.009*L,eye_pos[2]+.017*L),(.004*L,)*3,'M_RailIvory')
 elif kind=='hammer':
  for side in [-1,1]:
   ball('Eye',(side*.337*L,-.40*L,.02*L),(.018*L,.027*L,.021*L),'M_Rubber')
   ball('EyeGlint',(side*.346*L,-.408*L,.025*L),(.003*L,)*3,'M_RailIvory')
 else:
  for side in [-1,1]:
   y=(-.30 if kind=='squid' else -.34)*L;z=(.02 if kind=='squid' else .045)*L
   x=W*({'puffer':.70,'squid':.64,'sunfish':.62,'orca':.98}.get(kind,.85))*L;size=.036 if kind=='squid' else .022
   ball('Eye',(side*x,y,z),(L*.012,L*size,L*size),'M_Rubber')
   ball('EyeGlint',(side*(x+.010*L),y-.004*L,z+.006*L),(L*.003,)*3,'M_RailIvory')

def shark_fins(L,fc,kind):
 fin('Dorsal',[(-.25,.10),(-.19,.35),(-.05,.54),(.02,.45),(-.05,.34),(.15,.12)] if kind=='sword' else [(-.15,.12),(-.04,.45 if kind=='hammer' else .34),(.02,.24),(.12,.13)],fc,L)
 for side in [-1,1]:
  plate('Pectoral',[(side*.10,-.18,-.04),(side*.39,.13,-.10),(side*.12,.10,-.06)],fc,L)
 fin('Anal',[(.14,-.07),(.27,-.18),(.31,-.05)],fc,L)
 poly=[(.39,.02),(.64,.32),(.55,.04),(.59,-.2),(.41,-.025)]
 if kind=='thresher':poly=[(.39,.025),(.60,.38),(.89,.85),(.91,1.02),(.80,.83),(.54,.16),(.57,-.18),(.40,-.025)]
 tail=fin('Tail',poly,fc,L)
 pivot=Vector((0,.40*L,0))
 for v in tail.data.vertices:v.co-=pivot
 tail.location=pivot
 for side in [-1,1]:
  for i in range(5):
   y=(-.22+i*.027)*L;line('GillSlit',[(side*.125*L,y,-.065*L),(side*.15*L,y,.03*L),(side*.13*L,y,.08*L)],.0024*L,'M_Rubber')
  line('Mouth',[(side*.025*L,-.475*L,-.015*L),(side*.09*L,-.42*L,-.04*L)],.002*L,'M_Rubber')
 if kind=='white':
  for side in [-1,1]:
   for i in range(5):cone('SerratedTooth',(side*(.035+i*.009)*L,(-.46+i*.007)*L,-.025*L),(side*(.035+i*.009)*L,(-.46+i*.007)*L,-.052*L),.006*L,'M_RailIvory')
   line('OldScar',[(side*.132*L,-.1*L,.07*L),(side*.152*L,-.07*L,.01*L),(side*.146*L,-.035*L,-.04*L)],.004*L,'M_RailIvory')

# Independent saved-source/FBX checks, with the same exact image used by native UI.
def deliver(name,L,kind):
 sc=bpy.context.scene;folder=OUT/name;folder.mkdir(parents=True,exist_ok=True)
 group=base.GROUP;all_meshes=[o for o in group.children_recursive if o.type=='MESH'];features=list(FEATURES)
 static=[o for o in all_meshes if o.name!='Tail' and not o.name.startswith(('Arm_','FeedingClub_'))]
 bpy.ops.object.select_all(action='DESELECT')
 for o in static:o.select_set(True)
 bpy.context.view_layer.objects.active=static[0];bpy.ops.object.join();bpy.context.object.name='Body'
 for o in group.children_recursive:
  if o.type=='MESH':
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 # Explicit heading markers let wide rays/mantas/sunfish avoid longest-axis misorientation in Unity.
 for n,y in [('Nose',-.5*L),('TailEnd',.4*L)]:
  ob=bpy.data.objects.new(n,None);sc.collection.objects.link(ob);ob.parent=group;ob.location=(0,y,0)
 meshes=[o for o in group.children_recursive if o.type=='MESH'];coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 bpy.context.view_layer.update();coords=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 bounds=[Vector(tuple(min(v[i] for v in coords) for i in range(3))),Vector(tuple(max(v[i] for v in coords) for i in range(3)))];center=(bounds[0]+bounds[1])/2
 sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.resolution_x=768;sc.render.resolution_y=384;sc.render.resolution_percentage=100
 sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.view_settings.view_transform='Standard'
 try:sc.view_settings.look='Medium High Contrast'
 except:pass
 world=bpy.data.worlds.new('Soft coastal fill');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.74,.80,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;sc.world=world
 for n,pos,power,size in [('Warm key',(L,-L,2*L),80*L*L,1.4*L),('Cool fill',(-L,-.3*L,L),35*L*L,1.2*L)]:
  d=bpy.data.lights.new(n,'AREA');d.energy=power;d.size=size;d.color=(1,.86,.68) if n=='Warm key' else (.70,.85,1)
  o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=Vector(pos)+center;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
 d=bpy.data.cameras.new('Portrait');cam=bpy.data.objects.new('Portrait',d);sc.collection.objects.link(cam)
 direction=Vector((1.8,-.25,.8)) if kind not in ['eagle','stingray','manta'] else Vector((1.35,-.85,1.8))
 if kind=='hammer':direction=Vector((1.2,-1.35,1.0))
 cam.location=center+direction*L;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO'
 if kind=='thresher':cam.rotation_euler.rotate_axis('Z',.65)
 right=cam.rotation_euler.to_quaternion()@Vector((1,0,0));up=cam.rotation_euler.to_quaternion()@Vector((0,1,0))
 w=max((p-center).dot(right) for p in coords)-min((p-center).dot(right) for p in coords);h=max((p-center).dot(up) for p in coords)-min((p-center).dot(up) for p in coords)
 xs=[(p-center).dot(right) for p in coords];ys=[(p-center).dot(up) for p in coords]
 projected_center=center+right*((min(xs)+max(xs))/2)+up*((min(ys)+max(ys))/2)
 cam.location=projected_center+direction.normalized()*direction.length*L
 d.ortho_scale=max(w,h*2)*1.25;sc.camera=cam
 group['brief_kind']=kind;group['features']=json.dumps(features);group['nose']='source -Y; Unity +Z';group['units']='metres'
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(name+'.blend')))
 bpy.ops.object.select_all(action='DESELECT')
 for o in [group]+list(group.children_recursive):o.select_set(True)
 bpy.context.view_layer.objects.active=group
 bpy.ops.export_scene.fbx(filepath=str(folder/(name+'.fbx')),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',bake_space_transform=True,add_leaf_bones=False,bake_anim=False)
 portrait=folder/('fish-'+name.lower()+'.png');sc.render.filepath=str(portrait);bpy.ops.render.render(write_still=True)
 original=sorted(tuple(o.matrix_world@v.co) for o in meshes for v in o.data.vertices);tri=sum(len(o.data.polygons) for o in meshes);materials=sorted({m.name for o in meshes for m in o.data.materials})
 assert tri<15000 and all(math.isfinite(x) for v in original for x in v)
 bpy.ops.wm.open_mainfile(filepath=str(folder/(name+'.blend')))
 saved=[o for o in bpy.data.objects if o.type=='MESH'];assert sum(len(o.data.polygons) for o in saved)==tri
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(folder/(name+'.fbx')))
 imported=[o for o in bpy.data.objects if o.type=='MESH'];assert sum(len(o.data.polygons) for o in imported)==tri
 rt=[tuple(o.matrix_world@v.co) for o in imported for v in o.data.vertices];assert len(rt)==len(original)
 kd=KDTree(len(original))
 for i,v in enumerate(original):kd.insert(v,i)
 kd.balance();err=max(kd.find(v)[2] for v in rt);assert err<.0001,(name,err)
 assert sorted({m.name for o in imported for m in o.data.materials})==materials
 assert not list(bpy.data.images)
 report={'name':name,'kind':kind,'features':features,'triangles':tri,'meshes':len(imported),'materials':materials,'bounds':[[float(x) for x in b] for b in bounds],'saved_source_checked':True,'fbx_checked':True,'roundtrip_error_m':err,'portrait_from_exact_saved_model':True,'portrait':[768,384],'file_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [folder/(name+'.blend'),folder/(name+'.fbx'),portrait]}}
 (folder/'validation.json').write_text(json.dumps(report,indent=2));print('FISH043 VERIFIED',name,tri,flush=True)

def build_special(row):
 global FEATURES
 name,L,kind,back,fc=row;FEATURES=[];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;base.MATS={}
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
 base.GROUP=bpy.data.objects.new('Catchline_'+name,None);sc.collection.objects.link(base.GROUP)
 ray=kind in ['eagle','stingray','manta'];W=.15;H=.14
 if kind=='puffer':W=.34;H=.35
 if kind=='orca':W=.22;H=.21
 if kind=='sunfish':W=.08;H=.36
 if kind=='squid':W=.105;H=.12
 if ray:W=.13;H=.055
 body(L,W,H,back,kind);eyes(L,W,kind)
 if ray:
  for side in [-1,1]:
   width=.85 if kind=='manta' else .59
   poly=[(side*.06,-.38,0),(side*width,-.04,-.015),(side*(width*.68),.14,-.02),(side*.10,.38,-.012)]
   if kind=='stingray':poly=[(side*.035,-.40,0)]+[(side*.54*math.cos(-math.pi/2+i*math.pi/12),.02+.42*math.sin(-math.pi/2+i*math.pi/12),-.008) for i in range(1,12)]+[(side*.035,.44,0)]
   plate('Wing',poly,fc,L,.012)
   if kind=='manta':
    ball('WhiteShoulder',(side*.18*L,-.15*L,.045*L),(.13*L,.10*L,.012*L),'M_RailIvory')
    line('CephalicHorn',[(side*.10*L,-.30*L,.02*L),(side*.15*L,-.48*L,.04*L),(side*.12*L,-.55*L,.09*L)],.018*L,back)
   else:
    for j in range(12):
     x=side*(.12+(j%3)*.10);y=-.20+(j//3)*.12
     if kind=='eagle':
      ring=[((x+.020*math.cos(i*math.tau/12))*L,(y+.020*math.sin(i*math.tau/12))*L,.023*L) for i in range(13)]
      line('IvoryOcellus',ring,.0035*L,'M_RailIvory')
     else:ball('BlueSpotDome',(x*L,y*L,.022*L),(.024*L,.022*L,.012*L),'M_SpotBlue')
  line('Tail',[(0,.30*L,0),(.04*L,.65*L,-.02*L),(.10*L,1.06*L,-.04*L)],.008*L,back)
  if kind=='eagle':ball('DistinctSnout',(0,-.42*L,0),(.06*L,.12*L,.033*L),back)
 elif kind=='puffer':
  for i in range(30):
   y=1-2*(i+.5)/30;r=math.sqrt(1-y*y);a=i*2.399963;v=Vector((r*math.cos(a),y,r*math.sin(a)))
   start=Vector((v.x*W,v.y*.38,v.z*H))*L;end=start+v*.055*L;cone('ConicalSpine',start,end,.014*L,'M_BandIvory')
  for side in [-1,1]:
   for j in range(9):ball('DarkWoodSpot',(side*W*.93*L,(-.22+j%3*.16)*L,(-.08+j//3*.12)*L),(.010*L,.023*L,.022*L),'M_WoodRecess')
  fin('Tail',[(.32,.025),(.49,.16),(.53,.10),(.53,-.10),(.49,-.16),(.32,-.025)],fc,L)
 elif kind=='sunfish':
  fin('TowerDorsal',[(-.08,.32),(.15,.89),(.28,.72),(.25,.25)],fc,L)
  fin('TowerAnal',[(-.08,-.32),(.15,-.89),(.28,-.72),(.25,-.25)],fc,L)
  fin('Tail',[(.32,.25),(.45,.22),(.42,.13),(.46,.07),(.43,0),(.46,-.07),(.42,-.13),(.45,-.22),(.32,-.25)],fc,L)
  for side in [-1,1]:plate('Pectoral',[(side*.06,-.20,0),(side*.22,-.05,-.05),(side*.07,.04,-.04)],back,L)
 elif kind=='squid':
  for side in [-1,1]:plate('ArrowFin',[(0,.48,0),(side*.26,.20,0),(side*.11,.02,-.01),(0,.12,0)],fc,L)
  for i in range(10):
   a=i*math.tau/10;long=i>=8;length=1.45 if long else .75+.12*math.sin(i)
   pts=[]
   for j in range(15):
    t=j/14;spread=.08+.17*math.sin(t*math.pi*.8);pts.append((math.cos(a)*spread*L,(-.3-length*t)*L,(math.sin(a)*spread+.06*math.sin(t*math.tau+i))*L))
   line(('FeedingClub_' if long else 'Arm_')+str(i-7 if long else i+1).zfill(2),pts,(.009 if long else .018)*L,fc if long else back)
   if long:ball('FeedingClubTip',pts[-1],(.035*L,.12*L,.035*L),back)
 elif kind=='orca':
  fin('TallDorsal',[(-.1,.17),(.02,.62),(.19,.18)],back,L)
  for side in [-1,1]:
   plate('PaddlePectoral',[(side*.16,-.24,-.08),(side*.40,-.02,-.16),(side*.37,.10,-.15),(side*.16,.04,-.10)],back,L)
   # Patch is behind the actual eye, never used as a substitute eye.
   ball('WhiteEyePatch',(side*.213*L,-.18*L,.075*L),(.015*L,.10*L,.045*L),'M_RailIvory')
  plate('Tail',[(-.31,.68,0),(-.07,.45,0),(0,.40,0),(.07,.45,0),(.31,.68,0),(.08,.61,0),(0,.59,0),(-.08,.61,0)],back,L)
 elif kind in ['reef','goldtip','white','hammer','thresher','sword']:
  shark_fins(L,fc,kind)
  if kind=='hammer':
   # Real T-shaped head with a shallow scalloped leading edge.
   plate('Cephalofoil',[(-.36,-.43,.01),(-.28,-.48,.01),(-.16,-.45,.01),(0,-.48,.01),(.16,-.45,.01),(.28,-.48,.01),(.36,-.43,.01),(.32,-.32,.01),(.10,-.33,.01),(-.10,-.33,.01),(-.32,-.32,.01)],back,L,.04)
  if kind=='sword':plate('FlattenedBill',[(-.025,-.43,0),(0,-1.05,0),(.025,-.43,0)],'M_Steel',L,.006)
  if kind=='goldtip':fin('GoldFinTip',[(-.04,.34),(-.01,.27),(.02,.26)],'M_OilskinYellow',L,.009)
 elif kind=='flying':
  for side in [-1,1]:plate('SweptPectoralWing',[(side*.08,-.25,0),(side*.58,.08,.025),(side*.49,.33,.005),(side*.12,.08,-.02)],fc,L,.007)
  fin('Dorsal',[(-.1,.12),(.01,.24),(.15,.1)],back,L);fin('Tail',[(.39,.02),(.56,.14),(.50,0),(.58,-.22),(.39,-.02)],'M_FishSilver',L)
 elif kind=='lion':
  for i in range(11):
   y=-.25+i*.05;cone('FannedDorsalSpine',(0,y*L,.10*L),(0,(y+.045)*L,(.28+.13*math.sin(i*math.pi/10))*L),.011*L,fc)
  for side in [-1,1]:
   for i in range(9):
    a=-.7+i*.21;start=(side*.10*L,-.18*L,0);end=(side*(.30+.08*math.sin(i)) *L,(-.05+.28*math.sin(a))*L,-.18*math.cos(a)*L)
    cone('SplayedPectoralPlume',start,end,.018*L,fc if i%2 else back)
  fin('Tail',[(.39,.03),(.53,.15),(.57,.09),(.57,-.09),(.53,-.15),(.39,-.03)],fc,L)
 deliver(name,L,kind)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for row in base.FISH:
  if not args or row[0] in args:base.build(row)
 for row in ROWS:
  if not args or row[0] in args:build_special(row)

"""Mira-only head overlay in existing toggle; shared body/wardrobe/actions untouched."""
import bpy,sys,math,json,hashlib,importlib.util,shutil
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[3];B=O/'_mira-match-backup';
if not (O/'mira-match-baseline-measurements.json.gz').exists():
 B.mkdir(exist_ok=True)
 for ext in ['blend','fbx']:
  p=O/('CrewRig_Restaurant.'+ext)
  if not (B/p.name).exists():shutil.copy2(p,B/p.name)
source=B/'CrewRig_Restaurant.blend' if (B/'CrewRig_Restaurant.blend').exists() else O/'CrewRig_Restaurant.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;rig=bpy.data.objects['CrewRig'];rig.animation_data_clear();rig.data.pose_position='REST'
sp=importlib.util.spec_from_file_location('town',str(R/'Art/Source/Townsfolk/build.py'));T=importlib.util.module_from_spec(sp);sp.loader.exec_module(T)
P={'MiraMatch_Skin':'#D9A376','MiraMatch_Hair':'#543021','MiraMatch_HairLight':'#79452A','MiraMatch_HairShadow':'#3F281F','MiraMatch_Gold':'#E8B64F','MiraMatch_Teal':'#168F91','MiraMatch_White':'#FFF4DF','MiraMatch_Iris':'#79401D','MiraMatch_Pupil':'#251E1A','MiraMatch_Lip':'#A74336','MiraMatch_Mouth':'#672D28','MiraMatch_Blush':'#CF835F'}
T.H.PALETTE.update(P)
for n,c in T.H.PALETTE.items():T.H.MATERIALS[n]=T.H.material(n,c)
s=T.Skin(rig)
# Round the strand cross-sections and interpolate sparse control points for soft waves.
def smooth_tube(path,radii,col,bone=None,sides=10,weights=None):
 from mathutils import Vector
 pts=[Vector(p) for p in path];dense=[];rs=[]
 for i in range(len(pts)-1):
  a,b,c,d=pts[max(0,i-1)],pts[i],pts[i+1],pts[min(len(pts)-1,i+2)]
  for j in range(5):
   t=j/5;v=.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t);dense.append(tuple(v));rs.append(radii[i]+(radii[i+1]-radii[i])*t)
 dense.append(tuple(pts[-1]));rs.append(radii[-1]);s.part('tube',dense,rs,sides,col,bone=bone,smooth=True,weights=weights)
s.tube=smooth_tube
# A closed facial shell covers the generic shared face; no edits to other crew's Body.
s.ell((0,-.008,.759),(.195,.184,.202),'MiraMatch_Skin','Head',seg=32,rings=16)
for sign in [-1,1]:
 s.ell((sign*.188,-.007,.748),(.030,.027,.043),'MiraMatch_Skin','Head',seg=12,rings=6)
 s.ell((sign*.202,-.028,.750),(.012,.007,.021),'MiraMatch_Blush','Head',seg=10,rings=4)
 # Warm brown eyes with soft ivory sclera, restrained highlights and curved brows.
 x=sign*.067
 s.ell((x,-.183,.786),(.028,.014,.035),'MiraMatch_White','Head',seg=16,rings=7)
 s.ell((x-sign*.003,-.196,.785),(.017,.006,.025),'MiraMatch_Iris','Head',seg=16,rings=6)
 s.ell((x-sign*.003,-.201,.786),(.009,.004,.018),'MiraMatch_Pupil','Head',seg=12,rings=5)
 s.ell((x-.006,-.205,.799),(.005,.002,.007),'MiraMatch_White','Head',seg=8,rings=4)
 s.tube([(x-sign*.025,-.174,.832),(x,-.183,.840),(x+sign*.025,-.166,.834)],[.005,.007,.004],'MiraMatch_Hair','Head',sides=8)
 # Upper lash only: small enough to stay readable at game scale.
 s.tube([(x-.025,-.19,.798),(x-.010,-.199,.817),(x+.010,-.199,.817),(x+.025,-.19,.800)],[.0025]*4,'MiraMatch_HairShadow','Head',sides=6)

s.ell((0,-.194,.750),(.025,.034,.027),'MiraMatch_Skin','Head',seg=16,rings=8)
# Open asymmetric smile with ivory teeth and a small warm lower lip.
s.ell((.002,-.184,.703),(.047,.014,.025),'MiraMatch_Lip','Head',seg=20,rings=8)
s.ell((.002,-.195,.706),(.039,.006,.018),'MiraMatch_Mouth','Head',seg=16,rings=6)
s.ell((0,-.201,.715),(.030,.003,.006),'MiraMatch_White','Head',seg=14,rings=4)
s.ell((.009,-.202,.694),(.020,.003,.005),'MiraMatch_Lip','Head',seg=12,rings=4)
# Long closed hair shell, swept forehead and tapered corkscrew locks at the shoulders.
# Dense scalp avoids chord intersections with the closed face overlay at temples.
n=48;rings=16;vs=[(0,0,.985)];fs=[]
for j in range(1,rings+1):
 for i in range(n):
  a=i*math.tau/n;edge=.603+(.873-.603)*max(0,-math.sin(a))**3;ang=math.acos((edge-.76)/.225)*j/rings
  vs.append((.215*math.sin(ang)*math.cos(a),.205*math.sin(ang)*math.sin(a),.76+.225*math.cos(ang)))
fs.extend((0,1+i,1+(i+1)%n) for i in range(n))
for j in range(rings-1):fs.extend((1+j*n+i,1+j*n+(i+1)%n,1+(j+1)*n+(i+1)%n,1+(j+1)*n+i) for i in range(n))
s.part('add',vs,fs,'MiraMatch_Hair',bone='Head')
# Back waves: rounded wavy strands, never a bun or flat sheets.
for k in range(7):
 a=.12+(math.pi-.24)*k/6
 path=[(.211*math.cos(a)+.012*math.sin(j*1.7+k),.175*math.sin(a)+.024,.90-j*.048) for j in range(7)]
 s.ell(path[0],(.040,.040,.040),'MiraMatch_Hair','Head',seg=12,rings=6)
 s.tube(path,[.040,.042,.042,.040,.035,.026,.010],'MiraMatch_Hair','Head',sides=10)
for sign in [-1,1]:
 for k in range(3):
  path=[]
  for j in range(15):
   t=j/14;a=t*math.tau*1.45+k*.75
   path.append((sign*(.190+k*.013+.017*math.sin(a)),-.044+k*.060+.022*math.cos(a),.881-t*(.291-k*.020)))
  radii=[.031*(1-.60*(j/14)**3) for j in range(15)];radii[-1]=.006
  s.tube(path,radii,'MiraMatch_Hair' if k!=1 else 'MiraMatch_HairLight','Head',sides=10)
 # Teal-and-gold drops stay outside the curls and match the bust.
 s.ell((sign*.207,-.067,.717),(.012,.009,.020),'MiraMatch_Gold','Head',seg=12,rings=5)
 s.ell((sign*.210,-.073,.693),(.018,.008,.026),'MiraMatch_Gold','Head',seg=12,rings=6)
 s.ell((sign*.210,-.081,.693),(.010,.004,.017),'MiraMatch_Teal','Head',seg=10,rings=5)
# Broad swept S-locks give a side-part and a few loose forehead curls.
for k in range(4):
 y=-.095-k*.020;z=.960-k*.015
 s.tube([(-.174,y+.035,z-.014),(-.105,y-.026,z+.036),(-.015,y-.026,z+.045),(.070,y-.005,z+.025),(.123,y+.015,z-.005)],[.026,.037,.040,.030,.008],'MiraMatch_Hair','Head',sides=12)
 s.tube([(-.155,y+.015,z+.006),(-.093,y-.048,z+.050),(-.015,y-.051,z+.056),(.054,y-.025,z+.035)],[.003,.004,.004,.002],'MiraMatch_HairLight','Head',sides=6)
s.tube([(.071,-.164,.940),(.110,-.184,.915),(.112,-.194,.877),(.085,-.194,.859),(.068,-.192,.868)],[.019,.025,.021,.013,.004],'MiraMatch_Hair','Head',sides=10)
# Gold botanical clip on viewer-left temple, clearly legible from service camera.
s.tube([(-.177,-.213,.892),(-.153,-.220,.925),(-.131,-.207,.953)],[.004]*3,'MiraMatch_Gold','Head',sides=8)
for x,y,z,rot in [(-.175,-.223,.911,-.6),(-.147,-.228,.935,.45),(-.142,-.219,.953,.1)]:
 s.ell((x,y,z),(.009,.006,.022),'MiraMatch_Gold','Head',seg=10,rings=5)
s.ell((-.166,-.232,.904),(.010,.006,.010),'MiraMatch_Gold','Head',seg=10,rings=4)
old=bpy.data.objects['Hat_HairUpClip'];bpy.data.objects.remove(old,do_unlink=True);head=s.finish('Hat_HairUpClip')
for poly in head.data.polygons:poly.use_smooth=True
uv=head.data.uv_layers.new(name='UVMap')
for p in head.data.polygons:
 for li in p.loop_indices:
  co=head.data.vertices[head.data.loops[li].vertex_index].co;uv.data[li].uv=(co.x+.5,co.z)
head['identity']='Mira only; reference call+coach curly shoulder-length chestnut hair, gold clip, warm brown eyes';head['toggle_contract']='Existing Hat_HairUpClip name; neutral Body and all outfits unchanged'
rig.data.pose_position='POSE';T.bind(rig,'Idle');sc.frame_set(13)
for o in sc.objects:
 if o.type=='MESH':o.hide_render=o.name not in ['Body','Outfit_HostFormal','Hat_HairUpClip']
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CrewRig_Restaurant.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
 if o.type in ['ARMATURE','MESH']:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
print('MIRA MATCH BUILD PASS',flush=True)

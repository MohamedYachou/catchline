"""Six additional civilians, independently named real-colour materials, unchanged rig."""
import bpy,sys,math,json,hashlib,importlib.util,ast
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
sp=importlib.util.spec_from_file_location('town',str(R/'Art/Source/Townsfolk/build.py'));T=importlib.util.module_from_spec(sp);sp.loader.exec_module(T)
# Reuse accepted seated motion function only; do not execute the earlier build queue.
src=(O/'build-v2.py').read_text();tree=ast.parse(src);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='pose_action');exec(compile(ast.Module(body=[fn],type_ignores=[]),str(O/'build-v2.py'),'exec'))
from mathutils import Vector
GUESTS=[('Guest_Gus','older man','CDA27E','BBC0B8','87694B','3E4C4C','silver'),('Guest_Hazel','older woman','A56E52','D0CCC0','914E62','454554','bun'),('Guest_Ivo','teenager','CC956A','382D2A','B06B3E','354E69','teen'),('Guest_Jonas','fisherman in cap','A16C4B','665847','556A43','3D4D56','cap'),('Guest_Kai','smart dinner man','825239','272A30','493E59','2D3345','suit'),('Guest_Lena','smart dinner woman','E1B08A','8A4B32','8E3B49','3C3B52','dress')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for name,role,skin,hair,shirt,pants,style in GUESTS:
 rig=T.init();rig.data.pose_position='REST';bpy.context.scene.frame_set(1)
 for key,h in [('M_Skin',skin),('M_HairChestnut',hair),('M_HairSilver',hair),('M_SeaTeal',shirt),('M_HullNavy',pants)]:T.H.MATERIALS[key]=T.H.material(name+'_'+key[2:],'#'+h)
 # All OTHER used palette materials also carry guest-specific names; no crew-remap keys survive.
 for key,m in T.H.MATERIALS.items():m.name=name+'_'+key.replace('M_','')
 s=T.Skin(rig);T.torso(s,'M_SeaTeal');T.limbs(s,'M_SeaTeal',pants='M_HullNavy',rolled=style in ['teen','cap'],boots=False);T.face(s,old=style in ['silver','bun']);T.hair(s,long=style in ['bun','dress'])
 if style=='silver':
  s.ell((0,-.12,.717),(.077,.022,.018),'M_HairSilver','Head',seg=10,rings=3)
  # Small oval reading spectacles and bridge, no giant cartoon frames.
  for sign in [-1,1]:
   p=[(sign*.063+.035*math.cos(i*math.tau/14),-.154,.774+.027*math.sin(i*math.tau/14)) for i in range(15)]
   s.tube(p,[.0035]*15,'M_Rubber','Head',sides=5)
  s.tube([(-.028,-.155,.779),(.028,-.155,.779)],[.003]*2,'M_Rubber','Head',sides=5)
 if style=='bun':
  s.ell((0,.153,.87),(.086,.071,.082),'M_HairSilver','Head',seg=12,rings=4)
  # Warm berry cardigan with ivory collar, restrained pearl necklace.
  for z in [.34,.39,.44,.49]:s.ell((0,-.105,z),(.008,.006,.008),'M_BandIvory','Spine',seg=8,rings=3)
  s.tube([(-.082,-.080,.522),(0,-.115,.483),(.082,-.080,.522)],[.011]*3,'M_RailIvory','Spine',sides=6)
  for i in range(7):
   a=math.pi*(i+1)/8;s.ell((.065*math.cos(a),-.12,.494-.025*math.sin(a)),(.005,.005,.005),'M_BandIvory','Spine',seg=6,rings=2)
 if style=='teen':
  # Ochre sweatshirt, ivory drawcords, mint sneakers; no staff uniform or tie.
  s.lathe([(.28,.141,.103,0),(.31,.140,.102,0)],'M_SeaTeal','Hips',segments=16)
  s.ell((0,.081,.519),(.085,.047,.040),'M_SeaTeal','Spine1',seg=12,rings=4)
  for sign in [-1,1]:
   s.tube([(sign*.027,-.084,.543),(sign*.025,-.109,.476)],[.004,.004],'M_RailIvory','Spine',sides=5)
   s.ell((sign*.085,-.044,.058),(.067,.105,.025),'M_RailIvory',('Left' if sign==1 else 'Right')+'Foot',seg=10,rings=3)
  s.box((0,-.105,.365),(.125,.015,.044),'M_SeaTeal','Spine')
 if style=='cap':
  T.cap(s,'M_SeaTeal','cap')
  for z in [.36,.405,.45]:s.tube([(-.12,-.066,z),(0,-.102,z),(.12,-.066,z)],[.006]*3,'M_RailIvory','Spine',sides=5)
  for sign in [-1,1]:s.ell((sign*.035,-.154,.722),(.036,.010,.012),'M_HairChestnut','Head',seg=8,rings=3)
 if style in ['silver','suit']:
  # Collar and lapels are raised geometry over the civilian torso.
  s.ell((0,-.086,.469),(.046,.023,.066),'M_RailIvory','Spine',seg=10,rings=3)
  for sign in [-1,1]:
   s.part('add',[(sign*.114,-.063,.515),(sign*.015,-.119,.406),(sign*.077,-.096,.467)],[(0,1,2)],'M_HullNavy',bone='Spine')
  if style=='suit':
   s.ell((0,-.120,.490),(.028,.010,.013),'M_SafetyOrange','Spine',seg=8,rings=3)
   s.box((-.071,-.095,.462),(.033,.009,.013),'M_RailIvory','Spine')
 if style=='dress':
  # Short seated-safe burgundy evening tunic; hip bound, feet and knees remain unobstructed.
  s.lathe([(.247,.166,.128,0),(.31,.153,.107,0),(.37,.142,.105,0)],'M_SeaTeal','Hips',segments=16)
  s.lathe([(.35,.145,.108,0),(.365,.145,.108,0)],'M_OilskinYellow','Hips',segments=16)
  s.ell((0,.146,.881),(.080,.068,.072),'M_HairChestnut','Head',seg=12,rings=4)
  for sign in [-1,1]:s.ell((sign*.178,-.013,.729),(.009,.009,.017),'M_OilskinYellow','Head',seg=8,rings=3)
  s.tube([(-.08,-.084,.52),(0,-.116,.476),(.08,-.084,.52)],[.004]*3,'M_OilskinYellow','Spine',sides=5)
 ob=s.finish(name);assert all(not m.name.startswith('M_') for m in ob.data.materials)
 uv=ob.data.uv_layers.new(name='UVMap')
 for p in ob.data.polygons:
  for li in p.loop_indices:
   co=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=((co.x+.5),co.z)
 for clip in ['Sit','Eat']:pose_action(rig,clip)
 rig.animation_data_clear();rig.data.pose_position='REST';bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
 rig.data.pose_position='POSE';T.bind(rig,'Idle');bpy.context.scene.frame_set(1)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,use_custom_props=True)
 rows.append({'name':name,'role':role,'skin_srgb':'#'+skin,'hair_srgb':'#'+hair,'shirt_srgb':'#'+shirt,'pants_srgb':'#'+pants,'fbx_sha256':sha(O/(name+'.fbx')),'materials':[{'name':m.name,'linear_rgba':list(m.diffuse_color)} for m in ob.data.materials]});print('EXTRA GUEST',name,flush=True)
(O/'build-metrics-extra.json').write_text(json.dumps({'guests':rows,'no_crew_palette_names':True,'fps':24},indent=2));print('EXTRA BUILD PASS',flush=True)

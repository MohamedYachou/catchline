"""Eight review-face civilians; additive sources only. Run via run.py guests3-build."""
import bpy,sys,math,json,hashlib,importlib.util,ast
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
sp=importlib.util.spec_from_file_location('town',str(R/'Art/Source/Townsfolk/build.py'));T=importlib.util.module_from_spec(sp);sp.loader.exec_module(T)
T.SOURCE=O.parent/'Clothes/CrewRig_Restaurant.blend'
tree=ast.parse((O/'build-v2.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='pose_action');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<accepted seated clips>','exec'))
GUESTS=[('Marta','B47B51','653421','7D8F66','444E45','bob'),('Nils','B47A50','4B3024','B9522B','354355','beard'),('Pia','BB8157','6E3424','E48272','606B59','pigtails'),('Greta','D7AA85','D9D8CA','327D7C','465564','sunhat'),('Henrik','C48E66','92948A','C49534','33475E','fisher'),('Zola','855036','26251F','D46943','4B4450','curls'),('Vera','BDA17A','E0DFCF','225C65','33454C','chignon'),('Anton','B89B78','CCCDC4','2C3E60','303D52','ascot')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for idx,(short,skin,hair,shirt,pants,style) in enumerate(GUESTS):
 name='Guest_'+short;rig=T.init();s=T.Skin(rig)
 for key,h in [('M_Skin',skin),('M_HairChestnut',hair),('M_HairSilver',hair),('M_SeaTeal',shirt),('M_HullNavy',pants)]:T.H.MATERIALS[key]=T.H.material(name+'_'+key[2:],'#'+h)
 for key,m in T.H.MATERIALS.items():m.name=name+'_'+key.replace('M_','')
 T.torso(s,'M_SeaTeal');T.limbs(s,'M_SeaTeal',pants='M_HullNavy',rolled=False,boots=False);T.face(s,old=style in ['sunhat','fisher','chignon','ascot']);T.hair(s,long=style in ['bob','pigtails','chignon'])
 # Cream inset blouse/shirt remains distinct from outer cardigan/jacket.
 if style in ['bob','beard','curls','ascot']:
  s.ell((0,-.087,.459),(.064,.021,.082),'M_RailIvory','Spine',seg=10,rings=4)
  for sign in [-1,1]:
   s.part('add',[(sign*.11,-.068,.525),(sign*.022,-.116,.412),(sign*.052,-.112,.486)],[(0,1,2)],'M_SeaTeal',bone='Spine')
 if style=='bob':
  for sign in [-1,1]:
   for j in range(5):s.ell((sign*(.148+.012*math.sin(j)),.02,.69+j*.039),(.054,.107,.047),'M_HairChestnut','Head',seg=8,rings=3)
  for z in [.34,.39,.44]:s.ell((.019,-.11,z),(.006,.006,.006),'M_BandIvory','Spine',seg=6,rings=2)
 if style=='beard':
  s.ell((0,-.106,.663),(.078,.038,.052),'M_HairChestnut','Head',seg=12,rings=4)
  s.ell((0,-.111,.716),(.109,.043,.049),'M_HairChestnut','Head',seg=12,rings=4)
  # Smile remains on top of beard rather than submerged.
  s.tube([(-.028,-.155,.716),(0,-.165,.708),(.028,-.155,.716)],[.004]*3,'M_Rubber','Head',sides=5)
 if style=='pigtails':
  # Child's pigtails with small sage bow knots; scale fitted into adult animation skeleton below.
  for sign in [-1,1]:
   for j in range(6):
    a=j*math.tau/6;s.ell((sign*(.198+.022*math.sin(a)),.018+.031*math.cos(a),.82+.064*math.sin(a)),(.043,.044,.043),'M_HairChestnut','Head',seg=8,rings=3)
   for q in [-1,1]:s.ell((sign*.173+q*.018,-.053,.887),(.025,.014,.017),'M_HullNavy','Head',seg=6,rings=3)
  s.lathe([(.25,.151,.116,0),(.34,.14,.101,0)],'M_SeaTeal','Hips',segments=16)
 if style=='sunhat':
  T.cap(s,'M_RailIvory','sou')
  s.lathe([(.924,.172,.153,0),(.947,.166,.149,0)],'M_SeaTeal','Head',segments=16)
  for sign in [-1,1]:
   p=[(sign*.062+.039*math.cos(i*math.tau/16),-.159,.778+.032*math.sin(i*math.tau/16)) for i in range(17)];s.tube(p,[.004]*17,'M_Rubber','Head',sides=5)
   s.tube([(sign*.10,-.065,.525),(sign*.065,-.111,.348)],[.007]*2,'M_Rubber','Spine',sides=5)
  s.tube([(-.023,-.16,.782),(.023,-.16,.782)],[.003]*2,'M_Rubber','Head',sides=5)
  s.box((0,-.126,.346),(.082,.025,.052),'M_Rubber','Spine');s.ell((0,-.144,.346),(.025,.013,.022),'M_HullNavy','Spine',seg=10,rings=3)
 if style=='fisher':
  T.cap(s,'M_HullNavy','beanie');s.ell((0,-.104,.659),(.091,.04,.059),'M_HairSilver','Head',seg=12,rings=4);s.ell((0,-.106,.71),(.119,.05,.065),'M_HairSilver','Head',seg=12,rings=4)
  s.tube([(-.03,-.16,.72),(0,-.171,.711),(.03,-.16,.72)],[.004]*3,'M_Rubber','Head',sides=5)
  s.lathe([(.515,.078,.073,0),(.541,.066,.063,0)],'M_HullNavy','Spine1',segments=12)
  for x in [-.09,-.045,0,.045,.09]:s.tube([(x,-.102,.36),(x,-.106,.46)],[.0025]*2,'M_SeaTeal','Spine',sides=4)
 if style=='curls':
  # Dense rounded crown, no smooth helmet silhouette.
  for j in range(5):
   z=.79+j*.038;r=.178*math.sqrt(max(.10,1-((z-.79)/.21)**2))
   for k in range(12):
    a=k*math.tau/12+j*.23;y=r*.91*math.sin(a)
    if y<-.075 and z<.875:continue
    s.ell((r*math.cos(a),y,z),(.041,.039,.04),'M_HairChestnut','Head',seg=8,rings=3)
  for sign in [-1,1]:s.ell((sign*.179,-.025,.731),(.009,.009,.012),'M_OilskinYellow','Head',seg=6,rings=3)
 if style=='chignon':
  s.ell((0,.146,.889),(.09,.076,.087),'M_HairSilver','Head',seg=12,rings=4)
  for sign in [-1,1]:
   s.ell((sign*.18,-.018,.731),(.01,.011,.013),'M_RailIvory','Head',seg=8,rings=3)
   s.ell((sign*.028,-.107,.494),(.032,.015,.026),'M_RailIvory','Spine',seg=8,rings=3)
  s.tube([(0,-.11,.492),(-.035,-.114,.419)],[.015,.01],'M_RailIvory','Spine',sides=6)
  for i in range(9):
   a=math.pi*(i+1)/10;s.ell((.078*math.cos(a),-.112,.526-.034*math.sin(a)),(.005,.005,.005),'M_RailIvory','Spine',seg=6,rings=2)
 if style=='ascot':
  s.ell((0,-.118,.482),(.026,.012,.041),'M_SafetyOrange','Spine',seg=8,rings=3)
  # Burgundy ascot uses a civilian material, no crew colour remap name.
  mat=T.H.MATERIALS['M_SafetyOrange'];mat.diffuse_color=(.21,.027,.043,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=mat.diffuse_color
  for sign in [-1,1]:s.ell((sign*.029,-.154,.725),(.035,.012,.012),'M_HairSilver','Head',seg=8,rings=3)
 # Pia is visibly child-sized; accepted fitted-mesh scaling maintains existing bind skeleton.
 ob=s.finish(name,scale=.82 if style=='pigtails' else 1);uv=ob.data.uv_layers.new(name='UVMap')
 for p in ob.data.polygons:
  for li in p.loop_indices:
   co=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(co.x+.5,co.z)
 assert all(not m.name.startswith('M_') for m in ob.data.materials)
 for clip in ['Sit','Eat']:pose_action(rig,clip)
 rig.animation_data_clear();rig.data.pose_position='REST';bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
 rig.data.pose_position='POSE';T.bind(rig,'Idle');bpy.context.scene.frame_set(1)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',colors_type='LINEAR',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,use_custom_props=True)
 rows.append({'name':name,'face':f'v2-guest-{idx+9:02}.png','style':style,'fbx_sha256':sha(O/(name+'.fbx')),'blend_sha256':sha(O/(name+'.blend')),'skin':skin,'hair':hair,'top':shirt,'bottom':pants});print('GUEST3 EXPORTED',name,flush=True)
(O/'guests3-metrics.json').write_text(json.dumps({'guests':rows,'clip_source_sha256':sha(T.SOURCE),'clips':'20 current crew clips unchanged + Sit/Eat =22','fps':24},indent=2))

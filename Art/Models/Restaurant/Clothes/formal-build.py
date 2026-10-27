import bpy,sys,math,json,hashlib,importlib.util,shutil
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
B=O/'_formal-backup'
if not (B/'CrewRig_Restaurant.blend').exists():
 with bpy.data.libraries.load(str(O/'CrewRig_Restaurant.blend'),link=False) as (source,_):
  assert 'Outfit_HostFormal' not in source.objects, 'Formal delivery already present. Rebuild accepted baseline with clothes2-build.py before running this one-shot additive builder.'
B.mkdir(exist_ok=True)
for ext in ['blend','fbx']:
 p=O/('CrewRig_Restaurant.'+ext)
 if not (B/p.name).exists():shutil.copy2(p,B/p.name)
sp=importlib.util.spec_from_file_location('town',str(R/'Art/Source/Townsfolk/build.py'));T=importlib.util.module_from_spec(sp);sp.loader.exec_module(T)
bpy.ops.wm.open_mainfile(filepath=str(B/'CrewRig_Restaurant.blend'));bpy.context.preferences.filepaths.save_version=0
rig=bpy.data.objects['CrewRig'];rig.animation_data_clear();rig.data.pose_position='REST'
for o in bpy.context.scene.objects:o.hide_set(False)
# Existing accepted Host garment is duplicated; every accepted mesh remains unchanged.
host=bpy.data.objects['Outfit_Host'];out=host.copy();out.data=host.data.copy();out.name='Outfit_HostFormal';bpy.context.scene.collection.objects.link(out)
navy=next(m for m in out.data.materials if m.name.startswith('R_Navy'))
for i,m in enumerate(out.data.materials):
 if m.name.startswith('R_Ivory'):out.data.materials[i]=navy
P={'F_Navy':'#142F55','F_Gold':'#E8B64F','F_Teal':'#147B89','F_Jewel':'#1EA6A4','F_Hair':'#50392E'}
T.H.PALETTE.update(P)
for n,c in T.H.PALETTE.items():T.H.MATERIALS[n]=T.H.material(n,c)
s=T.Skin(rig)
# Swept gold lapels sit outside the faceted jacket; paired edging and cuffs read at phone scale.
for sign in [-1,1]:
 s.tube([(sign*.084,-.090,.539),(sign*.112,-.079,.507),(sign*.063,-.111,.480),(sign*.088,-.096,.465),(sign*.017,-.120,.404)],[.005]*5,'F_Gold','Spine',sides=6)
 # Gold cuff is weighted like the original sleeve envelope.
 s.tube([(sign*.365,0,.510),(sign*.385,0,.510)],[.048,.046],'F_Gold',weights=lambda p,k='Left' if sign==1 else 'Right':T.armweights(k,p),sides=10)
 # Teardrop earrings, solid gold with teal central stones.
 s.ell((sign*.179,-.018,.728),(.013,.012,.023),'F_Gold','Head',seg=8,rings=4)
 s.ell((sign*.179,-.029,.728),(.007,.005,.014),'F_Jewel','Head',seg=8,rings=3)
# Gold wrap edge on a flared navy coat-dress; existing skirt envelope retains verified Walk clearance.
s.lathe([(.172,.197,.192,0),(.182,.196,.191,0)],'F_Gold','Hips',segments=24)
s.tube([(.055,-.111,.355),(.068,-.128,.30),(.079,-.155,.24),(.087,-.173,.18)],[.0045]*4,'F_Gold','Hips',sides=6)
s.box((.025,-.116,.367),(.046,.013,.027),'F_Gold','Hips');s.box((.025,-.124,.367),(.029,.004,.015),'F_Navy','Hips')
# Teal neck scarf and folded asymmetric tail, no white blouse triangle.
s.lathe([(.543,.069,.060,0),(.564,.064,.057,0),(.581,.057,.052,0)],'F_Teal','Neck',segments=16)
s.ell((.052,-.066,.550),(.027,.021,.023),'F_Teal','Neck',seg=10,rings=4)
s.tube([(.054,-.077,.545),(.088,-.099,.514),(.065,-.119,.482)],[.024,.028,.010],'F_Teal','Spine',sides=6)
s.ell((-.057,-.104,.486),(.017,.008,.013),'F_Gold','Spine',seg=8,rings=3)
extra=s.finish('formal garment details')
bpy.ops.object.select_all(action='DESELECT');out.select_set(True);extra.select_set(True);bpy.context.view_layer.objects.active=out;bpy.ops.object.join()
h=T.Skin(rig)
# Neutral chestnut updo fits the unchanged Body head and closes its exposed crown.
h.ell((0,.012,.916),(.189,.172,.089),'F_Hair','Head',seg=20,rings=7)
h.ell((0,.143,.985),(.099,.077,.095),'F_Hair','Head',seg=16,rings=6)
for j in range(3):
 h.tube([(-.15,.01+j*.035,.952),(-.08,.015+j*.035,.999),(0,.045+j*.035,1.01),(.10,.075+j*.035,.977)],[.009,.014,.013,.005],'F_Hair','Head',sides=7)
h.box((-.064,-.122,.947),(.065,.012,.014),'F_Gold','Head')
for x,z in [(-.08,.954),(-.062,.966),(-.047,.977)]:h.ell((x,-.128,z),(.009,.006,.017),'F_Gold','Head',seg=6,rings=3)
hat=h.finish('Hat_HairUpClip')
for ob in [out,hat]:
 uv=ob.data.uv_layers.new(name='UVMap') if not ob.data.uv_layers else ob.data.uv_layers[0]
 for p in ob.data.polygons:
  for li in p.loop_indices:
   co=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=((co.x+.5),co.z)
 ob['look_reference']='Art/Source/Restaurant/clothes/2d/mira-d-sheet.png';ob['toggle_contract']='Enable with Body; all previous siblings preserved'
rig.data.pose_position='POSE';T.bind(rig,'Idle');bpy.context.scene.frame_set(13)
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':ob.hide_render=ob.name not in ['Body','Outfit_HostFormal','Hat_HairUpClip']
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CrewRig_Restaurant.blend'))
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
 if ob.type in ['MESH','ARMATURE']:ob.hide_set(False);ob.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
print('FORMAL BUILD PASS',flush=True)

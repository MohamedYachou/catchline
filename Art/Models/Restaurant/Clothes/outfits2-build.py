"""Classic restaurant tailoring additions; never rebuilds accepted rig/actions."""
import bpy,sys,json,importlib.util,shutil
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[3];B=O/'_outfits2-backup';B.mkdir(exist_ok=True)
for ext in ['blend','fbx']:
 p=O/('CrewRig_Restaurant.'+ext)
 if not (B/p.name).exists():shutil.copy2(p,B/p.name)
bpy.ops.wm.open_mainfile(filepath=str(O/'CrewRig_Restaurant.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;rig=bpy.data.objects['CrewRig'];rig.animation_data_clear();rig.data.pose_position='REST'
sp=importlib.util.spec_from_file_location('town',str(R/'Art/Source/Townsfolk/build.py'));T=importlib.util.module_from_spec(sp);sp.loader.exec_module(T)
T.H.PALETTE.update({'C2_Ivory':'#F3F0DC','C2_Navy':'#182F46','C2_Wine':'#773F41','C2_Gold':'#E5B24A','C2_Teal':'#1EA6A4'})
for n,c in T.H.PALETTE.items():T.H.MATERIALS[n]=T.H.material(n,c)
def merge(name,s):
 target=bpy.data.objects[name];q=s.finish('WardrobeDetail');uv=q.data.uv_layers.new(name='UVMap')
 for p in q.data.polygons:
  for i in p.loop_indices:
   co=q.data.vertices[q.data.loops[i].vertex_index].co;uv.data[i].uv=(co.x+.5,co.z)
 bpy.ops.object.select_all(action='DESELECT');target.hide_set(False);target.select_set(True);q.select_set(True);bpy.context.view_layer.objects.active=target;bpy.ops.object.join()
if not sc.get('outfits2_v1'):
 # Waiter waistcoat gets navy lapels and a sculpted wine bow rather than teal workwear accents.
 for name in ['Outfit_WaiterSuit','Outfit_HelperSuit']:
  ob=bpy.data.objects[name];navy=next(m for m in ob.data.materials if m.name.startswith('R_Navy'))
  for i,m in enumerate(ob.data.materials):
   if m.name.startswith('R_Teal'):ob.data.materials[i]=navy
  s=T.Skin(rig)
  for sign in [-1,1]:
   s.ell((sign*.021,-.138,.489),(.023,.012,.016),'C2_Wine','Spine',seg=8,rings=3)
   s.tube([(sign*.114,-.074,.514),(sign*.079,-.114,.462),(sign*.018,-.133,.418)],[.006]*3,'C2_Navy','Spine',sides=6)
  s.ell((0,-.146,.489),(.009,.008,.012),'C2_Navy','Spine',seg=8,rings=3)
  for z in [.405,.438]:s.ell((0,-.135,z),(.006,.006,.006),'C2_Gold','Spine',seg=6,rings=3)
  merge(name,s)
 # White bib and softly flared apron over the accepted navy skirt. Blouse sleeves stay ivory.
 s=T.Skin(rig)
 s.part('add',[(-.065,-.123,.486),(.065,-.123,.486),(.073,-.130,.365),(-.073,-.130,.365)],[(0,1,2,3)],'C2_Ivory',bone='Spine')
 s.part('add',[(-.073,-.132,.363),(.073,-.132,.363),(.133,-.192,.191),(-.133,-.192,.191)],[(0,1,2,3)],'C2_Ivory',bone='Hips')
 for sign in [-1,1]:s.tube([(sign*.053,-.12,.476),(sign*.075,-.087,.536)],[.012,.012],'C2_Ivory','Spine',sides=6)
 s.lathe([(.360,.147,.119,0),(.376,.147,.119,0)],'C2_Ivory','Hips',segments=20)
 s.box((.073,-.187,.246),(.045,.008,.035),'C2_Ivory','Hips');merge('Outfit_WaiterSkirt',s)
 # Formal host already has fitted coat-dress, updo, gold piping and teal scarf; enlarge the signature brooch slightly.
 s=T.Skin(rig);s.ell((-.057,-.118,.486),(.021,.008,.017),'C2_Gold','Spine',seg=10,rings=4);s.ell((-.057,-.127,.486),(.011,.004,.009),'C2_Teal','Spine',seg=8,rings=3);merge('Outfit_HostFormal',s)
 sc['outfits2_v1']=True
# Correct collar placement after first lit-room review. Preserve all other tailoring.
if not sc.get('outfits2_collar_v2'):
 for name in ['Outfit_WaiterSuit','Outfit_HelperSuit']:
  ob=bpy.data.objects[name];ids=set()
  for poly in ob.data.polygons:
   if ob.data.materials[poly.material_index].name.startswith('C2_Wine'):ids.update(poly.vertices)
  for v in ob.data.vertices:
   if v.index in ids or (abs(v.co.x)<.012 and v.co.y<-.136 and .474<v.co.z<.506):v.co.z+=.040
 sc['outfits2_collar_v2']=True
rig.data.pose_position='POSE';T.bind(rig,'Idle');sc.frame_set(13);bpy.ops.wm.save_as_mainfile(filepath=str(O/'CrewRig_Restaurant.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
 if o.type in ['ARMATURE','MESH']:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
print('OUTFITS2 BUILD PASS')

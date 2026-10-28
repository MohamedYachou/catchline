"""Critic on the exact delivered Ada bind rig and untouched thirteen actions."""
import sys,importlib.util,re,uuid,hashlib,json,bpy,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[2];sys.path.insert(0,str(O));sys.dont_write_bytecode=True
import build_props3 as P
sp=importlib.util.spec_from_file_location('town',R/'Art/Source/Townsfolk/build.py');T=importlib.util.module_from_spec(sp);sp.loader.exec_module(T)
SOURCE=R/'Art/Models/Restaurant/Guests/Guest_Ada.blend'
def atlas_skin(ob):
 cols=[tuple(ob.data.materials[p.material_index].diffuse_color) for p in ob.data.polygons]
 ob.data.uv_layers.new(name='UVMap');ob.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
 uv=ob.data.uv_layers['UVMap'];ca=ob.data.color_attributes['Color']
 im=bpy.data.images.get('Restaurant_BaseColor.png');px=int(7.5/8*im.size[0]);py=int((1-1.5/4)*im.size[1]);base=im.pixels[(py*im.size[0]+px)*4:(py*im.size[0]+px)*4+3]
 for p,col in zip(ob.data.polygons,cols):
  for li in p.loop_indices:uv.data[li].uv=(7.5/8,1-1.5/4);ca.data[li].color=tuple(col[i]/P.linear(base[i]) for i in range(3))+(1,)
 ob.data.materials.clear();ob.data.materials.append(P.b.MAT)
 for p in ob.data.polygons:p.material_index=0
 ob.data.color_attributes.active_color=ca
 ob.data.calc_loop_triangles()
def build():
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.preferences.filepaths.save_version=0
 rig=bpy.data.objects['CrewRig'];rig.animation_data_clear();rig.data.pose_position='REST'
 for ob in list(bpy.data.objects):
  if ob!=rig:bpy.data.objects.remove(ob,do_unlink=True)
 for mat in list(bpy.data.materials):bpy.data.materials.remove(mat)
 palette={**T.P,'M_Skin':'#C58C60','M_HairChestnut':'#909996','M_Coat':'#26384C','M_Lapel':'#425569','M_Beret':'#252E38','M_Notebook':'#9D493F','M_Pages':'#EBD9AC','M_Brass':'#D7A746'}
 T.H.PALETTE.update(palette)
 for name,col in palette.items():T.H.MATERIALS[name]=T.H.material(name,col)
 s=T.Skin(rig);T.torso(s,'M_Coat');T.limbs(s,'M_Coat',pants='M_HullNavy');T.face(s);T.hair(s,col='M_HairChestnut')
 s.lathe([(.31,.147,.111,0),(.40,.15,.112,0),(.49,.132,.1,0),(.54,.102,.077,0),(.56,.053,.048,0)],'M_Coat','Spine')
 # Split tails are weighted to the upper legs so the long coat bends with Sit/Eat.
 for sign,side in [(1,'Left'),(-1,'Right')]:
  start=len(s.g.vertices);s.lathe([(.19,.089,.123,0),(.255,.091,.12,0),(.33,.091,.109,0)],'M_Coat','Hips',segments=10)
  for i in range(start,len(s.g.vertices)):
   p=Vector(s.g.vertices[i]);p.x+=sign*.081;s.g.vertices[i]=tuple(p);s.weights[i]=T.blend('Hips',side+'UpLeg',(.34-p.z)/.11)
  # Lapel planes follow the front of the coat, deliberately broad at room scale.
  v=[(sign*.037,-.075,.546),(sign*.097,-.080,.511),(sign*.045,-.112,.458),(sign*.016,-.113,.493)]
  s.part('add',v,[(0,1,2,3)],'M_Lapel',bone='Spine')
  s.box((sign*.112,-.075,.364),(.043,.012,.009),'M_Lapel','Spine')
 for z in [.351,.397,.441]:s.ell((0,-.115,z),(.008,.005,.008),'M_Brass','Spine',seg=6,rings=2)
 s.box((0,-.081,.539),(.034,.020,.045),'M_Pages','Spine')
 s.tube([(-.042,-.061,.56),(0,-.080,.548),(.043,-.061,.56)],[.014]*3,'M_SeaTeal','Neck',sides=5)
 # Beret: dark rolled band, asymmetric soft crown and small top stalk.
 s.lathe([(.869,.18,.159,0),(.891,.18,.159,0)],'M_Beret','Head')
 start=len(s.g.vertices);s.lathe([(.89,.196,.171,0),(.927,.214,.18,.005),(.972,.155,.132,.008),(.991,.046,.044,.008)],'M_Beret','Head',segments=12)
 for i in range(start,len(s.g.vertices)):
  x,y,z=s.g.vertices[i];s.g.vertices[i]=(x+.035,y,z-.09*x)
 s.tube([(.03,.008,.982),(.038,.008,1.012)],[.009,.007],'M_Beret','Head',sides=6)
 # Round frames are actual open rings with bridge and temple arms, no opaque lenses.
 for sign in [-1,1]:
  path=[(sign*.062+.036*math.cos(i*math.tau/12),-.160,.777+.036*math.sin(i*math.tau/12)) for i in range(13)]
  s.tube(path,[.0048]*13,'M_Brass','Head',sides=4)
  s.tube([(sign*.097,-.159,.784),(sign*.155,-.1,.788),(sign*.168,-.007,.773)],[.0045]*3,'M_Beret','Head',sides=4)
 s.tube([(-.026,-.162,.784),(0,-.177,.791),(.026,-.162,.784)],[.0045]*3,'M_Brass','Head',sides=4)
 body=s.finish('Restaurant_Guest_Critic');n=T.Skin(rig)
 n.box((.445,-.042,.464),(.126,.021,.106),'M_Notebook','LeftHand')
 n.box((.445,-.043,.464),(.112,.022,.089),'M_Pages','LeftHand')
 for yy in [-.057,-.028]:n.box((.445,yy,.464),(.129,.005,.109),'M_Notebook','LeftHand')
 n.box((.478,-.061,.464),(.007,.003,.109),'M_Brass','LeftHand')
 notebook=n.finish('Critic_Notebook')
 P.b.MAT=P.material()
 for ob in [body,notebook]:atlas_skin(ob)
 tris=sum(len(ob.data.loop_triangles) for ob in [body,notebook]);assert tris<6000,tris
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.context.scene.render.fps=24
 name=body.name;path=R/'Assets/Art/Models/Restaurant/Guests'/(name+'.fbx');src=O/'blends'/('props3-'+name+'.blend')
 bpy.ops.wm.save_as_mainfile(filepath=str(src),check_existing=False)
 rig.data.pose_position='POSE';T.bind(rig,'Idle');bpy.context.scene.frame_set(1)
 bpy.ops.object.select_all(action='DESELECT')
 for ob in [rig,body,notebook]:ob.select_set(True)
 bpy.context.view_layer.objects.active=rig
 P.b.export_fbx_bin.save(P.b.OP,bpy.context,filepath=str(path),use_selection=True,object_types={'MESH','ARMATURE'},global_matrix=P.b.axis_conversion(to_forward='-Z',to_up='Y').to_4x4(),axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,use_custom_props=True,use_triangles=True,path_mode='STRIP')
 meta=Path(str(path)+'.meta');template=(path.parent/'Restaurant_Guest_Ada.fbx.meta').read_text();guid=re.search(r'^guid: (.+)$',meta.read_text(),re.M).group(1) if meta.exists() else uuid.uuid4().hex
 template=re.sub(r'^guid: .+$','guid: '+guid,template,flags=re.M).replace('  externalObjects: {}','  externalObjects:\n  - first:\n      type: UnityEngine:Material\n      assembly: UnityEngine.CoreModule\n      name: RestaurantAtlas\n    second: {fileID: 2100000, guid: 93ede68a78343aa4bbc6d4deed7baeec, type: 2}')
 meta.write_text(template)
 rec=dict(name=name,tris=tris,triangle_limit_exclusive=6000,rig='CrewRig',children=['Critic_Notebook'],file=path.relative_to(R).as_posix(),source=src.relative_to(R).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),material='RestaurantAtlas',render_review='PENDING',renders=[],origin_offset_authored=[0,0,0],size_xyz_unity_m=[.94,1.02,.35],actions=[a.name for a in bpy.data.actions],notebook_attachment='LeftHand 100%, separate skinned child of CrewRig',import_settings='Exact Ada ModelImporter except new GUID and explicit canonical material external remap')
 P.save_manifest(rec);print('CRITIC BUILT',tris,flush=True)
if __name__=='__main__':build()

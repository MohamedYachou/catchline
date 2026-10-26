"""Add toggleable wardrobe siblings to an untouched import of the production CrewRig."""
import bpy,bmesh,sys,json,hashlib,math,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
sp=importlib.util.spec_from_file_location('town',str(R/'Art/Source/Townsfolk/build.py'));T=importlib.util.module_from_spec(sp);sp.loader.exec_module(T)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(o):
 if o.type=='ARMATURE':return {'bones':{b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(r) for r in b.matrix_local]} for b in o.data.bones}}
 d={'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'smooth':[p.use_smooth for p in o.data.polygons],'material_indices':[p.material_index for p in o.data.polygons],'materials':[m.name for m in o.data.materials],'weights':[{o.vertex_groups[g.group].name:round(g.weight,7) for g in v.groups} for v in o.data.vertices],'uv':[[list(v.uv) for v in l.data] for l in o.data.uv_layers],'matrix':[list(r) for r in o.matrix_world]}
 return {'sha256':hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest(),'vertices':len(d['vertices']),'triangles':sum(len(f)-2 for f in d['faces'])}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(R/'Assets/Art/Models/Crew/CrewRig.fbx'))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');rig.animation_data_clear();rig.data.pose_position='REST'
bpy.context.view_layer.update()
originals={o.name:snapshot(o) for o in bpy.context.scene.objects};original_meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];actions={a.name:list(a.frame_range) for a in bpy.data.actions}
# Build from accepted garment forms, omitting all identity-specific scalp, hair, jewellery and skin.
# Original Body already supplies the neutral face, crown, hands and underlying limbs.
source_rows=[('Outfit_Host','Host_Mira'),('Outfit_CookWhites','Cook_Dirk'),('Outfit_WaiterSkirt','Server_Ana'),('Outfit_WaiterSuit','Helper_Captain'),('Outfit_Barista','Barista_Ines'),('Outfit_Handyman','Handyman_Olaf'),('Outfit_HelperSuit','Helper_Captain'),('Outfit_Dishwasher','Dishwasher_Olaf')]
added=[]
for name,src in source_rows:
 with bpy.data.libraries.load(str(O/(src+'.blend')),link=False) as (a,b):b.objects=[src+'_Outfit']
 ob=b.objects[0];bpy.context.scene.collection.objects.link(ob)
 # Keep only garment materials. Anything weighted solely to Head is a person crown/accessory or chef cap.
 groups={g.index:g.name for g in ob.vertex_groups}
 valid=[]
 for p in ob.data.polygons:
  m=ob.data.materials[p.material_index];skin='Skin' in m.name or 'Hands' in m.name
  head=all(any(groups[g.group]=='Head' and g.weight>.99 for g in ob.data.vertices[v].groups) for v in p.vertices)
  if not skin and not head:valid.append(p)
 ids=sorted({v for p in valid for v in p.vertices});lookup={old:i for i,old in enumerate(ids)}
 # Offset garment envelope very slightly so unchanged original Body never z-fights through cloth.
 verts=[]
 for i in ids:
  v=ob.data.vertices[i].co.copy()
  # Original neutral body has heavy oilskin/boots; the new garments cover those using a 5mm envelope.
  if v.z<.57:
   if abs(v.x)>.16:v.y*=1.08;v.z=.51+(v.z-.51)*1.08
   else:v.x*=1.05;v.y*=1.08
  verts.append(v)
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],[[lookup[v] for v in p.vertices] for p in valid]);mesh.update()
 used=sorted({p.material_index for p in valid})
 for i in used:mesh.materials.append(ob.data.materials[i])
 out=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(out);out.parent=rig
 for b in rig.data.bones:out.vertex_groups.new(name=b.name)
 for ni,old in enumerate(ids):
  for g in ob.data.vertices[old].groups:out.vertex_groups[groups[g.group]].add([ni],g.weight,'REPLACE')
 for p,sourcep in zip(mesh.polygons,valid):p.material_index=used.index(sourcep.material_index);p.use_smooth=sourcep.use_smooth
 mod=out.modifiers.new('CrewSkin','ARMATURE');mod.object=rig
 out['source_accepted_garment']=src;out['neutral_skin']='Original Body supplies unchanged crown, face, hands; no identity mesh copied'
 # An exact-weight opaque lining follows the original body's sleeves/shoulders.
 # This prevents original navy skin-shell showing through ivory garments in animation.
 body=bpy.data.objects['Body'];lining=body.copy();lining.data=body.data.copy();lining.name='temporary lining';bpy.context.scene.collection.objects.link(lining)
 bm=bmesh.new();bm.from_mesh(lining.data)
 reject=[f for f in bm.faces if not (body.data.materials[f.material_index].name=='M_HullNavy' and min(v.co.z for v in f.verts)>.278)]
 bmesh.ops.delete(bm,geom=reject,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(lining.data);bm.free();lining.data.update()
 for v in lining.data.vertices:v.co+=v.normal*.008
 base=next(m for m in out.data.materials if m.name.startswith('R_Ivory' if name in ['Outfit_CookWhites','Outfit_WaiterSkirt','Outfit_Barista','Outfit_Dishwasher'] else 'R_Navy'))
 lining.data.materials.clear();lining.data.materials.append(base)
 for f in lining.data.polygons:f.material_index=0
 bpy.ops.object.select_all(action='DESELECT');out.select_set(True);lining.select_set(True);bpy.context.view_layer.objects.active=out;bpy.ops.object.join()
 added.append(out);bpy.data.objects.remove(ob,do_unlink=True)
# Standalone generic chef toque, toggle it separately from the outfit.
T.H.PALETTE.update({'R_Ivory':'#F3F0DC','R_Navy':'#173F57'})
for k,v in T.H.PALETTE.items():T.H.MATERIALS[k]=T.H.material(k,v)
s=T.Skin(rig);s.lathe([(.906,.172,.16,0),(.953,.172,.16,0),(.968,.168,.154,0)],'R_Ivory','Head',segments=16);s.ell((0,.005,1.023),(.179,.164,.088),'R_Ivory','Head',seg=12,rings=5)
for x in [-.09,-.045,0,.045,.09]:s.tube([(x,-.153,.955),(x,-.145,1.045)],[.003,.003],'R_Navy','Head',sides=4)
added.append(s.finish('Hat_Toque'))
# Discard imported foreign armature/action data; only original actions remain in the export.
print('PRESERVATION DIFF',[(n,v,snapshot(bpy.data.objects[n])) for n,v in originals.items() if snapshot(bpy.data.objects[n])!=v],flush=True)
assert all(snapshot(bpy.data.objects[n])==v for n,v in originals.items())
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=24;bpy.context.preferences.filepaths.save_version=0
for o in added:o.hide_render=o.name!='Outfit_Host';o.hide_set(o.hide_render)
for o in original_meshes:o.hide_render=o.name!='Body';o.hide_set(o.hide_render)
rig.data.pose_position='POSE';T.bind(rig,'Idle');sc.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CrewRig_Restaurant.blend'))
bpy.ops.object.select_all(action='DESELECT')
for o in original_meshes+added+[rig]:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(O/'CrewRig_Restaurant.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
(O/'clothes2-build-metrics.json').write_text(json.dumps({'source_sha256':sha(R/'Assets/Art/Models/Crew/CrewRig.fbx'),'originals_before':originals,'originals_after':{n:snapshot(bpy.data.objects[n]) for n in originals},'original_actions':actions,'added':[{ 'name':o.name,'source':o.get('source_accepted_garment'),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'materials':[m.name for m in o.data.materials]} for o in added],'fbx_sha256':sha(O/'CrewRig_Restaurant.fbx')},indent=2));print('CLOTHES2 BUILD PASS',flush=True)

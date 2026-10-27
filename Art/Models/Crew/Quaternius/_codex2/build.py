import bpy,bmesh,json,sys,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path(__file__).resolve().parents[5];O=R/'Art/Models/Crew/Quaternius';W=O/'_codex2';S=R/'Art/Downloads/quaternius/base/Universal Base Characters[Standard]'
rows=json.loads((W/'roster.json').read_text())
def rgba(h):
 c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c)+(1.,)
def material(name,h,texture=None):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=rgba(h);p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba(h);p.inputs['Roughness'].default_value=.76;p.inputs['Specular'].default_value=.22
 if texture:
  tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texture));tex.image.pack();m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);p.inputs['Base Color'].default_value=(1,1,1,1)
 return m
def sig(arm):
 return dict(name=arm.name,matrix=[list(x) for x in arm.matrix_world],bones=[dict(name=b.name,parent=b.parent.name if b.parent else None,matrix=[list(x) for x in b.matrix_local],length=b.length,scale=list(arm.pose.bones[b.name].scale)) for b in arm.data.bones])
def attach(obj,arm):
 bpy.context.view_layer.update();world=obj.matrix_world.copy()
 for mod in list(obj.modifiers):
  if mod.type=='ARMATURE':obj.modifiers.remove(mod)
 obj.parent=arm;obj.parent_type='BONE';obj.parent_bone='Head';obj.matrix_parent_inverse=Matrix.Identity(4)
 bpy.context.view_layer.update();obj.matrix_world=world;bpy.context.view_layer.update()
 assert max(abs(a-b) for rowa,rowb in zip(world,obj.matrix_world) for a,b in zip(rowa,rowb))<1e-5
 for g in list(obj.vertex_groups):obj.vertex_groups.remove(g)
def add_accessory(stem,arm,mat,trim=False):
 before=set(bpy.context.scene.objects);bpy.ops.import_scene.fbx(filepath=str(S/f'Hairstyles/Rigged to Head Bone/FBX (Unity)/{stem}.fbx'),ignore_leaf_bones=False,automatic_bone_orientation=False)
 added=set(bpy.context.scene.objects)-before;obj=next(o for o in added if o.type=='MESH');obj.name=stem
 if trim:
  bm=bmesh.new();bm.from_mesh(obj.data)
  # Retain the upper-lip patch of the supplied beard, remove chin/sideburns.
  remove=[f for f in bm.faces if f.calc_center_median().z<1.630 or f.calc_center_median().y>-.063 or abs(f.calc_center_median().x)>.062]
  bmesh.ops.delete(bm,geom=remove,context='FACES');loose=[v for v in bm.verts if not v.link_faces]
  if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
  bm.to_mesh(obj.data);bm.free();obj.name='Hair_Beard_Moustache'
 if stem=='Hair_Buns':
  for v in obj.data.vertices:v.co.z+=.050
 assert len(obj.data.vertices)>0
 attach(obj,arm)
 for ob in added:
  if ob!=obj:bpy.data.objects.remove(ob,do_unlink=True)
 obj.data.materials.clear();obj.data.materials.append(mat)
 for p in obj.data.polygons:p.material_index=0;p.use_smooth=True
 return obj
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [x['name'] for x in rows]
for row in rows:
 name=row['name']
 if name not in names:continue
 bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
 bpy.ops.import_scene.fbx(filepath=str(S/'Base Characters/Unity/Superhero_Male_FullBody.fbx'),ignore_leaf_bones=False,automatic_bone_orientation=False)
 arm=next(o for o in scene.objects if o.type=='ARMATURE');original=sig(arm)
 body=bpy.data.objects['SuperHero_Male'];eyes=bpy.data.objects['Eyes'];bpy.data.objects.remove(bpy.data.objects['Eyebrows'],do_unlink=True)
 for o in scene.objects:o.animation_data_clear()
 for act in list(bpy.data.actions):bpy.data.actions.remove(act)
 # Remove unused source material datablocks to retain exact slot names.
 for m in list(bpy.data.materials):
  for o in scene.objects:
   if o.type=='MESH':o.data.materials.clear()
  bpy.data.materials.remove(m)
 mats={k:material(k,row[h],W/f'{name}-{tex}.png' if tex else None) for k,h,tex in [('Skin','skinHex','skin'),('Suit','suitHex',None),('Hair','hairHex',None),('Eyes','eyeHex','eyes'),('Brows','hairHex',None)]}
 body.data.materials.append(mats['Skin']);body.data.materials.append(mats['Suit'])
 # Only neck/head and hands are bare. Existing mesh/UV/weights remain unchanged.
 skin_count=0
 for p in body.data.polygons:
  vs=[body.data.vertices[i] for i in p.vertices];center=sum((v.co for v in vs),Vector())/len(vs)
  bare=center.z>=1.535 or abs(center.x)>=.710
  p.material_index=0 if bare else 1;p.use_smooth=True;skin_count+=bare
 eyes.data.materials.append(mats['Eyes']);[setattr(p,'material_index',0) for p in eyes.data.polygons]
 add_accessory(row['hair'],arm,mats['Hair'])
 add_accessory('Eyebrows_Regular',arm,mats['Brows'])
 if row['beard']:add_accessory('Hair_Beard',arm,mats['Hair'],row['beard']=='moustache')
 # Accessory imports may bring stale source material datablocks, never exported.
 bpy.context.view_layer.update();assert sig(arm)==original
 assert all(max(abs(x-(1 if i%5==0 else 0)) for i,x in enumerate([q for r in pb.matrix_basis for q in r]))<1e-5 for pb in arm.pose.bones)
 bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=arm
 blend=W/f'{name}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
 bpy.ops.export_scene.fbx(filepath=str(O/f'{name}.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1.,apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',bake_space_transform=False,axis_forward='-Z',axis_up='Y',use_mesh_modifiers=False,mesh_smooth_type='FACE',add_leaf_bones=False,use_armature_deform_only=False,bake_anim=False,path_mode='COPY',embed_textures=True)
 details=dict(name=name,sourceSkeleton=original,skinPolygons=skin_count,suitPolygons=len(body.data.polygons)-skin_count,objects=[dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None,parentType=o.parent_type,parentBone=o.parent_bone,vertices=len(o.data.vertices) if o.type=='MESH' else None,materials=[m.name for m in o.data.materials] if o.type=='MESH' else []) for o in scene.objects],fbxSha256=hashlib.sha256((O/f'{name}.fbx').read_bytes()).hexdigest())
 (W/f'{name}-build.json').write_text(json.dumps(details,indent=2)+'\n');print('BUILT',name,skin_count,'skin faces',flush=True)

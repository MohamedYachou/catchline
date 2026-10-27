import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[5];O=R/'Art/Models/Crew/Quaternius';W=O/'_codex2';S=R/'Art/Downloads/quaternius/base/Universal Base Characters[Standard]'
def import_fbx(p):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(p),ignore_leaf_bones=False,automatic_bone_orientation=False)
 return next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
def matrices(arm):return {b.name:dict(parent=b.parent.name if b.parent else None,matrix=[list(x) for x in b.matrix_local]) for b in arm.data.bones}
def worldverts(o):return [o.matrix_world@v.co for v in o.data.vertices]
def error(a,b):return max(abs(x-y) for ra,rb in zip(a,b) for x,y in zip(ra,rb))
a=import_fbx(S/'Base Characters/Unity/Superhero_Male_FullBody.fbx');original=matrices(a);armworld=a.matrix_world.copy();basebody=worldverts(bpy.data.objects['SuperHero_Male']);origuv=[list(u.uv) for u in bpy.data.objects['SuperHero_Male'].data.uv_layers.active.data];origweights=[{bpy.data.objects['SuperHero_Male'].vertex_groups[g.group].name:float(g.weight) for g in v.groups} for v in bpy.data.objects['SuperHero_Male'].data.vertices]
rows=json.loads((W/'roster.json').read_text());names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [r['name'] for r in rows]
results=[]
for row in rows:
 if row['name'] not in names:continue
 name=row['name'];a=import_fbx(O/f'{name}.fbx');bones=matrices(a);body=bpy.data.objects['SuperHero_Male'];objects=list(bpy.context.scene.objects);meshes=[o for o in objects if o.type=='MESH'];mats={m.name for o in meshes for m in o.data.materials};attachments=[o for o in meshes if o.name.startswith('Hair_') or o.name.startswith('Eyebrows_')]
 checks={};checks['bone_names_exact']=set(original)==set(bones);checks['bone_parents_exact']=all(bones[k]['parent']==v['parent'] for k,v in original.items());delta=max(error(v['matrix'],bones[k]['matrix']) for k,v in original.items());checks['bone_rest_matrices']=delta<1e-4;checks['armature_transform']=error(armworld,a.matrix_world)<1e-5
 checks['one_original_armature']=sum(o.type=='ARMATURE' for o in objects)==1;checks['five_named_materials']=mats=={'Skin','Suit','Hair','Eyes','Brows'};checks['no_animations']=not bpy.data.actions and all(not o.animation_data or not o.animation_data.action for o in objects)
 bind_error=max(error(p.matrix_basis,Matrix.Identity(4)) for p in a.pose.bones);checks['bind_pose']=bind_error<1e-4;checks['no_clothing_meshes']=set(o.name for o in meshes)=={'SuperHero_Male','Eyes',row['hair'],'Eyebrows_Regular'}|({'Hair_Beard_Moustache' if row['beard']=='moustache' else 'Hair_Beard'} if row['beard'] else set())
 coords=worldverts(body);vertex_error=max((x-y).length for x,y in zip(coords,basebody));checks['body_vertices_unchanged']=len(coords)==len(basebody) and vertex_error<1e-5
 uv=[list(u.uv) for u in body.data.uv_layers.active.data];uv_error=max(abs(x-y) for a,b in zip(uv,origuv) for x,y in zip(a,b));checks['body_uv_unchanged']=len(uv)==len(origuv) and uv_error<1e-6
 weights=[{body.vertex_groups[g.group].name:float(g.weight) for g in v.groups} for v in body.data.vertices];checks['body_skin_weights_unchanged']=len(weights)==len(origweights) and all(set(v)==set(w) and all(abs(v[k]-w[k])<1e-5 for k in v) for v,w in zip(origweights,weights))
 checks['nonempty_meshes']=all(len(o.data.vertices)>0 and len(o.data.polygons)>0 for o in meshes)
 checks['head_parented']=all(o.parent==a and o.parent_type=='BONE' and o.parent_bone=='Head' and not any(m.type=='ARMATURE' for m in o.modifiers) for o in attachments)
 imgs=[n.image for mat in bpy.data.materials if mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image];checks['two_decoded_textures']=len(imgs)==2 and all(im.has_data and im.size[0]>0 for im in imgs)
 before={o.name:o.matrix_world.copy() for o in attachments};p=a.pose.bones['Head'];p.rotation_mode='XYZ';p.rotation_euler.z=.3;bpy.context.view_layer.update();head_delta=a.matrix_world@p.matrix@a.data.bones['Head'].matrix_local.inverted()@a.matrix_world.inverted();follow=max(error(head_delta@before[o.name],o.matrix_world) for o in attachments);checks['head_rotation_follow']=follow<1e-5;p.rotation_euler.z=0;bpy.context.view_layer.update()
 detail=dict(name=name,passAll=all(checks.values()),checks=checks,boneCount=len(bones),matrixTolerance=1e-4,maxBodyVertexError=vertex_error,maxBodyUvError=uv_error,maxRestMatrixError=delta,maxBindMatrixError=bind_error,headFollowMatrixError=follow,bodyHeight=max(v.z for v in coords)-min(v.z for v in coords),triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),materials=sorted(mats),attachments=[dict(name=o.name,parentBone=o.parent_bone,vertices=len(o.data.vertices)) for o in attachments],textures=[dict(name=im.name,size=list(im.size),path=im.filepath) for im in imgs],sha256=hashlib.sha256((O/f'{name}.fbx').read_bytes()).hexdigest())
 (W/f'{name}-audit.json').write_text(json.dumps(detail,indent=2)+'\n');print(json.dumps(detail),flush=True);results.append(detail)
(W/('audit-'+('-'.join(names))+'.json')).write_text(json.dumps(results,indent=2)+'\n')
assert all(d['passAll'] for d in results),'Audit failures; inspect per-crew JSON'

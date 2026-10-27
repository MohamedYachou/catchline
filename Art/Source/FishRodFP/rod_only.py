"""FISH-ARMS-2 STEP0: delete entire v1 sleeve/glove islands, preserve everything else.
Run Windows Blender. Existing source/FBX/atlas remain byte-identical.
"""
import bpy,bmesh,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/FishRodFP';D=O/'rod-only';D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
protected={p.name:sha(p) for p in O.iterdir() if p.is_file() and p.suffix in ('.blend','.fbx','.png','.json','.md') and not p.name.startswith('FishRodFP_RodOnly')}
M=json.loads((O/'build-manifest.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(O/'FishRodFP.blend'));bpy.context.preferences.filepaths.save_version=0
sc=bpy.context.scene;rig=bpy.data.objects['FishRodFP_Rig'];mesh=bpy.data.objects['FishRodFP_Mesh']
handgroups={g.index for g in mesh.vertex_groups if g.name in ('GripHand.L','ReelHand.R')}
assert len(handgroups)==2
adj=[[] for v in mesh.data.vertices]
for e in mesh.data.edges:
 a,b=e.vertices;adj[a].append(b);adj[b].append(a)
seen=set();remove=set();components=[]
for i in range(len(adj)):
 if i in seen:continue
 stack=[i];seen.add(i);part=[]
 while stack:
  j=stack.pop();part.append(j)
  for k in adj[j]:
   if k not in seen:seen.add(k);stack.append(k)
 if any(g.group in handgroups and g.weight>1e-7 for j in part for g in mesh.data.vertices[j].groups):remove.update(part);components.append(len(part))
assert remove and len(remove)<len(adj)
original=mesh.copy();original.data=mesh.data.copy();sc.collection.objects.link(original);original.name='AUDIT_V1_ONLY';original.hide_render=True
attr=mesh.data.attributes.new('v1_index','INT','POINT')
for i,x in enumerate(attr.data):x.value=i
bm=bmesh.new();bm.from_mesh(mesh.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(remove)],context='VERTS');bm.to_mesh(mesh.data);bm.free();mesh.data.update()
kept=[x.value for x in mesh.data.attributes['v1_index'].data]
assert len(kept)+len(remove)==len(adj)
assert all(not any(g.group in handgroups and g.weight>1e-7 for g in v.groups) for v in mesh.data.vertices)
mesh.data.calc_loop_triangles();tri=len(mesh.data.loop_triangles)
# Exact retained geometry, material, UV and normalized weights.
for i,k in enumerate(kept):
 assert (mesh.data.vertices[i].co-original.data.vertices[k].co).length<1e-9
 assert [(g.group,g.weight) for g in mesh.data.vertices[i].groups]==[(g.group,g.weight) for g in original.data.vertices[k].groups]
assert list(mesh.data.materials)==list(original.data.materials)
def verts(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();p=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear();return p
def sample(a,f,check=False):
 rig.animation_data.action=a;sc.frame_set(f);bpy.context.view_layer.update();vs=verts(mesh)
 if check:
  full=verts(original);assert max((v-full[k]).length for v,k in zip(vs,kept))<1e-7
 return {'heads':{p.name:rig.matrix_world@p.head for p in rig.pose.bones},'vertices':vs}
samples={}
for n,c in M['clips'].items():
 for f in range(c['frames'][1]+1):samples[n,f]=sample(bpy.data.actions[n],f,True)
rest={b.name:{'parent':b.parent.name if b.parent else None,'head':list(b.head_local),'tail':list(b.tail_local)} for b in rig.data.bones}
bpy.data.objects.remove(original,do_unlink=True)
rig.animation_data.action=bpy.data.actions['Idle'];sc.frame_set(0)
bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=rig
fbx=O/'FishRodFP_RodOnly.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,path_mode='RELATIVE',use_custom_props=True,mesh_smooth_type='FACE')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'FishRodFP_RodOnly.blend'))
# Actual exported data, not an export-operator success receipt.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=True)
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(rigs)==len(meshes)==1 and len(bpy.context.scene.objects)==2
rig=rigs[0];mesh=meshes[0];sc=bpy.context.scene
assert {b.name:b.parent.name if b.parent else None for b in rig.data.bones}=={n:b['parent'] for n,b in rest.items()}
mesh.data.calc_loop_triangles();assert len(mesh.data.loop_triangles)==tri
assert len(mesh.data.vertices)==len(kept)
assert len(mesh.data.materials)==1 and mesh.data.uv_layers.active
images=[n.image for n in mesh.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE'];assert len(images)==1
assert Path(bpy.path.abspath(images[0].filepath)).resolve()==(O/'FishRodFP_Atlas.png').resolve()
actions={a.name.split('|')[-1]:a for a in bpy.data.actions};assert set(actions)==set(M['clips'])
maxbone=maxvert=0
for (n,f),expected in samples.items():
 a=actions[n];start=round(a.frame_range[0]);assert abs(a.frame_range[1]-start-M['clips'][n]['frames'][1])<.001
 actual=sample(a,start+f);be=max((expected['heads'][k]-actual['heads'][k]).length for k in expected['heads']);ve=max((a-b).length for a,b in zip(expected['vertices'],actual['vertices']))
 maxbone=max(maxbone,be);maxvert=max(maxvert,ve);assert be<.0001 and ve<.0002,(n,f,be,ve)
for n,h in protected.items():assert sha(O/n)==h,('changed original',n)
receipt={'status':'PASS','task':'FISH-ARMS-2 STEP0','triangles':tri,'original_triangles':M['triangles'],'removed_triangles':M['triangles']-tri,'retained_vertices':len(kept),'removed_vertices':len(remove),'removed_sleeve_glove_components':len(components),'removal_method':'Remove complete connected mesh islands containing any positive GripHand.L/ReelHand.R skin weight; no retained vertex, material, UV, weight or rig edit.','bones':rest,'actions':list(M['clips']),'fps':sc.render.fps,'source_and_actual_fbx_samples':len(samples),'max_bone_error_m':maxbone,'max_vertex_error_m':maxvert,'retained_v1_deformation_identity':True,'stage_excluded':True,'atlas_resolves':True,'original_hashes_unchanged':protected,'delivered_sha256':{p.name:sha(p) for p in [fbx,O/'FishRodFP_RodOnly.blend',O/'FishRodFP_Atlas.png']}}
(D/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print('ROD ONLY PASS',json.dumps({k:receipt[k] for k in ['triangles','removed_triangles','source_and_actual_fbx_samples','max_bone_error_m','max_vertex_error_m']}))

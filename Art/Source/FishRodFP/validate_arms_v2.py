"""Actual FBX roundtrip across every baked frame, shoulder/hand/loop invariants."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/FishRodFP';V=O/'arms-v2';M=json.loads((V/'build-manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(O/'FishRodFP_ArmsV2.blend'))
sc=bpy.context.scene;rig=bpy.data.objects['FishRodFP_ArmsV2_Rig'];body=bpy.data.objects['FishRodFP_ArmsV2_Mesh']
hierarchy={b.name:b.parent.name if b.parent else None for b in rig.data.bones}
def vertices():
 e=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();p=[e.matrix_world@v.co for v in me.vertices];e.to_mesh_clear();return p
def sample(action,frame):
 rig.animation_data.action=action;sc.frame_set(frame);bpy.context.view_layer.update()
 return {'heads':{p.name:rig.matrix_world@p.head for p in rig.pose.bones},'tails':{p.name:rig.matrix_world@p.tail for p in rig.pose.bones},'vertices':vertices()}
for v in body.data.vertices:
 assert 0<len(v.groups)<=4
 assert abs(sum(g.weight for g in v.groups)-1)<1e-5
 assert all(math.isfinite(x) for x in v.co)
assert len(body.data.materials)==1 and body.data.uv_layers.active
expected={};max_wrist=max_shoulder=0;loops={}
for n,c in M['clips'].items():
 for f in range(c['frames'][1]+1):
  s=sample(bpy.data.actions[n],f);expected[n,f]=s
  for side in ['R','L']:
   max_wrist=max(max_wrist,(s['tails']['Forearm.'+side]-s['heads']['Hand.'+side]).length,(s['heads']['WristTarget.'+side]-s['heads']['Hand.'+side]).length)
   max_shoulder=max(max_shoulder,(s['heads']['UpperArm.'+side]-Vector(M['shoulders_source'][side])).length)
 if c['loop']:
  a=expected[n,0]['vertices'];b=expected[n,c['frames'][1]]['vertices'];err=max((x-y).length for x,y in zip(a,b));assert err<.0001,(n,err);loops[n]=err
assert max_wrist<.00001 and max_shoulder<.00001,(max_wrist,max_shoulder)
fbx=O/'FishRodFP_ArmsV2.fbx'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=True)
sc=bpy.context.scene;rigs=[o for o in sc.objects if o.type=='ARMATURE'];meshes=[o for o in sc.objects if o.type=='MESH'];assert len(rigs)==len(meshes)==1 and len(sc.objects)==2
rig=rigs[0];body=meshes[0];assert {b.name:b.parent.name if b.parent else None for b in rig.data.bones}==hierarchy
body.data.calc_loop_triangles();assert len(body.data.loop_triangles)==M['triangles']<8000
assert len(body.data.materials)==1 and body.data.uv_layers.active
images=[n.image for n in body.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE'];assert len(images)==1 and Path(bpy.path.abspath(images[0].filepath)).resolve()==(O/'FishRodFP_Atlas.png').resolve()
actions={a.name.split('|')[-1]:a for a in bpy.data.actions};assert set(actions)==set(M['clips'])
maxbone=maxvert=0
for (n,f),e in expected.items():
 a=actions[n];start=round(a.frame_range[0]);assert round(a.frame_range[1])-start==M['clips'][n]['frames'][1]
 s=sample(a,start+f);be=max((s['heads'][k]-e['heads'][k]).length for k in hierarchy);ve=max((x-y).length for x,y in zip(s['vertices'],e['vertices']));maxbone=max(maxbone,be);maxvert=max(maxvert,ve);assert be<.0001 and ve<.0002,(n,f,be,ve)
for n,h in M['protected_original_hashes'].items():
 if not n.startswith('FishRodFP_ArmsV2'):assert sha(O/n)==h,n
r={'status':'PASS','triangles':M['triangles'],'bones':len(hierarchy),'actions':list(actions),'fps':sc.render.fps,'all_frame_samples':len(expected),'max_actual_fbx_bone_error_m':maxbone,'max_actual_fbx_vertex_error_m':maxvert,'max_source_hand_wrist_error_m':max_wrist,'max_fixed_shoulder_error_m':max_shoulder,'loop_vertex_errors_m':loops,'one_material_atlas_and_normalized_max4_weights':True,'stage_excluded':True,'original_and_rod_only_unchanged':True,'hashes':{p.name:sha(p) for p in [fbx,O/'FishRodFP_ArmsV2.blend',O/'FishRodFP_Atlas.png']},'limits':'Analytic IK/FBX parity do not prove absence of visible mesh penetration. Final pose and grip renders require separate review. No Unity/native acceptance.'}
(V/'validation.json').write_text(json.dumps(r,indent=2)+'\n');print('ARMS V2 FBX PASS',json.dumps(r))

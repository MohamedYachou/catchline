import bpy,json,ast,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[3]
src=(O/'validate-extra.py').read_text();tree=ast.parse(src)
for node in tree.body:
 if isinstance(node,ast.FunctionDef):exec(compile(ast.Module(body=[node],type_ignores=[]),str(O/'validate-extra.py'),'exec'))
def sample(rig,a):
 bind(rig,a.name.split('|')[-1]);rows=[]
 for t in range(5):
  bpy.context.scene.frame_set(int(a.frame_range[0]+(a.frame_range[1]-a.frame_range[0])*t/4));bpy.context.view_layer.update();rows.append({b.name:[list(r) for r in b.matrix] for b in rig.pose.bones})
 return rows
init();bpy.ops.import_scene.fbx(filepath=str(R/'Assets/Art/Models/Crew/CrewRig.fbx'));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');reference={a.name.split('|')[-1]:{'range':list(a.frame_range),'poses':sample(rig,a)} for a in bpy.data.actions}
out={'pass':True,'sample_count_per_clip':5,'guests':[]}
for row in json.loads((O/'validation-extra.json').read_text())['guests']:
 init();bpy.ops.import_scene.fbx(filepath=str(O/(row['name']+'.fbx')));rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE');clips={a.name.split('|')[-1]:a for a in bpy.data.actions};deltas={}
 for n,r in reference.items():
  assert list(clips[n].frame_range)==r['range'];mm=sample(rig,clips[n]);d=max(abs(mm[f][b][i][j]-r['poses'][f][b][i][j]) for f in range(5) for b in r['poses'][0] for i in range(4) for j in range(4));assert d<1e-4,(row['name'],n,d);deltas[n]=d
 out['guests'].append({'name':row['name'],'fbx_sha256':sha(O/(row['name']+'.fbx')),'all_original_clip_sample_deltas':deltas,'ranges_preserved':True})
(O/'audit-extra-clips.json').write_text(json.dumps(out,indent=2));print('ALL ORIGINAL CLIPS PASS',flush=True)

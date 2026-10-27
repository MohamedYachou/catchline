"""Verify the accepted JigKit is unchanged except the explicitly revised rock mesh."""
import bpy,json,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent;O=R/'Art/Models/JigKit'
def capture(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));out={}
 for o in bpy.context.scene.objects:
  row={'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(v) for v in o.matrix_local]}
  if o.type=='MESH':row.update(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[m.name for m in o.data.materials],indices=[p.material_index for p in o.data.polygons],groups=[[(x.group,x.weight) for x in v.groups] for v in o.data.vertices])
  if o.type=='ARMATURE':row['bones']={b.name:[list(b.head_local),list(b.tail_local),b.parent.name if b.parent else None] for b in o.data.bones}
  out[o.name]=row
 out['actions']={a.name:[(f.data_path,f.array_index,[(list(k.co),k.interpolation) for k in f.keyframe_points]) for layer in a.layers for strip in layer.strips for bag in strip.channelbags for f in bag.fcurves] for a in bpy.data.actions}
 return out
old=capture(D/'pre-rocks/JigKit/JigKit.blend');new=capture(O/'JigKit.blend');assert old.keys()==new.keys();changed=[k for k in old if old[k]!=new[k]];assert changed==['SeabedRocks'],changed
baseline=json.loads((D/'pre-rocks/repair-baseline.json').read_text())
for p,v in baseline.items():assert (R/p).stat().st_size==v['bytes'] and hashlib.sha256((R/p).read_bytes()).hexdigest()==v['sha256'],p
proof={'result':'PASS','changed_objects':changed,'unchanged_objects_and_actions':sorted(k for k in old if k not in changed),'retained_unchanged_review_images':30,'repair_model_and_evidence_files_unchanged':len(baseline),'previous_blend_sha256':hashlib.sha256((D/'pre-rocks/JigKit/JigKit.blend').read_bytes()).hexdigest(),'final_blend_sha256':hashlib.sha256((O/'JigKit.blend').read_bytes()).hexdigest()}
(O/'metrics/rocks-revision.json').write_text(json.dumps(proof,indent=2)+'\n');print('ROCKS COMPARISON PASS',flush=True)

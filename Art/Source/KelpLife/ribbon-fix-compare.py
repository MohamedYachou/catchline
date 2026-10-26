import bpy,json,sys,hashlib
from pathlib import Path
S=Path(__file__).resolve().parent;R=S.parents[2];O=R/'Art/Models/KelpLife'
def animal(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));res={}
 for n in ('AdultA','AdultB','Pup'):
  o=bpy.data.objects[n];res[n]={'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'materials':[m.name for m in o.data.materials],'material_indices':[p.material_index for p in o.data.polygons]}
 return res
def digest(d):return {n:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest() for n,v in d.items()}
proof=O/'metrics/ribbon-fix-otters.json'
backup=S/'ribbon-fix-backup/OtterRaft.blend'
old=digest(animal(backup)) if backup.exists() else json.loads(proof.read_text())['baseline_sha256']
new=digest(animal(O/'OtterRaft.blend'));assert old==new
row={'result':'PASS','unchanged_animals':list(old),'exact_local_vertices_faces_materials':True,'baseline_sha256':old,'current_sha256':new}
(O/'metrics/ribbon-fix-otters.json').write_text(json.dumps(row,indent=2)+'\n');print('KELP RIBBON OTTERS PASS')

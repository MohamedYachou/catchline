"""One-time correction of previously exported draft assemblies, preserving their components."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Matrix
O=Path(__file__).resolve().parent
sys.path.insert(0,str(O));from build import export,bounds
d=json.loads((O/'manifest.json').read_text())
for rec in d['items']:
 p=O/(rec['name']+'.blend');bpy.ops.wm.open_mainfile(filepath=str(p))
 ob=bpy.data.objects[rec['name']]
 ob.data.transform(Matrix.Rotation(math.pi,4,'Z'))
 lo,hi=bounds([ob]);rec['bounds_blender']=[list(lo),list(hi)]
 rec['assembly_rotation_baked_z_deg']=180
 export(ob,rec['name'].removeprefix('Restaurant_'))
 bpy.ops.wm.save_as_mainfile(filepath=str(p))
 rec['fbx_sha256']=hashlib.sha256((O/(rec['name']+'.fbx')).read_bytes()).hexdigest()
 print('FACING_FIXED',rec['name'],flush=True)
d['coordinate_contract']='Blender Z-up, front -Y matches Stage1V2; assembly rotation180 baked; Y-up FBX identity local transform; Unity importer handedness checked by lead.'
(O/'manifest.json').write_text(json.dumps(d,indent=2))

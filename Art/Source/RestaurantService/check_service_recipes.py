import sys,bpy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import build_service as b
for key in b.SERVICE:
 bpy.ops.wm.read_factory_settings(use_empty=True);b.PARTS=[];b.MAT=b.atlas_material();b.make_service(key)
 ob,rec=b.join_asset('Restaurant_'+key);assert rec['tris']<3000,rec
 print('RECIPE_PASS',key,rec['tris'],rec['size_xyz_unity_m'],flush=True)

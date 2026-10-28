import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import build_service as b
bpy.ops.wm.read_factory_settings(use_empty=True);b.PARTS=[];b.MAT=b.atlas_material();b.make_service('Gull_Flap')
for ob in b.PARTS:
 if ob.name.startswith(('Raised grey wing','Black primary fan','Wing underside','White tail fan','Tail black tips')):
  z=sum(p.normal.z*p.area for p in ob.data.polygons);expected=-1 if ob.name.startswith('Wing underside') else 1
  assert z*expected>0,(ob.name,z)
  print('WINDING_PASS',ob.name,z,flush=True)

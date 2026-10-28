import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import build_service as b
for key in b.DISHES+['FishCrateOpen','Gull_Stand','Gull_Flap','Spill']:
 bpy.ops.wm.read_factory_settings(use_empty=True);b.PARTS=[];b.MAT=b.atlas_material();(b.make_dish if key in b.DISHES else b.make_service)(key)
 for ob in b.PARTS:
  if ob.name.startswith(('Lemon flesh','Tail fin','Label tail','Spilled drink puddle','Raised grey wing','Black primary fan','Wing underside','White tail fan','Tail black tips')):
   normal=sum((p.normal*p.area for p in ob.data.polygons),__import__('mathutils').Vector())
   expected= -normal.y if ob.name.startswith('Label tail') else (-normal.z if ob.name.startswith('Wing underside') else normal.z)
   print('SHEET',key,ob.name,list(normal),'PASS' if expected>0 else 'FAIL',flush=True)
   assert expected>0,(key,ob.name,list(normal))

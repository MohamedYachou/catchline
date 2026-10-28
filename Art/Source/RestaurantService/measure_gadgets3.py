import bpy,sys
from pathlib import Path
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O))
import build_props3 as p
from mathutils import Vector
for key in ['PassCounter','ReceptionDesk']:
 bpy.ops.wm.read_factory_settings(use_empty=True);p.b.MAT=p.material();obs=p.c.load_station(key);bpy.context.view_layer.update();vs=[o.matrix_world@v.co for o in obs if o.type=='MESH' for v in o.data.vertices]
 print('STATION',key,'bounds',[[round(fun(v[i] for v in vs),5) for i in range(3)] for fun in [min,max]],flush=True)
 heights={}
 for o in obs:
  if o.type!='MESH':continue
  for f in o.data.polygons:
   if f.normal.z>.98:heights[round(f.center.z,4)]=heights.get(round(f.center.z,4),0)+f.area
 deps=bpy.context.evaluated_depsgraph_get()
 for x,y in [(0,0),(.15,-.10),(-.15,0)]:
  hit,loc,n,idx,obj,m=bpy.context.scene.ray_cast(deps,Vector((x,y,3)),Vector((0,0,-1)))
  print('CONTACT',key,x,y,hit,tuple(round(v,6) for v in loc),obj.name if obj else None,flush=True)
 print('FLAT_TOPS',sorted(heights.items(),key=lambda x:-x[1])[:12],flush=True)

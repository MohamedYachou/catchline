"""Read-only ray measurements for table-payment and harbour evidence surfaces."""
import bpy,sys,json,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[2]
spec=importlib.util.spec_from_file_location('service_base',O/'build_service.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
bpy.ops.wm.read_factory_settings(use_empty=True)
room=b.load_fbx(R/'Assets/Resources/Restaurant/Stage1V4.fbx');bpy.context.view_layer.update()
out=[]
for name,x,y in [('EXPORT_DiningFour',1.35,.28),('EXPORT_DiningFour',1.35,.48)]:
 ob=next(o for o in room if o.name==name);inv=ob.matrix_world.inverted();hit,co,n,fi=ob.ray_cast(inv@Vector((x,y,5)),inv.to_3x3()@Vector((0,0,-1)));assert hit
 out.append(dict(object=name,position_blender_m=list(ob.matrix_world@co),normal_blender=list(ob.matrix_world.to_3x3()@n),triangle=fi))
for ob in room:
 if ob.type!='MESH':continue
 inv=ob.matrix_world.inverted();hit,co,n,fi=ob.ray_cast(inv@Vector((1.35,.28,5)),inv.to_3x3()@Vector((0,0,-1)))
 if not hit:continue
 world=ob.matrix_world@co
 if .7<world.z<1.5:out.append(dict(object=ob.name,position_blender_m=list(world),normal_blender=list(ob.matrix_world.to_3x3()@n),triangle=fi))
(O/'service-contact-measurements.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
bpy.ops.wm.open_mainfile(filepath='C:/Users/momoy/Projects/Catchline/Art/Models/CrewV2/Captain/Captain.blend')
ob=bpy.data.objects['Captain_Hat']
polys=[tuple(p.vertices) for p in ob.data.polygons if ob.data.materials[p.material_index].name=='M_RailIvory']
tree=BVHTree.FromPolygons([v.co for v in ob.data.vertices],polys)
out=[]
for x in (-.025,0,.025):
    for z in (.948,.973,.998):
        hit=tree.ray_cast(Vector((x,-1,z)),Vector((0,1,0)))
        out.append({'x':x,'z':z,'crown_front_y':hit[0].y if hit[0] else None})
print(json.dumps(out,indent=2),flush=True)

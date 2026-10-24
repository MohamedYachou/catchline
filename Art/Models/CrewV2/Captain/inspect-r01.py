import bpy,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
root=Path('C:/Users/momoy/Projects/Catchline')
bpy.ops.wm.open_mainfile(filepath=str(root/'Art/Models/CrewV2/Captain/Captain.blend'))
arm=bpy.data.objects['CrewRig'];ob=bpy.data.objects['Captain_MaleBody']
bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons])
out=[]
for x in (.115,.15,.19):
    for y in (-.032,0,.032):
        hit=tree.ray_cast(Vector((x,y,.7)),Vector((0,0,-1)))
        p=arm.pose.bones['LeftShoulder'].matrix@arm.data.bones['LeftShoulder'].matrix_local.inverted()@Vector((x,y,.554-(x-.115)/.075*.008))
        out.append({'x':x,'y':y,'surface_z':hit[0].z if hit[0] else None,'old_board_world':list(p)})
print(json.dumps(out,indent=2),flush=True)

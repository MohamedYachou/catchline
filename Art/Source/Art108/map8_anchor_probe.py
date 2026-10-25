import bpy, json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[3]
bpy.ops.wm.open_mainfile(filepath=str(root/'Art/Models/Maps/GullLighthouseRock/GullLighthouseRockSeaV2.blend'))
o=bpy.data.objects['Terrain_lighthouse-stack']
vs=[o.matrix_world@v.co for v in o.data.vertices]
tree=BVHTree.FromPolygons(vs,[list(p.vertices) for p in o.data.polygons])
for x in [-16,-12,-6,0,8,12]:
    out=[]
    for z in [-7,-5,-3,-1,1,3,5]:
        hit=tree.ray_cast(Vector((x,-z,50)),Vector((0,0,-1)))
        out.append((z,round(hit[0].z,2) if hit[0] else None))
    print('STACK TOP',x,out)

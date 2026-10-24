import bpy
from pathlib import Path
from collections import Counter
import json

root = Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'Mira.blend'))
ob = bpy.data.objects['Mira_OfficerCap']
data = ob.data
data.calc_loop_triangles()
def tris(ob):
    ob.data.calc_loop_triangles()
    return [tuple(sorted(tuple(round(x, 6) for x in ob.matrix_world @ ob.data.vertices[i].co)
                         for i in t.vertices)) for t in ob.data.loop_triangles]
a = Counter(tris(ob))
print('BEFORE',len(data.polygons),len(data.vertices), flush=True)
print('VALIDATE CHANGED', data.validate(verbose=True, clean_customdata=False), flush=True)
print('AFTER',len(data.polygons),len(data.vertices), flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=str(root/'Mira.fbx'))
ob = bpy.data.objects['Mira_OfficerCap']
b = Counter(tris(ob))
print('LOST',json.dumps(list((a-b).elements())), flush=True)
print('ADDED',json.dumps(list((b-a).elements())[:20]), flush=True)

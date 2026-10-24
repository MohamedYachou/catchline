import bpy, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
out={}
for name in ['Rowboat','Skiff','CompactFisherV1','PrepFisherV1','Tier5DeepLines103']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/Art/Models/Boats'/f'{name}.fbx'))
    meshes=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH': continue
        pts=[o.matrix_world @ Vector(v) for v in o.bound_box]
        meshes.append({'name':o.name,'min':[round(min(p[i] for p in pts),3) for i in range(3)],'max':[round(max(p[i] for p in pts),3) for i in range(3)]})
    out[name]=meshes
(ROOT/'Art/Source/Art108/hull-baseline.json').write_text(json.dumps(out,indent=2))
print('HULL INSPECTION COMPLETE')

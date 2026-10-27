"""Read-only baseline of existing kit and hull FBXs, no runtime writes."""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3]
O=R/'Art/Models/GullHarbour/HarbourV2'
O.mkdir(parents=True,exist_ok=True)
result={}
for name,path in [('Quay4m',R/'Art/Models/GullHarbour/Harbour/Quay4m.blend'),
                  ('HouseA',R/'Art/Models/GullHarbour/Harbour/HouseA.blend')]+[
    (n,R/'Assets/Art/Models/Boats'/f'{n}.fbx') for n in ['Rowboat','Skiff','CompactFisherV1','PrepFisherV1','Tier5DeepLines103']]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if path.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(path))
    else:bpy.ops.import_scene.fbx(filepath=str(path))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Preview')]
    bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    result[name]={'path':str(path.relative_to(R)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)],
        'parts':[{'name':o.name,'parent':o.parent.name if o.parent else None,'materials':[m.name for m in o.data.materials]} for o in meshes]}
    print('BASELINE',name,result[name]['min'],result[name]['max'],flush=True)
(O/'baseline.json').write_text(json.dumps(result,indent=2))

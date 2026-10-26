import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(R/'Art/Models/BoatsV2/CompactFisherV1/CompactFisherV1.fbx'))
d={}
for n in ['PlankDeck','Hull']:
 o=bpy.data.objects[n];d[n]=[list(o.matrix_world@v.co) for v in o.data.vertices]
(R/'Art/Source/BoatsV2/diagnose2.json').write_text(json.dumps(d))

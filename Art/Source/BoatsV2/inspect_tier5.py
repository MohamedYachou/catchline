import bpy,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3]
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(R/'Assets/Art/Models/Boats/Tier5DeepLines103.fbx'));bpy.context.view_layer.update()
d={}
for o in bpy.context.scene.objects:
 vs=[list(o.matrix_world@v.co) for v in o.data.vertices] if o.type=='MESH' else []
 d[o.name]={'parent':o.parent.name if o.parent else None,'location':list(o.location),'scale':list(o.scale),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons) if vs else 0,'bounds':[[min(p[i] for p in vs) for i in range(3)],[max(p[i] for p in vs) for i in range(3)]] if vs else [],'materials':[m.name for m in o.data.materials] if vs else [],'vertices':vs if o.name in ['Hull','GunwaleHardware','HullPaintBand'] else []}
(R/'Art/Source/BoatsV2/tier5-inventory.json').write_text(json.dumps(d,indent=2));print('INVENTORY',len(d))

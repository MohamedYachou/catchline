"""Read-only reference inventory. Output is not asset delivery evidence."""
from pathlib import Path
import bpy, json
R=Path(__file__).resolve().parents[3]
for rel in ['Art/Models/GullHarbour/Fishing/GillNetFloatLine.blend',
            'Art/Models/GullHarbour/HarbourV2/CompactFisherV1_VariantRed.blend',
            'Art/Models/Fish043/Mackerel/Mackerel.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(R/rel))
    print('REFERENCE',rel,json.dumps({
        'objects':[{ 'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,
                     'dimensions':list(o.dimensions)} for o in bpy.context.scene.objects
                    if o.type in ('MESH','EMPTY') and not o.name.startswith('Preview')],
        'materials':{m.name:list(m.diffuse_color) for m in bpy.data.materials}}),flush=True)

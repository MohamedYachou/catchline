import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'Stage4Seafood.blend'))
rows={o.name:[{'name':a.name,'domain':a.domain,'type':a.data_type} for a in o.data.color_attributes] for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')}
(O/'stages-look2-color-layers.json').write_text(json.dumps(rows,indent=2))
print('NON LocalAO',[(n,a) for n,a in rows.items() if not any(x['name']=='LocalAO' for x in a)],flush=True)

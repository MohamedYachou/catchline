import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
rows={}
for ext in ('blend','fbx'):
 if ext=='blend':bpy.ops.wm.open_mainfile(filepath=str(B.O/'ChannelMarkers.blend'))
 else:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(B.O/'ChannelMarkers.fbx'))
 bpy.context.view_layer.update()
 rows[ext]={o.name:{'location':list(o.location),'rotation':list(o.rotation_euler),'matrix':[list(x) for x in o.matrix_world],'firstverts':[list(o.matrix_world@v.co) for v in o.data.vertices[:12]] if o.type=='MESH' else []} for o in bpy.context.scene.objects}
(B.O/'metrics/marker-diagnostic.json').write_text(json.dumps(rows,indent=2))

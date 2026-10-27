"""Read-only transform diagnostic for canonical / saved / exported boats."""
import bpy,sys,json,importlib.util
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/GullHarbour/HarbourV2'
spec=importlib.util.spec_from_file_location('audit',Path(__file__).with_name('audit.py'))
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
name=sys.argv[-1]
for path in [O/(name+'.blend'),O/(name+'.fbx'),R/'Assets/Art/Models/Boats/CompactFisherV1.fbx']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 if path.suffix=='.blend':bpy.ops.wm.open_mainfile(filepath=str(path))
 else:bpy.ops.import_scene.fbx(filepath=str(path))
 print('PROBE',path.name,json.dumps(A.snapshot()),flush=True)
 for o in bpy.context.scene.objects:
  if o.name.startswith('Preview'):continue
  if o.parent is None or o.type=='EMPTY':print('TRANSFORM',o.name,'parent',o.parent.name if o.parent else None,'local',[list(r) for r in o.matrix_local],flush=True)

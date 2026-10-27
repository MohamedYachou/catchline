import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;P=O/'backwall-renders';P.mkdir(exist_ok=True)
for variant in ['before','after']:
 if variant=='before' and all((P/('before-'+r['file'])).exists() for r in json.loads((O/'final-cameras.json').read_text())):continue
 bpy.ops.wm.open_mainfile(filepath=str(O/'LookProof.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
 if variant=='after':
  names=[c['node'].removeprefix('EXPORT_') for c in json.loads((O/'backwall-changes.json').read_text())['changes']]
  originals={n:bpy.data.objects[n] for n in names}
  with bpy.data.libraries.load(str(O/'Stage1V4.blend'),link=False) as (src,dst):dst.objects=list(names)
  for source in dst.objects:
   assert source is not None
   key=next(n for n in names if source.name==n or source.name.startswith(n+'.'))
   originals[key].data=source.data
 sc.cycles.device='GPU';sc.cycles.samples=24;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 for row in json.loads((O/'final-cameras.json').read_text()):
  sc.camera.location=row['position_blender_m'];sc.camera.rotation_euler=row['rotation_blender_rad'];sc.camera.data.lens=row['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.resolution_percentage=100;sc.render.filepath=str(P/(variant+'-'+row['file']));bpy.ops.render.render(write_still=True)
print('BACKWALL PROOF PASS',flush=True)

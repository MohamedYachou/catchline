import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;P=O/'room-look-renders';P.mkdir(exist_ok=True)
for variant in ['before','after']:
 bpy.ops.wm.open_mainfile(filepath=str(O/'LookProof.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
 source=O.parent/'_pickup-backup-Stage1V4/Stage1V4.blend' if variant=='before' else O/'Stage1V4.blend'
 oldnames={r['name'] for r in json.loads((O/'build-metrics.json').read_text())['production_meshes']}
 for ob in list(sc.objects):
  if ob.name in oldnames or ob.type=='LIGHT':bpy.data.objects.remove(ob,do_unlink=True)
 with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=[n for n in src.objects if n in oldnames or n.startswith(('Dusk','WallLantern','WindowWash','KitchenWarm','DiningWarm','TerraceWarm','JettyLampPool','V4_Practical','Look3_TablePool'))];dst.worlds=src.worlds
 for ob in dst.objects:
  if ob:sc.collection.objects.link(ob)
 if dst.worlds:sc.world=dst.worlds[0]
 sc.view_settings.exposure=-.4 if variant=='after' else -.25
 sc.cycles.device='GPU';sc.cycles.samples=24;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 for row in json.loads((O/'final-cameras.json').read_text()):
  sc.camera.location=row['position_blender_m'];sc.camera.rotation_euler=row['rotation_blender_rad'];sc.camera.data.lens=row['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.resolution_percentage=100;sc.render.filepath=str(P/(variant+'-'+row['file']));bpy.ops.render.render(write_still=True)
 if variant=='after':bpy.ops.wm.save_as_mainfile(filepath=str(O/'RoomLook3-Check.blend'))
print('ROOM LOOK3 PROOF PASS')

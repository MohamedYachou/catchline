import bpy,json,math
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'LookProof.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for device in prefs.devices:device.use=device.type=='OPTIX'
for name,loc,yaw in [('Diner_E',(.99,.80,.04),0),('Diner_F',(1.71,.16,.04),180)]:
 o=bpy.data.objects[name+'_placement'];o.location=loc;o.rotation_euler.z=math.radians(yaw)
rows=json.loads((O/'characters.json').read_text())
for row in rows:
 if row['name']=='Diner_E':row['position_blender_m']=[.99,.80,.04];row['yaw_deg']=0
 if row['name']=='Diner_F':row['position_blender_m']=[1.71,.16,.04];row['yaw_deg']=180
(O/'characters.json').write_text(json.dumps(rows,indent=2))
P=O/'renders'
source=(O/'review.py').read_text();exec(source[source.index('sc.frame_set(13)'):source.index("(O/'characters.json').write_text")])
(O/'final-cameras.json').write_text(json.dumps(camrows,indent=2));print('SEATING CORRECTION PASS',flush=True)

import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;P=O/'renders';P.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'RestaurantUpgrades.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;rows=json.loads((O/'manifest.json').read_text())['assets'];groups={r['name']:[bpy.data.objects[n] for n in r['export_meshes']] for r in rows}
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.world=bpy.data.worlds.new('ReviewNight');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.16,.27,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.45
for loc,power,size,col in [((-3,-4,7),750,5,(1,.78,.54)),((4,0,5),550,4,(.56,.73,1)),((0,4,6),650,3,(1,.79,.52))]:
 data=bpy.data.lights.new('REVIEW_Area','AREA');data.energy=power;data.color=col;data.shape='DISK';data.size=size;ob=bpy.data.objects.new('REVIEW_Area',data);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('REVIEW_V4Camera',bpy.data.cameras.new('REVIEW_V4Camera'));sc.collection.objects.link(cam);sc.camera=cam;camera_rows=json.loads((O.parent/'Stage1V4/final-cameras.json').read_text());cam.rotation_euler=camera_rows[0]['rotation_blender_rad'];cam.data.lens=58;sc.render.resolution_x=640;sc.render.resolution_y=640;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.view_settings.view_transform='AgX'
for row in rows:
 for name,obs in groups.items():
  for ob in obs:ob.hide_render=name!=row['name']
 lo,hi=row['bounds_blender_m'];target=Vector((0,0,(hi[2]+lo[2])/2));dist=max(hi[k]-lo[k] for k in range(3))*2.7;cam.location=target+cam.rotation_euler.to_matrix()@Vector((0,0,dist));sc.render.filepath=str(P/(row['name']+'.png'));bpy.ops.render.render(write_still=True)
# Unscaled lineup under exact saved game camera; tiers in rows, wall props at rear.
locations={}
for t in [1,2,3]:
 y=1.65-(t-1)*1.55
 locations[f'Dining2_Tier{t}']=(-2.5,y,0);locations[f'Dining4_Tier{t}']=(0,y,0);locations[f'Chair_Tier{t}']=(2,y,0)
locations.update({'WallNetFloats':(-2.8,2.6,.95),'WallFishTrophy':(-1.3,2.6,1.1),'WallMenuBoard':(0,2.6,1),'StringLights':(1.65,2.6,1.35),'PlantPot_Herbs':(3,1,0),'PlantPot_Flowering':(3,-.3,0),'TableCandle':(3,-1.55,.72)})
for name,obs in groups.items():
 for ob in obs:ob.hide_render=False;ob.location=locations[name]
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.4,-.06));floor=bpy.context.object;floor.name='REVIEW_ONLY_Floor';floor.dimensions=(8,6,.12);mat=bpy.data.materials.new('REVIEW_ONLY_Floor');mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.16,.20,.23,1);floor.data.materials.append(mat)
# Presentation plinth separates the tiny candle from chairs; never exported.
bpy.ops.mesh.primitive_cube_add(size=1,location=(3,-1.55,.36));plinth=bpy.context.object;plinth.name='REVIEW_ONLY_CandlePlinth';plinth.dimensions=(.25,.25,.72);plinth.data.materials.append(mat)
sc.render.film_transparent=False
for row in camera_rows:
 cam.location=row['position_blender_m'];cam.rotation_euler=row['rotation_blender_rad'];cam.data.lens=row['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.filepath=str(O/('lineup-V4-'+row['file']));bpy.ops.render.render(write_still=True)
(O/'lineup-camera.json').write_text(json.dumps({'cameras':camera_rows,'asset_placements':locations,'note':'Exact V4 cameras; neutral presentation lighting/floor. No scale changes.'},indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'Upgrades-V4-check.blend'));print('UPGRADES REVIEW RENDERS PASS',flush=True)

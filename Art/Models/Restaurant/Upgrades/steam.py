"""Eight coherent rising wisps. Native Blender curves, translucent emission, RGBA film."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;P=O/'Steam';P.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.render.resolution_x=256;sc.render.resolution_y=256;sc.render.resolution_percentage=100;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.view_settings.view_transform='Standard';sc.view_settings.look='None';sc.world=bpy.data.worlds.new('TransparentSteamWorld');sc.world.color=(0,0,0)
cam=bpy.data.objects.new('SteamCamera',bpy.data.cameras.new('SteamCamera'));sc.collection.objects.link(cam);cam.location=(0,-3,.42);cam.rotation_euler=(math.pi/2,0,0);cam.data.type='ORTHO';cam.data.ortho_scale=.96;sc.camera=cam
wisps=[]
for j in range(3):
 mat=bpy.data.materials.new('SteamIvory_'+str(j));mat.use_nodes=True;n=mat.node_tree.nodes;n.clear();l=mat.node_tree.links;out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');tr=n.new('ShaderNodeBsdfTransparent');em=n.new('ShaderNodeEmission');em.inputs[0].default_value=(.91,.96,1,1);em.inputs[1].default_value=1;l.new(tr.outputs[0],mix.inputs[1]);l.new(em.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
 curve=bpy.data.curves.new('SteamWisp'+str(j),'CURVE');curve.dimensions='3D';curve.resolution_u=3;curve.bevel_depth=.018;curve.bevel_resolution=4;s=curve.splines.new('BEZIER');s.bezier_points.add(23);ob=bpy.data.objects.new('SteamWisp'+str(j),curve);sc.collection.objects.link(ob);curve.materials.append(mat);wisps.append((j,ob,s,mix))
for frame in range(8):
 for j,ob,s,mix in wisps:
  # Repeating phases avoid a single obvious puff disappearing at the loop seam.
  phase=(frame/8+j/3)%1;opacity=.13+.12*math.sin(math.pi*phase);mix.inputs[0].default_value=opacity;mix.inputs[0].keyframe_insert('default_value',frame=frame+1)
  for k,p in enumerate(s.bezier_points):
   t=k/23;z=.045+t*.70;theta=t*7.5-frame*math.tau/8+j*2.1;x=(j-1)*.055+(.015+.08*t)*math.sin(theta);y=.015*math.cos(theta)
   p.co=(x,y,z);p.handle_left_type='AUTO';p.handle_right_type='AUTO';p.radius=max(.015,math.sin(math.pi*t)**1.3)*(1-.38*t)*(1+.14*math.sin(theta))
   p.keyframe_insert('co',frame=frame+1);p.keyframe_insert('radius',frame=frame+1)
  ob.location.x=.012*math.sin(frame*math.tau/8+j)
  ob.keyframe_insert('location',frame=frame+1)
 sc.frame_set(frame+1);sc.render.filepath=str(P/f'steam-{frame:02}.png');bpy.ops.render.render(write_still=True)
sc.frame_start=1;sc.frame_end=8
bpy.ops.wm.save_as_mainfile(filepath=str(P/'Steam.blend'));(P/'steam.json').write_text(json.dumps({'frames':8,'frame_px':[256,256],'sheet_px':[2048,256],'layout':'8 columns x1 row, left to right','fps':8,'loop':True,'alpha':'straight RGBA; normal alpha blend recommended','pivot_normalized_bottom_left':[.5,.08],'suggested_world_height_m':.38,'source':'Blender native coherent three curve wisps, translucent ivory/cool-white emission; no stock or generated image'},indent=2));print('STEAM RENDERS PASS',flush=True)

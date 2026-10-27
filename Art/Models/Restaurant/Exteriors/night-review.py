import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'night-renders';P.mkdir(exist_ok=True);M=json.loads((O/'manifest.json').read_text());cameras=[]
for row in M['stages']:
 filename=Path(row['file']).stem;bpy.ops.wm.open_mainfile(filepath=str(O/(filename+'.blend')));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
 sc.render.engine='CYCLES';sc.cycles.device='GPU';sc.cycles.samples=32;sc.cycles.use_denoising=True;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.world=bpy.data.worlds.new('HarbourNight');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.21,.33,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.09
 sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.1
 def light(name,kind,loc,power,color,size):
  d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color
  if kind=='AREA':d.shape='DISK';d.size=size
  elif kind=='POINT':d.shadow_soft_size=size
  ob=bpy.data.objects.new(name,d);sc.collection.objects.link(ob);ob.location=loc
  if kind!='POINT':ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
 light('REVIEW_WarmSky','AREA',(-5,4,11),240,(1,.70,.43),9);light('REVIEW_BlueFill','AREA',(6,-1,8),180,(.30,.55,1),8)
 fp=json.loads((O/row['footprint']).read_text())
 for i,pt in enumerate(fp['lamp_positions_blender_m']):light('REVIEW_Practical'+str(i),'POINT',pt,12,(1,.60,.24),.12)
 # Match harbour quay scale and include accepted 3m HouseA as a scale witness.
 W=fp['tiles'][0]
 with bpy.data.libraries.load(str(R/'Art/Models/GullHarbour/Harbour/HouseA.blend'),link=False) as (a,b):b.objects=[n for n in a.objects if n in {'HouseWalls','HouseRoof','DoorsWindowsTrim'}]
 for ob in b.objects:
  if ob and ob.type=='MESH':sc.collection.objects.link(ob);ob.name='REVIEW_Neighbour_'+ob.name;ob.rotation_euler.z=math.pi;ob.location+=Vector((W/2+2.15,-.15,0))
 def simple(name,col,rough=.8):
  ma=bpy.data.materials.new(name);ma.diffuse_color=(*col,1);ma.use_nodes=True;bs=ma.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough;return ma
 def cube(name,loc,size,ma):
  bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.dimensions=size;ob.data.materials.append(ma);return ob
 quay=simple('REVIEW_QuayStone',(.24,.25,.25));cube('REVIEW_Quay',(1,-1.70,-.22),(W+13,8.8,.40),quay)
 # Water starts beyond quay edge at BlenderY2.7, at -0.35m relative to quay surface.
 sea=simple('REVIEW_HarbourSea',(.012,.1,.15),.64);ns=sea.node_tree.nodes;lk=sea.node_tree.links;bs=ns['Principled BSDF'];geo=ns.new('ShaderNodeNewGeometry');scale=ns.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=.125;lk.new(geo.outputs['Position'],scale.inputs[0]);tx=ns.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(O.parent/'Sea/night-water-2048.png'));tx.image.pack();lk.new(scale.outputs[0],tx.inputs[0]);lk.new(tx.outputs[0],bs.inputs['Base Color']);lk.new(tx.outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.25;cube('REVIEW_Water',(0,0,-.40),(160,160,.10),sea)
 # Camera is exactly harbour pitch45/yaw35; wider ortho framing includes the growing frontage and neighbouring house.
 direction=Vector((-math.sin(math.radians(35))*math.cos(math.pi/4),math.cos(math.radians(35))*math.cos(math.pi/4),math.sin(math.pi/4)));target=Vector((.6,.5,1.6));d=bpy.data.cameras.new('REVIEW_HarbourCamera');cam=bpy.data.objects.new('REVIEW_HarbourCamera',d);sc.collection.objects.link(cam);cam.location=target+direction*30;cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=24;sc.camera=cam
 sc.render.resolution_x=1440;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/(row['name'].lower()+'-harbour-night-1440x900.png'));bpy.ops.render.render(write_still=True)
 cameras.append({'stage':row['stage'],'render':Path(sc.render.filepath).name,'resolution':[1440,900],'unity_rotation_euler':[45,35,0],'blender_position_m':list(cam.location),'blender_rotation_rad':list(cam.rotation_euler),'blender_ortho_scale':24,'unity_orthographic_size':7.5,'target_blender_m':list(target),'neighbour':'accepted HouseA 3x2.6x3.6m, review only','quay_top_z_m':-.02,'waterline_z_m':-.35})
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(row['name']+'-Harbour-Night-check.blend')))
(O/'night-harbour-cameras.json').write_text(json.dumps(cameras,indent=2));print('EXTERIORS NIGHT HARBOUR REVIEW PASS',flush=True)

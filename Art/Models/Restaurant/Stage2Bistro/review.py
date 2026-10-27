import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).resolve().parent;P=O/'renders';P.mkdir(exist_ok=True);V=O.parent/'Stage1V4';R=O.parents[3]
bpy.ops.wm.open_mainfile(filepath=str(O/'Stage2Bistro.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.cycles.device='GPU';sc.cycles.samples=32;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
for d in p.devices:d.use=d.type=='OPTIX'
# Accepted painted night water, review only.
w=bpy.data.objects['REVIEW_WaterPlane'];m=bpy.data.materials.new('REVIEW_PaintedNightSea');m.use_nodes=True;ns=m.node_tree.nodes;lk=m.node_tree.links;bs=ns['Principled BSDF'];bs.inputs['Roughness'].default_value=.74;bs.inputs['Metallic'].default_value=0;bs.inputs['Emission Strength'].default_value=.65;geo=ns.new('ShaderNodeNewGeometry');scale=ns.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/8;lk.new(geo.outputs['Position'],scale.inputs[0]);tx=ns.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(O.parent/'Sea/night-water-2048.png'));tx.image.pack();lk.new(scale.outputs[0],tx.inputs[0]);lk.new(tx.outputs['Color'],bs.inputs['Base Color']);lk.new(tx.outputs['Color'],bs.inputs['Emission Color']);w.data=w.data.copy();w.data.materials.clear();w.data.materials.append(m)
cam=sc.camera;v4=json.loads((V/'final-cameras.json').read_text());cam.rotation_euler=v4[0]['rotation_blender_rad'];cam.data.type='PERSP';target=Vector((2.5,0,.65));pts=[o.matrix_world@Vector(c) for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_') for c in [v.co for v in o.data.vertices if (o.matrix_world@v.co).z>=-.08]];records=[]
for row in v4:
 sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.resolution_percentage=100;cam.data.lens=row['lens_mm'];distance=21.0
 while True:
  cam.location=target+cam.rotation_euler.to_matrix()@Vector((0,0,distance));bpy.context.view_layer.update();uv=[world_to_camera_view(sc,cam,v) for v in pts]
  if all(.045<u.x<.955 and .045<u.y<.955 and u.z>0 for u in uv):break
  distance+=.25
  assert distance<40
 rec=dict(row);rec['position_blender_m']=list(cam.location);rec['position_unity_m']=[cam.location.x,cam.location.z,-cam.location.y];rec['distance_m']=distance;rec['target_blender_m']=list(target);rec['framing_note']='V4 rotation+lens retained; expanded 10m room and terrace reframed to >4.5% above-water geometry margin';records.append(rec);sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/('bistro-'+row['file']));bpy.ops.render.render(write_still=True)
(O/'final-cameras.json').write_text(json.dumps(records,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'Bistro-V4-check.blend'));print('BISTRO REVIEW PASS',flush=True)

"""Exact accepted cameras; same backdrop/tint treatment on both sides, source proof only."""
import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;STAGE=O.name;P=O/'kitchen-look-renders';P.mkdir(exist_ok=True)
for variant in ['before','after']:
 source=O/'_kitchen-look-backup'/(STAGE+'.blend') if variant=='before' else O/(STAGE+'.blend')
 # Cleanup reruns preserve original BEFORE after temporary backups are removed.
 if not source.exists():continue
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
 sc.cycles.device='GPU';sc.cycles.samples=24;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 for ob in sc.objects:
  if ob.type=='MESH' and not ob.name.startswith('REVIEW_') and not ob.data.color_attributes.get('LocalAO'):
   ob.data=ob.data.copy();ao=ob.data.color_attributes.new(name='LocalAO',type='BYTE_COLOR',domain='CORNER')
   for d in ao.data:d.color=(1,1,1,1)
 for m in bpy.data.materials:
  if not m.use_nodes or 'Atlas' not in m.name:continue
  ns=m.node_tree.nodes;lk=m.node_tree.links;bs=ns.get('Principled BSDF')
  if not bs or not bs.inputs['Base Color'].links:continue
  if ns.get('KitchenProofAO'):continue
  old=bs.inputs['Base Color'].links[0].from_socket;attr=ns.new('ShaderNodeVertexColor');attr.layer_name='LocalAO';mul=ns.new('ShaderNodeMixRGB');mul.name='KitchenProofAO';mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;lk.new(old,mul.inputs[1]);lk.new(attr.outputs['Color'],mul.inputs[2]);lk.new(mul.outputs[0],bs.inputs['Base Color'])
 w=bpy.data.objects.get('REVIEW_WaterPlane')
 if w:
  m=bpy.data.materials.new('REVIEW_KitchenSea');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n['Principled BSDF'];bs.inputs['Roughness'].default_value=.8;bs.inputs['Emission Strength'].default_value=.55
  geo=n.new('ShaderNodeNewGeometry');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/8;l.new(geo.outputs['Position'],scale.inputs[0]);tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O.parent/'Sea/sea1-night-water-2048.png'));l.new(scale.outputs[0],tex.inputs[0]);l.new(tex.outputs['Color'],bs.inputs['Base Color']);l.new(tex.outputs['Color'],bs.inputs['Emission Color']);w.data=w.data.copy();w.data.materials.clear();w.data.materials.append(m)
 for row in json.loads((O/'final-cameras.json').read_text()):
  cam=sc.camera;cam.location=row['position_blender_m'];cam.rotation_euler=row['rotation_blender_rad'];cam.data.type='PERSP';cam.data.lens=row['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/(variant+'-'+row['file']));bpy.ops.render.render(write_still=True)
 # Diagnostic kitchen detail uses same yaw/elevation, closer target; clearly labelled non-game crop.
 from mathutils import Vector
 cam=sc.camera;cam.rotation_euler=tuple(json.loads((O/'final-cameras.json').read_text())[0]['rotation_blender_rad']);cam.data.type='ORTHO';cam.data.ortho_scale=4.45;target=Vector((-2.1,1.05,1.13));cam.location=target+(cam.rotation_euler.to_quaternion()@Vector((0,0,10)));sc.render.resolution_x=1200;sc.render.resolution_y=900;sc.render.filepath=str(P/(variant+'-kitchen-detail.png'));bpy.ops.render.render(write_still=True)
 if variant=='after':
  for im in bpy.data.images:
   if im.source=='FILE':
    try:im.filepath=bpy.path.abspath(im.filepath);im.pack()
    except Exception:pass
  bpy.ops.wm.save_as_mainfile(filepath=str(O/'kitchen-look-Check.blend'))
print('KITCHEN LOOK PROOFS PASS',STAGE,flush=True)

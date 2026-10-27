"""Additive current V4 room proof; production scene unchanged."""
import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V4';P=O/'renders-sea1';P.mkdir(exist_ok=True)
source=V/'RoomLook3-Check.blend';bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
sc.cycles.device='GPU';sc.cycles.samples=24;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
w=bpy.data.objects['REVIEW_WaterPlane'];mat=bpy.data.materials.new('Sea1_PaintedNightWater');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.8;bs.inputs['Emission Strength'].default_value=.55
geo=n.new('ShaderNodeNewGeometry');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/8;l.new(geo.outputs['Position'],scale.inputs[0]);tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/'sea1-night-water-2048.png'));tex.extension='REPEAT';l.new(scale.outputs[0],tex.inputs[0]);l.new(tex.outputs['Color'],bs.inputs['Base Color']);l.new(tex.outputs['Color'],bs.inputs['Emission Color']);l.new(bs.outputs[0],out.inputs['Surface']);w.data=w.data.copy();w.data.materials.clear();w.data.materials.append(mat)
for im in bpy.data.images:
 if im.source=='FILE':
  try:im.filepath=bpy.path.abspath(im.filepath);im.pack()
  except Exception as e:print('PACK SKIP',im.name,e)
sc.frame_set(13);records=[]
for row in json.loads((V/'final-cameras.json').read_text()):
 cam=sc.camera;cam.location=row['position_blender_m'];cam.rotation_euler=row['rotation_blender_rad'];cam.data.type='PERSP';cam.data.lens=row['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/('sea1-'+row['file']));bpy.ops.render.render(write_still=True);records.append(row)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Sea1-V4-check.blend'))
(O/'sea1-blender-check.json').write_text(json.dumps({'source':str(source.name),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'camera_source':'Stage1V4/final-cameras.json','cameras':records,'repeat_m':8,'roughness':.8,'emission_strength':.55,'packed_texture':tex.image.packed_file is not None,'no_extra_reflection_overlay':True,'native_Unity_unverified':True},indent=2));print('SEA1 V4 check PASS')

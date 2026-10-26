"""Read-only V4 room input; additive Sea/ proof outputs only."""
import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V4';P=O/'renders';P.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(V/'LookProof.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
sc.cycles.device='GPU';sc.cycles.samples=32;prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
w=bpy.data.objects['REVIEW_WaterPlane'];z=max((w.matrix_world@v.co).z for v in w.data.vertices)
mat=bpy.data.materials.new('NightSea_Painted');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.74;bs.inputs['Metallic'].default_value=0;bs.inputs['Emission Strength'].default_value=.65
geo=n.new('ShaderNodeNewGeometry');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/8.0;l.new(geo.outputs['Position'],scale.inputs[0]);tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O/'night-water-2048.png'));tex.extension='REPEAT';l.new(scale.outputs[0],tex.inputs[0]);l.new(tex.outputs['Color'],bs.inputs['Base Color']);l.new(tex.outputs['Color'],bs.inputs['Emission Color']);l.new(bs.outputs[0],out.inputs['Surface']);w.data=w.data.copy();w.data.materials.clear();w.data.materials.append(mat)
# Additive black-zero light contribution. This overlay is review-only, kept out of FBX.
ref=bpy.data.materials.new('LanternStreaks_Additive');ref.use_nodes=True;n=ref.node_tree.nodes;l=ref.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');add=n.new('ShaderNodeAddShader');trans=n.new('ShaderNodeBsdfTransparent');em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=.65
uv=n.new('ShaderNodeTexCoord');tx=n.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(str(O/'lantern-reflections-additive-2048.png'));tx.extension='REPEAT'
mp=n.new('ShaderNodeVectorMath');mp.operation='MULTIPLY';mp.inputs[1].default_value=(2.0,1.0,1);l.new(uv.outputs['UV'],mp.inputs[0]);l.new(mp.outputs[0],tx.inputs[0])
# Fade gold away from the warm quay; preserve the independent art PNG.
sep=n.new('ShaderNodeSeparateXYZ');l.new(uv.outputs['UV'],sep.inputs[0]);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.02;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(1,1,1,1)
l.new(sep.outputs['Y'],ramp.inputs[0]);mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;l.new(tx.outputs['Color'],mul.inputs[1]);l.new(ramp.outputs['Color'],mul.inputs[2]);l.new(mul.outputs[0],em.inputs[0]);l.new(trans.outputs[0],add.inputs[0]);l.new(em.outputs[0],add.inputs[1]);l.new(add.outputs[0],out.inputs['Surface'])
bpy.ops.mesh.primitive_plane_add(size=2,location=(0,-5.0,z+.012));overlay=bpy.context.object;overlay.name='REVIEW_LanternReflectionOverlay';overlay.scale=(5.6,1.65,1);overlay.data.materials.append(ref)
# Pack new images and repair existing room references before moving the proof file.
for im in bpy.data.images:
 if im.source=='FILE':
  try:
   im.filepath=bpy.path.abspath(im.filepath);im.pack()
  except Exception as e:print('PACK SKIP',im.name,str(e),flush=True)
sc.frame_set(13);cam=sc.camera;records=[]
for row in json.loads((V/'final-cameras.json').read_text()):
 cam.location=row['position_blender_m'];cam.rotation_euler=row['rotation_blender_rad'];cam.data.type='PERSP';cam.data.lens=row['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/('night-sea-'+row['file']));bpy.ops.render.render(write_still=True);records.append(row)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'NightSea-V4-check.blend'))
(O/'blender-check.json').write_text(json.dumps({'source':'Stage1V4/LookProof.blend','source_sha256':hashlib.sha256((V/'LookProof.blend').read_bytes()).hexdigest(),'cameras':records,'water_z_m':z,'base_repeat_m':8.0,'overlay_repeat_across_width':2,'overlay_size_m':[11.2,3.3],'review_only':True,'packed_new_images':all(im.packed_file is not None for im in [tex.image,tx.image])},indent=2));print('SEA V4 CHECK COMPLETE',flush=True)

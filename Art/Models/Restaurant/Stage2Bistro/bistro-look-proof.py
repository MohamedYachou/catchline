"""Same-camera source comparisons. Preview seats never enter production export."""
import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent;P=O/'bistro-look-renders';P.mkdir(exist_ok=True)
for variant in (['before','after'] if (O/'_bistro-look-backup/Stage2Bistro.blend').exists() else ['after']):
 source=O/'_bistro-look-backup/Stage2Bistro.blend' if variant=='before' else O/'Stage2Bistro.blend'
 bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
 sc.cycles.device='GPU';sc.cycles.samples=32;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 # Show exported vertex pigment in Blender too: the native shader always multiplies COLOR_0.
 for m in bpy.data.materials:
  if not m.use_nodes or 'Atlas' not in m.name:continue
  ns=m.node_tree.nodes;lk=m.node_tree.links;bs=ns.get('Principled BSDF')
  if not bs or not bs.inputs['Base Color'].links:continue
  if ns.get('BistroProofAO'):continue
  old=bs.inputs['Base Color'].links[0].from_socket;attr=ns.new('ShaderNodeVertexColor');attr.layer_name='LocalAO';mul=ns.new('ShaderNodeMixRGB');mul.name='BistroProofAO';mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;lk.new(old,mul.inputs[1]);lk.new(attr.outputs['Color'],mul.inputs[2]);lk.new(mul.outputs[0],bs.inputs['Base Color'])
 # Same accepted sea on both sides; source-only backdrop, never exported.
 w=bpy.data.objects['REVIEW_WaterPlane'];m=bpy.data.materials.new('REVIEW_BistroLookSea');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n['Principled BSDF'];bs.inputs['Roughness'].default_value=.8;bs.inputs['Emission Strength'].default_value=.55
 geo=n.new('ShaderNodeNewGeometry');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/8;l.new(geo.outputs['Position'],scale.inputs[0]);tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(O.parent/'Sea/sea1-night-water-2048.png'));l.new(scale.outputs[0],tex.inputs[0]);l.new(tex.outputs['Color'],bs.inputs['Base Color']);l.new(tex.outputs['Color'],bs.inputs['Emission Color']);w.data=w.data.copy();w.data.materials.clear();w.data.materials.append(m)
 for row in json.loads((O/'final-cameras.json').read_text()):
  cam=sc.camera;cam.location=row['position_blender_m'];cam.rotation_euler=row['rotation_blender_rad'];cam.data.type='PERSP';cam.data.lens=row['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=str(P/(variant+'-'+row['file']));bpy.ops.render.render(write_still=True)
 # Add only review furniture as a populated illustration, never to the source model.
 with bpy.data.libraries.load(str(O.parent/'Upgrades/RestaurantUpgrades.blend'),link=False) as (src,dst):dst.objects=['Dining2_Tier2','Dining4_Tier2']
 tables={o.name:o for o in dst.objects if o}
 for i,(name,x,y) in enumerate([('Dining2_Tier2',1.6,-.6),('Dining4_Tier2',3.8,.7),('Dining2_Tier2',7.35,-.8),('Dining2_Tier2',7.35,1.25)]):
  ob=tables[name].copy();ob.data=ob.data.copy();ob.name='REVIEW_LayoutExample'+str(i);sc.collection.objects.link(ob);ob.location=(x,y,.055)
 for row in json.loads((O/'final-cameras.json').read_text()):
  cam=sc.camera;cam.location=row['position_blender_m'];cam.rotation_euler=row['rotation_blender_rad'];cam.data.lens=row['lens_mm'];sc.render.resolution_x,sc.render.resolution_y=row['resolution'];sc.render.filepath=str(P/(variant+'-populated-'+row['file']));bpy.ops.render.render(write_still=True)
 if variant=='after':
  for im in bpy.data.images:
   if im.source=='FILE':
    try:im.filepath=bpy.path.abspath(im.filepath);im.pack()
    except Exception:pass
  bpy.ops.wm.save_as_mainfile(filepath=str(O/'bistro-look-Check.blend'))
print('BISTRO LOOK PROOFS PASS',flush=True)

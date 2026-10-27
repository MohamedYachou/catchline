"""Fresh runtime-item FBX proofs; shared V4 atlas, lighting and cameras on both sides."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V2';B=O/'_station-finish-backup';P=O/'station-finish-renders';P.mkdir(exist_ok=True)
names=['Stove','Oven','FridgeV2','Fryer','PrepCounter','SoupKettle','SinkDishRack','CoffeeBar'];cameras=json.loads((O/'final-cameras.json').read_text())
def posix(p):return str(p).replace(chr(92),'/')
def settings(sc):
 sc.render.engine='CYCLES';sc.cycles.device='GPU';sc.cycles.samples=24;sc.cycles.use_denoising=True;p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
def materials():
 # Explicit production V4 images for identical before/after runtime material interpretation.
 mats=[m for m in bpy.data.materials if m.use_nodes and 'Atlas' in m.name and 'V4' in m.name]
 assert mats
 mat=mats[0]
 for m in mats:
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image:
    file='Restaurant_Surface.png' if 'Surface' in n.name or 'Surface' in n.image.name else 'Restaurant_BaseColor.png'
    n.image=bpy.data.images.load(posix(O/'textures'/file),check_existing=True);n.image.colorspace_settings.name='Non-Color' if 'Surface' in file else 'sRGB'
  ns=m.node_tree.nodes;lk=m.node_tree.links;bs=ns.get('Principled BSDF')
  if bs and bs.inputs['Base Color'].links and not ns.get('StationProofAO'):
   old=bs.inputs['Base Color'].links[0].from_socket;a=ns.new('ShaderNodeVertexColor');a.layer_name='LocalAO';mul=ns.new('ShaderNodeMixRGB');mul.name='StationProofAO';mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;lk.new(old,mul.inputs[1]);lk.new(a.outputs['Color'],mul.inputs[2]);lk.new(mul.outputs[0],bs.inputs['Base Color'])
 return mat
def fillAO(ob):
 if not ob.data.color_attributes.get('LocalAO'):
  a=ob.data.color_attributes.new(name='LocalAO',type='BYTE_COLOR',domain='CORNER')
  for d in a.data:d.color=(1,1,1,1)
def getitem(name,variant,mat):
 path=(B/'Stage1V2/items' if variant=='before' else V/'items')/f'{name}.fbx';old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=posix(path),colors_type='LINEAR');new=set(bpy.data.objects)-old;ob=next(o for o in new if o.type=='MESH');data=ob.data.copy();data.materials.clear();data.materials.append(mat)
 for o in new:bpy.data.objects.remove(o,do_unlink=True)
 return data
def render(sc,path,w,h):
 sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.filepath=posix(path);bpy.ops.render.render(write_still=True)
for variant in ['before','after']:
 bpy.ops.wm.open_mainfile(filepath=posix(O/'Stage1V4.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;settings(sc);mat=materials()
 for ob in sc.objects:
  if ob.type=='MESH' and not ob.name.startswith('REVIEW_'):fillAO(ob)
 for name in names:bpy.data.objects[name].data=getitem(name,variant,mat)
 # Same night sea as accepted kitchen proof, neutral and equal both sides.
 w=bpy.data.objects.get('REVIEW_WaterPlane')
 if w:
  m=bpy.data.materials.new('REVIEW_StationSea');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n['Principled BSDF'];bs.inputs['Roughness'].default_value=.8;bs.inputs['Emission Strength'].default_value=.55
  geo=n.new('ShaderNodeNewGeometry');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=1/8;l.new(geo.outputs['Position'],scale.inputs[0]);tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(posix(O.parent/'Sea/sea1-night-water-2048.png'));l.new(scale.outputs[0],tex.inputs[0]);l.new(tex.outputs['Color'],bs.inputs['Base Color']);l.new(tex.outputs['Color'],bs.inputs['Emission Color']);w.data=w.data.copy();w.data.materials.clear();w.data.materials.append(m)
 for row in cameras:
  cam=sc.camera;cam.location=row['position_blender_m'];cam.rotation_euler=row['rotation_blender_rad'];cam.data.type='PERSP';cam.data.lens=row['lens_mm'];render(sc,P/(variant+'-'+row['file']),*row['resolution'])
 cam=sc.camera;cam.rotation_euler=cameras[0]['rotation_blender_rad'];cam.data.type='ORTHO';cam.data.ortho_scale=4.45;target=Vector((-2.1,1.05,1.13));cam.location=target+(cam.rotation_euler.to_quaternion()@Vector((0,0,10)));render(sc,P/(variant+'-kitchen-detail.png'),1200,900)
 if variant=='after':
  for im in bpy.data.images:
   if im.source=='FILE':
    try:im.pack()
    except Exception:pass
  bpy.ops.wm.save_as_mainfile(filepath=posix(O/'station-finish-Check.blend'))
# Isolated exports, lit identically, same V4 camera elevation/yaw; diagnostic ortho framing.
for variant in ['before','after']:
 bpy.ops.wm.open_mainfile(filepath=posix(O/'Stage1V4.blend'));sc=bpy.context.scene;settings(sc);mat=materials()
 for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
 world=bpy.data.worlds.new('StationStudio');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.23,.32,1);world.node_tree.nodes['Background'].inputs[1].default_value=.45;sc.world=world
 bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='REVIEW_Floor';m=bpy.data.materials.new('REVIEW_Slate');m.diffuse_color=(.055,.073,.102,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=m.diffuse_color;m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.9;floor.data.materials.append(m);floor.location.z=-.006
 for loc,power,size,color in [((-3,-4,6),650,4,(1,.81,.59)),((4,-1,4),400,3,(.65,.8,1)),((0,4,5),800,3,(1,.93,.8))]:
  light=bpy.data.lights.new('REVIEW_Area','AREA');light.energy=power;light.shape='DISK';light.size=size;light.color=color;ob=bpy.data.objects.new(light.name,light);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,.5))-ob.location).to_track_quat('-Z','Y').to_euler()
 data=bpy.data.cameras.new('REVIEW_Camera');cam=bpy.data.objects.new(data.name,data);sc.collection.objects.link(cam);sc.camera=cam;cam.rotation_euler=cameras[0]['rotation_blender_rad'];cam.data.type='ORTHO'
 for name in names:
  data=getitem(name,variant,mat);ob=bpy.data.objects.new('REVIEW_'+name,data);sc.collection.objects.link(ob);fillAO(ob);pts=[v.co for v in data.vertices];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);target=(lo+hi)*.5;cam.location=target+(cam.rotation_euler.to_quaternion()@Vector((0,0,10)));cam.data.ortho_scale=max((hi.x-lo.x)*1.32,(hi.z-lo.z)*1.55,1.35);render(sc,P/(variant+'-'+name+'.png'),640,640);bpy.data.objects.remove(ob,do_unlink=True)
print('STATION FINISH PROOF PASS',flush=True)

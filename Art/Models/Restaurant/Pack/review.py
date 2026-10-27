"""Fresh-FBX equal-scale grid and incumbent comparison proofs, no Unity writes."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
O=Path(__file__).resolve().parent;R=O.parents[3]
sys.path.insert(0,str(R/'Art/Source/Restaurant/kenney'))
from inspect_pack import load,bounds,reset
from build_fit import material
M=json.loads((O/'manifest.json').read_text());names=[r['name'] for r in M['items']]
def grid(mode):
 reset();anchors=[]
 reference_material=None
 if mode=='before':
  with bpy.data.libraries.load(str(R/'Art/Models/Restaurant/Stage1V2/Stage1V2.blend'),link=False) as (src,dst):dst.materials=['Restaurant_Atlas_URP']
  reference_material=dst.materials[0]
 for i,rec in enumerate(M['items']):
  p=R/rec['reference']['source'] if mode=='before' else O/(rec['name']+'.fbx')
  obs=load(p);meshes=[o for o in obs if o.type=='MESH'];bpy.context.view_layer.update()
  if mode=='before' and 'Stage1V2' in str(p):
   for ob in meshes:ob.data.materials.clear();ob.data.materials.append(reference_material)
  x=(i%6-2.5)*3;y=(i//6-2)*3.7
  for ob in meshes:
   ob.data=ob.data.copy();ob.data.transform(ob.matrix_world);ob.parent=None;ob.matrix_world=Matrix.Identity(4)
   for v in ob.data.vertices:v.co+=Vector((x,y,0))
  lo,hi=bounds(meshes)
  anchors.append(dict(name=rec['name'],origin=[x,y,0],bounds=[list(lo),list(hi)]))
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True
 prefs=bpy.context.preferences.addons['cycles'].preferences
 prefs.compute_device_type='OPTIX';prefs.get_devices()
 for device in prefs.devices:device.use=device.type=='OPTIX'
 s.cycles.device='GPU'
 s.render.resolution_x=3600;s.render.resolution_y=2800;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
 s.world=bpy.data.worlds.new('Harbour studio');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.61,.72,.79,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
 bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.014));bpy.context.object.data.materials.append(material('Quay cream','#DDD7C8'))
 line=material('One metre grid','#BDB9AA')
 for k in range(-12,13):
  for axis in [0,1]:
   bpy.ops.mesh.primitive_cube_add(size=1,location=(k if axis==0 else 0,k if axis==1 else 0,-.009));ob=bpy.context.object;ob.scale=(.008,26,.002) if axis==0 else (26,.008,.002);ob.data.materials.append(line)
 bpy.ops.object.light_add(type='AREA',location=(-7,-10,16));bpy.context.object.data.energy=6500;bpy.context.object.data.size=12
 bpy.ops.object.camera_add();c=bpy.context.object;c.data.type='ORTHO';c.data.ortho_scale=20.5
 pitch=math.radians(38);yaw=math.radians(2);target=Vector((0,0,.2));d=Vector((math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)))
 if mode=='front':d.y=-d.y
 c.location=target+d*40;c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c
 bpy.context.view_layer.update()
 for a in anchors:
  p=world_to_camera_view(s,c,Vector(a['origin']));a['pixel_origin']=[p.x*3600,(1-p.y)*2800]
  box=a['bounds'];pts=[world_to_camera_view(s,c,Vector((x,y,z))) for x in [box[0][0],box[1][0]] for y in [box[0][1],box[1][1]] for z in [0,box[1][2]]]
  a['pixel_bounds']=[min(p.x for p in pts)*3600,min(1-p.y for p in pts)*2800,max(p.x for p in pts)*3600,max(1-p.y for p in pts)*2800]
 (O/(mode+'-grid-layout.json')).write_text(json.dumps(anchors,indent=2))
 if '--eevee' in sys.argv:
  s.render.engine='BLENDER_EEVEE'
 s.render.filepath=str(O/'renders'/(mode+'-grid.png'));bpy.ops.render.render(write_still=True)
 print('GRID_DONE',mode,flush=True)
if __name__=='__main__':grid(sys.argv[-1])
